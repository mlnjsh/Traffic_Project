"use client";

import { useMap, useMapsLibrary } from "@vis.gl/react-google-maps";
import { useEffect, useRef } from "react";
import { SEVERITY_COLORS } from "@/lib/colors";
import type { IncidentReport } from "@/lib/types";

interface Props {
  incidents: IncidentReport[];
}

const TYPE_EMOJI: Record<string, string> = {
  accident: "💥",
  jam: "🚗",
  construction: "🚧",
  weather: "🌧",
  flooding: "🌊",
  breakdown: "🔧",
  debris: "⚠️",
};

/**
 * Renders incident markers on the map with severity-based styling.
 * Each marker shows a popup with incident details on click.
 */
export function IncidentMarkers({ incidents }: Props) {
  const map = useMap();
  const mapsLib = useMapsLibrary("maps");
  const markerLib = useMapsLibrary("marker");
  const markersRef = useRef<google.maps.marker.AdvancedMarkerElement[]>([]);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  useEffect(() => {
    if (!map || !mapsLib || !markerLib) return;

    // Clear previous markers
    markersRef.current.forEach((m) => (m.map = null));
    markersRef.current = [];

    if (!infoWindowRef.current) {
      infoWindowRef.current = new google.maps.InfoWindow();
    }

    incidents.forEach((incident) => {
      const emoji = TYPE_EMOJI[incident.type] || "⚠️";
      const color = SEVERITY_COLORS[incident.severity] || "#ef4444";

      // Create a custom marker element
      const el = document.createElement("div");
      el.className = "incident-marker";
      el.style.cssText = `
        width: 28px; height: 28px;
        border-radius: 50%;
        background: ${color};
        border: 2px solid white;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
      `;
      el.textContent = emoji;

      const marker = new markerLib.AdvancedMarkerElement({
        map,
        position: { lat: incident.location.lat, lng: incident.location.lng },
        content: el,
        title: `${incident.type_label} — Severity ${incident.severity}/5`,
      });

      marker.addListener("click", () => {
        infoWindowRef.current?.setContent(`
          <div style="color:#111;max-width:260px;font-family:system-ui,sans-serif">
            <strong>${incident.type_label}</strong>
            <span style="background:${color};color:white;padding:1px 6px;border-radius:4px;margin-left:6px;font-size:12px">
              ${incident.severity}/5
            </span>
            <p style="margin:6px 0 4px;font-size:13px">${incident.location.road_name}</p>
            <p style="margin:0;font-size:12px;color:#555">
              ${incident.affected_length_km.toFixed(1)} km affected · +${incident.delay_minutes} min delay
            </p>
            ${incident.description ? `<p style="margin:6px 0 0;font-size:12px;color:#333">${incident.description}</p>` : ""}
          </div>
        `);
        infoWindowRef.current?.open(map, marker);
      });

      markersRef.current.push(marker);
    });

    return () => {
      markersRef.current.forEach((m) => (m.map = null));
      markersRef.current = [];
    };
  }, [map, mapsLib, markerLib, incidents]);

  return null;
}
