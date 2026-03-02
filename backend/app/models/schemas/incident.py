"""Pydantic schemas for Prompt 1.2: Active Incident Report."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    JAM = "jam"
    ACCIDENT = "accident"
    CONSTRUCTION = "construction"
    WEATHER = "weather"
    BREAKDOWN = "vehicle_breakdown"
    DEBRIS = "debris"
    SIGNAL_MALFUNCTION = "signal_malfunction"
    FLOODING = "flooding"


class IncidentSeverity(int, Enum):
    MINIMAL = 1
    MINOR = 2
    MODERATE = 3
    MAJOR = 4
    CRITICAL = 5


class IncidentLocation(BaseModel):
    lat: float
    lng: float
    road_name: str
    nearest_landmark: str | None = None
    direction: str | None = None


class DiversionRoute(BaseModel):
    name: str
    via: str
    added_distance_km: float
    added_time_minutes: float
    current_conditions: str  # e.g., "Severe, 120-140% capacity"


class IncidentReport(BaseModel):
    """Response schema for Prompt 1.2 — Active Incident Report."""
    incident_id: str
    # 1. Incident type
    type: IncidentType
    type_label: str  # Human-readable: "Vehicle Breakdown", "Road Construction"

    # 2. Exact location
    location: IncidentLocation

    # 3. Severity rating (1-5)
    severity: int = Field(ge=1, le=5)
    severity_label: str  # "Critical", "Major", etc.

    # 4. Affected segment length
    affected_length_km: float

    # 5. Estimated additional delay
    delay_minutes: float

    # 6. Diversion routes
    diversions: list[DiversionRoute] = []

    # Additional context
    description: str
    start_time: datetime
    estimated_end_time: datetime | None = None
    is_active: bool = True
    source: str  # "ASTraM", "TomTom", "Citizen Report"
    last_updated: datetime


class IncidentListResponse(BaseModel):
    """Incidents sorted by severity (highest first) per Prompt 1.2."""
    incidents: list[IncidentReport]
    total_active: int
    corridor_filter: str | None = None
    timestamp: datetime
    data_freshness: str
    demo_mode: bool = True
