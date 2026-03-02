"""Pydantic schemas for Prompt 1.1: Current Corridor Status."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CongestionColor(str, Enum):
    GREEN = "green"      # >30 km/h, <30% congestion
    YELLOW = "yellow"    # 20-30 km/h, 30-60%
    ORANGE = "orange"    # 10-20 km/h, 60-100%
    RED = "red"          # 5-10 km/h, 100-150%
    BLACK = "black"      # <5 km/h, >150%


class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"


class CorridorCoordinate(BaseModel):
    lat: float
    lng: float


class CorridorSegment(BaseModel):
    start: CorridorCoordinate
    end: CorridorCoordinate
    speed_kmh: float
    congestion_pct: float
    color: CongestionColor


class ActiveIncidentBrief(BaseModel):
    """Brief incident info embedded in corridor status."""
    type: str
    location: str
    severity: int = Field(ge=1, le=5)


class CorridorStatus(BaseModel):
    """Response schema for Prompt 1.1 — Current Corridor Status."""
    corridor_id: str
    name: str
    direction: str | None = None

    # 1. Current speed and congestion
    current_speed_kmh: float
    free_flow_speed_kmh: float
    congestion_pct: float

    # 2. Active incidents
    active_incidents: list[ActiveIncidentBrief] = []
    incident_count: int = 0

    # 3. Estimated delay vs free-flow
    delay_minutes: float
    travel_time_minutes: float
    free_flow_time_minutes: float

    # 4. Color code
    color: CongestionColor

    # 5. Trend prediction
    trend: TrendDirection
    trend_description: str

    # Segments for heatmap rendering
    segments: list[CorridorSegment] = []

    # Metadata
    data_freshness: str  # e.g., "Updated 30 seconds ago via TomTom + ASTraM fusion"
    updated_at: datetime
    sources: list[str] = ["TomTom", "ASTraM"]


class CorridorListResponse(BaseModel):
    corridors: list[CorridorStatus]
    total: int
    timestamp: datetime
    demo_mode: bool = True


class HeatmapDataPoint(BaseModel):
    corridor_id: str
    segments: list[CorridorSegment]


class HeatmapResponse(BaseModel):
    data: list[HeatmapDataPoint]
    timestamp: datetime
    color_scale: dict = {
        "green": ">30 km/h, <30% congestion",
        "yellow": "20-30 km/h, 30-60%",
        "orange": "10-20 km/h, 60-100%",
        "red": "5-10 km/h, 100-150%",
        "black": "<5 km/h, >150% gridlock",
    }
