from fastapi import APIRouter
from app.schemas.responses import LayerListResponse, LayerMetadata

router = APIRouter()


@router.get("/layers", response_model=LayerListResponse)
def get_map_layers():
    """
    Get metadata for active geospatial layers for visualization.
    """
    layers = [
        LayerMetadata(
            id="lst",
            name="Land Surface Temperature (LST)",
            description="Thermal infrared surface temperature (°C)",
            type="continuous",
            legend={"unit": "°C", "min": 30.0, "max": 45.0, "palette": ["#22c55e", "#eab308", "#f97316", "#ef4444"]},
            active=True
        ),
        LayerMetadata(
            id="heat_risk",
            name="Heat Stress Risk Index",
            description="Categorical risk rating based on LST, NDVI & NDBI",
            type="categorical",
            legend={
                "categories": [
                    {"label": "Low Risk", "color": "#22c55e"},
                    {"label": "Medium Risk", "color": "#eab308"},
                    {"label": "High Risk", "color": "#f97316"},
                    {"label": "Extreme Risk", "color": "#ef4444"}
                ]
            },
            active=True
        ),
        LayerMetadata(
            id="ndvi",
            name="Vegetation Index (NDVI)",
            description="Normalized Difference Vegetation Index",
            type="continuous",
            legend={"unit": "Index (-1 to 1)", "min": -0.2, "max": 0.8, "palette": ["#ca8a04", "#84cc16", "#16a34a", "#15803d"]},
            active=False
        ),
        LayerMetadata(
            id="ndbi",
            name="Built-up Index (NDBI)",
            description="Normalized Difference Built-up Index",
            type="continuous",
            legend={"unit": "Index (-1 to 1)", "min": -0.3, "max": 0.6, "palette": ["#38bdf8", "#fbbf24", "#ea580c"]},
            active=False
        )
    ]

    return LayerListResponse(
        study_area="Pune",
        layers=layers
    )
