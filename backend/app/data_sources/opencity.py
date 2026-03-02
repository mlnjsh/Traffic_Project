"""OpenCity Bengaluru data client.

Provides construction zone data from REPORT.md Section 3.1 and 3.2.
Live mode: Downloads CSV/KML from OpenCity portal (daily batch).
Demo mode: Returns curated construction project data.

Per skills.md: Automated periodic download; KML geospatial parsing;
historical data integration with real-time feeds.
"""

from datetime import date, datetime, timezone

from app.data_sources.base import BaseDataSource


class OpenCityClient(BaseDataSource):
    """OpenCity Bengaluru Urban Data Portal client."""

    def __init__(self):
        super().__init__(name="OpenCity", demo_mode=True)

    async def fetch(self) -> dict:
        """Fetch construction zone and infrastructure project data."""
        return {"construction_zones": self._demo_construction_zones()}

    def _demo_construction_zones(self) -> list[dict]:
        """Construction data from REPORT.md Sections 3.1 and 3.2.

        All data points sourced directly from the report with
        real coordinates, dates, and impact metrics.
        """
        return [
            {
                "id": "cz_001",
                "project_name": "BWSSB Pipeline Installation",
                "agency": "BWSSB",
                "location_description": "ORR Zakir Nagar to Goraguntepalya (~7 km)",
                "affected_roads": [
                    "Outer Ring Road (Zakir Nagar section)",
                    "Outer Ring Road (Goraguntepalya section)",
                ],
                "start_coords": {"lat": 13.0421, "lng": 77.6088},
                "end_coords": {"lat": 13.0284, "lng": 77.5403},
                "lane_restriction": "Single-lane contraflow",
                "traffic_management": "Portable signals (90-second cycles)",
                "start_date": "2026-02-06",
                "end_date": "2026-03-06",
                "completion_pct": 89.0,
                "milestones": [
                    {"name": "Trench completion", "target_date": "2026-02-20", "status": "Complete", "risk": None},
                    {"name": "Pipe laying/jointing", "target_date": "2026-02-28", "status": "95% complete", "risk": "Technical complications"},
                    {"name": "Pressure testing", "target_date": "2026-03-04", "status": "In progress", "risk": "Test failure → repair delay"},
                    {"name": "Surface restoration", "target_date": "2026-03-06", "status": "Pending", "risk": "Weather, material availability"},
                ],
                "capacity_reduction_pct": 72.5,
                "additional_delay_minutes": "15-30",
                "peak_amplification": {
                    "normal_peak_window": "17:30-19:00",
                    "amplified_window": "16:30-21:30",
                    "extension_hours": 3.5,
                },
                "diversions": [
                    {
                        "direction": "Northbound",
                        "primary_alternative": "Thanisandra Main Road → Hennur Road",
                        "added_distance_km": 5.0,
                        "time_penalty_freeflow": "+8-12 min",
                        "current_conditions": "Severe, 120-140% capacity",
                    },
                    {
                        "direction": "Southbound",
                        "primary_alternative": "Bellary Road (NH-44) → Airport connectors",
                        "added_distance_km": 6.5,
                        "time_penalty_freeflow": "+10-15 min",
                        "current_conditions": "Moderate, 90-110% capacity",
                    },
                ],
                "diversion_compliance_pct": 67.5,
                "source": "OpenCity / newsfirstprime.com / Kaggle",
            },
            {
                "id": "cz_002",
                "project_name": "White-Topping — Goraguntepalya Flyover Vicinity",
                "agency": "BBMP",
                "location_description": "Goraguntepalya flyover vicinity, North Bangalore",
                "affected_roads": ["Goraguntepalya flyover approach roads"],
                "start_coords": {"lat": 13.0300, "lng": 77.5380},
                "end_coords": {"lat": 13.0250, "lng": 77.5350},
                "lane_restriction": "Phased lane closures",
                "traffic_management": "Traffic marshals + temporary barriers",
                "start_date": "2026-02-15",
                "end_date": "2026-03-15",
                "completion_pct": 60.0,
                "milestones": [
                    {"name": "Surface milling", "target_date": "2026-02-22", "status": "Complete", "risk": None},
                    {"name": "Concrete pouring Phase 1", "target_date": "2026-03-01", "status": "Complete", "risk": None},
                    {"name": "Concrete pouring Phase 2", "target_date": "2026-03-08", "status": "In progress", "risk": "Weather delay"},
                    {"name": "Curing period (14 days)", "target_date": "2026-03-15", "status": "Pending", "risk": "Cannot be accelerated"},
                ],
                "capacity_reduction_pct": 40.0,
                "additional_delay_minutes": "10-15",
                "peak_amplification": {
                    "normal_peak_window": "18:00-19:30",
                    "amplified_window": "17:00-21:00",
                    "extension_hours": 2.5,
                },
                "diversions": [],
                "diversion_compliance_pct": None,
                "source": "OpenCity / Kaggle",
            },
            {
                "id": "cz_003",
                "project_name": "Rajajinagar Lane Widening",
                "agency": "BBMP",
                "location_description": "Rajajinagar Industrial Corridor, West Bangalore",
                "affected_roads": ["Rajajinagar Main Road", "Industrial Area connector roads"],
                "start_coords": {"lat": 12.9900, "lng": 77.5500},
                "end_coords": {"lat": 12.9850, "lng": 77.5450},
                "lane_restriction": "Single-lane bidirectional with directional imbalances",
                "traffic_management": "Night work (22:00-06:00) for major disruptions",
                "start_date": "2026-01-15",
                "end_date": "2026-04-30",
                "completion_pct": 45.0,
                "milestones": [
                    {"name": "Phase 1 — Utility relocation", "target_date": "2026-02-15", "status": "Complete", "risk": None},
                    {"name": "Phase 2 — Road widening (south)", "target_date": "2026-03-15", "status": "In progress", "risk": "Freight traffic coordination"},
                    {"name": "Phase 3 — Road widening (north)", "target_date": "2026-04-15", "status": "Pending", "risk": "Monsoon risk if delayed"},
                    {"name": "Surface and marking", "target_date": "2026-04-30", "status": "Pending", "risk": None},
                ],
                "capacity_reduction_pct": 35.0,
                "additional_delay_minutes": "8-15",
                "peak_amplification": None,
                "diversions": [],
                "diversion_compliance_pct": None,
                "source": "OpenCity",
            },
            {
                "id": "cz_004",
                "project_name": "Silk Board Junction Flyover",
                "agency": "BBMP / NHAI",
                "location_description": "Silk Board Junction — ORR / Hosur Road intersection",
                "affected_roads": ["ORR (Silk Board section)", "Hosur Road"],
                "start_coords": {"lat": 12.9170, "lng": 77.6230},
                "end_coords": {"lat": 12.9200, "lng": 77.6260},
                "lane_restriction": "Partial lane restriction near pillars",
                "traffic_management": "Signal-controlled diversions",
                "start_date": "2023-06-01",
                "end_date": "2026-12-31",
                "completion_pct": 65.0,
                "milestones": [
                    {"name": "Foundation and pillars", "target_date": "2025-06-30", "status": "Complete", "risk": None},
                    {"name": "Deck slab casting", "target_date": "2026-06-30", "status": "In progress", "risk": "Multiple delays historically"},
                    {"name": "Surface work and ramps", "target_date": "2026-10-31", "status": "Pending", "risk": None},
                    {"name": "Opening to traffic", "target_date": "2026-12-31", "status": "Pending", "risk": "Delayed multiple times"},
                ],
                "capacity_reduction_pct": 15.0,
                "additional_delay_minutes": "5-10",
                "peak_amplification": None,
                "diversions": [],
                "diversion_compliance_pct": None,
                "source": "OpenCity",
            },
            {
                "id": "cz_005",
                "project_name": "Namma Metro Phase 2B (Whitefield-Challaghatta)",
                "agency": "BMRCL",
                "location_description": "12 station construction sites along 15-km corridor (Whitefield to Challaghatta)",
                "affected_roads": ["Whitefield Main Road", "Old Madras Road sections", "Various local roads"],
                "start_coords": {"lat": 12.9700, "lng": 77.7500},
                "end_coords": {"lat": 12.9600, "lng": 77.6000},
                "lane_restriction": "Lane occupation reducing road capacity 20-30% in vicinities",
                "traffic_management": "Station-specific traffic management plans",
                "start_date": "2024-01-01",
                "end_date": "2028-12-31",
                "completion_pct": 25.0,
                "milestones": [
                    {"name": "Station box excavation (4 of 12)", "target_date": "2026-06-30", "status": "In progress", "risk": "Utility conflicts"},
                    {"name": "Viaduct erection (Phase 1)", "target_date": "2026-12-31", "status": "Pending", "risk": None},
                    {"name": "Systems installation", "target_date": "2027-12-31", "status": "Pending", "risk": None},
                    {"name": "Phased opening", "target_date": "2028-12-31", "status": "Pending", "risk": "2-3 year active work per station"},
                ],
                "capacity_reduction_pct": 25.0,
                "additional_delay_minutes": "5-15",
                "peak_amplification": None,
                "diversions": [],
                "diversion_compliance_pct": None,
                "source": "OpenCity / BMRCL",
            },
        ]
