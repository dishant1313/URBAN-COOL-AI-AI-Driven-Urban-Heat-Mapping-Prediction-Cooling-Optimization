import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="URBAN-COOL AI Backend API - Urban Heat Mapping, Prediction & Cooling Optimization",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def read_root():
    """Root Endpoint providing API information and documentation link."""
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "phase": settings.PHASE,
        "docs_url": "/docs",
        "health_check": f"{settings.API_PREFIX}/health",
        "sample_heatmap": f"{settings.API_PREFIX}/sample/heatmap"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development")
    )
