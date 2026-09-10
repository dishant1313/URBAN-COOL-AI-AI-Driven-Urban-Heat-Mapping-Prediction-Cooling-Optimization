'use client';

import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import MapView from '../components/MapView';
import MetricCard from '../components/MetricCard';
import CellDetailsCard from '../components/CellDetailsCard';
import RiskChart from '../components/RiskChart';
import HeatDriversView from '../components/HeatDriversView';
import ScenarioSimulatorView from '../components/ScenarioSimulatorView';
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
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [geoJsonData, setGeoJsonData] = useState<FeatureCollection | null>(null);
  const [statistics, setStatistics] = useState<DatasetStatistics | null>(null);
  const [metadata, setMetadata] = useState<PipelineMetadataReport | null>(null);
  const [selectedCell, setSelectedCell] = useState<GridCellFeature | null>(null);
  const [activeLayer, setActiveLayer] = useState<MapLayerType>('lst');
  const [isMetadataOpen, setIsMetadataOpen] = useState<boolean>(false);
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const health = await fetchHealthCheck();
      setBackendConnected(health.status === 'ok' || health.status === 'online');

      const [mapData, statsData, metaData] = await Promise.all([
        fetchHeatmapGeoJSON(activeLayer, 700),
        fetchDatasetStatistics(),
        fetchPipelineMetadata(),
      ]);

      setGeoJsonData(mapData);
      setStatistics(statsData);
      setMetadata(metaData);

      if (mapData.features && mapData.features.length > 0 && !selectedCell) {
        setSelectedCell(mapData.features[0]);
      }
      setLoading(false);
    }
    loadData();
  }, [activeLayer]);

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col font-sans selection:bg-teal-500 selection:text-slate-950">
      <Navbar backendConnected={backendConnected} activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-[1650px] w-full mx-auto p-4 md:p-6 space-y-5">
        
        {/* Render Tab Content based on Navigation */}
        {activeTab === 'drivers' ? (
          <HeatDriversView />
        ) : activeTab === 'scenarios' ? (
          <ScenarioSimulatorView />
        ) : activeTab === 'about' ? (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-8 backdrop-blur-md shadow-2xl space-y-4 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-teal-400">About URBAN-COOL AI</h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              URBAN-COOL AI is a scientifically transparent, production-ready geospatial platform built to map, quantify, and explain urban thermal dynamics for heat resilience planning.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800 text-xs">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <strong className="text-emerald-400 block text-sm mb-1">Phase 1</strong>
                Real Geospatial Processing Pipeline (100m x 100m Metric CRS EPSG:32643)
              </div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <strong className="text-rose-400 block text-sm mb-1">Phase 2</strong>
                Getis-Ord Gi* Spatial Hotspot Detection & Risk Classification
              </div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <strong className="text-cyan-400 block text-sm mb-1">Phase 3</strong>
                Explainable AI & ML Driver Analysis (SHAP + Spatial Cross-Validation)
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* Category Badges & Transparency Banner */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-3 backdrop-blur-md shadow-xl text-xs">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Category Badges:</span>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold" title="Landsat 8 TIRS LST">
                  Observed (Satellite LST)
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-semibold" title="Derived anomalies and percentile risk">
                  Derived (Anomaly & Risk)
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-semibold" title="Getis-Ord Gi* test">
                  Statistical (Getis-Ord Gi*)
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-300 border border-teal-500/30 font-semibold" title="Phase 3 ML Driver Analysis">
                  Modeled (SHAP Drivers)
                </span>
              </div>

              <div className="text-[11px] text-slate-400 italic">
                Relative thermal-risk classification for selected period. Not an official medical heat warning.
              </div>
            </div>

            {/* Header Toolbar */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 backdrop-blur-md shadow-xl">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-teal-500/10 border border-teal-500/30 rounded-lg text-teal-400">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-[10px] uppercase font-mono tracking-widest text-slate-400">Active Study Area (100m Metric Grid)</div>
                  <div className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    Pune, MH (India)
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 rounded-full">
                      Phase 3 Driver Analysis Active
                    </span>
                  </div>
                </div>
              </div>

              {/* Layer selector */}
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={() => setIsMetadataOpen(true)}
                  className="px-3 py-1.5 text-xs font-semibold bg-slate-950/60 text-teal-300 border border-teal-500/30 hover:border-teal-500/60 rounded-lg transition shadow"
                >
                  📋 View Heat Lineage & Stats
                </button>

                <div className="flex items-center gap-2 bg-slate-950/90 px-3 py-1.5 rounded-lg border border-slate-800 text-xs shadow-inner">
                  <span className="text-slate-400 font-semibold uppercase tracking-wider text-[11px]">Heat Layer:</span>
                  <select
                    value={activeLayer}
                    onChange={(e) => setActiveLayer(e.target.value as MapLayerType)}
                    className="bg-transparent text-teal-300 font-bold focus:outline-none cursor-pointer text-xs"
                  >
                    <option value="lst">○ LST (°C)</option>
                    <option value="lst_anomaly">○ LST Anomaly (°C)</option>
                    <option value="lst_zscore">○ LST Z-score</option>
                    <option value="heat_risk">○ Heat Risk</option>
                    <option value="hotspots">○ Statistical Hotspots (Gi*)</option>
                    <option value="hotspot_score">○ Hotspot Score (0–1)</option>
                    <option value="thermal_stress_index">○ Thermal Stress Index</option>
                    <option value="dominant_driver">★ Dominant Heat Driver (Phase 3)</option>
                    <option value="shap_building_density">★ SHAP: Building Density Impact</option>
                    <option value="shap_ndvi">★ SHAP: NDVI Vegetation Impact</option>
                    <option value="shap_ndbi">★ SHAP: NDBI Built-up Impact</option>
                    <option value="shap_air_temperature">★ SHAP: Air Temperature Impact</option>
                    <option value="ndvi">○ NDVI (Vegetation)</option>
                    <option value="building_density">○ Building Density</option>
                    <option value="road_density">○ Road Density</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Dashboard Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
              <MetricCard
                title="MEAN LST"
                value={statistics ? `${statistics.mean_lst_celsius}°C` : '38.56°C'}
                change={`Median: ${statistics?.median_lst_celsius || 38.62}°C`}
                changeType="neutral"
                description="Study Area Mean LST"
                badge="Observed"
              />

              <MetricCard
                title="MAXIMUM LST"
                value={statistics ? `${statistics.max_lst_celsius}°C` : '44.0°C'}
                change={`Min: ${statistics?.min_lst_celsius || 32.75}°C`}
                changeType="increase"
                description="Peak Surface Temperature"
                badge="Observed"
              />

              <MetricCard
                title="MAXIMUM ANOMALY"
                value={statistics ? `+${statistics.max_anomaly_celsius}°C` : '+5.44°C'}
                change="Above Area Mean"
                changeType="increase"
                description="Maximum Thermal Anomaly"
                badge="Derived"
              />

              <MetricCard
                title="HOTSPOT AREA"
                value={statistics ? `${statistics.hotspot_area_km2} km²` : '9.4 km²'}
                change="Metric EPSG:32643"
                changeType="increase"
                description="Getis-Ord Gi* Significant"
                badge="Statistical"
              />

              <MetricCard
                title="HIGH-RISK AREA"
                value={statistics ? `${statistics.high_risk_area_km2} km²` : '12.09 km²'}
                change="High & Very High Risk"
                changeType="increase"
                description="Area > P60 Threshold"
                badge="Derived"
              />

              <MetricCard
                title="HOTSPOT CELLS"
                value={statistics ? `${statistics.hotspot_count}` : '940'}
                change={`Coldspots: ${statistics?.coldspot_count || 881}`}
                changeType="neutral"
                description="Clustered High Thermal Cells"
                badge="Statistical"
              />
            </div>

            {/* Core Map & Cell Inspector */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 h-[580px]">
                <MapView
                  geoJsonData={geoJsonData}
                  activeLayer={activeLayer}
                  onSelectCell={setSelectedCell}
                  selectedCellId={selectedCell?.properties.grid_id}
                />
              </div>

              <div className="space-y-6 flex flex-col justify-between">
                <CellDetailsCard selectedCell={selectedCell} />

                <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 backdrop-blur-md shadow-xl flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Heat Risk Distribution</h3>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {statistics ? statistics.sample_size : 3024} Cells (100m Grid)
                      </span>
                    </div>
                    <RiskChart statistics={statistics} />
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>

      <PipelineMetadataModal
        isOpen={isMetadataOpen}
        onClose={() => setIsMetadataOpen(false)}
        metadata={metadata}
      />

      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500 flex flex-wrap justify-between items-center max-w-[1650px] mx-auto w-full">
        <div>
          <strong className="text-slate-400">URBAN-COOL AI</strong> — Phase 3 Urban Heat Driver Analysis & Explainable AI
        </div>
        <div className="flex gap-4 font-mono text-[11px]">
          <span>Frontend: Next.js 14</span>
          <span>Backend: FastAPI</span>
          <span>CRS: EPSG:4326 / EPSG:32643</span>
          <span>Explainability: SHAP</span>
        </div>
      </footer>
    </div>
  );
}
