"use client";

import { CONGESTION_COLORS, COLOR_LABELS, TREND_ICONS } from "@/lib/colors";
import type { CorridorStatus, CongestionColor } from "@/lib/types";

interface Props {
  corridors: CorridorStatus[];
  selectedCorridor: string | null;
  onSelectCorridor: (id: string | null) => void;
  timestamp: string | null;
  demoMode: boolean;
}

export function CorridorSidebar({
  corridors,
  selectedCorridor,
  onSelectCorridor,
  timestamp,
  demoMode,
}: Props) {
  return (
    <aside
      style={{
        display: "flex",
        flex: 1,
        minHeight: 0,
        flexDirection: "column",
        background: "#111827",
      }}
    >
      {/* Header */}
      <div style={{ borderBottom: "1px solid #1f2937", padding: "0.75rem 1rem" }}>
        <h1 style={{ fontSize: "1.125rem", fontWeight: 700 }}>Bangalore Traffic</h1>
        <p style={{ fontSize: "0.75rem", color: "#9ca3af" }}>
          {corridors.length} corridors monitored
          {demoMode && (
            <span
              style={{
                marginLeft: "0.5rem",
                borderRadius: "0.25rem",
                background: "rgba(113,63,18,0.5)",
                padding: "0.125rem 0.375rem",
                color: "#facc15",
                fontSize: "0.7rem",
              }}
            >
              DEMO
            </span>
          )}
        </p>
        {timestamp && (
          <p suppressHydrationWarning style={{ marginTop: "0.25rem", fontSize: "10px", color: "#6b7280" }}>
            Updated: {new Date(timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          borderBottom: "1px solid #1f2937",
          padding: "0.5rem 1rem",
        }}
      >
        {(Object.keys(CONGESTION_COLORS) as CongestionColor[]).map((color) => (
          <span
            key={color}
            style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "10px", color: "#d1d5db" }}
          >
            <span
              style={{
                display: "inline-block",
                height: "0.625rem",
                width: "0.625rem",
                borderRadius: "9999px",
                background: CONGESTION_COLORS[color],
              }}
            />
            {COLOR_LABELS[color].split(" (")[0]}
          </span>
        ))}
      </div>

      {/* Corridor list */}
      <div className="sidebar-scroll" style={{ flex: 1, overflowY: "auto" }}>
        {corridors
          .sort((a, b) => b.congestion_pct - a.congestion_pct)
          .map((c) => {
            const isSelected = selectedCorridor === c.corridor_id;
            return (
              <button
                key={c.corridor_id}
                onClick={() => onSelectCorridor(isSelected ? null : c.corridor_id)}
                style={{
                  width: "100%",
                  borderBottom: "1px solid rgba(31,41,55,0.5)",
                  padding: "0.75rem 1rem",
                  textAlign: "left",
                  transition: "background 150ms",
                  background: isSelected ? "#1f2937" : "transparent",
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = "rgba(31,41,55,0.5)";
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = "transparent";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "0.875rem", fontWeight: 500 }}>{c.name}</span>
                  <span
                    style={{
                      height: "0.75rem",
                      width: "0.75rem",
                      borderRadius: "9999px",
                      background: CONGESTION_COLORS[c.color],
                    }}
                  />
                </div>
                <div style={{ marginTop: "0.25rem", display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.75rem", color: "#9ca3af" }}>
                  <span>{c.current_speed_kmh.toFixed(0)} km/h</span>
                  <span>{c.congestion_pct.toFixed(0)}% congestion</span>
                  <span>{TREND_ICONS[c.trend] || "→"} {c.trend}</span>
                </div>
                {c.incident_count > 0 && (
                  <p style={{ marginTop: "0.25rem", fontSize: "11px", color: "#f87171" }}>
                    {c.incident_count} active incident{c.incident_count > 1 ? "s" : ""}
                    {c.delay_minutes > 0 && ` · +${c.delay_minutes.toFixed(0)} min`}
                  </p>
                )}
              </button>
            );
          })}
      </div>
    </aside>
  );
}
