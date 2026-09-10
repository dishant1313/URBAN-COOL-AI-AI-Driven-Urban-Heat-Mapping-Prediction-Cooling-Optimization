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
