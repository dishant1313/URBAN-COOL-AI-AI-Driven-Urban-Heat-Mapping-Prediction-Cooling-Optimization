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
        <p className="text-xs text-slate-400">Click on any 100m grid cell on the map to explore microclimate thermal indicators, hotspot stats, and urban heat driver explanations.</p>
      </div>
    );
  }

  const p = selectedCell.properties;
  const anomalyStr = p.lst_anomaly !== undefined ? `${p.lst_anomaly > 0 ? '+' : ''}${p.lst_anomaly} °C` : 'N/A';
  const zscoreStr = p.lst_zscore !== undefined ? `${p.lst_zscore}` : 'N/A';
  const hotspotSigStr = p.hotspot_significance || p.hotspot_class || 'Not Significant';
  const hotspotScoreStr = p.hotspot_score !== undefined ? `${p.hotspot_score}` : 'N/A';

  // Extract SHAP drivers if available
  const topDrivers = [
    { name: 'Building Density', shap: p.shap_building_density, raw: `${Math.round((p.building_density || 0) * 100)}%` },
    { name: 'Vegetation (NDVI)', shap: p.shap_ndvi, raw: `${p.ndvi}` },
    { name: 'Built-up (NDBI)', shap: p.shap_ndbi, raw: `${p.ndbi}` },
    { name: 'Air Temp', shap: p.shap_air_temperature, raw: `${p.air_temperature}°C` },
  ].filter(d => d.shap !== undefined).sort((a, b) => Math.abs(b.shap || 0) - Math.abs(a.shap || 0));

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

      {/* Primary Thermal Diagnostics */}
      <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800/80 mb-4 shadow-inner">
        <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 mb-3 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span> Thermal Condition
        </h4>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Observed LST</span>
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
      </div>

      {/* Phase 3 Model Explanation & SHAP Local Drivers */}
      <div className="bg-slate-950/90 rounded-xl p-4 border border-emerald-800/60 mb-4 shadow-xl">
        <div className="flex justify-between items-center mb-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <span>🧠 Model Explanation (Phase 3)</span>
          </h4>
          {p.dominant_driver_label && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              Dominant: {p.dominant_driver_label}
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
          <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800 flex justify-between">
            <span className="text-slate-400">Predicted LST:</span>
            <span className="font-mono text-emerald-300 font-bold">{p.predicted_lst ? `${p.predicted_lst}°C` : `${p.lst}°C`}</span>
          </div>
          <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800 flex justify-between">
            <span className="text-slate-400">Prediction Error:</span>
            <span className="font-mono text-slate-300">{p.prediction_error !== undefined ? `${p.prediction_error}°C` : '0.00°C'}</span>
          </div>
        </div>

        <div className="space-y-1.5 text-xs">
          <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider block mb-1">Top Contributing Factors (SHAP)</span>
          {topDrivers.length > 0 ? (
            topDrivers.slice(0, 3).map((driver, i) => (
              <div key={i} className="flex justify-between items-center p-2 rounded bg-slate-900/80 border border-slate-800 text-[11px]">
                <span className="text-slate-300 font-medium">{i + 1}. {driver.name} ({driver.raw})</span>
                <span className={`font-mono font-bold ${driver.shap && driver.shap > 0 ? 'text-red-400' : 'text-teal-400'}`}>
                  {driver.shap && driver.shap > 0 ? `+${driver.shap}°C` : `${driver.shap}°C`}
                </span>
              </div>
            ))
          ) : (
            <div className="text-[11px] text-slate-400 italic">Top drivers calculated via SHAP model explainer.</div>
          )}
        </div>

        {/* Mandatory Phase 3 Disclaimer */}
        <p className="mt-3 text-[10px] text-amber-300/80 bg-amber-950/40 p-2 rounded border border-amber-800/40 italic">
          "These are model-based explanations and should not be interpreted as direct causal estimates."
        </p>
      </div>

      {/* Urban Morphology Metrics */}
      <div className="pt-2 border-t border-slate-800/80">
        <h4 className="text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2">Urban Indicators</h4>
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
            <span className="text-slate-400">NDVI Vegetation:</span>
            <span className="font-mono text-emerald-300">{p.ndvi}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">NDBI Built-up:</span>
            <span className="font-mono text-amber-300">{p.ndbi}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
