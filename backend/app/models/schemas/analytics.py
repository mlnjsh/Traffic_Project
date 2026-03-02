"""Pydantic schemas for Category 6: Advanced Analytics Prompts.

Prompt 6.1: Pattern Discovery
Prompt 6.2: What-If Scenario Modeling
"""

from datetime import datetime

from pydantic import BaseModel


# --- Prompt 6.1: Pattern Discovery ---

class TemporalPattern(BaseModel):
    pattern_type: str  # "peak", "off_peak", "weekend", "monsoon"
    description: str
    time_window: str
    congestion_level: str
    speed_kmh: float | None = None
    insight: str


class SeasonalPattern(BaseModel):
    month: str
    congestion_index: float  # e.g., 64, 81
    classification: str  # "lowest", "highest", "moderate"
    note: str


class SpatialPattern(BaseModel):
    corridor: str
    trend: str  # "persistent", "growing", "improving"
    annual_change_pct: float
    years_tracked: int
    cause: str


class PatternDiscoveryResponse(BaseModel):
    """Response for Prompt 6.1 — Pattern Discovery."""
    temporal_patterns: list[TemporalPattern]
    seasonal_patterns: list[SeasonalPattern]
    spatial_patterns: list[SpatialPattern]
    key_insights: list[str]
    data_period: str  # "January 2022 — January 2024"
    timestamp: datetime
    demo_mode: bool = True


# --- Prompt 6.2: What-If Scenario Modeling ---

class ScenarioResult(BaseModel):
    metric: str
    before: str
    after: str
    change: str
    confidence: str


class WhatIfScenario(BaseModel):
    scenario_id: str
    title: str
    description: str
    parameters: dict[str, str]
    results: list[ScenarioResult]
    investment_estimate: str | None = None
    implementation_timeline: str | None = None
    equity_considerations: str | None = None
    feasibility: str  # "high", "medium", "low"
    recommendation: str


class WhatIfResponse(BaseModel):
    """Response for Prompt 6.2 — What-If Scenario Modeling."""
    scenario: WhatIfScenario
    comparison_baseline: str  # "Current conditions as of March 2026"
    methodology: str
    caveats: list[str]
    timestamp: datetime
    demo_mode: bool = True
