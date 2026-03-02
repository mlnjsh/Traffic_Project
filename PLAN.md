# Bangalore Traffic Intelligence Bot — Free-Tier Implementation Plan

## Why This App? The Problem It Solves

### The Crisis: Bangalore Is Choking

Bangalore's traffic is not just an inconvenience — it's a **city-wide economic and humanitarian crisis**:

| Metric | Reality |
|--------|---------|
| Registered vehicles | **12.3 million** on just 3,500 km of road |
| Vehicle density | **3,500 vehicles per km** (one of the highest globally) |
| Global congestion rank | **6th worst city in the world** (TomTom 2025) |
| Average congestion level | **74.4%** — roads are nearly always jammed |
| Time lost per commuter | **132 hours/year** (5.5 full days sitting in traffic) |
| Peak hour speed | **13.9 km/h** (slower than cycling at 15-20 km/h) |
| Annual economic cost | **Rs 50,000 crore ($6 billion USD)** in lost productivity, fuel, pollution |

### Who Suffers and How

**Daily commuters (12+ million people)**
- No way to know *before leaving home* whether their route is jammed
- Google Maps shows current traffic but doesn't answer "When will it get better?"
- No construction-aware routing — they drive into blocked roads daily
- Two-wheeler riders (35% of traffic) get no routing tailored to their vehicle

**Logistics & delivery operators**
- Trucks stuck in daytime congestion despite night-window availability
- No real-time construction zone tracking for fleet route planning
- Fuel waste from inefficient routing costs crores annually

**BMTC bus commuters**
- No reliable real-time arrival predictions adjusted for actual traffic
- Cannot plan multi-modal trips (bus + metro + walk) effectively

**Emergency services**
- Ambulances delayed in congestion — every minute costs lives
- No centralized system for green corridor activation

**City planners & traffic police (BTP)**
- Decisions made on outdated/manual traffic counts
- No predictive modeling for event impact (cricket matches, rallies, festivals)
- Cannot simulate "what if" scenarios before implementing changes

### What Exists Today vs. What's Missing

| Feature | Google Maps | Waze | This App |
|---------|------------|------|----------|
| Current traffic | Yes | Yes | Yes (multi-source fused) |
| "When will it clear?" prediction | No | No | **Yes (ML-based, 15-60 min)** |
| Vehicle-class routing (bike/truck/bus) | No | No | **Yes** |
| Construction zone tracking with timeline | No | Partial | **Yes (with completion %)** |
| Signal countdown (time-to-green) | No | No | **Yes (via Mappls)** |
| Satellite flood detection | No | No | **Yes (Sentinel-2)** |
| Bangalore-specific incident data (BTP) | No | No | **Yes (ASTraM integration)** |
| City planner analytics dashboard | No | No | **Yes** |
| Conversational bot interface | No | No | **Yes** |
| Event impact prediction | No | No | **Yes** |
| Open/free for citizens | Free | Free | **Free** |

### The 5 Core Problems This App Solves

**1. "Should I leave now or wait?" (Prediction Gap)**
- Current apps show what traffic looks like *right now*
- This app predicts what it will look like in 15, 30, 60 minutes
- Commuters can time their departure to avoid peak congestion
- Target: Save 20-30 minutes per commuter per day

**2. "Which route works for MY vehicle?" (Vehicle-Specific Routing)**
- A two-wheeler can take narrow lanes a car cannot
- A truck has height/weight restrictions and night-only windows
- An ambulance needs green corridor activation
- No existing app provides vehicle-class-specific routing for Bangalore

**3. "Why is this road blocked?" (Information Fragmentation)**
- Traffic data is scattered: BTP has incidents, BBMP has construction, TomTom has speeds
- No single source fuses all of them into one view
- This app merges ASTraM + TomTom + Mappls + OpenCity into a unified real-time picture

**4. "When will this construction end?" (Construction Transparency)**
- Bangalore has dozens of simultaneous road projects (metro, flyovers, drains)
- Citizens have no visibility into completion timelines
- This app tracks construction progress with satellite imagery and official milestones

**5. "Is my area flooding?" (Monsoon + Emergency Response)**
- Bangalore floods regularly during monsoon (June-September)
- Roads become impassable with no advance warning
- Sentinel-2 satellite imagery detects waterlogging
- Emergency routing helps ambulances and citizens navigate around flooded zones

### Impact Targets

| Metric | Target |
|--------|--------|
| Effective congestion reduction for users | **15-25%** (through information optimization) |
| Average time saved per commuter per day | **20-30 minutes** |
| Prediction accuracy (15-min horizon) | **>70%** |
| Incident detection to notification | **<2 minutes** |
| Route compliance rate | **>70%** of users follow suggested routes |
| Emergency response time improvement | **15-20%** faster ambulance routing |

### Who Benefits

| User Group | Population | Key Benefit |
|-----------|-----------|-------------|
| Daily commuters | ~6 million | Departure timing, alternate routes, time savings |
| Two-wheeler riders | ~4.3 million | Vehicle-specific narrow-lane routing |
| Logistics/delivery | ~500K vehicles | Night window optimization, construction avoidance |
| BMTC riders | ~4 million trips/day | Reliable arrival predictions |
| City planners | BTP, BBMP, BMTC | Data-driven decisions, what-if modeling |
| Emergency services | BTP, hospitals | Green corridor routing, flood alerts |
| Tourists/visitors | Variable | Navigate unfamiliar Bangalore traffic confidently |

---

## Context

Build the full traffic intelligence system using **100% free hosting and services**. The project currently has only documentation (CLAUDE.md, skills.md, PROMPTS.MD) — no code exists. This plan covers architecture, project structure, phased implementation, and Google Maps + satellite integration.

---

## Free-Tier Budget (Hard Constraints)

| Service | Free Tier Limit | Role |
|---------|----------------|------|
| **Oracle Cloud ARM (Mumbai)** | 2 VMs: 4 OCPU, 24 GB RAM total — always free | Backend + ML inference |
| **Cloudflare Pages** | Unlimited bandwidth, 100K Workers/day | Frontend hosting |
| **Neon PostgreSQL + PostGIS** | 0.5 GB storage | Database |
| **Upstash Redis** | 500K commands/month, 256 MB | Cache |
| **Upstash Kafka** | 10K messages/day | Cross-service events only |
| **Google Maps Platform** | $200/month free credit | Maps + satellite view |
| **TomTom Traffic** | 50K tiles/day + 2,500 API calls/day | Primary traffic data |
| **Sentinel-2 (ESA)** | Free, 10m resolution, 5-day revisit | Flood/construction detection |
| **ISRO Bhuvan** | Free | Indian satellite data |
| **HuggingFace Spaces** | 2 CPU, 16 GB RAM | ML model hosting (optional) |

**Key design constraint:** Upstash Kafka's 10K messages/day cannot support real-time streaming. Use an **in-process asyncio event bus** on Oracle VM for real-time, and Kafka only for cross-service alerts (~50-100/day).

---

## Architecture

```
                    ┌──────────────────┐
                    │ Cloudflare Pages  │
                    │ (Next.js Frontend)│
                    └────────┬─────────┘
                             │ HTTPS + WebSocket
                    ┌────────▼─────────┐
                    │ Oracle ARM VM 1   │
                    │ (FastAPI Backend)  │
                    │ - API Gateway      │
                    │ - Data Fusion      │
                    │ - Scheduler/Cron   │
                    │ - WebSocket Server │
                    │ - In-process Bus   │
                    └──┬─────┬──────┬──┘
                       │     │      │
              ┌────────▼┐ ┌─▼────┐ ┌▼───────────┐
              │  Neon    │ │Upstash│ │Oracle VM 2  │
              │PostgreSQL│ │Redis  │ │(ML + Satellite│
              │+ PostGIS │ │Cache  │ │ Processing)  │
              └─────────┘ └──────┘ └─────────────┘
                       │
          ┌────────────▼─────────────────────┐
          │ External APIs (Polled every 2 min)│
          │ - TomTom Traffic (flow + incidents)│
          │ - ASTraM/BTP (incidents)           │
          │ - OpenCity (daily batch)            │
          │ - Sentinel-2 (weekly batch)        │
          └────────────────────────────────────┘
```

---

## Project Structure

```
Traffic_Project/
├── CLAUDE.md, PROMPTS.MD, skills.md     # Existing docs
├── README.md
├── .gitignore, .env.example
├── docker-compose.yml
│
├── backend/                              # Python FastAPI (Oracle VM 1)
│   ├── requirements.txt, Dockerfile
│   ├── alembic/                          # DB migrations
│   └── app/
│       ├── main.py                       # FastAPI entry + lifespan
│       ├── config.py                     # Pydantic settings
│       ├── api/v1/
│       │   ├── traffic.py                # GET /traffic/corridors
│       │   ├── incidents.py              # GET /incidents
│       │   ├── routes.py                 # POST /routes/optimize
│       │   ├── predictions.py            # GET /predictions/{corridor}
│       │   ├── heatmap.py                # GET /heatmap/data
│       │   ├── construction.py           # GET /construction/zones
│       │   ├── satellite.py              # GET /satellite/latest
│       │   ├── bot.py                    # POST /bot/chat
│       │   └── ws.py                     # WebSocket live updates
│       ├── core/
│       │   ├── fusion.py                 # Multi-source data fusion
│       │   ├── prediction.py             # Prediction orchestrator
│       │   ├── routing.py                # Vehicle-class routing
│       │   ├── heatmap.py                # Heatmap tile generator
│       │   └── bot_engine.py             # NLU + response gen
│       ├── data_sources/
│       │   ├── tomtom.py                 # TomTom Flow + Incidents
│       │   ├── astram.py                 # ASTraM/BTP feed
│       │   ├── mappls.py                 # Signal countdown
│       │   ├── opencity.py               # OpenCity batch parser
│       │   ├── google_maps.py            # Directions + Distance Matrix
│       │   └── sentinel.py               # Sentinel-2 downloader
│       ├── models/
│       │   ├── db/                        # SQLAlchemy ORM
│       │   └── schemas/                   # Pydantic schemas
│       ├── scheduler/
│       │   ├── poller.py                 # APScheduler polling loop
│       │   └── tasks.py                  # Per-source poll tasks
│       ├── event_bus/
│       │   └── bus.py                    # asyncio pub-sub (replaces Kafka)
│       ├── services/                      # Business logic layer
│       └── utils/                         # Geo helpers, caching, rate limiting
│
├── ml/                                    # ML models (Oracle VM 2)
│   ├── requirements.txt, Dockerfile
│   ├── training/
│   │   ├── prepare_kaggle_data.py
│   │   ├── train_short_term.py           # LightGBM 0-15 min
│   │   ├── train_medium_term.py          # LightGBM 15-60 min
│   │   └── evaluate.py
│   ├── inference/
│   │   ├── server.py                     # FastAPI inference server
│   │   └── satellite_analyzer.py         # Flood/construction from imagery
│   └── models/                            # Saved ONNX artifacts
│
├── frontend/                              # Next.js (Cloudflare Pages)
│   ├── package.json, next.config.js, wrangler.toml
│   └── src/
│       ├── app/
│       │   ├── page.tsx                  # Map dashboard (main page)
│       │   ├── chat/page.tsx             # Bot chat
│       │   ├── routes/page.tsx           # Route planner
│       │   ├── satellite/page.tsx        # Satellite viewer
│       │   └── dashboard/page.tsx        # Analytics dashboard
│       ├── components/
│       │   ├── map/
│       │   │   ├── GoogleMapContainer.tsx # Main map + satellite toggle
│       │   │   ├── HeatmapLayer.tsx      # Congestion polylines
│       │   │   ├── IncidentMarkers.tsx
│       │   │   ├── ConstructionZones.tsx
│       │   │   ├── SentinelOverlay.tsx   # Satellite analysis overlay
│       │   │   └── RouteRenderer.tsx
│       │   ├── chat/
│       │   │   ├── ChatPanel.tsx
│       │   │   └── QuickActions.tsx
│       │   └── dashboard/
│       │       ├── PredictionWidget.tsx   # "When will it clear?"
│       │       └── CorridorChart.tsx
│       ├── hooks/
│       │   ├── useTrafficData.ts
│       │   ├── useWebSocket.ts
│       │   └── useGoogleMaps.ts
│       └── lib/
│           ├── api.ts, types.ts, colors.ts
│           └── corridors.ts              # Bangalore corridor definitions
│
├── infra/
│   ├── oracle/                            # VM setup scripts
│   ├── docker/                            # docker-compose (dev + prod)
│   └── cloudflare/                        # Deployment config
│
├── data/
│   ├── corridors.geojson                  # Bangalore road geometries
│   ├── construction_zones.json
│   └── signal_locations.json
│
└── scripts/
    ├── seed_corridors.py
    ├── download_kaggle.py
    └── test_apis.py
```

---

## Phased Implementation

### Phase 1: MVP — Live Map + TomTom Traffic (Weeks 1-3)
**Goal:** Google Maps with live traffic heatmap + satellite toggle

Build:
- FastAPI backend scaffold with Neon PostgreSQL + Upstash Redis
- TomTom Traffic client (flow + incidents), polling every 2 min for 10 corridors
- Database schema: corridors, traffic_snapshots, incidents tables
- Heatmap API returning GeoJSON with speed/congestion per segment
- Next.js frontend with Google Maps (satellite/hybrid toggle built-in)
- Colored polylines for congestion: Green > Yellow > Orange > Red > Black
- Incident markers on map
- Deploy: Backend on Oracle VM 1, Frontend on Cloudflare Pages

### Phase 2: Multi-Source Fusion + Overlays (Weeks 4-6)
**Goal:** ASTraM + OpenCity integration, data fusion, construction zones

Build:
- ASTraM incident client
- OpenCity batch downloader (CSV/KML parsing, daily)
- Data fusion engine: ASTraM for incidents, TomTom for speeds, recency + confidence scoring
- Construction zone API with polygon overlays on map
- WebSocket live updates for incidents
- In-process asyncio event bus

### Phase 3: Predictions + "When Will It Clear?" (Weeks 7-9)
**Goal:** ML-based traffic forecasting

Build:
- Kaggle Traffic Pulse data pipeline
- LightGBM short-term model (0-15 min, ONNX export, <5 MB)
- LightGBM medium-term model (15-60 min)
- Inference server on Oracle VM 2
- Prediction API + "clear time" calculator
- Prediction widget on map: "Improving by 18:45 (70% confidence)"

### Phase 4: Bot + Route Optimization (Weeks 10-12)
**Goal:** Conversational interface + vehicle-class routing

Build:
- Rule-based bot engine (intent classification + entity extraction)
- 6 intent categories mapped from PROMPTS.MD
- Google Maps Directions-based routing enhanced with live congestion
- Vehicle-class filtering (bike, car, truck, bus, auto, emergency)
- Chat UI with quick-action buttons
- Route planner page with vehicle selector

### Phase 5: Satellite Imagery + Analytics (Weeks 13-16)
**Goal:** Sentinel-2 integration, city planner dashboard

Build:
- Sentinel-2 pipeline via Copernicus CDSE API (weekly download)
- Flood detection (NDWI analysis) + construction change detection
- Satellite overlay on map (flood risk zones, construction progress)
- Analytics dashboard: corridor charts, pattern discovery, event predictor
- Mappls signal countdown integration (if partnership secured)

### Phase 6: Advanced Features (Weeks 17-20+)
**Goal:** Emergency routing, what-if modeling, citizen reporting, PWA

Build:
- Emergency response optimizer (e-Path corridors)
- What-if scenario modeling (statistical, not SUMO)
- Citizen incident reporting with image upload
- Logistics/freight optimizer
- PWA + push notifications

---

## Google Maps + Satellite Integration Details

**Satellite view** — free, built into Maps JavaScript API:
```
map.setMapTypeId('hybrid')  // satellite + labels
```

**Custom overlays on satellite:**
- Congestion polylines (colored by speed)
- Incident markers with type-specific icons
- Construction zone polygons with completion %
- Sentinel-2 flood risk zones (semi-transparent blue)

**Sentinel-2 satellite analysis:**
- Source: Copernicus Data Space Ecosystem (free)
- Flood detection: NDWI > 0.3 from Band 3 + Band 8
- Construction monitoring: consecutive image comparison
- Updated weekly, NOT real-time (clearly labeled in UI)

---

## Database Storage Strategy (Neon 0.5 GB limit)

- Raw traffic snapshots: **14-day retention**, then delete
- Hourly aggregates: **90-day retention**
- Daily aggregates: keep indefinitely (~tiny)
- Estimated steady state: **~300 MB** (60% of limit)

## Redis Strategy (Upstash 500K commands/month)

- Batch writes via MSET (1 command for N keys) every 5 min
- ~5,300 commands/day -> ~160K/month (32% of limit)

---

## Verification Strategy

1. **Unit tests**: All API clients with recorded HTTP fixtures (respx)
2. **Integration tests**: DB operations + API cycle with mocked external services
3. **E2E tests**: Playwright — map loads, satellite toggle, heatmap renders, bot responds
4. **Data quality**: Compare TomTom vs ASTraM, flag >30% divergence
5. **ML evaluation**: MAPE on held-out test set, backtest vs "same time yesterday" baseline
6. **Manual**: Compare displayed congestion against TomTom's own map viewer

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Oracle VM out-of-capacity in Mumbai | Provision immediately; backup: Hyderabad/Chennai region |
| ASTraM API access denied | Fall back to TomTom incidents + crowdsourced reports |
| Neon 0.5 GB exceeded | Aggressive retention + archive to Oracle VM disk |
| Google Maps pricing changes | Fallback: Leaflet + OpenStreetMap |
| Upstash Redis limit hit | In-memory cache (Python cachetools) as primary |

---

## Total Cost: $0/month
All services on free tiers. Google Maps $200/month credit covers all map API usage.
