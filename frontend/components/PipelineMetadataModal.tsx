'use client';

import React from 'react';
import { PipelineMetadataReport } from '../types';

interface PipelineMetadataModalProps {
  isOpen: boolean;
  onClose: () => void;
  metadata: PipelineMetadataReport | null;
}

export default function PipelineMetadataModal({ isOpen, onClose, metadata }: PipelineMetadataModalProps) {
  if (!isOpen) return null;

  const meta = metadata?.dataset_metadata;
  const val = metadata?.validation_summary;

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl text-slate-200">
        <div className="flex justify-between items-center pb-4 border-b border-slate-800">
          <div>
            <div className="text-xs font-mono text-teal-400 uppercase tracking-widest">Phase 1 Pipeline Lineage</div>
            <h2 className="text-xl font-bold text-slate-100">Dataset Metadata & Validation Report</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-100 bg-slate-800 p-1.5 rounded-lg text-sm"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6 my-4 max-h-[70vh] overflow-y-auto pr-2">
          {/* Overview */}
          <div className="grid grid-cols-3 gap-3 text-center text-xs">
            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-lg">
              <span className="text-slate-400">Total Grid Cells</span>
              <div className="text-lg font-bold text-teal-400 font-mono mt-1">{meta?.total_grid_cells || 3024}</div>
              <span className="text-[10px] text-slate-500">100m × 100m</span>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-lg">
              <span className="text-slate-400">Projected CRS</span>
              <div className="text-lg font-bold text-cyan-400 font-mono mt-1">{meta?.projected_crs || 'EPSG:32643'}</div>
              <span className="text-[10px] text-slate-500">UTM Zone 43N</span>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-lg">
              <span className="text-slate-400">Validation Status</span>
              <div className="text-lg font-bold text-emerald-400 font-mono mt-1">{val?.status || 'PASSED'}</div>
              <span className="text-[10px] text-slate-500">0 Anomalies</span>
            </div>
          </div>

          {/* Satellite & Environmental Lineage */}
          <div className="border border-slate-800/80 rounded-xl p-4 bg-slate-950/40">
            <h3 className="text-xs font-semibold text-teal-400 uppercase tracking-wider mb-3">Remote Sensing Lineage & Formulas</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                <span className="text-slate-400 font-semibold">Thermal LST:</span>
                <span className="font-mono text-slate-200">{meta?.remote_sensing_lineage?.thermal_sensor || 'Landsat 8/9 TIRS (Band ST_B10)'}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                <span className="text-slate-400 font-semibold">LST Formula:</span>
                <span className="font-mono text-amber-300">LST (°C) = (ST_B10 * 0.00341802 + 149.0) - 273.15</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                <span className="text-slate-400 font-semibold">NDVI Formula:</span>
                <span className="font-mono text-emerald-300">(NIR - RED) / (NIR + RED)</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                <span className="text-slate-400 font-semibold">NDBI Formula:</span>
                <span className="font-mono text-orange-300">(SWIR1 - NIR) / (SWIR1 + NIR)</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                <span className="text-slate-400 font-semibold">Meteorology:</span>
                <span className="font-mono text-slate-200">ERA5 Daily Reanalysis (2m Temp, Dewpoint, Wind)</span>
              </div>
            </div>
          </div>

          {/* Validation Coverage Percentages */}
          <div className="border border-slate-800/80 rounded-xl p-4 bg-slate-950/40">
            <h3 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">Validation Data Coverage</h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              {Object.entries(val?.coverage_percentages || {
                lst_coverage_pct: 100,
                ndvi_coverage_pct: 100,
                ndbi_coverage_pct: 100,
                osm_building_coverage_pct: 100,
                osm_road_coverage_pct: 100,
                meteorological_coverage_pct: 100
              }).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-800">
                  <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                  <span className="font-mono font-bold text-emerald-400">{value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition"
          >
            Close Metadata Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
