import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.geospatial.crs import get_projected_crs
from app.geospatial.gee_service import GEEService, GEEExtractionParams
from app.geospatial.osm_service import OSMService


def test_crs_lookup():
    assert get_projected_crs("Pune") == "EPSG:32643"
    assert get_projected_crs("Delhi") == "EPSG:32644"
    assert get_projected_crs("UnknownCity") == "EPSG:3857"


def test_gee_service_initialization():
    service = GEEService()
    params = GEEExtractionParams()
    meta = service.get_source_metadata(params)
    assert "thermal_sensor" in meta
    assert meta["spatial_resolution_m"] == 100


def test_osm_service_initialization():
    service = OSMService()
    assert service.overpass_url is not None

