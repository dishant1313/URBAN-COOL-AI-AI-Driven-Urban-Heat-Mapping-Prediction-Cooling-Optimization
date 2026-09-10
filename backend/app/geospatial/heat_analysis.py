"""
URBAN-COOL AI — Phase 2 Urban Heat Hotspot Detection & Heat Stress Mapping.

Implements rigorous spatial statistical analysis:
1. Data quality check (drops invalid geometries, handles missing LST without zero substitution).
2. LST baseline statistics (mean, min, max, std, percentiles P10, P25, P50, P75, P90, P95).
3. LST Anomaly & Standardized Anomaly (Z-score).
4. Configurable percentile-based heat-risk classification (Very Low, Low, Moderate, High, Very High).
5. Getis-Ord Gi* spatial hotspot detection with distance/Queen spatial weights.
6. Normalized Hotspot Score (0.0 to 1.0).
7. Prototype Thermal Stress Index (combining LST, air temp, humidity).
8. Multi-date temporal persistence analysis (when multi-observation data exists).
9. Projected metric CRS (EPSG:32643) spatial area calculations (hotspot_area_km2, high_risk_area_km2).
"""

import logging
import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field

logger = logging.getLogger("urban_cool_heat_analysis")


class HeatRiskConfig(BaseModel):
    """Configurable thresholds for percentile-based heat-risk classification."""
    p_very_low: float = Field(20.0, description="Percentile upper bound for Very Low risk")
    p_low: float = Field(40.0, description="Percentile upper bound for Low risk")
    p_moderate: float = Field(60.0, description="Percentile upper bound for Moderate risk")
    p_high: float = Field(80.0, description="Percentile upper bound for High risk")


class ThermalStressWeights(BaseModel):
    """Configurable weights for Prototype Thermal Stress Index."""
    w_lst_zscore: float = Field(0.50, description="Weight for standardized LST")
    w_air_temp: float = Field(0.30, description="Weight for near-surface air temperature")
    w_humidity: float = Field(0.20, description="Weight for relative humidity contribution")


def validate_and_clean_lst_data(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Validates geometries and LST data quality before analysis.
    
    1. Removes invalid or empty geometries.
    2. Identifies missing LST values without replacing them with zero.
    3. Generates statistical summary report.
    """
    total_cells = len(gdf)
    if total_cells == 0:
        summary = {
            "total_cells": 0,
            "valid_cells": 0,
            "missing_lst": 0,
            "min_lst": None,
            "max_lst": None,
            "mean_lst": None,
            "median_lst": None,
            "std_lst": None
        }
        return gdf.copy(), summary

    # Step 1: Remove invalid or empty geometries
    valid_geom_mask = gdf.geometry.is_valid & (~gdf.geometry.is_empty)
    gdf_clean = gdf[valid_geom_mask].copy()
    valid_cells = len(gdf_clean)

    if valid_cells < total_cells:
        logger.warning(f"Dropped {total_cells - valid_cells} invalid/empty geometries.")

    # Step 2: Check missing LST values
    if "lst" not in gdf_clean.columns:
        gdf_clean["lst"] = np.nan

    lst_series = gdf_clean["lst"]
    missing_lst = int(lst_series.isna().sum())
    valid_lst_series = lst_series.dropna()

    if len(valid_lst_series) > 0:
        min_lst = round(float(valid_lst_series.min()), 2)
        max_lst = round(float(valid_lst_series.max()), 2)
        mean_lst = round(float(valid_lst_series.mean()), 2)
        median_lst = round(float(valid_lst_series.median()), 2)
        std_lst = round(float(valid_lst_series.std(ddof=0)), 2)
    else:
        min_lst = max_lst = mean_lst = median_lst = std_lst = None

    summary = {
        "total_cells": total_cells,
        "valid_cells": valid_cells,
        "missing_lst": missing_lst,
        "min_lst": min_lst,
        "max_lst": max_lst,
        "mean_lst": mean_lst,
        "median_lst": median_lst,
        "std_lst": std_lst
    }

    return gdf_clean, summary


def compute_lst_percentiles(lst_series: pd.Series) -> Dict[str, float]:
    """Calculates P10, P25, P50, P75, P90, P95 percentiles for LST."""
    clean_series = lst_series.dropna()
    if len(clean_series) == 0:
        return {"P10": 0.0, "P25": 0.0, "P50": 0.0, "P75": 0.0, "P90": 0.0, "P95": 0.0}

    percentile_keys = [10, 25, 50, 75, 90, 95]
    percentile_vals = np.percentile(clean_series, percentile_keys)

    return {
        f"P{p}": round(float(val), 2) for p, val in zip(percentile_keys, percentile_vals)
    }


def compute_lst_anomalies(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculates LST Anomaly (°C relative to mean LST) and Standardized Z-Score:
    
    LST_anomaly_i = LST_i - mean(LST)
    Z_i = (LST_i - mean(LST)) / std(LST)
    """
    gdf_res = gdf.copy()
    valid_lst = gdf_res["lst"].dropna()

    if len(valid_lst) == 0:
        gdf_res["lst_anomaly"] = np.nan
        gdf_res["lst_zscore"] = np.nan
        return gdf_res

    mean_lst = valid_lst.mean()
    std_lst = valid_lst.std(ddof=0)

    gdf_res["lst_anomaly"] = (gdf_res["lst"] - mean_lst).round(2)

    if std_lst > 1e-6:
        gdf_res["lst_zscore"] = ((gdf_res["lst"] - mean_lst) / std_lst).round(3)
    else:
        gdf_res["lst_zscore"] = 0.0

    return gdf_res


def classify_heat_risk(
    gdf: gpd.GeoDataFrame,
    config: Optional[HeatRiskConfig] = None
) -> gpd.GeoDataFrame:
    """
    Assigns percentile-based heat-risk classification:
    Very Low, Low, Moderate, High, Very High.
    """
    if config is None:
        config = HeatRiskConfig()

    gdf_res = gdf.copy()
    valid_lst = gdf_res["lst"].dropna()

    if len(valid_lst) == 0:
        gdf_res["heat_risk"] = "Not Classified"
        return gdf_res

    p_vl = float(np.percentile(valid_lst, config.p_very_low))
    p_l = float(np.percentile(valid_lst, config.p_low))
    p_m = float(np.percentile(valid_lst, config.p_moderate))
    p_h = float(np.percentile(valid_lst, config.p_high))

    def _assign_risk(val):
        if pd.isna(val):
            return "Not Classified"
        if val <= p_vl:
            return "Very Low"
        elif val <= p_l:
            return "Low"
        elif val <= p_m:
            return "Moderate"
        elif val <= p_h:
            return "High"
        else:
            return "Very High"

    gdf_res["heat_risk"] = gdf_res["lst"].apply(_assign_risk)
    return gdf_res


def compute_getis_ord_gi_star(
    gdf: gpd.GeoDataFrame,
    distance_threshold_m: float = 180.0
) -> gpd.GeoDataFrame:
    """
    Computes spatial Getis-Ord Gi* statistics for LST spatial clustering.
    
    Neighborhood definition:
    Grid is 100m x 100m. Centroid-to-centroid distance threshold of 180m includes
    all 8 immediate Queen contiguity neighbors + self (distance 0 and 100m/141m).
    
    Formula for Gi*:
    Gi* = [ sum_j w_{ij} x_j - X_bar sum_j w_{ij} ] / [ S * sqrt( (N sum_j w_{ij}^2 - (sum_j w_{ij})^2) / (N - 1) ) ]
    
    Output fields:
    - gi_zscore: calculated Gi* z-score
    - gi_pvalue: two-tailed p-value
    - hotspot_class: "Hotspot", "Coldspot", "Not Significant"
    - hotspot_significance: "99% Hotspot", "95% Hotspot", "90% Hotspot", "Not Significant", "90% Coldspot", "95% Coldspot", "99% Coldspot"
    """
    gdf_res = gdf.copy()
    n = len(gdf_res)

    if n < 3 or "lst" not in gdf_res.columns or gdf_res["lst"].dropna().empty:
        gdf_res["gi_zscore"] = 0.0
        gdf_res["gi_pvalue"] = 1.0
        gdf_res["hotspot_class"] = "Not Significant"
        gdf_res["hotspot_significance"] = "Not Significant"
        return gdf_res

    # Convert to centroid points in projected metric CRS if available, or compute from lat/lon
    if "geometry" in gdf_res.columns and gdf_res.crs is not None and gdf_res.crs.is_projected:
        centroids = gdf_res.geometry.centroid
        coords = np.column_stack([centroids.x, centroids.y])
    else:
        # Fallback to lat/lon converted to approx metric coords (meters)
        lats = gdf_res["latitude"].values if "latitude" in gdf_res.columns else np.zeros(n)
        lons = gdf_res["longitude"].values if "longitude" in gdf_res.columns else np.zeros(n)
        # 1 deg lat ~ 111,000m; 1 deg lon ~ 111,000m * cos(lat)
        mean_lat_rad = np.radians(np.mean(lats))
        y_m = lats * 111000.0
        x_m = lons * 111000.0 * np.cos(mean_lat_rad)
        coords = np.column_stack([x_m, y_m])

    # LST values array
    x = gdf_res["lst"].fillna(gdf_res["lst"].mean()).values
    x_bar = np.mean(x)
    s = np.std(x, ddof=0)

    if s < 1e-6:
        # Zero variance: no hotspots can be detected
        gdf_res["gi_zscore"] = 0.0
        gdf_res["gi_pvalue"] = 1.0
        gdf_res["hotspot_class"] = "Not Significant"
        gdf_res["hotspot_significance"] = "Not Significant"
        return gdf_res

    gi_zscores = np.zeros(n)
    
    # Pairwise distance matrix computation (optimized vectorized array or KDTree)
    for i in range(n):
        dists = np.linalg.norm(coords - coords[i], axis=1)
        # Include self in Gi* calculation (w_ii = 1)
        weights = (dists <= distance_threshold_m).astype(float)
        
        w_sum = np.sum(weights)
        w_sq_sum = np.sum(weights**2)
        
        num = np.sum(weights * x) - x_bar * w_sum
        denom_inside = (n * w_sq_sum - w_sum**2) / (n - 1)
        
        if denom_inside <= 0 or s <= 0:
            gi_zscores[i] = 0.0
        else:
            denom = s * np.sqrt(denom_inside)
            gi_zscores[i] = num / denom

    gdf_res["gi_zscore"] = np.round(gi_zscores, 3)

    # Convert Gi* z-score to class and significance labels
    # Critical Z-values for two-tailed standard normal:
    # 99%: Z > 2.576 or Z < -2.576
    # 95%: Z > 1.960 or Z < -1.960
    # 90%: Z > 1.645 or Z < -1.645

    hotspot_classes = []
    hotspot_sigs = []

    for z in gi_zscores:
        if z >= 2.576:
            hotspot_classes.append("Hotspot")
            hotspot_sigs.append("99% Confidence Hotspot")
        elif z >= 1.960:
            hotspot_classes.append("Hotspot")
            hotspot_sigs.append("95% Confidence Hotspot")
        elif z >= 1.645:
            hotspot_classes.append("Hotspot")
            hotspot_sigs.append("90% Confidence Hotspot")
        elif z <= -2.576:
            hotspot_classes.append("Coldspot")
            hotspot_sigs.append("99% Confidence Coldspot")
        elif z <= -1.960:
            hotspot_classes.append("Coldspot")
            hotspot_sigs.append("95% Confidence Coldspot")
        elif z <= -1.645:
            hotspot_classes.append("Coldspot")
            hotspot_sigs.append("90% Confidence Coldspot")
        else:
            hotspot_classes.append("Not Significant")
            hotspot_sigs.append("Not Significant")

    gdf_res["hotspot_class"] = hotspot_classes
    gdf_res["hotspot_significance"] = hotspot_sigs

    return gdf_res


def compute_hotspot_score(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Computes a normalized Hotspot Score between 0.0 and 1.0.
    """
    gdf_res = gdf.copy()
    if len(gdf_res) == 0:
        gdf_res["hotspot_score"] = np.nan
        return gdf_res

    lst_vals = gdf_res["lst"].fillna(gdf_res["lst"].mean()).values
    gi_zvals = gdf_res["gi_zscore"].fillna(0.0).values if "gi_zscore" in gdf_res.columns else np.zeros(len(gdf_res))

    lst_range = np.ptp(lst_vals) if len(lst_vals) > 0 else 0.0
    lst_norm = (lst_vals - np.min(lst_vals)) / lst_range if lst_range > 1e-6 else np.zeros(len(gdf_res))

    gi_range = np.ptp(gi_zvals) if len(gi_zvals) > 0 else 0.0
    gi_norm = (gi_zvals - np.min(gi_zvals)) / gi_range if gi_range > 1e-6 else np.zeros(len(gdf_res))

    score = 0.5 * lst_norm + 0.5 * gi_norm
    gdf_res["hotspot_score"] = np.clip(np.round(score, 3), 0.0, 1.0)

    return gdf_res


def compute_prototype_thermal_stress_index(
    gdf: gpd.GeoDataFrame,
    weights: Optional[ThermalStressWeights] = None
) -> gpd.GeoDataFrame:
    """
    Computes the 'Prototype Thermal Stress Index' (0.0 to 1.0).
    """
    if weights is None:
        weights = ThermalStressWeights()

    gdf_res = gdf.copy()
    n = len(gdf_res)
    if n == 0:
        gdf_res["thermal_stress_index"] = np.nan
        return gdf_res

    z_lst = gdf_res["lst_zscore"].fillna(0.0).values if "lst_zscore" in gdf_res.columns else np.zeros(n)
    air_temp = gdf_res["air_temperature"].fillna(35.0).values if "air_temperature" in gdf_res.columns else np.full(n, 35.0)
    humidity = gdf_res["humidity"].fillna(50.0).values if "humidity" in gdf_res.columns else np.full(n, 50.0)

    # Normalize z_lst (map -3.0 to +3.0 onto 0..1)
    norm_z_lst = np.clip((z_lst + 3.0) / 6.0, 0.0, 1.0)

    # Normalize air_temp
    t_ptp = np.ptp(air_temp) if n > 0 else 0.0
    norm_air_temp = (air_temp - np.min(air_temp)) / t_ptp if t_ptp > 1e-6 else np.full(n, 0.5)

    # Normalize humidity contribution (higher humidity + higher temp = higher stress)
    h_ptp = np.ptp(humidity) if n > 0 else 0.0
    norm_humidity = (humidity - np.min(humidity)) / h_ptp if h_ptp > 1e-6 else np.full(n, 0.5)

    tsi = (
        weights.w_lst_zscore * norm_z_lst +
        weights.w_air_temp * norm_air_temp +
        weights.w_humidity * norm_humidity
    )

    gdf_res["thermal_stress_index"] = np.clip(np.round(tsi, 3), 0.0, 1.0)
    return gdf_res


def compute_temporal_persistence(gdf: gpd.GeoDataFrame) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Computes multi-date hotspot persistence if multi-date observations exist.
    
    If single observation date exists:
    Returns hotspot_frequency = None/1.0 with message:
    "Temporal persistence analysis requires multi-date observations."
    """
    gdf_res = gdf.copy()

    has_multi_date = (
        "observation_date" in gdf_res.columns and
        gdf_res["observation_date"].nunique() > 1
    )

    if not has_multi_date:
        gdf_res["hotspot_frequency"] = np.where(gdf_res["hotspot_class"] == "Hotspot", 1.0, 0.0)
        gdf_res["persistence_class"] = np.where(gdf_res["hotspot_class"] == "Hotspot", "Single Observation Hotspot", "Not Hotspot")
        meta = {
            "is_multi_date": False,
            "message": "Temporal persistence analysis requires multi-date observations.",
            "observation_dates_count": 1
        }
        return gdf_res, meta

    # Group by grid_id or geometry centroid to calculate persistence across dates
    unique_dates = gdf_res["observation_date"].nunique()
    
    # Calculate frequency per cell
    freq_map = (
        gdf_res[gdf_res["hotspot_class"] == "Hotspot"]
        .groupby("grid_id")["observation_date"]
        .count() / float(unique_dates)
    ).to_dict()

    frequencies = gdf_res["grid_id"].map(lambda gid: round(float(freq_map.get(gid, 0.0)), 2)).values
    gdf_res["hotspot_frequency"] = frequencies

    # Assign persistence classes
    persistence_labels = []
    for freq in frequencies:
        if freq >= 0.8:
            persistence_labels.append("Persistent Hotspot")
        elif freq >= 0.5:
            persistence_labels.append("Frequent Hotspot")
        elif freq > 0.0:
            persistence_labels.append("Occasional Hotspot")
        else:
            persistence_labels.append("Not Hotspot")

    gdf_res["persistence_class"] = persistence_labels

    meta = {
        "is_multi_date": True,
        "observation_dates_count": unique_dates,
        "message": f"Multi-date persistence analyzed across {unique_dates} observation periods."
    }

    return gdf_res, meta


def compute_spatial_area_metrics(
    gdf: gpd.GeoDataFrame,
    projected_crs: str = "EPSG:32643"
) -> Dict[str, float]:
    """
    Calculates exact hotspot area (km²) and high-risk area (km²) in projected metric CRS.
    
    Requirement 20: Use projected metric CRS (EPSG:32643 for Pune).
    Do NOT calculate area directly using EPSG:4326 degrees.
    """
    if len(gdf) == 0:
        return {"hotspot_area_km2": 0.0, "high_risk_area_km2": 0.0, "total_study_area_km2": 0.0}

    # Reproject to metric CRS if not already
    if gdf.crs is None or not gdf.crs.is_projected:
        gdf_proj = gdf.to_crs(projected_crs)
    else:
        gdf_proj = gdf

    # Cell area in m²
    cell_areas_m2 = gdf_proj.geometry.area

    hotspot_mask = gdf_proj["hotspot_class"] == "Hotspot"
    high_risk_mask = gdf_proj["heat_risk"].isin(["High", "Very High", "Extreme"])

    hotspot_area_m2 = cell_areas_m2[hotspot_mask].sum()
    high_risk_area_m2 = cell_areas_m2[high_risk_mask].sum()
    total_area_m2 = cell_areas_m2.sum()

    return {
        "hotspot_area_km2": round(float(hotspot_area_m2 / 1_000_000.0), 3),
        "high_risk_area_km2": round(float(high_risk_area_m2 / 1_000_000.0), 3),
        "total_study_area_km2": round(float(total_area_m2 / 1_000_000.0), 3)
    }


def execute_phase2_heat_analysis_pipeline(
    gdf_input: gpd.GeoDataFrame,
    risk_config: Optional[HeatRiskConfig] = None,
    distance_threshold_m: float = 180.0,
    projected_crs: str = "EPSG:32643"
) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Executes the full Phase 2 Urban Heat Hotspot & Stress Mapping pipeline.
    """
    logger.info("Executing Phase 2 Urban Heat Pipeline...")

    # Step 1: Data Quality Check
    gdf_clean, validation_summary = validate_and_clean_lst_data(gdf_input)

    # Step 2: LST Baseline Statistics & Percentiles
    percentiles = compute_lst_percentiles(gdf_clean["lst"])

    # Step 3: LST Anomalies & Standardized Z-Score
    gdf_proc = compute_lst_anomalies(gdf_clean)

    # Step 4: Heat-Risk Classification
    gdf_proc = classify_heat_risk(gdf_proc, config=risk_config)

    # Step 5: Getis-Ord Gi* Spatial Hotspot Detection
    gdf_proc = compute_getis_ord_gi_star(gdf_proc, distance_threshold_m=distance_threshold_m)

    # Step 6: Hotspot Score (0 to 1)
    gdf_proc = compute_hotspot_score(gdf_proc)

    # Step 7: Prototype Thermal Stress Index
    gdf_proc = compute_prototype_thermal_stress_index(gdf_proc)

    # Step 8: Multi-date Temporal Persistence Analysis
    gdf_proc, temporal_meta = compute_temporal_persistence(gdf_proc)

    # Step 9: Metric CRS Spatial Area Calculations
    area_metrics = compute_spatial_area_metrics(gdf_proc, projected_crs=projected_crs)

    # Compute max anomaly
    valid_anomalies = gdf_proc["lst_anomaly"].dropna()
    max_anomaly = round(float(valid_anomalies.max()), 2) if len(valid_anomalies) > 0 else 0.0

    hotspot_count = int((gdf_proc["hotspot_class"] == "Hotspot").sum())
    coldspot_count = int((gdf_proc["hotspot_class"] == "Coldspot").sum())

    # Build full comprehensive Phase 2 summary metadata
    phase2_summary = {
        "pipeline_phase": "Phase 2 Urban Heat Hotspot Detection & Heat Stress Mapping",
        "validation_summary": validation_summary,
        "lst_statistics": {
            "min_lst": validation_summary["min_lst"],
            "max_lst": validation_summary["max_lst"],
            "mean_lst": validation_summary["mean_lst"],
            "median_lst": validation_summary["median_lst"],
            "std_lst": validation_summary["std_lst"],
            "percentiles": percentiles
        },
        "max_anomaly_celsius": max_anomaly,
        "hotspot_statistics": {
            "hotspot_count": hotspot_count,
            "coldspot_count": coldspot_count,
            "not_significant_count": int(len(gdf_proc) - hotspot_count - coldspot_count),
            "hotspot_area_km2": area_metrics["hotspot_area_km2"],
            "high_risk_area_km2": area_metrics["high_risk_area_km2"],
            "total_study_area_km2": area_metrics["total_study_area_km2"]
        },
        "risk_distribution": gdf_proc["heat_risk"].value_counts().to_dict(),
        "hotspot_distribution": gdf_proc["hotspot_significance"].value_counts().to_dict(),
        "spatial_parameters": {
            "grid_resolution_m": 100,
            "spatial_weights_method": "Distance-based Queen neighborhood",
            "distance_threshold_m": distance_threshold_m,
            "projected_crs": projected_crs
        },
        "temporal_metadata": temporal_meta,
        "disclaimer": "Heat risk and hotspot scores represent relative spatial thermal intensity for the study area and period. Not a medical or official heat-health warning."
    }

    return gdf_proc, phase2_summary
