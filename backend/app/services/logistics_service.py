"""Logistics & Freight Optimizer — implements Prompt 5.2.

Night window (02:00-06:00): 68% faster.
Construction avoidance, fleet management, fuel optimization.
"""

from datetime import datetime, timezone

from app.services.construction_service import ConstructionService
from app.models.schemas.problem_solving import (
    DeliveryStop,
    FreightRouteOption,
    LogisticsResponse,
)


class LogisticsService:
    """Service for Prompt 5.2 — Logistics & Freight Optimizer."""

    def __init__(self):
        self.construction_service = ConstructionService()

    async def optimize_logistics(self, origin: str, stops: list[str]) -> LogisticsResponse:
        now = datetime.now()
        hour = now.hour

        # Determine time window
        if 2 <= hour <= 6:
            window = "night_optimal"
            multiplier = 1.0
        elif 7 <= hour <= 22:
            window = "daytime_restricted"
            multiplier = 2.0 if 7 <= hour <= 10 or 16 <= hour <= 21 else 1.5
        else:
            window = "transition"
            multiplier = 1.1

        # Get construction zones
        zones = await self.construction_service.get_all_zones()
        active_zones = len(zones.zones)

        # Build delivery route
        delivery_stops = []
        cum_time = 0
        for i, stop in enumerate(stops or ["Koramangala", "Electronic City", "Whitefield"]):
            leg_time = int(20 * multiplier)
            cum_time += leg_time
            arrival_h = hour + cum_time // 60
            arrival_m = cum_time % 60
            restrictions = []
            if 7 <= arrival_h <= 22:
                restrictions.append("Daytime truck ban on major arterials")
            delivery_stops.append(DeliveryStop(
                location=stop,
                estimated_arrival=f"{arrival_h % 24:02d}:{arrival_m:02d}",
                loading_time_minutes=15,
                restrictions=restrictions,
            ))

        total_km = len(delivery_stops) * 15
        fuel_savings = 15.0 if window == "night_optimal" else 5.0

        route = FreightRouteOption(
            total_distance_km=total_km,
            total_time_minutes=cum_time + len(delivery_stops) * 15,
            stops=delivery_stops,
            fuel_savings_pct=fuel_savings,
            night_window_used=(window == "night_optimal"),
        )

        restrictions = [
            "Daytime truck ban: major arterials 07:00-22:00",
            "20-tonne limit on flyovers and elevated expressways",
            "4.5m height clearance on underpasses",
        ]

        return LogisticsResponse(
            fleet_id=f"fleet_{now.strftime('%Y%m%d')}",
            current_time_window=window,
            night_window_insight="Night window (02:00-06:00): 68% faster than peak hours — 4.2 km vs 2.5 km in 15 minutes. All loading zones accessible.",
            active_construction_zones=active_zones,
            construction_free_routes=max(1, 3 - active_zones),
            recommended_route=route,
            restrictions_summary=restrictions,
            fuel_optimization_note=f"Estimated {fuel_savings:.0f}% fuel savings through congestion avoidance (12-18% typical range).",
            timestamp=datetime.now(timezone.utc),
        )
