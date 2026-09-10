# Phase 2 — Urban Heat Hotspot Detection & Heat Stress Mapping Report

**Project:** URBAN-COOL AI  
**Phase:** 2 — Urban Heat Intelligence & Spatial Statistics  
**Study Area:** Pune, MH, India (30.24 km², 3,024 100m × 100m grid cells)  
**Status:** COMPLETED & VERIFIED  

---

## 1. Executive Summary

Phase 2 introduces the **Urban Heat Intelligence Module** into URBAN-COOL AI. Building upon the 100m x 100m metric spatial grid established in Phase 1, Phase 2 implements a robust Python backend pipeline for spatial statistical analysis:
1. **LST Thermal Anomaly Detection**: Absolute temperature deviation (°C) from the study area spatial mean.
2. **Standardized Anomaly (Z-Score)**: Normalized thermal deviation ($Z_i = \frac{LST_i - \bar{x}}{\sigma}$).
3. **Percentile-Based Heat-Risk Classification**: Configurable thresholds mapping cells to *Very Low*, *Low*, *Moderate*, *High*, and *Very High* risk.
4. **Getis-Ord Gi\* Spatial Hotspot Detection**: Distance-based Queen spatial weights (180m threshold) identifying statistically significant clusters at 90%, 95%, and 99% confidence levels.
5. **Continuous Hotspot Score (0.0–1.0)**: Blended 0-1 spatial heat intensity score.
6. **Prototype Thermal Stress Index (0.0–1.0)**: Multi-indicator index integrating surface temperature, 2m air temperature, and relative humidity.
7. **Metric CRS Area Calculations**: Hotspot area ($9.40\text{ km}^2$) and high-risk area ($12.09\text{ km}^2$) computed strictly in metric `EPSG:32643` CRS.
8. **Interactive Layer Visualization**: Dashboard support for toggling map layers, detailed tooltips, legends, and grid inspector cards.

---

## 2. Statistical & Spatial Analysis Summary

| Indicator / Metric | Value / Statistics | Units / Details |
|---|---|---|
| **Total Study Grid Cells** | 3,024 | 100m × 100m cells |
| **Total Study Area** | 30.24 km² | EPSG:32643 Projected |
| **Mean Land Surface Temp (LST)** | 38.56 °C | Landsat 8 TIRS (ST_B10) |
| **Median LST (P50)** | 38.62 °C | Percentile P50 |
| **LST Standard Deviation ($\sigma$)** | 1.93 °C | Spatial Spread |
| **Min / Max LST Range** | 32.75 °C – 44.00 °C | Range: 11.25 °C |
| **Maximum Thermal Anomaly** | +5.44 °C | Above Area Mean |
| **Hotspot Area (Gi\* Significant)** | 9.40 km² | 31.08% of total area |
| **High & Very High Risk Area** | 12.09 km² | 39.98% of total area |
| **Hotspot Count (Gi\* Z > +1.645)** | 940 cells | 99%: 586, 95%: 230, 90%: 124 |
| **Coldspot Count (Gi\* Z < -1.645)** | 881 cells | 99%: 498, 95%: 223, 90%: 160 |

---

## 3. Data Schema & Asset Contracts

Processed Phase 2 analytical assets are precomputed and stored in:
- `data/processed/phase2_heat_analysis.geojson`
- `data/processed/phase2_heat_analysis.parquet`
- `data/processed/phase2_heat_statistics.json`

### Cell-Level Attributes
- `grid_id`: Unique identifier (`PUNE_GRID_100M_XXXX`)
- `lst`: Land surface temperature (°C)
- `lst_anomaly`: Thermal anomaly relative to mean (°C)
- `lst_zscore`: Standardized anomaly Z-score
- `heat_risk`: Risk level (`Very Low`, `Low`, `Moderate`, `High`, `Very High`)
- `hotspot_class`: `Hotspot`, `Coldspot`, `Not Significant`
- `hotspot_significance`: Gi\* confidence level (`99% Confidence Hotspot`, etc.)
- `hotspot_score`: Continuous 0.0–1.0 hotspot intensity score
- `thermal_stress_index`: Prototype 0.0–1.0 thermal stress index
- `hotspot_frequency` & `persistence_class`: Multi-date temporal persistence indicators

---

## 4. API Endpoints Registered

FastAPI router mounted at `/api/heat`:
- `GET /api/heat/statistics`: Summary metrics, percentiles, area calculations.
- `GET /api/heat/hotspots`: GeoJSON features filtered by hotspot significance.
- `GET /api/heat/risk`: GeoJSON features filtered by heat-risk category.
- `GET /api/heat/anomaly`: GeoJSON thermal anomaly layer.
- `GET /api/heat/layers`: Layer catalog metadata for frontend.
- `GET /api/heat/grid/{grid_id}`: Full Phase 2 microclimate inspection for a single cell.
- `GET /api/heat/metadata`: Lineage, methodology parameters, and scientific disclaimers.

---

## 5. Verification & Testing

- **Backend Test Suite (`backend/tests/test_phase2_heat_analysis.py`)**: 19 unit & integration tests covering percentiles, anomalies, Getis-Ord Gi\*, zero-variance, empty dataset, single-cell dataset, missing values, and API routes. Total test suite count: **29 passed**.
- **Frontend Production Build**: `npm run build` executed clean with 0 errors.

---

## 6. Scientific Transparency & Disclaimer

All heat risk classifications and hotspot scores represent relative spatial thermal intensity for the study area and observation period. They are calculated for urban spatial planning research and do **not** constitute official medical heat-health warnings. As mandated, driver causality analysis is deferred to **Phase 3**.
