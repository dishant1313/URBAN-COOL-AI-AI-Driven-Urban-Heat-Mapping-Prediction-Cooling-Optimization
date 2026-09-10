from fastapi import APIRouter
from app.schemas.responses import HealthResponse
from app.config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health_status():
    """
    Health Check Endpoint.
    Returns status: ok, service name, and phase indicator.
    """
    return HealthResponse(
        status="ok",
        service="urban-cool-ai-api",
        phase=settings.PHASE
    )
