import { FeatureCollection, DatasetStatistics, StudyAreaConfig, LayerMetadata, PipelineMetadataReport } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealthCheck() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (error) {
    console.warn('API Health offline:', error);
    return { status: 'offline', phase: 'Phase 1 Geospatial Pipeline' };
  }
}

export async function fetchHeatmapGeoJSON(layer: string = 'lst', limit: number = 600): Promise<FeatureCollection> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/heatmap?layer=${layer}&limit=${limit}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch Phase 1 spatial dataset');
    return await res.json();
  } catch (error) {
    console.warn('Backend API unreachable. Falling back to local Phase 1 sample dataset:', error);
    // Fallback attempt to Phase 0 sample endpoint if data endpoint is unavailable
    try {
      const fallbackRes = await fetch(`${API_BASE_URL}/api/sample/heatmap`, { cache: 'no-store' });
      if (fallbackRes.ok) return await fallbackRes.json();
    } catch {}
    
    // Default local fallback feature collection
    return {
      type: 'FeatureCollection',
      name: 'pune_phase1_fallback',
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
            heat_risk: 'Extreme'
          }
        }
      ]
    };
  }
}

export async function fetchDatasetStatistics(): Promise<DatasetStatistics> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/statistics`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch statistics');
    return await res.json();
  } catch (error) {
    console.warn('Using fallback statistics:', error);
    return {
      city: 'Pune',
      sample_size: 3024,
      data_source: 'Phase 1 Master Dataset (100m Grid)',
      mean_lst_celsius: 38.6,
      max_lst_celsius: 43.8,
      min_lst_celsius: 31.2,
      mean_ndvi: 0.22,
      mean_ndbi: 0.38,
      mean_ndwi: -0.18,
      mean_building_density: 0.54,
      mean_road_density: 0.38,
      high_risk_cells_count: 820,
      extreme_risk_cells_count: 640,
      risk_distribution: {
        Low: 710,
        Medium: 854,
        High: 820,
        Extreme: 640
      }
    };
  }
}

export async function fetchPipelineMetadata(): Promise<PipelineMetadataReport | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/metadata`, { cache: 'no-store' });
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
