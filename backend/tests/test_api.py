import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure app package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "urban-cool-ai-api"
    assert data["phase"] == "phase-0"


def test_study_area():
    response = client.get("/api/study-area")
    assert response.status_code == 200
    data = response.json()
    assert data["active_study_area"]["city"] == "Pune"
    assert len(data["available_cities"]) >= 1


def test_layers():
    response = client.get("/api/layers")
    assert response.status_code == 200
    data = response.json()
    assert "layers" in data
    assert len(data["layers"]) > 0


def test_sample_heatmap():
    response = client.get("/api/sample/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) > 0
    # Check data contract schema on first feature
    first_feat = data["features"][0]["properties"]
    assert "grid_id" in first_feat
    assert "latitude" in first_feat
    assert "longitude" in first_feat
    assert "lst" in first_feat


def test_sample_statistics():
    response = client.get("/api/sample/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Pune"
    assert data["sample_size"] > 0
    assert "mean_lst_celsius" in data
    assert "risk_distribution" in data
