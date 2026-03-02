"""Commuter Decision Assistant — implements Prompt 5.1.

Morning routine (6:00-10:00) and evening return (16:00-21:00).
Per REPORT.md: Peak at 18:00 = 183%, 13.9 km/h.
"""

from datetime import datetime, timezone

from app.models.schemas.problem_solving import (
    CommuteMode,
    CommuterForecast,
    ModeComparison,
)

TRAVEL_MULTIPLIER = {
    0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.05,
    6: 1.20, 7: 1.60, 8: 2.10, 9: 2.40, 10: 1.80, 11: 1.50,
    12: 1.40, 13: 1.40, 14: 1.50, 15: 1.60, 16: 2.00, 17: 2.50,
    18: 2.85, 19: 2.30, 20: 1.60, 21: 1.25, 22: 1.10, 23: 1.05,
}


class CommuterService:
    """Service for Prompt 5.1 — Commuter Decision Assistant."""

    async def get_forecast(self, origin: str, destination: str) -> CommuterForecast:
        now = datetime.now()
        hour = now.hour
        multiplier = TRAVEL_MULTIPLIER.get(hour, 1.5)
        base_drive_time = 35  # default
        base_km = 22

        combined = f"{origin.lower()} {destination.lower()}"
        if "whitefield" in combined and "electronic" in combined:
            base_drive_time, base_km = 35, 28
        elif "koramangala" in combined and "whitefield" in combined:
            base_drive_time, base_km = 30, 22
        elif "hebbal" in combined and "electronic" in combined:
            base_drive_time, base_km = 40, 35

        drive_time = int(base_drive_time * multiplier)

        # Determine period
        if 6 <= hour < 10:
            period = "morning"
            greeting = f"Good morning! Here's your commute forecast for {origin} → {destination}:"
            opt_departure = f"{max(6, hour):02d}:{15 if multiplier < 2.0 else 0:02d}"
        elif 16 <= hour < 21:
            period = "evening"
            greeting = f"Good evening! Here's your return forecast for {origin} → {destination}:"
            opt_departure = f"{hour:02d}:{30 if multiplier > 2.5 else 0:02d}"
        else:
            period = "off_peak"
            greeting = f"Current conditions for {origin} → {destination}:"
            opt_departure = "Now (off-peak — ideal)"

        # Mode comparisons
        modes = [
            ModeComparison(
                mode=CommuteMode.DRIVE,
                estimated_time_minutes=drive_time,
                estimated_cost_inr=int(base_km * 8),  # ~₹8/km fuel
                reliability="medium" if multiplier > 2.0 else "high",
                notes=f"Via main arterials. Current multiplier: {multiplier:.1f}x free-flow.",
            ),
            ModeComparison(
                mode=CommuteMode.METRO,
                estimated_time_minutes=int(base_km / 35 * 60) + 15,  # metro speed ~35km/h + 15min access
                estimated_cost_inr=45,
                reliability="high",
                notes="Namma Metro Purple/Green Line. Fixed schedule, unaffected by road congestion.",
            ),
            ModeComparison(
                mode=CommuteMode.BUS,
                estimated_time_minutes=int(drive_time * 1.3),
                estimated_cost_inr=40,
                reliability="low" if multiplier > 2.0 else "medium",
                notes="BMTC bus. Affected by same traffic conditions as driving.",
            ),
            ModeComparison(
                mode=CommuteMode.COMBINATION,
                estimated_time_minutes=int(base_km / 35 * 60) + 20,  # metro + auto
                estimated_cost_inr=100,
                reliability="high",
                notes="Auto → Metro → Auto. Combines reliability of metro with door-to-door convenience.",
            ),
        ]

        # Event alert (demo)
        event_alert = None
        if now.weekday() >= 5:
            event_alert = "Weekend traffic patterns — Saturday can exceed weekday severity (101% recorded)"

        # Departure advice
        if multiplier < 1.5:
            advice = "Leave now — conditions are excellent!"
        elif multiplier < 2.0:
            advice = "Good time to depart — moderate congestion."
        elif multiplier < 2.5:
            advice = f"Heavy traffic. Consider delaying 30 min — congestion peaks at 18:00."
        else:
            advice = f"Severe congestion ({multiplier:.1f}x). Delay departure if possible or take Metro."

        overnight = []
        if period == "morning":
            overnight = [
                "No new overnight incidents on your route.",
                "BWSSB Pipeline work continues on ORR Zakir Nagar — expect +10 min if passing through.",
            ]

        return CommuterForecast(
            period=period,
            greeting=greeting,
            route_summary=f"{origin} → {destination}",
            optimal_departure=opt_departure,
            current_conditions=f"Traffic multiplier: {multiplier:.1f}x free-flow. Average speed ~{int(50/multiplier)} km/h on main corridors.",
            mode_comparisons=modes,
            event_alert=event_alert,
            overnight_updates=overnight,
            departure_advice=advice,
            savings_narrative=f"Following recommended route saves ~{int(drive_time*0.2)} min vs average",
            peak_insight="Peak congestion at 18:00 hits 183% (2.83x free-flow travel time). 13.9 km/h average speed — slower than cycling. Every minute of departure optimization matters enormously.",
            timestamp=datetime.now(timezone.utc),
        )
