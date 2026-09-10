export type HeatRiskLevel = 'Low' | 'Medium' | 'High' | 'Extreme';

export type MapLayerType = 'lst' | 'ndvi' | 'ndbi' | 'ndwi' | 'building_density' | 'road_density';

export interface GridCellProperties {
  grid_id: string;
  latitude: number;
  longitude: number;
  lst: number;
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
  heat_risk: HeatRiskLevel;
  observation_date?: string;
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
  mean_ndvi: number;
  mean_ndbi: number;
  mean_ndwi: number;
  mean_building_density: number;
  mean_road_density: number;
  high_risk_cells_count: number;
  extreme_risk_cells_count: number;
  risk_distribution: {
    Low: number;
    Medium: number;
    High: number;
    Extreme: number;
  };
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
  min_val: number;
  max_val: number;
  palette: string[];
}

export interface PipelineMetadataReport {
  dataset_metadata: {
    city: string;
    grid_resolution_m: number;
    total_grid_cells: number;
    crs: string;
    projected_crs: string;
    temporal_range: {
      start_date: string;
      end_date: string;
    };
    remote_sensing_lineage: Record<string, any>;
    osm_lineage: Record<string, any>;
  };
  validation_summary: {
    status: string;
    total_grid_cells: number;
    valid_geometries: number;
    duplicate_grid_ids: number;
    crs: string;
    is_crs_wgs84: boolean;
    coverage_percentages: Record<string, number>;
    anomalies_detected: string[];
  };
}
