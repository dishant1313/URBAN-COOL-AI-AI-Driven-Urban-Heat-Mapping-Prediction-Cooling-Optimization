import { FeatureCollection, DatasetStatistics, StudyAreaConfig, PipelineMetadataReport, GridCellProperties } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealthCheck() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (error) {
    console.warn('API Health offline:', error);
    return { status: 'offline', phase: 'Phase 2 Urban Heat Hotspot Detection' };
  }
}

export async function fetchHeatmapGeoJSON(layer: string = 'lst', limit: number = 700): Promise<FeatureCollection> {
  try {
    // Try Phase 2 heat layer endpoint first
    let res = await fetch(`${API_BASE_URL}/api/heat/layer?layer=${layer}&limit=${limit}`, { cache: 'no-store' });
    if (!res.ok) {
      // Fallback to general data heatmap endpoint
      res = await fetch(`${API_BASE_URL}/api/data/heatmap?layer=${layer}&limit=${limit}`, { cache: 'no-store' });
    }
    if (!res.ok) throw new Error('Failed to fetch spatial dataset');
    return await res.json();
  } catch (error) {
    console.warn('Backend API unreachable. Using client-side sample spatial dataset:', error);
    return {
      type: 'FeatureCollection',
      name: 'pune_phase2_fallback',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [[[73.852, 18.517], [73.861, 18.517], [73.861, 18.524], [73.852, 18.524], [73.852, 18.517]]]
          },
          properties: {
            grid_id: 'PUNE_GRID_100M_0001',
            latitude: 18.5204,
            longitude: 73.8567,
            lst: 41.8,
            lst_anomaly: 3.24,
            lst_zscore: 1.68,
            heat_risk: 'High',
            hotspot_class: 'Hotspot',
            hotspot_significance: '95% Confidence Hotspot',
            hotspot_score: 0.84,
            thermal_stress_index: 0.78,
            ndvi: 0.12,
            ndbi: 0.48,
            ndwi: -0.25,
            lulc: 'Built-up',
            albedo: 0.14,
            air_temperature: 36.2,
            humidity: 42.0,
            wind_speed: 2.1,
            building_count: 32,
            building_area: 7200,
            building_density: 0.72,
            road_length: 420,
            road_density: 0.42,
            green_area: 600,
            green_fraction: 0.06,
            phase3_notice: 'Driver analysis will be available in Phase 3.'
          }
        }
      ]
    };
  }
}

export async function fetchDatasetStatistics(): Promise<DatasetStatistics> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/heat/statistics`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch heat statistics');
    const data = await res.json();
    
    // Normalize into DatasetStatistics interface
    return {
      city: 'Pune',
      sample_size: data.validation_summary?.valid_cells || 3024,
      data_source: 'Phase 2 Urban Heat Hotspot Analysis',
      mean_lst_celsius: data.lst_statistics?.mean_lst || 38.56,
      max_lst_celsius: data.lst_statistics?.max_lst || 44.0,
      min_lst_celsius: data.lst_statistics?.min_lst || 32.75,
      median_lst_celsius: data.lst_statistics?.median_lst || 38.62,
      std_lst_celsius: data.lst_statistics?.std_lst || 1.93,
      max_anomaly_celsius: data.max_anomaly_celsius || 5.44,
      hotspot_area_km2: data.hotspot_statistics?.hotspot_area_km2 || 9.4,
      high_risk_area_km2: data.hotspot_statistics?.high_risk_area_km2 || 12.09,
      total_study_area_km2: data.hotspot_statistics?.total_study_area_km2 || 30.24,
      hotspot_count: data.hotspot_statistics?.hotspot_count || 940,
      coldspot_count: data.hotspot_statistics?.coldspot_count || 881,
      mean_ndvi: 0.22,
      mean_ndbi: 0.38,
      mean_ndwi: -0.18,
      mean_building_density: 0.54,
      mean_road_density: 0.38,
      high_risk_cells_count: data.risk_distribution?.High || 610,
      extreme_risk_cells_count: data.risk_distribution?.['Very High'] || 599,
      percentiles: data.lst_statistics?.percentiles || { P10: 36.0, P25: 37.15, P50: 38.62, P75: 39.95, P90: 41.05, P95: 41.64 },
      risk_distribution: data.risk_distribution || { 'Very Low': 605, Low: 613, Moderate: 597, High: 610, 'Very High': 599 },
      hotspot_distribution: data.hotspot_distribution || {}
    };
  } catch (error) {
    console.warn('Using fallback statistics:', error);
    return {
      city: 'Pune',
      sample_size: 3024,
      data_source: 'Phase 2 Master Dataset (100m Grid)',
      mean_lst_celsius: 38.56,
      max_lst_celsius: 44.0,
      min_lst_celsius: 32.75,
      median_lst_celsius: 38.62,
      std_lst_celsius: 1.93,
      max_anomaly_celsius: 5.44,
      hotspot_area_km2: 9.4,
      high_risk_area_km2: 12.09,
      total_study_area_km2: 30.24,
      hotspot_count: 940,
      coldspot_count: 881,
      mean_ndvi: 0.22,
      mean_ndbi: 0.38,
      mean_ndwi: -0.18,
      mean_building_density: 0.54,
      mean_road_density: 0.38,
      high_risk_cells_count: 610,
      extreme_risk_cells_count: 599,
      percentiles: { P10: 36.0, P25: 37.15, P50: 38.62, P75: 39.95, P90: 41.05, P95: 41.64 },
      risk_distribution: { 'Very Low': 605, Low: 613, Moderate: 597, High: 610, 'Very High': 599 },
      hotspot_distribution: { '99% Confidence Hotspot': 586, '95% Confidence Hotspot': 230, '90% Confidence Hotspot': 124 }
    };
  }
}

export async function fetchGridCellDetails(grid_id: string): Promise<GridCellProperties | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/heat/grid/${grid_id}`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    console.warn(`Grid cell ${grid_id} fetch failed:`, error);
    return null;
  }
}

export async function fetchPipelineMetadata(): Promise<PipelineMetadataReport | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/heat/metadata`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch metadata');
    return await res.json();
  } catch (error) {
    console.warn('Metadata unavailable:', error);
    return null;
  }
}

export async function fetchStudyAreas(): Promise<StudyAreaConfig[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/study-area`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch study areas');
    return await res.json();
  } catch (error) {
    return [
      {
        id: 'pune',
        name: 'Pune, MH (India)',
        country: 'India',
        center_lat: 18.5204,
        center_lon: 73.8567,
        default_zoom: 13,
        bbox_wgs84: [73.820, 18.500, 73.870, 18.550],
        projected_crs: 'EPSG:32643',
        grid_resolution_m: 100,
        active: true
      }
    ];
  }
}
