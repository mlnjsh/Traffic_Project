"use client";

import { useState, useEffect } from "react";
import { GoogleMapContainer } from "@/components/map/GoogleMapContainer";
import { CorridorSidebar } from "@/components/map/CorridorSidebar";
import { PredictionWidget } from "@/components/dashboard/PredictionWidget";
import { RoutePlanner } from "@/components/dashboard/RoutePlanner";
import { useCorridors, useIncidents, useConstructionZones } from "@/hooks/useTrafficData";

export default function Home() {
  const [selectedCorridor, setSelectedCorridor] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data: corridorData, error: corridorError } = useCorridors();
  const { data: incidentData } = useIncidents();
  const { data: constructionData } = useConstructionZones();

  const corridors = corridorData?.corridors ?? [];
  const incidents = incidentData?.incidents ?? [];
  const constructionZones = constructionData?.zones ?? [];

  /* Show a loading skeleton during SSR / before hydration to avoid mismatch */
  if (!mounted) {
    return (
      <div style={{ display: "flex", height: "100vh" }}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "20rem",
            flexShrink: 0,
            borderRight: "1px solid #1f2937",
            background: "#111827",
          }}
        >
          <p style={{ color: "#6b7280", fontSize: "0.875rem" }}>Loading corridors...</p>
        </div>
        <main style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", background: "#030712" }}>
          <p style={{ color: "#6b7280", fontSize: "0.875rem" }}>Loading map...</p>
        </main>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ display: "flex", flexDirection: "column", width: "20rem", flexShrink: 0, borderRight: "1px solid #1f2937", background: "#111827" }}>
        <CorridorSidebar
          corridors={corridors}
          selectedCorridor={selectedCorridor}
          onSelectCorridor={setSelectedCorridor}
          timestamp={corridorData?.timestamp ?? null}
          demoMode={corridorData?.demo_mode ?? false}
        />
        <PredictionWidget corridorId={selectedCorridor} />
        <RoutePlanner />
      </div>

      <main style={{ position: "relative", flex: 1 }}>
        {corridorError && (
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              zIndex: 20,
              background: "rgba(127,29,29,0.9)",
              padding: "0.5rem 1rem",
              textAlign: "center",
              fontSize: "0.875rem",
              color: "#fecaca",
            }}
          >
            Failed to load traffic data. Is the backend running?
          </div>
        )}
        <GoogleMapContainer
          corridors={corridors}
          incidents={incidents}
          constructionZones={constructionZones}
          selectedCorridor={selectedCorridor}
          onSelectCorridor={setSelectedCorridor}
        />
      </main>
    </div>
  );
}
