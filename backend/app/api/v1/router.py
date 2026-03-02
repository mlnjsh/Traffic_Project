"""Aggregated API v1 router."""

from fastapi import APIRouter

from app.api.v1.traffic import router as traffic_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.construction import router as construction_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.routing import router as routing_router
from app.api.v1.visualization import router as visualization_router
from app.api.v1.problem_solving import router as problem_solving_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()

# Category 1: Real-Time Traffic Condition Queries
api_router.include_router(traffic_router, tags=["Traffic — Prompt 1.1"])
api_router.include_router(incidents_router, tags=["Incidents — Prompt 1.2"])
api_router.include_router(construction_router, tags=["Construction — Prompt 1.3"])

# Category 2: Predictive & Planning Queries
api_router.include_router(predictions_router, tags=["Predictions — Prompts 2.1, 2.2, 2.3"])

# Category 3: Route Optimization Queries
api_router.include_router(routing_router, tags=["Routing — Prompts 3.1, 3.2"])

# Category 4: Heatmap & Visualization Queries
api_router.include_router(visualization_router, tags=["Visualization — Prompts 4.1, 4.2"])

# Category 5: Bangalore Traffic Problem-Solving Prompts
api_router.include_router(problem_solving_router, tags=["Problem Solving — Prompts 5.1-5.5"])

# Category 6: Advanced Analytics Prompts
api_router.include_router(analytics_router, tags=["Analytics — Prompts 6.1, 6.2"])
