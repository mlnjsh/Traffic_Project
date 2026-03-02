"""Pydantic schemas for Category 4: Heatmap & Visualization Queries.

Prompt 4.1: Real-Time Heatmap Generation
Prompt 4.2: Google Maps Integration Layer
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# --- Signal Status (Mappls-inspired) ---

class SignalPhase(str, Enum):
    GREEN = "green"
    RED = "red"
    AMBER = "amber"


class SignalStatus(BaseModel):
    """Signal countdown data per Prompt 4.1 overlay + Prompt 4.2 signal countdown bubbles."""
    junction_id: str
    junction_name: str
    lat: float
    lng: float
    current_phase: SignalPhase
    countdown_seconds: int  # seconds remaining in current phase
    cycle_time_seconds: int  # total cycle length
    green_time_seconds: int
    red_time_seconds: int
    pedestrian_phase: bool = False
    data_source: str = "Mappls"


class SignalListResponse(BaseModel):
    signals: list[SignalStatus]
    total: int
    coverage_note: str = "Signal countdown available at 1,000+ ASTraM-controlled junctions"
    timestamp: datetime
    demo_mode: bool = True


# --- Enhanced Heatmap with Overlay Metadata ---

class OverlayLayer(BaseModel):
    """A toggleable overlay layer per Prompt 4.1."""
    layer_id: str
    name: str
    description: str
    enabled_by_default: bool
    data_endpoint: str  # API path for this layer's data
    icon: str  # emoji for UI


class DataSourceInfo(BaseModel):
    """Data source metadata per Prompt 4.1."""
    name: str
    refresh_rate: str  # "30 seconds", "1 minute"
    coverage: str
    role: str  # "Speed/flow data", "Incident detection"


class EnhancedHeatmapResponse(BaseModel):
    """Enhanced heatmap metadata per Prompt 4.1 + 4.2."""
    data_sources: list[DataSourceInfo]
    overlay_layers: list[OverlayLayer]
    color_scale: dict = {
        "green": ">30 km/h, <30% congestion — free flow",
        "yellow": "20-30 km/h, 30-60% — moderate delay",
        "orange": "10-20 km/h, 60-100% — substantial delay",
        "red": "5-10 km/h, 100-150% — severe congestion",
        "black": "<5 km/h, >150% — gridlock",
    }
    refresh_interval_seconds: int = 30
    map_config: dict = {
        "center": {"lat": 12.9716, "lng": 77.5946},
        "zoom": 12,
        "map_type": "roadmap",
        "satellite_toggle": True,
    }
    timestamp: datetime
    demo_mode: bool = True


# --- Traffic Card (segment click popup) ---

class TrafficCardResponse(BaseModel):
    """Detailed traffic card for a road segment per Prompt 4.2 "tap segment" feature."""
    corridor_id: str
    corridor_name: str
    segment_road: str
    current_speed_kmh: float
    free_flow_speed_kmh: float
    congestion_pct: float
    color: str
    delay_minutes: float
    trend: str
    trend_description: str
    active_incidents: int
    construction_nearby: bool
    prediction_summary: str  # "Improving by ~20:30 (65% confidence)"
    data_freshness: str
    sources: list[str]
    timestamp: datetime
