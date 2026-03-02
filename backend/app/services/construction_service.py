"""Construction service — implements Prompt 1.3: Construction Zone Status.

Provides:
1. Project name and agency (BWSSB, BBMP, Metro, etc.)
2. Exact location with affected road segments
3. Lane restrictions (single-lane, contraflow, full closure)
4. Official start and end dates with completion confidence %
5. Current progress (% complete, milestone status)
6. Official diversion routes with current conditions
7. Peak-hour amplification: how much earlier/later congestion starts/ends
8. Post-completion normalization timeline

Data sourced from OpenCity Bengaluru Portal + REPORT.md Section 3.
"""

from datetime import date, datetime, timezone

from app.data_sources.opencity import OpenCityClient
from app.models.schemas.construction import (
    ConstructionListResponse,
    ConstructionZone,
    DiversionInfo,
    PeakAmplification,
    ProjectMilestone,
)


class ConstructionService:
    """Service for Prompt 1.3 — Construction Zone Status."""

    def __init__(self):
        self.opencity = OpenCityClient()

    async def get_all_zones(self) -> ConstructionListResponse:
        """Get all active construction zones."""
        data = await self.opencity.fetch()
        raw_zones = data.get("construction_zones", [])

        zones = []
        for raw in raw_zones:
            milestones = [
                ProjectMilestone(
                    name=m["name"],
                    target_date=date.fromisoformat(m["target_date"]),
                    status=m["status"],
                    risk_factor=m.get("risk"),
                )
                for m in raw.get("milestones", [])
            ]

            diversions = [
                DiversionInfo(
                    direction=d["direction"],
                    primary_alternative=d["primary_alternative"],
                    added_distance_km=d["added_distance_km"],
                    time_penalty_freeflow=d["time_penalty_freeflow"],
                    current_conditions=d["current_conditions"],
                )
                for d in raw.get("diversions", [])
            ]

            peak_amp = None
            if raw.get("peak_amplification"):
                pa = raw["peak_amplification"]
                peak_amp = PeakAmplification(
                    normal_peak_window=pa["normal_peak_window"],
                    amplified_window=pa["amplified_window"],
                    extension_hours=pa["extension_hours"],
                    description=f"Construction extends peak congestion by {pa['extension_hours']} hours: from {pa['normal_peak_window']} to {pa['amplified_window']}",
                )

            # Calculate completion confidence based on progress and days remaining
            end_dt = date.fromisoformat(raw["end_date"])
            days_remaining = (end_dt - date.today()).days
            completion_pct = raw.get("completion_pct", 50.0)

            # Per REPORT.md: BWSSB confidence is 89%, +-5 day uncertainty
            if completion_pct > 85:
                confidence = 89.0
                uncertainty = 5
            elif completion_pct > 60:
                confidence = 75.0
                uncertainty = 10
            elif completion_pct > 30:
                confidence = 60.0
                uncertainty = 20
            else:
                confidence = 45.0
                uncertainty = 30

            zones.append(ConstructionZone(
                zone_id=raw["id"],
                project_name=raw["project_name"],
                agency=raw["agency"],
                location_description=raw["location_description"],
                affected_roads=raw["affected_roads"],
                start_coordinates=raw["start_coords"],
                end_coordinates=raw["end_coords"],
                lane_restriction=raw["lane_restriction"],
                traffic_management=raw.get("traffic_management", "Standard traffic management"),
                start_date=date.fromisoformat(raw["start_date"]),
                end_date=end_dt,
                completion_confidence_pct=confidence,
                uncertainty_days=uncertainty,
                completion_pct=completion_pct,
                milestones=milestones,
                diversions=diversions,
                diversion_compliance_pct=raw.get("diversion_compliance_pct"),
                peak_amplification=peak_amp,
                normalization_weeks=3 if days_remaining <= 10 else 2,
                capacity_reduction_pct=raw.get("capacity_reduction_pct"),
                additional_delay_minutes=raw.get("additional_delay_minutes"),
                source=raw.get("source", "OpenCity"),
                last_updated=datetime.now(timezone.utc),
            ))

        return ConstructionListResponse(
            zones=zones,
            total_active=len(zones),
            timestamp=datetime.now(timezone.utc),
            demo_mode=True,
        )

    async def get_zone(self, zone_id: str) -> ConstructionZone | None:
        """Get a single construction zone by ID."""
        all_zones = await self.get_all_zones()
        for zone in all_zones.zones:
            if zone.zone_id == zone_id:
                return zone
        return None
