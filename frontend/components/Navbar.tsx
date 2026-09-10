'use client';

import React from 'react';

interface NavbarProps {
  backendConnected?: boolean;
  isConnected?: boolean;
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
}

export default function Navbar({ backendConnected = true, isConnected = true }: NavbarProps) {
  const connected = backendConnected && isConnected;

  return (
    <header className="bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 via-emerald-500 to-orange-500 p-0.5 shadow-lg shadow-teal-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <span className="text-xl">🔥</span>
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold bg-gradient-to-r from-slate-100 via-teal-200 to-emerald-400 bg-clip-text text-transparent tracking-tight">
                  URBAN-COOL AI
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-teal-950 text-teal-300 border border-teal-800/60 rounded-full">
                  PHASE 1
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Geospatial AI for Urban Heat Resilience & Processing Pipeline
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 text-xs text-slate-300">
            <button className="px-3 py-1.5 rounded-lg bg-teal-950/80 text-teal-300 border border-teal-800/80 font-medium">
              Overview
            </button>
            <button className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-200">
              Heat Map
            </button>
            <button className="px-3 py-1.5 rounded-lg text-slate-400 flex items-center gap-1">
              Heat Drivers <span className="text-[9px] px-1 bg-slate-800 rounded">Phase 2</span>
            </button>
            <button className="px-3 py-1.5 rounded-lg text-slate-400 flex items-center gap-1">
              Scenarios <span className="text-[9px] px-1 bg-slate-800 rounded">Phase 2</span>
            </button>
            <button className="px-3 py-1.5 rounded-lg text-slate-400 flex items-center gap-1">
              Optimization <span className="text-[9px] px-1 bg-slate-800 rounded">Phase 3</span>
            </button>
          </nav>

          {/* Backend API Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium border ${
              connected
                ? 'bg-emerald-950/50 text-emerald-300 border-emerald-800/60'
                : 'bg-amber-950/50 text-amber-300 border-amber-800/60'
            }`}>
              <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span>{connected ? 'Backend API: Connected' : 'Backend API: Local Fallback'}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export { Navbar };
