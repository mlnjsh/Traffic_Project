"""API endpoints for Category 4: Heatmap & Visualization Queries.

Prompt 4.1: GET /visualization/config — Enhanced heatmap with overlay metadata
Prompt 4.1: GET /visualization/signals — Signal countdown status (Mappls-style)
Prompt 4.2: GET /visualization/traffic-card/{corridor_id} — Segment tap traffic card
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas.visualization import (
    EnhancedHeatmapResponse,
    SignalListResponse,
    TrafficCardResponse,
)
from app.services.visualization_service import VisualizationService

router = APIRouter(prefix="/visualization")
viz_service = VisualizationService()


@router.get("/config", response_model=EnhancedHeatmapResponse)
async def get_heatmap_config():
    """Get enhanced heatmap configuration with data sources and overlay layers.

    Per Prompt 4.1: Lists all data sources (ASTraM, TomTom, IoT sensors,
    floating car data) with refresh rates and coverage.

    Returns toggleable overlay layers: congestion heatmap, incidents,
    construction zones, signal status, emergency corridors, weather impact.
    """
    return await viz_service.get_enhanced_heatmap()


@router.get("/signals", response_model=SignalListResponse)
async def get_signal_status():
    """Get real-time signal countdown status for major Bangalore junctions.

    Per Prompt 4.1 overlay + Prompt 4.2 signal countdown bubbles:
    Returns current phase (green/red/amber), countdown seconds, cycle time
    for 15 ASTraM-controlled junctions.

    Data source: Mappls signal countdown at 1,000+ junctions.
    """
    return await viz_service.get_signal_status()


@router.get("/traffic-card/{corridor_id}", response_model=TrafficCardResponse)
async def get_traffic_card(corridor_id: str):
    """Get detailed traffic card for a road segment (tap-to-view).

    Per Prompt 4.2: "Tap any road segment for detailed traffic card"
    Returns speed, congestion, delay, trend, incidents, construction status,
    and prediction summary ("When will this clear?").
    """
    result = await viz_service.get_traffic_card(corridor_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Corridor '{corridor_id}' not found.",
        )
    return result
