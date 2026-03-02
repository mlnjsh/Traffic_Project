/** Backend API client. */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchAPI<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

async function postAPI<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  // Category 1
  getCorridors: () => fetchAPI<import("./types").CorridorListResponse>("/traffic/corridors"),
  getCorridor: (id: string) => fetchAPI<import("./types").CorridorStatus>(`/traffic/corridor/${id}`),
  getHeatmap: () => fetchAPI<any>("/heatmap/data"),
  getIncidents: (corridor?: string) => {
    const params = corridor ? `?corridor=${encodeURIComponent(corridor)}` : "";
    return fetchAPI<import("./types").IncidentListResponse>(`/incidents${params}`);
  },
  getIncident: (id: string) => fetchAPI<import("./types").IncidentReport>(`/incidents/${id}`),
  getConstructionZones: () => fetchAPI<import("./types").ConstructionListResponse>("/construction/zones"),
  getConstructionZone: (id: string) => fetchAPI<import("./types").ConstructionZone>(`/construction/zones/${id}`),

  // Category 2
  getPrediction: (corridorId: string) =>
    fetchAPI<import("./types").PredictionResponse>(`/predictions/${corridorId}`),
  optimizeDeparture: (body: { origin: string; destination: string; desired_arrival: string; day_of_week?: string }) =>
    postAPI<import("./types").DepartureOptimizerResponse>("/departure/optimize", body),
  predictEventImpact: (body: { event_name: string; event_type: string; venue: string; expected_attendance: number; event_date: string; event_time: string }) =>
    postAPI<import("./types").EventImpactResponse>("/events/impact", body),

  // Category 3
  getSmartRoutes: (body: { origin: string; destination: string }) =>
    postAPI<import("./types").SmartRouteResponse>("/routes/smart", body),
  getVehicleRoute: (body: { origin: string; destination: string; vehicle_class: string }) =>
    postAPI<import("./types").VehicleRoutingResponse>("/routes/vehicle", body),
  getRouteNarrative: (body: { origin: string; destination: string; vehicle_class?: string }) =>
    postAPI<import("./types").RouteNarrativeResponse>("/routes/narrative", body),

  // Category 4
  getHeatmapConfig: () => fetchAPI<import("./types").EnhancedHeatmapResponse>("/visualization/config"),
  getSignals: () => fetchAPI<import("./types").SignalListResponse>("/visualization/signals"),
  getTrafficCard: (corridorId: string) =>
    fetchAPI<import("./types").TrafficCardResponse>(`/visualization/traffic-card/${corridorId}`),

  // Category 5
  getCommuterForecast: (body: { origin: string; destination: string }) =>
    postAPI<import("./types").CommuterForecast>("/commuter/forecast", body),
  optimizeLogistics: (body: { origin: string; stops: string[] }) =>
    postAPI<import("./types").LogisticsResponse>("/logistics/optimize", body),
  getPlannerDashboard: () =>
    fetchAPI<import("./types").PlannerDashboardResponse>("/planner/dashboard"),
  optimizeEmergency: (body: { origin: string; emergency_type: string }) =>
    postAPI<import("./types").EmergencyResponseData>("/emergency/optimize", body),
  submitCitizenReport: (body: { category: string; lat: number; lng: number; road_name: string; description: string }) =>
    postAPI<import("./types").CitizenEngagementResponse>("/citizen/report", body),

  // Category 6
  getPatterns: () =>
    fetchAPI<import("./types").PatternDiscoveryResponse>("/analytics/patterns"),
  runScenario: (scenarioId: string) =>
    fetchAPI<import("./types").WhatIfResponse>(`/analytics/scenario/${scenarioId}`),
};
