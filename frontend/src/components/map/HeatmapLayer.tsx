"use client";

import { useMap, useMapsLibrary } from "@vis.gl/react-google-maps";
import { useEffect, useRef } from "react";
import { CONGESTION_COLORS } from "@/lib/colors";
import type { CorridorStatus, CorridorSegment } from "@/lib/types";

interface Props {
  corridors: CorridorStatus[];
  selectedCorridor: string | null;
  onSelectCorridor: (id: string | null) => void;
}

/**
 * Renders colored polylines for each corridor segment.
 * Color scale per CLAUDE.md: Green (>30) → Yellow → Orange → Red → Black (<5 km/h).
 */
export function HeatmapLayer({ corridors, selectedCorridor, onSelectCorridor }: Props) {
  const map = useMap();
  const mapsLib = useMapsLibrary("maps");
  const polylinesRef = useRef<google.maps.Polyline[]>([]);

  useEffect(() => {
    if (!map || !mapsLib) return;

    // Clear previous polylines
    polylinesRef.current.forEach((p) => p.setMap(null));
    polylinesRef.current = [];

    corridors.forEach((corridor) => {
      const isSelected = selectedCorridor === corridor.corridor_id;
      const isFaded = selectedCorridor !== null && !isSelected;

      corridor.segments.forEach((seg: CorridorSegment) => {
        const polyline = new google.maps.Polyline({
          path: [
            { lat: seg.start.lat, lng: seg.start.lng },
            { lat: seg.end.lat, lng: seg.end.lng },
          ],
          strokeColor: CONGESTION_COLORS[seg.color],
          strokeOpacity: isFaded ? 0.3 : 0.85,
          strokeWeight: isSelected ? 7 : 5,
          map,
          zIndex: isSelected ? 10 : 1,
        });

        polyline.addListener("click", () => {
          onSelectCorridor(
            selectedCorridor === corridor.corridor_id ? null : corridor.corridor_id,
          );
        });

        polylinesRef.current.push(polyline);
      });
    });

    return () => {
      polylinesRef.current.forEach((p) => p.setMap(null));
      polylinesRef.current = [];
    };
  }, [map, mapsLib, corridors, selectedCorridor, onSelectCorridor]);

  return null;
}
