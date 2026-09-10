#!/usr/bin/env python3
"""
URBAN-COOL AI — Phase 2 Execution Pipeline Script.

Executes the Phase 2 Urban Heat Hotspot Detection & Heat Stress Mapping pipeline:
1. Loads Phase 1 master geospatial dataset (pune_master_100m.geojson).
2. Validates LST quality (identifies missing LST, drops invalid geometries).
3. Computes LST summary statistics & percentiles (P10, P25, P50, P75, P90, P95).
4. Computes LST anomalies (°C relative to mean) & standardized Z-scores.
5. Computes percentile-based heat-risk classification (Very Low, Low, Moderate, High, Very High).
6. Performs Getis-Ord Gi* spatial hotspot detection with distance-based spatial weights.
7. Computes continuous normalized Hotspot Score (0.0 to 1.0).
8. Computes Prototype Thermal Stress Index (0.0 to 1.0).
9. Computes multi-date temporal persistence (if multi-date data available).
10. Computes exact projected metric CRS (EPSG:32643) spatial area metrics (hotspot_area_km2, high_risk_area_km2).
11. Exports processed Phase 2 dataset to GeoParquet, GeoJSON, and statistics JSON.
"""

import sys
import json
import logging
import geopandas as gpd
from pathlib import Path

# Add backend directory to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "backend"))

from app.geospatial.heat_analysis import execute_phase2_heat_analysis_pipeline, HeatRiskConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("run_phase2_analysis")


def run_phase2_pipeline():
    logger.info("==========================================================")
    logger.info("  URBAN-COOL AI — Starting Phase 2 Urban Heat Analysis")
    logger.info("==========================================================")

    data_dir = root_dir / "data" / "processed"
    phase1_geojson_path = data_dir / "pune_master_100m.geojson"

    if not phase1_geojson_path.exists():
        logger.error(f"Phase 1 master dataset not found at {phase1_geojson_path}.")
        logger.info("Please run `python scripts/run_phase1_pipeline.py` first.")
        sys.exit(1)

    # Step 1: Load Phase 1 Master Dataset
    logger.info(f"Loading Phase 1 master dataset from {phase1_geojson_path}...")
    gdf_p1 = gpd.read_file(phase1_geojson_path)
    logger.info(f"Loaded {len(gdf_p1)} grid cell features.")

    # Step 2-10: Execute Phase 2 Heat Analysis Pipeline
    gdf_p2, phase2_summary = execute_phase2_heat_analysis_pipeline(
        gdf_input=gdf_p1,
        risk_config=HeatRiskConfig(),
        distance_threshold_m=180.0,
        projected_crs="EPSG:32643"
    )

    # Step 11: Export Phase 2 Processed Dataset
    logger.info("Exporting Phase 2 outputs...")
    
    # Export GeoJSON
    p2_geojson_path = data_dir / "phase2_heat_analysis.geojson"
    gdf_p2.to_file(p2_geojson_path, driver="GeoJSON")
    logger.info(f"  [GEOJSON]: {p2_geojson_path}")

    # Export Parquet / GeoParquet
    p2_parquet_path = data_dir / "phase2_heat_analysis.parquet"
    # Ensure all datetime or non-numeric object columns are clean strings
    gdf_p2_clean = gdf_p2.copy()
    for col in gdf_p2_clean.columns:
        if col != "geometry" and (gdf_p2_clean[col].dtype == "object" or "datetime" in str(gdf_p2_clean[col].dtype)):
            gdf_p2_clean[col] = gdf_p2_clean[col].astype(str)
    gdf_p2_clean.to_parquet(p2_parquet_path)
    logger.info(f"  [PARQUET]: {p2_parquet_path}")

    # Export Statistics & Metadata JSON
    p2_stats_path = data_dir / "phase2_heat_statistics.json"
    with open(p2_stats_path, "w", encoding="utf-8") as f:
        json.dump(phase2_summary, f, indent=2)
    logger.info(f"  [JSON STATS]: {p2_stats_path}")

    logger.info("==========================================================")
    logger.info("  Phase 2 Urban Heat Analysis Execution Complete!")
    logger.info("  LST Statistics:")
    logger.info(f"    - Mean LST: {phase2_summary['lst_statistics']['mean_lst']} °C")
    logger.info(f"    - Max LST:  {phase2_summary['lst_statistics']['max_lst']} °C")
    logger.info(f"    - Max Anomaly: +{phase2_summary['max_anomaly_celsius']} °C")
    logger.info("  Hotspot Summary:")
    logger.info(f"    - Hotspot Area: {phase2_summary['hotspot_statistics']['hotspot_area_km2']} km²")
    logger.info(f"    - High-Risk Area: {phase2_summary['hotspot_statistics']['high_risk_area_km2']} km²")
    logger.info(f"    - Hotspot Count: {phase2_summary['hotspot_statistics']['hotspot_count']} cells")
    logger.info("==========================================================")


if __name__ == "__main__":
    run_phase2_pipeline()
