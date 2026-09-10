"""
URBAN-COOL AI — Cooling Intervention Scenario Simulation Engine (Phase 5).

Executes cooling scenario simulations by modifying predictor feature vectors,
evaluating baseline vs scenario predicted LSTs through the trained Phase 4 AI model,
detecting out-of-distribution feature extrapolation, and aggregating city & hotspot statistics.
"""

import hashlib
import json
import logging
import pickle
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.geospatial.intervention_rules import INTERVENTION_REGISTRY

logger = logging.getLogger("urban_cool_scenario_engine")

_SCENARIO_CACHE: Dict[str, Dict[str, Any]] = {}


def generate_scenario_hash(
    area_filter: Optional[str],
    interventions: List[Dict[str, Any]],
    model_version: str = "v4.1.0"
) -> str:
    """Generates a unique deterministic MD5 hash for caching scenario executions."""
    canonical_dict = {
        "area": area_filter or "all",
        "interventions": sorted(interventions, key=lambda x: x.get("type", "")),
        "model_version": model_version
    }
    dumped = json.dumps(canonical_dict, sort_keys=True)
    return hashlib.md5(dumped.encode("utf-8")).hexdigest()


def check_out_of_distribution(
    X_modified: pd.DataFrame,
    feature_bounds: Dict[str, Dict[str, float]]
) -> Tuple[bool, List[str]]:
    """Checks if any modified feature values fall substantially outside training distribution bounds."""
    warnings = []
    is_ood = False

    for col in X_modified.columns:
        if col in feature_bounds:
            b = feature_bounds[col]
            f_min, f_max = b["min"], b["max"]
            col_min = float(X_modified[col].min())
            col_max = float(X_modified[col].max())

            # 10% margin threshold beyond training range
            margin = (f_max - f_min) * 0.10
            if col_min < (f_min - margin) or col_max > (f_max + margin):
                is_ood = True
                warnings.append(
                    f"Feature '{col}' values [{col_min:.2f}, {col_max:.2f}] extend beyond model training range [{f_min:.2f}, {f_max:.2f}]."
                )

    return is_ood, warnings


def run_cooling_scenario(
    gdf: gpd.GeoDataFrame,
    predictive_pipeline: Any,
    feature_bounds: Dict[str, Dict[str, float]],
    interventions: List[Dict[str, Any]],
    grid_id_filter: Optional[str] = None,
    hotspot_only: bool = False
) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """Runs a single or multi-intervention cooling scenario simulation across grid cells."""
    if not interventions:
        raise ValueError("Scenario execution requires at least one intervention rule.")

    # Validate intervention inputs
    for spec in interventions:
        itype = spec.get("type")
        intensity = float(spec.get("intensity", 0.0))

        if itype not in INTERVENTION_REGISTRY:
            raise ValueError(f"Unsupported intervention type '{itype}'. Available: {list(INTERVENTION_REGISTRY.keys())}")
        
        rule_cls = INTERVENTION_REGISTRY[itype]
        min_i, max_i = rule_cls.allowed_intensity_range
        if not (min_i <= intensity <= max_i):
            raise ValueError(f"Intensity {intensity} for '{itype}' outside valid range [{min_i}, {max_i}].")

    # Filter target grid subset if requested
    target_gdf = gdf.copy()
    if grid_id_filter:
        target_gdf = target_gdf[target_gdf["grid_id"] == grid_id_filter]
        if len(target_gdf) == 0:
            raise ValueError(f"Grid cell '{grid_id_filter}' not found in study area dataset.")
    elif hotspot_only and "hotspot_class" in target_gdf.columns:
        target_gdf = target_gdf[target_gdf["hotspot_class"] == "Hotspot"]

    # Extract baseline predictors
    cont_cols = list(feature_bounds.keys())
    cat_cols = ["lulc"] if "lulc" in target_gdf.columns else []

    X_baseline = target_gdf[cont_cols + cat_cols].copy()

    # Predict Baseline LST if not already present
    if "baseline_predicted_lst" in target_gdf.columns:
        baseline_preds = target_gdf["baseline_predicted_lst"].values
    else:
        baseline_preds = predictive_pipeline.predict(X_baseline)

    # Modify feature matrix iteratively according to intervention rules
    X_modified = X_baseline.copy()
    affected_cells_mask = pd.Series(False, index=target_gdf.index)

    for spec in interventions:
        itype = spec.get("type")
        intensity = float(spec.get("intensity", 0.10))
        rule_cls = INTERVENTION_REGISTRY[itype]

        for idx, row in target_gdf.iterrows():
            if rule_cls.is_cell_suitable(row):
                mods = rule_cls.apply_transformation(row, intensity)
                for feat, val in mods.items():
                    if feat in X_modified.columns:
                        X_modified.loc[idx, feat] = val
                affected_cells_mask.loc[idx] = True

    # Check Out-of-Distribution Warnings
    is_ood, ood_warnings = check_out_of_distribution(X_modified[cont_cols], feature_bounds)

    # Predict Scenario LST through the EXACT SAME Phase 4 model
    scenario_preds = predictive_pipeline.predict(X_modified)

    # Calculate cooling delta (baseline - scenario)
    cooling_delta = baseline_preds - scenario_preds

    # Attach results to GeoDataFrame output
    gdf_res = target_gdf.copy()
    gdf_res["baseline_predicted_lst"] = np.round(baseline_preds, 2)
    gdf_res["scenario_predicted_lst"] = np.round(scenario_preds, 2)
    gdf_res["cooling_delta"] = np.round(cooling_delta, 2)
    gdf_res["intervention_impact"] = np.where(cooling_delta > 0.05, "Cooling", np.where(cooling_delta < -0.05, "Warming", "No Change"))
    gdf_res["cell_suitable"] = affected_cells_mask.values

    # Compute City-level & Hotspot Scenario Summary Metrics
    affected_count = int(affected_cells_mask.sum())
    mean_base = float(np.mean(baseline_preds))
    mean_scen = float(np.mean(scenario_preds))
    mean_cool = float(np.mean(cooling_delta))
    max_cool = float(np.max(cooling_delta))

    # Area threshold metrics (1 cell = 0.01 km²)
    cell_area_km2 = 0.01
    affected_area_km2 = round(affected_count * cell_area_km2, 2)
    
    # High heat area (> 40°C) before vs after
    high_base_count = int((baseline_preds >= 40.0).sum())
    high_scen_count = int((scenario_preds >= 40.0).sum())

    summary = {
        "scenario_id": generate_scenario_hash(grid_id_filter, interventions),
        "pipeline_phase": "Phase 5 Cooling Intervention Scenario Simulator",
        "interventions_applied": interventions,
        "sample_size": len(gdf_res),
        "affected_cells": affected_count,
        "affected_area_km2": affected_area_km2,
        "mean_baseline_lst": round(mean_base, 2),
        "mean_scenario_lst": round(mean_scen, 2),
        "mean_cooling_celsius": round(mean_cool, 2),
        "maximum_cooling_celsius": round(max_cool, 2),
        "high_heat_area_before_km2": round(high_base_count * cell_area_km2, 2),
        "high_heat_area_after_km2": round(high_scen_count * cell_area_km2, 2),
        "high_heat_area_reduction_km2": round((high_base_count - high_scen_count) * cell_area_km2, 2),
        "extrapolation_warning": is_ood,
        "out_of_distribution_details": ood_warnings,
        "disclaimer": "Cooling values produced by this prototype are model-based scenario estimates derived from changes in predictor variables. They are not direct measurements of real-world intervention performance."
    }

    return gdf_res, summary
