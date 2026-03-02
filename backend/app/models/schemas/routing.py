"""Pydantic schemas for Category 3: Route Optimization Queries.

Prompt 3.1: Smart Route Recommendation
Prompt 3.2: Vehicle-Class-Specific Routing
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# --- Shared Enums ---

class RouteObjective(str, Enum):
    FASTEST = "fastest"
    RELIABLE = "most_reliable"
    FUEL_EFFICIENT = "fuel_efficient"
    MULTIMODAL = "multimodal"
    AVOID_CONSTRUCTION = "avoid_construction"


class VehicleClass(str, Enum):
    TWO_WHEELER = "two_wheeler"
    CAR = "car"
    TRUCK = "truck"
    BMTC_BUS = "bmtc_bus"
    EMERGENCY = "emergency"
    AUTO_RICKSHAW = "auto_rickshaw"


class CongestionLevel(str, Enum):
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    SEVERE = "severe"
    GRIDLOCK = "gridlock"


# --- Prompt 3.1: Smart Route Recommendation ---

class RouteSegment(BaseModel):
    """A single segment of a route."""
    road_name: str
    distance_km: float
    estimated_time_minutes: float
    congestion_level: CongestionLevel
    speed_kmh: float
    known_issues: list[str] = []


class RouteOption(BaseModel):
    """A single route recommendation."""
    objective: RouteObjective
    label: str  # "Fastest Route", "Most Reliable", etc.
    summary: str  # "via ORR (Marathahalli → Silk Board)"
    total_distance_km: float
    estimated_time_minutes: float
    time_range_minutes: str  # "45-55 min"
    confidence_pct: float = Field(ge=0, le=100)
    congestion_level: CongestionLevel
    known_issues: list[str] = []
    segments: list[RouteSegment] = []
    savings_vs_default: str | None = None  # "Save 12-18 minutes, 72% confidence"
    notes: str = ""


class MultiModalLeg(BaseModel):
    """A single leg of a multi-modal route."""
    mode: str  # "walk", "metro", "bus", "auto", "drive"
    from_location: str
    to_location: str
    distance_km: float
    time_minutes: float
    cost_inr: float | None = None
    details: str  # "Namma Metro Purple Line: MG Road → Whitefield"


class MultiModalOption(BaseModel):
    """Multi-modal route comparison."""
    legs: list[MultiModalLeg]
    total_time_minutes: float
    total_cost_inr: float | None = None
    comparison_vs_driving: str  # "15 min faster than driving, ₹80 cheaper"


class SmartRouteResponse(BaseModel):
    """Response schema for Prompt 3.1."""
    origin: str
    destination: str
    routes: list[RouteOption]
    multimodal: MultiModalOption | None = None
    data_sources: list[str] = ["ASTraM", "TomTom", "Mappls"]
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 3.2: Vehicle-Class-Specific Routing ---

class VehicleRestriction(BaseModel):
    """A restriction applicable to a vehicle class."""
    restriction_type: str  # "weight_limit", "height_limit", "time_window", "truck_ban"
    description: str
    affected_roads: list[str]


class ParkingInfo(BaseModel):
    """Parking information near destination."""
    name: str
    type: str  # "street", "multi_level", "private"
    distance_from_dest_m: int
    estimated_cost_inr: float | None = None
    availability: str  # "likely_available", "limited", "full"


class BusConnection(BaseModel):
    """BMTC bus connection details."""
    route_number: str
    from_stop: str
    to_stop: str
    frequency_minutes: int
    estimated_arrival_minutes: int  # traffic-adjusted
    walking_distance_m: int
    metro_connection: str | None = None  # "Connect to Purple Line at Majestic"


class VehicleRouteOption(BaseModel):
    """A route adapted to vehicle class constraints."""
    vehicle_class: VehicleClass
    route_summary: str
    total_distance_km: float
    estimated_time_minutes: float
    time_range_minutes: str
    restrictions_applied: list[VehicleRestriction] = []
    parking: ParkingInfo | None = None
    bus_connections: list[BusConnection] = []
    safety_notes: list[str] = []
    cost_estimate: str | None = None  # fare/fuel estimate
    special_notes: list[str] = []  # vehicle-class-specific tips


class VehicleRoutingResponse(BaseModel):
    """Response schema for Prompt 3.2."""
    origin: str
    destination: str
    vehicle_class: VehicleClass
    vehicle_label: str  # "Two-Wheeler", "Car", etc.
    route: VehicleRouteOption
    alternative_mode_suggestion: str | None = None  # "Consider Metro — 15 min faster"
    data_sources: list[str] = ["ASTraM", "TomTom", "Mappls"]
    timestamp: datetime
    demo_mode: bool = True
