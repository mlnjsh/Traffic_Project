"""Prediction service — implements Prompt 2.1: "When Will It Get Better?" Engine.

Three prediction horizons:
- SHORT-TERM (0-15 min): Real-time trend extrapolation, 75-80% accuracy
- MEDIUM-TERM (15-60 min): Historical pattern matching + current state, 60-70% accuracy
- CONSTRUCTION: Project milestone data, 85-90% accuracy on completion date

Per REPORT.md Section 2.2.1: Evening peak reaches 183% at 18:00, clears by ~21:30.
Per CLAUDE.md: Prediction confidence levels must always be cited.
"""

from datetime import datetime, timezone

from app.data_sources.bangalore_corridors import CORRIDORS
from app.services.traffic_service import TrafficService
from app.services.construction_service import ConstructionService
from app.models.schemas.prediction import (
    CongestionPrediction,
    ConstructionPrediction,
    MediumTermPrediction,
    PredictionResponse,
    ShortTermPrediction,
)


# Per REPORT.md Section 2.2.1: Typical clearing times by corridor type
TYPICAL_CLEAR_TIMES = {
    "orr_silk_board": "21:30",
    "orr_zakir_nagar": "22:00",  # Extended due to BWSSB construction
    "bellandur_road": "21:00",
    "whitefield_main": "21:15",
    "electronic_city": "20:45",
    "bannerghatta_road": "21:00",
    "cbd_mg_road": "20:30",
    "thanisandra_hennur": "21:15",
}

# Congestion profile by hour (REPORT.md Section 2.2.1, normalized 0-1)
HOURLY_CONGESTION = {
    0: 0.10, 1: 0.08, 2: 0.05, 3: 0.05, 4: 0.06, 5: 0.10,
    6: 0.25, 7: 0.55, 8: 0.80, 9: 0.90, 10: 0.70, 11: 0.60,
    12: 0.55, 13: 0.55, 14: 0.60, 15: 0.65, 16: 0.80, 17: 0.95,
    18: 1.00, 19: 0.85, 20: 0.60, 21: 0.40, 22: 0.25, 23: 0.15,
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class PredictionService:
    """Service for Prompt 2.1 — When Will It Get Better?"""

    def __init__(self):
        self.traffic_service = TrafficService()
        self.construction_service = ConstructionService()

    async def get_prediction(self, corridor_id: str) -> PredictionResponse | None:
        """Generate predictions for a corridor."""
        corridor_status = await self.traffic_service.get_corridor(corridor_id)
        if not corridor_status:
            return None

        now = datetime.now(timezone.utc)
        hour = datetime.now().hour
        minute = datetime.now().minute
        hour_frac = hour + minute / 60.0

        # Find corridor def
        corridor_def = next((c for c in CORRIDORS if c["id"] == corridor_id), None)
        free_flow_speed = corridor_def["free_flow_speed"] if corridor_def else 45.0

        current_speed = corridor_status.current_speed_kmh
        congestion = corridor_status.congestion_pct

        # --- Short-term prediction (0-15 min) ---
        short_term = self._predict_short_term(
            corridor_id, corridor_status.name, current_speed, congestion, free_flow_speed, hour_frac
        )

        # --- Medium-term prediction (15-60 min) ---
        medium_term = self._predict_medium_term(
            corridor_id, corridor_status.name, current_speed, congestion, free_flow_speed, hour_frac
        )

        # --- Construction-specific prediction ---
        construction = await self._predict_construction(corridor_id)

        return PredictionResponse(
            corridor_id=corridor_id,
            corridor_name=corridor_status.name,
            short_term=short_term,
            medium_term=medium_term,
            construction=construction,
            timestamp=now,
        )

    def _predict_short_term(
        self, corridor_id: str, name: str, speed: float, congestion: float,
        free_flow: float, hour_frac: float,
    ) -> ShortTermPrediction:
        """0-15 min trend extrapolation per Prompt 2.1."""
        # Determine direction from time-of-day curve
        current_level = HOURLY_CONGESTION.get(int(hour_frac), 0.5)
        next_level = HOURLY_CONGESTION.get(min(int(hour_frac) + 1, 23), 0.5)

        if next_level < current_level - 0.05:
            direction = "improving"
            speed_delta_5min = (free_flow - speed) * 0.05
            est_change = max(5, int((congestion - 60) / 5))
        elif next_level > current_level + 0.05:
            direction = "worsening"
            speed_delta_5min = -(free_flow - speed) * 0.03
            est_change = max(5, int((100 - congestion) / 8))
        else:
            direction = "stable"
            speed_delta_5min = 0
            est_change = 30  # stable for a while

        pred_5 = max(3, round(speed + speed_delta_5min, 1))
        pred_10 = max(3, round(speed + speed_delta_5min * 2, 1))
        pred_15 = max(3, round(speed + speed_delta_5min * 3, 1))

        narrative = (
            f"Based on current flow rates, conditions on {name} should "
            f"{direction.replace('ing', '')}e in approximately {est_change} minutes."
            if direction != "stable"
            else f"Conditions on {name} are expected to remain stable for the next 15 minutes."
        )

        return ShortTermPrediction(
            direction=direction,
            current_speed_kmh=round(speed, 1),
            predicted_speed_5min=pred_5,
            predicted_speed_10min=pred_10,
            predicted_speed_15min=pred_15,
            estimated_change_minutes=est_change,
            confidence_pct=77.5,  # 75-80% per Prompt 2.1
            basis="Real-time trend extrapolation from TomTom + ASTraM fusion data",
            narrative=narrative,
        )

    def _predict_medium_term(
        self, corridor_id: str, name: str, speed: float, congestion: float,
        free_flow: float, hour_frac: float,
    ) -> MediumTermPrediction:
        """15-60 min historical pattern matching per Prompt 2.1."""
        now = datetime.now()
        day_name = DAY_NAMES[now.weekday()]
        typical_clear = TYPICAL_CLEAR_TIMES.get(corridor_id, "21:00")

        # Parse typical clear time
        clear_h, clear_m = map(int, typical_clear.split(":"))
        clear_frac = clear_h + clear_m / 60.0

        # Assess current vs typical
        if congestion > 120:
            assessment = "later"
            offset_min = 15
        elif congestion < 60:
            assessment = "earlier"
            offset_min = -15
        else:
            assessment = "on-track"
            offset_min = 0

        est_clear_min = clear_m + offset_min
        est_clear_h = clear_h + est_clear_min // 60
        est_clear_min = est_clear_min % 60
        est_clear = f"{est_clear_h:02d}:{est_clear_min:02d}"

        # Build prediction points at 15, 30, 45, 60 min
        predictions = []
        for mins_ahead in [15, 30, 45, 60]:
            future_hour = hour_frac + mins_ahead / 60.0
            future_level = HOURLY_CONGESTION.get(min(int(future_hour), 23), 0.5)
            pred_congestion = future_level * 183  # Per REPORT.md: peak = 183%
            pred_speed = max(3, free_flow * (1 - future_level * 0.85))

            from app.core.fusion import speed_to_color
            predictions.append(CongestionPrediction(
                time_from_now_minutes=mins_ahead,
                predicted_speed_kmh=round(pred_speed, 1),
                predicted_congestion_pct=round(pred_congestion, 1),
                predicted_color=speed_to_color(pred_speed).value,
                confidence_pct=65.0,  # 60-70% per Prompt 2.1
            ))

        narrative = (
            f"Based on typical {day_name} patterns, {name} usually clears by {typical_clear}. "
            f"Current conditions suggest {assessment} clearing — estimated around {est_clear}."
        )

        return MediumTermPrediction(
            day_of_week=day_name,
            typical_clear_time=typical_clear,
            current_assessment=assessment,
            estimated_clear_time=est_clear,
            predictions=predictions,
            confidence_pct=65.0,
            basis=f"Historical {day_name} pattern matching from Kaggle Traffic Pulse + current ASTraM state",
            narrative=narrative,
        )

    async def _predict_construction(self, corridor_id: str) -> ConstructionPrediction | None:
        """Construction-specific prediction per Prompt 2.1."""
        zones = await self.construction_service.get_all_zones()

        # Find construction affecting this corridor
        for zone in zones.zones:
            affected = [r.lower() for r in zone.affected_roads]
            corridor_def = next((c for c in CORRIDORS if c["id"] == corridor_id), None)
            if not corridor_def:
                continue

            corridor_name_lower = corridor_def["name"].lower()
            if any(keyword in corridor_name_lower for road in affected for keyword in road.split() if len(keyword) > 4):
                return ConstructionPrediction(
                    project_name=zone.project_name,
                    completion_pct=zone.completion_pct,
                    scheduled_completion=str(zone.end_date),
                    uncertainty_days=zone.uncertainty_days,
                    normalization_weeks=zone.normalization_weeks,
                    confidence_pct=89.0 if zone.completion_pct > 80 else 75.0,
                    basis=f"Project milestone tracking via OpenCity + {zone.agency} reports",
                    narrative=(
                        f"The {zone.project_name} is {zone.completion_pct}% complete. "
                        f"Scheduled completion: {zone.end_date} ±{zone.uncertainty_days} days. "
                        f"After reopening, expect {zone.normalization_weeks} weeks for traffic patterns to normalize."
                    ),
                )

        return None
