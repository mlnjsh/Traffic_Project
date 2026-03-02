"use client";

import { useState, useCallback, useEffect } from "react";
import { APIProvider, Map } from "@vis.gl/react-google-maps";
import { HeatmapLayer } from "./HeatmapLayer";
import { IncidentMarkers } from "./IncidentMarkers";
import { ConstructionZones } from "./ConstructionZones";
import { SignalMarkers } from "./SignalMarkers";
import { api } from "@/lib/api";
import type { CorridorStatus, IncidentReport, ConstructionZone, SignalStatus, TrafficCardResponse } from "@/lib/types";
import { CONGESTION_COLORS } from "@/lib/colors";
import type { CongestionColor } from "@/lib/types";

const BANGALORE_CENTER = { lat: 12.9716, lng: 77.5946 };
const DEFAULT_ZOOM = 12;

type MapTypeId = "roadmap" | "satellite" | "hybrid";

interface Layers {
  heatmap: boolean;
  incidents: boolean;
  construction: boolean;
  signals: boolean;
}

interface Props {
  corridors: CorridorStatus[];
  incidents: IncidentReport[];
  constructionZones: ConstructionZone[];
  selectedCorridor: string | null;
  onSelectCorridor: (id: string | null) => void;
}

export function GoogleMapContainer({
  corridors,
  incidents,
  constructionZones,
  selectedCorridor,
  onSelectCorridor,
}: Props) {
  const [mapType, setMapType] = useState<MapTypeId>("roadmap");
  const [layers, setLayers] = useState<Layers>({
    heatmap: true,
    incidents: true,
    construction: true,
    signals: false,
  });
  const [signals, setSignals] = useState<SignalStatus[]>([]);
  const [trafficCard, setTrafficCard] = useState<TrafficCardResponse | null>(null);
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY || "";

  // Fetch signals when layer is enabled
  useEffect(() => {
    if (!layers.signals) {
      setSignals([]);
      return;
    }
    api.getSignals().then((res) => setSignals(res.signals)).catch(() => setSignals([]));
    const interval = setInterval(() => {
      api.getSignals().then((res) => setSignals(res.signals)).catch(() => {});
    }, 30000);
    return () => clearInterval(interval);
  }, [layers.signals]);

  // Fetch traffic card when corridor is selected
  useEffect(() => {
    if (!selectedCorridor) {
      setTrafficCard(null);
      return;
    }
    api.getTrafficCard(selectedCorridor).then(setTrafficCard).catch(() => setTrafficCard(null));
  }, [selectedCorridor]);

  const cycleMapType = useCallback(() => {
    setMapType((prev) => {
      if (prev === "roadmap") return "satellite";
      if (prev === "satellite") return "hybrid";
      return "roadmap";
    });
  }, []);

  const toggleLayer = (layer: keyof Layers) => {
    setLayers((prev) => ({ ...prev, [layer]: !prev[layer] }));
  };

  const mapTypeLabel: Record<MapTypeId, string> = {
    roadmap: "Map",
    satellite: "Satellite",
    hybrid: "Hybrid",
  };

  const trendEmoji: Record<string, string> = {
    improving: "↗",
    stable: "→",
    worsening: "↘",
  };

  return (
    <APIProvider apiKey={apiKey}>
      <div style={{ position: "relative", height: "100%", width: "100%" }}>
        <Map
          defaultCenter={BANGALORE_CENTER}
          defaultZoom={DEFAULT_ZOOM}
          mapTypeId={mapType}
          gestureHandling="greedy"
          disableDefaultUI={false}
          mapId="traffic-map"
          style={{ width: "100%", height: "100%" }}
        >
          {layers.heatmap && (
            <HeatmapLayer
              corridors={corridors}
              selectedCorridor={selectedCorridor}
              onSelectCorridor={onSelectCorridor}
            />
          )}
          {layers.incidents && <IncidentMarkers incidents={incidents} />}
          {layers.construction && <ConstructionZones zones={constructionZones} />}
          {layers.signals && <SignalMarkers signals={signals} />}
        </Map>

        {/* Map type toggle */}
        <button
          onClick={cycleMapType}
          style={{
            position: "absolute",
            top: "0.75rem",
            right: "3.5rem",
            zIndex: 10,
            borderRadius: "0.25rem",
            background: "rgba(17,24,39,0.8)",
            padding: "0.375rem 0.75rem",
            fontSize: "0.75rem",
            fontWeight: 500,
            color: "white",
            boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
            border: "none",
            cursor: "pointer",
          }}
        >
          {mapTypeLabel[mapType]}
        </button>

        {/* Layer Toggle Panel (Prompt 4.1 — toggleable overlay layers) */}
        <div
          style={{
            position: "absolute",
            top: "3rem",
            right: "0.75rem",
            zIndex: 10,
            background: "rgba(17,24,39,0.9)",
            borderRadius: "0.375rem",
            padding: "0.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "4px",
            boxShadow: "0 2px 6px rgba(0,0,0,0.3)",
          }}
        >
          <div style={{ fontSize: "9px", color: "#6b7280", fontWeight: 600, marginBottom: "2px" }}>
            LAYERS
          </div>
          {([
            { key: "heatmap" as const, icon: "🔥", label: "Heatmap" },
            { key: "incidents" as const, icon: "⚠", label: "Incidents" },
            { key: "construction" as const, icon: "🚧", label: "Construction" },
            { key: "signals" as const, icon: "🚦", label: "Signals" },
          ]).map(({ key, icon, label }) => (
            <button
              key={key}
              onClick={() => toggleLayer(key)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "3px 8px",
                borderRadius: "3px",
                background: layers[key] ? "rgba(59,130,246,0.2)" : "transparent",
                border: layers[key] ? "1px solid rgba(59,130,246,0.4)" : "1px solid transparent",
                color: layers[key] ? "#93c5fd" : "#6b7280",
                fontSize: "10px",
                cursor: "pointer",
                width: "100%",
                textAlign: "left",
              }}
            >
              <span>{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Traffic Card Popup (Prompt 4.2 — tap segment for detailed traffic card) */}
        {trafficCard && selectedCorridor && (
          <div
            style={{
              position: "absolute",
              bottom: "1rem",
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 10,
              background: "rgba(17,24,39,0.95)",
              borderRadius: "0.5rem",
              padding: "0.75rem 1rem",
              minWidth: "320px",
              maxWidth: "420px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
              border: `2px solid ${CONGESTION_COLORS[trafficCard.color as CongestionColor] || "#374151"}`,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.375rem" }}>
              <div>
                <div style={{ fontSize: "13px", fontWeight: 700, color: "#e5e7eb" }}>
                  {trafficCard.segment_road}
                </div>
                <div style={{ fontSize: "10px", color: "#6b7280" }}>
                  {trafficCard.corridor_name}
                </div>
              </div>
              <button
                onClick={() => { onSelectCorridor(null); setTrafficCard(null); }}
                style={{
                  background: "none", border: "none", color: "#6b7280",
                  cursor: "pointer", fontSize: "14px", padding: "0 4px",
                }}
              >
                ✕
              </button>
            </div>

            {/* Speed + Congestion Row */}
            <div style={{ display: "flex", gap: "1rem", marginBottom: "0.375rem" }}>
              <div style={{ textAlign: "center" }}>
                <div style={{
                  fontSize: "20px", fontWeight: 700,
                  color: CONGESTION_COLORS[trafficCard.color as CongestionColor] || "#e5e7eb",
                }}>
                  {trafficCard.current_speed_kmh}
                </div>
                <div style={{ fontSize: "9px", color: "#6b7280" }}>km/h</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "20px", fontWeight: 700, color: "#f97316" }}>
                  {trafficCard.congestion_pct.toFixed(0)}%
                </div>
                <div style={{ fontSize: "9px", color: "#6b7280" }}>congestion</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "20px", fontWeight: 700, color: "#ef4444" }}>
                  +{trafficCard.delay_minutes.toFixed(0)}
                </div>
                <div style={{ fontSize: "9px", color: "#6b7280" }}>min delay</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "20px" }}>
                  {trendEmoji[trafficCard.trend] || "→"}
                </div>
                <div style={{ fontSize: "9px", color: "#6b7280" }}>{trafficCard.trend}</div>
              </div>
            </div>

            {/* "When will this clear?" (Prompt 4.2) */}
            <div style={{
              padding: "0.375rem 0.5rem",
              background: "rgba(59,130,246,0.1)",
              borderRadius: "4px",
              marginBottom: "0.25rem",
            }}>
              <div style={{ fontSize: "10px", fontWeight: 600, color: "#60a5fa", marginBottom: "2px" }}>
                When will this clear?
              </div>
              <div style={{ fontSize: "11px", color: "#d1d5db" }}>
                {trafficCard.prediction_summary}
              </div>
            </div>

            {/* Metadata */}
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "9px", color: "#4b5563" }}>
              <span>
                {trafficCard.active_incidents > 0 && `⚠ ${trafficCard.active_incidents} incident(s) `}
                {trafficCard.construction_nearby && "🚧 Construction nearby"}
              </span>
              <span>{trafficCard.data_freshness}</span>
            </div>
          </div>
        )}
      </div>
    </APIProvider>
  );
}
