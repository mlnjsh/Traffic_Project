"""City Planner Intelligence Dashboard — implements Prompt 5.3.

Corridor analysis, infrastructure impact, demand management, performance metrics.
Per REPORT.md: Congestion +1.7pp YoY, speed -1.0 km/h, time loss +5.6%.
"""

from datetime import datetime, timezone

from app.models.schemas.problem_solving import (
    CorridorRanking,
    DemandMetric,
    InfrastructureProject,
    PlannerDashboardResponse,
)


class PlannerService:
    """Service for Prompt 5.3 — City Planner Intelligence Dashboard."""

    async def get_dashboard(self) -> PlannerDashboardResponse:
        corridor_rankings = [
            CorridorRanking(rank=1, corridor_id="orr_silk_board", corridor_name="Outer Ring Road (Silk Board)",
                          congestion_severity="Critical", structural_cause="300K+ daily trips on 4-lane road, single interchange bottleneck",
                          years_persistent=5),
            CorridorRanking(rank=2, corridor_id="bellandur_road", corridor_name="Bellandur Road",
                          congestion_severity="Severe", structural_cause="ORR-Whitefield connector, intersection bottlenecks, no grade separation",
                          years_persistent=4),
            CorridorRanking(rank=3, corridor_id="whitefield_main", corridor_name="Whitefield Main Road",
                          congestion_severity="Severe", structural_cause="400K+ tech workforce, severe tidal flows (inbound AM / outbound PM)",
                          years_persistent=5),
        ]

        emerging = [
            CorridorRanking(rank=1, corridor_id="thanisandra_hennur", corridor_name="Thanisandra / Hennur Road",
                          congestion_severity="High (emerging)", structural_cause="Rapid residential development, IT corridor extension",
                          years_persistent=2, annual_growth_pct=25.0),
            CorridorRanking(rank=2, corridor_id="hennur", corridor_name="Hennur Main Road",
                          congestion_severity="Moderate (growing)", structural_cause="New apartment complexes, inadequate road width",
                          years_persistent=2, annual_growth_pct=20.0),
            CorridorRanking(rank=3, corridor_id="sarjapur", corridor_name="Sarjapur Road",
                          congestion_severity="Moderate (growing)", structural_cause="Tech corridor extension, 18% annual growth",
                          years_persistent=3, annual_growth_pct=18.0),
        ]

        projects = [
            InfrastructureProject(project_name="Namma Metro Phase 2B", type="metro",
                                expected_impact="30-40% congestion reduction on Whitefield-Challaghatta corridor post-completion",
                                investment_crore=15000, timeline="2024-2028"),
            InfrastructureProject(project_name="15+ Flyover/Underpass Projects", type="flyover",
                                expected_impact="15-25% delay reduction at key intersections",
                                investment_crore=2500, timeline="2024-2027"),
            InfrastructureProject(project_name="ASTraM AI Signal Expansion", type="signal_optimization",
                                expected_impact="17-22% delay reduction per junction (60 → 200+ junctions by 2027)",
                                investment_crore=500, timeline="2024-2027"),
            InfrastructureProject(project_name="BWSSB Pipeline ORR", type="utility",
                                expected_impact="Temporary +25 min during construction, normalization in 3 weeks post-completion",
                                investment_crore=50, timeline="Feb 6 - Mar 6, 2026"),
        ]

        demand = [
            DemandMetric(metric="Vehicle Growth Rate", value="8% annually", trend="worsening",
                        insight="Doubling in 9 years at current rate. 12.3M registered vehicles on 3,500 km roads."),
            DemandMetric(metric="Trip Distribution", value="65% work, 15% education, 12% logistics, 8% other", trend="stable",
                        insight="Work commute dominance creates severe peak-hour concentration."),
            DemandMetric(metric="Mode Share (BMTC)", value="5M passengers/day, 6,000+ buses", trend="improving",
                        insight="Public transit absorption critical. Each bus replaces 40-60 cars."),
            DemandMetric(metric="On-Street Parking Impact", value="25-40% lane capacity reduction", trend="worsening",
                        insight="Parking policy reform could recover significant road capacity."),
        ]

        performance = {
            "congestion_yoy": "+1.7 percentage points year-over-year",
            "speed_yoy": "-1.0 km/h year-over-year",
            "time_loss_yoy": "+5.6% year-over-year (132 hours/year per commuter)",
            "signal_optimization_roi": "17-22% wait time reduction per junction (ASTraM AI)",
            "epath_performance": "30-35% ambulance response time improvement",
            "construction_routing": "17-22% delay reduction with AI-optimized routing",
        }

        recommendations = [
            "Priority 1: Accelerate ASTraM AI signal expansion (60→200+ junctions) — highest ROI at 17-22% per junction",
            "Priority 2: Fast-track Metro Phase 2B construction to offset Whitefield corridor saturation",
            "Priority 3: Implement congestion pricing on ORR during peak hours (15-25% demand reduction expected)",
            "Priority 4: Reform on-street parking policy to recover 25-40% lane capacity",
            "Priority 5: Incentivize staggered work hours for IT corridors (20-30% peak flattening potential)",
        ]

        return PlannerDashboardResponse(
            corridor_rankings=corridor_rankings,
            emerging_hotspots=emerging,
            infrastructure_projects=projects,
            demand_metrics=demand,
            performance_metrics=performance,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc),
        )
