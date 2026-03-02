"""Route Intelligence Narrative service.

Generates plain English narrative summaries by orchestrating existing services:
- RoutingService (Prompt 3.1) for route options and multimodal data
- IncidentService (Prompt 1.2) for active incidents on the route
- ConstructionService (Prompt 1.3) for active construction zones
- VehicleRoutingService (Prompt 3.2) for parking and vehicle-specific info
"""

from datetime import datetime, timezone

from app.models.schemas.narrative import NarrativeSection, RouteNarrativeResponse
from app.services.routing_service import RoutingService
from app.services.incident_service import IncidentService
from app.services.construction_service import ConstructionService
from app.services.vehicle_routing_service import VehicleRoutingService


TRAVEL_MULTIPLIER = {
    0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.05,
    6: 1.20, 7: 1.60, 8: 2.10, 9: 2.40, 10: 1.80, 11: 1.50,
    12: 1.40, 13: 1.40, 14: 1.50, 15: 1.60, 16: 2.00, 17: 2.50,
    18: 2.85, 19: 2.30, 20: 1.60, 21: 1.25, 22: 1.10, 23: 1.05,
}

CONGESTION_DESCRIPTIONS = {
    "free_flow": "free-flowing with no delays",
    "light": "moving well with minor slowdowns",
    "moderate": "moderately congested — expect some delays",
    "heavy": "heavily congested — significant delays likely",
    "severe": "severely congested — nearly at a standstill",
    "gridlock": "gridlocked — barely moving at all",
}

CONGESTION_SEVERITY_ORDER = ["free_flow", "light", "moderate", "heavy", "severe", "gridlock"]


class NarrativeService:
    """Generates plain English route intelligence narratives."""

    def __init__(self) -> None:
        self.routing_service = RoutingService()
        self.incident_service = IncidentService()
        self.construction_service = ConstructionService()
        self.vehicle_service = VehicleRoutingService()

    async def generate_narrative(
        self, origin: str, destination: str, vehicle_class: str | None = None,
    ) -> RouteNarrativeResponse:
        smart_routes = await self.routing_service.get_routes(origin, destination)
        incidents = await self.incident_service.get_active_incidents()
        construction = await self.construction_service.get_all_zones()
        vehicle_route = await self.vehicle_service.get_vehicle_route(
            origin, destination, vehicle_class or "car",
        )

        sections = [
            self._build_overview(origin, destination, smart_routes),
            self._build_traffic_now(smart_routes),
            self._build_best_route(smart_routes),
            self._build_incidents(incidents, smart_routes),
            self._build_construction(construction, smart_routes),
            self._build_parking(vehicle_route),
            self._build_pro_tips(smart_routes, vehicle_route),
        ]

        return RouteNarrativeResponse(
            origin=origin,
            destination=destination,
            vehicle_class=vehicle_class,
            sections=sections,
            generated_at=datetime.now(timezone.utc),
        )

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _build_overview(self, origin, destination, smart_routes):
        hour = datetime.now().hour
        multiplier = TRAVEL_MULTIPLIER.get(hour, 1.5)

        if 7 <= hour <= 9:
            time_ctx = "morning rush hour"
        elif 17 <= hour <= 19:
            time_ctx = "evening rush hour"
        elif 10 <= hour <= 16:
            time_ctx = "midday"
        elif 20 <= hour <= 23:
            time_ctx = "late evening"
        else:
            time_ctx = "off-peak hours"

        fastest = smart_routes.routes[0]
        congestion_word = fastest.congestion_level.value.replace("_", " ")

        content = (
            f"Heading from {origin} to {destination}? Here's what you need to know. "
            f"It's currently {time_ctx} and the fastest route will take about "
            f"{fastest.time_range_minutes}. The trip is {fastest.total_distance_km} km "
            f"with {congestion_word} congestion overall. Let's break it down for you."
        )

        severity = "warning" if multiplier >= 2.0 else "info"
        return NarrativeSection(
            section_id="overview", title="Trip Overview", icon="🗺",
            content=content, severity=severity,
        )

    def _build_traffic_now(self, smart_routes):
        fastest = smart_routes.routes[0]
        parts = []
        worst_level = "free_flow"
        for seg in fastest.segments:
            level = seg.congestion_level.value if hasattr(seg.congestion_level, "value") else seg.congestion_level
            desc = CONGESTION_DESCRIPTIONS.get(level, "unknown conditions")
            parts.append(f"{seg.road_name} ({seg.distance_km} km): {desc} at {seg.speed_kmh:.0f} km/h")
            if CONGESTION_SEVERITY_ORDER.index(level) > CONGESTION_SEVERITY_ORDER.index(worst_level):
                worst_level = level

        content = "Here's the segment-by-segment breakdown: " + ". ".join(parts) + "."

        severity_map = {
            "free_flow": "success", "light": "success", "moderate": "info",
            "heavy": "warning", "severe": "alert", "gridlock": "alert",
        }
        return NarrativeSection(
            section_id="traffic_now", title="Traffic Right Now", icon="🚦",
            content=content, severity=severity_map.get(worst_level, "info"),
        )

    def _build_best_route(self, smart_routes):
        fastest = smart_routes.routes[0]
        content = (
            f"We recommend the {fastest.label}: {fastest.summary}. "
            f"Estimated time: {fastest.time_range_minutes} "
            f"(distance: {fastest.total_distance_km} km, confidence: {fastest.confidence_pct}%). "
        )

        # Mention savings from the reliable route
        if len(smart_routes.routes) > 1:
            reliable = smart_routes.routes[1]
            if reliable.savings_vs_default:
                content += (
                    f"If you prefer predictability, the {reliable.label} "
                    f"({reliable.summary}) offers {reliable.savings_vs_default}. "
                )

        # Multimodal comparison
        mm = smart_routes.multimodal
        if mm:
            content += (
                f"Alternatively, public transport ({mm.comparison_vs_driving}) "
                f"takes {mm.total_time_minutes:.0f} min for about Rs.{mm.total_cost_inr:.0f}."
            )

        return NarrativeSection(
            section_id="best_route", title="Best Route", icon="🛣",
            content=content, severity="success",
        )

    def _build_incidents(self, incidents_response, smart_routes):
        route_roads = set()
        for seg in smart_routes.routes[0].segments:
            for word in seg.road_name.lower().split():
                if len(word) > 3:
                    route_roads.add(word)

        relevant = []
        for inc in incidents_response.incidents:
            inc_road = inc.location.road_name.lower()
            if any(word in inc_road for word in route_roads):
                relevant.append(inc)

        if not relevant:
            return NarrativeSection(
                section_id="incidents", title="Incidents", icon="✅",
                content="Great news — no active incidents on your route! The road is clear.",
                severity="success",
            )

        parts = []
        max_sev = 0
        for inc in relevant[:3]:
            parts.append(
                f"{inc.type_label} on {inc.location.road_name} "
                f"(severity: {inc.severity}/5, +{inc.delay_minutes:.0f} min delay, "
                f"{inc.affected_length_km:.1f} km affected)"
            )
            max_sev = max(max_sev, inc.severity)

        plural = "s" if len(relevant) > 1 else ""
        verb = "are" if len(relevant) > 1 else "is"
        content = (
            f"Heads up — there {verb} {len(relevant)} active incident{plural} "
            f"on your route: " + ". ".join(parts) + "."
        )
        if relevant[0].description:
            content += f" Details: {relevant[0].description}"

        return NarrativeSection(
            section_id="incidents", title="Active Incidents", icon="⚠",
            content=content, severity="alert" if max_sev >= 4 else "warning",
        )

    def _build_construction(self, construction_response, smart_routes):
        route_roads = set()
        for seg in smart_routes.routes[0].segments:
            for word in seg.road_name.lower().split():
                if len(word) > 3:
                    route_roads.add(word)

        relevant = []
        for zone in construction_response.zones:
            zone_text = " ".join(zone.affected_roads).lower()
            if any(word in zone_text for word in route_roads):
                relevant.append(zone)

        if not relevant:
            return NarrativeSection(
                section_id="construction", title="Construction Zones", icon="✅",
                content="No active construction zones are affecting your route today.",
                severity="success",
            )

        parts = []
        for zone in relevant:
            part = (
                f"{zone.project_name} by {zone.agency} "
                f"({zone.completion_pct:.0f}% complete, {zone.lane_restriction})"
            )
            if zone.additional_delay_minutes:
                part += f" — expect +{zone.additional_delay_minutes} extra delay"
            parts.append(part)

        plural = "s" if len(relevant) > 1 else ""
        content = (
            f"Watch out for {len(relevant)} construction zone{plural}: "
            + ". ".join(parts) + "."
        )

        return NarrativeSection(
            section_id="construction", title="Construction Zones", icon="🚧",
            content=content, severity="warning",
        )

    def _build_parking(self, vehicle_route):
        parking = vehicle_route.route.parking if vehicle_route else None

        if not parking:
            return NarrativeSection(
                section_id="parking", title="Parking", icon="🅿",
                content=(
                    "Parking information not available for this destination. "
                    "Consider checking Google Maps for nearby options."
                ),
                severity="info",
            )

        avail_text = {
            "likely_available": "spaces are likely available",
            "limited": "spaces are limited — arrive early",
            "full": "currently reported as full — consider alternatives",
        }.get(parking.availability, "availability unknown")

        cost_text = f" at Rs.{parking.estimated_cost_inr:.0f}/visit" if parking.estimated_cost_inr else ""

        content = (
            f"Park at {parking.name} ({parking.type.replace('_', ' ')} parking, "
            f"{parking.distance_from_dest_m}m from your destination{cost_text}). "
            f"Currently, {avail_text}."
        )

        return NarrativeSection(
            section_id="parking", title="Parking", icon="🅿",
            content=content,
            severity="warning" if parking.availability == "full" else "info",
        )

    def _build_pro_tips(self, smart_routes, vehicle_route):
        hour = datetime.now().hour
        multiplier = TRAVEL_MULTIPLIER.get(hour, 1.5)
        tips: list[str] = []

        # Time-based advice
        if multiplier >= 2.5:
            tips.append(
                "You're hitting peak congestion right now. "
                "If you can delay by 30-45 minutes, travel times drop significantly."
            )
        elif multiplier >= 2.0:
            tips.append(
                "Traffic is heavy but manageable. "
                "Leaving in the next 15 minutes is better than waiting for peak."
            )
        elif multiplier <= 1.2:
            tips.append("You're in the sweet spot — off-peak conditions. This is as good as it gets!")

        # Multimodal tip
        mm = smart_routes.multimodal
        if mm and mm.total_time_minutes < smart_routes.routes[0].estimated_time_minutes:
            tips.append(f"Public transport is actually faster right now — {mm.comparison_vs_driving}.")

        # Vehicle-specific tips
        if vehicle_route and vehicle_route.route.special_notes:
            tips.append(vehicle_route.route.special_notes[0])

        # Bangalore-specific tip
        if 18 <= hour <= 19:
            tips.append(
                "Peak hour (18:00) sees 183% congestion with average speed dropping "
                "to 13.9 km/h — slower than cycling. Every minute of optimization counts."
            )

        content = " ".join(tips) if tips else (
            "Safe travels! Check back for updated conditions if your departure time changes."
        )

        return NarrativeSection(
            section_id="pro_tips", title="Pro Tips", icon="💡",
            content=content, severity="info",
        )
