"""
Geospatial Grid Generator for URBAN-COOL AI.

Generates regular square spatial analysis grids (e.g. 100m x 100m) in a local metric
projected CRS (e.g. EPSG:32643 for Pune) and provides centroid coordinates and geometries
in both projected CRS (for spatial analysis) and WGS84 EPSG:4326 (for web GeoJSON export).
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
from typing import Dict, Any, Tuple, Optional
from app.geospatial.crs import get_projected_crs, DEFAULT_GEOGRAPHIC_CRS


def create_spatial_grid(
    city_name: str = "Pune",
    bbox_wgs84: Optional[list[float]] = None,
    grid_resolution_m: float = 100.0
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Creates a regular spatial grid of grid_resolution_m x grid_resolution_m.

    Args:
        city_name: Target study area city.
        bbox_wgs84: Optional bounding box [min_lon, min_lat, max_lon, max_lat] in EPSG:4326.
                    Defaults to central Pune study area.
        grid_resolution_m: Cell edge length in meters (default 100m).

    Returns:
        Tuple of (gdf_projected, gdf_wgs84):
        - gdf_projected: GeoDataFrame in local metric CRS (e.g., EPSG:32643)
        - gdf_wgs84: GeoDataFrame in WGS84 (EPSG:4326) with grid_id, latitude, longitude
    """
    if bbox_wgs84 is None:
        # Core Pune metropolitan study bounding box (approx 5km x 5km for Phase 1 performance)
        bbox_wgs84 = [73.820, 18.500, 73.870, 18.550]

    min_lon, min_lat, max_lon, max_lat = bbox_wgs84
    projected_crs = get_projected_crs(city_name)

    # Convert bounding box to metric projected CRS
    bbox_poly = Polygon([
        [min_lon, min_lat],
        [max_lon, min_lat],
        [max_lon, max_lat],
        [min_lon, max_lat],
        [min_lon, min_lat]
    ])
    gdf_bbox = gpd.GeoDataFrame(geometry=[bbox_poly], crs=DEFAULT_GEOGRAPHIC_CRS)
    gdf_bbox_proj = gdf_bbox.to_crs(projected_crs)
    
    minx, miny, maxx, maxy = gdf_bbox_proj.total_bounds

    # Generate grid cell coordinates in metric projected CRS
    x_coords = np.arange(minx, maxx, grid_resolution_m)
    y_coords = np.arange(miny, maxy, grid_resolution_m)

    polygons = []
    grid_ids = []
    
    city_prefix = city_name.upper().replace(" ", "_")

    cell_counter = 1
    for x in x_coords:
        for y in y_coords:
            poly = Polygon([
                (x, y),
                (x + grid_resolution_m, y),
                (x + grid_resolution_m, y + grid_resolution_m),
                (x, y + grid_resolution_m),
                (x, y)
            ])
            polygons.append(poly)
            grid_ids.append(f"{city_prefix}_GRID_100M_{cell_counter:04d}")
            cell_counter += 1

    gdf_proj = gpd.GeoDataFrame({
        "grid_id": grid_ids,
        "cell_area_m2": [p.area for p in polygons]
    }, geometry=polygons, crs=projected_crs)

    # Reproject to WGS84 for GeoJSON
    gdf_wgs84 = gdf_proj.to_crs(DEFAULT_GEOGRAPHIC_CRS)

    # Calculate centroids in projected metric CRS first for exact precision
    proj_centroids = gdf_proj.geometry.centroid
    gdf_centroids_proj = gpd.GeoDataFrame(geometry=proj_centroids, crs=projected_crs)
    gdf_centroids_wgs84 = gdf_centroids_proj.to_crs(DEFAULT_GEOGRAPHIC_CRS)

    gdf_wgs84["latitude"] = gdf_centroids_wgs84.geometry.y.round(6)
    gdf_wgs84["longitude"] = gdf_centroids_wgs84.geometry.x.round(6)

    # Attach coordinates back to projected GeoDataFrame as well
    gdf_proj["latitude"] = gdf_wgs84["latitude"]
    gdf_proj["longitude"] = gdf_wgs84["longitude"]

    return gdf_proj, gdf_wgs84
