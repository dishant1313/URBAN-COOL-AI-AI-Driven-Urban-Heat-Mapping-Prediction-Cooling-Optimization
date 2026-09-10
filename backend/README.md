# URBAN-COOL AI - Backend API Service

FastAPI geospatial backend service providing API endpoints, geospatial CRS management, and interface abstractions for GEE and OSM ingestion pipelines.

## Endpoints
- `GET /api/health`: Health status & phase version.
- `GET /api/study-area`: Configured study areas and bounding boxes.
- `GET /api/layers`: Active geospatial layer metadata.
- `GET /api/sample/heatmap`: GeoJSON collection of sample grid cells.
- `GET /api/sample/statistics`: Baseline aggregate statistics for sample grid cells.

## Running Locally
```bash
python -m venv venv
# Activate virtual environment
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Running Tests
```bash
pytest tests/
```

## Render Deployment
Backend uses `render.yaml` at project root or manual deployment with start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
