import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { getRiskColor } from '../types';

interface RiskTrendChartProps {
  score: number;
  breakdown: {
    kap_score: number;
    news_score: number;
    sentiment_score: number;
    market_score: number;
  };
}

const RiskTrendChart: React.FC<RiskTrendChartProps> = ({ score, breakdown }) => {
  const data = [
    { name: 'KAP', score: breakdown.kap_score, fill: '#3b82f6' },
    { name: 'Haber', score: breakdown.news_score, fill: '#f59e0b' },
    { name: 'Duygu', score: breakdown.sentiment_score, fill: '#10b981' },
    { name: 'Piyasa', score: breakdown.market_score, fill: '#8b5cf6' },
    { name: 'Genel', score: score, fill: getRiskColor(score) },
  ];

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Risk Bileşenleri</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="name" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis 
            domain={[0, 100]} 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <Tooltip 
            formatter={(value: number) => [`${value.toFixed(1)}`, 'Risk Skoru']}
            contentStyle={{ 
              borderRadius: '8px', 
              border: 'none', 
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              backgroundColor: 'white'
            }}
          />
          <ReferenceLine y={50} stroke="#9ca3af" strokeDasharray="3 3" />
          <Line 
            type="monotone" 
            dataKey="score" 
            stroke={getRiskColor(score)} 
            strokeWidth={3}
            dot={{ fill: getRiskColor(score), strokeWidth: 2, r: 6 }}
            activeDot={{ r: 8, fill: getRiskColor(score) }}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-4 flex justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span className="text-gray-600">KAP</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-500"></div>
          <span className="text-gray-600">Haber</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
          <span className="text-gray-600">Duygu</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-violet-500"></div>
          <span className="text-gray-600">Piyasa</span>
        </div>
      </div>
    </div>
  );
};

export default RiskTrendChart;
