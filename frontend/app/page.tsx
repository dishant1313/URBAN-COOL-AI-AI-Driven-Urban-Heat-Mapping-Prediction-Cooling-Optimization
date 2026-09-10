'use client';

import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import MapView from '../components/MapView';
import MetricCard from '../components/MetricCard';
import CellDetailsCard from '../components/CellDetailsCard';
import RiskChart from '../components/RiskChart';
import PipelineMetadataModal from '../components/PipelineMetadataModal';
import {
  FeatureCollection,
  GridCellFeature,
  DatasetStatistics,
  MapLayerType,
  PipelineMetadataReport,
} from '../types';
import {
  fetchHeatmapGeoJSON,
  fetchDatasetStatistics,
  fetchPipelineMetadata,
  fetchHealthCheck,
} from '../lib/api';

export default function DashboardPage() {
  const [geoJsonData, setGeoJsonData] = useState<FeatureCollection | null>(null);
  const [statistics, setStatistics] = useState<DatasetStatistics | null>(null);
  const [metadata, setMetadata] = useState<PipelineMetadataReport | null>(null);
  const [selectedCell, setSelectedCell] = useState<GridCellFeature | null>(null);
  const [activeLayer, setActiveLayer] = useState<MapLayerType>('lst');
  const [showHotspotPreview, setShowHotspotPreview] = useState<boolean>(false);
  const [isMetadataOpen, setIsMetadataOpen] = useState<boolean>(false);
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const health = await fetchHealthCheck();
      setBackendConnected(health.status === 'ok' || health.status === 'online');

      const [mapData, statsData, metaData] = await Promise.all([
        fetchHeatmapGeoJSON(activeLayer, 600),
        fetchDatasetStatistics(),
        fetchPipelineMetadata(),
      ]);

      setGeoJsonData(mapData);
      setStatistics(statsData);
      setMetadata(metaData);

      if (mapData.features && mapData.features.length > 0) {
        setSelectedCell(mapData.features[0]);
      }
      setLoading(false);
    }
    loadData();
  }, [activeLayer]);

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col font-sans selection:bg-teal-500 selection:text-slate-950">
      <Navbar backendConnected={backendConnected} />

      <main className="flex-1 max-w-[1600px] w-full mx-auto p-4 md:p-6 space-y-6">
        {/* Phase 1 Header Toolbar */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 backdrop-blur-md shadow-xl">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-500/10 border border-teal-500/30 rounded-lg text-teal-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
            </div>
            <div>
              <div className="text-[10px] uppercase font-mono tracking-widest text-slate-400">Active Study Area (100m Grid)</div>
              <div className="text-sm font-bold text-slate-100 flex items-center gap-2">
                Pune, MH (India)
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">
                  Phase 1 Master Dataset
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Hotspot Preview Toggle */}
            <button
              onClick={() => setShowHotspotPreview(!showHotspotPreview)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all flex items-center gap-1.5 ${
                showHotspotPreview
                  ? 'bg-red-500/20 text-red-300 border-red-500/50 shadow-lg shadow-red-950/50'
                  : 'bg-slate-950/60 text-slate-300 border-slate-800 hover:border-slate-700'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-red-400 animate-ping" />
              Hotspot Preview (Prelim)
            </button>

            {/* Metadata Inspector Button */}
            <button
              onClick={() => setIsMetadataOpen(true)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-950/60 text-teal-300 border border-teal-500/30 hover:border-teal-500/60 rounded-lg transition"
            >
              📋 View Metadata & Lineage
            </button>

            {/* Active Layer Selector */}
            <div className="flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
              <span className="text-slate-400 font-semibold">Active Layer:</span>
              <select
                value={activeLayer}
                onChange={(e) => setActiveLayer(e.target.value as MapLayerType)}
                className="bg-transparent text-teal-300 font-semibold focus:outline-none cursor-pointer"
              >
                <option value="lst">Layer 1: LST (°C)</option>
                <option value="ndvi">Layer 2: NDVI (Vegetation)</option>
                <option value="ndbi">Layer 3: NDBI (Built-up)</option>
                <option value="ndwi">Layer 4: NDWI (Water)</option>
                <option value="building_density">Layer 5: Building Density</option>
                <option value="road_density">Layer 6: Road Density</option>
              </select>
            </div>
          </div>
        </div>

        {/* Top Summary Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="LAND SURFACE TEMP (LST)"
            value={statistics ? `${statistics.mean_lst_celsius}°C` : '38.6°C'}
            change={`Max: ${statistics ? statistics.max_lst_celsius : 43.8}°C`}
            changeType="increase"
            description="Landsat 8 TIRS Mean Surface Temp"
            badge="Phase 1 Observed"
          />

          <MetricCard
            title="VEGETATION INDEX (NDVI)"
            value={statistics ? `${statistics.mean_ndvi}` : '0.22'}
            change="Sentinel-2 Canopy"
            changeType="neutral"
            description="Mean Vegetation Density"
            badge="Phase 1 Derived"
          />

          <MetricCard
            title="BUILT-UP INDEX (NDBI)"
            value={statistics ? `${statistics.mean_ndbi}` : '0.38'}
            change="High Impervious Surface"
            changeType="increase"
            description="Built-up & Roof Impervious Index"
            badge="Phase 1 Derived"
          />

          <MetricCard
            title="BUILDING FOOTPRINT DENSITY"
            value={statistics ? `${Math.round(statistics.mean_building_density * 100)}%` : '54%'}
            change="OSM Morphological"
            changeType="increase"
            description="Footprint Area / 100m Grid Cell"
            badge="OSM Morphology"
          />
        </div>

        {/* Core Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Map View */}
          <div className="lg:col-span-2 h-[560px]">
            <MapView
              geoJsonData={geoJsonData}
              activeLayer={activeLayer}
              onSelectCell={setSelectedCell}
              selectedCellId={selectedCell?.properties.grid_id}
              showHotspotPreview={showHotspotPreview}
            />
          </div>

          {/* Side Panel: Microclimate Inspector & Risk Distribution */}
          <div className="space-y-6 flex flex-col justify-between">
            <CellDetailsCard selectedCell={selectedCell} />

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-md shadow-xl flex-1 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Heat Risk Distribution</h3>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {statistics ? statistics.sample_size : 3024} Grid Cells (100m)
                  </span>
                </div>
                <RiskChart statistics={statistics} />
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Metadata Lineage Modal */}
      <PipelineMetadataModal
        isOpen={isMetadataOpen}
        onClose={() => setIsMetadataOpen(false)}
        metadata={metadata}
      />

      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500 flex flex-wrap justify-between items-center max-w-[1600px] mx-auto w-full">
        <div>
          <strong className="text-slate-400">URBAN-COOL AI</strong> — Geospatial AI Decision-Support System
        </div>
        <div className="flex gap-4 font-mono text-[11px]">
          <span>Frontend: Next.js 14</span>
          <span>Backend: FastAPI</span>
          <span>CRS: EPSG:4326 / EPSG:32643</span>
          <span>Grid: 100m × 100m</span>
        </div>
      </footer>
    </div>
  );
}
