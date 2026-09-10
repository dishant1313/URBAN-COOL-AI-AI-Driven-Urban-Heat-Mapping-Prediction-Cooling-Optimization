"""
URBAN-COOL AI — Phase 3 Urban Heat Driver Analysis & Explainable AI.

Implements ML model training, spatial validation, global feature importance,
and SHAP local driver explanations for Land Surface Temperature (LST).
"""

import os
import logging
import json
import joblib
import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import KFold

import shap

logger = logging.getLogger("urban_cool_driver_analysis")

# Define standard feature sets according to Phase 3 specification
CONTINUOUS_PREDICTORS = [
    "ndvi",
    "ndbi",
    "ndwi",
    "albedo",
    "air_temperature",
    "humidity",
    "wind_speed",
    "building_density",
    "road_density",
    "green_fraction",
]

CATEGORICAL_PREDICTORS = ["lulc"]
TARGET_VARIABLE = "lst"


def prepare_feature_matrix(gdf: gpd.GeoDataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str], List[str]]:
    """
    Extracts features and target variable from input GeoDataFrame.
    Handles missing feature columns gracefully without fabricating data.
    """
    df = gdf.copy()

    # Verify target variable exists
    if TARGET_VARIABLE not in df.columns:
        raise ValueError(f"Target variable '{TARGET_VARIABLE}' not found in GeoDataFrame.")

    # Select existing continuous predictors
    available_continuous = [col for col in CONTINUOUS_PREDICTORS if col in df.columns]
    
    # Optional population density if present
    if "population_density" in df.columns and "population_density" not in available_continuous:
        available_continuous.append("population_density")

    # Select existing categorical predictors
    available_categorical = [col for col in CATEGORICAL_PREDICTORS if col in df.columns]

    all_predictors = available_continuous + available_categorical

    # Drop rows where target is missing
    df_clean = df.dropna(subset=[TARGET_VARIABLE]).copy()

    # Fill continuous predictor NaNs with median values (defensive)
    for col in available_continuous:
        if df_clean[col].isna().sum() > 0:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    # Fill categorical predictor NaNs with mode/Unknown
    for col in available_categorical:
        if df_clean[col].isna().sum() > 0:
            df_clean[col] = df_clean[col].fillna("Unknown")

    X = df_clean[all_predictors]
    y = df_clean[TARGET_VARIABLE]

    return X, y, available_continuous, available_categorical


def build_preprocessing_pipeline(continuous_cols: List[str], categorical_cols: List[str]) -> ColumnTransformer:
    """
    Constructs a robust scikit-learn ColumnTransformer:
    - Continuous features: StandardScaler
    - Categorical features: OneHotEncoder (handle_unknown='ignore')
    """
    transformers = []
    
    if continuous_cols:
        transformers.append(("num", StandardScaler(), continuous_cols))
    
    if categorical_cols:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols))

    preprocessor = ColumnTransformer(transformers=transformers)
    return preprocessor


def get_feature_names_from_preprocessor(preprocessor: ColumnTransformer, continuous_cols: List[str], categorical_cols: List[str]) -> List[str]:
    """Retrieves post-transform feature names after One-Hot Encoding."""
    feature_names = list(continuous_cols)
    if categorical_cols and "cat" in preprocessor.named_transformers_:
        cat_encoder = preprocessor.named_transformers_["cat"]
        if hasattr(cat_encoder, "get_feature_names_out"):
            cat_names = list(cat_encoder.get_feature_names_out(categorical_cols))
            feature_names.extend(cat_names)
    return feature_names


def perform_spatial_block_cv(
    gdf: gpd.GeoDataFrame,
    X: pd.DataFrame,
    y: pd.Series,
    model_pipeline: Pipeline,
    n_blocks_side: int = 3
) -> Dict[str, float]:
    """
    Performs spatial block cross-validation by partitioning space into n_blocks_side x n_blocks_side blocks.
    Ensures training blocks and testing blocks do not overlap spatially.
    """
    if "geometry" not in gdf.columns or gdf.geometry.is_empty.all():
        # Fallback to standard 5-fold CV if spatial geometries are missing
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        r2_list, rmse_list, mae_list = [], [], []
        for train_idx, test_idx in kf.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
            model_pipeline.fit(X_tr, y_tr)
            preds = model_pipeline.predict(X_te)
            r2_list.append(r2_score(y_te, preds))
            rmse_list.append(np.sqrt(mean_squared_error(y_te, preds)))
            mae_list.append(mean_absolute_error(y_te, preds))

        return {
            "spatial_cv_r2": round(float(np.mean(r2_list)), 4),
            "spatial_cv_rmse": round(float(np.mean(rmse_list)), 4),
            "spatial_cv_mae": round(float(np.mean(mae_list)), 4),
            "method": "Random KFold (Fallback)"
        }

    # Extract centroids
    centroids = gdf.geometry.centroid
    min_x, min_y, max_x, max_y = gdf.total_bounds
    
    x_step = (max_x - min_x) / n_blocks_side
    y_step = (max_y - min_y) / n_blocks_side

    block_ids = []
    for pt in centroids:
        col_idx = min(int((pt.x - min_x) / x_step), n_blocks_side - 1)
        row_idx = min(int((pt.y - min_y) / y_step), n_blocks_side - 1)
        block_ids.append(row_idx * n_blocks_side + col_idx)

    unique_blocks = np.unique(block_ids)
    r2_list, rmse_list, mae_list = [], [], []

    for block in unique_blocks:
        test_mask = (np.array(block_ids) == block)
        train_mask = ~test_mask

        if np.sum(test_mask) < 2 or np.sum(train_mask) < 2:
            continue

        X_tr, X_te = X[train_mask], X[test_mask]
        y_tr, y_te = y[train_mask], y[test_mask]

        model_pipeline.fit(X_tr, y_tr)
        preds = model_pipeline.predict(X_te)

        r2_list.append(r2_score(y_te, preds))
        rmse_list.append(np.sqrt(mean_squared_error(y_te, preds)))
        mae_list.append(mean_absolute_error(y_te, preds))

    if len(r2_list) == 0:
        return {"spatial_cv_r2": 0.0, "spatial_cv_rmse": 0.0, "spatial_cv_mae": 0.0, "method": "Spatial Blocks"}

    return {
        "spatial_cv_r2": round(float(np.mean(r2_list)), 4),
        "spatial_cv_rmse": round(float(np.mean(rmse_list)), 4),
        "spatial_cv_mae": round(float(np.mean(mae_list)), 4),
        "method": f"{n_blocks_side}x{n_blocks_side} Spatial Grid Blocks"
    }


def train_and_evaluate_models(
    gdf: gpd.GeoDataFrame
) -> Tuple[Dict[str, Any], Pipeline, pd.DataFrame, pd.Series, List[str], List[str]]:
    """
    Trains 3 candidate models:
    1. Multiple Linear Regression (Baseline)
    2. Random Forest Regressor
    3. XGBoost Regressor

    Performs spatial block cross-validation, compares validation metrics, and selects the best model.
    """
    X, y, cont_cols, cat_cols = prepare_feature_matrix(gdf)
    preprocessor = build_preprocessing_pipeline(cont_cols, cat_cols)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.08, max_depth=5, random_state=42, n_jobs=-1)
    }

    results = {}
    best_model_name = None
    best_spatial_r2 = -float("inf")
    best_pipeline = None

    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])

        # Random holdout 80/20 evaluation
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        train_idx, test_idx = next(kf.split(X))
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        r2 = round(float(r2_score(y_test, y_pred)), 4)
        rmse = round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4)
        mae = round(float(mean_absolute_error(y_test, y_pred)), 4)

        # Spatial block CV
        spatial_metrics = perform_spatial_block_cv(gdf.iloc[X.index], X, y, pipeline)

        results[name] = {
            "random_cv_r2": r2,
            "random_cv_rmse": rmse,
            "random_cv_mae": mae,
            "spatial_cv_r2": spatial_metrics["spatial_cv_r2"],
            "spatial_cv_rmse": spatial_metrics["spatial_cv_rmse"],
            "spatial_cv_mae": spatial_metrics["spatial_cv_mae"],
            "spatial_cv_method": spatial_metrics["method"]
        }

        # Model selection based on Spatial CV R²
        if spatial_metrics["spatial_cv_r2"] > best_spatial_r2:
            best_spatial_r2 = spatial_metrics["spatial_cv_r2"]
            best_model_name = name
            best_pipeline = pipeline

    # Refit best pipeline on 100% of data
    best_pipeline.fit(X, y)

    summary = {
        "best_model": best_model_name,
        "model_performance": results,
        "features_used": cont_cols + cat_cols,
        "target_variable": TARGET_VARIABLE
    }

    return summary, best_pipeline, X, y, cont_cols, cat_cols


def compute_global_feature_importance(
    best_pipeline: Pipeline,
    cont_cols: List[str],
    cat_cols: List[str]
) -> Dict[str, float]:
    """Computes global relative feature importances from the trained tree model."""
    preprocessor = best_pipeline.named_steps["preprocessor"]
    regressor = best_pipeline.named_steps["regressor"]

    feature_names = get_feature_names_from_preprocessor(preprocessor, cont_cols, cat_cols)

    if hasattr(regressor, "feature_importances_"):
        importances = regressor.feature_importances_
    elif hasattr(regressor, "coef_"):
        importances = np.abs(regressor.coef_)
    else:
        importances = np.ones(len(feature_names)) / len(feature_names)

    # Sum one-hot categorical feature importances back to raw feature names
    importance_map = {}
    for name, imp in zip(feature_names, importances):
        # Strip categorical prefix if any (e.g. cat__lulc_Built-up -> lulc)
        raw_name = name
        if name.startswith("cat__"):
            raw_name = name.split("__")[1].split("_")[0]
        elif name.startswith("num__"):
            raw_name = name.replace("num__", "")

        importance_map[raw_name] = importance_map.get(raw_name, 0.0) + float(imp)

    # Normalize to percentages summing to 100%
    total_imp = sum(importance_map.values())
    if total_imp > 0:
        importance_pct = {k: round(float(v / total_imp * 100.0), 2) for k, v in importance_map.items()}
    else:
        importance_pct = {k: 0.0 for k in importance_map}

    # Sort descending
    sorted_importance = dict(sorted(importance_pct.items(), key=lambda x: x[1], reverse=True))
    return sorted_importance


def compute_shap_explanations(
    best_pipeline: Pipeline,
    X: pd.DataFrame,
    cont_cols: List[str],
    cat_cols: List[str]
) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    """
    Calculates SHAP values for all grid cells using TreeExplainer.
    Returns:
    - shap_matrix: (N_samples, N_features) numpy array
    - feature_names: list of feature names corresponding to matrix columns
    - shap_df: DataFrame with grid-level shap attributes (shap_ndvi, shap_ndbi, dominant_driver, etc.)
    """
    preprocessor = best_pipeline.named_steps["preprocessor"]
    regressor = best_pipeline.named_steps["regressor"]

    # Transform X to preprocessed numerical matrix
    X_trans = preprocessor.transform(X)
    feature_names = get_feature_names_from_preprocessor(preprocessor, cont_cols, cat_cols)

    # Use SHAP TreeExplainer or Explainer
    try:
        explainer = shap.TreeExplainer(regressor)
        shap_values = explainer.shap_values(X_trans)
    except Exception:
        # Fallback to Kernel/Linear explainer
        explainer = shap.Explainer(regressor.predict, X_trans[:50])
        shap_values = explainer(X_trans).values

    if isinstance(shap_values, list):
        shap_matrix = shap_values[0]
    else:
        shap_matrix = shap_values

    # Aggregate SHAP values per raw predictor
    raw_predictors = cont_cols + cat_cols
    aggregated_shap = np.zeros((len(X), len(raw_predictors)))

    for idx, f_name in enumerate(feature_names):
        target_raw = f_name
        if f_name.startswith("cat__"):
            target_raw = f_name.split("__")[1].split("_")[0]
        elif f_name.startswith("num__"):
            target_raw = f_name.replace("num__", "")

        if target_raw in raw_predictors:
            p_idx = raw_predictors.index(target_raw)
            aggregated_shap[:, p_idx] += shap_matrix[:, idx]

    # Create cell-level SHAP DataFrame
    shap_df = pd.DataFrame(index=X.index)

    # Store individual predictor SHAP values
    for idx, p_name in enumerate(raw_predictors):
        shap_df[f"shap_{p_name}"] = np.round(aggregated_shap[:, idx], 3)

    # Determine dominant driver per cell (predictor with max absolute SHAP contribution)
    abs_shap = np.abs(aggregated_shap)
    dominant_indices = np.argmax(abs_shap, axis=1)

    dominant_drivers = [raw_predictors[i] for i in dominant_indices]
    dominant_strengths = [round(float(aggregated_shap[i, dominant_indices[i]]), 3) for i in range(len(X))]

    shap_df["dominant_driver"] = dominant_drivers
    shap_df["dominant_driver_strength"] = dominant_strengths

    # Map friendly human readable driver names
    driver_labels = {
        "ndvi": "Vegetation Canopy (NDVI)",
        "ndbi": "Built-up Intensity (NDBI)",
        "ndwi": "Water Presence (NDWI)",
        "albedo": "Shortwave Albedo",
        "air_temperature": "Atmospheric Air Temp",
        "humidity": "Relative Humidity",
        "wind_speed": "Wind Speed",
        "building_density": "Building Footprint Density",
        "road_density": "Road Network Density",
        "green_fraction": "Green Cover Fraction",
        "population_density": "Population Density",
        "lulc": "Land Use / Land Cover"
    }
    shap_df["dominant_driver_label"] = [driver_labels.get(d, d) for d in dominant_drivers]

    return shap_matrix, feature_names, shap_df


def execute_phase3_driver_pipeline(
    gdf_input: gpd.GeoDataFrame,
    output_dir: str = "data/processed",
    model_dir: str = "backend/models"
) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
    """
    Executes full Phase 3 Urban Heat Driver Analysis pipeline:
    1. Feature matrix building & missing value check
    2. Candidate models training (Linear Regression, Random Forest, XGBoost)
    3. Spatial block cross-validation & model selection
    4. Global feature importance calculation
    5. SHAP values & dominant heat driver identification
    6. Asset & model metadata export
    """
    logger.info("Executing Phase 3 Driver Analysis Pipeline...")

    # Step 1-3: Model training and evaluation
    summary, best_pipeline, X, y, cont_cols, cat_cols = train_and_evaluate_models(gdf_input)

    # Step 4: Global feature importance
    importance = compute_global_feature_importance(best_pipeline, cont_cols, cat_cols)
    summary["global_feature_importance"] = importance

    # Step 5: SHAP explanations & cell-level attributes
    shap_matrix, feature_names, shap_df = compute_shap_explanations(best_pipeline, X, cont_cols, cat_cols)

    # Merge SHAP attributes into output GeoDataFrame
    gdf_out = gdf_input.copy()
    
    # Store predicted LST and prediction error
    preds = best_pipeline.predict(X)
    gdf_out["predicted_lst"] = np.round(preds, 2)
    gdf_out["prediction_error"] = np.round(gdf_out[TARGET_VARIABLE] - gdf_out["predicted_lst"], 2)

    for col in shap_df.columns:
        gdf_out[col] = shap_df[col]

    # Calculate LST-predictor correlations
    corr_matrix = {}
    for col in cont_cols:
        if col in gdf_out.columns:
            corr_val = gdf_out[[TARGET_VARIABLE, col]].corr().iloc[0, 1]
            corr_matrix[col] = round(float(corr_val), 3) if not np.isnan(corr_val) else 0.0

    summary["correlation_with_lst"] = corr_matrix
    summary["dominant_driver_distribution"] = gdf_out["dominant_driver_label"].value_counts().to_dict()

    # Step 6: Save model artifact & metadata
    os.makedirs(model_dir, exist_ok=True)
    model_path = Path(model_dir) / "best_model.pkl"
    joblib.dump(best_pipeline, model_path)

    metadata_report = {
        "pipeline_phase": "Phase 3 Urban Heat Driver Analysis & Explainable AI",
        "best_model": summary["best_model"],
        "model_performance": summary["model_performance"],
        "features_used": summary["features_used"],
        "target_variable": TARGET_VARIABLE,
        "global_feature_importance": importance,
        "correlation_with_lst": corr_matrix,
        "dominant_driver_distribution": summary["dominant_driver_distribution"],
        "disclaimer": "These are model-based explanations and should not be interpreted as direct physical causal estimates."
    }

    metadata_path = Path(model_dir) / "model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_report, f, indent=2)

    logger.info(f"Phase 3 Pipeline Complete. Best model '{summary['best_model']}' saved to {model_path}.")
    return gdf_out, metadata_report
