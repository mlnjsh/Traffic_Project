/** SWR hooks for auto-refreshing traffic data from backend. */

import useSWR from "swr";
import { api } from "@/lib/api";
import type {
  CorridorListResponse,
  IncidentListResponse,
  ConstructionListResponse,
} from "@/lib/types";

const REFRESH_MS = 120_000; // 2 minutes — matches backend poll interval

export function useCorridors() {
  return useSWR<CorridorListResponse>("corridors", () => api.getCorridors(), {
    refreshInterval: REFRESH_MS,
  });
}

export function useIncidents(corridor?: string) {
  return useSWR<IncidentListResponse>(
    corridor ? `incidents-${corridor}` : "incidents",
    () => api.getIncidents(corridor),
    { refreshInterval: REFRESH_MS },
  );
}

export function useConstructionZones() {
  return useSWR<ConstructionListResponse>(
    "construction",
    () => api.getConstructionZones(),
    { refreshInterval: 300_000 }, // 5 min — construction data changes slowly
  );
}
