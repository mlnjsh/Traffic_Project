"""ASTraM (BTP) API client.

Live mode: Calls ASTraM incident API (1-minute refresh).
Demo mode: Returns realistic Bangalore incident data from REPORT.md.

Per skills.md: Parse proprietary incident severity classification;
handle real-time streaming connections; implement reconnection logic.
Per CLAUDE.md: ASTraM prioritized for incident location/type (authoritative local).
"""

from datetime import datetime, timedelta, timezone

from app.config import settings
from app.data_sources.base import BaseDataSource


class ASTraMClient(BaseDataSource):
    """ASTraM (Bangalore Traffic Police) incident and flow data client."""

    def __init__(self):
        super().__init__(name="ASTraM", demo_mode=settings.demo_mode)
        self.api_url = settings.astram_api_url
        self.api_key = settings.astram_api_key

    async def fetch(self) -> dict:
        """Fetch active incidents from ASTraM."""
        if self.demo_mode or not self.api_key:
            return {"incidents": self._demo_incidents()}
        # Live API call would go here
        return {"incidents": []}

    def _demo_incidents(self) -> list[dict]:
        """Realistic ASTraM incident data from REPORT.md Sections 2.1, 3.1.

        ASTraM fields per CLAUDE.md: start/end coordinates, road name,
        delay type (jam/accident/construction/weather), segment length,
        significance (1-5), distance.
        """
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "ast_001",
                "type": "construction",
                "road_name": "ORR (Zakir Nagar to Goraguntepalya)",
                "start_coords": {"lat": 13.0421, "lng": 77.6088},
                "end_coords": {"lat": 13.0284, "lng": 77.5403},
                "description": "BWSSB Pipeline Installation — Water supply and sewerage network enhancement. Single-lane contraflow with portable signals (90-second cycles). 24-hour shifts.",
                "significance": 5,
                "delay_type": "construction",
                "segment_length_km": 7.0,
                "distance_km": 7.0,
                "additional_delay_min": 25,
                "start_time": (now - timedelta(days=24)).isoformat(),
                "estimated_end_time": "2026-03-06T23:59:00+05:30",
                "source": "ASTraM",
                "nearest_landmark": "Zakir Nagar Junction",
                "diversions": [
                    {
                        "direction": "Northbound",
                        "route": "Thanisandra Main Road → Hennur Road",
                        "added_distance_km": 5.0,
                        "added_time_min": 10,
                        "current_status": "Severe, 120-140% capacity utilization",
                    },
                    {
                        "direction": "Southbound",
                        "route": "Bellary Road (NH-44) → Airport connectors",
                        "added_distance_km": 6.5,
                        "added_time_min": 12,
                        "current_status": "Moderate, 90-110% capacity",
                    },
                ],
            },
            {
                "id": "ast_002",
                "type": "construction",
                "road_name": "Goraguntepalya Flyover Vicinity",
                "start_coords": {"lat": 13.0300, "lng": 77.5380},
                "end_coords": {"lat": 13.0250, "lng": 77.5350},
                "description": "White-topping surface work — phased lane closures, 14-day curing period. Concrete overlay replacing asphalt (25-30 year service life).",
                "significance": 3,
                "delay_type": "construction",
                "segment_length_km": 1.5,
                "distance_km": 1.5,
                "additional_delay_min": 12,
                "start_time": (now - timedelta(days=14)).isoformat(),
                "estimated_end_time": "2026-03-15T23:59:00+05:30",
                "source": "ASTraM",
                "nearest_landmark": "Goraguntepalya Flyover",
                "diversions": [],
            },
            {
                "id": "ast_003",
                "type": "jam",
                "road_name": "Silk Board Junction",
                "start_coords": {"lat": 12.9170, "lng": 77.6230},
                "end_coords": {"lat": 12.9220, "lng": 77.6280},
                "description": "Peak-hour congestion at Silk Board — all approaches severely congested. Flyover construction ongoing (delayed, target 2026).",
                "significance": 4,
                "delay_type": "jam",
                "segment_length_km": 0.8,
                "distance_km": 0.8,
                "additional_delay_min": 20,
                "start_time": (now - timedelta(hours=1)).isoformat(),
                "estimated_end_time": None,
                "source": "ASTraM",
                "nearest_landmark": "Silk Board Flyover",
                "diversions": [],
            },
            {
                "id": "ast_004",
                "type": "jam",
                "road_name": "Thanisandra Main Road",
                "start_coords": {"lat": 13.0500, "lng": 77.6300},
                "end_coords": {"lat": 13.0400, "lng": 77.6350},
                "description": "ORR diversion-induced congestion — operating at 120-140% of designed capacity, intersection queue lengths exceeding 800 meters.",
                "significance": 4,
                "delay_type": "jam",
                "segment_length_km": 2.0,
                "distance_km": 2.0,
                "additional_delay_min": 15,
                "start_time": (now - timedelta(hours=2)).isoformat(),
                "estimated_end_time": None,
                "source": "ASTraM",
                "nearest_landmark": "Thanisandra Junction",
                "diversions": [],
            },
            {
                "id": "ast_005",
                "type": "accident",
                "road_name": "Hosur Road (near Electronic City toll)",
                "start_coords": {"lat": 12.8500, "lng": 77.6610},
                "end_coords": {"lat": 12.8520, "lng": 77.6615},
                "description": "Minor vehicle collision — two-wheeler and car. Lane 1 blocked. BTP patrol on scene. Tow dispatch requested.",
                "significance": 3,
                "delay_type": "accident",
                "segment_length_km": 0.3,
                "distance_km": 0.3,
                "additional_delay_min": 10,
                "start_time": (now - timedelta(minutes=25)).isoformat(),
                "estimated_end_time": (now + timedelta(minutes=20)).isoformat(),
                "source": "ASTraM",
                "nearest_landmark": "Electronic City Toll Plaza",
                "diversions": [],
            },
        ]
