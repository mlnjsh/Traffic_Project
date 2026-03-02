"""Pydantic schemas for Category 2: Predictive & Planning Queries.

Prompt 2.1: "When Will It Get Better?" Engine
Prompt 2.2: Departure Time Optimizer
Prompt 2.3: Event Impact Predictor
"""

from datetime import datetime, time
from enum import Enum

from pydantic import BaseModel, Field


# --- Prompt 2.1: "When Will It Get Better?" ---

class PredictionHorizon(str, Enum):
    SHORT_TERM = "short_term"    # 0-15 min
    MEDIUM_TERM = "medium_term"  # 15-60 min
    CONSTRUCTION = "construction"


class CongestionPrediction(BaseModel):
    """A single prediction point."""
    time_from_now_minutes: int
    predicted_speed_kmh: float
    predicted_congestion_pct: float
    predicted_color: str
    confidence_pct: float


class ShortTermPrediction(BaseModel):
    """0-15 min: Real-time trend extrapolation (75-80% accuracy)."""
    horizon: str = "short_term"
    direction: str  # "improving" | "stable" | "worsening"
    current_speed_kmh: float
    predicted_speed_5min: float
    predicted_speed_10min: float
    predicted_speed_15min: float
    estimated_change_minutes: int  # minutes until noticeable change
    confidence_pct: float = Field(ge=0, le=100)
    basis: str  # e.g., "Real-time trend extrapolation from TomTom + ASTraM"
    narrative: str  # Human-readable: "Based on current flow rates, conditions on ORR should improve in approximately 12 minutes."


class MediumTermPrediction(BaseModel):
    """15-60 min: Historical pattern matching + current state (60-70% accuracy)."""
    horizon: str = "medium_term"
    day_of_week: str
    typical_clear_time: str  # e.g., "19:45"
    current_assessment: str  # "earlier" | "on-track" | "later"
    estimated_clear_time: str  # e.g., "20:15"
    predictions: list[CongestionPrediction] = []
    confidence_pct: float = Field(ge=0, le=100)
    basis: str
    narrative: str


class ConstructionPrediction(BaseModel):
    """Construction-specific: Project milestone data (85-90% accuracy)."""
    horizon: str = "construction"
    project_name: str
    completion_pct: float
    scheduled_completion: str  # date string
    uncertainty_days: int
    normalization_weeks: int = 3  # 2-3 weeks after reopening
    confidence_pct: float = Field(ge=0, le=100)
    basis: str
    narrative: str


class PredictionResponse(BaseModel):
    """Response schema for Prompt 2.1."""
    corridor_id: str
    corridor_name: str
    short_term: ShortTermPrediction
    medium_term: MediumTermPrediction
    construction: ConstructionPrediction | None = None  # only if active construction
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 2.2: Departure Time Optimizer ---

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DepartureOption(BaseModel):
    """A single departure time option."""
    label: str  # "Earliest (safe)", "Optimal", "Latest (risky)"
    departure_time: str  # "17:00"
    arrival_time: str  # "18:15"
    travel_time_minutes: int
    route_recommendation: str
    confidence_pct: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    congestion_at_departure: str  # "Moderate — 65% congestion"
    notes: str


class DepartureElasticityInsight(BaseModel):
    """Key time-saving insight per Prompt 2.2."""
    corridor: str
    early_departure: str  # "17:00"
    late_departure: str  # "18:30"
    time_saved_pct: float  # 40-50%
    time_saved_minutes: int
    insight: str  # "Leaving at 17:00 vs 18:30 saves 40-50% travel time on Whitefield Main Road"


class DepartureOptimizerResponse(BaseModel):
    """Response schema for Prompt 2.2."""
    origin: str
    destination: str
    desired_arrival: str
    day_of_week: str
    options: list[DepartureOption]
    elasticity_insight: DepartureElasticityInsight | None = None
    factors_considered: list[str]  # ["day_of_week", "historical_patterns", "current_conditions", "construction"]
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 2.3: Event Impact Predictor ---

class EventType(str, Enum):
    CRICKET = "cricket"
    POLITICAL_RALLY = "political_rally"
    RELIGIOUS_PROCESSION = "religious_procession"
    FESTIVAL = "festival"
    CONCERT = "concert"
    MARATHON = "marathon"
    OTHER = "other"


class CorridorImpact(BaseModel):
    """Predicted impact on a specific corridor."""
    corridor_id: str
    corridor_name: str
    congestion_multiplier: float  # e.g., 2.5 for 250%
    additional_delay_minutes: int
    severity: str  # "Severe", "High", "Moderate", "Low"


class TimingWindow(BaseModel):
    """A window to avoid or use."""
    label: str
    window: str  # "14:00-16:00"
    recommendation: str


class EventImpactResponse(BaseModel):
    """Response schema for Prompt 2.3."""
    event_name: str
    event_type: EventType
    venue: str
    expected_attendance: int
    event_date: str
    event_time: str

    # Historical analog
    historical_analog: str  # "Based on 12 similar cricket matches at Chinnaswamy"
    analog_count: int

    # Corridor-specific predictions
    corridor_impacts: list[CorridorImpact]

    # Routing advice
    avoid_windows: list[TimingWindow]
    safe_windows: list[TimingWindow]

    # Recovery
    estimated_recovery_hours: float
    recovery_narrative: str

    timestamp: datetime
    demo_mode: bool = True
