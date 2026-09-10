'use client';

import React from 'react';
import { Sparkles, Layers, Cpu, Info, ArrowRight } from 'lucide-react';

interface ComingSoonProps {
  title: string;
  phase: string;
  description: string;
  features: string[];
}

export const ComingSoon: React.FC<ComingSoonProps> = ({
  title,
  phase,
  description,
  features,
}) => {
  return (
    <div className="bg-slate-900/90 rounded-2xl p-8 border border-slate-800 shadow-2xl max-w-4xl mx-auto my-8">
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-3 bg-teal-950/80 rounded-xl border border-teal-800 text-teal-400">
          <Sparkles className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <span className="text-xs font-bold text-teal-400 uppercase tracking-widest px-2 py-0.5 rounded bg-teal-950 border border-teal-800/80">
            {phase} Roadmap
          </span>
          <h2 className="text-2xl font-bold text-slate-100 mt-1">{title}</h2>
        </div>
      </div>

      <p className="text-sm text-slate-300 mb-6 leading-relaxed">
        {description}
      </p>

      <div className="bg-slate-950/60 rounded-xl p-5 border border-slate-800/80 mb-6">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Planned Deliverables in {phase}:
        </h4>
        <div className="grid sm:grid-cols-2 gap-3">
          {features.map((feat, idx) => (
            <div key={idx} className="flex items-center space-x-2 text-xs text-slate-200 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
              <ArrowRight className="w-3.5 h-3.5 text-teal-400 flex-shrink-0" />
              <span>{feat}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-slate-950/40 rounded-lg border border-slate-800/60 text-xs text-slate-400 text-center font-mono">
        Phase 0 repository foundation & data contracts complete. Module planned for upcoming release.
      </div>
    </div>
  );
};
