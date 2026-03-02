"""Pydantic schemas for Category 5: Bangalore Traffic Problem-Solving Prompts.

Prompt 5.1: Commuter Decision Assistant
Prompt 5.2: Logistics & Freight Optimizer
Prompt 5.3: City Planner Intelligence Dashboard
Prompt 5.4: Emergency Response Optimizer
Prompt 5.5: Citizen Engagement & Crowdsourcing
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# --- Prompt 5.1: Commuter Decision Assistant ---

class CommuteMode(str, Enum):
    DRIVE = "drive"
    METRO = "metro"
    BUS = "bus"
    COMBINATION = "combination"


class ModeComparison(BaseModel):
    """Comparison of a single commute mode."""
    mode: CommuteMode
    estimated_time_minutes: int
    estimated_cost_inr: int
    reliability: str  # "high", "medium", "low"
    notes: str


class CommuterForecast(BaseModel):
    """Response for Prompt 5.1 — Commuter Decision Assistant."""
    period: str  # "morning" or "evening"
    greeting: str  # "Good morning! Here's your commute forecast:"
    route_summary: str  # "Whitefield → Electronic City"
    optimal_departure: str  # "07:15"
    current_conditions: str  # narrative
    mode_comparisons: list[ModeComparison]
    event_alert: str | None = None  # "Today is IPL match — expect +25 min on ORR"
    overnight_updates: list[str] = []  # construction/incident updates
    departure_advice: str  # "Leave now — 20% less traffic than usual"
    savings_narrative: str | None = None  # "You saved 18 min vs average"
    peak_insight: str  # "Peak at 18:00 = 183%, 13.9 km/h. Every minute matters."
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 5.2: Logistics & Freight Optimizer ---

class DeliveryStop(BaseModel):
    location: str
    estimated_arrival: str  # HH:MM
    loading_time_minutes: int
    restrictions: list[str] = []


class FreightRouteOption(BaseModel):
    total_distance_km: float
    total_time_minutes: int
    stops: list[DeliveryStop]
    fuel_savings_pct: float
    night_window_used: bool


class LogisticsResponse(BaseModel):
    """Response for Prompt 5.2 — Logistics & Freight Optimizer."""
    fleet_id: str
    current_time_window: str  # "night_optimal", "daytime_restricted", "transition"
    night_window_insight: str  # "68% faster than peak..."
    active_construction_zones: int
    construction_free_routes: int
    recommended_route: FreightRouteOption
    restrictions_summary: list[str]
    fuel_optimization_note: str
    dynamic_reroute_available: bool = True
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 5.3: City Planner Intelligence Dashboard ---

class CorridorRanking(BaseModel):
    rank: int
    corridor_id: str
    corridor_name: str
    congestion_severity: str
    structural_cause: str
    years_persistent: int
    annual_growth_pct: float | None = None


class InfrastructureProject(BaseModel):
    project_name: str
    type: str  # "flyover", "underpass", "signal_optimization", "metro"
    expected_impact: str
    investment_crore: float | None = None
    timeline: str


class DemandMetric(BaseModel):
    metric: str
    value: str
    trend: str
    insight: str


class PlannerDashboardResponse(BaseModel):
    """Response for Prompt 5.3 — City Planner Intelligence Dashboard."""
    corridor_rankings: list[CorridorRanking]
    emerging_hotspots: list[CorridorRanking]
    infrastructure_projects: list[InfrastructureProject]
    demand_metrics: list[DemandMetric]
    performance_metrics: dict[str, str]
    recommendations: list[str]
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 5.4: Emergency Response Optimizer ---

class EmergencyType(str, Enum):
    CARDIAC = "cardiac"
    TRAUMA = "trauma"
    OBSTETRIC = "obstetric"
    GENERAL = "general"


class HospitalOption(BaseModel):
    name: str
    specialty: str
    distance_km: float
    estimated_time_minutes: int
    capacity_status: str  # "available", "limited", "full"
    epath_available: bool


class EmergencyResponse(BaseModel):
    """Response for Prompt 5.4 — Emergency Response Optimizer."""
    emergency_type: EmergencyType
    origin: str
    recommended_hospital: HospitalOption
    alternative_hospitals: list[HospitalOption]
    epath_status: str  # "Green corridor establishing... 45-90 seconds"
    signal_preemption_count: int
    estimated_response_time_minutes: int
    improvement_vs_standard: str  # "30-35% faster"
    gps_tracking: str  # "<10m accuracy, 5-second updates"
    pre_arrival_alert: str  # "Alert sent to [hospital]"
    incident_detection_note: str
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 5.5: Citizen Engagement ---

class IncidentCategory(str, Enum):
    ACCIDENT = "accident"
    BREAKDOWN = "breakdown"
    DEBRIS = "debris"
    SIGNAL_MALFUNCTION = "signal_malfunction"
    FLOODING = "flooding"
    POTHOLE = "pothole"
    OTHER = "other"


class CitizenReport(BaseModel):
    report_id: str
    category: IncidentCategory
    location_lat: float
    location_lng: float
    road_name: str
    description: str
    image_url: str | None = None
    ai_classification: str | None = None
    verification_status: str  # "pending", "verified", "rejected"
    verification_eta_minutes: int = 3
    reporter_reliability_score: float = Field(ge=0, le=100)


class CitizenEngagementResponse(BaseModel):
    """Response for Prompt 5.5 — Citizen Engagement."""
    report: CitizenReport
    confirmation_message: str
    community_validations: int
    gamification: dict  # {"badge": "Traffic Hero", "reports_count": 12}
    feedback_channels: list[str]
    timestamp: datetime
    demo_mode: bool = True
