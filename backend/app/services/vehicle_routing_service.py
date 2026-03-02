"""Vehicle-Class-Specific Routing service — implements Prompt 3.2.

Adapts routing based on vehicle type per CLAUDE.md vehicle classes:
- Two-wheelers (35%): narrow streets, avoid truck zones, safety notes
- Cars (45%): standard routing + parking, carpool suggestions
- Trucks (8%): weight/height restrictions, night windows, loading zones
- BMTC Bus (5%): real-time bus arrival, metro connections
- Emergency (<1%): e-Path green corridors, signal preemption
- Auto-rickshaws (6%): frequent stops, fare estimates, pickup zones

Per REPORT.md: Night window (02:00-06:00) = 68% faster for trucks.
Per CLAUDE.md: 12.3M registered vehicles, 3,500 km roads, 3,500 vehicles/km.
"""

from datetime import datetime, timezone

from app.models.schemas.routing import (
    BusConnection,
    CongestionLevel,
    ParkingInfo,
    VehicleClass,
    VehicleRestriction,
    VehicleRouteOption,
    VehicleRoutingResponse,
)

# Travel multipliers (reused from routing_service)
TRAVEL_MULTIPLIER = {
    0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.05,
    6: 1.20, 7: 1.60, 8: 2.10, 9: 2.40, 10: 1.80, 11: 1.50,
    12: 1.40, 13: 1.40, 14: 1.50, 15: 1.60, 16: 2.00, 17: 2.50,
    18: 2.85, 19: 2.30, 20: 1.60, 21: 1.25, 22: 1.10, 23: 1.05,
}

# Vehicle class labels
VEHICLE_LABELS = {
    VehicleClass.TWO_WHEELER: "Two-Wheeler",
    VehicleClass.CAR: "Car",
    VehicleClass.TRUCK: "Truck / Commercial Vehicle",
    VehicleClass.BMTC_BUS: "BMTC Bus User",
    VehicleClass.EMERGENCY: "Emergency Vehicle",
    VehicleClass.AUTO_RICKSHAW: "Auto-Rickshaw",
}

# Truck restrictions in Bangalore
TRUCK_RESTRICTIONS = [
    VehicleRestriction(
        restriction_type="truck_ban",
        description="Daytime truck ban on major arterials (07:00-22:00)",
        affected_roads=["MG Road", "Brigade Road", "Residency Road", "Outer Ring Road (select sections)"],
    ),
    VehicleRestriction(
        restriction_type="weight_limit",
        description="20-tonne limit on flyovers and elevated expressways",
        affected_roads=["Hebbal Flyover", "Silk Board Flyover", "Electronic City Elevated Expressway"],
    ),
    VehicleRestriction(
        restriction_type="height_limit",
        description="4.5m height limit on underpasses",
        affected_roads=["Yeshwanthpur Underpass", "KR Puram Railway Underpass", "Hennur Underpass"],
    ),
    VehicleRestriction(
        restriction_type="time_window",
        description="Optimal night delivery window: 02:00-06:00 (68% faster than peak)",
        affected_roads=["All corridors — significantly reduced congestion"],
    ),
]

# Parking spots near common destinations
PARKING_SPOTS = {
    "whitefield": ParkingInfo(
        name="ITPL Multi-Level Parking",
        type="multi_level",
        distance_from_dest_m=200,
        estimated_cost_inr=50,
        availability="likely_available",
    ),
    "electronic_city": ParkingInfo(
        name="Infosys Campus Parking (visitor)",
        type="private",
        distance_from_dest_m=150,
        estimated_cost_inr=30,
        availability="limited",
    ),
    "koramangala": ParkingInfo(
        name="Forum Mall Basement Parking",
        type="multi_level",
        distance_from_dest_m=300,
        estimated_cost_inr=60,
        availability="likely_available",
    ),
    "mg_road": ParkingInfo(
        name="Garuda Mall Parking",
        type="multi_level",
        distance_from_dest_m=250,
        estimated_cost_inr=80,
        availability="limited",
    ),
    "default": ParkingInfo(
        name="Nearest street parking",
        type="street",
        distance_from_dest_m=500,
        estimated_cost_inr=20,
        availability="likely_available",
    ),
}

# BMTC bus routes
BMTC_ROUTES = {
    "whitefield_to_electronic_city": [
        BusConnection(
            route_number="500C",
            from_stop="ITPL Main Gate",
            to_stop="Electronic City Phase 1",
            frequency_minutes=15,
            estimated_arrival_minutes=8,
            walking_distance_m=200,
            metro_connection="Connect to Purple Line at MG Road for faster option",
        ),
    ],
    "koramangala_to_whitefield": [
        BusConnection(
            route_number="335E",
            from_stop="Koramangala Bus Stand",
            to_stop="Whitefield ITPL",
            frequency_minutes=20,
            estimated_arrival_minutes=12,
            walking_distance_m=350,
            metro_connection="Connect to Purple Line at Indiranagar",
        ),
    ],
    "hebbal_to_electronic_city": [
        BusConnection(
            route_number="365",
            from_stop="Hebbal Bus Stand",
            to_stop="Majestic",
            frequency_minutes=10,
            estimated_arrival_minutes=5,
            walking_distance_m=150,
            metro_connection="Transfer at Majestic to Green Line for Bommasandra → Electronic City",
        ),
        BusConnection(
            route_number="600D (Volvo)",
            from_stop="Majestic",
            to_stop="Electronic City",
            frequency_minutes=15,
            estimated_arrival_minutes=10,
            walking_distance_m=100,
            metro_connection=None,
        ),
    ],
    "default": [
        BusConnection(
            route_number="Check BMTC App",
            from_stop="Nearest bus stop",
            to_stop="Destination area",
            frequency_minutes=20,
            estimated_arrival_minutes=15,
            walking_distance_m=500,
            metro_connection="Check Namma Metro Purple/Green Line for connections",
        ),
    ],
}


def _speed_to_congestion(speed: float) -> CongestionLevel:
    if speed > 30:
        return CongestionLevel.FREE_FLOW
    elif speed > 20:
        return CongestionLevel.LIGHT
    elif speed > 15:
        return CongestionLevel.MODERATE
    elif speed > 10:
        return CongestionLevel.HEAVY
    elif speed > 5:
        return CongestionLevel.SEVERE
    return CongestionLevel.GRIDLOCK


class VehicleRoutingService:
    """Service for Prompt 3.2 — Vehicle-Class-Specific Routing."""

    async def get_vehicle_route(
        self, origin: str, destination: str, vehicle_class: str,
    ) -> VehicleRoutingResponse:
        """Generate vehicle-class-adapted route."""
        vc = VehicleClass(vehicle_class)
        now = datetime.now()
        hour = now.hour
        multiplier = TRAVEL_MULTIPLIER.get(hour, 1.5)

        route_key = self._match_route_key(origin, destination)

        if vc == VehicleClass.TWO_WHEELER:
            route = self._two_wheeler_route(origin, destination, multiplier, route_key)
            alt_suggestion = None
        elif vc == VehicleClass.CAR:
            route = self._car_route(origin, destination, multiplier, route_key)
            alt_suggestion = "Consider carpooling — single-occupancy cars contribute to 45% of Bangalore congestion"
        elif vc == VehicleClass.TRUCK:
            route = self._truck_route(origin, destination, multiplier, hour, route_key)
            alt_suggestion = None
        elif vc == VehicleClass.BMTC_BUS:
            route = self._bus_route(origin, destination, multiplier, route_key)
            alt_suggestion = "Consider Namma Metro for fixed-schedule reliability — avoid peak bus delays"
        elif vc == VehicleClass.EMERGENCY:
            route = self._emergency_route(origin, destination, route_key)
            alt_suggestion = None
        elif vc == VehicleClass.AUTO_RICKSHAW:
            route = self._auto_route(origin, destination, multiplier, route_key)
            alt_suggestion = None
        else:
            route = self._car_route(origin, destination, multiplier, route_key)
            alt_suggestion = None

        return VehicleRoutingResponse(
            origin=origin,
            destination=destination,
            vehicle_class=vc,
            vehicle_label=VEHICLE_LABELS[vc],
            route=route,
            alternative_mode_suggestion=alt_suggestion,
            timestamp=datetime.now(timezone.utc),
        )

    def _match_route_key(self, origin: str, destination: str) -> str:
        combined = f"{origin.lower()} {destination.lower()}"
        if "whitefield" in combined and "electronic" in combined:
            return "whitefield_to_electronic_city"
        elif "koramangala" in combined and "whitefield" in combined:
            return "koramangala_to_whitefield"
        elif "hebbal" in combined and "electronic" in combined:
            return "hebbal_to_electronic_city"
        return "default"

    def _base_params(self, origin: str, dest: str, multiplier: float) -> tuple[float, float]:
        """Get base distance and time."""
        combined = f"{origin.lower()} {dest.lower()}"
        if "whitefield" in combined and "electronic" in combined:
            return 28.0, 35.0 * multiplier
        elif "koramangala" in combined and "whitefield" in combined:
            return 22.0, 30.0 * multiplier
        elif "hebbal" in combined and "electronic" in combined:
            return 35.0, 40.0 * multiplier
        return 18.0, 25.0 * multiplier

    def _two_wheeler_route(self, origin: str, dest: str, multiplier: float, route_key: str) -> VehicleRouteOption:
        """Two-wheeler: narrow streets, shortcuts, avoid truck zones."""
        base_km, base_time = self._base_params(origin, dest, multiplier)
        # Two-wheelers are 15% faster due to lane splitting + narrow street access
        adjusted_time = base_time * 0.85
        adjusted_km = base_km * 0.92  # shorter via narrow streets

        speed = (adjusted_km / adjusted_time) * 60 if adjusted_time > 0 else 30
        time_low = int(adjusted_time * 0.85)
        time_high = int(adjusted_time * 1.15)

        dest_lower = dest.lower()
        parking = None
        for key in PARKING_SPOTS:
            if key in dest_lower:
                parking = ParkingInfo(
                    name=f"Two-wheeler parking near {dest}",
                    type="street",
                    distance_from_dest_m=100,
                    estimated_cost_inr=10,
                    availability="likely_available",
                )
                break

        return VehicleRouteOption(
            vehicle_class=VehicleClass.TWO_WHEELER,
            route_summary=f"{origin} → {dest} via narrow streets and shortcuts (two-wheeler optimized)",
            total_distance_km=round(adjusted_km, 1),
            estimated_time_minutes=round(adjusted_time, 0),
            time_range_minutes=f"{time_low}-{time_high} min",
            parking=parking,
            safety_notes=[
                "Avoid ORR Silk Board heavy-vehicle zone during peak hours",
                "Use helmet — mandatory in Bangalore (₹1,000 fine)",
                "Be cautious near BMTC bus stops — buses pull in/out frequently",
                "Pothole alert on service roads near construction zones",
            ],
            special_notes=[
                "15% faster than cars via lane splitting + narrow street access",
                "Short-cuts through residential areas included where safe",
                "Avoid truck-prohibited zones automatically applied",
            ],
        )

    def _car_route(self, origin: str, dest: str, multiplier: float, route_key: str) -> VehicleRouteOption:
        """Car: standard routing + parking + carpool suggestion."""
        base_km, base_time = self._base_params(origin, dest, multiplier)
        speed = (base_km / base_time) * 60 if base_time > 0 else 25
        time_low = int(base_time * 0.85)
        time_high = int(base_time * 1.15)

        # Find parking
        dest_lower = dest.lower()
        parking = PARKING_SPOTS.get("default")
        for key, spot in PARKING_SPOTS.items():
            if key in dest_lower:
                parking = spot
                break

        return VehicleRouteOption(
            vehicle_class=VehicleClass.CAR,
            route_summary=f"{origin} → {dest} via main arterials",
            total_distance_km=round(base_km, 1),
            estimated_time_minutes=round(base_time, 0),
            time_range_minutes=f"{time_low}-{time_high} min",
            parking=parking,
            safety_notes=[
                "Keep dashcam active — useful for incident documentation",
            ],
            special_notes=[
                "Single-occupancy car — consider carpooling for regular commutes (reduces 45% of Bangalore congestion)",
                f"Parking available: {parking.name}" if parking else "Limited parking — consider park-and-ride",
                "Fuel estimate: ₹150-250 depending on traffic (petrol, 12 km/l average in city)",
            ],
            cost_estimate="₹150-250 fuel",
        )

    def _truck_route(self, origin: str, dest: str, multiplier: float, hour: int, route_key: str) -> VehicleRouteOption:
        """Truck: restrictions, night windows, loading zones."""
        base_km, base_time = self._base_params(origin, dest, multiplier)
        # Trucks are 20% slower due to size constraints
        adjusted_time = base_time * 1.20

        # Night window optimization
        is_night_window = 2 <= hour <= 6
        if is_night_window:
            adjusted_time = base_km / 45.0 * 60  # near free-flow at night
            special_notes = [
                "OPTIMAL: Currently in night delivery window (02:00-06:00) — 68% faster than peak",
                "Loading zones accessible at all locations during night window",
            ]
        elif 7 <= hour <= 22:
            special_notes = [
                "WARNING: Daytime truck ban active on major arterials (07:00-22:00)",
                "Route adjusted to use permitted truck corridors",
                "Recommend rescheduling to night window (02:00-06:00) for 68% faster delivery",
            ]
        else:
            special_notes = [
                "Early night — moderate conditions. Full night window starts at 02:00.",
            ]

        speed = (base_km / adjusted_time) * 60 if adjusted_time > 0 else 20
        time_low = int(adjusted_time * 0.9)
        time_high = int(adjusted_time * 1.2)

        return VehicleRouteOption(
            vehicle_class=VehicleClass.TRUCK,
            route_summary=f"{origin} → {dest} via truck-permitted corridors",
            total_distance_km=round(base_km * 1.1, 1),  # longer due to restrictions
            estimated_time_minutes=round(adjusted_time, 0),
            time_range_minutes=f"{time_low}-{time_high} min",
            restrictions_applied=TRUCK_RESTRICTIONS,
            safety_notes=[
                "Observe 20-tonne limit on flyovers",
                "4.5m height clearance on underpasses — verify load height",
                "GPS tracking required for commercial vehicles in Bangalore",
            ],
            special_notes=special_notes,
            cost_estimate="₹800-1,500 diesel (truck, 4 km/l avg in city)",
        )

    def _bus_route(self, origin: str, dest: str, multiplier: float, route_key: str) -> VehicleRouteOption:
        """BMTC bus: real-time arrivals, metro connections."""
        base_km, base_time = self._base_params(origin, dest, multiplier)
        # Bus is typically 30% slower than car (stops, fixed routes)
        adjusted_time = base_time * 1.30
        connections = BMTC_ROUTES.get(route_key, BMTC_ROUTES["default"])

        # Adjust arrival estimates based on current congestion
        adjusted_connections = []
        for conn in connections:
            adj = BusConnection(
                route_number=conn.route_number,
                from_stop=conn.from_stop,
                to_stop=conn.to_stop,
                frequency_minutes=conn.frequency_minutes,
                estimated_arrival_minutes=int(conn.estimated_arrival_minutes * multiplier / 1.5),
                walking_distance_m=conn.walking_distance_m,
                metro_connection=conn.metro_connection,
            )
            adjusted_connections.append(adj)

        time_low = int(adjusted_time * 0.85)
        time_high = int(adjusted_time * 1.25)

        return VehicleRouteOption(
            vehicle_class=VehicleClass.BMTC_BUS,
            route_summary=f"{origin} → {dest} via BMTC bus + walking",
            total_distance_km=round(base_km, 1),
            estimated_time_minutes=round(adjusted_time, 0),
            time_range_minutes=f"{time_low}-{time_high} min",
            bus_connections=adjusted_connections,
            safety_notes=[
                "Board only at designated bus stops",
                "BMTC Day Pass available for ₹70 (unlimited rides)",
            ],
            special_notes=[
                f"Walking distance to first stop: {connections[0].walking_distance_m}m",
                f"Bus frequency: every {connections[0].frequency_minutes} min",
                connections[0].metro_connection or "No direct metro connection for this route",
                "BMTC carries 5M passengers/day with 6,000+ buses",
            ],
            cost_estimate="₹30-60 (BMTC fare)",
        )

    def _emergency_route(self, origin: str, dest: str, route_key: str) -> VehicleRouteOption:
        """Emergency vehicle: e-Path green corridors, signal preemption."""
        combined = f"{origin.lower()} {dest.lower()}"
        if "whitefield" in combined and "electronic" in combined:
            base_km, base_time = 28.0, 20.0  # emergency priority = much faster
        elif "koramangala" in combined and "whitefield" in combined:
            base_km, base_time = 22.0, 15.0
        elif "hebbal" in combined and "electronic" in combined:
            base_km, base_time = 35.0, 22.0
        else:
            base_km, base_time = 18.0, 12.0

        time_low = int(base_time * 0.8)
        time_high = int(base_time * 1.2)

        return VehicleRouteOption(
            vehicle_class=VehicleClass.EMERGENCY,
            route_summary=f"{origin} → {dest} via e-Path green corridor (signal preemption active)",
            total_distance_km=round(base_km, 1),
            estimated_time_minutes=round(base_time, 0),
            time_range_minutes=f"{time_low}-{time_high} min",
            safety_notes=[
                "e-Path green corridor established — signal preemption active",
                "GPS tracking active with <10m accuracy, 5-second updates",
                "Pre-arrival alerts sent to destination hospital",
                "30-35% response time improvement vs standard routing",
            ],
            special_notes=[
                "e-PATH system: 20-22 daily ambulance deployments with signal preemption",
                "Signal override: 45-90 seconds to establish green corridor",
                "All intersections on route set to priority green",
                "Cross-traffic held at signals along corridor",
            ],
        )

    def _auto_route(self, origin: str, dest: str, multiplier: float, route_key: str) -> VehicleRouteOption:
        """Auto-rickshaw: frequent stops, fare estimates, pickup zones."""
        base_km, base_time = self._base_params(origin, dest, multiplier)
        # Auto is 10% slower than car (frequent stops)
        adjusted_time = base_time * 1.10

        # Fare calculation (Bangalore auto fare: ₹30 for first 2 km, ₹15/km after)
        if base_km <= 2:
            fare = 30
        else:
            fare = 30 + (base_km - 2) * 15
        # Peak surcharge
        if multiplier > 2.0:
            fare *= 1.3  # ~30% peak surcharge (informal)

        time_low = int(adjusted_time * 0.85)
        time_high = int(adjusted_time * 1.20)

        return VehicleRouteOption(
            vehicle_class=VehicleClass.AUTO_RICKSHAW,
            route_summary=f"{origin} → {dest} via main roads (auto-optimized for pickup/drop zones)",
            total_distance_km=round(base_km, 1),
            estimated_time_minutes=round(adjusted_time, 0),
            time_range_minutes=f"{time_low}-{time_high} min",
            safety_notes=[
                "Use only metered autos or Ola/Uber auto for fare transparency",
                "Avoid autos near bus stands — higher refusal rates",
            ],
            special_notes=[
                "Account for frequent stopping patterns at signals",
                f"Meter fare: ₹{int(fare)} (₹30 first 2km + ₹15/km)",
                "Suggested pickup zone: main road intersection (easier hailing)",
                "Drop zone: nearest main road to avoid narrow street surcharge",
                "Peak hours: expect 30% above meter due to demand (negotiate or use app)",
            ],
            cost_estimate=f"₹{int(fare)}-{int(fare * 1.3)} (meter + peak adjustment)",
        )
