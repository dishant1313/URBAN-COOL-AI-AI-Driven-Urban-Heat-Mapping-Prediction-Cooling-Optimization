import json
import logging
import geopandas as gpd
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger("urban_cool_data_service")


class DataService:
    def __init__(self, master_geojson_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        if master_geojson_path:
            self.geojson_path = Path(master_geojson_path)
        else:
            p2_path = base_dir / "data" / "processed" / "phase2_heat_analysis.geojson"
            if p2_path.exists():
                self.geojson_path = p2_path
            else:
                self.geojson_path = base_dir / "data" / "processed" / "pune_master_100m.geojson"
        
        self.validation_report_path = base_dir / "data" / "processed" / "validation_report.json"
        self._cached_gdf: Optional[gpd.GeoDataFrame] = None
        self._cached_json: Optional[Dict[str, Any]] = None

    def get_gdf(self) -> gpd.GeoDataFrame:
        """Return cached GeoDataFrame of master dataset."""
        if self._cached_gdf is None:
            if not self.geojson_path.exists():
                raise FileNotFoundError(f"Processed master dataset not found at {self.geojson_path}. Run `python scripts/run_phase1_pipeline.py` first.")
            gdf = gpd.read_file(self.geojson_path)
            # Ensure all non-numeric objects (e.g. Timestamp) are clean strings
            for col in gdf.columns:
                if col != "geometry" and (gdf[col].dtype == "object" or "datetime" in str(gdf[col].dtype)):
                    gdf[col] = gdf[col].astype(str)
            self._cached_gdf = gdf
        return self._cached_gdf

    def get_heatmap_geojson(
        self,
        bbox: Optional[List[float]] = None,
        layer: str = "lst",
        limit: int = 500,
        min_lst: Optional[float] = None,
        max_lst: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Returns GeoJSON FeatureCollection filtered by bounding box [min_lon, min_lat, max_lon, max_lat],
        layer metric, and limit to ensure ultra-fast web rendering.
        """
        gdf = self.get_gdf().copy()

        # Filter by bounding box if provided
        if bbox and len(bbox) == 4:
            min_lon, min_lat, max_lon, max_lat = bbox
            gdf = gdf.cx[min_lon:max_lon, min_lat:max_lat]

        # Filter by temperature range
        if min_lst is not None:
            gdf = gdf[gdf["lst"] >= min_lst]
        if max_lst is not None:
            gdf = gdf[gdf["lst"] <= max_lst]

        # Limit feature count for browser optimization
        if limit > 0 and len(gdf) > limit:
            gdf = gdf.iloc[:limit]

        geojson_dict = json.loads(gdf.to_json())
        geojson_dict["name"] = "pune_master_100m"
        geojson_dict["metadata"] = {
            "total_matching_features": len(gdf),
            "requested_limit": limit,
            "layer": layer,
            "data_status": "Phase 1 Processed Dataset"
        }
        return geojson_dict

    def get_statistics(self) -> Dict[str, Any]:
        """Compute aggregate baseline and risk statistics from processed master dataset."""
        gdf = self.get_gdf()

        lst_series = gdf["lst"].dropna()
        ndvi_series = gdf["ndvi"].dropna()
        ndbi_series = gdf["ndbi"].dropna()
        ndwi_series = gdf["ndwi"].dropna()
        bld_series = gdf["building_density"].dropna()
        road_series = gdf["road_density"].dropna()
        risk_series = gdf["heat_risk"]

        risk_counts = risk_series.value_counts().to_dict()

        return {
            "city": "Pune",
            "sample_size": len(gdf),
            "data_source": "Phase 1 Master Dataset (100m Grid)",
            "mean_lst_celsius": round(float(lst_series.mean()), 2) if len(lst_series) > 0 else None,
            "max_lst_celsius": round(float(lst_series.max()), 2) if len(lst_series) > 0 else None,
            "min_lst_celsius": round(float(lst_series.min()), 2) if len(lst_series) > 0 else None,
            "mean_ndvi": round(float(ndvi_series.mean()), 3) if len(ndvi_series) > 0 else None,
            "mean_ndbi": round(float(ndbi_series.mean()), 3) if len(ndbi_series) > 0 else None,
            "mean_ndwi": round(float(ndwi_series.mean()), 3) if len(ndwi_series) > 0 else None,
            "mean_building_density": round(float(bld_series.mean()), 3) if len(bld_series) > 0 else None,
            "mean_road_density": round(float(road_series.mean()), 3) if len(road_series) > 0 else None,
            "high_risk_cells_count": int(risk_counts.get("High", 0)),
            "extreme_risk_cells_count": int(risk_counts.get("Extreme", 0)),
            "risk_distribution": {
                "Low": int(risk_counts.get("Low", 0)),
                "Medium": int(risk_counts.get("Medium", 0)),
                "High": int(risk_counts.get("High", 0)),
                "Extreme": int(risk_counts.get("Extreme", 0)),
            }
        }

    def get_metadata(self) -> Dict[str, Any]:
        """Returns processing lineage and validation report metadata."""
        if not self.validation_report_path.exists():
            return {
                "status": "Notice",
                "message": "Validation report pending execution. Run python scripts/run_phase1_pipeline.py"
            }
        with open(self.validation_report_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_grid_cell_by_id(self, grid_id: str) -> Optional[Dict[str, Any]]:
        """Returns single grid cell features by grid_id."""
        gdf = self.get_gdf()
        cell_match = gdf[gdf["grid_id"] == grid_id]
        if len(cell_match) == 0:
            return None
        return json.loads(cell_match.iloc[0:1].to_json())["features"][0]
