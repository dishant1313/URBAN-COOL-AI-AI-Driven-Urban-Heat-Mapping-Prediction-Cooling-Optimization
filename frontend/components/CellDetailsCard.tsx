'use client';

import React from 'react';
import { GridCellFeature } from '../types';

interface CellDetailsCardProps {
  selectedCell: GridCellFeature | null;
}

export default function CellDetailsCard({ selectedCell }: CellDetailsCardProps) {
  if (!selectedCell) {
    return (
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 backdrop-blur-md shadow-xl text-slate-400">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">Selected Location Inspector</h3>
        <p className="text-xs text-slate-400">Click on any 100m grid cell on the map to explore microclimate thermal indicators, hotspot stats, and urban morphology.</p>
      </div>
    );
  }

  const p = selectedCell.properties;
  const anomalyStr = p.lst_anomaly !== undefined ? `${p.lst_anomaly > 0 ? '+' : ''}${p.lst_anomaly} °C` : 'N/A';
  const zscoreStr = p.lst_zscore !== undefined ? `${p.lst_zscore}` : 'N/A';
  const hotspotSigStr = p.hotspot_significance || p.hotspot_class || 'Not Significant';
  const hotspotScoreStr = p.hotspot_score !== undefined ? `${p.hotspot_score}` : 'N/A';

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 backdrop-blur-md shadow-2xl text-slate-200">
      {/* Header */}
      <div className="flex justify-between items-start mb-4 border-b border-slate-800 pb-3">
        <div>
          <span className="text-[10px] uppercase font-mono tracking-widest text-teal-400">GRID ID: {p.grid_id}</span>
          <h3 className="text-lg font-bold text-slate-100 mt-0.5">SELECTED LOCATION</h3>
          <p className="text-xs text-slate-400 font-mono">Centroid: {p.latitude}°N, {p.longitude}°E</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${
            p.heat_risk === 'Very High' || p.heat_risk === 'Extreme' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
            p.heat_risk === 'High' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
            p.heat_risk === 'Moderate' || p.heat_risk === 'Medium' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
            'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
          }`}>
            {p.heat_risk || 'Unclassified'}
          </span>
          <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${
            p.hotspot_class === 'Hotspot' ? 'bg-red-950/60 text-red-300 border-red-800' :
            p.hotspot_class === 'Coldspot' ? 'bg-blue-950/60 text-blue-300 border-blue-800' :
            'bg-slate-800 text-slate-400 border-slate-700'
          }`}>
            {hotspotSigStr}
          </span>
        </div>
      </div>

      {/* Section 18: Primary Hotspot Detail Panel */}
      <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800/80 mb-4 shadow-inner">
        <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 mb-3 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span> Thermal & Hotspot Diagnostics
        </h4>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">LST</span>
            <div className="text-lg font-bold text-red-400 mt-0.5 font-mono">{p.lst} °C</div>
            <span className="text-[9px] text-slate-500">Landsat 8 TIRS</span>
          </div>

          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">LST Anomaly</span>
            <div className="text-lg font-bold text-orange-400 mt-0.5 font-mono">{anomalyStr}</div>
            <span className="text-[9px] text-slate-500">vs Area Mean</span>
          </div>

          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Z-Score</span>
            <div className="text-lg font-bold text-amber-300 mt-0.5 font-mono">{zscoreStr}</div>
            <span className="text-[9px] text-slate-500">Standardized</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mt-3">
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Hotspot Score</span>
              <span className="text-base font-bold text-cyan-300 font-mono">{hotspotScoreStr}</span>
            </div>
            <div className="text-[9px] text-slate-500 text-right">0.0 to 1.0 Scale</div>
          </div>

          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Thermal Stress Index</span>
              <span className="text-base font-bold text-rose-300 font-mono">{p.thermal_stress_index ?? 'N/A'}</span>
            </div>
            <div className="text-[9px] text-slate-500 text-right">Prototype Index</div>
          </div>
        </div>
      </div>

      {/* Satellite Spectral Indices */}
      <div className="grid grid-cols-3 gap-2.5 mb-4">
        <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800 text-center">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">NDVI</span>
          <span className="text-sm font-bold text-emerald-400 font-mono">{p.ndvi}</span>
        </div>
        <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800 text-center">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">NDBI</span>
          <span className="text-sm font-bold text-amber-400 font-mono">{p.ndbi}</span>
        </div>
        <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800 text-center">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">NDWI</span>
          <span className="text-sm font-bold text-sky-400 font-mono">{p.ndwi}</span>
        </div>
      </div>

      {/* Urban Morphology Metrics */}
      <div className="mb-4 pt-2 border-t border-slate-800/80">
        <h4 className="text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2">Urban Morphology Indicators</h4>
        <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs">
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Building Density:</span>
            <span className="font-mono text-cyan-300">{Math.round((p.building_density || 0) * 100)}%</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Road Density:</span>
            <span className="font-mono text-purple-300">{Math.round((p.road_density || 0) * 100)}%</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Building Count:</span>
            <span className="font-mono text-slate-200">{p.building_count || 0}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Green Fraction:</span>
            <span className="font-mono text-emerald-300">{Math.round((p.green_fraction || 0) * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Requirement 18: Mandatory Phase 3 Notice Banner */}
      <div className="mt-3 p-2.5 rounded-lg bg-blue-950/40 border border-blue-800/60 text-xs text-blue-300 flex items-center gap-2">
        <span className="text-base">ℹ️</span>
        <span className="italic">Driver analysis will be available in Phase 3.</span>
      </div>
    </div>
  );
}
