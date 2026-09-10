from fastapi import APIRouter, HTTPException
from app.services.sample_service import SampleDataService
from app.schemas.responses import HeatmapStatisticsResponse

router = APIRouter()
sample_service = SampleDataService()


@router.get("/sample/heatmap")
def get_sample_heatmap():
    """
    Returns valid GeoJSON containing sample urban heat grid cells for demonstration.
    Explicitly labeled as Phase 0 Prototype Data.
    """
    try:
        return sample_service.get_sample_heatmap_geojson()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading sample heatmap: {str(e)}")


@router.get("/sample/statistics", response_model=HeatmapStatisticsResponse)
def get_sample_statistics():
    """
    Returns aggregate baseline statistics for the sample heat grid area.
    """
    try:
        stats = sample_service.get_sample_statistics()
        return HeatmapStatisticsResponse(**stats)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing sample statistics: {str(e)}")
