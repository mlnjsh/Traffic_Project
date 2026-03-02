/** Shared TypeScript types matching backend Pydantic schemas. */

export type CongestionColor = "green" | "yellow" | "orange" | "red" | "black";
export type TrendDirection = "improving" | "stable" | "worsening";

export interface Coordinate {
  lat: number;
  lng: number;
}

export interface CorridorSegment {
  start: Coordinate;
  end: Coordinate;
  speed_kmh: number;
  congestion_pct: number;
  color: CongestionColor;
}

export interface ActiveIncidentBrief {
  type: string;
  location: string;
  severity: number;
}

export interface CorridorStatus {
  corridor_id: string;
  name: string;
  direction: string | null;
  current_speed_kmh: number;
  free_flow_speed_kmh: number;
  congestion_pct: number;
  active_incidents: ActiveIncidentBrief[];
  incident_count: number;
  delay_minutes: number;
  travel_time_minutes: number;
  free_flow_time_minutes: number;
  color: CongestionColor;
  trend: TrendDirection;
  trend_description: string;
  segments: CorridorSegment[];
  data_freshness: string;
  updated_at: string;
  sources: string[];
}

export interface CorridorListResponse {
  corridors: CorridorStatus[];
  total: number;
  timestamp: string;
  demo_mode: boolean;
}

export interface IncidentLocation {
  lat: number;
  lng: number;
  road_name: string;
  nearest_landmark: string | null;
}

export interface DiversionRoute {
  name: string;
  via: string;
  added_distance_km: number;
  added_time_minutes: number;
  current_conditions: string;
}

export interface IncidentReport {
  incident_id: string;
  type: string;
  type_label: string;
  location: IncidentLocation;
  severity: number;
  severity_label: string;
  affected_length_km: number;
  delay_minutes: number;
  diversions: DiversionRoute[];
  description: string;
  start_time: string;
  estimated_end_time: string | null;
  is_active: boolean;
  source: string;
  last_updated: string;
}

export interface IncidentListResponse {
  incidents: IncidentReport[];
  total_active: number;
  corridor_filter: string | null;
  timestamp: string;
  data_freshness: string;
  demo_mode: boolean;
}

export interface ProjectMilestone {
  name: string;
  target_date: string;
  status: string;
  risk_factor: string | null;
}

export interface DiversionInfo {
  direction: string;
  primary_alternative: string;
  added_distance_km: number;
  time_penalty_freeflow: string;
  current_conditions: string;
}

export interface PeakAmplification {
  normal_peak_window: string;
  amplified_window: string;
  extension_hours: number;
  description: string;
}

export interface ConstructionZone {
  zone_id: string;
  project_name: string;
  agency: string;
  location_description: string;
  affected_roads: string[];
  start_coordinates: Coordinate;
  end_coordinates: Coordinate;
  lane_restriction: string;
  traffic_management: string;
  start_date: string;
  end_date: string;
  completion_confidence_pct: number;
  uncertainty_days: number;
  completion_pct: number;
  milestones: ProjectMilestone[];
  diversions: DiversionInfo[];
  diversion_compliance_pct: number | null;
  peak_amplification: PeakAmplification | null;
  normalization_weeks: number;
  normalization_note: string;
  capacity_reduction_pct: number | null;
  additional_delay_minutes: string | null;
  source: string;
  last_updated: string;
}

export interface ConstructionListResponse {
  zones: ConstructionZone[];
  total_active: number;
  timestamp: string;
  demo_mode: boolean;
}

// --- Category 2: Predictive & Planning Queries ---

export interface CongestionPredictionPoint {
  time_from_now_minutes: number;
  predicted_speed_kmh: number;
  predicted_congestion_pct: number;
  predicted_color: string;
  confidence_pct: number;
}

export interface ShortTermPrediction {
  horizon: string;
  direction: string;
  current_speed_kmh: number;
  predicted_speed_5min: number;
  predicted_speed_10min: number;
  predicted_speed_15min: number;
  estimated_change_minutes: number;
  confidence_pct: number;
  basis: string;
  narrative: string;
}

export interface MediumTermPrediction {
  horizon: string;
  day_of_week: string;
  typical_clear_time: string;
  current_assessment: string;
  estimated_clear_time: string;
  predictions: CongestionPredictionPoint[];
  confidence_pct: number;
  basis: string;
  narrative: string;
}

export interface ConstructionPrediction {
  horizon: string;
  project_name: string;
  completion_pct: number;
  scheduled_completion: string;
  uncertainty_days: number;
  normalization_weeks: number;
  confidence_pct: number;
  basis: string;
  narrative: string;
}

export interface PredictionResponse {
  corridor_id: string;
  corridor_name: string;
  short_term: ShortTermPrediction;
  medium_term: MediumTermPrediction;
  construction: ConstructionPrediction | null;
  timestamp: string;
  demo_mode: boolean;
}

export interface DepartureOption {
  label: string;
  departure_time: string;
  arrival_time: string;
  travel_time_minutes: number;
  route_recommendation: string;
  confidence_pct: number;
  risk_level: string;
  congestion_at_departure: string;
  notes: string;
}

export interface DepartureOptimizerResponse {
  origin: string;
  destination: string;
  desired_arrival: string;
  day_of_week: string;
  options: DepartureOption[];
  elasticity_insight: { corridor: string; early_departure: string; late_departure: string; time_saved_pct: number; time_saved_minutes: number; insight: string } | null;
  factors_considered: string[];
  timestamp: string;
  demo_mode: boolean;
}

export interface EventImpactResponse {
  event_name: string;
  event_type: string;
  venue: string;
  expected_attendance: number;
  corridor_impacts: { corridor_id: string; corridor_name: string; congestion_multiplier: number; additional_delay_minutes: number; severity: string }[];
  avoid_windows: { label: string; window: string; recommendation: string }[];
  safe_windows: { label: string; window: string; recommendation: string }[];
  estimated_recovery_hours: number;
  recovery_narrative: string;
  timestamp: string;
  demo_mode: boolean;
}

// --- Category 3: Route Optimization Queries ---

export type RouteObjective = "fastest" | "most_reliable" | "fuel_efficient" | "multimodal" | "avoid_construction";
export type VehicleClass = "two_wheeler" | "car" | "truck" | "bmtc_bus" | "emergency" | "auto_rickshaw";
export type CongestionLevel = "free_flow" | "light" | "moderate" | "heavy" | "severe" | "gridlock";

export interface RouteSegment {
  road_name: string;
  distance_km: number;
  estimated_time_minutes: number;
  congestion_level: CongestionLevel;
  speed_kmh: number;
  known_issues: string[];
}

export interface RouteOption {
  objective: RouteObjective;
  label: string;
  summary: string;
  total_distance_km: number;
  estimated_time_minutes: number;
  time_range_minutes: string;
  confidence_pct: number;
  congestion_level: CongestionLevel;
  known_issues: string[];
  segments: RouteSegment[];
  savings_vs_default: string | null;
  notes: string;
}

export interface MultiModalLeg {
  mode: string;
  from_location: string;
  to_location: string;
  distance_km: number;
  time_minutes: number;
  cost_inr: number | null;
  details: string;
}

export interface MultiModalOption {
  legs: MultiModalLeg[];
  total_time_minutes: number;
  total_cost_inr: number | null;
  comparison_vs_driving: string;
}

export interface SmartRouteResponse {
  origin: string;
  destination: string;
  routes: RouteOption[];
  multimodal: MultiModalOption | null;
  data_sources: string[];
  timestamp: string;
  demo_mode: boolean;
}

export interface VehicleRestriction {
  restriction_type: string;
  description: string;
  affected_roads: string[];
}

export interface ParkingInfo {
  name: string;
  type: string;
  distance_from_dest_m: number;
  estimated_cost_inr: number | null;
  availability: string;
}

export interface BusConnection {
  route_number: string;
  from_stop: string;
  to_stop: string;
  frequency_minutes: number;
  estimated_arrival_minutes: number;
  walking_distance_m: number;
  metro_connection: string | null;
}

export interface VehicleRouteOption {
  vehicle_class: VehicleClass;
  route_summary: string;
  total_distance_km: number;
  estimated_time_minutes: number;
  time_range_minutes: string;
  restrictions_applied: VehicleRestriction[];
  parking: ParkingInfo | null;
  bus_connections: BusConnection[];
  safety_notes: string[];
  cost_estimate: string | null;
  special_notes: string[];
}

export interface VehicleRoutingResponse {
  origin: string;
  destination: string;
  vehicle_class: VehicleClass;
  vehicle_label: string;
  route: VehicleRouteOption;
  alternative_mode_suggestion: string | null;
  data_sources: string[];
  timestamp: string;
  demo_mode: boolean;
}

// --- Category 4: Heatmap & Visualization Queries ---

export type SignalPhase = "green" | "red" | "amber";

export interface SignalStatus {
  junction_id: string;
  junction_name: string;
  lat: number;
  lng: number;
  current_phase: SignalPhase;
  countdown_seconds: number;
  cycle_time_seconds: number;
  green_time_seconds: number;
  red_time_seconds: number;
  pedestrian_phase: boolean;
  data_source: string;
}

export interface SignalListResponse {
  signals: SignalStatus[];
  total: number;
  coverage_note: string;
  timestamp: string;
  demo_mode: boolean;
}

export interface OverlayLayer {
  layer_id: string;
  name: string;
  description: string;
  enabled_by_default: boolean;
  data_endpoint: string;
  icon: string;
}

export interface DataSourceInfo {
  name: string;
  refresh_rate: string;
  coverage: string;
  role: string;
}

export interface EnhancedHeatmapResponse {
  data_sources: DataSourceInfo[];
  overlay_layers: OverlayLayer[];
  color_scale: Record<string, string>;
  refresh_interval_seconds: number;
  map_config: { center: { lat: number; lng: number }; zoom: number; map_type: string; satellite_toggle: boolean };
  timestamp: string;
  demo_mode: boolean;
}

export interface TrafficCardResponse {
  corridor_id: string;
  corridor_name: string;
  segment_road: string;
  current_speed_kmh: number;
  free_flow_speed_kmh: number;
  congestion_pct: number;
  color: string;
  delay_minutes: number;
  trend: string;
  trend_description: string;
  active_incidents: number;
  construction_nearby: boolean;
  prediction_summary: string;
  data_freshness: string;
  sources: string[];
  timestamp: string;
}

// --- Category 5: Problem-Solving Prompts ---

export interface ModeComparison {
  mode: string;
  estimated_time_minutes: number;
  estimated_cost_inr: number;
  reliability: string;
  notes: string;
}

export interface CommuterForecast {
  period: string;
  greeting: string;
  route_summary: string;
  optimal_departure: string;
  current_conditions: string;
  mode_comparisons: ModeComparison[];
  event_alert: string | null;
  overnight_updates: string[];
  departure_advice: string;
  savings_narrative: string | null;
  peak_insight: string;
  timestamp: string;
  demo_mode: boolean;
}

export interface LogisticsResponse {
  fleet_id: string;
  current_time_window: string;
  night_window_insight: string;
  active_construction_zones: number;
  construction_free_routes: number;
  recommended_route: { total_distance_km: number; total_time_minutes: number; stops: { location: string; estimated_arrival: string; loading_time_minutes: number; restrictions: string[] }[]; fuel_savings_pct: number; night_window_used: boolean };
  restrictions_summary: string[];
  fuel_optimization_note: string;
  timestamp: string;
  demo_mode: boolean;
}

export interface PlannerDashboardResponse {
  corridor_rankings: { rank: number; corridor_id: string; corridor_name: string; congestion_severity: string; structural_cause: string; years_persistent: number; annual_growth_pct: number | null }[];
  emerging_hotspots: { rank: number; corridor_id: string; corridor_name: string; congestion_severity: string; structural_cause: string; years_persistent: number; annual_growth_pct: number | null }[];
  infrastructure_projects: { project_name: string; type: string; expected_impact: string; investment_crore: number | null; timeline: string }[];
  demand_metrics: { metric: string; value: string; trend: string; insight: string }[];
  performance_metrics: Record<string, string>;
  recommendations: string[];
  timestamp: string;
  demo_mode: boolean;
}

export interface EmergencyResponseData {
  emergency_type: string;
  origin: string;
  recommended_hospital: { name: string; specialty: string; distance_km: number; estimated_time_minutes: number; capacity_status: string; epath_available: boolean };
  alternative_hospitals: { name: string; specialty: string; distance_km: number; estimated_time_minutes: number; capacity_status: string; epath_available: boolean }[];
  epath_status: string;
  signal_preemption_count: number;
  estimated_response_time_minutes: number;
  improvement_vs_standard: string;
  gps_tracking: string;
  pre_arrival_alert: string;
  incident_detection_note: string;
  timestamp: string;
  demo_mode: boolean;
}

export interface CitizenEngagementResponse {
  report: { report_id: string; category: string; location_lat: number; location_lng: number; road_name: string; description: string; ai_classification: string | null; verification_status: string; verification_eta_minutes: number; reporter_reliability_score: number };
  confirmation_message: string;
  community_validations: number;
  gamification: Record<string, any>;
  feedback_channels: string[];
  timestamp: string;
  demo_mode: boolean;
}

// --- Category 6: Advanced Analytics ---

export interface PatternDiscoveryResponse {
  temporal_patterns: { pattern_type: string; description: string; time_window: string; congestion_level: string; speed_kmh: number | null; insight: string }[];
  seasonal_patterns: { month: string; congestion_index: number; classification: string; note: string }[];
  spatial_patterns: { corridor: string; trend: string; annual_change_pct: number; years_tracked: number; cause: string }[];
  key_insights: string[];
  data_period: string;
  timestamp: string;
  demo_mode: boolean;
}

export interface WhatIfResponse {
  scenario: { scenario_id: string; title: string; description: string; parameters: Record<string, string>; results: { metric: string; before: string; after: string; change: string; confidence: string }[]; investment_estimate: string | null; implementation_timeline: string | null; equity_considerations: string | null; feasibility: string; recommendation: string };
  comparison_baseline: string;
  methodology: string;
  caveats: string[];
  timestamp: string;
  demo_mode: boolean;
}

// --- Route Intelligence Narrative ---

export interface NarrativeSection {
  section_id: string;
  title: string;
  icon: string;
  content: string;
  severity: "info" | "warning" | "alert" | "success";
}

export interface RouteNarrativeResponse {
  origin: string;
  destination: string;
  vehicle_class: string | null;
  sections: NarrativeSection[];
  generated_at: string;
  data_sources: string[];
  demo_mode: boolean;
}
