"""
URBAN-COOL AI — Phase 3 Model Training & Driver Analysis Script.

Loads Phase 2 processed GeoJSON data, trains baseline Linear Regression,
Random Forest, and XGBoost models, performs spatial block cross-validation,
computes SHAP driver contributions and dominant drivers, and exports processed assets.
"""

import sys
import os
import json
import logging
import geopandas as gpd
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.geospatial.driver_analysis import execute_phase3_driver_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_phase3_models")


def main():
    data_dir = BASE_DIR / "data" / "processed"
    input_geojson = data_dir / "phase2_heat_analysis.geojson"

    if not input_geojson.exists():
        input_geojson = data_dir / "pune_master_100m.geojson"

    if not input_geojson.exists():
        logger.error(f"Input dataset not found at {input_geojson}. Please run Phase 1 and 2 scripts first.")
        sys.exit(1)

    logger.info(f"Loading input dataset from {input_geojson}...")
    gdf = gpd.read_file(input_geojson)

    model_dir = BACKEND_DIR / "models"
    gdf_out, summary = execute_phase3_driver_pipeline(
        gdf,
        output_dir=str(data_dir),
        model_dir=str(model_dir)
    )

    # Save Phase 3 outputs
    output_geojson = data_dir / "phase3_driver_analysis.geojson"
    output_parquet = data_dir / "phase3_driver_analysis.parquet"
    output_stats = data_dir / "phase3_driver_statistics.json"

    logger.info(f"Saving GeoJSON output to {output_geojson}...")
    gdf_out.to_file(output_geojson, driver="GeoJSON")

    logger.info(f"Saving Parquet output to {output_parquet}...")
    # Convert object/string columns cleanly for Parquet export
    gdf_parquet = gdf_out.copy()
    for col in gdf_parquet.columns:
        if col != "geometry" and gdf_parquet[col].dtype == "object":
            gdf_parquet[col] = gdf_parquet[col].astype(str)
    gdf_parquet.to_parquet(output_parquet)

    logger.info(f"Saving Driver Statistics report to {output_stats}...")
    with open(output_stats, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("Phase 3 Driver Analysis Pipeline executed successfully!")


if __name__ == "__main__":
    main()
