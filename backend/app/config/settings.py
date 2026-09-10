import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "URBAN-COOL AI API"
    VERSION: str = "0.1.0"
    PHASE: str = "phase-0"
    API_PREFIX: str = "/api"
    
    # Environment & Host
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,https://urban-cool-ai.vercel.app"
    )
    
    @property
    def cors_origins(self) -> List[str]:
        if not self.CORS_ORIGINS_RAW:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # GEE Configuration (Phase 1 placeholders)
    GEE_PROJECT_ID: str = os.getenv("GEE_PROJECT_ID", "")
    GEE_SERVICE_ACCOUNT: str = os.getenv("GEE_SERVICE_ACCOUNT", "")
    GEE_PRIVATE_KEY: str = os.getenv("GEE_PRIVATE_KEY", "")

    # Default Study Area Config
    DEFAULT_STUDY_AREA: str = "Pune"

    class Config:
        case_sensitive = True


settings = Settings()
