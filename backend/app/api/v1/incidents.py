"""API endpoints for Prompt 1.2: Active Incident Report.

GET /incidents — All active incidents sorted by severity
GET /incidents/{incident_id} — Single incident detail
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas.incident import IncidentListResponse, IncidentReport
from app.services.incident_service import IncidentService

router = APIRouter()
incident_service = IncidentService()


@router.get("/incidents", response_model=IncidentListResponse)
async def get_active_incidents(
    corridor: str | None = Query(None, description="Filter by corridor/road name (e.g., 'ORR', 'Silk Board', 'Whitefield')"),
):
    """Get all active traffic incidents sorted by severity (highest first).

    Fuses ASTraM (authoritative local, 1-min refresh) with TomTom incidents.
    Each incident includes type, location, severity (1-5), affected length,
    estimated delay, and diversion routes.

    If no incidents on queried route, confirms "No active incidents" with timestamp.
    """
    return await incident_service.get_active_incidents(corridor_filter=corridor)


@router.get("/incidents/{incident_id}", response_model=IncidentReport)
async def get_incident(incident_id: str):
    """Get detailed report for a single incident."""
    result = await incident_service.get_incident(incident_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return result
