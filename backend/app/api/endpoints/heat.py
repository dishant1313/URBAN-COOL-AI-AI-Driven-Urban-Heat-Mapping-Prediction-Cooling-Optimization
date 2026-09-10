from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from app.services.heat_service import HeatService

router = APIRouter(prefix="/heat", tags=["Phase 2 Heat Analysis"])
heat_service = HeatService()


@router.get("/statistics")
def get_heat_statistics():
    """
    Returns summary statistics for Urban Heat Analysis:
    - Min, Max, Mean, Median, Std, Percentiles (P10..P95)
    - Max Anomaly
    - Hotspot Area (km²), High Risk Area (km²)
    - Hotspot / Risk distributions
    """
    try:
        return heat_service.get_heat_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hotspots")
def get_hotspots(
    bbox: Optional[str] = Query(None, description="Bounding box min_lon,min_lat,max_lon,max_lat"),
    limit: int = Query(600, ge=1, le=5000),
    confidence_min: Optional[str] = Query(None, description="Minimum confidence level filter (e.g. 90%, 95%, 99%)")
):
    """
    Returns spatial Getis-Ord Gi* hotspot GeoJSON features.
    """
    try:
        bbox_list = [float(x) for x in bbox.split(",")] if bbox else None
        return heat_service.get_layer_geojson(
            layer="hotspots",
            bbox=bbox_list,
            limit=limit,
            hotspot_only=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk")
def get_heat_risk_layer(
    risk_level: Optional[str] = Query(None, description="Filter by risk category: Very Low, Low, Moderate, High, Very High"),
    limit: int = Query(600, ge=1, le=5000)
):
    """
    Returns heat-risk classification GeoJSON layer.
    """
    try:
        return heat_service.get_layer_geojson(
            layer="heat_risk",
            limit=limit,
            risk_level=risk_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomaly")
def get_lst_anomaly_layer(
    min_anomaly: Optional[float] = Query(None, description="Minimum thermal anomaly in °C"),
    limit: int = Query(600, ge=1, le=5000)
):
    """
    Returns LST thermal anomaly (°C relative to mean) GeoJSON layer.
    """
    try:
        return heat_service.get_layer_geojson(
            layer="lst_anomaly",
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers")
def list_heat_layers():
    """
    Returns metadata for available Phase 2 heat analysis map layers.
    """
    return heat_service.get_layer_metadata_catalog()


@router.get("/grid/{grid_id}")
def get_grid_cell_details(grid_id: str):
    """
    Returns complete Phase 2 heat indicators and morphology attributes for a single grid cell.
    """
    cell_data = heat_service.get_grid_cell_details(grid_id)
    if not cell_data:
        raise HTTPException(status_code=404, detail=f"Grid cell '{grid_id}' not found.")
    return cell_data


@router.get("/metadata")
def get_heat_metadata():
    """
    Returns Phase 2 processing methodology metadata, thresholds, spatial weights, and disclaimer.
    """
    stats = heat_service.get_heat_statistics()
    return {
        "pipeline_phase": stats.get("pipeline_phase"),
        "spatial_parameters": stats.get("spatial_parameters"),
        "temporal_metadata": stats.get("temporal_metadata"),
        "risk_thresholds": "Percentile-based classification (P20, P40, P60, P80)",
        "disclaimer": stats.get("disclaimer")
    }
