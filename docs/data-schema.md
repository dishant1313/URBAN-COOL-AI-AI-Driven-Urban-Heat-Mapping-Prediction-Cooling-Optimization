# Standard Geospatial Data Schema Contract

Every spatial analysis grid cell in URBAN-COOL AI adheres to the standard schema contract defined below.

## 1. Grid Cell Feature Schema

```json
{
  "grid_id": "PUNE_GRID_001",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [73.852, 18.517],
        [73.861, 18.517],
        [73.861, 18.524],
        [73.852, 18.524],
        [73.852, 18.517]
      ]
    ]
  },
  "lst": 41.8,
  "ndvi": 0.12,
  "ndbi": 0.48,
  "ndwi": -0.25,
  "lulc": "Built-up",
  "albedo": 0.14,
  "air_temperature": 36.2,
  "humidity": 42.0,
  "wind_speed": 2.1,
  "building_density": 0.85,
  "road_density": 0.65,
  "population_density": 18500,
  "heat_risk": "Extreme"
}
```

## 2. Field Definitions

| Field Name | Type | Unit / Range | Description |
| :--- | :--- | :--- | :--- |
| `grid_id` | String | Unique Code | Unique grid cell identifier (e.g., PUNE_GRID_001) |
| `latitude` | Float | Degrees (-90 to +90) | Centroid latitude in WGS84 |
| `longitude` | Float | Degrees (-180 to +180) | Centroid longitude in WGS84 |
| `geometry` | GeoJSON | Polygon/Point | GeoJSON geometry object (EPSG:4326) |
| `lst` | Float | °C | Land Surface Temperature from Landsat 8/9 TIRS |
| `ndvi` | Float | Index (-1.0 to +1.0) | Normalized Difference Vegetation Index |
| `ndbi` | Float | Index (-1.0 to +1.0) | Normalized Difference Built-up Index |
| `ndwi` | Float | Index (-1.0 to +1.0) | Normalized Difference Water Index |
| `lulc` | String | Categorical | Land Use Land Cover (Built-up, Vegetation, Water, Bare Soil) |
| `albedo` | Float | Ratio (0.0 to 1.0) | Surface Shortwave Albedo |
| `air_temperature` | Float | °C | 2m Near-surface Air Temperature |
| `humidity` | Float | % | Relative Humidity |
| `wind_speed` | Float | m/s | 10m Wind Speed |
| `building_density` | Float | Ratio (0.0 to 1.0) | Ratio of building footprint area to grid cell area |
| `road_density` | Float | Ratio (0.0 to 1.0) | Ratio of road network area to grid cell area |
| `population_density` | Float | People / km² | Gridded population count per km² |
| `heat_risk` | String | Category | Assessed Heat Stress Risk (`Low`, `Medium`, `High`, `Extreme`) |

> **Note**: In Phase 0, missing or pending sensor fields are set to `null` rather than generating fabricated data.
