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
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">Microclimate Inspector</h3>
        <p className="text-xs text-slate-400">Click on any 100m grid cell on the map to inspect satellite & morphology attributes.</p>
      </div>
    );
  }

  const p = selectedCell.properties;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-md shadow-xl text-slate-200">
      <div className="flex justify-between items-start mb-4 border-b border-slate-800 pb-3">
        <div>
          <span className="text-[10px] uppercase font-mono tracking-widest text-teal-400">GRID CELL: {p.grid_id}</span>
          <h3 className="text-lg font-bold text-slate-100 mt-0.5">100m × 100m Spatial Cell</h3>
          <p className="text-xs text-slate-400 font-mono">Centroid: {p.latitude}°N, {p.longitude}°E</p>
        </div>
        <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${
          p.heat_risk === 'Extreme' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
          p.heat_risk === 'High' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
          p.heat_risk === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' :
          'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
        }`}>
          {p.heat_risk} Heat Risk
        </span>
      </div>

      {/* Main Satellite Indicators */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Land Surface Temp</span>
          <div className="text-xl font-bold text-red-400 mt-0.5 font-mono">{p.lst}°C</div>
          <span className="text-[9px] text-slate-500">Landsat 8 TIRS (ST_B10)</span>
        </div>
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Vegetation (NDVI)</span>
          <div className="text-xl font-bold text-emerald-400 mt-0.5 font-mono">{p.ndvi}</div>
          <span className="text-[9px] text-slate-500">Sentinel-2 (NIR/Red)</span>
        </div>
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Built-up (NDBI)</span>
          <div className="text-xl font-bold text-amber-400 mt-0.5 font-mono">{p.ndbi}</div>
          <span className="text-[9px] text-slate-500">Sentinel-2 (SWIR/NIR)</span>
        </div>
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Water Index (NDWI)</span>
          <div className="text-xl font-bold text-sky-400 mt-0.5 font-mono">{p.ndwi}</div>
          <span className="text-[9px] text-slate-500">Sentinel-2 (Green/NIR)</span>
        </div>
      </div>

      {/* Urban Morphology (OSM Features) */}
      <div className="mb-4 pt-2 border-t border-slate-800/80">
        <h4 className="text-xs font-semibold text-teal-400 uppercase tracking-wider mb-2">Urban Morphology (OSM)</h4>
        <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs">
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Building Count:</span>
            <span className="font-mono text-slate-200">{p.building_count || 0} structures</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Building Density:</span>
            <span className="font-mono text-cyan-300">{Math.round((p.building_density || 0) * 100)}%</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Road Length:</span>
            <span className="font-mono text-slate-200">{p.road_length || 0} m</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Road Density:</span>
            <span className="font-mono text-purple-300">{Math.round((p.road_density || 0) * 100)}%</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Green Area:</span>
            <span className="font-mono text-slate-200">{p.green_area || 0} m²</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1">
            <span className="text-slate-400">Green Fraction:</span>
            <span className="font-mono text-emerald-300">{Math.round((p.green_fraction || 0) * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Extended Meteorology & Physics Attributes */}
      <div className="pt-2 border-t border-slate-800/80">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Meteorology & Surface Physics</h4>
        <div className="grid grid-cols-2 gap-y-1.5 gap-x-4 text-xs text-slate-300">
          <div className="flex justify-between">
            <span className="text-slate-400">LULC Class:</span>
            <span className="font-semibold text-slate-200">{p.lulc}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Shortwave Albedo:</span>
            <span className="font-mono">{p.albedo}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">2m Air Temp:</span>
            <span className="font-mono">{p.air_temperature}°C</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Relative Humidity:</span>
            <span className="font-mono">{p.humidity}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">10m Wind Speed:</span>
            <span className="font-mono">{p.wind_speed} m/s</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Observation Date:</span>
            <span className="font-mono text-slate-400">{p.observation_date || '2026-05-31'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
