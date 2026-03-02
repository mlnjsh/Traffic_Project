"""API endpoints for Category 3: Route Optimization Queries.

Prompt 3.1: POST /routes/smart — Smart Route Recommendation
Prompt 3.2: POST /routes/vehicle — Vehicle-Class-Specific Routing
Prompt 3.N: POST /routes/narrative — Route Intelligence Narrative
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.schemas.routing import (
    SmartRouteResponse,
    VehicleRoutingResponse,
)
from app.models.schemas.narrative import RouteNarrativeResponse
from app.services.routing_service import RoutingService
from app.services.vehicle_routing_service import VehicleRoutingService
from app.services.narrative_service import NarrativeService

router = APIRouter(prefix="/routes")
routing_service = RoutingService()
vehicle_service = VehicleRoutingService()
narrative_service = NarrativeService()


# --- Prompt 3.1: Smart Route Recommendation ---

class SmartRouteRequest(BaseModel):
    origin: str
    destination: str


@router.post("/smart", response_model=SmartRouteResponse)
async def get_smart_routes(req: SmartRouteRequest):
    """Get multi-objective route recommendations.

    Returns 4 route options optimized for different objectives:
    1. Fastest Route — AI-optimized with uncertainty integration
    2. Most Reliable Route — minimize variance (best for meetings, flights)
    3. Fuel Efficient Route — Mappls signal countdown green-wave riding
    4. Avoid Construction — bypass all active work zones

    Plus a multi-modal option (BMTC bus + Namma Metro + walking + auto).

    Data sources: ASTraM real-time + TomTom flow + Mappls signals.
    """
    return await routing_service.get_routes(
        origin=req.origin,
        destination=req.destination,
    )


# --- Prompt 3.2: Vehicle-Class-Specific Routing ---

class VehicleRouteRequest(BaseModel):
    origin: str
    destination: str
    vehicle_class: str  # "two_wheeler", "car", "truck", "bmtc_bus", "emergency", "auto_rickshaw"


VALID_VEHICLE_CLASSES = [
    "two_wheeler", "car", "truck", "bmtc_bus", "emergency", "auto_rickshaw",
]


@router.post("/vehicle", response_model=VehicleRoutingResponse)
async def get_vehicle_route(req: VehicleRouteRequest):
    """Get vehicle-class-specific route recommendation.

    Adapts routing based on vehicle type:
    - two_wheeler: narrow streets, shortcuts, safety notes
    - car: standard routing + parking + carpool suggestion
    - truck: weight/height restrictions, night windows, loading zones
    - bmtc_bus: real-time bus arrival, metro connections, walking distances
    - emergency: e-Path green corridors, signal preemption
    - auto_rickshaw: frequent stops, fare estimates, pickup/drop zones
    """
    if req.vehicle_class not in VALID_VEHICLE_CLASSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid vehicle_class '{req.vehicle_class}'. Valid classes: {', '.join(VALID_VEHICLE_CLASSES)}",
        )
    return await vehicle_service.get_vehicle_route(
        origin=req.origin,
        destination=req.destination,
        vehicle_class=req.vehicle_class,
    )


# --- Route Intelligence Narrative ---

class NarrativeRequest(BaseModel):
    origin: str
    destination: str
    vehicle_class: str | None = None


@router.post("/narrative", response_model=RouteNarrativeResponse)
async def get_route_narrative(req: NarrativeRequest):
    """Plain English route intelligence narrative.

    Generates a conversational breakdown covering traffic conditions,
    best route recommendation, active incidents, construction zones,
    parking information, and pro tips — all in easy-to-read language.
    """
    if req.vehicle_class and req.vehicle_class not in VALID_VEHICLE_CLASSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid vehicle_class '{req.vehicle_class}'. Valid: {', '.join(VALID_VEHICLE_CLASSES)}",
        )
    return await narrative_service.generate_narrative(
        origin=req.origin,
        destination=req.destination,
        vehicle_class=req.vehicle_class,
    )
