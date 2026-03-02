"""API endpoints for Prompt 1.3: Construction Zone Status.

GET /construction/zones — All active construction zones
GET /construction/zones/{zone_id} — Single zone detail
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas.construction import ConstructionListResponse, ConstructionZone
from app.services.construction_service import ConstructionService

router = APIRouter()
construction_service = ConstructionService()


@router.get("/construction/zones", response_model=ConstructionListResponse)
async def get_construction_zones():
    """Get all active construction zones in Bangalore.

    Each zone includes project details, agency, lane restrictions,
    completion %, milestones, diversion routes, and peak-hour amplification.

    Key active projects tracked per Prompt 1.3:
    - BWSSB Pipeline: ORR Zakir Nagar-Goraguntepalya (Feb 6 - Mar 6, 2026)
    - White-topping: Goraguntepalya flyover vicinity (target Mar 15, 2026)
    - Rajajinagar lane widening (target Apr 30, 2026)
    - Metro Phase 2B: Whitefield-Challaghatta corridor
    - Silk Board Junction Flyover (delayed, target 2026)
    """
    return await construction_service.get_all_zones()


@router.get("/construction/zones/{zone_id}", response_model=ConstructionZone)
async def get_construction_zone(zone_id: str):
    """Get detailed status of a single construction zone.

    Includes milestones with risk factors, diversion compliance rates,
    and post-completion normalization timeline (2-3 weeks).
    """
    result = await construction_service.get_zone(zone_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Construction zone '{zone_id}' not found")
    return result
