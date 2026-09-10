"""
URBAN-COOL AI — Phase 5 Scenario Simulation API Endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.scenario_service import ScenarioService

router = APIRouter()
_scenario_service = ScenarioService()


class InterventionSpec(BaseModel):
    type: str = Field(..., example="tree_cover")
    intensity: float = Field(..., ge=0.01, le=1.0, example=0.20)


class ScenarioRunRequest(BaseModel):
    interventions: List[InterventionSpec]
    grid_id: Optional[str] = Field(None, example="PUNE_GRID_100M_0001")
    hotspot_only: Optional[bool] = Field(False)


@router.get("/types")
def get_scenario_types():
    """Returns available cooling intervention types, intensity bounds, and affected features."""
    return _scenario_service.get_scenario_types()


@router.post("/run")
def run_scenario_simulation(payload: ScenarioRunRequest):
    """Runs single or multi-intervention cooling scenario simulation."""
    try:
        interventions_dict = [item.model_dump() for item in payload.interventions]
        result = _scenario_service.run_scenario(
            interventions=interventions_dict,
            grid_id_filter=payload.grid_id,
            hotspot_only=payload.hotspot_only
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map")
def get_scenario_map(
    intervention: str = Query("tree_cover", description="Intervention type"),
    intensity: float = Query(0.20, ge=0.01, le=1.0, description="Intervention intensity"),
    limit: int = Query(700, ge=1, le=5000, description="Max cells to return")
):
    """Returns GeoJSON spatial layer for a simulated cooling scenario."""
    try:
        interventions = [{"type": intervention, "intensity": intensity}]
        res = _scenario_service.run_scenario(interventions=interventions)
        geojson = res["geojson"]
        if "features" in geojson and len(geojson["features"]) > limit:
            geojson["features"] = geojson["features"][:limit]
        return geojson
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
def get_scenario_statistics(
    intervention: str = Query("tree_cover"),
    intensity: float = Query(0.20)
):
    """Returns summary statistics for a simulated scenario."""
    try:
        interventions = [{"type": intervention, "intensity": intensity}]
        res = _scenario_service.run_scenario(interventions=interventions)
        return res["summary"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scenario_id}")
def get_scenario_by_id(scenario_id: str):
    """Returns cached scenario simulation details by scenario hash ID."""
    from app.geospatial.scenario_engine import _SCENARIO_CACHE
    if scenario_id in _SCENARIO_CACHE:
        return _SCENARIO_CACHE[scenario_id]
    raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found in cache. Run simulation first.")
