"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { PredictionResponse } from "@/lib/types";
import { CONGESTION_COLORS } from "@/lib/colors";
import type { CongestionColor } from "@/lib/types";

interface Props {
  corridorId: string | null;
}

export function PredictionWidget({ corridorId }: Props) {
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!corridorId) {
      setPrediction(null);
      return;
    }
    setLoading(true);
    api
      .getPrediction(corridorId)
      .then(setPrediction)
      .catch(() => setPrediction(null))
      .finally(() => setLoading(false));
  }, [corridorId]);

  if (!corridorId) {
    return (
      <div style={{ padding: "0.75rem 1rem", fontSize: "0.75rem", color: "#6b7280" }}>
        Select a corridor to see predictions
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: "0.75rem 1rem", fontSize: "0.75rem", color: "#9ca3af" }}>
        Loading prediction...
      </div>
    );
  }

  if (!prediction) return null;

  const st = prediction.short_term;
  const mt = prediction.medium_term;
  const ct = prediction.construction;

  const directionEmoji: Record<string, string> = {
    improving: "↗",
    stable: "→",
    worsening: "↘",
  };

  return (
    <div style={{ borderTop: "1px solid #1f2937" }}>
      {/* Header */}
      <div style={{ padding: "0.5rem 1rem", borderBottom: "1px solid #1f2937", background: "#0f172a" }}>
        <span style={{ fontSize: "0.75rem", fontWeight: 600 }}>When will it clear?</span>
      </div>

      {/* Short-term */}
      <div style={{ padding: "0.5rem 1rem", borderBottom: "1px solid rgba(31,41,55,0.5)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
          <span style={{ fontSize: "1rem" }}>{directionEmoji[st.direction] || "→"}</span>
          <span style={{ fontSize: "0.75rem", fontWeight: 500, textTransform: "capitalize" }}>
            {st.direction}
          </span>
          <span style={{ fontSize: "10px", color: "#6b7280", marginLeft: "auto" }}>
            {st.confidence_pct}% confidence
          </span>
        </div>
        <p style={{ fontSize: "11px", color: "#9ca3af", lineHeight: 1.4 }}>{st.narrative}</p>
        <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.25rem", fontSize: "10px", color: "#6b7280" }}>
          <span>5m: {st.predicted_speed_5min} km/h</span>
          <span>10m: {st.predicted_speed_10min} km/h</span>
          <span>15m: {st.predicted_speed_15min} km/h</span>
        </div>
      </div>

      {/* Medium-term */}
      <div style={{ padding: "0.5rem 1rem", borderBottom: "1px solid rgba(31,41,55,0.5)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: 500 }}>Clears by ~{mt.estimated_clear_time}</span>
          <span style={{ fontSize: "10px", color: "#6b7280" }}>{mt.confidence_pct}% confidence</span>
        </div>
        <p style={{ fontSize: "11px", color: "#9ca3af", lineHeight: 1.4 }}>{mt.narrative}</p>
        {/* Mini prediction bar */}
        <div style={{ display: "flex", gap: "2px", marginTop: "0.375rem" }}>
          {mt.predictions.map((p) => (
            <div
              key={p.time_from_now_minutes}
              style={{
                flex: 1,
                height: "6px",
                borderRadius: "2px",
                background: CONGESTION_COLORS[p.predicted_color as CongestionColor] || "#6b7280",
              }}
              title={`+${p.time_from_now_minutes}m: ${p.predicted_speed_kmh} km/h`}
            />
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "9px", color: "#4b5563", marginTop: "2px" }}>
          <span>+15m</span>
          <span>+30m</span>
          <span>+45m</span>
          <span>+60m</span>
        </div>
      </div>

      {/* Construction (if applicable) */}
      {ct && (
        <div style={{ padding: "0.5rem 1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
            <span style={{ fontSize: "0.75rem", fontWeight: 500 }}>
              🚧 {ct.project_name}
            </span>
            <span style={{ fontSize: "10px", color: "#6b7280" }}>{ct.confidence_pct}%</span>
          </div>
          <p style={{ fontSize: "11px", color: "#9ca3af", lineHeight: 1.4 }}>{ct.narrative}</p>
        </div>
      )}
    </div>
  );
}
