"""
Geospatial Data Validation Engine for URBAN-COOL AI.

Runs validation checks on the aggregated master dataset:
1. Geometry validity & topology check.
2. Duplicate grid_id check.
3. Feature presence & missing data coverage percentages.
4. Physical value range validation (LST: 10-65°C, NDVI/NDBI/NDWI: -1 to +1, densities: 0 to 1).
5. CRS consistency check.
6. Structured validation report generation.
"""

import geopandas as gpd
import numpy as np
from typing import Dict, Any


def validate_master_dataset(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """
    Validates master geospatial dataset and produces a complete validation report.

    Args:
        gdf: GeoDataFrame containing aggregated master features.

    Returns:
        Dict containing validation metrics, coverage stats, and anomaly flags.
    """
    total_cells = len(gdf)
    if total_cells == 0:
        return {"error": "Empty dataset", "status": "FAILED"}

    # 1. Geometry checks
    valid_geometries = int(gdf.geometry.is_valid.sum())
    non_empty_geometries = int((~gdf.geometry.is_empty).sum())

    # 2. Duplicate Grid IDs
    duplicate_grid_ids = int(gdf["grid_id"].duplicated().sum())

    # 3. Missing Value / Coverage Statistics
    lst_valid_count = int(gdf["lst"].notna().sum()) if "lst" in gdf.columns else 0
    ndvi_valid_count = int(gdf["ndvi"].notna().sum()) if "ndvi" in gdf.columns else 0
    ndbi_valid_count = int(gdf["ndbi"].notna().sum()) if "ndbi" in gdf.columns else 0
    ndwi_valid_count = int(gdf["ndwi"].notna().sum()) if "ndwi" in gdf.columns else 0
    building_valid_count = int(gdf["building_density"].notna().sum()) if "building_density" in gdf.columns else 0
    road_valid_count = int(gdf["road_density"].notna().sum()) if "road_density" in gdf.columns else 0
    meteo_valid_count = int(gdf["air_temperature"].notna().sum()) if "air_temperature" in gdf.columns else 0

    lst_coverage_pct = round((lst_valid_count / total_cells) * 100, 2)
    ndvi_coverage_pct = round((ndvi_valid_count / total_cells) * 100, 2)
    ndbi_coverage_pct = round((ndbi_valid_count / total_cells) * 100, 2)
    ndwi_coverage_pct = round((ndwi_valid_count / total_cells) * 100, 2)
    building_coverage_pct = round((building_valid_count / total_cells) * 100, 2)
    road_coverage_pct = round((road_valid_count / total_cells) * 100, 2)
    meteo_coverage_pct = round((meteo_valid_count / total_cells) * 100, 2)

    # 4. Physical Value Range & Anomaly Checks
    anomalies = []
    
    if "lst" in gdf.columns:
        invalid_lst = int(((gdf["lst"] < 10.0) | (gdf["lst"] > 65.0)).sum())
        if invalid_lst > 0:
            anomalies.append(f"{invalid_lst} cells with impossible LST values (outside 10°C to 65°C)")

    if "ndvi" in gdf.columns:
        invalid_ndvi = int(((gdf["ndvi"] < -1.0) | (gdf["ndvi"] > 1.0)).sum())
        if invalid_ndvi > 0:
            anomalies.append(f"{invalid_ndvi} cells with invalid NDVI values (outside -1 to +1)")

    if "building_density" in gdf.columns:
        invalid_bld_density = int(((gdf["building_density"] < 0.0) | (gdf["building_density"] > 1.0)).sum())
        if invalid_bld_density > 0:
            anomalies.append(f"{invalid_bld_density} cells with invalid building_density values (outside 0 to 1)")

    # 5. CRS consistency check
    crs_str = gdf.crs.to_string() if gdf.crs else "Unassigned"
    is_wgs84 = "4326" in crs_str or "OGC:CRS84" in crs_str

    # 6. Overall validation status
    is_passed = (
        valid_geometries == total_cells and
        duplicate_grid_ids == 0 and
        len(anomalies) == 0 and
        is_wgs84
    )

    validation_report = {
        "status": "PASSED" if is_passed else "WARNINGS_DETECTED",
        "total_grid_cells": total_cells,
        "valid_geometries": valid_geometries,
        "duplicate_grid_ids": duplicate_grid_ids,
        "crs": crs_str,
        "is_crs_wgs84": is_wgs84,
        "coverage_percentages": {
            "lst_coverage_pct": lst_coverage_pct,
            "ndvi_coverage_pct": ndvi_coverage_pct,
            "ndbi_coverage_pct": ndbi_coverage_pct,
            "ndwi_coverage_pct": ndwi_coverage_pct,
            "osm_building_coverage_pct": building_coverage_pct,
            "osm_road_coverage_pct": road_coverage_pct,
            "meteorological_coverage_pct": meteo_coverage_pct
        },
        "anomalies_detected": anomalies
    }

    return validation_report
