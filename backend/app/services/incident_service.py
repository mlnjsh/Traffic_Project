"""Incident service — implements Prompt 1.2: Active Incident Report.

Provides:
1. Incident type: jam, accident, construction, weather, vehicle breakdown
2. Exact location with road name and nearest landmark
3. Severity rating (1-5 significance scale)
4. Affected segment length in km
5. Estimated additional delay in minutes
6. Current diversion routes with comparative travel times

Incidents sorted by severity (highest first) per Prompt 1.2.
ASTraM prioritized for incident data (authoritative local) per CLAUDE.md.
"""

from datetime import datetime, timezone

from app.data_sources.astram import ASTraMClient
from app.data_sources.tomtom import TomTomClient
from app.models.schemas.incident import (
    DiversionRoute,
    IncidentListResponse,
    IncidentLocation,
    IncidentReport,
    IncidentType,
)


SEVERITY_LABELS = {
    1: "Minimal",
    2: "Minor",
    3: "Moderate",
    4: "Major",
    5: "Critical",
}

TYPE_LABELS = {
    "jam": "Traffic Jam",
    "accident": "Road Accident",
    "construction": "Road Construction",
    "weather": "Weather Event",
    "vehicle_breakdown": "Vehicle Breakdown",
    "breakdown": "Vehicle Breakdown",
    "debris": "Road Debris",
    "signal_malfunction": "Signal Malfunction",
    "flooding": "Road Flooding",
}


class IncidentService:
    """Service for Prompt 1.2 — Active Incident Report."""

    def __init__(self):
        self.astram = ASTraMClient()
        self.tomtom = TomTomClient()

    async def get_active_incidents(self, corridor_filter: str | None = None) -> IncidentListResponse:
        """Get all active incidents, sorted by severity (highest first).

        ASTraM is primary source, TomTom supplements with additional incidents.
        Deduplication: incidents within same road and type are merged.
        """
        # ASTraM is authoritative for incidents per CLAUDE.md
        astram_data = await self.astram.fetch()
        astram_incidents = astram_data.get("incidents", [])

        # TomTom supplements
        tomtom_incidents = await self.tomtom.fetch_incidents()

        # Merge and deduplicate (ASTraM takes priority)
        all_incidents = self._merge_incidents(astram_incidents, tomtom_incidents)

        # Filter by corridor if requested
        if corridor_filter:
            all_incidents = [
                inc for inc in all_incidents
                if corridor_filter.lower() in inc.get("road_name", "").lower()
            ]

        # Convert to response models
        reports = []
        for inc in all_incidents:
            inc_type = self._normalize_type(inc.get("type", "jam"))
            severity = min(inc.get("significance", inc.get("severity", 3)), 5)

            diversions = [
                DiversionRoute(
                    name=d.get("direction", "Alternative"),
                    via=d.get("route", d.get("primary_alternative", "")),
                    added_distance_km=d.get("added_distance_km", 0),
                    added_time_minutes=d.get("added_time_min", d.get("time_penalty_freeflow", 0)),
                    current_conditions=d.get("current_status", d.get("current_conditions", "Unknown")),
                )
                for d in inc.get("diversions", [])
            ]

            start_coords = inc.get("start_coords", inc.get("location", {}))

            reports.append(IncidentReport(
                incident_id=inc.get("id", "unknown"),
                type=inc_type,
                type_label=TYPE_LABELS.get(inc_type, inc_type.replace("_", " ").title()),
                location=IncidentLocation(
                    lat=start_coords.get("lat", 0),
                    lng=start_coords.get("lng", 0),
                    road_name=inc.get("road_name", "Unknown"),
                    nearest_landmark=inc.get("nearest_landmark"),
                    direction=None,
                ),
                severity=severity,
                severity_label=SEVERITY_LABELS.get(severity, "Unknown"),
                affected_length_km=inc.get("segment_length_km", inc.get("length_km", 0)),
                delay_minutes=inc.get("additional_delay_min", inc.get("delay_seconds", 0) / 60),
                diversions=diversions,
                description=inc.get("description", ""),
                start_time=datetime.fromisoformat(inc["start_time"]) if isinstance(inc.get("start_time"), str) else datetime.now(timezone.utc),
                estimated_end_time=self._parse_datetime(inc.get("estimated_end_time")),
                is_active=True,
                source=inc.get("source", "Unknown"),
                last_updated=datetime.now(timezone.utc),
            ))

        # Sort by severity descending (highest first per Prompt 1.2)
        reports.sort(key=lambda r: r.severity, reverse=True)

        return IncidentListResponse(
            incidents=reports,
            total_active=len(reports),
            corridor_filter=corridor_filter,
            timestamp=datetime.now(timezone.utc),
            data_freshness=f"ASTraM: 1-min refresh | TomTom: 30-sec refresh | Fused {len(reports)} active incidents",
            demo_mode=self.astram.demo_mode,
        )

    async def get_incident(self, incident_id: str) -> IncidentReport | None:
        """Get a single incident by ID."""
        all_incidents = await self.get_active_incidents()
        for inc in all_incidents.incidents:
            if inc.incident_id == incident_id:
                return inc
        return None

    def _merge_incidents(self, astram: list[dict], tomtom: list[dict]) -> list[dict]:
        """Merge incidents from both sources. ASTraM takes priority."""
        # Use ASTraM incidents as base
        merged = list(astram)
        astram_roads = {inc.get("road_name", "").lower() for inc in astram}

        # Add TomTom incidents that don't overlap with ASTraM
        for tt_inc in tomtom:
            tt_road = tt_inc.get("road_name", "").lower()
            if not any(keyword in tt_road for keyword in astram_roads if len(keyword) > 5):
                merged.append(tt_inc)

        return merged

    def _normalize_type(self, raw_type: str) -> str:
        """Normalize incident type string to IncidentType enum value."""
        mapping = {
            "jam": "jam",
            "accident": "accident",
            "construction": "construction",
            "weather": "weather",
            "breakdown": "vehicle_breakdown",
            "vehicle_breakdown": "vehicle_breakdown",
            "debris": "debris",
            "flooding": "flooding",
        }
        return mapping.get(raw_type.lower(), "jam")

    def _parse_datetime(self, value) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except (ValueError, TypeError):
            return None
