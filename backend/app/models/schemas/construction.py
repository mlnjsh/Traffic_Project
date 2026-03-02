"""Pydantic schemas for Prompt 1.3: Construction Zone Status."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class ProjectMilestone(BaseModel):
    name: str
    target_date: date
    status: str  # "Complete", "In progress", "Pending", "95% complete"
    risk_factor: str | None = None


class PeakAmplification(BaseModel):
    normal_peak_window: str      # e.g., "17:30-19:00"
    amplified_window: str        # e.g., "16:30-21:30"
    extension_hours: float       # e.g., 3.5
    description: str


class DiversionInfo(BaseModel):
    direction: str               # "Northbound", "Southbound"
    primary_alternative: str     # "Thanisandra Main Road -> Hennur Road"
    added_distance_km: float
    time_penalty_freeflow: str   # "+8-12 min (free flow)"
    current_conditions: str      # "Severe, 120-140% capacity"


class ConstructionZone(BaseModel):
    """Response schema for Prompt 1.3 — Construction Zone Status."""
    zone_id: str

    # 1. Project name and agency
    project_name: str
    agency: str  # BWSSB, BBMP, Metro/BMRCL, etc.

    # 2. Exact location with affected segments
    location_description: str
    affected_roads: list[str]
    start_coordinates: dict  # {"lat": 13.0421, "lng": 77.6088}
    end_coordinates: dict    # {"lat": 13.0284, "lng": 77.5403}

    # 3. Lane restrictions
    lane_restriction: str    # "Single-lane contraflow", "Full closure", etc.
    traffic_management: str  # "Portable signals (90s cycles)"

    # 4. Dates and completion confidence
    start_date: date
    end_date: date
    completion_confidence_pct: float = Field(ge=0, le=100)
    uncertainty_days: int    # +-X days

    # 5. Current progress
    completion_pct: float = Field(ge=0, le=100)
    milestones: list[ProjectMilestone] = []

    # 6. Official diversion routes
    diversions: list[DiversionInfo] = []
    diversion_compliance_pct: float | None = None  # 60-75% per REPORT.md

    # 7. Peak-hour amplification
    peak_amplification: PeakAmplification | None = None

    # 8. Post-completion normalization
    normalization_weeks: int = 2  # 2-3 weeks per REPORT.md
    normalization_note: str = "Post-completion, expect 2-3 weeks for traffic patterns to normalize as travelers verify improved conditions."

    # Impact metrics
    capacity_reduction_pct: float | None = None
    additional_delay_minutes: str | None = None  # "15-30 minutes"

    # Metadata
    source: str
    last_updated: datetime


class ConstructionListResponse(BaseModel):
    zones: list[ConstructionZone]
    total_active: int
    timestamp: datetime
    demo_mode: bool = True
