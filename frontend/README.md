# URBAN-COOL AI - Frontend Application

Next.js 14 Web Application for the URBAN-COOL AI Decision Support Dashboard.

## Features
- **App Router Architecture**: Next.js 14 with TypeScript & Tailwind CSS.
- **Interactive Geospatial Canvas**: Leaflet rendering of sample grid cell polygons with heat risk styling and tooltips.
- **Dynamic Microclimate Inspector**: Click-to-inspect cell property drawer (LST, NDVI, NDBI, NDWI, LULC, meteorology).
- **Statistical Visualization**: Recharts heat risk distribution breakdown.
- **Resilient Fallback Handling**: Automatic connection status detection with client-side fallback sample data when API is offline.

## Running Locally
```bash
npm install
npm run dev
```

## Vercel Deployment
1. Set Root Directory to `frontend`.
2. Configure `NEXT_PUBLIC_API_URL` environment variable pointing to backend API.
