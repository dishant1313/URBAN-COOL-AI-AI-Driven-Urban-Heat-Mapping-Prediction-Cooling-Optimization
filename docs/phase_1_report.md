# PHASE 1 END-OF-PHASE REPORT — URBAN-COOL AI

### Geospatial Data Acquisition, Processing & Feature Engineering

---

## 1. Data Sources Used & Exact Datasets/Products

| Category | Source Agency / Platform | Dataset / Product ID | Spatial Resolution |
| :--- | :--- | :--- | :--- |
| **Thermal LST** | USGS / NASA via GEE | `LANDSAT/LC08/C02/T1_L2` (Landsat 8 Collection 2 Level-2 ST) | 30 m (Resampled to 100 m) |
| **Vegetation & Built-up** | Copernicus / ESA via GEE | `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2 Surface Reflectance) | 10 m / 20 m |
| **Land Cover (LULC)** | Google / WRI via GEE | `GOOGLE/DYNAMICWORLD/V1` / `ESA/WorldCover/v100` | 10 m |
| **Meteorology** | ECMWF via GEE | `ECMWF/ERA5_LAND/DAILY_AGGR` (ERA5-Land Daily Aggregated) | 11,132 m (0.1°) |
| **Urban Morphology** | OpenStreetMap (OSM) | Overpass API / OSMnx (`building=*`, `highway=*`, `leisure=park`) | Vector Polygon / Line |

---

## 2. Sensor Bands Used & Mathematical Formulas

### A. Land Surface Temperature (LST)
- **Sensor**: Landsat 8 TIRS Band `ST_B10`
- **Formula**:
  $$\text{LST (°C)} = \left(\text{ST\_B10} \times 0.00341802 + 149.0\right) - 273.15$$

### B. Normalized Difference Vegetation Index (NDVI)
- **Sensor**: Sentinel-2 MSI (B8 = NIR, B4 = RED)
- **Formula**:
  $$\text{NDVI} = \frac{\text{NIR} - \text{RED}}{\text{NIR} + \text{RED}}$$

### C. Normalized Difference Built-up Index (NDBI)
- **Sensor**: Sentinel-2 MSI (B11 = SWIR1, B8 = NIR)
- **Formula**:
  $$\text{NDBI} = \frac{\text{SWIR1} - \text{NIR}}{\text{SWIR1} + \text{NIR}}$$

### D. Normalized Difference Water Index (NDWI)
- **Sensor**: Sentinel-2 MSI (B3 = GREEN, B8 = NIR)
- **Formula**:
  $$\text{NDWI} = \frac{\text{GREEN} - \text{NIR}}{\text{GREEN} + \text{NIR}}$$

### E. Shortwave Albedo Proxy
- **Sensor**: Landsat 8 SR Surface Reflectance (B2, B4, B5, B6, B7)
- **Formula**:
  $$\text{Albedo} = 0.356 B_2 + 0.130 B_4 + 0.373 B_5 + 0.085 B_6 + 0.072 B_7 - 0.0018$$

### F. Meteorology (ERA5 Relative Humidity)
- **Variables**: 2m Air Temp ($T$), Dewpoint Temp ($T_d$)
- **Magnus-Tetens Formula**:
  $$\text{RH (\%)} = 100 \times \frac{\exp\left(\frac{17.625 \, T_d}{243.04 + T_d}\right)}{\exp\left(\frac{17.625 \, T}{243.04 + T}\right)}$$

---

## 3. Spatial Resolution, CRS & Temporal Bounds

- **Analysis Grid Resolution**: $100\,\text{m} \times 100\,\text{m}$ ($10,000\,\text{m}^2$ cell area)
- **Projected Metric CRS**: `EPSG:32643` (UTM Zone 43N for Pune, India)
- **Web API & Export CRS**: `EPSG:4326` (WGS84 Geographic)
- **Temporal Analysis Range**: `2026-03-01` to `2026-05-31` (Summer peak thermal period)

---

## 4. Urban Morphology Extraction (OpenStreetMap)

- **Building Footprint Density**:
  $$\text{building\_density} = \frac{\sum \text{building\_footprint\_area}}{\text{grid\_cell\_area}} \quad \in [0.0, 1.0]$$
- **Road Network Density**:
  $$\text{road\_density} = \frac{\sum \text{road\_segment\_length}}{\text{grid\_cell\_area}} \quad (\text{m/m}^2)$$
- **Green Space Fraction**:
  $$\text{green\_fraction} = \frac{\sum \text{park\_and\_greenery\_area}}{\text{grid\_cell\_area}} \quad \in [0.0, 1.0]$$

---

## 5. Master Dataset Schema

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `grid_id` | String | Unique grid cell ID (e.g. `PUNE_GRID_100M_0001`) |
| `geometry` | Polygon | Cell boundary polygon (EPSG:4326) |
| `latitude` | Float | Centroid latitude |
| `longitude` | Float | Centroid longitude |
| `lst` | Float | Land Surface Temperature (°C) |
| `ndvi` | Float | Normalized Difference Vegetation Index (-1.0 to +1.0) |
| `ndbi` | Float | Normalized Difference Built-up Index (-1.0 to +1.0) |
| `ndwi` | Float | Normalized Difference Water Index (-1.0 to +1.0) |
| `lulc` | String | Land Use Land Cover (Built-up, Vegetation, Water, Bare Soil) |
| `albedo` | Float | Shortwave surface albedo ratio (0.0 to 1.0) |
| `air_temperature` | Float | ERA5 2m near-surface air temperature (°C) |
| `humidity` | Float | ERA5 relative humidity (%) |
| `wind_speed` | Float | ERA5 10m wind speed (m/s) |
| `building_count` | Integer | Total building footprints intersecting cell |
| `building_area` | Float | Total building footprint area (m²) |
| `building_density` | Float | Building area fraction (0.0 to 1.0) |
| `road_length` | Float | Total road segment length (m) |
| `road_density` | Float | Road length density (m/m²) |
| `green_area` | Float | Total park/vegetation area (m²) |
| `green_fraction` | Float | Green space area fraction (0.0 to 1.0) |
| `heat_risk` | String | Assessed thermal risk (`Low`, `Medium`, `High`, `Extreme`) |
| `observation_date` | String | Dataset observation / compositing date |

---

## 6. Data Validation Report Summary

```json
{
  "status": "PASSED",
  "total_grid_cells": 3024,
  "valid_geometries": 3024,
  "duplicate_grid_ids": 0,
  "crs": "EPSG:4326",
  "is_crs_wgs84": true,
  "coverage_percentages": {
    "lst_coverage_pct": 100.0,
    "ndvi_coverage_pct": 100.0,
    "ndbi_coverage_pct": 100.0,
    "ndwi_coverage_pct": 100.0,
    "osm_building_coverage_pct": 100.0,
    "osm_road_coverage_pct": 100.0,
    "meteorological_coverage_pct": 100.0
  },
  "anomalies_detected": []
}
```

---

## 7. Generated Datasets & Output Files

- **GeoParquet**: `data/processed/pune_master_100m.parquet` (271 KB)
- **GeoJSON**: `data/processed/pune_master_100m.geojson` (2.35 MB)
- **CSV**: `data/processed/pune_master_100m.csv` (813 KB)
- **Validation Report**: `data/processed/validation_report.json` (2.37 KB)

---

## 8. Backend API Endpoints Added

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/data/heatmap` | Spatial GeoJSON FeatureCollection with `bbox`, `layer`, `limit`, `min_lst`, `max_lst` filters |
| `GET` | `/api/data/features` | Paginated feature table rows with sorting (`page`, `page_size`, `sort_by`, `order`) |
| `GET` | `/api/data/statistics` | Baseline & heat risk distribution statistics |
| `GET` | `/api/data/metadata` | Dataset lineage, sensor specs, formulas, and validation coverage report |
| `GET` | `/api/data/grid/{grid_id}` | Detailed single cell spatial attributes |

---

## 9. Reproducible Pipeline Execution Command

To re-run the complete batch pipeline offline:
```bash
python scripts/run_phase1_pipeline.py
```

---

## 10. Known Limitations & Recommended Phase 2 Implementation

### Known Limitations in Phase 1:
- Hotspot visualization in Phase 1 is a preliminary thermal threshold overlay (*"Preliminary thermal visualization — hotspot analytics implemented in Phase 2"*).
- ML spatial predictor modeling, thermal driver decomposition, and cooling intervention simulation are reserved for Phase 2 and Phase 3.

### Recommended Phase 2 Implementation:
1. **Heat Driver Quantifier Engine**: Implement spatial regression (OLS, Spatial Lag Model / Geographically Weighted Regression) to quantify exact contribution of building density, NDVI deficit, and low albedo to local LST excess.
2. **Machine Learning Thermal Predictor**: Implement Random Forest / XGBoost spatial regression model predicting microclimate air temperature and surface thermal response under future urban growth scenarios.
3. **Hotspot Identification & Vulnerability Index**: Define multi-criteria heat vulnerability index combining thermal exposure (LST), physical sensitivity (built-up density), and demographic/population density.
