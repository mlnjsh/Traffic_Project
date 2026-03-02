"""TomTom Traffic API client.

Live mode: Calls TomTom Traffic Flow + Incidents APIs (30-sec refresh, freemium tier).
Demo mode: Returns realistic data from REPORT.md Section 2.2 time-based patterns.

Per skills.md: Implement freemium tier rate limiting; parse standardized congestion
levels (0-100%); handle batch historical data for pattern analysis.
"""

import random
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.data_sources.base import BaseDataSource
from app.data_sources.bangalore_corridors import CORRIDORS


def _get_time_based_congestion() -> dict[str, dict]:
    """Generate congestion levels based on current time of day.

    Data from REPORT.md Section 2.2:
    - 16:30: 120% congestion, 22 km/h
    - 17:30: 150%, 18 km/h
    - 18:00: 183%, 13.9 km/h (PEAK)
    - 19:00: 170%, 15 km/h
    - 20:00: 140%, 19 km/h
    - 21:30: 90%, 28 km/h
    - 02:00-06:00: <20%, free flow
    """
    now = datetime.now()
    hour = now.hour + now.minute / 60.0

    # Base congestion by time of day (from REPORT.md Table 11)
    if 2.0 <= hour < 6.0:
        base_congestion = 15.0
        base_speed_factor = 0.90  # near free flow
    elif 6.0 <= hour < 7.0:
        base_congestion = 30.0
        base_speed_factor = 0.75
    elif 7.0 <= hour < 10.0:
        base_congestion = 100.0  # morning peak
        base_speed_factor = 0.45
    elif 10.0 <= hour < 16.0:
        base_congestion = 60.0
        base_speed_factor = 0.60
    elif 16.0 <= hour < 16.5:
        base_congestion = 120.0
        base_speed_factor = 0.44  # 22 km/h on 50 free flow
    elif 16.5 <= hour < 17.5:
        base_congestion = 150.0
        base_speed_factor = 0.36  # 18 km/h
    elif 17.5 <= hour < 18.5:
        base_congestion = 183.0  # PEAK from TomTom 2025
        base_speed_factor = 0.28  # 13.9 km/h
    elif 18.5 <= hour < 19.5:
        base_congestion = 170.0
        base_speed_factor = 0.30  # 15 km/h
    elif 19.5 <= hour < 20.5:
        base_congestion = 140.0
        base_speed_factor = 0.38  # 19 km/h
    elif 20.5 <= hour < 21.5:
        base_congestion = 90.0
        base_speed_factor = 0.56  # 28 km/h
    else:
        base_congestion = 40.0
        base_speed_factor = 0.70

    # Per-corridor variation (from REPORT.md Section 2.1 & 2.3)
    corridor_multipliers = {
        "orr_silk_board": 1.15,        # ORR consistently worst
        "orr_zakir_nagar": 1.40,       # BWSSB construction: 70-75% capacity reduction
        "bellandur_road": 1.10,        # High volume intersections
        "whitefield_main": 1.20,       # Tech corridor tidal flows
        "electronic_city": 1.05,       # Shift-based, less peaky
        "bannerghatta_road": 0.95,     # Sustained but less extreme
        "cbd_mg_road": 1.00,           # Dense but manageable
        "thanisandra_hennur": 1.25,    # ORR diversion demand (120-140% capacity)
    }

    results = {}
    for corridor in CORRIDORS:
        cid = corridor["id"]
        multiplier = corridor_multipliers.get(cid, 1.0)
        noise = random.uniform(-5, 5)

        congestion = min(base_congestion * multiplier + noise, 250.0)
        speed = corridor["free_flow_speed"] * base_speed_factor / multiplier
        speed = max(speed + random.uniform(-2, 2), 3.0)  # minimum 3 km/h

        results[cid] = {
            "speed_kmh": round(speed, 1),
            "free_flow_speed_kmh": corridor["free_flow_speed"],
            "congestion_pct": round(max(congestion, 0), 1),
        }

    return results


class TomTomClient(BaseDataSource):
    """TomTom Traffic Flow + Incidents API client."""

    def __init__(self):
        super().__init__(name="TomTom", demo_mode=settings.demo_mode)
        self.api_key = settings.tomtom_api_key
        self.base_url = "https://api.tomtom.com"

    async def fetch(self) -> dict:
        """Fetch traffic flow data for all Bangalore corridors."""
        if self.demo_mode or not self.api_key:
            return self._demo_flow_data()
        return await self._live_flow_data()

    async def fetch_incidents(self) -> list[dict]:
        """Fetch active traffic incidents."""
        if self.demo_mode or not self.api_key:
            return self._demo_incidents()
        return await self._live_incidents()

    def _demo_flow_data(self) -> dict:
        """Realistic demo data based on REPORT.md time patterns."""
        self.last_fetched = datetime.now(timezone.utc)
        return _get_time_based_congestion()

    def _demo_incidents(self) -> list[dict]:
        """Demo incidents based on REPORT.md Section 2.1.2."""
        self.last_fetched = datetime.now(timezone.utc)
        return [
            {
                "id": "tt_inc_001",
                "type": "construction",
                "location": {"lat": 13.0350, "lng": 77.5750},
                "road_name": "ORR (Zakir Nagar - Goraguntepalya)",
                "description": "BWSSB Pipeline Installation — single-lane contraflow, 15-30 min additional delay",
                "severity": 5,
                "delay_seconds": 1500,
                "length_km": 7.0,
                "source": "TomTom",
            },
            {
                "id": "tt_inc_002",
                "type": "jam",
                "location": {"lat": 12.9260, "lng": 77.6620},
                "road_name": "Bellandur Junction",
                "description": "Peak-hour congestion — cycle failure at Bellandur Junction, queue spillback 1.2 km",
                "severity": 4,
                "delay_seconds": 900,
                "length_km": 1.5,
                "source": "TomTom",
            },
            {
                "id": "tt_inc_003",
                "type": "jam",
                "location": {"lat": 12.9750, "lng": 77.7400},
                "road_name": "Whitefield Main Road (near ITPL)",
                "description": "Outbound tidal flow congestion — 45-60 min delays during 17:00-21:00 window",
                "severity": 4,
                "delay_seconds": 1200,
                "length_km": 3.0,
                "source": "TomTom",
            },
        ]

    async def _live_flow_data(self) -> dict:
        """Call TomTom Traffic Flow API."""
        bbox = settings.bbox_tuple
        url = f"{self.base_url}/traffic/services/4/flowSegmentData/absolute/10/json"
        results = {}
        async with httpx.AsyncClient(timeout=30) as client:
            for corridor in CORRIDORS:
                seg = corridor["segments"][0]
                params = {
                    "key": self.api_key,
                    "point": f"{seg['start']['lat']},{seg['start']['lng']}",
                }
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("flowSegmentData", {})
                    speed = data.get("currentSpeed", 0)
                    free_flow = data.get("freeFlowSpeed", corridor["free_flow_speed"])
                    congestion = max(0, (1 - speed / free_flow) * 100) if free_flow else 0
                    results[corridor["id"]] = {
                        "speed_kmh": round(speed, 1),
                        "free_flow_speed_kmh": round(free_flow, 1),
                        "congestion_pct": round(congestion, 1),
                    }
        self.last_fetched = datetime.now(timezone.utc)
        return results

    async def _live_incidents(self) -> list[dict]:
        """Call TomTom Traffic Incidents API."""
        bbox = settings.bbox_tuple
        url = f"{self.base_url}/traffic/services/5/incidentDetails"
        params = {
            "key": self.api_key,
            "bbox": f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}",
            "fields": "{incidents{type,geometry{type,coordinates},properties{iconCategory,magnitudeOfDelay,events{description},startTime,endTime,from,to,length,delay,roadNumbers}}}",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                incidents = []
                for inc in data.get("incidents", []):
                    props = inc.get("properties", {})
                    coords = inc.get("geometry", {}).get("coordinates", [[0, 0]])[0]
                    incidents.append({
                        "id": f"tt_{id(inc)}",
                        "type": self._map_incident_type(props.get("iconCategory", 0)),
                        "location": {"lat": coords[1], "lng": coords[0]},
                        "road_name": props.get("from", "Unknown"),
                        "description": props.get("events", [{}])[0].get("description", ""),
                        "severity": min(props.get("magnitudeOfDelay", 1), 5),
                        "delay_seconds": props.get("delay", 0),
                        "length_km": round(props.get("length", 0) / 1000, 2),
                        "source": "TomTom",
                    })
                self.last_fetched = datetime.now(timezone.utc)
                return incidents
        return []

    @staticmethod
    def _map_incident_type(icon_category: int) -> str:
        mapping = {0: "jam", 1: "accident", 2: "weather", 3: "construction", 6: "breakdown"}
        return mapping.get(icon_category, "jam")
