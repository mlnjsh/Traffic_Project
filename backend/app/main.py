from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router
from app.scheduler.poller import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    if not settings.demo_mode:
        start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="Bangalore Traffic Intelligence API",
    description="Real-time traffic intelligence for Bangalore powered by ASTraM, TomTom, and Mappls data fusion.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "demo_mode": settings.demo_mode,
    }
