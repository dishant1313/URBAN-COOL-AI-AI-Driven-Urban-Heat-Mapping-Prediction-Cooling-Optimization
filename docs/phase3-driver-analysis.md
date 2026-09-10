# PHASE 3 — URBAN HEAT DRIVER ANALYSIS & EXPLAINABLE AI DOCUMENTATION

## 1. Executive Summary
Phase 3 transitions URBAN-COOL AI from localized hotspot detection (*"Where is it hot?"*) to explainable machine learning driver analysis (*"Why is it hot?"*). The system quantifies the relationships between Land Surface Temperature (LST) and key urban predictors (NDVI, NDBI, NDWI, albedo, air temperature, wind speed, building density, road density, green fraction, and LULC) using validated ML regression models and SHAP (SHapley Additive exPlanations).

---

## 2. Machine Learning Architecture & Spatial CV

### 2.1 Model Selection & Evaluation
Three machine learning model architectures are trained and benchmarked against 100m grid cell samples:
1. **Linear Regression**: Baseline interpretable parametric model.
2. **Random Forest Regressor**: Non-linear ensemble model capturing non-monotonic urban relationships.
3. **XGBoost Regressor**: Gradient-boosted decision tree algorithm.

### 2.2 Spatial Block Cross-Validation (Requirement 11)
Standard random k-fold cross-validation suffers from spatial autocorrelation leakage (adjacent 100m grid cells share microclimate similarities). Phase 3 evaluates model generalization using **3x3 Non-Overlapping Spatial Grid Blocks**:
* The study area is divided into a 3x3 grid of spatial blocks.
* Iteratively, whole spatial blocks are held out as validation folds while remaining blocks are used for training.

**Evaluation Results**:
| Model Architecture | Random CV R² | Random CV RMSE | Spatial Block CV R² | Spatial Block CV RMSE | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear Regression** | **0.9996** | **0.0396 °C** | **0.9987** | **0.0413 °C** | **Selected (Best)** |
| **Random Forest** | 0.9994 | 0.0473 °C | 0.9966 | 0.0615 °C | Benchmark |
| **XGBoost** | 0.9994 | 0.0469 °C | 0.9947 | 0.0707 °C | Benchmark |

---

## 3. Explainable AI & SHAP Attribution

### 3.1 Dominant Driver Identification
For each 100m grid cell, SHAP values quantify how much each predictor shifts the local predicted LST away from the global expected mean LST:
$$\text{LST}_{\text{predicted}} = \mathbb{E}[\text{LST}] + \sum_{i=1}^{M} \phi_i$$
The predictor with the largest absolute SHAP value $|\phi_i|$ is assigned as the **Dominant Heat Driver** for that grid cell.

### 3.2 Global Feature Importance Ranking
1. **Building Footprint Density** (95.85% relative importance weight) — Strongest warming driver (+1.000 correlation with LST).
2. **Wind Speed** (1.70%) — Cooling/ventilation driver.
3. **Atmospheric Air Temp** (0.88%) — Background thermal influence (+0.976 correlation).
4. **Green Canopy Cover / NDVI** (0.48%) — Cooling driver (-0.861 correlation with LST).

---

## 4. FastAPI Endpoints (Phase 3)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/drivers/statistics` | Summary report of Phase 3 training, importances, and SHAP stats. |
| `GET` | `/api/drivers/importance` | Ranked global feature importances for trained models. |
| `GET` | `/api/drivers/correlation` | Predictor-LST Pearson linear correlations. |
| `GET` | `/api/drivers/grid/{grid_id}` | Cell-level SHAP breakdown and top contributing factors for a single grid cell. |
| `GET` | `/api/drivers/dominant` | GeoJSON layer populated with dominant driver labels and SHAP values. |
| `GET` | `/api/models/performance` | Comparative benchmark table across Linear, RF, and XGBoost models. |
| `GET` | `/api/models/metadata` | Metadata and model specification. |

---

## 5. Scientific Transparency & Causality Disclaimer

To maintain scientific rigor:
1. **Correlation**: Quantifies linear statistical association.
2. **Predictive Importance**: Measures utility of features when predicting microclimate LST.
3. **SHAP Contribution**: Quantifies how much each predictor shifts model predictions.
4. **Causality (Not Claimed)**: Model-based explanations do not replace physical micro-meteorological CFD simulations.

**Mandatory Disclaimer**:
> *"These are model-based explanations and should not be interpreted as direct physical causal estimates."*
