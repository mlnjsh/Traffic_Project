"use client";

import { useEffect, useState } from "react";
import { AdvancedMarker, InfoWindow } from "@vis.gl/react-google-maps";
import type { SignalStatus } from "@/lib/types";

const PHASE_COLORS: Record<string, string> = {
  green: "#22c55e",
  red: "#ef4444",
  amber: "#eab308",
};

interface Props {
  signals: SignalStatus[];
}

export function SignalMarkers({ signals }: Props) {
  const [selected, setSelected] = useState<SignalStatus | null>(null);

  return (
    <>
      {signals.map((signal) => (
        <AdvancedMarker
          key={signal.junction_id}
          position={{ lat: signal.lat, lng: signal.lng }}
          onClick={() => setSelected(signal)}
        >
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: "50%",
              background: PHASE_COLORS[signal.current_phase] || "#6b7280",
              border: "2px solid rgba(255,255,255,0.8)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "9px",
              fontWeight: 700,
              color: "#fff",
              cursor: "pointer",
              boxShadow: "0 1px 3px rgba(0,0,0,0.4)",
            }}
          >
            {signal.countdown_seconds}
          </div>
        </AdvancedMarker>
      ))}

      {selected && (
        <InfoWindow
          position={{ lat: selected.lat, lng: selected.lng }}
          onCloseClick={() => setSelected(null)}
        >
          <div style={{ padding: "4px", maxWidth: 200, fontSize: "11px", color: "#1f2937" }}>
            <div style={{ fontWeight: 700, marginBottom: "4px" }}>
              🚦 {selected.junction_name}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  background: PHASE_COLORS[selected.current_phase],
                }}
              />
              <span style={{ fontWeight: 600, textTransform: "uppercase" }}>
                {selected.current_phase}
              </span>
              <span style={{ marginLeft: "auto", fontWeight: 700 }}>
                {selected.countdown_seconds}s
              </span>
            </div>
            <div style={{ fontSize: "10px", color: "#4b5563" }}>
              <div>Cycle: {selected.cycle_time_seconds}s (Green: {selected.green_time_seconds}s / Red: {selected.red_time_seconds}s)</div>
              {selected.pedestrian_phase && <div>🚶 Pedestrian phase active</div>}
              <div style={{ marginTop: "2px", color: "#6b7280" }}>Source: {selected.data_source}</div>
            </div>
          </div>
        </InfoWindow>
      )}
    </>
  );
}
