# System Architecture Specification

## 1. Architectural Overview

**URBAN-COOL AI** is structured as a decoupled monorepo, separating frontend visualization from spatial backend services.

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 14 Dashboard                     │
│        (Vercel / React 18 / Tailwind / Leaflet / Recharts)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON & GeoJSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│          (Render / GeoPandas / Rasterio / Scikit-learn)     │
├──────────────────────────────┬──────────────────────────────┤
│    geospatial/crs.py         │    geospatial/gee_service.py │
│    (EPSG:4326 <-> EPSG:32643)│    (Landsat/Sentinel/ERA5)  │
├──────────────────────────────┼──────────────────────────────┤
│    geospatial/osm_service.py │    services/sample_service  │
│    (Building/Road Vectors)   │    (GeoJSON Grid Loader)    │
└──────────────────────────────┴──────────────────────────────┘
```

---

## 2. Architectural Principles

1. **Independent Deployability**: Frontend and backend can be built, tested, and deployed independently to Vercel and Render.
2. **Configurable Study Areas**: System architecture is city-agnostic. Initial demo uses Pune, India (`EPSG:32643`), but bbox and projected CRS can be swapped seamlessly.
3. **Decoupled Geospatial Interfaces**: GEE and OSM ingestion pipelines are isolated behind interface classes (`GEEService`, `OSMService`), allowing model and UI development to progress independently of cloud rate limits or authentication setup.
4. **Strict CRS Management**: All API payload exchanges use standard WGS84 (`EPSG:4326`). All metric calculations (area in m², Euclidean distance, buffer radii) reproject to a local equal-area projected CRS (`EPSG:32643` for UTM 43N).

---

## 3. Technology Selection Rationale

- **FastAPI**: Lightweight, high throughput, native Pydantic data validation, automatic OpenAPI schema generation.
- **GeoPandas & Rasterio**: Standard Python spatial data science ecosystem for vector manipulation and satellite raster processing.
- **Next.js 14 App Router**: Server-side rendering, quick page loads, seamless API integration.
- **Leaflet & CartoDB Dark Matter**: Client-rendered interactive GIS map without requiring third-party map tiles API keys.
