"""API endpoints for Category 6: Advanced Analytics Prompts.

Prompt 6.1: GET /analytics/patterns — Pattern Discovery
Prompt 6.2: GET /analytics/scenario/{scenario_id} — What-If Scenario Modeling
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas.analytics import PatternDiscoveryResponse, WhatIfResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics")
analytics_service = AnalyticsService()

VALID_SCENARIOS = ["metro_shift", "ai_signals", "congestion_pricing", "staggered_hours"]


@router.get("/patterns", response_model=PatternDiscoveryResponse)
async def get_patterns():
    """Pattern Discovery — temporal, seasonal, and spatial traffic patterns.

    Temporal: Peak 17:00-20:00, worst 18:00 (183%), best 02:00-06:00.
    Seasonal: Lowest Jan/Aug (64%), Highest Jun (81%)/Oct (79%).
    Spatial: Persistent (ORR, Bellandur), Growing (Thanisandra +25%/yr), Improving (Old Airport Rd -17%).
    """
    return await analytics_service.get_patterns()


@router.get("/scenario/{scenario_id}", response_model=WhatIfResponse)
async def run_scenario(scenario_id: str):
    """What-If Scenario Modeling — run pre-built traffic intervention scenarios.

    Available scenarios:
    - metro_shift: 10% car commuters shift to metro
    - ai_signals: All 2,000+ signals become AI-adaptive
    - congestion_pricing: Congestion pricing on ORR
    - staggered_hours: IT companies implement staggered hours
    """
    result = await analytics_service.run_scenario(scenario_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{scenario_id}' not found. Valid: {', '.join(VALID_SCENARIOS)}",
        )
    return result
