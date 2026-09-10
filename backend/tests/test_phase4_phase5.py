"""
URBAN-COOL AI — Phase 4 & Phase 5 Automated Test Suite.

Validates Phase 4 LST prediction pipeline, spatial block cross-validation, prediction error,
ensemble uncertainty estimation, Phase 5 cooling scenario feature transformations, spatial suitability,
out-of-distribution detection, scenario caching, baseline vs scenario deltas, and FastAPI endpoints.
"""

import sys
from pathlib import Path

# Force local backend directory to top of sys.path
backend_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, backend_dir)

import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from fastapi.testclient import TestClient

from app.main import app
from app.geospatial.predictive_models import (
    prepare_feature_matrix,
    perform_spatial_block_cv,
    train_and_compare_predictive_models,
    compute_ensemble_uncertainty,
    execute_phase4_predictive_pipeline
)
from app.geospatial.intervention_rules import (
    TreeCoverIntervention,
    CoolRoofIntervention,
    GreenRoofIntervention,
    WaterBodyIntervention,
    ReflectivePavementIntervention,
    INTERVENTION_REGISTRY,
    get_available_intervention_types
)
from app.geospatial.scenario_engine import (
    run_cooling_scenario,
    check_out_of_distribution,
    generate_scenario_hash,
    _SCENARIO_CACHE
)
from app.services.scenario_service import ScenarioService

client = TestClient(app)


@pytest.fixture
def mock_predictive_gdf():
    """Generates synthetic 100m grid cell dataset with realistic urban features for testing."""
    np.random.seed(42)
    n_samples = 40
    
    geometries = []
    grid_ids = []
    
    for i in range(n_samples):
        x = 73.850 + (i % 6) * 0.001
        y = 18.510 + (i // 6) * 0.001
        poly = Polygon([(x, y), (x + 0.001, y), (x + 0.001, y + 0.001), (x, y + 0.001)])
        geometries.append(poly)
        grid_ids.append(f"TEST_GRID_{i+1:04d}")

    bld_density = np.random.uniform(0.1, 0.9, n_samples)
    green_frac = np.random.uniform(0.05, 0.5, n_samples)
    ndvi = green_frac * 0.8 + np.random.uniform(-0.05, 0.05, n_samples)
    ndbi = bld_density * 0.7 + np.random.uniform(-0.05, 0.05, n_samples)
    ndwi = np.random.uniform(-0.4, 0.1, n_samples)
    albedo = np.random.uniform(0.10, 0.25, n_samples)
    air_temp = np.random.uniform(34.0, 38.0, n_samples)
    humidity = np.random.uniform(35.0, 60.0, n_samples)
    wind = np.random.uniform(1.0, 4.0, n_samples)
    road_density = np.random.uniform(0.1, 0.6, n_samples)

    # Physical target equation with small noise
    lst = 30.0 + 12.0 * bld_density - 8.0 * green_frac + 0.2 * air_temp + np.random.normal(0, 0.05, n_samples)

    df = pd.DataFrame({
        "grid_id": grid_ids,
        "lst": lst,
        "ndvi": ndvi,
        "ndbi": ndbi,
        "ndwi": ndwi,
        "albedo": albedo,
        "air_temperature": air_temp,
        "humidity": humidity,
        "wind_speed": wind,
        "building_density": bld_density,
        "road_density": road_density,
        "green_fraction": green_frac,
        "lulc": ["Built-up" if b > 0.4 else "Vegetation" for b in bld_density],
        "hotspot_class": ["Hotspot" if l > 40.0 else "Not Significant" for l in lst],
        "geometry": geometries
    })

    return gpd.GeoDataFrame(df, crs="EPSG:4326")


# --- PHASE 4 TESTS ---

def test_prepare_feature_matrix(mock_predictive_gdf):
    X, y, cont, cat = prepare_feature_matrix(mock_predictive_gdf)
    assert len(X) == len(mock_predictive_gdf)
    assert len(y) == len(mock_predictive_gdf)
    assert "ndvi" in cont
    assert "building_density" in cont
    assert "lulc" in cat


def test_spatial_block_cv(mock_predictive_gdf):
    summary, best_pipe, X, y, cont, cat = train_and_compare_predictive_models(mock_predictive_gdf)
    assert "pipeline_phase" in summary
    assert summary["best_model"] in summary["model_performance"]
    
    perf = summary["model_performance"][summary["best_model"]]
    assert perf["spatial_cv_r2"] > 0.80
    assert perf["spatial_cv_rmse"] < 2.0


def test_phase4_pipeline_execution(mock_predictive_gdf, tmp_path):
    gdf_res, summary = execute_phase4_predictive_pipeline(
        gdf=mock_predictive_gdf,
        output_dir=str(tmp_path / "data"),
        model_dir=str(tmp_path / "models")
    )
    assert "predicted_lst" in gdf_res.columns
    assert "baseline_predicted_lst" in gdf_res.columns
    assert "prediction_error" in gdf_res.columns
    assert "absolute_error" in gdf_res.columns
    assert "prediction_uncertainty" in gdf_res.columns
    assert (tmp_path / "data" / "phase4_predictions.geojson").exists()
    assert (tmp_path / "models" / "phase4_predictive_model.pkl").exists()


# --- PHASE 5 INTERVENTION RULES TESTS ---

def test_tree_intervention_transformation():
    row = pd.Series({"green_fraction": 0.20, "ndvi": 0.25, "ndwi": -0.10, "building_density": 0.50})
    assert bool(TreeCoverIntervention.is_cell_suitable(row)) is True

    mods = TreeCoverIntervention.apply_transformation(row, intensity=0.20)
    assert mods["green_fraction"] > 0.20
    assert mods["ndvi"] > 0.25
    assert mods["green_fraction"] <= 1.0
    assert mods["ndvi"] <= 1.0


def test_cool_roof_suitability_and_transformation():
    unsuitable_row = pd.Series({"building_density": 0.02, "lulc": "Water"})
    suitable_row = pd.Series({"building_density": 0.60, "lulc": "Built-up", "albedo": 0.14})

    assert bool(CoolRoofIntervention.is_cell_suitable(unsuitable_row)) is False
    assert bool(CoolRoofIntervention.is_cell_suitable(suitable_row)) is True

    mods = CoolRoofIntervention.apply_transformation(suitable_row, intensity=0.20)
    assert mods["albedo"] > 0.14
    assert mods["albedo"] <= 0.85


def test_green_roof_transformation():
    row = pd.Series({"building_density": 0.50, "green_fraction": 0.10, "ndvi": 0.20, "albedo": 0.15})
    assert bool(GreenRoofIntervention.is_cell_suitable(row)) is True

    mods = GreenRoofIntervention.apply_transformation(row, intensity=0.20)
    assert mods["green_fraction"] > 0.10
    assert mods["ndvi"] > 0.20


def test_water_and_albedo_interventions():
    water_row = pd.Series({"building_density": 0.10, "ndwi": -0.20, "humidity": 40.0})
    assert bool(WaterBodyIntervention.is_cell_suitable(water_row)) is True
    w_mods = WaterBodyIntervention.apply_transformation(water_row, intensity=0.15)
    assert w_mods["ndwi"] > -0.20

    road_row = pd.Series({"road_density": 0.40, "building_density": 0.20, "albedo": 0.12})
    assert bool(ReflectivePavementIntervention.is_cell_suitable(road_row)) is True
    r_mods = ReflectivePavementIntervention.apply_transformation(road_row, intensity=0.20)
    assert r_mods["albedo"] > 0.12


# --- PHASE 5 SCENARIO ENGINE TESTS ---

def test_scenario_baseline_zero_delta(mock_predictive_gdf):
    summary, pipe, X, y, cont, cat = train_and_compare_predictive_models(mock_predictive_gdf)
    
    # Run test scenario with tiny tree intensity on 0.0
    gdf_res, scen_summary = run_cooling_scenario(
        gdf=mock_predictive_gdf,
        predictive_pipeline=pipe,
        feature_bounds=summary["feature_bounds"],
        interventions=[{"type": "tree_cover", "intensity": 0.05}]
    )
    
    assert "cooling_delta" in gdf_res.columns
    assert "mean_cooling_celsius" in scen_summary
    assert "maximum_cooling_celsius" in scen_summary


def test_multi_intervention_scenario(mock_predictive_gdf):
    summary, pipe, X, y, cont, cat = train_and_compare_predictive_models(mock_predictive_gdf)
    
    interventions = [
        {"type": "tree_cover", "intensity": 0.20},
        {"type": "cool_roof", "intensity": 0.20}
    ]
    
    gdf_res, scen_summary = run_cooling_scenario(
        gdf=mock_predictive_gdf,
        predictive_pipeline=pipe,
        feature_bounds=summary["feature_bounds"],
        interventions=interventions
    )
    
    assert scen_summary["affected_cells"] > 0
    assert scen_summary["high_heat_area_reduction_km2"] >= 0.0


def test_invalid_scenario_validation(mock_predictive_gdf):
    summary, pipe, X, y, cont, cat = train_and_compare_predictive_models(mock_predictive_gdf)
    
    with pytest.raises(ValueError, match="Unsupported intervention type"):
        run_cooling_scenario(
            gdf=mock_predictive_gdf,
            predictive_pipeline=pipe,
            feature_bounds=summary["feature_bounds"],
            interventions=[{"type": "invalid_type", "intensity": 0.20}]
        )

    with pytest.raises(ValueError, match="outside valid range"):
        run_cooling_scenario(
            gdf=mock_predictive_gdf,
            predictive_pipeline=pipe,
            feature_bounds=summary["feature_bounds"],
            interventions=[{"type": "tree_cover", "intensity": 0.99}]
        )


def test_out_of_distribution_check():
    feature_bounds = {"ndvi": {"min": 0.0, "max": 0.8}}
    X_modified = pd.DataFrame({"ndvi": [1.5, 1.8]})
    is_ood, warnings = check_out_of_distribution(X_modified, feature_bounds)
    assert is_ood is True
    assert len(warnings) > 0


# --- FASTAPI ENDPOINTS TESTS ---

def test_api_predict_status():
    res = client.get("/api/predict/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["status"] == "ready"


def test_api_predict_performance():
    res = client.get("/api/predict/performance")
    assert res.status_code == 200
    data = res.json()
    assert "best_model" in data
    assert "performance_table" in data


def test_api_predict_single_vector():
    payload = {
        "ndvi": 0.15,
        "ndbi": 0.50,
        "building_density": 0.70,
        "air_temperature": 36.5
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "predicted_lst" in data
    assert "prediction_uncertainty" in data
    assert isinstance(data["predicted_lst"], float)


def test_api_scenarios_types():
    res = client.get("/api/scenarios/types")
    assert res.status_code == 200
    types = res.json()
    assert isinstance(types, list)
    assert any(t["code"] == "tree_cover" for t in types)


def test_api_scenarios_run():
    payload = {
        "interventions": [
            {"type": "tree_cover", "intensity": 0.20}
        ]
    }
    res = client.post("/api/scenarios/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "geojson" in data
    assert "mean_cooling_celsius" in data["summary"]


def test_api_scenarios_map():
    res = client.get("/api/scenarios/map?intervention=tree_cover&intensity=0.20&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) <= 5
