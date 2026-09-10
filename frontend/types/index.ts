export type HeatRiskLevel = 'Very Low' | 'Low' | 'Moderate' | 'High' | 'Very High' | 'Extreme' | 'Medium';

export type HotspotClass = 'Hotspot' | 'Coldspot' | 'Not Significant';

export type MapLayerType =
  | 'lst'
  | 'lst_anomaly'
  | 'lst_zscore'
  | 'heat_risk'
  | 'hotspots'
  | 'hotspot_score'
  | 'thermal_stress_index'
  | 'dominant_driver'
  | 'predicted_lst'
  | 'prediction_error'
  | 'baseline_predicted_lst'
  | 'scenario_predicted_lst'
  | 'cooling_delta'
  | 'shap_building_density'
  | 'shap_ndvi'
  | 'shap_ndbi'
  | 'shap_air_temperature'
  | 'ndvi'
  | 'ndbi'
  | 'ndwi'
  | 'building_density'
  | 'road_density';

export interface GridCellProperties {
  grid_id: string;
  latitude: number;
  longitude: number;
  lst: number;
  lst_anomaly?: number;
  lst_zscore?: number;
  heat_risk?: HeatRiskLevel;
  hotspot_class?: HotspotClass;
  hotspot_significance?: string;
  hotspot_score?: number;
  thermal_stress_index?: number;
  hotspot_frequency?: number;
  persistence_class?: string;

  // Phase 3 & 4 ML attributes
  predicted_lst?: number;
  prediction_error?: number;
  absolute_error?: number;
  prediction_uncertainty?: number;
  dominant_driver?: string;
  dominant_driver_label?: string;
  dominant_driver_strength?: number;
  shap_ndvi?: number;
  shap_ndbi?: number;
  shap_ndwi?: number;
  shap_albedo?: number;
  shap_air_temperature?: number;
  shap_humidity?: number;
  shap_wind_speed?: number;
  shap_building_density?: number;
  shap_road_density?: number;
  shap_green_fraction?: number;

  // Phase 5 Scenario attributes
  baseline_predicted_lst?: number;
  scenario_predicted_lst?: number;
  cooling_delta?: number;
  intervention_impact?: string;
  cell_suitable?: boolean;

  ndvi: number;
  ndbi: number;
  ndwi: number;
  lulc: string;
  albedo: number;
  air_temperature: number;
  humidity: number;
  wind_speed: number;
  building_count?: number;
  building_area?: number;
  building_density?: number;
  road_length?: number;
  road_density?: number;
  green_area?: number;
  green_fraction?: number;
  observation_date?: string;
  phase3_notice?: string;
}

export interface GridCellFeature {
  type: 'Feature';
  id?: string;
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  properties: GridCellProperties;
}

export interface FeatureCollection {
  type: 'FeatureCollection';
  name?: string;
  metadata?: Record<string, any>;
  features: GridCellFeature[];
}

export interface DatasetStatistics {
  city: string;
  sample_size: number;
  data_source: string;
  mean_lst_celsius: number;
  max_lst_celsius: number;
  min_lst_celsius: number;
  median_lst_celsius?: number;
  std_lst_celsius?: number;
  max_anomaly_celsius?: number;
  hotspot_area_km2?: number;
  high_risk_area_km2?: number;
  total_study_area_km2?: number;
  hotspot_count?: number;
  coldspot_count?: number;
  mean_ndvi: number;
  mean_ndbi: number;
  mean_ndwi: number;
  mean_building_density: number;
  mean_road_density: number;
  high_risk_cells_count: number;
  extreme_risk_cells_count: number;
  percentiles?: {
    P10: number;
    P25: number;
    P50: number;
    P75: number;
    P90: number;
    P95: number;
  };
  risk_distribution: Record<string, number>;
  hotspot_distribution?: Record<string, number>;
}

export interface StudyAreaConfig {
  id: string;
  name: string;
  country: string;
  center_lat: number;
  center_lon: number;
  default_zoom: number;
  bbox_wgs84: [number, number, number, number];
  projected_crs: string;
  grid_resolution_m: number;
  active: boolean;
}

export interface LayerMetadata {
  id: MapLayerType;
  name: string;
  description: string;
  unit: string;
  min_val?: number;
  max_val?: number;
  palette?: string[];
  categories?: string[];
}

export interface PipelineMetadataReport {
  dataset_metadata?: Record<string, any>;
  validation_summary?: Record<string, any>;
  pipeline_phase?: string;
  lst_statistics?: Record<string, any>;
  hotspot_statistics?: Record<string, any>;
  spatial_parameters?: Record<string, any>;
  temporal_metadata?: Record<string, any>;
  disclaimer?: string;
}

// Phase 3 & 4 Specific Interfaces
export interface ModelMetrics {
  random_cv_r2: number;
  random_cv_rmse: number;
  random_cv_mae: number;
  spatial_cv_r2: number;
  spatial_cv_rmse: number;
  spatial_cv_mae: number;
  spatial_cv_method: string;
}

export interface ModelPerformanceComparison {
  best_model: string;
  performance_table: Record<string, ModelMetrics>;
  disclaimer: string;
}

export interface DriverStatisticsReport {
  pipeline_phase: string;
  best_model: string;
  model_performance: Record<string, ModelMetrics>;
  features_used: string[];
  target_variable: string;
  global_feature_importance: Record<string, number>;
  correlation_with_lst: Record<string, number>;
  dominant_driver_distribution: Record<string, number>;
  disclaimer: string;
}

// Phase 5 Scenario Interfaces
export interface InterventionTypeConfig {
  code: string;
  name: string;
  description: string;
  affected_features: string[];
  min_intensity: number;
  max_intensity: number;
  default_intensity: number;
}

export interface ScenarioInterventionSpec {
  type: string;
  intensity: number;
}

export interface ScenarioResultSummary {
  scenario_id: string;
  pipeline_phase: string;
  interventions_applied: ScenarioInterventionSpec[];
  sample_size: number;
  affected_cells: number;
  affected_area_km2: number;
  mean_baseline_lst: number;
  mean_scenario_lst: number;
  mean_cooling_celsius: number;
  maximum_cooling_celsius: number;
  high_heat_area_before_km2: number;
  high_heat_area_after_km2: number;
  high_heat_area_reduction_km2: number;
  extrapolation_warning: boolean;
  out_of_distribution_details: string[];
  disclaimer: string;
}

export interface ScenarioSimulationResult {
  summary: ScenarioResultSummary;
  geojson: FeatureCollection;
}
