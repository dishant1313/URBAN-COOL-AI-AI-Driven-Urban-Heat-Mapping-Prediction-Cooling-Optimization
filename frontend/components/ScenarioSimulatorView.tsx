'use client';

import React, { useState, useEffect } from 'react';
import MapView from './MapView';
import {
  FeatureCollection,
  GridCellProperties,
  InterventionTypeConfig,
  ScenarioInterventionSpec,
  ScenarioSimulationResult
} from '../types';
import {
  fetchScenarioTypes,
  runScenarioSimulation,
  fetchHeatmapGeoJSON
} from '../lib/api';

export default function ScenarioSimulatorView() {
  const [availableTypes, setAvailableTypes] = useState<InterventionTypeConfig[]>([]);
  const [activeInterventions, setActiveInterventions] = useState<ScenarioInterventionSpec[]>([
    { type: 'tree_cover', intensity: 0.20 }
  ]);
  
  const [areaSelection, setAreaSelection] = useState<'city' | 'hotspots'>('city');
  const [loading, setLoading] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<ScenarioSimulationResult | null>(null);
  const [geoJsonData, setGeoJsonData] = useState<FeatureCollection | null>(null);
  const [activeMapLayer, setActiveMapLayer] = useState<string>('cooling_delta');
  const [selectedCell, setSelectedCell] = useState<GridCellProperties | null>(null);
  const [comparisonResults, setComparisonResults] = useState<Array<{ name: string; mean_cooling: number; max_cooling: number; area_reduced: number }>>([]);

  // Fetch intervention types on mount & run initial simulation
  useEffect(() => {
    async function initScenarios() {
      setLoading(true);
      try {
        const types = await fetchScenarioTypes();
        setAvailableTypes(types);

        const initialRes = await runScenarioSimulation(activeInterventions);
        setSimulationResult(initialRes);
        setGeoJsonData(initialRes.geojson);

        // Populate comparison benchmark table
        const benchmarks = await Promise.all([
          runScenarioSimulation([{ type: 'tree_cover', intensity: 0.10 }]),
          runScenarioSimulation([{ type: 'tree_cover', intensity: 0.20 }]),
          runScenarioSimulation([{ type: 'cool_roof', intensity: 0.20 }]),
          runScenarioSimulation([{ type: 'green_roof', intensity: 0.15 }]),
          runScenarioSimulation([
            { type: 'tree_cover', intensity: 0.20 },
            { type: 'cool_roof', intensity: 0.20 }
          ])
        ]);

        setComparisonResults([
          { name: 'Tree Canopy +10%', mean_cooling: benchmarks[0].summary.mean_cooling_celsius, max_cooling: benchmarks[0].summary.maximum_cooling_celsius, area_reduced: benchmarks[0].summary.high_heat_area_reduction_km2 },
          { name: 'Tree Canopy +20%', mean_cooling: benchmarks[1].summary.mean_cooling_celsius, max_cooling: benchmarks[1].summary.maximum_cooling_celsius, area_reduced: benchmarks[1].summary.high_heat_area_reduction_km2 },
          { name: 'Cool Roofs (20%)', mean_cooling: benchmarks[2].summary.mean_cooling_celsius, max_cooling: benchmarks[2].summary.maximum_cooling_celsius, area_reduced: benchmarks[2].summary.high_heat_area_reduction_km2 },
          { name: 'Green Roofs (15%)', mean_cooling: benchmarks[3].summary.mean_cooling_celsius, max_cooling: benchmarks[3].summary.maximum_cooling_celsius, area_reduced: benchmarks[3].summary.high_heat_area_reduction_km2 },
          { name: 'Combined (Trees + Cool Roofs)', mean_cooling: benchmarks[4].summary.mean_cooling_celsius, max_cooling: benchmarks[4].summary.maximum_cooling_celsius, area_reduced: benchmarks[4].summary.high_heat_area_reduction_km2 }
        ]);

      } catch (err) {
        console.error('Failed to initialize scenario view:', err);
      } finally {
        setLoading(false);
      }
    }
    initScenarios();
  }, []);

  const handleRunSimulation = async () => {
    if (activeInterventions.length === 0) return;
    setLoading(true);
    try {
      const res = await runScenarioSimulation(activeInterventions, undefined, areaSelection === 'hotspots');
      setSimulationResult(res);
      setGeoJsonData(res.geojson);
    } catch (err) {
      console.error('Scenario simulation execution failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddIntervention = () => {
    const existing = new Set(activeInterventions.map((i) => i.type));
    const nextType = availableTypes.find((t) => !existing.has(t.code)) || availableTypes[0];
    if (nextType) {
      setActiveInterventions([...activeInterventions, { type: nextType.code, intensity: nextType.default_intensity }]);
    }
  };

  const handleRemoveIntervention = (index: number) => {
    if (activeInterventions.length <= 1) return;
    setActiveInterventions(activeInterventions.filter((_, i) => i !== index));
  };

  const handleUpdateIntervention = (index: number, key: 'type' | 'intensity', value: any) => {
    const updated = [...activeInterventions];
    updated[index] = { ...updated[index], [key]: value };
    setActiveInterventions(updated);
  };

  const summary = simulationResult?.summary;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800/80 backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              Cooling Intervention Scenario Simulator
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold bg-cyan-950 text-cyan-300 border border-cyan-800/60 rounded-full">
              PHASE 4 + 5 ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Simulate physical microclimate feature modifications (Trees, Cool Roofs, Green Roofs, Reflective Pavements) and predict resulting thermal LST deltas.
          </p>
        </div>
      </div>

      {/* Out-of-Distribution Warning Banner */}
      {summary?.extrapolation_warning && (
        <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs space-y-1">
          <div className="flex items-center gap-2 font-bold text-amber-200">
            <span>⚠️</span>
            <span>OUT-OF-DISTRIBUTION WARNING: Scenario Extends Beyond Training Bounds</span>
          </div>
          <p className="text-amber-300/80">
            One or more modified feature values exceed the bounds of the machine learning training dataset. Predictions may involve extrapolation.
          </p>
          {summary.out_of_distribution_details?.map((detail, i) => (
            <div key={i} className="pl-6 font-mono text-[11px] text-amber-400/90">• {detail}</div>
          ))}
        </div>
      )}

      {/* Main Simulation Panel (Controls + Metrics) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Scenario Controls */}
        <div className="lg:col-span-5 space-y-5 bg-slate-900/70 p-6 rounded-2xl border border-slate-800/80">
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center justify-between">
            <span>Intervention Parameters</span>
            <span className="text-[11px] text-slate-400 font-normal">Physical Feature Transforms</span>
          </h2>

          {/* Target Area Selection */}
          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1.5">Target Study Area</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setAreaSelection('city')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold transition border ${
                  areaSelection === 'city'
                    ? 'bg-cyan-950 text-cyan-300 border-cyan-700/80 shadow-md shadow-cyan-950/50'
                    : 'bg-slate-950/50 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                Entire Study Area (3,024 Cells)
              </button>
              <button
                onClick={() => setAreaSelection('hotspots')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold transition border ${
                  areaSelection === 'hotspots'
                    ? 'bg-cyan-950 text-cyan-300 border-cyan-700/80 shadow-md shadow-cyan-950/50'
                    : 'bg-slate-950/50 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                Phase 2 Hotspots Only
              </button>
            </div>
          </div>

          {/* Intervention List */}
          <div className="space-y-4 pt-2">
            {activeInterventions.map((item, idx) => {
              const typeConfig = availableTypes.find((t) => t.code === item.type) || availableTypes[0];
              return (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-cyan-400">Intervention #{idx + 1}</span>
                    {activeInterventions.length > 1 && (
                      <button
                        onClick={() => handleRemoveIntervention(idx)}
                        className="text-xs text-rose-400 hover:text-rose-300 font-medium"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  {/* Selector */}
                  <div>
                    <label className="text-[11px] font-medium text-slate-400 block mb-1">Intervention Category</label>
                    <select
                      value={item.type}
                      onChange={(e) => handleUpdateIntervention(idx, 'type', e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg p-2 focus:ring-1 focus:ring-cyan-500 focus:outline-none"
                    >
                      {availableTypes.map((t) => (
                        <option key={t.code} value={t.code}>
                          {t.name} ({t.affected_features.join(', ')})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Intensity Slider */}
                  <div>
                    <div className="flex justify-between items-center text-xs mb-1">
                      <span className="text-slate-400 text-[11px]">Intervention Intensity / Coverage</span>
                      <span className="font-mono text-cyan-300 font-bold">
                        {Math.round(item.intensity * 100)}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min={typeConfig?.min_intensity || 0.05}
                      max={typeConfig?.max_intensity || 0.50}
                      step={0.05}
                      value={item.intensity}
                      onChange={(e) => handleUpdateIntervention(idx, 'intensity', parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                      <span>Min ({Math.round((typeConfig?.min_intensity || 0.05) * 100)}%)</span>
                      <span>Max ({Math.round((typeConfig?.max_intensity || 0.5) * 100)}%)</span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 italic">
                    {typeConfig?.description}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleAddIntervention}
              disabled={activeInterventions.length >= availableTypes.length}
              className="px-3.5 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700 transition disabled:opacity-40"
            >
              + Add Intervention
            </button>
            <button
              onClick={handleRunSimulation}
              disabled={loading}
              className="flex-1 py-2.5 px-4 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-600 via-teal-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white shadow-lg shadow-cyan-900/30 transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span>Simulating Model...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>RUN SCENARIO SIMULATION</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Key Simulation Metric Cards */}
        <div className="lg:col-span-7 space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {/* Metric 1 */}
            <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl space-y-1">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block">Baseline Mean LST</span>
              <span className="text-xl font-extrabold text-slate-100 font-mono">
                {summary ? `${summary.mean_baseline_lst} °C` : '--'}
              </span>
              <span className="text-[10px] text-slate-500 block">Pre-intervention reference</span>
            </div>

            {/* Metric 2 */}
            <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl space-y-1">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block">Scenario Mean LST</span>
              <span className="text-xl font-extrabold text-cyan-300 font-mono">
                {summary ? `${summary.mean_scenario_lst} °C` : '--'}
              </span>
              <span className="text-[10px] text-slate-500 block">Post-intervention model state</span>
            </div>

            {/* Metric 3 */}
            <div className="bg-slate-900/80 border border-cyan-800/50 bg-cyan-950/20 p-4 rounded-2xl space-y-1 col-span-2 sm:col-span-1">
              <span className="text-[11px] text-cyan-300 uppercase font-bold block flex items-center justify-between">
                <span>Model Cooling Delta</span>
                <span className="text-[9px] px-1.5 bg-emerald-950 text-emerald-300 rounded font-semibold">ΔLST</span>
              </span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">
                {summary ? `-${summary.mean_cooling_celsius} °C` : '--'}
              </span>
              <span className="text-[10px] text-emerald-400/80 block">
                Max cooling: {summary ? `${summary.maximum_cooling_celsius} °C` : '--'}
              </span>
            </div>

            {/* Metric 4 */}
            <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl space-y-1">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block">Affected Area</span>
              <span className="text-xl font-extrabold text-slate-200 font-mono">
                {summary ? `${summary.affected_area_km2} km²` : '--'}
              </span>
              <span className="text-[10px] text-slate-500 block">
                {summary ? `${summary.affected_cells} grid cells modified` : '--'}
              </span>
            </div>

            {/* Metric 5 */}
            <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl space-y-1">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block">High Heat Area Before</span>
              <span className="text-xl font-extrabold text-rose-400 font-mono">
                {summary ? `${summary.high_heat_area_before_km2} km²` : '--'}
              </span>
              <span className="text-[10px] text-slate-500 block">Cells &gt; 40°C baseline</span>
            </div>

            {/* Metric 6 */}
            <div className="bg-slate-900/80 border border-slate-800/80 p-4 rounded-2xl space-y-1">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block">High Heat Area Reduced</span>
              <span className="text-xl font-extrabold text-emerald-400 font-mono">
                {summary ? `${summary.high_heat_area_reduction_km2} km²` : '--'}
              </span>
              <span className="text-[10px] text-slate-500 block">Area shift below 40°C</span>
            </div>
          </div>

          {/* Scenario Comparison Table */}
          <div className="bg-slate-900/80 border border-slate-800/80 p-5 rounded-2xl space-y-3">
            <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center justify-between">
              <span>Scenario Strategy Benchmark Comparison</span>
              <span className="text-[10px] text-slate-400 font-normal">Model-Estimated Impact</span>
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold text-[11px]">
                    <th className="pb-2">Scenario Package</th>
                    <th className="pb-2 text-right">Mean ΔLST</th>
                    <th className="pb-2 text-right">Max Cooling</th>
                    <th className="pb-2 text-right">High Heat Reduced</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {comparisonResults.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition">
                      <td className="py-2.5 text-slate-300 font-medium">{item.name}</td>
                      <td className="py-2.5 text-right font-mono font-bold text-emerald-400">-{item.mean_cooling} °C</td>
                      <td className="py-2.5 text-right font-mono text-cyan-300">-{item.max_cooling} °C</td>
                      <td className="py-2.5 text-right font-mono text-slate-300">{item.area_reduced} km²</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Scenario Map View */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <span>🗺️</span>
              <span>Spatial Cooling Impact Map</span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive grid-cell visualization comparing baseline predicted LST vs simulated scenario cooling delta.
            </p>
          </div>

          {/* Layer Selector */}
          <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setActiveMapLayer('cooling_delta')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeMapLayer === 'cooling_delta'
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Cooling Delta (ΔLST)
            </button>
            <button
              onClick={() => setActiveMapLayer('baseline_predicted_lst')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeMapLayer === 'baseline_predicted_lst'
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Baseline Predicted LST
            </button>
            <button
              onClick={() => setActiveMapLayer('scenario_predicted_lst')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeMapLayer === 'scenario_predicted_lst'
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Scenario Predicted LST
            </button>
          </div>
        </div>

        {/* Map Canvas */}
        <div className="h-[520px] rounded-xl overflow-hidden border border-slate-800 relative">
          <MapView
            geoJsonData={geoJsonData}
            activeLayer={activeMapLayer as any}
            onSelectCell={(cell) => setSelectedCell(cell ? cell.properties : null)}
          />
        </div>
      </div>

      {/* Hotspot Inspection Detail Panel (if cell selected) */}
      {selectedCell && (
        <div className="bg-slate-900/90 border border-cyan-800/60 p-5 rounded-2xl space-y-3 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-cyan-300 text-sm">{selectedCell.grid_id}</span>
              <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px]">
                {selectedCell.lulc || 'Built-up'}
              </span>
            </div>
            <button
              onClick={() => setSelectedCell(null)}
              className="text-slate-400 hover:text-slate-200 font-bold"
            >
              ✕ Close
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
            <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Observed LST</span>
              <span className="text-slate-200 font-bold">{selectedCell.lst} °C</span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Baseline Predicted</span>
              <span className="text-slate-200 font-bold">{selectedCell.baseline_predicted_lst || selectedCell.predicted_lst || '--'} °C</span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Scenario Predicted</span>
              <span className="text-cyan-300 font-bold">{selectedCell.scenario_predicted_lst || '--'} °C</span>
            </div>
            <div className="p-2.5 rounded-xl bg-cyan-950/40 border border-cyan-800">
              <span className="text-[10px] text-cyan-400 block">Estimated Cooling</span>
              <span className="text-emerald-400 font-bold">-{selectedCell.cooling_delta || 0.0} °C</span>
            </div>
          </div>
        </div>
      )}

      {/* Mandatory Scientific Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-400 text-xs flex items-start gap-3">
        <span className="text-lg">ℹ️</span>
        <div className="space-y-1">
          <p className="font-semibold text-slate-300">Mandatory Scientific Disclaimer & Methodological Notice</p>
          <p className="text-[11px] leading-relaxed text-slate-400">
            {summary?.disclaimer ||
              'Cooling values produced by this prototype are model-based scenario estimates derived from changes in predictor variables. They are not direct measurements of real-world intervention performance.'}
          </p>
          <p className="text-[10px] text-slate-500">
            Scenario results should be validated using microclimate physical CFD simulation, field measurements, or established urban climate models before implementation decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
