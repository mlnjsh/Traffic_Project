"""API endpoints for Prompt 1.1: Current Corridor Status.

GET /traffic/corridors — All corridors with current status
GET /traffic/corridor/{corridor_id} — Single corridor detail
GET /heatmap/data — GeoJSON-ready heatmap data for map rendering
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas.traffic import CorridorListResponse, CorridorStatus, HeatmapResponse
from app.services.traffic_service import TrafficService

router = APIRouter()
traffic_service = TrafficService()


@router.get("/traffic/corridors", response_model=CorridorListResponse)
async def get_all_corridors():
    """Get real-time status of all 8 monitored Bangalore corridors.

    Returns speed, congestion %, color code, active incidents, delay,
    and trend prediction for each corridor.

    Data fused from TomTom (speed/flow) + ASTraM (incidents).
    """
    return await traffic_service.get_all_corridors()


@router.get("/traffic/corridor/{corridor_id}", response_model=CorridorStatus)
async def get_corridor(corridor_id: str):
    """Get detailed status of a single corridor.

    Example corridor_ids: orr_silk_board, bellandur_road, whitefield_main,
    electronic_city, bannerghatta_road, cbd_mg_road, thanisandra_hennur,
    orr_zakir_nagar
    """
    result = await traffic_service.get_corridor(corridor_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Corridor '{corridor_id}' not found. Valid IDs: orr_silk_board, orr_zakir_nagar, bellandur_road, whitefield_main, electronic_city, bannerghatta_road, cbd_mg_road, thanisandra_hennur",
        )
    return result


@router.get("/heatmap/data", response_model=HeatmapResponse)
async def get_heatmap_data():
    """Get heatmap data for all corridors.

    Returns colored segments for rendering on Google Maps.
    Color scale: Green (>30 km/h) → Yellow → Orange → Red → Black (<5 km/h).
    """
    return await traffic_service.get_heatmap_data()
