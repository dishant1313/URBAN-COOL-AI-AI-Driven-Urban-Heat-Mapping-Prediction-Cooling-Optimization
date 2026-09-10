"""
Spatial Aggregation & Master Feature Dataset Builder.

Unifies 100m spatial grid generation, satellite/environmental remote sensing features (GEE),
and urban morphology features (OSM) into a clean, spatially aligned Master Geospatial Dataset.
"""

import logging
import geopandas as gpd
from typing import Tuple, Dict, Any, Optional
from datetime import date

from app.geospatial.grid import create_spatial_grid
from app.geospatial.gee_service import GEEService, GEEExtractionParams
from app.geospatial.osm_service import OSMService, OSMQueryArea
from app.geospatial.crs import DEFAULT_GEOGRAPHIC_CRS

logger = logging.getLogger("urban_cool_aggregation")


def build_master_geospatial_dataset(
    city_name: str = "Pune",
    bbox_wgs84: Optional[list[float]] = None,
    grid_resolution_m: float = 100.0,
    start_date: str = "2026-03-01",
    end_date: str = "2026-05-31"
) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Executes the spatial alignment and feature aggregation workflow:
    1. Creates projected 100m grid (EPSG:32643) and WGS84 grid (EPSG:4326).
    2. Extracts GEE & satellite environmental parameters (LST, NDVI, NDBI, NDWI, LULC, Albedo, ERA5).
    3. Extracts OSM urban morphology parameters (Buildings, Roads, Green spaces).
    4. Combines spatial attributes into a unified master GeoDataFrame in EPSG:4326.
    5. Assembles dataset lineage metadata.

    Returns:
        Tuple of (gdf_master_wgs84, metadata_dict)
    """
    logger.info(f"Initiating Master Dataset Construction for {city_name} ({grid_resolution_m}m grid)...")

    # Step 1: Spatial Grid Generation
    gdf_proj, gdf_wgs84 = create_spatial_grid(
        city_name=city_name,
        bbox_wgs84=bbox_wgs84,
        grid_resolution_m=grid_resolution_m
    )

    # Step 2: Satellite Remote Sensing Ingestion (GEE)
    gee_params = GEEExtractionParams(
        city_name=city_name,
        bbox=bbox_wgs84 if bbox_wgs84 else [73.820, 18.500, 73.870, 18.550],
        start_date=start_date,
        end_date=end_date
    )
    gee_service = GEEService()
    gdf_sat = gee_service.extract_grid_satellite_features(gdf_wgs84, gee_params)

    # Step 3: Urban Morphology Ingestion (OSM)
    osm_area = OSMQueryArea(
        city_name=city_name,
        bbox=gee_params.bbox
    )
    osm_service = OSMService()
    gdf_morph = osm_service.extract_grid_urban_morphology(gdf_proj, osm_area)

    # Step 4: Merge Features into Master Dataset
    master_columns = [
        "grid_id", "latitude", "longitude", "geometry",
        "lst", "ndvi", "ndbi", "ndwi", "lulc", "albedo",
        "air_temperature", "humidity", "wind_speed", "heat_risk"
    ]
    
    gdf_master = gdf_sat[master_columns].copy()

    # Join OSM features by grid_id
    morph_columns = ["grid_id", "building_count", "building_area", "building_density", "road_length", "road_density", "green_area", "green_fraction"]
    gdf_master = gdf_master.merge(gdf_morph[morph_columns], on="grid_id", how="left")

    # Add temporal & metadata columns
    gdf_master["observation_date"] = end_date

    # Dataset metadata
    metadata = {
        "city": city_name,
        "grid_resolution_m": int(grid_resolution_m),
        "total_grid_cells": len(gdf_master),
        "crs": DEFAULT_GEOGRAPHIC_CRS,
        "projected_crs": gdf_proj.crs.to_string(),
        "temporal_range": {"start_date": start_date, "end_date": end_date},
        "remote_sensing_lineage": gee_service.get_source_metadata(gee_params),
        "osm_lineage": {
            "source": "OpenStreetMap Contributors",
            "extracted_features": ["buildings", "highways", "parks_greenery"]
        }
    }

    logger.info(f"Master Dataset created successfully with {len(gdf_master)} grid cells.")
    return gdf_master, metadata
