import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.geospatial.grid import create_spatial_grid
from app.geospatial.validation import validate_master_dataset

client = TestClient(app)


def test_grid_generation():
    gdf_proj, gdf_wgs84 = create_spatial_grid(
        city_name="Pune",
        bbox_wgs84=[73.850, 18.510, 73.860, 18.520], # Small test box
        grid_resolution_m=100.0
    )
    assert len(gdf_proj) > 0
    assert len(gdf_wgs84) == len(gdf_proj)
    assert "grid_id" in gdf_wgs84.columns
    assert "latitude" in gdf_wgs84.columns
    assert "longitude" in gdf_wgs84.columns
    assert gdf_wgs84.crs.to_string() == "EPSG:4326"


def test_data_api_endpoints():
    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200

    # 2. Real Heatmap API
    res_map = client.get("/api/data/heatmap?limit=10&layer=lst")
    assert res_map.status_code == 200
    data_map = res_map.json()
    assert data_map["type"] == "FeatureCollection"
    assert len(data_map["features"]) <= 10

    # 3. Real Statistics API
    res_stats = client.get("/api/data/statistics")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "sample_size" in stats
    assert "mean_lst_celsius" in stats
    assert "mean_building_density" in stats

    # 4. Real Metadata API
    res_meta = client.get("/api/data/metadata")
    assert res_meta.status_code == 200
    meta = res_meta.json()
    assert "dataset_metadata" in meta or "status" in meta

    # 5. Paginated Features API
    res_feat = client.get("/api/data/features?page=1&page_size=5")
    assert res_feat.status_code == 200
    feats = res_feat.json()
    assert feats["page"] == 1
    assert len(feats["items"]) <= 5
