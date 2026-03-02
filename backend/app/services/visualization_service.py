"""Visualization service — implements Category 4: Heatmap & Visualization Queries.

Prompt 4.1: Real-Time Heatmap Generation
- Data sources: ASTraM (CCTV), TomTom (flow), IoT sensors, floating car data
- Color coding: Green/Yellow/Orange/Red/Black
- Overlay layers: incidents, construction, signals, emergency, weather
- Update every 30-60 seconds with trend arrows

Prompt 4.2: Google Maps Integration Layer
- Custom overlays on Google Maps
- Signal countdown bubbles
- Traffic card on segment tap
- "When will this clear?" popup
"""

import random
from datetime import datetime, timezone

from app.data_sources.bangalore_corridors import CORRIDORS
from app.services.traffic_service import TrafficService
from app.services.prediction_service import PredictionService
from app.models.schemas.visualization import (
    DataSourceInfo,
    EnhancedHeatmapResponse,
    OverlayLayer,
    SignalListResponse,
    SignalPhase,
    SignalStatus,
    TrafficCardResponse,
)


# Major junctions in Bangalore with signal infrastructure
BANGALORE_JUNCTIONS = [
    {"id": "silk_board_jn", "name": "Silk Board Junction", "lat": 12.9170, "lng": 77.6230, "cycle": 180},
    {"id": "marathahalli_jn", "name": "Marathahalli Bridge Junction", "lat": 12.9570, "lng": 77.7010, "cycle": 150},
    {"id": "hebbal_flyover", "name": "Hebbal Flyover Junction", "lat": 13.0358, "lng": 77.5970, "cycle": 120},
    {"id": "kr_puram_jn", "name": "KR Puram Junction", "lat": 13.0050, "lng": 77.6890, "cycle": 150},
    {"id": "banashankari_jn", "name": "Banashankari Signal", "lat": 12.9255, "lng": 77.5468, "cycle": 120},
    {"id": "jayanagar_4th_block", "name": "Jayanagar 4th Block", "lat": 12.9259, "lng": 77.5838, "cycle": 90},
    {"id": "mg_road_signal", "name": "MG Road / Brigade Road", "lat": 12.9747, "lng": 77.6060, "cycle": 120},
    {"id": "indiranagar_100ft", "name": "Indiranagar 100 Feet Road", "lat": 12.9784, "lng": 77.6408, "cycle": 100},
    {"id": "koramangala_sony", "name": "Koramangala Sony Signal", "lat": 12.9352, "lng": 77.6245, "cycle": 110},
    {"id": "bellandur_gate", "name": "Bellandur Gate Junction", "lat": 12.9260, "lng": 77.6620, "cycle": 140},
    {"id": "whitefield_itpl", "name": "Whitefield ITPL Main Gate", "lat": 12.9850, "lng": 77.7260, "cycle": 130},
    {"id": "electronic_city_toll", "name": "Electronic City Toll Gate", "lat": 12.8450, "lng": 77.6600, "cycle": 160},
    {"id": "majestic_jn", "name": "Majestic Bus Stand Junction", "lat": 12.9766, "lng": 77.5713, "cycle": 120},
    {"id": "yeshwanthpur_circle", "name": "Yeshwanthpur Circle", "lat": 13.0226, "lng": 77.5500, "cycle": 110},
    {"id": "thanisandra_jn", "name": "Thanisandra Main Road Junction", "lat": 13.0500, "lng": 77.6300, "cycle": 100},
]


class VisualizationService:
    """Service for Category 4 — Heatmap & Visualization."""

    def __init__(self):
        self.traffic_service = TrafficService()
        self.prediction_service = PredictionService()

    async def get_signal_status(self) -> SignalListResponse:
        """Get real-time signal status for major junctions (Mappls-style)."""
        now = datetime.now()
        signals = []

        for jn in BANGALORE_JUNCTIONS:
            cycle = jn["cycle"]
            # Simulate signal state based on current time
            elapsed = (now.minute * 60 + now.second) % cycle
            green_time = int(cycle * 0.45)  # ~45% green
            red_time = cycle - green_time - 5  # 5s amber

            if elapsed < green_time:
                phase = SignalPhase.GREEN
                countdown = green_time - elapsed
            elif elapsed < green_time + 5:
                phase = SignalPhase.AMBER
                countdown = green_time + 5 - elapsed
            else:
                phase = SignalPhase.RED
                countdown = cycle - elapsed

            signals.append(SignalStatus(
                junction_id=jn["id"],
                junction_name=jn["name"],
                lat=jn["lat"],
                lng=jn["lng"],
                current_phase=phase,
                countdown_seconds=countdown,
                cycle_time_seconds=cycle,
                green_time_seconds=green_time,
                red_time_seconds=red_time,
                pedestrian_phase=random.random() > 0.7,
            ))

        return SignalListResponse(
            signals=signals,
            total=len(signals),
            timestamp=datetime.now(timezone.utc),
        )

    async def get_enhanced_heatmap(self) -> EnhancedHeatmapResponse:
        """Get enhanced heatmap configuration with data sources and overlay layers."""
        data_sources = [
            DataSourceInfo(
                name="ASTraM (BTP)",
                refresh_rate="1 minute",
                coverage="1,500+ CCTV cameras with YOLOv8 AI analytics — covers ~60% major roads",
                role="Incident detection, vehicle classification, trajectory analysis",
            ),
            DataSourceInfo(
                name="TomTom Traffic API",
                refresh_rate="30 seconds",
                coverage="Network-wide speed, travel times, congestion %",
                role="Primary speed/flow data — global consistency",
            ),
            DataSourceInfo(
                name="IoT Sensors",
                refresh_rate="15 seconds",
                coverage="200+ locations with volume, occupancy, speed",
                role="Ground-truth validation at key intersections",
            ),
            DataSourceInfo(
                name="Floating Car Data",
                refresh_rate="30 seconds",
                coverage="Probe vehicles from TomTom, Google, Mappls",
                role="Real-time speed sampling across road network",
            ),
        ]

        overlay_layers = [
            OverlayLayer(
                layer_id="congestion_heatmap",
                name="Congestion Heatmap",
                description="ASTraM + TomTom fused congestion polylines (Green→Black)",
                enabled_by_default=True,
                data_endpoint="/api/v1/heatmap/data",
                icon="🔥",
            ),
            OverlayLayer(
                layer_id="incidents",
                name="Active Incidents",
                description="Accident, breakdown, debris markers with severity icons",
                enabled_by_default=True,
                data_endpoint="/api/v1/incidents",
                icon="⚠",
            ),
            OverlayLayer(
                layer_id="construction",
                name="Construction Zones",
                description="Polygon boundaries with completion % and project info",
                enabled_by_default=True,
                data_endpoint="/api/v1/construction/zones",
                icon="🚧",
            ),
            OverlayLayer(
                layer_id="signals",
                name="Signal Status",
                description="Green/red countdown at ASTraM-controlled junctions (Mappls data)",
                enabled_by_default=False,
                data_endpoint="/api/v1/visualization/signals",
                icon="🚦",
            ),
            OverlayLayer(
                layer_id="emergency",
                name="Emergency Corridors",
                description="Active e-Path green corridor routes",
                enabled_by_default=False,
                data_endpoint="/api/v1/visualization/emergency",
                icon="🚑",
            ),
            OverlayLayer(
                layer_id="weather",
                name="Weather Impact",
                description="Flooding zones, visibility reduction areas",
                enabled_by_default=False,
                data_endpoint="/api/v1/visualization/weather",
                icon="🌧",
            ),
        ]

        return EnhancedHeatmapResponse(
            data_sources=data_sources,
            overlay_layers=overlay_layers,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_traffic_card(self, corridor_id: str) -> TrafficCardResponse | None:
        """Get detailed traffic card for segment tap (Prompt 4.2)."""
        corridor = await self.traffic_service.get_corridor(corridor_id)
        if not corridor:
            return None

        # Get prediction summary
        prediction = await self.prediction_service.get_prediction(corridor_id)
        if prediction:
            st = prediction.short_term
            mt = prediction.medium_term
            pred_summary = (
                f"{st.direction.capitalize()} — clears by ~{mt.estimated_clear_time} "
                f"({mt.confidence_pct:.0f}% confidence)"
            )
        else:
            pred_summary = "Prediction data unavailable"

        # Check construction nearby
        from app.services.construction_service import ConstructionService
        constr_service = ConstructionService()
        zones = await constr_service.get_all_zones()
        construction_nearby = any(
            any(corridor.name.lower().split()[0] in r.lower() for r in z.affected_roads)
            for z in zones.zones
        )

        return TrafficCardResponse(
            corridor_id=corridor.corridor_id,
            corridor_name=corridor.name,
            segment_road=corridor.name.split("(")[0].strip() if "(" in corridor.name else corridor.name,
            current_speed_kmh=corridor.current_speed_kmh,
            free_flow_speed_kmh=corridor.free_flow_speed_kmh,
            congestion_pct=corridor.congestion_pct,
            color=corridor.color.value,
            delay_minutes=corridor.delay_minutes,
            trend=corridor.trend.value,
            trend_description=corridor.trend_description,
            active_incidents=corridor.incident_count,
            construction_nearby=construction_nearby,
            prediction_summary=pred_summary,
            data_freshness=corridor.data_freshness,
            sources=corridor.sources,
            timestamp=datetime.now(timezone.utc),
        )
