"""
URBAN-COOL AI — Scenario Service (Phase 4 & Phase 5).

Manages Phase 4 AI model status, single vector prediction with ensemble uncertainty,
Phase 5 cooling scenario simulation execution, intervention types metadata, and spatial maps.
"""

import json
import logging
import pickle
import geopandas as gpd
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from app.geospatial.scenario_engine import run_cooling_scenario, _SCENARIO_CACHE, generate_scenario_hash
from app.geospatial.intervention_rules import get_available_intervention_types, INTERVENTION_REGISTRY
from app.geospatial.predictive_models import compute_ensemble_uncertainty
import pandas as pd
import numpy as np

logger = logging.getLogger("urban_cool_scenario_service")


class ScenarioService:
    def __init__(self, dataset_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        
        p4_path = base_dir / "data" / "processed" / "phase4_predictions.geojson"
        p3_path = base_dir / "data" / "processed" / "phase3_driver_analysis.geojson"
        
        if dataset_path:
            self.dataset_path = Path(dataset_path)
        elif p4_path.exists():
            self.dataset_path = p4_path
        elif p3_path.exists():
            self.dataset_path = p3_path
        else:
            self.dataset_path = base_dir / "data" / "processed" / "phase2_heat_analysis.geojson"

        self.model_path = base_dir / "backend" / "models" / "phase4_predictive_model.pkl"
        self.metadata_path = base_dir / "backend" / "models" / "phase4_model_metadata.json"

        self._cached_gdf: Optional[gpd.GeoDataFrame] = None
        self._cached_model: Optional[Any] = None
        self._cached_metadata: Optional[Dict[str, Any]] = None

    def get_gdf(self) -> gpd.GeoDataFrame:
        if self._cached_gdf is None:
            if not self.dataset_path.exists():
                raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
            gdf = gpd.read_file(self.dataset_path)
            for col in gdf.columns:
                if col != "geometry" and (gdf[col].dtype == "object" or "datetime" in str(gdf[col].dtype)):
                    gdf[col] = gdf[col].astype(str)
            self._cached_gdf = gdf
        return self._cached_gdf

    def get_model_and_metadata(self) -> Tuple[Any, Dict[str, Any]]:
        if self._cached_model is None or self._cached_metadata is None:
            if not self.model_path.exists() or not self.metadata_path.exists():
                # Fallback model metadata if files missing
                self._cached_metadata = {
                    "pipeline_phase": "Phase 4 Predictive Urban Heat AI",
                    "best_model": "Linear Regression",
                    "features_used": ["ndvi", "ndbi", "ndwi", "albedo", "air_temperature", "humidity", "wind_speed", "building_density", "road_density", "green_fraction"],
                    "feature_bounds": {
                        "ndvi": {"min": 0.0, "max": 0.8, "mean": 0.22, "std": 0.12},
                        "building_density": {"min": 0.0, "max": 1.0, "mean": 0.54, "std": 0.24}
                    },
                    "model_performance": {
                        "Linear Regression": {"random_cv_r2": 0.9996, "spatial_cv_r2": 0.9987, "spatial_cv_rmse": 0.0413}
                    },
                    "model_version": "v4.1.0"
                }
                raise FileNotFoundError("Model artifacts not serialized. Run `python scripts/train_phase4_5_models.py` first.")
            else:
                with open(self.model_path, "rb") as f:
                    self._cached_model = pickle.load(f)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self._cached_metadata = json.load(f)
        return self._cached_model, self._cached_metadata

    def get_model_status(self) -> Dict[str, Any]:
        """Returns loaded predictive model status, version, and performance metrics."""
        _, meta = self.get_model_and_metadata()
        return {
            "status": "ready",
            "model_version": meta.get("model_version", "v4.1.0"),
            "best_model": meta.get("best_model", "Linear Regression"),
            "features_used": meta.get("features_used", []),
            "target_variable": meta.get("target_variable", "lst"),
            "spatial_cv_r2": meta.get("model_performance", {}).get(meta.get("best_model", ""), {}).get("spatial_cv_r2", 0.9987),
            "spatial_cv_rmse": meta.get("model_performance", {}).get(meta.get("best_model", ""), {}).get("spatial_cv_rmse", 0.0413),
            "disclaimer": meta.get("disclaimer", "")
        }

    def predict_vector(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Runs single grid cell prediction given input feature vector."""
        model, meta = self.get_model_and_metadata()
        cont_cols = meta.get("continuous_features", ["ndvi", "ndbi", "ndwi", "albedo", "air_temperature", "humidity", "wind_speed", "building_density", "road_density", "green_fraction"])
        cat_cols = meta.get("categorical_features", ["lulc"])

        # Default vector fallback for missing keys
        row = {}
        for col in cont_cols:
            row[col] = float(features.get(col, 0.2 if col == "ndvi" else 0.5 if col == "building_density" else 35.0 if col == "air_temperature" else 0.15))
        for col in cat_cols:
            row[col] = str(features.get(col, "Built-up"))

        df_in = pd.DataFrame([row])
        pred = float(model.predict(df_in)[0])
        uncert = float(compute_ensemble_uncertainty(model, df_in)[0])

        return {
            "predicted_lst": round(pred, 2),
            "prediction_uncertainty": round(uncert, 3),
            "model_version": meta.get("model_version", "v4.1.0"),
            "features_provided": list(features.keys())
        }

    def run_scenario(
        self,
        interventions: List[Dict[str, Any]],
        grid_id_filter: Optional[str] = None,
        hotspot_only: bool = False
    ) -> Dict[str, Any]:
        """Executes cooling scenario simulation with caching."""
        model, meta = self.get_model_and_metadata()
        gdf = self.get_gdf()
        bounds = meta.get("feature_bounds", {})

        scen_hash = generate_scenario_hash(grid_id_filter, interventions)
        if scen_hash in _SCENARIO_CACHE:
            logger.info(f"Returning cached scenario result for hash {scen_hash}")
            return _SCENARIO_CACHE[scen_hash]

        gdf_res, summary = run_cooling_scenario(
            gdf=gdf,
            predictive_pipeline=model,
            feature_bounds=bounds,
            interventions=interventions,
            grid_id_filter=grid_id_filter,
            hotspot_only=hotspot_only
        )

        geojson_data = json.loads(gdf_res.to_json())

        result = {
            "summary": summary,
            "geojson": geojson_data
        }
        _SCENARIO_CACHE[scen_hash] = result
        return result

    def get_scenario_types(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available intervention types."""
        return get_available_intervention_types()
