from fastapi import APIRouter
from app.schemas.responses import StudyAreaListResponse
from app.schemas.data_contract import StudyAreaConfig

router = APIRouter()


@router.get("/study-area", response_model=StudyAreaListResponse)
def get_study_areas():
    """
    Get configured study area details and available candidate cities.
    Configurable architecture (not hard-coded to Pune alone).
    """
    pune_config = StudyAreaConfig(
        city="Pune",
        country="India",
        bbox=[73.734, 18.452, 73.930, 18.595],
        grid_resolution_m=500,
        crs="EPSG:4326",
        projected_crs="EPSG:32643",
        status="Active (Phase 0 Prototype)"
    )

    mumbai_config = StudyAreaConfig(
        city="Mumbai",
        country="India",
        bbox=[72.77, 18.89, 72.98, 19.27],
        grid_resolution_m=500,
        crs="EPSG:4326",
        projected_crs="EPSG:32643",
        status="Supported in Phase 2"
    )

    delhi_config = StudyAreaConfig(
        city="Delhi NCR",
        country="India",
        bbox=[76.84, 28.40, 77.34, 28.88],
        grid_resolution_m=500,
        crs="EPSG:4326",
        projected_crs="EPSG:32644",
        status="Supported in Phase 2"
    )

    return StudyAreaListResponse(
        active_study_area=pune_config,
        available_cities=[pune_config, mumbai_config, delhi_config]
    )
