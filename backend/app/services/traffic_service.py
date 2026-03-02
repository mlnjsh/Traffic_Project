"""Traffic service — implements Prompt 1.1: Current Corridor Status.

Fuses TomTom flow data with ASTraM incidents to provide:
1. Current speed (km/h) and congestion level (%)
2. Active incidents with location
3. Estimated delay vs free-flow
4. Color code: Green/Yellow/Orange/Red/Black
5. Brief prediction: improving, stable, or worsening

Data freshness citation per Prompt 1.1: "Updated X seconds ago via TomTom + ASTraM fusion"
"""

from datetime import datetime, timezone

from app.core.fusion import (
    calculate_delay,
    estimate_trend,
    fuse_color,
)
from app.data_sources.bangalore_corridors import CORRIDORS
from app.data_sources.tomtom import TomTomClient
from app.data_sources.astram import ASTraMClient
from app.models.schemas.traffic import (
    ActiveIncidentBrief,
    CorridorCoordinate,
    CorridorListResponse,
    CorridorSegment,
    CorridorStatus,
    HeatmapDataPoint,
    HeatmapResponse,
)


class TrafficService:
    """Service for Prompt 1.1 — Current Corridor Status."""

    def __init__(self):
        self.tomtom = TomTomClient()
        self.astram = ASTraMClient()

    async def get_all_corridors(self) -> CorridorListResponse:
        """Get status of all 8 monitored Bangalore corridors."""
        # Fetch from both sources
        tomtom_data = await self.tomtom.fetch()
        astram_data = await self.astram.fetch()
        astram_incidents = astram_data.get("incidents", [])

        corridors = []
        for corridor_def in CORRIDORS:
            cid = corridor_def["id"]
            flow = tomtom_data.get(cid, {})

            speed = flow.get("speed_kmh", corridor_def["free_flow_speed"] * 0.5)
            free_flow = flow.get("free_flow_speed_kmh", corridor_def["free_flow_speed"])
            congestion = flow.get("congestion_pct", 50.0)

            # Find incidents on this corridor (ASTraM prioritized per CLAUDE.md)
            corridor_incidents = [
                inc for inc in astram_incidents
                if self._incident_matches_corridor(inc, corridor_def)
            ]

            incident_briefs = [
                ActiveIncidentBrief(
                    type=inc["type"],
                    location=inc.get("nearest_landmark", inc["road_name"]),
                    severity=inc["significance"],
                )
                for inc in corridor_incidents
            ]

            # Calculate delay (using 10km reference distance per REPORT.md)
            travel_time, free_flow_time, delay = calculate_delay(speed, free_flow)

            # Color code per CLAUDE.md spec
            color = fuse_color(speed, congestion)

            # Trend prediction
            trend, trend_desc = estimate_trend(congestion)

            # Build segments for heatmap rendering
            segments = [
                CorridorSegment(
                    start=CorridorCoordinate(**seg["start"]),
                    end=CorridorCoordinate(**seg["end"]),
                    speed_kmh=speed + (i * 0.5),  # slight variation per segment
                    congestion_pct=congestion - (i * 2),
                    color=color,
                )
                for i, seg in enumerate(corridor_def["segments"])
            ]

            now = datetime.now(timezone.utc)
            corridors.append(CorridorStatus(
                corridor_id=cid,
                name=corridor_def["name"],
                direction=corridor_def.get("direction"),
                current_speed_kmh=round(speed, 1),
                free_flow_speed_kmh=free_flow,
                congestion_pct=round(congestion, 1),
                active_incidents=incident_briefs,
                incident_count=len(incident_briefs),
                delay_minutes=delay,
                travel_time_minutes=travel_time,
                free_flow_time_minutes=free_flow_time,
                color=color,
                trend=trend,
                trend_description=trend_desc,
                segments=segments,
                data_freshness=f"Updated {self._freshness_seconds()}s ago via TomTom + ASTraM fusion",
                updated_at=now,
                sources=["TomTom", "ASTraM"],
            ))

        return CorridorListResponse(
            corridors=corridors,
            total=len(corridors),
            timestamp=datetime.now(timezone.utc),
            demo_mode=self.tomtom.demo_mode,
        )

    async def get_corridor(self, corridor_id: str) -> CorridorStatus | None:
        """Get status of a single corridor by ID."""
        all_corridors = await self.get_all_corridors()
        for c in all_corridors.corridors:
            if c.corridor_id == corridor_id:
                return c
        return None

    async def get_heatmap_data(self) -> HeatmapResponse:
        """Get heatmap data for all corridors (GeoJSON-ready)."""
        all_corridors = await self.get_all_corridors()
        data = [
            HeatmapDataPoint(
                corridor_id=c.corridor_id,
                segments=c.segments,
            )
            for c in all_corridors.corridors
        ]
        return HeatmapResponse(
            data=data,
            timestamp=datetime.now(timezone.utc),
        )

    def _incident_matches_corridor(self, incident: dict, corridor: dict) -> bool:
        """Check if an incident is on or near a corridor."""
        inc_road = incident.get("road_name", "").lower()
        corridor_name = corridor["name"].lower()
        corridor_short = corridor.get("short_name", "").lower()

        # Simple keyword matching
        for keyword in corridor_short.split():
            if len(keyword) > 3 and keyword in inc_road:
                return True

        return False

    def _freshness_seconds(self) -> int:
        """Get data freshness in seconds."""
        if self.tomtom.last_fetched:
            delta = (datetime.now(timezone.utc) - self.tomtom.last_fetched).total_seconds()
            return int(delta)
        return 0
