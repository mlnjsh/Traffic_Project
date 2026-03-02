/** Congestion color scale per CLAUDE.md specification.
 *
 * Green (>30 km/h) -> Yellow -> Orange -> Red -> Black (<5 km/h)
 */

import { CongestionColor } from "./types";

export const CONGESTION_COLORS: Record<CongestionColor, string> = {
  green: "#22c55e",
  yellow: "#eab308",
  orange: "#f97316",
  red: "#ef4444",
  black: "#1f2937",
};

export const CONGESTION_HEX: Record<CongestionColor, string> = CONGESTION_COLORS;

export const COLOR_LABELS: Record<CongestionColor, string> = {
  green: "Free Flow (>30 km/h)",
  yellow: "Moderate (20-30 km/h)",
  orange: "Substantial Delay (10-20 km/h)",
  red: "Severe Congestion (5-10 km/h)",
  black: "Gridlock (<5 km/h)",
};

export const TREND_ICONS: Record<string, string> = {
  improving: "↗",
  stable: "→",
  worsening: "↘",
};

export const SEVERITY_COLORS: Record<number, string> = {
  1: "#22c55e",
  2: "#84cc16",
  3: "#eab308",
  4: "#f97316",
  5: "#ef4444",
};
