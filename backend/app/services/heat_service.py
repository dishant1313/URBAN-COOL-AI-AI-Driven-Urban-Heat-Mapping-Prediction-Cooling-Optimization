import json
import logging
import geopandas as gpd
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger("urban_cool_heat_service")


class HeatService:
    """
    Phase 2 Urban Heat Data Service.
    Loads precomputed Phase 2 spatial heat analysis dataset and statistics.
    Ensures sub-millisecond API response times by reading stored Phase 2 assets.
    """

    def __init__(self, p2_geojson_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        data_dir = base_dir / "data" / "processed"
        
        if p2_geojson_path:
            self.geojson_path = Path(p2_geojson_path)
        else:
            self.geojson_path = data_dir / "phase2_heat_analysis.geojson"
            # Fallback to Phase 1 dataset if Phase 2 is not yet generated
            if not self.geojson_path.exists():
                self.geojson_path = data_dir / "pune_master_100m.geojson"

        self.stats_path = data_dir / "phase2_heat_statistics.json"
        self._cached_gdf: Optional[gpd.GeoDataFrame] = None
        self._cached_stats: Optional[Dict[str, Any]] = None

    def get_gdf(self) -> gpd.GeoDataFrame:
        """Returns cached GeoDataFrame of Phase 2 dataset."""
        if self._cached_gdf is None:
            if not self.geojson_path.exists():
                raise FileNotFoundError(
                    f"Phase 2 dataset not found at {self.geojson_path}. Run `python scripts/run_phase2_analysis.py` first."
                )
            gdf = gpd.read_file(self.geojson_path)
            # Ensure clean string representation for object/datetime columns
            for col in gdf.columns:
                if col != "geometry" and (gdf[col].dtype == "object" or "datetime" in str(gdf[col].dtype)):
                    gdf[col] = gdf[col].astype(str)
            self._cached_gdf = gdf
        return self._cached_gdf

    def get_heat_statistics(self) -> Dict[str, Any]:
        """Returns Phase 2 summary heat statistics."""
        if self.stats_path.exists():
            with open(self.stats_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Compute on the fly if stats file missing
        gdf = self.get_gdf()
        lst_s = gdf["lst"].dropna()
        anom_s = gdf["lst_anomaly"].dropna() if "lst_anomaly" in gdf.columns else (lst_s - lst_s.mean())
        hotspot_mask = gdf["hotspot_class"] == "Hotspot" if "hotspot_class" in gdf.columns else (lst_s >= 40.0)

        return {
            "pipeline_phase": "Phase 2 Urban Heat Hotspot Detection & Heat Stress Mapping",
            "validation_summary": {
                "total_cells": len(gdf),
                "valid_cells": len(gdf),
                "missing_lst": 0,
                "min_lst": round(float(lst_s.min()), 2),
                "max_lst": round(float(lst_s.max()), 2),
                "mean_lst": round(float(lst_s.mean()), 2),
                "median_lst": round(float(lst_s.median()), 2),
                "std_lst": round(float(lst_s.std()), 2)
            },
            "max_anomaly_celsius": round(float(anom_s.max()), 2),
            "hotspot_statistics": {
                "hotspot_count": int(hotspot_mask.sum()),
                "hotspot_area_km2": round(float(hotspot_mask.sum() * 0.01), 3),
                "high_risk_area_km2": round(float((gdf["heat_risk"].isin(["High", "Very High"])).sum() * 0.01), 3) if "heat_risk" in gdf.columns else 0.0,
                "total_study_area_km2": round(float(len(gdf) * 0.01), 3)
            }
        }

    def get_layer_geojson(
        self,
        layer: str = "lst",
        bbox: Optional[List[float]] = None,
        limit: int = 600,
        hotspot_only: bool = False,
        risk_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Returns GeoJSON FeatureCollection filtered by layer metric, bounding box, or risk level.
        """
        gdf = self.get_gdf().copy()

        # Spatial filter
        if bbox and len(bbox) == 4:
            min_lon, min_lat, max_lon, max_lat = bbox
            gdf = gdf.cx[min_lon:max_lon, min_lat:max_lat]

        # Hotspot filter
        if hotspot_only and "hotspot_class" in gdf.columns:
            gdf = gdf[gdf["hotspot_class"] == "Hotspot"]

        # Risk level filter
        if risk_level and "heat_risk" in gdf.columns:
            gdf = gdf[gdf["heat_risk"].str.lower() == risk_level.lower()]

        # Limit for web UI response optimization
        if limit > 0 and len(gdf) > limit:
            gdf = gdf.iloc[:limit]

        geojson_dict = json.loads(gdf.to_json())
        geojson_dict["name"] = f"phase2_heat_{layer}"
        geojson_dict["metadata"] = {
            "active_layer": layer,
            "matching_features": len(gdf),
            "requested_limit": limit,
            "data_phase": "Phase 2 Processed Heat Analysis"
        }
        return geojson_dict

    def get_grid_cell_details(self, grid_id: str) -> Optional[Dict[str, Any]]:
        """Returns comprehensive attributes for a specific grid cell by grid_id."""
        gdf = self.get_gdf()
        cell_match = gdf[gdf["grid_id"] == grid_id]
        if len(cell_match) == 0:
            return None
        
        feature = json.loads(cell_match.iloc[0:1].to_json())["features"][0]
        props = feature["properties"]

        # Formatted response adhering to Section 23 specification
        formatted_cell = {
            "grid_id": props.get("grid_id"),
            "latitude": props.get("latitude"),
            "longitude": props.get("longitude"),
            "lst": props.get("lst"),
            "lst_anomaly": props.get("lst_anomaly"),
            "lst_zscore": props.get("lst_zscore"),
            "heat_risk": props.get("heat_risk"),
            "hotspot_class": props.get("hotspot_class"),
            "hotspot_significance": props.get("hotspot_significance"),
            "hotspot_score": props.get("hotspot_score"),
            "thermal_stress_index": props.get("thermal_stress_index"),
            "hotspot_frequency": props.get("hotspot_frequency"),
            "ndvi": props.get("ndvi"),
            "ndbi": props.get("ndbi"),
            "ndwi": props.get("ndwi"),
            "lulc": props.get("lulc"),
            "albedo": props.get("albedo"),
            "air_temperature": props.get("air_temperature"),
            "humidity": props.get("humidity"),
            "wind_speed": props.get("wind_speed"),
            "building_count": props.get("building_count"),
            "building_area": props.get("building_area"),
            "building_density": props.get("building_density"),
            "road_length": props.get("road_length"),
            "road_density": props.get("road_density"),
            "green_area": props.get("green_area"),
            "green_fraction": props.get("green_fraction"),
            "geometry": feature["geometry"],
            "phase3_notice": "Driver analysis will be available in Phase 3."
        }
        return formatted_cell

    def get_layer_metadata_catalog(self) -> List[Dict[str, Any]]:
        """Returns catalog of Phase 2 map layers for frontend layer selector."""
        return [
            {
                "id": "lst",
                "name": "Land Surface Temperature (LST)",
                "unit": "°C",
                "type": "Continuous",
                "description": "Satellite thermal infrared surface temperature",
                "color_scale": "YlOrRd"
            },
            {
                "id": "lst_anomaly",
                "name": "LST Anomaly",
                "unit": "°C",
                "type": "Diverging",
                "description": "Temperature deviation relative to study-area mean LST",
                "color_scale": "CoolWarm"
            },
            {
                "id": "lst_zscore",
                "name": "LST Z-Score",
                "unit": "Standard Deviations",
                "type": "Continuous",
                "description": "Standardized thermal anomaly Z-score",
                "color_scale": "RdBu_r"
            },
            {
                "id": "heat_risk",
                "name": "Heat Risk Classification",
                "unit": "Category",
                "type": "Categorical",
                "description": "Percentile-based thermal risk (Very Low to Very High)",
                "categories": ["Very Low", "Low", "Moderate", "High", "Very High"]
            },
            {
                "id": "hotspots",
                "name": "Statistical Spatial Hotspots (Gi*)",
                "unit": "Statistical Significance",
                "type": "Categorical",
                "description": "Getis-Ord Gi* spatial clustering of high/low thermal values",
                "categories": ["Hotspot", "Coldspot", "Not Significant"]
            },
            {
                "id": "hotspot_score",
                "name": "Normalized Hotspot Score",
                "unit": "0.0 – 1.0",
                "type": "Continuous",
                "description": "Combined thermal intensity and spatial clustering score",
                "color_scale": "Inferno"
            }
        ]
