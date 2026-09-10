'use client';

import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  change?: string;
  changeType?: 'increase' | 'decrease' | 'neutral';
  description?: string;
  badge?: string;
}

export default function MetricCard({
  title,
  value,
  unit,
  subtitle,
  change,
  description,
  badge = 'Phase 1 Master Data'
}: MetricCardProps) {
  return (
    <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 shadow-xl backdrop-blur-md hover:border-slate-700 transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <span className="text-[9px] px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/30 font-mono">
          {badge}
        </span>
      </div>

      <div className="flex items-baseline space-x-1.5 my-1">
        <span className="text-2xl font-extrabold text-slate-100 tracking-tight font-mono">
          {value}
        </span>
        {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
      </div>

      <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/80 text-xs">
        <span className="text-slate-400 text-[11px] truncate max-w-[170px]">
          {description || subtitle || 'Study Area Grid'}
        </span>
        {change && (
          <span className="font-semibold text-teal-400 text-[10px] font-mono">
            {change}
          </span>
        )}
      </div>
    </div>
  );
}

export { MetricCard };
