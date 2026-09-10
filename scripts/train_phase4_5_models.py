"""
URBAN-COOL AI — Phase 4 & Phase 5 Model Training & Pipeline Automation Script.

Loads Phase 3 grid cell dataset, fits Linear Regression, Random Forest, XGBoost, and MLP models,
conducts 3x3 Spatial Block Cross-Validation, calculates baseline predictions, error metrics, and
ensemble prediction uncertainty, and serializes artifacts to disk.
"""

import sys
import logging
import geopandas as gpd
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "backend"))

from app.geospatial.predictive_models import execute_phase4_predictive_pipeline
from app.geospatial.scenario_engine import run_cooling_scenario
import pickle

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("train_phase4_5_models")


def main():
    logger.info("Initializing Phase 4 Predictive Urban Heat AI Pipeline Execution...")

    # Define paths
    data_dir = root_dir / "data" / "processed"
    model_dir = root_dir / "backend" / "models"

    p3_path = data_dir / "phase3_driver_analysis.geojson"
    p2_path = data_dir / "phase2_heat_analysis.geojson"

    if p3_path.exists():
        input_path = p3_path
    elif p2_path.exists():
        input_path = p2_path
    else:
        raise FileNotFoundError(f"Neither {p3_path} nor {p2_path} exists. Run Phase 2/3 processing first.")

    logger.info(f"Loading input geospatial dataset from: {input_path}")
    gdf = gpd.read_file(input_path)
    logger.info(f"Loaded dataset: {len(gdf)} cells (CRS: {gdf.crs})")

    # Execute Phase 4 Training & Prediction Pipeline
    gdf_predictions, summary = execute_phase4_predictive_pipeline(
        gdf=gdf,
        output_dir=str(data_dir),
        model_dir=str(model_dir)
    )

    logger.info("--- PHASE 4 MODEL EVALUATION SUMMARY ---")
    logger.info(f"Best Validated Model: {summary['best_model']}")
    for name, perf in summary['model_performance'].items():
        logger.info(f"  [{name}] Random CV R2: {perf['random_cv_r2']} | Spatial Block CV R2: {perf['spatial_cv_r2']} | Spatial RMSE: {perf['spatial_cv_rmse']} °C")

    # Run Baseline Test Scenario (Tree Canopy +20%)
    logger.info("Testing Phase 5 Cooling Intervention Engine with baseline tree canopy scenario...")
    model_path = model_dir / "phase4_predictive_model.pkl"
    with open(model_path, "rb") as f:
        predictive_pipeline = pickle.load(f)

    test_interventions = [{"type": "tree_cover", "intensity": 0.20}]
    gdf_scen, scen_summary = run_cooling_scenario(
        gdf=gdf_predictions,
        predictive_pipeline=predictive_pipeline,
        feature_bounds=summary["feature_bounds"],
        interventions=test_interventions
    )

    # Save baseline scenario output
    scen_out_path = data_dir / "phase5_scenario_results.geojson"
    gdf_scen.to_file(scen_out_path, driver="GeoJSON")
    logger.info(f"Phase 5 baseline scenario results exported to {scen_out_path}")
    logger.info(f"  - Mean Cooling under 20% Tree Canopy: {scen_summary['mean_cooling_celsius']} °C (Max: {scen_summary['maximum_cooling_celsius']} °C)")
    logger.info(f"  - High Heat Area Reduction: {scen_summary['high_heat_area_reduction_km2']} km²")

    logger.info("Successfully completed Phase 4 & Phase 5 training, evaluation, and scenario export!")


if __name__ == "__main__":
    main()
