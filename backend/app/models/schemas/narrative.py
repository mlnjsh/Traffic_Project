"""Pydantic schemas for Route Intelligence Narrative."""

from datetime import datetime
from pydantic import BaseModel


class NarrativeSection(BaseModel):
    """A single section of the route intelligence narrative."""

    section_id: str
    title: str
    icon: str
    content: str
    severity: str = "info"  # "info", "warning", "alert", "success"


class RouteNarrativeResponse(BaseModel):
    """Full route intelligence narrative response."""

    origin: str
    destination: str
    vehicle_class: str | None = None
    sections: list[NarrativeSection]
    generated_at: datetime
    data_sources: list[str] = ["ASTraM", "TomTom", "Mappls", "OpenCity"]
    demo_mode: bool = True
