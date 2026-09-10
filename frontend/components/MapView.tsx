'use client';

import React, { useEffect, useRef } from 'react';
import { FeatureCollection, GridCellFeature, MapLayerType } from '../types';

interface MapViewProps {
  geoJsonData: FeatureCollection | null;
  activeLayer: MapLayerType;
  onSelectCell: (cell: GridCellFeature | null) => void;
  selectedCellId?: string | null;
}

export default function MapView({
  geoJsonData,
  activeLayer,
  onSelectCell,
  selectedCellId,
}: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const geoJsonLayerRef = useRef<any>(null);

  // Dynamic cell color calculator adhering to Phase 2 specs
  const getCellStyle = (feature: any) => {
    const props = feature.properties;
    let color = '#3b82f6';
    let opacity = 0.70;

    const isSelected = props.grid_id === selectedCellId;

    if (activeLayer === 'lst') {
      const lst = props.lst ?? 35.0;
      if (lst >= 41.5) color = '#7f1d1d';      // Deep Red
      else if (lst >= 39.5) color = '#ef4444'; // Red
      else if (lst >= 37.5) color = '#f97316'; // Orange
      else if (lst >= 35.5) color = '#eab308'; // Yellow
      else color = '#22c55e';                 // Green
    } else if (activeLayer === 'lst_anomaly') {
      const anomaly = props.lst_anomaly ?? (props.lst ? props.lst - 38.56 : 0);
      if (anomaly >= 3.0) color = '#991b1b';       // Dark Red (> +3°C)
      else if (anomaly >= 1.5) color = '#f97316';  // Orange (+1.5°C to +3°C)
      else if (anomaly >= 0.0) color = '#fde047';  // Light Yellow (Above mean)
      else if (anomaly >= -1.5) color = '#38bdf8'; // Sky Blue (Below mean)
      else color = '#1d4ed8';                      // Dark Blue (< -1.5°C)
    } else if (activeLayer === 'lst_zscore') {
      const z = props.lst_zscore ?? 0;
      if (z >= 2.0) color = '#7f1d1d';       // Severe Warm (+2 sigma)
      else if (z >= 1.0) color = '#f97316';  // Moderate Warm (+1 sigma)
      else if (z >= -1.0) color = '#94a3b8'; // Neutral (-1 to +1 sigma)
      else color = '#2563eb';                // Cool (-1 sigma)
    } else if (activeLayer === 'heat_risk') {
      const risk = props.heat_risk || 'Moderate';
      if (risk === 'Very High' || risk === 'Extreme') color = '#991b1b';
      else if (risk === 'High') color = '#ef4444';
      else if (risk === 'Moderate' || risk === 'Medium') color = '#f59e0b';
      else if (risk === 'Low') color = '#84cc16';
      else color = '#10b981'; // Very Low
    } else if (activeLayer === 'hotspots') {
      const hs = props.hotspot_class || 'Not Significant';
      const sig = props.hotspot_significance || '';
      if (hs === 'Hotspot') {
        if (sig.includes('99%')) color = '#991b1b';
        else if (sig.includes('95%')) color = '#dc2626';
        else color = '#f97316';
      } else if (hs === 'Coldspot') {
        if (sig.includes('99%')) color = '#1e3a8a';
        else color = '#2563eb';
      } else {
        color = '#475569'; // Not Significant
      }
    } else if (activeLayer === 'hotspot_score') {
      const score = props.hotspot_score ?? 0.5;
      if (score >= 0.8) color = '#991b1b';
      else if (score >= 0.6) color = '#ea580c';
      else if (score >= 0.4) color = '#eab308';
      else if (score >= 0.2) color = '#06b6d4';
      else color = '#3b82f6';
    } else if (activeLayer === 'thermal_stress_index') {
      const tsi = props.thermal_stress_index ?? 0.5;
      if (tsi >= 0.75) color = '#b91c1c';
      else if (tsi >= 0.55) color = '#f97316';
      else if (tsi >= 0.35) color = '#eab308';
      else color = '#10b981';
    } else if (activeLayer === 'dominant_driver') {
      const driver = props.dominant_driver || 'building_density';
      if (driver === 'building_density') color = '#dc2626';     // Red for Building Density
      else if (driver === 'ndbi') color = '#ea580c';            // Orange for Built-up NDBI
      else if (driver === 'ndvi' || driver === 'green_fraction') color = '#16a34a'; // Green for Vegetation
      else if (driver === 'air_temperature') color = '#eab308'; // Yellow for Atmospheric Air Temp
      else if (driver === 'wind_speed') color = '#06b6d4';      // Cyan for Wind Speed
      else if (driver === 'road_density') color = '#9333ea';    // Purple for Road Density
      else color = '#3b82f6';                                   // Blue for Water/Other
    } else if (activeLayer === 'cooling_delta') {
      const delta = typeof props.cooling_delta === 'number' ? props.cooling_delta : 0.0;
      if (delta >= 2.5) color = '#1e3a8a';       // Dark Blue (Major Cooling > 2.5°C)
      else if (delta >= 1.5) color = '#2563eb';  // Blue (Strong Cooling > 1.5°C)
      else if (delta >= 0.5) color = '#38bdf8';  // Light Blue (Moderate Cooling > 0.5°C)
      else if (delta > -0.1) color = '#fef08a';  // Soft Yellow (Neutral / No Change)
      else color = '#ef4444';                    // Red (Warming Delta)
    } else if (activeLayer === 'baseline_predicted_lst' || activeLayer === 'scenario_predicted_lst' || activeLayer === 'predicted_lst') {
      const lstVal = typeof props[activeLayer] === 'number' ? (props[activeLayer] as number) : (props.lst ?? 38.0);
      if (lstVal >= 42.0) color = '#7f1d1d';
      else if (lstVal >= 40.0) color = '#b91c1c';
      else if (lstVal >= 38.0) color = '#f97316';
      else if (lstVal >= 36.0) color = '#eab308';
      else color = '#10b981';
    } else if (activeLayer === 'prediction_error') {
      const err = typeof props.prediction_error === 'number' ? props.prediction_error : 0.0;
      if (Math.abs(err) <= 0.1) color = '#10b981';      // Low error green
      else if (Math.abs(err) <= 0.5) color = '#eab308'; // Medium error yellow
      else color = '#ef4444';                           // High error red
    } else if (activeLayer.startsWith('shap_')) {
      const featureKey = activeLayer as keyof typeof props;
      const val = typeof props[featureKey] === 'number' ? (props[featureKey] as number) : 0.0;
      if (val >= 1.5) color = '#7f1d1d';
      else if (val >= 0.5) color = '#ef4444';
      else if (val >= 0.0) color = '#fde047';
      else if (val >= -0.5) color = '#38bdf8';
      else color = '#1d4ed8';
    } else if (activeLayer === 'ndvi') {
      const ndvi = props.ndvi ?? 0.2;
      if (ndvi >= 0.45) color = '#15803d';
      else if (ndvi >= 0.30) color = '#22c55e';
      else if (ndvi >= 0.15) color = '#84cc16';
      else color = '#d97706';
    } else if (activeLayer === 'ndbi') {
      const ndbi = props.ndbi ?? 0.3;
      if (ndbi >= 0.40) color = '#991b1b';
      else if (ndbi >= 0.25) color = '#dc2626';
      else if (ndbi >= 0.10) color = '#f97316';
      else color = '#3b82f6';
    } else if (activeLayer === 'building_density') {
      const bldDensity = props.building_density ?? 0.4;
      if (bldDensity >= 0.70) color = '#7f1d1d';
      else if (bldDensity >= 0.50) color = '#b91c1c';
      else if (bldDensity >= 0.30) color = '#f97316';
      else color = '#fde047';
    } else if (activeLayer === 'road_density') {
      const roadDensity = props.road_density ?? 0.3;
      if (roadDensity >= 0.50) color = '#6b21a8';
      else if (roadDensity >= 0.35) color = '#9333ea';
      else if (roadDensity >= 0.20) color = '#a855f7';
      else color = '#cbd5e1';
    }

    return {
      fillColor: color,
      weight: isSelected ? 3 : 1,
      opacity: isSelected ? 1.0 : 0.8,
      color: isSelected ? '#38bdf8' : '#0f172a',
      fillOpacity: opacity,
    };
  };

  useEffect(() => {
    if (typeof window === 'undefined' || !mapContainerRef.current) return;

    import('leaflet').then((L) => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      if (!mapInstanceRef.current) {
        const map = L.map(mapContainerRef.current as HTMLElement, {
          center: [18.5204, 73.8567],
          zoom: 13,
          zoomControl: false,
        });

        L.control.zoom({ position: 'topright' }).addTo(map);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors',
          maxZoom: 19,
        }).addTo(map);

        mapInstanceRef.current = map;
      }

      const map = mapInstanceRef.current;

      if (geoJsonLayerRef.current) {
        map.removeLayer(geoJsonLayerRef.current);
      }

      if (geoJsonData && geoJsonData.features && geoJsonData.features.length > 0) {
        const geoJsonLayer = L.geoJSON(geoJsonData as any, {
          style: getCellStyle,
          onEachFeature: (feature, layer) => {
            const p = feature.properties;
            
            const anomalyStr = p.lst_anomaly !== undefined ? `${p.lst_anomaly > 0 ? '+' : ''}${p.lst_anomaly}°C` : 'N/A';
            const zscoreStr = p.lst_zscore !== undefined ? `${p.lst_zscore}` : 'N/A';
            const hotspotStr = p.hotspot_class || 'N/A';
            const scoreStr = p.hotspot_score !== undefined ? `${p.hotspot_score}` : 'N/A';

            const tooltipContent = `
              <div class="p-2.5 min-w-[200px] text-xs bg-slate-950 text-slate-100 rounded-lg border border-slate-700 shadow-2xl space-y-1">
                <div class="font-bold text-teal-400 text-sm border-b border-slate-800 pb-1 flex justify-between">
                  <span>${p.grid_id}</span>
                  <span class="text-[10px] text-slate-400">100m Grid</span>
                </div>
                <div class="flex justify-between"><span>LST:</span> <span class="font-mono font-bold text-red-400">${p.lst}°C</span></div>
                <div class="flex justify-between"><span>Anomaly:</span> <span class="font-mono text-orange-400">${anomalyStr}</span></div>
                <div class="flex justify-between"><span>Z-Score:</span> <span class="font-mono text-amber-300">${zscoreStr}</span></div>
                <div class="flex justify-between"><span>Heat Risk:</span> <span class="font-semibold text-rose-400">${p.heat_risk || 'N/A'}</span></div>
                <div class="flex justify-between"><span>Hotspot:</span> <span class="font-semibold ${hotspotStr === 'Hotspot' ? 'text-red-400' : hotspotStr === 'Coldspot' ? 'text-blue-400' : 'text-slate-400'}">${hotspotStr}</span></div>
                <div class="flex justify-between border-t border-slate-800 pt-1 text-[11px] text-slate-300"><span>Hotspot Score:</span> <span class="font-mono font-bold text-cyan-300">${scoreStr}</span></div>
              </div>
            `;

            layer.bindTooltip(tooltipContent, { sticky: true, opacity: 0.95 });

            layer.on({
              click: () => {
                onSelectCell(feature as GridCellFeature);
              },
            });
          },
        }).addTo(map);

        geoJsonLayerRef.current = geoJsonLayer;

        try {
          map.fitBounds(geoJsonLayer.getBounds(), { padding: [25, 25] });
        } catch {}
      }
    });
  }, [geoJsonData, activeLayer, selectedCellId]);

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <div ref={mapContainerRef} className="w-full h-full min-h-[540px] bg-slate-950" />

      {/* Requirement 16: Detailed Map Legend with Labels & Tooltips */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/95 backdrop-blur-md border border-slate-800 px-3.5 py-2.5 rounded-xl text-xs text-slate-300 shadow-2xl max-w-sm">
        <div className="font-bold text-slate-200 mb-1 text-[11px] uppercase tracking-wider flex items-center justify-between border-b border-slate-800 pb-1">
          <span>Legend — {activeLayer.replace('_', ' ').toUpperCase()}</span>
        </div>

        {activeLayer === 'lst' && (
          <div className="flex flex-wrap items-center gap-2.5 mt-1 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> &lt;35.5°C</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span> 35.5-37.5°C</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span> 37.5-39.5°C</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> 39.5-41.5°C</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-900"></span> &gt;41.5°C</span>
          </div>
        )}

        {activeLayer === 'lst_anomaly' && (
          <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-700"></span> &lt;-1.5°C</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span> Below Mean</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-yellow-300"></span> Above Mean</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span> &gt;+1.5°C</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-900"></span> &gt;+3.0°C</span>
          </div>
        )}

        {activeLayer === 'lst_zscore' && (
          <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span> Cool (&lt;-1σ)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span> Neutral (-1σ to +1σ)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span> Warm (+1σ to +2σ)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-900"></span> Severe (&gt;+2σ)</span>
          </div>
        )}

        {activeLayer === 'heat_risk' && (
          <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Very Low (&le;P20)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-lime-500"></span> Low</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Moderate</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> High</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-900"></span> Very High (&gt;P80)</span>
          </div>
        )}

        {activeLayer === 'hotspots' && (
          <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-600"></span> Hotspot (Gi* Z &gt; 1.645)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span> Coldspot (Gi* Z &lt; -1.645)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-slate-500"></span> Not Significant</span>
          </div>
        )}

        {activeLayer === 'hotspot_score' && (
          <div className="flex items-center gap-2 mt-1 text-[11px]">
            <span>0.0 (Cool)</span>
            <div className="w-24 h-2 rounded bg-gradient-to-r from-blue-500 via-yellow-400 to-red-700" />
            <span>1.0 (Intense Hotspot)</span>
          </div>
        )}

        {activeLayer === 'thermal_stress_index' && (
          <div className="flex items-center gap-2 mt-1 text-[11px]">
            <span>Low Stress</span>
            <div className="w-24 h-2 rounded bg-gradient-to-r from-emerald-500 via-yellow-400 to-red-700" />
            <span>Severe Stress</span>
          </div>
        )}

        {activeLayer === 'dominant_driver' && (
          <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-600"></span> Building Density</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span> Built-up NDBI</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span> Atmospheric Temp</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-green-600"></span> Vegetation Canopy</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span> Wind Speed</span>
          </div>
        )}

        {activeLayer === 'cooling_delta' && (
          <div className="flex items-center gap-2 mt-1 text-[11px]">
            <span>Warming (&lt;0°C)</span>
            <div className="w-28 h-2.5 rounded bg-gradient-to-r from-red-500 via-yellow-200 via-sky-400 to-blue-900" />
            <span>High Cooling (&gt;2.5°C)</span>
          </div>
        )}

        {activeLayer.startsWith('shap_') && (
          <div className="flex items-center gap-2 mt-1 text-[11px]">
            <span>Cooling Effect (&lt;0 SHAP)</span>
            <div className="w-24 h-2 rounded bg-gradient-to-r from-blue-600 via-yellow-300 to-red-800" />
            <span>Warming Effect (&gt;0 SHAP)</span>
          </div>
        )}

        {(activeLayer === 'ndvi' || activeLayer === 'ndbi' || activeLayer === 'building_density' || activeLayer === 'road_density') && (
          <div className="flex items-center gap-2 text-slate-400 mt-1">
            <span>Low Indicator</span>
            <div className="w-20 h-2 rounded bg-gradient-to-r from-slate-700 via-blue-500 to-red-500" />
            <span>High Indicator</span>
          </div>
        )}
      </div>
    </div>
  );
}
