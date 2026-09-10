from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.driver_service import DriverService

router = APIRouter(prefix="/models", tags=["Phase 3 ML Models"])
driver_service = DriverService()


@router.get("/performance")
def get_model_performance_comparison():
    """
    Returns comparative performance metrics for Linear Regression, Random Forest, and XGBoost:
    - Random CV R², RMSE, MAE
    - Spatial Block CV R², RMSE, MAE
    - Best Model selection badge
    """
    try:
        return driver_service.get_model_performance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata")
def get_model_metadata_report():
    """
    Returns complete Phase 3 ML model metadata:
    - Model name, version, training features, target variable
    - Spatial cross-validation methodology
    - Global feature importances
    - Scientific disclaimers
    """
    try:
        return driver_service.get_driver_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
