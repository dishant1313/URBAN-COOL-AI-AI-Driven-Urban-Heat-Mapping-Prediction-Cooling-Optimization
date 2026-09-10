from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class GridCellFeature(BaseModel):
    """
    Standard Geospatial Feature Data Contract Schema for URBAN-COOL AI.
    Phase 0: Some environmental or physical parameters may be None / null.
    """
    grid_id: str = Field(..., description="Unique identifier for the grid cell polygon/point")
    latitude: float = Field(..., description="Grid centroid latitude in EPSG:4326")
    longitude: float = Field(..., description="Grid centroid longitude in EPSG:4326")
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON geometry object")
    
    # Remote Sensing & Thermal Parameters
    lst: Optional[float] = Field(None, description="Land Surface Temperature (°C)")
    ndvi: Optional[float] = Field(None, description="Normalized Difference Vegetation Index (-1 to 1)")
    ndbi: Optional[float] = Field(None, description="Normalized Difference Built-up Index (-1 to 1)")
    ndwi: Optional[float] = Field(None, description="Normalized Difference Water Index (-1 to 1)")
    lulc: Optional[str] = Field(None, description="Land Use Land Cover Category")
    albedo: Optional[float] = Field(None, description="Surface Albedo (0 to 1)")
    
    # Meteorological Parameters
    air_temperature: Optional[float] = Field(None, description="Near-surface Air Temperature (°C)")
    humidity: Optional[float] = Field(None, description="Relative Humidity (%)")
    wind_speed: Optional[float] = Field(None, description="Wind Speed (m/s)")
    
    # Built Environment & Socioeconomic Parameters
    building_density: Optional[float] = Field(None, description="Building Footprint Density (0 to 1)")
    road_density: Optional[float] = Field(None, description="Road Network Density (0 to 1)")
    population_density: Optional[float] = Field(None, description="Population Density (people/km²)")
    
    # Risk & Intelligence
    heat_risk: Optional[str] = Field(None, description="Assessed Heat Risk Category (Low, Medium, High, Extreme)")

    class Config:
        json_schema_extra = {
            "example": {
                "grid_id": "PUNE_GRID_001",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "lst": 41.8,
                "ndvi": 0.12,
                "ndbi": 0.48,
                "ndwi": -0.25,
                "lulc": "Built-up",
                "albedo": 0.14,
                "air_temperature": 36.2,
                "humidity": 42.0,
                "wind_speed": 2.1,
                "building_density": 0.85,
                "road_density": 0.65,
                "population_density": 18500,
                "heat_risk": "Extreme"
            }
        }


class StudyAreaConfig(BaseModel):
    """Configuration structure for a supported study area."""
    city: str
    country: str
    bbox: Optional[list[float]] = Field(None, description="[min_lon, min_lat, max_lon, max_lat]")
    grid_resolution_m: int = Field(100, description="Spatial resolution in meters")
    crs: str = Field("EPSG:4326", description="API Output CRS")
    projected_crs: str = Field("EPSG:32643", description="Local metric projected CRS for analysis")
    status: str = Field("Active", description="Support status")
