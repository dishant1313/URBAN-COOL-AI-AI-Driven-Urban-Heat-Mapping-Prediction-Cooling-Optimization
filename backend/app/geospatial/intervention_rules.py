"""
URBAN-COOL AI — Intervention Rules Framework (Phase 5).

Defines physical feature transformation rules, spatial suitability constraints,
and parameter validation for cooling intervention scenarios (Trees, Cool Roofs,
Green Roofs, Water Bodies, Reflective Albedo).
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd


class BaseInterventionRule:
    """Abstract Base Class for Cooling Interventions."""
    name: str = "Base Intervention"
    code: str = "base"
    description: str = "Base cooling intervention"
    affected_features: List[str] = []
    allowed_intensity_range: Tuple[float, float] = (0.0, 1.0)

    @classmethod
    def is_cell_suitable(cls, row: pd.Series) -> bool:
        """Determines spatial suitability for a single grid cell."""
        return True

    @classmethod
    def apply_transformation(cls, row: pd.Series, intensity: float) -> Dict[str, Any]:
        """Applies physical feature transformation to a single grid cell feature dictionary."""
        return row.to_dict()


class TreeCoverIntervention(BaseInterventionRule):
    name = "Urban Tree Canopy Increase"
    code = "tree_cover"
    description = "Increases urban green canopy cover and vegetation density (NDVI)."
    affected_features = ["green_fraction", "ndvi"]
    allowed_intensity_range = (0.05, 0.50)

    @classmethod
    def is_cell_suitable(cls, row: pd.Series) -> bool:
        # Suitable on non-water areas where green canopy can expand
        ndwi = row.get("ndwi", -0.1)
        bld_density = row.get("building_density", 0.5)
        return ndwi < 0.3 and bld_density < 0.95

    @classmethod
    def apply_transformation(cls, row: pd.Series, intensity: float) -> Dict[str, Any]:
        mods = {}
        curr_green = row.get("green_fraction", 0.2)
        curr_ndvi = row.get("ndvi", 0.25)

        # Documented canopy expansion mapping
        new_green = min(1.0, curr_green + intensity * 0.8)
        new_ndvi = min(1.0, curr_ndvi + intensity * 0.35)

        mods["green_fraction"] = round(float(new_green), 3)
        mods["ndvi"] = round(float(new_ndvi), 3)
        return mods


class CoolRoofIntervention(BaseInterventionRule):
    name = "Cool Roof Albedo Coating"
    code = "cool_roof"
    description = "Applies high-albedo solar-reflective coating to building rooftops."
    affected_features = ["albedo"]
    allowed_intensity_range = (0.05, 0.50)

    @classmethod
    def is_cell_suitable(cls, row: pd.Series) -> bool:
        bld_density = row.get("building_density", 0.0)
        lulc = str(row.get("lulc", "")).lower()
        return bld_density >= 0.10 or "built" in lulc or "urban" in lulc

    @classmethod
    def apply_transformation(cls, row: pd.Series, intensity: float) -> Dict[str, Any]:
        mods = {}
        curr_albedo = row.get("albedo", 0.15)
        bld_density = row.get("building_density", 0.5)

        # Albedo increases proportionally to rooftop area fraction
        target_roof_albedo = 0.65  # High-reflectance cool roof standard
        effective_albedo = curr_albedo + (target_roof_albedo - curr_albedo) * (bld_density * intensity * 1.5)
        
        mods["albedo"] = round(float(min(0.85, max(curr_albedo, effective_albedo))), 3)
        return mods


class GreenRoofIntervention(BaseInterventionRule):
    name = "Green Roof Vegetation Integration"
    code = "green_roof"
    description = "Integrates vegetated rooftop gardens on suitable building structures."
    affected_features = ["green_fraction", "ndvi", "albedo"]
    allowed_intensity_range = (0.05, 0.50)

    @classmethod
    def is_cell_suitable(cls, row: pd.Series) -> bool:
        bld_density = row.get("building_density", 0.0)
        return bld_density >= 0.15

    @classmethod
    def apply_transformation(cls, row: pd.Series, intensity: float) -> Dict[str, Any]:
        mods = {}
        curr_green = row.get("green_fraction", 0.1)
        curr_ndvi = row.get("ndvi", 0.2)
        bld_density = row.get("building_density", 0.5)

        added_veg = bld_density * intensity * 0.6
        mods["green_fraction"] = round(float(min(1.0, curr_green + added_veg)), 3)
        mods["ndvi"] = round(float(min(1.0, curr_ndvi + added_veg * 0.4)), 3)
        mods["albedo"] = round(float(min(0.35, max(0.18, row.get("albedo", 0.15) + added_veg * 0.1))), 3)
        return mods


class WaterBodyIntervention(BaseInterventionRule):
    name = "Urban Water & Wetland Feature Creation"
    code = "water"
    description = "Introduces retention ponds, fountains, or urban wetland features."
    affected_features = ["ndwi", "humidity"]
    allowed_intensity_range = (0.05, 0.30)

    @classmethod
    def is_cell_suitable(cls, row: pd.Series) -> bool:
        bld_density = row.get("building_density", 0.0)
        ndwi = row.get("ndwi", -0.2)
        return bld_density <= 0.40 and ndwi < 0.40

    @classmethod
    def apply_transformation(cls, row: pd.Series, intensity: float) -> Dict[str, Any]:
        mods = {}
        curr_ndwi = row.get("ndwi", -0.2)
        curr_humidity = row.get("humidity", 45.0)

        mods["ndwi"] = round(float(min(1.0, curr_ndwi + intensity * 0.6)), 3)
        mods["humidity"] = round(float(min(100.0, curr_humidity + intensity * 15.0)), 2)
        return mods


class ReflectivePavementIntervention(BaseInterventionRule):
    name = "Cool Reflective Pavements"
    code = "albedo"
    description = "Applies solar reflective sealants to asphalt roads and paved parking lots."
    affected_features = ["albedo"]
    allowed_intensity_range = (0.05, 0.40)

    @classmethod
    def is_cell_suitable(cls, row: pd.Series) -> bool:
        road_density = row.get("road_density", 0.0)
        bld_density = row.get("building_density", 0.0)
        return road_density >= 0.10 or bld_density >= 0.20

    @classmethod
    def apply_transformation(cls, row: pd.Series, intensity: float) -> Dict[str, Any]:
        mods = {}
        curr_albedo = row.get("albedo", 0.14)
        road_density = row.get("road_density", 0.3)

        new_albedo = curr_albedo + (0.45 - curr_albedo) * (max(road_density, 0.2) * intensity * 1.5)
        mods["albedo"] = round(float(min(0.70, max(curr_albedo, new_albedo))), 3)
        return mods


INTERVENTION_REGISTRY: Dict[str, Any] = {
    "tree_cover": TreeCoverIntervention,
    "cool_roof": CoolRoofIntervention,
    "green_roof": GreenRoofIntervention,
    "water": WaterBodyIntervention,
    "albedo": ReflectivePavementIntervention
}


def get_available_intervention_types() -> List[Dict[str, Any]]:
    """Returns metadata for all available intervention types."""
    types_list = []
    for code, rule_cls in INTERVENTION_REGISTRY.items():
        types_list.append({
            "code": rule_cls.code,
            "name": rule_cls.name,
            "description": rule_cls.description,
            "affected_features": rule_cls.affected_features,
            "min_intensity": rule_cls.allowed_intensity_range[0],
            "max_intensity": rule_cls.allowed_intensity_range[1],
            "default_intensity": round((rule_cls.allowed_intensity_range[0] + rule_cls.allowed_intensity_range[1]) / 2, 2)
        })
    return types_list
