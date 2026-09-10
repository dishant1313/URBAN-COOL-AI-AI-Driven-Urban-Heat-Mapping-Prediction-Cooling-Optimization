"""
Geospatial Coordinate Reference System (CRS) Management.

Design Rationale:
- WGS84 (EPSG:4326) is standard for Web Mapping and GeoJSON exchanges across browsers and UI maps.
- EPSG:4326 uses angular degrees, so computing areas (m²) or Euclidean distances (m) directly in EPSG:4326
  results in severe spatial distortion depending on latitude.
- All metric operations (area, buffer distances, cooling radius calculations, grid generation) MUST be
  performed in an appropriate equal-area or conformal projected CRS (e.g. UTM Zone 43N / EPSG:32643 for Pune).
"""

import geopandas as gpd
from typing import Tuple, Dict

# Standard CRS Definitions
DEFAULT_GEOGRAPHIC_CRS = "EPSG:4326"

# Recommended projected CRS per study area
STUDY_AREA_PROJECTED_CRS: Dict[str, str] = {
    "Pune": "EPSG:32643",       # UTM Zone 43N
    "Mumbai": "EPSG:32643",     # UTM Zone 43N
    "Delhi": "EPSG:32644",      # UTM Zone 44N
    "Bengaluru": "EPSG:32643",  # UTM Zone 43N
    "Default": "EPSG:3857"      # Web Mercator
}


def get_projected_crs(city_name: str) -> str:
    """Return the suitable metric projected CRS for a given study area city."""
    return STUDY_AREA_PROJECTED_CRS.get(city_name, STUDY_AREA_PROJECTED_CRS["Default"])


def reproject_to_metric(gdf: gpd.GeoDataFrame, city_name: str = "Pune") -> gpd.GeoDataFrame:
    """Reproject a GeoDataFrame from geographic CRS (EPSG:4326) to local projected metric CRS."""
    target_crs = get_projected_crs(city_name)
    if gdf.crs is None:
        gdf.set_crs(DEFAULT_GEOGRAPHIC_CRS, inplace=True)
    return gdf.to_crs(target_crs)


def reproject_to_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject a GeoDataFrame back to standard WGS84 (EPSG:4326) for GeoJSON export."""
    return gdf.to_crs(DEFAULT_GEOGRAPHIC_CRS)
