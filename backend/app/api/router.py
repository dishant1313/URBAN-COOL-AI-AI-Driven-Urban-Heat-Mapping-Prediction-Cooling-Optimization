from fastapi import APIRouter
from app.api.endpoints import health, study_area, layers, sample, data, heat

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(study_area.router, tags=["Study Area"])
api_router.include_router(layers.router, tags=["Layers"])
api_router.include_router(sample.router, tags=["Sample Data"])
api_router.include_router(data.router, tags=["Phase 1 Real Data"])
api_router.include_router(heat.router, tags=["Phase 2 Heat Analysis"])

