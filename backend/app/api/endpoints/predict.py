"""
URBAN-COOL AI — Phase 4 Prediction API Endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.services.scenario_service import ScenarioService

router = APIRouter()
_scenario_service = ScenarioService()


class FeatureVectorInput(BaseModel):
    ndvi: Optional[float] = Field(0.20, ge=-1.0, le=1.0)
    ndbi: Optional[float] = Field(0.35, ge=-1.0, le=1.0)
    ndwi: Optional[float] = Field(-0.15, ge=-1.0, le=1.0)
    albedo: Optional[float] = Field(0.15, ge=0.0, le=1.0)
    air_temperature: Optional[float] = Field(36.0, ge=10.0, le=60.0)
    humidity: Optional[float] = Field(45.0, ge=0.0, le=100.0)
    wind_speed: Optional[float] = Field(2.5, ge=0.0, le=50.0)
    building_density: Optional[float] = Field(0.50, ge=0.0, le=1.0)
    road_density: Optional[float] = Field(0.30, ge=0.0, le=1.0)
    green_fraction: Optional[float] = Field(0.15, ge=0.0, le=1.0)
    lulc: Optional[str] = Field("Built-up")


@router.get("/status")
def get_model_status():
    """Returns predictive model status, version, and performance metrics."""
    try:
        return _scenario_service.get_model_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
def get_model_performance():
    """Returns model comparison table across candidate architectures."""
    try:
        _, meta = _scenario_service.get_model_and_metadata()
        return {
            "best_model": meta.get("best_model"),
            "performance_table": meta.get("model_performance", {}),
            "features_used": meta.get("features_used", []),
            "disclaimer": meta.get("disclaimer")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
def predict_single_vector(payload: FeatureVectorInput):
    """Predicts LST for a single input feature vector with uncertainty estimation."""
    try:
        features = payload.model_dump(exclude_unset=True)
        return _scenario_service.predict_vector(features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
