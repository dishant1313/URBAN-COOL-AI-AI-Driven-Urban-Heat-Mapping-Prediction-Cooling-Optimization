'use client';

import React, { useEffect, useState } from 'react';
import { DriverStatisticsReport, ModelPerformanceComparison } from '../types';
import { fetchDriverStatistics, fetchModelPerformance } from '../lib/api';

export default function HeatDriversView() {
  const [driverStats, setDriverStats] = useState<DriverStatisticsReport | null>(null);
  const [modelPerf, setModelPerf] = useState<ModelPerformanceComparison | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [stats, perf] = await Promise.all([
          fetchDriverStatistics(),
          fetchModelPerformance(),
        ]);
        setDriverStats(stats);
        setModelPerf(perf);
      } catch (err) {
        console.error('Failed to load Phase 3 driver statistics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="w-8 h-8 border-2 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading Phase 3 ML Model Performance & SHAP Driver Analysis...
      </div>
    );
  }

  const bestModel = modelPerf?.best_model || driverStats?.best_model || 'Linear Regression';
  const importances = driverStats?.global_feature_importance || {};
  const correlations = driverStats?.correlation_with_lst || {};
  const perfTable = modelPerf?.performance_table || driverStats?.model_performance || {};

  // Sort drivers by importance percentage
  const sortedDrivers = Object.entries(importances).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 backdrop-blur-md shadow-2xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 text-xs font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 rounded-full uppercase">
                Phase 3 Module Active
              </span>
              <span className="text-xs text-slate-400 font-mono">3,024 Grid Cells (30.24 km²)</span>
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 via-emerald-200 to-teal-400 bg-clip-text text-transparent mt-1">
              Urban Heat Driver Analysis & Explainable AI
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl">
              Answering <strong>"WHY IS IT HOT?"</strong> by training, validating, and explaining machine learning models on land surface temperature (LST) and urban morphology predictors.
            </p>
          </div>
          <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-800/60 flex items-center gap-3">
            <div className="text-2xl">🏆</div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">BEST VALIDATED MODEL</span>
              <span className="text-base font-bold text-emerald-300">{bestModel}</span>
            </div>
          </div>
        </div>

        {/* Section 22: Model Performance Dashboard Panel */}
        <div>
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span>📊 Model Performance & Spatial Cross-Validation</span>
          </h3>
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="bg-slate-900/90 text-slate-400 text-[10px] uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Model Architecture</th>
                  <th className="py-3 px-4 text-center">Random CV R²</th>
                  <th className="py-3 px-4 text-center">Random CV RMSE</th>
                  <th className="py-3 px-4 text-center">Spatial Block CV R²</th>
                  <th className="py-3 px-4 text-center">Spatial Block CV RMSE</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {Object.entries(perfTable).map(([name, m]) => {
                  const isBest = name === bestModel;
                  return (
                    <tr key={name} className={isBest ? 'bg-emerald-950/20 font-semibold' : 'hover:bg-slate-900/40'}>
                      <td className="py-3 px-4 font-sans flex items-center gap-2 text-slate-200">
                        {isBest && <span className="text-emerald-400">★</span>}
                        {name}
                      </td>
                      <td className="py-3 px-4 text-center text-teal-300">{m.random_cv_r2}</td>
                      <td className="py-3 px-4 text-center text-slate-300">{m.random_cv_rmse} °C</td>
                      <td className="py-3 px-4 text-center text-emerald-400 font-bold">{m.spatial_cv_r2}</td>
                      <td className="py-3 px-4 text-center text-orange-300">{m.spatial_cv_rmse} °C</td>
                      <td className="py-3 px-4 text-center">
                        {isBest ? (
                          <span className="px-2 py-0.5 text-[10px] bg-emerald-900/80 text-emerald-200 rounded border border-emerald-700">
                            BEST MODEL
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-400 rounded">
                            Evaluated
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="text-[10px] text-slate-400 mt-2 italic">
            * Spatial cross-validation evaluates model generalization across 3x3 non-overlapping spatial grid blocks to prevent spatial autocorrelation leakage.
          </p>
        </div>
      </div>

      {/* Grid Layout: Top Drivers & Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Section 23: Driver Ranking Dashboard */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 backdrop-blur-md shadow-xl">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center justify-between border-b border-slate-800 pb-2">
            <span>🔥 Top Urban Heat Drivers</span>
            <span className="text-[10px] text-teal-400 font-mono">Trained Model Importances</span>
          </h3>

          <div className="space-y-3">
            {sortedDrivers.slice(0, 6).map(([key, pct], idx) => {
              const labelMap: Record<string, string> = {
                building_density: 'Building Footprint Density',
                ndbi: 'Built-up Index (NDBI)',
                ndvi: 'Vegetation Index (NDVI)',
                air_temperature: 'Atmospheric Air Temp',
                wind_speed: 'Wind Speed',
                road_density: 'Road Network Density',
                green_fraction: 'Green Canopy Cover',
                albedo: 'Surface Albedo',
                ndwi: 'Water Index (NDWI)',
                humidity: 'Relative Humidity'
              };

              const label = labelMap[key] || key.replace('_', ' ');
              const corr = correlations[key] !== undefined ? correlations[key] : 0.0;

              return (
                <div key={key} className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 font-bold text-xs flex items-center justify-center font-mono">
                      {idx + 1}
                    </span>
                    <div>
                      <h4 className="text-xs font-semibold text-slate-100">{label}</h4>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Correlation with LST: <strong className={corr >= 0 ? 'text-red-400' : 'text-teal-400'}>{corr >= 0 ? `+${corr}` : `${corr}`}</strong>
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-emerald-400 font-mono">{pct}%</span>
                    <span className="text-[9px] text-slate-500 block">Relative Weight</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Section 12 & 32: Global Feature Importance Visualizer */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 backdrop-blur-md shadow-xl">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">
            📊 Global Feature Importance Breakdown
          </h3>

          <div className="space-y-3.5">
            {sortedDrivers.map(([key, pct]) => {
              const labelMap: Record<string, string> = {
                building_density: 'Building Density',
                ndbi: 'NDBI Built-up',
                ndvi: 'NDVI Vegetation',
                air_temperature: 'Air Temp',
                wind_speed: 'Wind Speed',
                road_density: 'Road Density',
                green_fraction: 'Green Fraction',
                albedo: 'Surface Albedo',
                ndwi: 'NDWI Water',
                humidity: 'Humidity'
              };
              const label = labelMap[key] || key.replace('_', ' ');

              return (
                <div key={key} className="space-y-1 text-xs">
                  <div className="flex justify-between text-slate-300 font-medium">
                    <span>{label}</span>
                    <span className="font-mono text-emerald-400">{pct}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="h-full bg-gradient-to-r from-teal-500 via-emerald-400 to-amber-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(pct, 2)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Section 29: Scientific Interpretation & Causality Disclaimer */}
      <div className="bg-slate-950 border border-amber-800/60 rounded-2xl p-5 shadow-2xl">
        <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-2 flex items-center gap-2">
          <span>⚠️ Scientific Interpretation & Causality Notice</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs text-slate-300 mt-2">
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <strong className="text-teal-400 block mb-1">1. Correlation</strong>
            Statistically measures linear association between urban predictors and Land Surface Temperature.
          </div>
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <strong className="text-emerald-400 block mb-1">2. Predictive Importance</strong>
            Quantifies relative utility of features when predicting microclimate LST across grid cells.
          </div>
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <strong className="text-amber-400 block mb-1">3. SHAP Contribution</strong>
            Measures how each feature shifts a specific model prediction away from the baseline average.
          </div>
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <strong className="text-rose-400 block mb-1">4. Causality (Not Claimed)</strong>
            Physical causation requires micro-meteorological computational fluid dynamics (CFD) modeling.
          </div>
        </div>
        <p className="text-[11px] text-amber-300/90 mt-3 italic text-center">
          "High building density is associated with higher modeled LST and contributes positively to model predictions; this does not claim direct medical causality."
        </p>
      </div>
    </div>
  );
}
