'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { DatasetStatistics } from '../types';

interface RiskChartProps {
  statistics: DatasetStatistics | null;
}

export default function RiskChart({ statistics }: RiskChartProps) {
  if (!statistics || !statistics.risk_distribution) return null;

  const data = [
    { category: 'Low', count: statistics.risk_distribution.Low || 0, color: '#22c55e' },
    { category: 'Medium', count: statistics.risk_distribution.Medium || 0, color: '#eab308' },
    { category: 'High', count: statistics.risk_distribution.High || 0, color: '#f97316' },
    { category: 'Extreme', count: statistics.risk_distribution.Extreme || 0, color: '#ef4444' },
  ];

  return (
    <div className="h-44 w-full mt-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <XAxis dataKey="category" stroke="#94a3b8" fontSize={11} tickLine={false} />
          <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} allowDecimals={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px', color: '#f8fafc' }}
            cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
