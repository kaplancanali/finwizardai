import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { DetectedEvent } from '../types';

interface EventDistributionChartProps {
  events: DetectedEvent[];
}

const EventDistributionChart: React.FC<EventDistributionChartProps> = ({ events }) => {
  const highRisk = events.filter(e => e.event_type === 'high_risk').length;
  const positive = events.filter(e => e.event_type === 'positive').length;
  const neutral = events.filter(e => e.event_type === 'neutral').length;

  const data = [
    { name: 'Risk Sinyali', value: highRisk, color: '#ef4444' },
    { name: 'Pozitif', value: positive, color: '#10b981' },
    { name: 'Nötr', value: neutral, color: '#9ca3af' },
  ].filter(d => d.value > 0);

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Olay Dağılımı</h3>
        <div className="h-[200px] flex items-center justify-center text-gray-400">
          Henüz olay tespit edilmedi
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Olay Dağılımı</h3>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              borderRadius: '8px', 
              border: 'none', 
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              backgroundColor: 'white'
            }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            iconType="circle"
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-2 text-center">
        <p className="text-sm text-gray-500">
          Toplam {events.length} olay tespit edildi
        </p>
      </div>
    </div>
  );
};

export default EventDistributionChart;
