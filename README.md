# URBAN-COOL AI

### AI-Driven Urban Heat Mapping, Prediction & Cooling Optimization

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.5-black?style=flat&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat&logo=typescript)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Project Objective

**URBAN-COOL AI** is a geospatial AI decision-support platform designed to:
1. **Identify** urban heat-stress hotspots and microclimate vulnerability.
2. **Quantify** physical heat drivers (vegetation deficit, high built-up density, low surface albedo).
3. **Predict** thermal conditions using spatial machine learning models.
4. **Simulate** urban cooling interventions (cool roofs, green canopy expansion, urban wetlands).
5. **Optimize** spatial placement of cooling investments under municipal budget and zoning constraints.
6. **Provide** an interactive, high-tech geospatial dashboard for urban planners and resilience officers.

> **Phase 0 Notice**: This repository establishes the complete project foundation, monorepo structure, API schema contract, geospatial CRS conventions, interface abstractions for GEE/OSM, and interactive prototype UI displaying verified sample GeoJSON grid datasets.

---

## 2. Monorepo Structure

```
urban-cool-ai/
│
├── frontend/                 # Next.js 14 Web Application (Vercel-ready)
│   ├── app/                  # App router dashboard pages & layouts
│   ├── components/           # UI components (Map, Metrics, Charts, Inspector)
│   ├── lib/                  # API client & fallback data providers
│   ├── public/               # Static web assets
│   ├── types/                # TypeScript interface definitions
│   ├── package.json          # Node dependencies
│   └── README.md             # Frontend deployment documentation
│
├── backend/                  # Python FastAPI Microservice (Render-ready)
│   ├── app/
│   │   ├── main.py           # FastAPI application entrypoint
│   │   ├── api/              # API router & endpoints (/health, /study-area, etc.)
│   │   ├── models/           # Data models
│   │   ├── schemas/          # Pydantic validation schemas & data contract
│   │   ├── services/         # Business logic & GeoJSON parser
│   │   ├── geospatial/       # CRS manager, GEE abstraction, OSM abstraction
│   │   └── config/           # Pydantic Settings & CORS configuration
│   ├── tests/                # Pytest unit & integration test suite
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # Backend deployment documentation
│
├── data/                     # Geospatial Data Directory
│   ├── raw/                  # Raw satellite rasters & vector files
│   ├── processed/            # Processed analysis grids
│   └── sample/               # Phase 0 prototype sample GeoJSON grid (Pune, India)
│
├── notebooks/                # Jupyter Notebooks for ML exploration
├── scripts/                  # Data processing utility scripts
├── docs/                     # Technical Architecture & Data Schema Docs
│   ├── architecture.md       # Full system architecture specification
│   ├── data-schema.md        # Standard geospatial grid feature contract
│   └── deployment.md         # Vercel & Render step-by-step guides
│
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Top-level documentation
└── render.yaml               # Render Infrastructure-as-Code deployment config
```

---

## 3. Quickstart: Local Development Setup

### Prerequisites
- **Node.js**: v18.x or higher
- **Python**: v3.11.x
- **npm** or **pnpm**

### Step A: Start Backend Service (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API will be live at: `http://localhost:8000`  
Swagger API Docs: `http://localhost:8000/docs`

### Step B: Start Frontend Application (Next.js)
```bash
# Navigate to frontend directory (in new terminal)
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```
Frontend UI will be live at: `http://localhost:3000`

---

## 4. Phase 0 API Specifications

| Method | Endpoint | Description | Phase |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status & phase version | Active |
| `GET` | `/api/study-area` | Supported city configurations & bbox | Active |
| `GET` | `/api/layers` | Available map layers & legend styling | Active |
| `GET` | `/api/sample/heatmap` | Sample GeoJSON grid cell collection | Active |
| `GET` | `/api/sample/statistics` | Aggregate baseline stats for study area | Active |

---

## 5. Deployment Overview

- **Frontend (Vercel)**: Import `frontend/` directory, set `NEXT_PUBLIC_API_URL` to backend URL.
- **Backend (Render)**: Deploy using `render.yaml` or point Render Web Service to `backend/` with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

See [`docs/deployment.md`](docs/deployment.md) for full instructions.

---

## 6. License & Citation

MIT License. Designed for Urban Heat Resilience Engineering.
