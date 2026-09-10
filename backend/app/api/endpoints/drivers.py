from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from app.services.driver_service import DriverService

router = APIRouter(prefix="/drivers", tags=["Phase 3 Driver Analysis"])
driver_service = DriverService()


@router.get("/statistics")
def get_driver_statistics():
    """
    Returns global summary statistics for Phase 3 Urban Heat Driver Analysis:
    - Global feature importances
    - Correlations with LST
    - Dominant driver distribution
    - Disclaimer
    """
    try:
        return driver_service.get_driver_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/importance")
def get_feature_importance():
    """
    Returns global feature importances for the best ML model.
    """
    try:
        return driver_service.get_feature_importance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation")
def get_correlation_matrix():
    """
    Returns correlation matrix between LST and predictors.
    """
    try:
        return driver_service.get_correlation_matrix()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grid/{grid_id}")
def get_grid_cell_driver_explanation(grid_id: str):
    """
    Returns local SHAP driver explanation and top contributing factors for a single 100m grid cell.
    """
    explanation = driver_service.get_grid_cell_shap_explanations(grid_id)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Grid cell '{grid_id}' not found.")
    return explanation


@router.get("/dominant")
def get_dominant_driver_layer(
    limit: int = Query(700, ge=1, le=5000),
    driver: Optional[str] = Query(None, description="Filter by dominant driver (e.g. building_density, ndvi, ndbi)")
):
    """
    Returns GeoJSON layer populated with dominant heat driver attributes.
    """
    try:
        return driver_service.get_dominant_driver_layer(limit=limit, driver_filter=driver)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shap/{grid_id}")
def get_grid_cell_shap_values(grid_id: str):
    """
    Returns raw SHAP values dict for a single grid cell.
    """
    explanation = driver_service.get_grid_cell_shap_explanations(grid_id)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Grid cell '{grid_id}' not found.")
    return {
        "grid_id": grid_id,
        "shap_values": explanation.get("shap_values", {}),
        "dominant_driver": explanation.get("dominant_driver"),
        "dominant_driver_strength": explanation.get("dominant_driver_strength")
    }
