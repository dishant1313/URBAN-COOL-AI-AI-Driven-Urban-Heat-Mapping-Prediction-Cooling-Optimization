import pytest
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.geospatial.heat_analysis import (
    validate_and_clean_lst_data,
    compute_lst_percentiles,
    compute_lst_anomalies,
    classify_heat_risk,
    compute_getis_ord_gi_star,
    compute_hotspot_score,
    compute_prototype_thermal_stress_index,
    compute_temporal_persistence,
    compute_spatial_area_metrics,
    execute_phase2_heat_analysis_pipeline,
    HeatRiskConfig
)

client = TestClient(app)


def create_sample_grid_gdf(n_cells: int = 25, lst_values=None):
    """Helper function to build dummy 100m grid GeoDataFrame."""
    polys = []
    ids = []
    lats = []
    lons = []

    # Grid in UTM 43N metric coordinates (e.g. Pune)
    base_x, base_y = 378000.0, 2048000.0
    side = int(np.ceil(np.sqrt(n_cells)))

    count = 0
    for i in range(side):
        for j in range(side):
            if count >= n_cells:
                break
            minx = base_x + j * 100.0
            miny = base_y + i * 100.0
            poly = Polygon([
                [minx, miny],
                [minx + 100.0, miny],
                [minx + 100.0, miny + 100.0],
                [minx, miny + 100.0],
                [minx, miny]
            ])
            polys.append(poly)
            ids.append(f"GRID_{count:04d}")
            lats.append(18.52 + i * 0.001)
            lons.append(73.85 + j * 0.001)
            count += 1

    gdf = gpd.GeoDataFrame({
        "grid_id": ids,
        "latitude": lats,
        "longitude": lons,
        "geometry": polys
    }, crs="EPSG:32643")

    if lst_values is not None:
        gdf["lst"] = lst_values
    else:
        np.random.seed(42)
        gdf["lst"] = np.random.uniform(32.0, 44.0, size=n_cells).round(2)

    gdf["ndvi"] = 0.25
    gdf["ndbi"] = 0.35
    gdf["ndwi"] = -0.15
    gdf["air_temperature"] = 36.0
    gdf["humidity"] = 45.0
    gdf["building_density"] = 0.50
    gdf["road_density"] = 0.30

    return gdf


# =====================================================================
# Unit Tests for Heat Analysis Functions
# =====================================================================

def test_validate_and_clean_lst_data():
    gdf = create_sample_grid_gdf(10)
    gdf.loc[0, "lst"] = np.nan

    gdf_clean, summary = validate_and_clean_lst_data(gdf)

    assert summary["total_cells"] == 10
    assert summary["valid_cells"] == 10
    assert summary["missing_lst"] == 1
    assert summary["min_lst"] is not None
    assert summary["mean_lst"] is not None
    # Verify missing value was NOT replaced with 0
    assert np.isnan(gdf_clean.loc[0, "lst"])


def test_lst_percentiles():
    s = pd.Series([30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 44.0])
    p = compute_lst_percentiles(s)

    assert "P10" in p
    assert "P50" in p
    assert "P90" in p
    assert p["P50"] == 37.0


def test_lst_anomalies_and_zscore():
    gdf = create_sample_grid_gdf(5, lst_values=[30.0, 35.0, 40.0, 45.0, 50.0])
    gdf_res = compute_lst_anomalies(gdf)

    # Mean = 40.0, Std = sqrt(50) = 7.071
    assert gdf_res.loc[2, "lst_anomaly"] == 0.0  # (40 - 40)
    assert gdf_res.loc[0, "lst_anomaly"] == -10.0
    assert gdf_res.loc[4, "lst_anomaly"] == 10.0

    assert round(gdf_res.loc[2, "lst_zscore"], 2) == 0.0
    assert gdf_res.loc[4, "lst_zscore"] > 0.0
    assert gdf_res.loc[0, "lst_zscore"] < 0.0


def test_heat_risk_classification_configurable_thresholds():
    gdf = create_sample_grid_gdf(10, lst_values=[30, 32, 34, 36, 38, 40, 42, 44, 46, 48])
    config = HeatRiskConfig(p_very_low=20.0, p_low=40.0, p_moderate=60.0, p_high=80.0)

    gdf_res = classify_heat_risk(gdf, config=config)

    risk_counts = gdf_res["heat_risk"].value_counts().to_dict()
    assert "Very Low" in risk_counts
    assert "Very High" in risk_counts
    assert "High" in risk_counts


def test_getis_ord_gi_star_spatial_hotspots():
    # Grid of 25 cells with a strong hotspot cluster in top right corner
    lst = [34.0] * 20 + [44.0, 44.5, 45.0, 44.8, 45.2]
    gdf = create_sample_grid_gdf(25, lst_values=lst)

    gdf_res = compute_getis_ord_gi_star(gdf, distance_threshold_m=180.0)

    assert "gi_zscore" in gdf_res.columns
    assert "hotspot_class" in gdf_res.columns
    assert "hotspot_significance" in gdf_res.columns

    # Top right cluster (indices 20..24) should be detected as Hotspots
    assert (gdf_res.iloc[20:]["hotspot_class"] == "Hotspot").any()


def test_hotspot_score_range():
    gdf = create_sample_grid_gdf(10)
    gdf = compute_lst_anomalies(gdf)
    gdf = compute_getis_ord_gi_star(gdf)
    gdf_res = compute_hotspot_score(gdf)

    scores = gdf_res["hotspot_score"]
    assert (scores >= 0.0).all()
    assert (scores <= 1.0).all()


def test_thermal_stress_index():
    gdf = create_sample_grid_gdf(10)
    gdf = compute_lst_anomalies(gdf)
    gdf_res = compute_prototype_thermal_stress_index(gdf)

    tsi = gdf_res["thermal_stress_index"]
    assert (tsi >= 0.0).all()
    assert (tsi <= 1.0).all()


def test_spatial_area_metrics_projected_crs():
    gdf = create_sample_grid_gdf(100) # 100 cells of 100m x 100m = 1 km² total area
    gdf = compute_lst_anomalies(gdf)
    gdf = compute_getis_ord_gi_star(gdf)
    gdf = classify_heat_risk(gdf)

    metrics = compute_spatial_area_metrics(gdf, projected_crs="EPSG:32643")

    assert metrics["total_study_area_km2"] == 1.0
    assert metrics["hotspot_area_km2"] >= 0.0
    assert metrics["high_risk_area_km2"] >= 0.0


# =====================================================================
# Edge Case Tests
# =====================================================================

def test_edge_case_all_lst_values_identical():
    """Zero variance dataset edge case."""
    gdf = create_sample_grid_gdf(10, lst_values=[38.0] * 10)
    gdf_proc, summary = execute_phase2_heat_analysis_pipeline(gdf)

    assert summary["lst_statistics"]["std_lst"] == 0.0
    assert (gdf_proc["lst_zscore"] == 0.0).all()
    assert (gdf_proc["hotspot_class"] == "Not Significant").all()


def test_edge_case_single_cell_dataset():
    """Single cell dataset edge case."""
    gdf = create_sample_grid_gdf(1, lst_values=[40.0])
    gdf_proc, summary = execute_phase2_heat_analysis_pipeline(gdf)

    assert len(gdf_proc) == 1
    assert summary["validation_summary"]["valid_cells"] == 1


def test_edge_case_empty_dataset():
    """Empty dataset edge case."""
    gdf = gpd.GeoDataFrame(columns=["grid_id", "lst", "geometry"], crs="EPSG:4326")
    gdf_proc, summary = execute_phase2_heat_analysis_pipeline(gdf)

    assert len(gdf_proc) == 0
    assert summary["validation_summary"]["total_cells"] == 0


def test_edge_case_invalid_geometries():
    """Invalid geometry dropping edge case."""
    gdf = create_sample_grid_gdf(5)
    # Inject an empty geometry
    gdf.loc[0, "geometry"] = Polygon()

    gdf_clean, summary = validate_and_clean_lst_data(gdf)
    assert summary["total_cells"] == 5
    assert summary["valid_cells"] == 4


# =====================================================================
# Phase 2 FastAPI Endpoints Tests
# =====================================================================

def test_api_heat_statistics():
    res = client.get("/api/heat/statistics")
    assert res.status_code == 200
    data = res.json()
    assert "lst_statistics" in data
    assert "hotspot_statistics" in data
    assert data["pipeline_phase"].startswith("Phase 2")


def test_api_heat_layers():
    res = client.get("/api/heat/layers")
    assert res.status_code == 200
    layers = res.json()
    assert isinstance(layers, list)
    layer_ids = [l["id"] for l in layers]
    assert "lst" in layer_ids
    assert "lst_anomaly" in layer_ids
    assert "hotspots" in layer_ids


def test_api_heat_hotspots():
    res = client.get("/api/heat/hotspots?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"


def test_api_heat_risk():
    res = client.get("/api/heat/risk?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"


def test_api_heat_anomaly():
    res = client.get("/api/heat/anomaly?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"


def test_api_heat_grid_cell():
    # First get stats or sample grid ID
    res = client.get("/api/data/heatmap?limit=1")
    grid_id = res.json()["features"][0]["properties"]["grid_id"]

    res_cell = client.get(f"/api/heat/grid/{grid_id}")
    assert res_cell.status_code == 200
    cell_data = res_cell.json()
    assert cell_data["grid_id"] == grid_id
    assert "lst" in cell_data
    assert "lst_anomaly" in cell_data
    assert "phase3_notice" in cell_data


def test_api_heat_metadata():
    res = client.get("/api/heat/metadata")
    assert res.status_code == 200
    meta = res.json()
    assert "spatial_parameters" in meta
    assert "disclaimer" in meta
