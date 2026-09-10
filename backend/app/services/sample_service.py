import os
import json
import geopandas as gpd
from typing import Dict, Any, Optional
from pathlib import Path


class SampleDataService:
    def __init__(self, sample_geojson_path: Optional[str] = None):
        if sample_geojson_path:
            self.sample_path = Path(sample_geojson_path)
        else:
            # Resolve relative to project root
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.sample_path = base_dir / "data" / "sample" / "pune_sample_grid.geojson"

    def get_sample_heatmap_geojson(self) -> Dict[str, Any]:
        """Read and return the raw sample GeoJSON dictionary."""
        if not self.sample_path.exists():
            raise FileNotFoundError(f"Sample data file not found at: {self.sample_path}")
        
        with open(self.sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def get_sample_statistics(self) -> Dict[str, Any]:
        """Compute aggregate thermal and environmental statistics from sample GeoJSON using GeoPandas."""
        if not self.sample_path.exists():
            raise FileNotFoundError(f"Sample data file not found at: {self.sample_path}")

        gdf = gpd.read_file(self.sample_path)
        
        lst_series = gdf["lst"].dropna() if "lst" in gdf.columns else []
        ndvi_series = gdf["ndvi"].dropna() if "ndvi" in gdf.columns else []
        risk_series = gdf["heat_risk"] if "heat_risk" in gdf.columns else []
        
        risk_counts = risk_series.value_counts().to_dict() if len(risk_series) > 0 else {}

        return {
            "city": "Pune",
            "sample_size": len(gdf),
            "data_source": "Prototype / Sample Data (Phase 0)",
            "mean_lst_celsius": round(float(lst_series.mean()), 2) if len(lst_series) > 0 else None,
            "max_lst_celsius": round(float(lst_series.max()), 2) if len(lst_series) > 0 else None,
            "min_lst_celsius": round(float(lst_series.min()), 2) if len(lst_series) > 0 else None,
            "mean_ndvi": round(float(ndvi_series.mean()), 3) if len(ndvi_series) > 0 else None,
            "high_risk_cells_count": int(risk_counts.get("High", 0)),
            "extreme_risk_cells_count": int(risk_counts.get("Extreme", 0)),
            "risk_distribution": {
                "Low": int(risk_counts.get("Low", 0)),
                "Medium": int(risk_counts.get("Medium", 0)),
                "High": int(risk_counts.get("High", 0)),
                "Extreme": int(risk_counts.get("Extreme", 0)),
            }
        }
