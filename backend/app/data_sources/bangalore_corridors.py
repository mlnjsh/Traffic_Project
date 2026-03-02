"""Bangalore corridor definitions seeded from REPORT.md Section 2.1 and CLAUDE.md.

8 critical traffic zones with real coordinates and characteristics.
"""

CORRIDORS = [
    {
        "id": "orr_silk_board",
        "name": "Outer Ring Road (Silk Board - Marathahalli)",
        "short_name": "ORR Silk Board",
        "direction": "Bidirectional",
        "free_flow_speed": 50.0,
        "road_class": "Major Arterial (ORR)",
        "daily_trips": 300000,
        "segments": [
            {"start": {"lat": 12.9170, "lng": 77.6230}, "end": {"lat": 12.9280, "lng": 77.6320}},
            {"start": {"lat": 12.9280, "lng": 77.6320}, "end": {"lat": 12.9400, "lng": 77.6410}},
            {"start": {"lat": 12.9400, "lng": 77.6410}, "end": {"lat": 12.9500, "lng": 77.6500}},
            {"start": {"lat": 12.9500, "lng": 77.6500}, "end": {"lat": 12.9570, "lng": 77.6690}},
        ],
    },
    {
        "id": "orr_zakir_nagar",
        "name": "ORR (Zakir Nagar - Goraguntepalya) — BWSSB Pipeline Zone",
        "short_name": "ORR Zakir Nagar",
        "direction": "Bidirectional",
        "free_flow_speed": 50.0,
        "road_class": "Major Arterial (ORR)",
        "daily_trips": 200000,
        "segments": [
            {"start": {"lat": 13.0421, "lng": 77.6088}, "end": {"lat": 13.0380, "lng": 77.5900}},
            {"start": {"lat": 13.0380, "lng": 77.5900}, "end": {"lat": 13.0340, "lng": 77.5700}},
            {"start": {"lat": 13.0340, "lng": 77.5700}, "end": {"lat": 13.0284, "lng": 77.5403}},
        ],
    },
    {
        "id": "bellandur_road",
        "name": "Bellandur Road (ORR to Whitefield-Sarjapur connector)",
        "short_name": "Bellandur Road",
        "direction": "East-West",
        "free_flow_speed": 40.0,
        "road_class": "Major Connector",
        "daily_trips": 150000,
        "segments": [
            {"start": {"lat": 12.9260, "lng": 77.6620}, "end": {"lat": 12.9310, "lng": 77.6750}},
            {"start": {"lat": 12.9310, "lng": 77.6750}, "end": {"lat": 12.9350, "lng": 77.6900}},
        ],
    },
    {
        "id": "whitefield_main",
        "name": "Whitefield Main Road (ITPL - EPIP Zone)",
        "short_name": "Whitefield Main",
        "direction": "Tidal (Inbound AM / Outbound PM)",
        "free_flow_speed": 40.0,
        "road_class": "Tech Corridor",
        "daily_trips": 400000,
        "segments": [
            {"start": {"lat": 12.9698, "lng": 77.7260}, "end": {"lat": 12.9750, "lng": 77.7400}},
            {"start": {"lat": 12.9750, "lng": 77.7400}, "end": {"lat": 12.9800, "lng": 77.7500}},
            {"start": {"lat": 12.9800, "lng": 77.7500}, "end": {"lat": 12.9850, "lng": 77.7600}},
        ],
    },
    {
        "id": "electronic_city",
        "name": "Electronic City / Hosur Road",
        "short_name": "Electronic City",
        "direction": "Bidirectional (shift-based)",
        "free_flow_speed": 45.0,
        "road_class": "Elevated Expressway + Surface Road",
        "daily_trips": 300000,
        "segments": [
            {"start": {"lat": 12.8450, "lng": 77.6600}, "end": {"lat": 12.8550, "lng": 77.6620}},
            {"start": {"lat": 12.8550, "lng": 77.6620}, "end": {"lat": 12.8700, "lng": 77.6640}},
        ],
    },
    {
        "id": "bannerghatta_road",
        "name": "Bannerghatta Road",
        "short_name": "Bannerghatta Rd",
        "direction": "North-South",
        "free_flow_speed": 35.0,
        "road_class": "Mixed Use Arterial",
        "daily_trips": 180000,
        "segments": [
            {"start": {"lat": 12.9000, "lng": 77.5970}, "end": {"lat": 12.8900, "lng": 77.5980}},
            {"start": {"lat": 12.8900, "lng": 77.5980}, "end": {"lat": 12.8800, "lng": 77.5990}},
        ],
    },
    {
        "id": "cbd_mg_road",
        "name": "CBD (MG Road - Koramangala)",
        "short_name": "CBD MG Road",
        "direction": "Radial convergence",
        "free_flow_speed": 30.0,
        "road_class": "Central Business District",
        "daily_trips": 200000,
        "segments": [
            {"start": {"lat": 12.9716, "lng": 77.5946}, "end": {"lat": 12.9750, "lng": 77.6050}},
            {"start": {"lat": 12.9750, "lng": 77.6050}, "end": {"lat": 12.9700, "lng": 77.6150}},
        ],
    },
    {
        "id": "thanisandra_hennur",
        "name": "Thanisandra / Hennur Road (Emerging Hotspot)",
        "short_name": "Thanisandra-Hennur",
        "direction": "North-South",
        "free_flow_speed": 35.0,
        "road_class": "Emerging Corridor",
        "daily_trips": 120000,
        "segments": [
            {"start": {"lat": 13.0500, "lng": 77.6300}, "end": {"lat": 13.0400, "lng": 77.6350}},
            {"start": {"lat": 13.0400, "lng": 77.6350}, "end": {"lat": 13.0300, "lng": 77.6400}},
        ],
    },
]
