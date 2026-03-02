"use client";

import { useMap, useMapsLibrary } from "@vis.gl/react-google-maps";
import { useEffect, useRef } from "react";
import type { ConstructionZone } from "@/lib/types";

interface Props {
  zones: ConstructionZone[];
}

/**
 * Renders construction zone polylines (start→end) with an info popup
 * showing project name, completion %, and lane restriction.
 */
export function ConstructionZones({ zones }: Props) {
  const map = useMap();
  const mapsLib = useMapsLibrary("maps");
  const markerLib = useMapsLibrary("marker");
  const overlaysRef = useRef<(google.maps.Polyline | google.maps.marker.AdvancedMarkerElement)[]>([]);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  useEffect(() => {
    if (!map || !mapsLib || !markerLib) return;

    // Clear previous overlays
    overlaysRef.current.forEach((o) => {
      if (o instanceof google.maps.Polyline) o.setMap(null);
      else o.map = null;
    });
    overlaysRef.current = [];

    if (!infoWindowRef.current) {
      infoWindowRef.current = new google.maps.InfoWindow();
    }

    zones.forEach((zone) => {
      // Dashed orange line from start to end
      const polyline = new google.maps.Polyline({
        path: [
          { lat: zone.start_coordinates.lat, lng: zone.start_coordinates.lng },
          { lat: zone.end_coordinates.lat, lng: zone.end_coordinates.lng },
        ],
        strokeColor: "#f97316",
        strokeOpacity: 0,
        strokeWeight: 5,
        icons: [
          {
            icon: { path: "M 0,-1 0,1", strokeOpacity: 0.8, scale: 3 },
            offset: "0",
            repeat: "14px",
          },
        ],
        map,
        zIndex: 5,
      });

      // Marker at midpoint
      const midLat = (zone.start_coordinates.lat + zone.end_coordinates.lat) / 2;
      const midLng = (zone.start_coordinates.lng + zone.end_coordinates.lng) / 2;

      const el = document.createElement("div");
      el.style.cssText = `
        background: #f97316; color: white; padding: 2px 6px;
        border-radius: 4px; font-size: 11px; font-weight: 600;
        cursor: pointer; white-space: nowrap;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      `;
      el.textContent = `🚧 ${zone.completion_pct}%`;

      const marker = new markerLib.AdvancedMarkerElement({
        map,
        position: { lat: midLat, lng: midLng },
        content: el,
      });

      const completionBar = Math.round(zone.completion_pct);
      const confidenceBar = Math.round(zone.completion_confidence_pct);

      // Build milestones HTML
      const milestonesHtml = zone.milestones?.length
        ? `<div style="margin:6px 0 0;font-size:11px">
            <strong>Milestones:</strong>
            ${zone.milestones.map((m) => `<div style="margin:2px 0;color:#444">• ${m.name}: <em>${m.status}</em></div>`).join("")}
          </div>`
        : "";

      // Build diversions HTML
      const diversionsHtml = zone.diversions?.length
        ? `<div style="margin:6px 0 0;font-size:11px">
            <strong>Diversions:</strong>
            ${zone.diversions.map((d) => `<div style="margin:2px 0;color:#444">• ${d.direction}: ${d.primary_alternative} (${d.time_penalty_freeflow})</div>`).join("")}
          </div>`
        : "";

      // Peak amplification
      const peakHtml = zone.peak_amplification
        ? `<p style="margin:4px 0 0;font-size:11px;color:#b45309">
            ⚡ Peak extended by ${zone.peak_amplification.extension_hours}h: ${zone.peak_amplification.amplified_window}
          </p>`
        : "";

      marker.addListener("click", () => {
        infoWindowRef.current?.setContent(`
          <div style="color:#111;max-width:320px;font-family:system-ui,sans-serif">
            <strong>🚧 ${zone.project_name}</strong>
            <p style="margin:4px 0;font-size:12px;color:#555">${zone.agency} · ${zone.lane_restriction}</p>
            <p style="margin:2px 0;font-size:11px;color:#666">${zone.traffic_management}</p>
            <div style="background:#e5e7eb;border-radius:4px;height:8px;margin:6px 0">
              <div style="background:#f97316;height:8px;border-radius:4px;width:${completionBar}%"></div>
            </div>
            <p style="margin:2px 0 0;font-size:12px">
              ${completionBar}% complete · ${confidenceBar}% confidence (±${zone.uncertainty_days} days)
            </p>
            <p style="margin:2px 0;font-size:12px">${zone.location_description}</p>
            <p style="margin:2px 0;font-size:11px;color:#777">
              ${zone.start_date} — ${zone.end_date}
              ${zone.additional_delay_minutes ? ` · +${zone.additional_delay_minutes} min delay` : ""}
            </p>
            ${peakHtml}
            ${milestonesHtml}
            ${diversionsHtml}
            <p style="margin:6px 0 0;font-size:10px;color:#999">
              Post-completion: ~${zone.normalization_weeks} weeks to normalize · Source: ${zone.source}
            </p>
          </div>
        `);
        infoWindowRef.current?.open(map, marker);
      });

      overlaysRef.current.push(polyline, marker);
    });

    return () => {
      overlaysRef.current.forEach((o) => {
        if (o instanceof google.maps.Polyline) o.setMap(null);
        else o.map = null;
      });
      overlaysRef.current = [];
    };
  }, [map, mapsLib, markerLib, zones]);

  return null;
}
