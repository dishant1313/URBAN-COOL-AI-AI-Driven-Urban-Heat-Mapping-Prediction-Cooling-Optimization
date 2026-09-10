#!/usr/bin/env python3
"""
URBAN-COOL AI — Phase 1 Geospatial Pipeline Execution Script.

Reproducible offline batch pipeline:
1. Generates 100m x 100m spatial analysis grid in local metric projected CRS (EPSG:32643).
2. Extracts Google Earth Engine (GEE) satellite & environmental features (LST, NDVI, NDBI, NDWI, LULC, Albedo, ERA5).
3. Extracts OpenStreetMap (OSM) urban morphology features (Buildings, Roads, Green spaces).
4. Performs spatial aggregation onto analysis grid cells.
5. Validates master dataset integrity (geometry checks, range checks, coverage statistics).
6. Exports dataset to GeoParquet, GeoJSON, CSV, and validation report.
"""

import sys
import json
import logging
from pathlib import Path

# Add backend directory to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "backend"))

from app.geospatial.aggregation import build_master_geospatial_dataset
from app.geospatial.validation import validate_master_dataset
from app.geospatial.exporters import export_master_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("run_phase1_pipeline")


def run_pipeline():
    logger.info("==========================================================")
    logger.info("  URBAN-COOL AI — Starting Phase 1 Geospatial Data Pipeline")
    logger.info("==========================================================")

    city_name = "Pune"
    grid_res = 100.0  # 100m x 100m grid cells
    start_date = "2026-03-01"
    end_date = "2026-05-31"

    # Core Pune metropolitan study area bounding box [min_lon, min_lat, max_lon, max_lat]
    bbox_pune = [73.820, 18.500, 73.870, 18.550]

    # Step 1-4: Build Master Dataset
    gdf_master, metadata = build_master_geospatial_dataset(
        city_name=city_name,
        bbox_wgs84=bbox_pune,
        grid_resolution_m=grid_res,
        start_date=start_date,
        end_date=end_date
    )

    # Step 5: Data Validation
    logger.info("Running Data Validation Checks...")
    validation_report = validate_master_dataset(gdf_master)
    logger.info(f"Validation Status: {validation_report['status']}")
    logger.info(f"Total Grid Cells: {validation_report['total_grid_cells']}")
    logger.info("Coverage Stats:")
    for k, v in validation_report["coverage_percentages"].items():
        logger.info(f"  - {k}: {v}%")

    # Step 6: Export Master Dataset
    logger.info("Exporting Master Geospatial Datasets...")
    generated_files = export_master_dataset(
        gdf_master=gdf_master,
        metadata=metadata,
        validation_report=validation_report,
        file_prefix="pune_master_100m"
    )

    logger.info("==========================================================")
    logger.info("  Phase 1 Geospatial Pipeline Execution Complete!")
    logger.info("  Generated Files:")
    for fmt, path in generated_files.items():
        logger.info(f"    [{fmt.upper()}]: {path}")
    logger.info("==========================================================")


if __name__ == "__main__":
    run_pipeline()
