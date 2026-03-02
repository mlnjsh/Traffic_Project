"""API endpoints for Category 5: Bangalore Traffic Problem-Solving Prompts.

Prompt 5.1: POST /commuter/forecast — Commuter Decision Assistant
Prompt 5.2: POST /logistics/optimize — Logistics & Freight Optimizer
Prompt 5.3: GET /planner/dashboard — City Planner Intelligence Dashboard
Prompt 5.4: POST /emergency/optimize — Emergency Response Optimizer
Prompt 5.5: POST /citizen/report — Citizen Engagement & Crowdsourcing
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.schemas.problem_solving import (
    CitizenEngagementResponse,
    CommuterForecast,
    EmergencyResponse,
    LogisticsResponse,
    PlannerDashboardResponse,
)
from app.services.commuter_service import CommuterService
from app.services.logistics_service import LogisticsService
from app.services.planner_service import PlannerService
from app.services.emergency_service import EmergencyService
from app.services.citizen_service import CitizenService

router = APIRouter()
commuter_service = CommuterService()
logistics_service = LogisticsService()
planner_service = PlannerService()
emergency_service = EmergencyService()
citizen_service = CitizenService()


# --- Prompt 5.1: Commuter Decision Assistant ---

class CommuterRequest(BaseModel):
    origin: str
    destination: str


@router.post("/commuter/forecast", response_model=CommuterForecast)
async def get_commuter_forecast(req: CommuterRequest):
    """Commuter Decision Assistant — morning/evening commute forecast.

    Provides: optimal departure time, mode comparisons (drive vs metro vs bus),
    event alerts, overnight updates, and departure advice.
    Key insight: Peak at 18:00 = 183%, 13.9 km/h.
    """
    return await commuter_service.get_forecast(req.origin, req.destination)


# --- Prompt 5.2: Logistics & Freight Optimizer ---

class LogisticsRequest(BaseModel):
    origin: str
    stops: list[str] = []


@router.post("/logistics/optimize", response_model=LogisticsResponse)
async def optimize_logistics(req: LogisticsRequest):
    """Logistics & Freight Optimizer — night window exploitation, fleet management.

    Night window (02:00-06:00): 68% faster. Construction avoidance.
    Weight/height restrictions, loading zones, fuel optimization (12-18%).
    """
    return await logistics_service.optimize_logistics(req.origin, req.stops)


# --- Prompt 5.3: City Planner Intelligence Dashboard ---

@router.get("/planner/dashboard", response_model=PlannerDashboardResponse)
async def get_planner_dashboard():
    """City Planner Intelligence Dashboard.

    Corridor rankings, emerging hotspots, infrastructure projects,
    demand management insights, and performance metrics.
    """
    return await planner_service.get_dashboard()


# --- Prompt 5.4: Emergency Response Optimizer ---

class EmergencyRequest(BaseModel):
    origin: str
    emergency_type: str  # "cardiac", "trauma", "obstetric", "general"


@router.post("/emergency/optimize", response_model=EmergencyResponse)
async def optimize_emergency(req: EmergencyRequest):
    """Emergency Response Optimizer — e-Path green corridor routing.

    Signal preemption: 45-90 seconds. GPS: <10m, 5-second updates.
    30-35% response time improvement vs standard routing.
    Hospital selection by specialty and capacity.
    """
    return await emergency_service.optimize_emergency(req.origin, req.emergency_type)


# --- Prompt 5.5: Citizen Engagement ---

class CitizenReportRequest(BaseModel):
    category: str  # "accident", "breakdown", "debris", "signal_malfunction", "flooding", "pothole"
    lat: float
    lng: float
    road_name: str
    description: str


@router.post("/citizen/report", response_model=CitizenEngagementResponse)
async def submit_citizen_report(req: CitizenReportRequest):
    """Citizen Incident Report — one-tap reporting with AI pre-classification.

    Auto-geotagging, image AI classification, control room verification (2-5 min),
    community validation, gamification (Traffic Hero badges).
    """
    return await citizen_service.submit_report(
        category=req.category, lat=req.lat, lng=req.lng,
        road_name=req.road_name, description=req.description,
    )
