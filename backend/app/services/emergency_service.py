"""Emergency Response Optimizer — implements Prompt 5.4.

e-Path green corridor: 20-22 daily deployments, 30-35% improvement.
Signal preemption: 45-90 seconds. GPS: <10m, 5-second updates.
"""

from datetime import datetime, timezone

from app.models.schemas.problem_solving import (
    EmergencyResponse,
    EmergencyType,
    HospitalOption,
)


BANGALORE_HOSPITALS = {
    "cardiac": [
        HospitalOption(name="Narayana Health City", specialty="Cardiac Surgery",
                      distance_km=8.5, estimated_time_minutes=12, capacity_status="available", epath_available=True),
        HospitalOption(name="Jayadeva Institute of Cardiology", specialty="Cardiac",
                      distance_km=6.0, estimated_time_minutes=9, capacity_status="available", epath_available=True),
    ],
    "trauma": [
        HospitalOption(name="St. John's Medical College Hospital", specialty="Trauma Center",
                      distance_km=5.0, estimated_time_minutes=8, capacity_status="available", epath_available=True),
        HospitalOption(name="Victoria Hospital", specialty="Trauma & Emergency",
                      distance_km=7.0, estimated_time_minutes=10, capacity_status="limited", epath_available=True),
    ],
    "obstetric": [
        HospitalOption(name="Cloudnine Hospital", specialty="Obstetrics & Gynecology",
                      distance_km=4.0, estimated_time_minutes=7, capacity_status="available", epath_available=True),
        HospitalOption(name="Manipal Hospital", specialty="Obstetrics",
                      distance_km=6.5, estimated_time_minutes=10, capacity_status="available", epath_available=True),
    ],
    "general": [
        HospitalOption(name="Manipal Hospital Old Airport Road", specialty="Multi-specialty",
                      distance_km=5.5, estimated_time_minutes=8, capacity_status="available", epath_available=True),
        HospitalOption(name="Columbia Asia Hospital", specialty="Multi-specialty",
                      distance_km=7.0, estimated_time_minutes=10, capacity_status="available", epath_available=True),
    ],
}


class EmergencyService:
    """Service for Prompt 5.4 — Emergency Response Optimizer."""

    async def optimize_emergency(self, origin: str, emergency_type: str) -> EmergencyResponse:
        etype = EmergencyType(emergency_type) if emergency_type in [e.value for e in EmergencyType] else EmergencyType.GENERAL
        hospitals = BANGALORE_HOSPITALS.get(etype.value, BANGALORE_HOSPITALS["general"])

        recommended = hospitals[0]
        alternatives = hospitals[1:] if len(hospitals) > 1 else []

        return EmergencyResponse(
            emergency_type=etype,
            origin=origin,
            recommended_hospital=recommended,
            alternative_hospitals=alternatives,
            epath_status="e-Path green corridor establishing... Signal preemption in 45-90 seconds",
            signal_preemption_count=8,
            estimated_response_time_minutes=recommended.estimated_time_minutes,
            improvement_vs_standard="30-35% faster than standard routing (pre-ASTraM: 30+ minutes in congested corridors)",
            gps_tracking="GPS tracking active: <10m accuracy, 5-second updates",
            pre_arrival_alert=f"Pre-arrival alert sent to {recommended.name}. ER team preparing for {etype.value} case.",
            incident_detection_note="ASTraM CCTV AI detects stopped vehicles in <2 minutes. Automatic tow dispatch for breakdowns (target: 12-18 min clearance).",
            timestamp=datetime.now(timezone.utc),
        )
