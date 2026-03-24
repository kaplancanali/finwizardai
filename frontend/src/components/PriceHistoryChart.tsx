import React, { useMemo } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { PriceBar } from '../types';

interface PriceHistoryChartProps {
  bars: PriceBar[];
  tickerLabel?: string | null;
}

const PriceHistoryChart: React.FC<PriceHistoryChartProps> = ({ bars, tickerLabel }) => {
  const data = useMemo(
    () =>
      bars.map((b) => ({
        t: b.date,
        label: new Date(b.date).toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' }),
        close: b.close,
      })),
    [bars]
  );

  if (data.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-gray-200 p-8 text-center text-sm text-gray-500">
        Gösterilecek fiyat serisi yok.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex flex-wrap items-baseline justify-between gap-2 mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Son ~1 yıl kapanış (günlük)</h3>
        {tickerLabel && <span className="text-xs text-gray-500 font-mono">{tickerLabel}</span>}
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="label"
            tick={{ fill: '#6b7280', fontSize: 10 }}
            interval="preserveStartEnd"
            minTickGap={24}
          />
          <YAxis
            domain={['auto', 'auto']}
            tick={{ fill: '#6b7280', fontSize: 11 }}
            width={56}
            tickFormatter={(v: number) => v.toFixed(2)}
          />
          <Tooltip
            formatter={(value: number) => [value.toFixed(2), 'Kapanış']}
            labelFormatter={(_, payload) => {
              if (payload && payload[0] && payload[0].payload) {
                return new Date(payload[0].payload.t as string).toLocaleDateString('tr-TR');
              }
              return '';
            }}
            contentStyle={{
              borderRadius: '8px',
              border: 'none',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              backgroundColor: 'white',
            }}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke="#4f46e5"
            strokeWidth={2}
            fill="url(#priceFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceHistoryChart;
