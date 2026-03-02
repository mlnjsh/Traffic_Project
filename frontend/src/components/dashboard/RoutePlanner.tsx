"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { RouteNarrative } from "./RouteNarrative";
import type {
  SmartRouteResponse,
  VehicleRoutingResponse,
  RouteNarrativeResponse,
  RouteOption,
  VehicleClass,
} from "@/lib/types";

const CONGESTION_LEVEL_COLORS: Record<string, string> = {
  free_flow: "#22c55e",
  light: "#84cc16",
  moderate: "#eab308",
  heavy: "#f97316",
  severe: "#ef4444",
  gridlock: "#1f2937",
};

const VEHICLE_OPTIONS: { value: VehicleClass; label: string; icon: string }[] = [
  { value: "two_wheeler", label: "Two-Wheeler", icon: "🏍" },
  { value: "car", label: "Car", icon: "🚗" },
  { value: "truck", label: "Truck", icon: "🚛" },
  { value: "bmtc_bus", label: "BMTC Bus", icon: "🚌" },
  { value: "emergency", label: "Emergency", icon: "🚑" },
  { value: "auto_rickshaw", label: "Auto", icon: "🛺" },
];

const PRESET_ROUTES = [
  { origin: "Whitefield", destination: "Electronic City", label: "Whitefield → E-City" },
  { origin: "Koramangala", destination: "Whitefield", label: "Koramangala → Whitefield" },
  { origin: "Hebbal", destination: "Electronic City", label: "Hebbal → E-City" },
];

type Tab = "smart" | "vehicle";

export function RoutePlanner() {
  const [tab, setTab] = useState<Tab>("smart");
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [vehicleClass, setVehicleClass] = useState<VehicleClass>("car");
  const [loading, setLoading] = useState(false);
  const [smartResult, setSmartResult] = useState<SmartRouteResponse | null>(null);
  const [vehicleResult, setVehicleResult] = useState<VehicleRoutingResponse | null>(null);
  const [narrativeResult, setNarrativeResult] = useState<RouteNarrativeResponse | null>(null);
  const [narrativeLoading, setNarrativeLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNarrative = async (vc?: string) => {
    setNarrativeLoading(true);
    try {
      const result = await api.getRouteNarrative({ origin, destination, vehicle_class: vc });
      setNarrativeResult(result);
    } catch {
      setNarrativeResult(null);
    } finally {
      setNarrativeLoading(false);
    }
  };

  const handleSmartRoute = async () => {
    if (!origin || !destination) return;
    setLoading(true);
    setError(null);
    setNarrativeResult(null);
    try {
      const result = await api.getSmartRoutes({ origin, destination });
      setSmartResult(result);
      fetchNarrative();
    } catch (e: any) {
      setError(e.message || "Failed to get routes");
    } finally {
      setLoading(false);
    }
  };

  const handleVehicleRoute = async () => {
    if (!origin || !destination) return;
    setLoading(true);
    setError(null);
    setNarrativeResult(null);
    try {
      const result = await api.getVehicleRoute({ origin, destination, vehicle_class: vehicleClass });
      setVehicleResult(result);
      fetchNarrative(vehicleClass);
    } catch (e: any) {
      setError(e.message || "Failed to get route");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    if (tab === "smart") handleSmartRoute();
    else handleVehicleRoute();
  };

  const applyPreset = (preset: { origin: string; destination: string }) => {
    setOrigin(preset.origin);
    setDestination(preset.destination);
  };

  return (
    <div style={{ borderTop: "1px solid #1f2937" }}>
      {/* Header */}
      <div style={{ padding: "0.5rem 1rem", borderBottom: "1px solid #1f2937", background: "#0f172a" }}>
        <span style={{ fontSize: "0.75rem", fontWeight: 600 }}>Route Planner</span>
      </div>

      {/* Tab Selector */}
      <div style={{ display: "flex", borderBottom: "1px solid #1f2937" }}>
        <button
          onClick={() => setTab("smart")}
          style={{
            flex: 1, padding: "0.375rem", fontSize: "11px", fontWeight: 500,
            background: tab === "smart" ? "#1e3a5f" : "transparent",
            color: tab === "smart" ? "#60a5fa" : "#6b7280",
            border: "none", cursor: "pointer",
            borderBottom: tab === "smart" ? "2px solid #3b82f6" : "2px solid transparent",
          }}
        >
          Smart Routes
        </button>
        <button
          onClick={() => setTab("vehicle")}
          style={{
            flex: 1, padding: "0.375rem", fontSize: "11px", fontWeight: 500,
            background: tab === "vehicle" ? "#1e3a5f" : "transparent",
            color: tab === "vehicle" ? "#60a5fa" : "#6b7280",
            border: "none", cursor: "pointer",
            borderBottom: tab === "vehicle" ? "2px solid #3b82f6" : "2px solid transparent",
          }}
        >
          By Vehicle
        </button>
      </div>

      {/* Input Form */}
      <div style={{ padding: "0.5rem 0.75rem" }}>
        {/* Presets */}
        <div style={{ display: "flex", gap: "4px", marginBottom: "0.375rem", flexWrap: "wrap" }}>
          {PRESET_ROUTES.map((p) => (
            <button
              key={p.label}
              onClick={() => applyPreset(p)}
              style={{
                fontSize: "9px", padding: "2px 6px", borderRadius: "3px",
                background: "#1f2937", color: "#9ca3af", border: "1px solid #374151",
                cursor: "pointer",
              }}
            >
              {p.label}
            </button>
          ))}
        </div>

        <input
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          placeholder="Origin (e.g., Whitefield)"
          style={{
            width: "100%", padding: "0.375rem 0.5rem", fontSize: "11px",
            background: "#1f2937", border: "1px solid #374151", borderRadius: "4px",
            color: "#e5e7eb", marginBottom: "0.25rem", boxSizing: "border-box",
          }}
        />
        <input
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder="Destination (e.g., Electronic City)"
          style={{
            width: "100%", padding: "0.375rem 0.5rem", fontSize: "11px",
            background: "#1f2937", border: "1px solid #374151", borderRadius: "4px",
            color: "#e5e7eb", marginBottom: "0.375rem", boxSizing: "border-box",
          }}
        />

        {/* Vehicle selector (only for vehicle tab) */}
        {tab === "vehicle" && (
          <div style={{ display: "flex", gap: "3px", flexWrap: "wrap", marginBottom: "0.375rem" }}>
            {VEHICLE_OPTIONS.map((v) => (
              <button
                key={v.value}
                onClick={() => setVehicleClass(v.value)}
                style={{
                  fontSize: "10px", padding: "3px 6px", borderRadius: "4px",
                  background: vehicleClass === v.value ? "#1e3a5f" : "#1f2937",
                  color: vehicleClass === v.value ? "#60a5fa" : "#9ca3af",
                  border: vehicleClass === v.value ? "1px solid #3b82f6" : "1px solid #374151",
                  cursor: "pointer",
                }}
              >
                {v.icon} {v.label}
              </button>
            ))}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading || !origin || !destination}
          style={{
            width: "100%", padding: "0.375rem", fontSize: "11px", fontWeight: 600,
            background: loading ? "#374151" : "#2563eb",
            color: loading ? "#6b7280" : "#ffffff",
            border: "none", borderRadius: "4px", cursor: loading ? "default" : "pointer",
          }}
        >
          {loading ? "Finding routes..." : tab === "smart" ? "Get Smart Routes" : "Get Vehicle Route"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: "0.375rem 0.75rem", fontSize: "10px", color: "#fca5a5" }}>
          {error}
        </div>
      )}

      {/* Smart Routes Result */}
      {tab === "smart" && smartResult && (
        <div style={{ maxHeight: "300px", overflowY: "auto" }}>
          {smartResult.routes.map((route, i) => (
            <SmartRouteCard key={i} route={route} />
          ))}
          {smartResult.multimodal && (
            <div style={{ padding: "0.5rem 0.75rem", borderTop: "1px solid rgba(31,41,55,0.5)" }}>
              <div style={{ fontSize: "11px", fontWeight: 600, color: "#a78bfa", marginBottom: "0.25rem" }}>
                🚇 Multi-Modal Option
              </div>
              {smartResult.multimodal.legs.map((leg, i) => (
                <div key={i} style={{ fontSize: "10px", color: "#9ca3af", marginBottom: "2px" }}>
                  <span style={{ color: "#d1d5db" }}>{modeEmoji(leg.mode)}</span>{" "}
                  {leg.from_location} → {leg.to_location} ({leg.time_minutes} min
                  {leg.cost_inr ? `, ₹${leg.cost_inr}` : ""})
                </div>
              ))}
              <div style={{ fontSize: "10px", color: "#6b7280", marginTop: "4px" }}>
                Total: {smartResult.multimodal.total_time_minutes} min
                {smartResult.multimodal.total_cost_inr && ` | ₹${smartResult.multimodal.total_cost_inr}`}
              </div>
              <div style={{ fontSize: "10px", color: "#a78bfa", marginTop: "2px" }}>
                {smartResult.multimodal.comparison_vs_driving}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Vehicle Route Result */}
      {tab === "vehicle" && vehicleResult && (
        <VehicleRouteCard result={vehicleResult} />
      )}

      {/* Route Intelligence Narrative */}
      {narrativeLoading && (
        <div style={{ padding: "0.5rem 0.75rem", fontSize: "10px", color: "#6b7280", textAlign: "center" }}>
          Generating route intelligence summary...
        </div>
      )}
      {narrativeResult && !narrativeLoading && (
        <RouteNarrative narrative={narrativeResult} />
      )}
    </div>
  );
}

function SmartRouteCard({ route }: { route: RouteOption }) {
  const colorDot = CONGESTION_LEVEL_COLORS[route.congestion_level] || "#6b7280";

  return (
    <div style={{ padding: "0.5rem 0.75rem", borderTop: "1px solid rgba(31,41,55,0.5)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: colorDot }} />
          <span style={{ fontSize: "11px", fontWeight: 600, color: "#e5e7eb" }}>{route.label}</span>
        </div>
        <span style={{ fontSize: "10px", color: "#6b7280" }}>{route.confidence_pct}%</span>
      </div>
      <div style={{ fontSize: "10px", color: "#9ca3af", marginBottom: "2px" }}>{route.summary}</div>
      <div style={{ display: "flex", gap: "0.75rem", fontSize: "10px", color: "#6b7280" }}>
        <span>{route.total_distance_km} km</span>
        <span>{route.time_range_minutes}</span>
      </div>
      {route.savings_vs_default && (
        <div style={{ fontSize: "10px", color: "#34d399", marginTop: "2px" }}>
          {route.savings_vs_default}
        </div>
      )}
      {route.known_issues.length > 0 && (
        <div style={{ fontSize: "9px", color: "#fbbf24", marginTop: "2px" }}>
          {route.known_issues.join("; ")}
        </div>
      )}
    </div>
  );
}

function VehicleRouteCard({ result }: { result: VehicleRoutingResponse }) {
  const r = result.route;
  return (
    <div style={{ maxHeight: "300px", overflowY: "auto" }}>
      <div style={{ padding: "0.5rem 0.75rem", borderTop: "1px solid rgba(31,41,55,0.5)" }}>
        <div style={{ fontSize: "11px", fontWeight: 600, color: "#e5e7eb", marginBottom: "4px" }}>
          {result.vehicle_label} Route
        </div>
        <div style={{ fontSize: "10px", color: "#9ca3af", marginBottom: "4px" }}>{r.route_summary}</div>
        <div style={{ display: "flex", gap: "0.75rem", fontSize: "10px", color: "#6b7280", marginBottom: "4px" }}>
          <span>{r.total_distance_km} km</span>
          <span>{r.time_range_minutes}</span>
          {r.cost_estimate && <span>{r.cost_estimate}</span>}
        </div>

        {/* Restrictions */}
        {r.restrictions_applied.length > 0 && (
          <div style={{ marginBottom: "4px" }}>
            <div style={{ fontSize: "10px", fontWeight: 500, color: "#fbbf24", marginBottom: "2px" }}>Restrictions:</div>
            {r.restrictions_applied.map((rest, i) => (
              <div key={i} style={{ fontSize: "9px", color: "#d97706", marginBottom: "1px" }}>
                • {rest.description}
              </div>
            ))}
          </div>
        )}

        {/* Bus Connections */}
        {r.bus_connections.length > 0 && (
          <div style={{ marginBottom: "4px" }}>
            <div style={{ fontSize: "10px", fontWeight: 500, color: "#60a5fa", marginBottom: "2px" }}>Bus Connections:</div>
            {r.bus_connections.map((bus, i) => (
              <div key={i} style={{ fontSize: "9px", color: "#93c5fd", marginBottom: "2px" }}>
                🚌 {bus.route_number}: {bus.from_stop} → {bus.to_stop} (every {bus.frequency_minutes} min, {bus.walking_distance_m}m walk)
                {bus.metro_connection && <div style={{ color: "#a78bfa" }}>🚇 {bus.metro_connection}</div>}
              </div>
            ))}
          </div>
        )}

        {/* Parking */}
        {r.parking && (
          <div style={{ fontSize: "9px", color: "#6b7280", marginBottom: "4px" }}>
            🅿 {r.parking.name} ({r.parking.distance_from_dest_m}m, {r.parking.availability})
            {r.parking.estimated_cost_inr && ` ₹${r.parking.estimated_cost_inr}`}
          </div>
        )}

        {/* Safety */}
        {r.safety_notes.length > 0 && (
          <div style={{ marginBottom: "4px" }}>
            <div style={{ fontSize: "10px", fontWeight: 500, color: "#f87171", marginBottom: "2px" }}>Safety:</div>
            {r.safety_notes.map((note, i) => (
              <div key={i} style={{ fontSize: "9px", color: "#fca5a5" }}>⚠ {note}</div>
            ))}
          </div>
        )}

        {/* Special Notes */}
        {r.special_notes.length > 0 && (
          <div>
            {r.special_notes.map((note, i) => (
              <div key={i} style={{ fontSize: "9px", color: "#9ca3af", marginBottom: "1px" }}>• {note}</div>
            ))}
          </div>
        )}

        {/* Alternative suggestion */}
        {result.alternative_mode_suggestion && (
          <div style={{ fontSize: "10px", color: "#34d399", marginTop: "4px", fontStyle: "italic" }}>
            💡 {result.alternative_mode_suggestion}
          </div>
        )}
      </div>
    </div>
  );
}

function modeEmoji(mode: string): string {
  const map: Record<string, string> = {
    walk: "🚶",
    metro: "🚇",
    bus: "🚌",
    auto: "🛺",
    drive: "🚗",
  };
  return map[mode] || "🚶";
}
