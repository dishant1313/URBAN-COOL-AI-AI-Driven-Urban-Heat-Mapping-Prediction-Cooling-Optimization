'use client';

import React, { useEffect, useRef } from 'react';
import { FeatureCollection, GridCellFeature, MapLayerType } from '../types';

interface MapViewProps {
  geoJsonData: FeatureCollection | null;
  activeLayer: MapLayerType;
  onSelectCell: (cell: GridCellFeature | null) => void;
  selectedCellId?: string | null;
  showHotspotPreview?: boolean;
}

export default function MapView({
  geoJsonData,
  activeLayer,
  onSelectCell,
  selectedCellId,
  showHotspotPreview = false,
}: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const geoJsonLayerRef = useRef<any>(null);

  // Layer color palette calculator
  const getCellStyle = (feature: any) => {
    const props = feature.properties;
    let color = '#3b82f6'; // default blue
    let opacity = 0.65;

    // Check if cell is selected
    const isSelected = props.grid_id === selectedCellId;

    if (activeLayer === 'lst') {
      const lst = props.lst || 35.0;
      if (lst >= 41.0) color = '#ef4444';      // Extreme (Red)
      else if (lst >= 37.5) color = '#f97316'; // High (Orange)
      else if (lst >= 34.0) color = '#eab308'; // Medium (Yellow)
      else color = '#22c55e';                 // Low (Green)
    } else if (activeLayer === 'ndvi') {
      const ndvi = props.ndvi || 0.2;
      if (ndvi >= 0.45) color = '#15803d';      // Dense Vegetation
      else if (ndvi >= 0.30) color = '#22c55e';
      else if (ndvi >= 0.15) color = '#84cc16';
      else color = '#d97706';                 // Low Vegetation
    } else if (activeLayer === 'ndbi') {
      const ndbi = props.ndbi || 0.3;
      if (ndbi >= 0.40) color = '#991b1b';      // High Built-up
      else if (ndbi >= 0.25) color = '#dc2626';
      else if (ndbi >= 0.10) color = '#f97316';
      else color = '#3b82f6';
    } else if (activeLayer === 'ndwi') {
      const ndwi = props.ndwi || -0.2;
      if (ndwi >= 0.20) color = '#0284c7';      // Water body
      else if (ndwi >= 0.0) color = '#38bdf8';
      else color = '#64748b';
    } else if (activeLayer === 'building_density') {
      const bldDensity = props.building_density || 0.4;
      if (bldDensity >= 0.70) color = '#7f1d1d'; // Dense urban core
      else if (bldDensity >= 0.50) color = '#b91c1c';
      else if (bldDensity >= 0.30) color = '#f97316';
      else color = '#fde047';
    } else if (activeLayer === 'road_density') {
      const roadDensity = props.road_density || 0.3;
      if (roadDensity >= 0.50) color = '#6b21a8'; // High transport corridor
      else if (roadDensity >= 0.35) color = '#9333ea';
      else if (roadDensity >= 0.20) color = '#a855f7';
      else color = '#cbd5e1';
    }

    // Preliminary Hotspot Overlay Highlight
    if (showHotspotPreview && (props.lst >= 40.5 || props.heat_risk === 'Extreme')) {
      color = '#ff0055';
      opacity = 0.85;
    }

    return {
      fillColor: color,
      weight: isSelected ? 3 : 1,
      opacity: isSelected ? 1.0 : 0.8,
      color: isSelected ? '#38bdf8' : '#1e293b',
      fillOpacity: opacity,
    };
  };

  useEffect(() => {
    if (typeof window === 'undefined' || !mapContainerRef.current) return;

    // Dynamically import Leaflet client-side
    import('leaflet').then((L) => {
      // Fix default marker icon assets
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

        // Standard OpenStreetMap tiles
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors',
          maxZoom: 19,
        }).addTo(map);

        mapInstanceRef.current = map;
      }

      const map = mapInstanceRef.current;

      // Clear previous GeoJSON layer
      if (geoJsonLayerRef.current) {
        map.removeLayer(geoJsonLayerRef.current);
      }

      if (geoJsonData && geoJsonData.features && geoJsonData.features.length > 0) {
        const geoJsonLayer = L.geoJSON(geoJsonData as any, {
          style: getCellStyle,
          onEachFeature: (feature, layer) => {
            const p = feature.properties;
            
            // Build informative tooltip HTML
            const tooltipContent = `
              <div class="p-2 min-w-[170px] text-xs bg-slate-900 text-slate-100 rounded border border-slate-700 shadow-xl">
                <div class="font-bold text-teal-400 mb-1 border-b border-slate-700 pb-1">${p.grid_id}</div>
                <div class="flex justify-between py-0.5"><span>LST:</span> <span class="font-mono font-bold text-red-400">${p.lst}°C</span></div>
                <div class="flex justify-between py-0.5"><span>NDVI:</span> <span class="font-mono text-emerald-400">${p.ndvi}</span></div>
                <div class="flex justify-between py-0.5"><span>NDBI:</span> <span class="font-mono text-amber-400">${p.ndbi}</span></div>
                <div class="flex justify-between py-0.5"><span>Bld Density:</span> <span class="font-mono text-cyan-300">${Math.round((p.building_density || 0) * 100)}%</span></div>
                <div class="mt-1 pt-1 border-t border-slate-800 text-[10px] text-slate-400 capitalize">Risk: <strong class="${p.heat_risk === 'Extreme' ? 'text-red-400' : p.heat_risk === 'High' ? 'text-orange-400' : 'text-emerald-400'}">${p.heat_risk}</strong></div>
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

        // Auto-fit map bounds if first load
        try {
          map.fitBounds(geoJsonLayer.getBounds(), { padding: [30, 30] });
        } catch {}
      }
    });

    return () => {
      // Keep map instance alive for smooth re-renders
    };
  }, [geoJsonData, activeLayer, selectedCellId, showHotspotPreview]);

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <div ref={mapContainerRef} className="w-full h-full min-h-[520px] bg-slate-950" />

      {/* Layer Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur-md border border-slate-800 px-3 py-2 rounded-lg text-xs text-slate-300 shadow-lg">
        <div className="font-semibold text-slate-200 mb-1 text-[11px] uppercase tracking-wider">
          Legend ({activeLayer.toUpperCase()})
        </div>
        {activeLayer === 'lst' && (
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Low (&lt;34°C)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span> Medium</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span> High</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Extreme (&gt;41°C)</span>
          </div>
        )}
        {activeLayer === 'ndvi' && (
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-600"></span> Low Vegetation (&lt;0.15)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Medium</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-green-700"></span> Dense Canopy (&gt;0.45)</span>
          </div>
        )}
        {activeLayer === 'building_density' && (
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-yellow-300"></span> Low Density (&lt;30%)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span> Moderate</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-800"></span> Core Density (&gt;70%)</span>
          </div>
        )}
        {(activeLayer === 'ndbi' || activeLayer === 'ndwi' || activeLayer === 'road_density') && (
          <div className="flex items-center gap-2 text-slate-400">
            <span>Low Value</span>
            <div className="w-20 h-2 rounded bg-gradient-to-r from-slate-700 via-blue-500 to-red-500" />
            <span>High Value</span>
          </div>
        )}
      </div>

      {/* Preliminary Hotspot Notice Badge */}
      {showHotspotPreview && (
        <div className="absolute top-4 left-4 z-[1000] bg-red-950/90 border border-red-700/80 px-3 py-1.5 rounded-lg text-xs text-red-200 shadow-xl backdrop-blur-md animate-pulse">
          ⚡ Preliminary thermal visualization — hotspot analytics implemented in Phase 2
        </div>
      )}
    </div>
  );
}
