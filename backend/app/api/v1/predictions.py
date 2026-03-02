"""API endpoints for Category 2: Predictive & Planning Queries.

Prompt 2.1: GET /predictions/{corridor_id} — "When Will It Get Better?"
Prompt 2.2: POST /departure/optimize — Departure Time Optimizer
Prompt 2.3: POST /events/impact — Event Impact Predictor
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.schemas.prediction import (
    DepartureOptimizerResponse,
    EventImpactResponse,
    PredictionResponse,
)
from app.services.prediction_service import PredictionService
from app.services.departure_service import DepartureService
from app.services.event_service import EventService

router = APIRouter()
prediction_service = PredictionService()
departure_service = DepartureService()
event_service = EventService()


# --- Prompt 2.1: "When Will It Get Better?" ---

@router.get("/predictions/{corridor_id}", response_model=PredictionResponse)
async def get_prediction(corridor_id: str):
    """Predict when congestion will clear for a corridor.

    Returns three prediction horizons:
    - Short-term (0-15 min): Real-time trend extrapolation (75-80% accuracy)
    - Medium-term (15-60 min): Historical pattern matching (60-70% accuracy)
    - Construction-specific: Project milestone data (85-90% accuracy)
    """
    result = await prediction_service.get_prediction(corridor_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Corridor '{corridor_id}' not found. Valid IDs: orr_silk_board, orr_zakir_nagar, bellandur_road, whitefield_main, electronic_city, bannerghatta_road, cbd_mg_road, thanisandra_hennur",
        )
    return result


# --- Prompt 2.2: Departure Time Optimizer ---

class DepartureRequest(BaseModel):
    origin: str
    destination: str
    desired_arrival: str  # "HH:MM"
    day_of_week: str | None = None


@router.post("/departure/optimize", response_model=DepartureOptimizerResponse)
async def optimize_departure(req: DepartureRequest):
    """Calculate optimal departure time with three risk-tier options.

    Returns earliest (safe), optimal, and latest (risky) departure times
    with travel estimates, route recommendations, and confidence levels.

    Key insight for Whitefield corridors: leaving at 17:00 vs 18:30
    saves 40-50% travel time.
    """
    return await departure_service.optimize_departure(
        origin=req.origin,
        destination=req.destination,
        desired_arrival=req.desired_arrival,
        day_of_week=req.day_of_week,
    )


# --- Prompt 2.3: Event Impact Predictor ---

class EventRequest(BaseModel):
    event_name: str
    event_type: str  # "cricket", "political_rally", "festival", etc.
    venue: str
    expected_attendance: int
    event_date: str  # "YYYY-MM-DD"
    event_time: str  # "HH:MM"


@router.post("/events/impact", response_model=EventImpactResponse)
async def predict_event_impact(req: EventRequest):
    """Predict traffic impact of an upcoming event.

    Uses historical analogs (50+ annual major events) to predict
    corridor-specific congestion multipliers, timing windows to avoid,
    and recovery timelines.

    Supported event types: cricket, political_rally, religious_procession,
    festival, concert, marathon.
    """
    return await event_service.predict_event_impact(
        event_name=req.event_name,
        event_type=req.event_type,
        venue=req.venue,
        expected_attendance=req.expected_attendance,
        event_date=req.event_date,
        event_time=req.event_time,
    )
