from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .data_contract import StudyAreaConfig


class HealthResponse(BaseModel):
    status: str
    service: str
    phase: str


class StudyAreaListResponse(BaseModel):
    active_study_area: StudyAreaConfig
    available_cities: List[StudyAreaConfig]


class LayerMetadata(BaseModel):
    id: str
    name: str
    description: str
    type: str
    legend: Dict[str, Any]
    active: bool


class LayerListResponse(BaseModel):
    study_area: str
    layers: List[LayerMetadata]


class HeatmapStatisticsResponse(BaseModel):
    city: str
    sample_size: int
    data_source: str
    mean_lst_celsius: Optional[float]
    max_lst_celsius: Optional[float]
    min_lst_celsius: Optional[float]
    mean_ndvi: Optional[float]
    high_risk_cells_count: int
    extreme_risk_cells_count: int
    risk_distribution: Dict[str, int]
