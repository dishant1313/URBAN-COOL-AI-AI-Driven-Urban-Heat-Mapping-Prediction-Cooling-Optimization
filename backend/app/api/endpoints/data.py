from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.data_service import DataService

router = APIRouter(prefix="/data", tags=["Phase 1 Real Geospatial Data"])
data_service = DataService()


@router.get("/heatmap", response_model=Dict[str, Any], summary="Get spatial GeoJSON heatmap grid")
def get_heatmap(
    bbox: Optional[str] = Query(None, description="Bounding box min_lon,min_lat,max_lon,max_lat"),
    layer: str = Query("lst", description="Active layer metric (lst, ndvi, ndbi, ndwi, building_density, road_density)"),
    limit: int = Query(500, description="Max grid cells to return for fast web rendering"),
    min_lst: Optional[float] = Query(None, description="Minimum LST threshold (°C)"),
    max_lst: Optional[float] = Query(None, description="Maximum LST threshold (°C)")
):
    """
    Returns spatial GeoJSON FeatureCollection of 100m x 100m grid cells.
    Supports bounding box spatial filtering, layer metric selection, temperature range filters, and result pagination.
    """
    try:
        bbox_list = None
        if bbox:
            bbox_list = [float(x.strip()) for x in bbox.split(",")]
            if len(bbox_list) != 4:
                raise HTTPException(status_code=400, detail="bbox must contain 4 comma-separated float values: min_lon,min_lat,max_lon,max_lat")

        return data_service.get_heatmap_geojson(
            bbox=bbox_list,
            layer=layer,
            limit=limit,
            min_lst=min_lst,
            max_lst=max_lst
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spatial heatmap: {str(e)}")


@router.get("/features", summary="Get paginated list of grid cell feature properties")
def get_features(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    sort_by: str = Query("lst", description="Field to sort by"),
    order: str = Query("desc", description="Sort order: asc or desc")
):
    """Returns paginated grid cell feature table data."""
    try:
        gdf = data_service.get_gdf().copy()
        
        if sort_by in gdf.columns:
            ascending = (order.lower() == "asc")
            gdf = gdf.sort_values(by=sort_by, ascending=ascending)

        total_records = len(gdf)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        sliced_gdf = gdf.iloc[start_idx:end_idx]
        features = sliced_gdf.drop(columns=["geometry"]).to_dict(orient="records")

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": (total_records + page_size - 1) // page_size,
            "sort_by": sort_by,
            "order": order,
            "items": features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", summary="Get aggregate microclimate & morphology statistics")
def get_data_statistics():
    """Returns baseline and risk distribution statistics computed from real processed master dataset."""
    try:
        return data_service.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata", summary="Get sensor lineage, band formulas & validation report")
def get_data_metadata():
    """Returns remote sensing sensor lineage, formulas, spatial resolution, and data validation report."""
    try:
        return data_service.get_metadata()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grid/{grid_id}", summary="Get detailed features for single grid cell")
def get_grid_by_id(grid_id: str):
    """Returns GeoJSON Feature object for a specific grid_id."""
    try:
        cell = data_service.get_grid_cell_by_id(grid_id)
        if not cell:
            raise HTTPException(status_code=404, detail=f"Grid cell '{grid_id}' not found.")
        return cell
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
