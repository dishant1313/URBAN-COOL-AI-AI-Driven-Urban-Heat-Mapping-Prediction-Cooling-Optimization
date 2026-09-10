from fastapi import APIRouter
from app.api.endpoints import health, study_area, layers, sample, data, heat, drivers, models, predict, scenarios

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(study_area.router, tags=["Study Area"])
api_router.include_router(layers.router, tags=["Layers"])
api_router.include_router(sample.router, tags=["Sample Data"])
api_router.include_router(data.router, tags=["Phase 1 Real Data"])
api_router.include_router(heat.router, tags=["Phase 2 Heat Analysis"])
api_router.include_router(drivers.router, tags=["Phase 3 Driver Analysis"])
api_router.include_router(models.router, tags=["Phase 3 ML Models"])
api_router.include_router(predict.router, prefix="/predict", tags=["Phase 4 Prediction"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Phase 5 Scenario Simulator"])



