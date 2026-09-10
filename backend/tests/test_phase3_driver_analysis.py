"""
URBAN-COOL AI — Phase 3 Backend Test Suite.

Tests feature matrix preparation, model training, spatial block cross-validation,
global feature importance, SHAP explanations, dominant drivers, edge cases,
and FastAPI endpoint integrations for Phase 3.
"""

import pytest
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.geospatial.driver_analysis import (
    prepare_feature_matrix,
    build_preprocessing_pipeline,
    perform_spatial_block_cv,
    train_and_evaluate_models,
    compute_global_feature_importance,
    compute_shap_explanations,
    execute_phase3_driver_pipeline,
    CONTINUOUS_PREDICTORS,
    CATEGORICAL_PREDICTORS,
    TARGET_VARIABLE
)

client = TestClient(app)


@pytest.fixture
def sample_gdf():
    """Generates a synthetic GeoDataFrame representing 25 grid cells with realistic microclimate features."""
    cells = []
    np.random.seed(42)
    for i in range(5):
        for j in range(5):
            min_x = 73.850 + i * 0.001
            min_y = 18.510 + j * 0.001
            poly = Polygon([
                (min_x, min_y),
                (min_x + 0.001, min_y),
                (min_x + 0.001, min_y + 0.001),
                (min_x, min_y + 0.001),
                (min_x, min_y)
            ])
            
            bld_density = float(np.random.uniform(0.1, 0.9))
            lst_val = float(35.0 + 10.0 * bld_density + np.random.normal(0, 0.2))

            cells.append({
                "grid_id": f"PUNE_GRID_100M_{i*5+j+1:04d}",
                "geometry": poly,
                "lst": round(lst_val, 2),
                "ndvi": round(float(0.5 - 0.4 * bld_density), 3),
                "ndbi": round(float(bld_density * 0.6), 3),
                "ndwi": -0.2,
                "albedo": 0.15,
                "air_temperature": round(32.0 + 4.0 * bld_density, 2),
                "humidity": 45.0,
                "wind_speed": 2.5,
                "building_density": round(bld_density, 3),
                "road_density": round(bld_density * 0.5, 3),
                "green_fraction": round(float(0.5 - 0.4 * bld_density), 3),
                "lulc": "Built-up" if bld_density > 0.4 else "Vegetation"
            })

    return gpd.GeoDataFrame(cells, crs="EPSG:4326")


def test_prepare_feature_matrix(sample_gdf):
    """Test feature matrix extraction and missing value handling."""
    X, y, cont_cols, cat_cols = prepare_feature_matrix(sample_gdf)
    assert len(X) == 25
    assert len(y) == 25
    assert "building_density" in cont_cols
    assert "lulc" in cat_cols
    assert y.name == "lst"


def test_prepare_feature_matrix_missing_target(sample_gdf):
    """Test ValueError raised if target variable is missing."""
    df_no_target = sample_gdf.drop(columns=["lst"])
    with pytest.raises(ValueError, match="Target variable 'lst' not found"):
        prepare_feature_matrix(df_no_target)


def test_preprocessing_pipeline(sample_gdf):
    """Test ColumnTransformer scaling and One-Hot Encoding."""
    X, y, cont_cols, cat_cols = prepare_feature_matrix(sample_gdf)
    preprocessor = build_preprocessing_pipeline(cont_cols, cat_cols)
    X_trans = preprocessor.fit_transform(X)
    assert X_trans.shape[0] == 25
    assert X_trans.shape[1] >= len(cont_cols) + 1  # Continuous + encoded categories


def test_spatial_block_cv(sample_gdf):
    """Test spatial block cross-validation metrics computation."""
    summary, best_pipeline, X, y, cont_cols, cat_cols = train_and_evaluate_models(sample_gdf)
    metrics = perform_spatial_block_cv(sample_gdf, X, y, best_pipeline, n_blocks_side=2)
    assert "spatial_cv_r2" in metrics
    assert "spatial_cv_rmse" in metrics
    assert "spatial_cv_mae" in metrics
    assert metrics["spatial_cv_r2"] > 0.5  # High spatial R² expected on synthetic clean dataset


def test_train_and_evaluate_models(sample_gdf):
    """Test model comparison (Linear Regression, Random Forest, XGBoost)."""
    summary, best_pipeline, X, y, cont_cols, cat_cols = train_and_evaluate_models(sample_gdf)
    assert "best_model" in summary
    assert summary["best_model"] in ["Linear Regression", "Random Forest", "XGBoost"]
    assert "Linear Regression" in summary["model_performance"]
    assert "Random Forest" in summary["model_performance"]
    assert "XGBoost" in summary["model_performance"]


def test_global_feature_importance(sample_gdf):
    """Test feature importance percentage calculation."""
    summary, best_pipeline, X, y, cont_cols, cat_cols = train_and_evaluate_models(sample_gdf)
    importances = compute_global_feature_importance(best_pipeline, cont_cols, cat_cols)
    assert isinstance(importances, dict)
    assert len(importances) > 0
    total_pct = sum(importances.values())
    assert abs(total_pct - 100.0) < 1.0  # Sums to ~100%


def test_shap_explanations(sample_gdf):
    """Test SHAP matrix and dominant driver attributes calculation."""
    summary, best_pipeline, X, y, cont_cols, cat_cols = train_and_evaluate_models(sample_gdf)
    shap_matrix, feature_names, shap_df = compute_shap_explanations(best_pipeline, X, cont_cols, cat_cols)
    assert shap_matrix.shape[0] == 25
    assert "dominant_driver" in shap_df.columns
    assert "dominant_driver_strength" in shap_df.columns
    assert len(shap_df) == 25


def test_execute_phase3_driver_pipeline(sample_gdf, tmp_path):
    """Test end-to-end Phase 3 driver pipeline execution."""
    output_dir = tmp_path / "processed"
    model_dir = tmp_path / "models"
    gdf_out, summary = execute_phase3_driver_pipeline(sample_gdf, str(output_dir), str(model_dir))
    
    assert "predicted_lst" in gdf_out.columns
    assert "prediction_error" in gdf_out.columns
    assert "dominant_driver" in gdf_out.columns
    assert "shap_building_density" in gdf_out.columns
    assert (model_dir / "best_model.pkl").exists()
    assert (model_dir / "model_metadata.json").exists()


# --- FASTAPI ENDPOINT INTEGRATION TESTS ---

def test_api_drivers_statistics():
    """Test GET /api/drivers/statistics endpoint."""
    response = client.get("/api/drivers/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "best_model" in data
    assert "global_feature_importance" in data
    assert "disclaimer" in data


def test_api_drivers_importance():
    """Test GET /api/drivers/importance endpoint."""
    response = client.get("/api/drivers/importance")
    assert response.status_code == 200
    data = response.json()
    assert "feature_importance" in data


def test_api_drivers_correlation():
    """Test GET /api/drivers/correlation endpoint."""
    response = client.get("/api/drivers/correlation")
    assert response.status_code == 200
    data = response.json()
    assert "correlations" in data


def test_api_drivers_grid_explanation():
    """Test GET /api/drivers/grid/{grid_id} endpoint."""
    response = client.get("/api/drivers/grid/PUNE_GRID_100M_0001")
    assert response.status_code == 200
    data = response.json()
    assert data["grid_id"] == "PUNE_GRID_100M_0001"
    assert "top_drivers" in data
    assert "disclaimer" in data


def test_api_drivers_grid_not_found():
    """Test GET /api/drivers/grid/{grid_id} 404 for invalid grid ID."""
    response = client.get("/api/drivers/grid/INVALID_GRID_9999")
    assert response.status_code == 404


def test_api_drivers_dominant():
    """Test GET /api/drivers/dominant layer endpoint."""
    response = client.get("/api/drivers/dominant?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0


def test_api_models_performance():
    """Test GET /api/models/performance endpoint."""
    response = client.get("/api/models/performance")
    assert response.status_code == 200
    data = response.json()
    assert "best_model" in data
    assert "performance_table" in data


def test_api_models_metadata():
    """Test GET /api/models/metadata endpoint."""
    response = client.get("/api/models/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "pipeline_phase" in data
