import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.geospatial.crs import get_projected_crs
from app.geospatial.gee_service import GEEService
from app.geospatial.osm_service import OSMService


def test_crs_lookup():
    assert get_projected_crs("Pune") == "EPSG:32643"
    assert get_projected_crs("Delhi") == "EPSG:32644"
    assert get_projected_crs("UnknownCity") == "EPSG:3857"


def test_gee_service_stubs():
    service = GEEService()
    with pytest.raises(NotImplementedError):
        service.initialize_gee()


def test_osm_service_stubs():
    service = OSMService()
    with pytest.raises(NotImplementedError):
        service.calculate_building_density("GRID_001")
