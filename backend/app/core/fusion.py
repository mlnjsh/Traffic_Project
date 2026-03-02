"""Multi-source data fusion engine.

Per CLAUDE.md:
- ASTraM prioritized for incident location/type (authoritative local)
- TomTom prioritized for speed/delay estimation (global consistency)
- Conflict resolution: recency weighting + confidence scoring

Per REPORT.md Section 1.2.1:
Integration middleware must resolve schema heterogeneity:
ASTraM's proprietary incident severity classification,
TomTom's standardized congestion levels (0-100%).
"""

from datetime import datetime, timezone

from app.models.schemas.traffic import CongestionColor, TrendDirection


def speed_to_color(speed_kmh: float) -> CongestionColor:
    """Map speed to congestion color per CLAUDE.md color scheme.

    Green: >30 km/h, <30% congestion
    Yellow: 20-30 km/h, 30-60%
    Orange: 10-20 km/h, 60-100%
    Red: 5-10 km/h, 100-150%
    Black: <5 km/h, >150% gridlock
    """
    if speed_kmh > 30:
        return CongestionColor.GREEN
    elif speed_kmh > 20:
        return CongestionColor.YELLOW
    elif speed_kmh > 10:
        return CongestionColor.ORANGE
    elif speed_kmh > 5:
        return CongestionColor.RED
    else:
        return CongestionColor.BLACK


def congestion_to_color(congestion_pct: float) -> CongestionColor:
    """Alternative color mapping from congestion percentage."""
    if congestion_pct < 30:
        return CongestionColor.GREEN
    elif congestion_pct < 60:
        return CongestionColor.YELLOW
    elif congestion_pct < 100:
        return CongestionColor.ORANGE
    elif congestion_pct < 150:
        return CongestionColor.RED
    else:
        return CongestionColor.BLACK


def fuse_color(speed_kmh: float, congestion_pct: float) -> CongestionColor:
    """Fuse speed and congestion into a single color.

    Use the WORSE of the two signals (conservative approach).
    Per CLAUDE.md: TomTom prioritized for speed/delay estimation.
    """
    color_by_speed = speed_to_color(speed_kmh)
    color_by_congestion = congestion_to_color(congestion_pct)

    severity_order = [
        CongestionColor.GREEN,
        CongestionColor.YELLOW,
        CongestionColor.ORANGE,
        CongestionColor.RED,
        CongestionColor.BLACK,
    ]

    idx_speed = severity_order.index(color_by_speed)
    idx_congestion = severity_order.index(color_by_congestion)

    return severity_order[max(idx_speed, idx_congestion)]


def estimate_trend(congestion_pct: float) -> tuple[TrendDirection, str]:
    """Estimate congestion trend based on current time and congestion level.

    Per REPORT.md Section 2.2.1:
    - 16:30-18:00: Worsening (building to 183% peak)
    - 18:00-18:30: Stable at peak
    - 18:30-21:30: Improving (gradual recovery)
    - 21:30-07:00: Stable/improving (off-peak)
    - 07:00-10:00: Worsening (morning peak)
    - 10:00-16:30: Stable (inter-peak)
    """
    now = datetime.now()
    hour = now.hour + now.minute / 60.0

    if 7.0 <= hour < 10.0:
        return TrendDirection.WORSENING, "Morning peak building — congestion increasing across corridors"
    elif 10.0 <= hour < 16.0:
        return TrendDirection.STABLE, "Inter-peak period — moderate, stable conditions"
    elif 16.0 <= hour < 18.0:
        return TrendDirection.WORSENING, "Evening peak building — expect conditions to deteriorate until ~18:00"
    elif 18.0 <= hour < 18.5:
        return TrendDirection.STABLE, "At peak congestion (183% typical at 18:00). System stress — minor incidents can trigger cascading gridlock."
    elif 18.5 <= hour < 21.5:
        return TrendDirection.IMPROVING, "Past peak — gradual recovery underway. Near-normal conditions expected by 21:30."
    elif 21.5 <= hour <= 24.0 or 0.0 <= hour < 2.0:
        return TrendDirection.IMPROVING, "Late evening — approaching off-peak conditions"
    else:
        return TrendDirection.STABLE, "Off-peak window (02:00-06:00) — free-flow conditions, <20% congestion"


def calculate_delay(
    speed_kmh: float,
    free_flow_speed_kmh: float,
    segment_length_km: float = 10.0,
) -> tuple[float, float, float]:
    """Calculate travel time and delay.

    Returns (travel_time_min, free_flow_time_min, delay_min).
    Per REPORT.md: 10 km travel time at peak = 36m 9s (vs 14m free flow).
    """
    if speed_kmh <= 0:
        speed_kmh = 3.0  # minimum 3 km/h to avoid division by zero

    travel_time = (segment_length_km / speed_kmh) * 60  # minutes
    free_flow_time = (segment_length_km / free_flow_speed_kmh) * 60
    delay = max(travel_time - free_flow_time, 0)

    return round(travel_time, 1), round(free_flow_time, 1), round(delay, 1)
