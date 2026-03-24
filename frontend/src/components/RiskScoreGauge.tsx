import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import type { RiskScoreGaugeProps } from '../types';
import { RISK_LEVEL_CONFIG, getRiskColor, getRiskLabel, RISK_GRADIENT } from '../types';

const RiskScoreGauge: React.FC<RiskScoreGaugeProps> = ({ score, level, size = 'md' }) => {
  const config = RISK_LEVEL_CONFIG[level];
  const mainColor = getRiskColor(score);
  
  // Calculate gauge data with dynamic color
  const data = [
    { value: score, color: mainColor },
    { value: 100 - score, color: '#e5e7eb' },
  ];

  const sizeClasses = {
    sm: { container: 'w-32 h-32', text: 'text-2xl' },
    md: { container: 'w-48 h-48', text: 'text-4xl' },
    lg: { container: 'w-64 h-64', text: 'text-5xl' },
  };

  const { container, text } = sizeClasses[size];

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${container}`}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={180}
              endAngle={0}
              innerRadius="60%"
              outerRadius="100%"
              dataKey="value"
              stroke="none"
              cornerRadius={6}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Center Text with dynamic color */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span 
            className={`${text} font-bold`}
            style={{ color: mainColor }}
          >
            {score}
          </span>
          <span className="text-sm text-gray-400">/100</span>
        </div>
      </div>

      {/* Risk Level Badge with dynamic background */}
      <div 
        className="mt-4 px-4 py-2 rounded-full font-semibold flex items-center gap-2 text-white shadow-lg"
        style={{ backgroundColor: mainColor }}
      >
        <span>{config.icon}</span>
        <span>{getRiskLabel(score)}</span>
      </div>

      {/* Gradient Scale Indicator */}
      <div className="mt-6 w-full max-w-xs">
        <div 
          className="h-2 rounded-full w-full"
          style={{
            background: `linear-gradient(to right, ${RISK_GRADIENT.map(g => g.color).join(', ')})`
          }} 
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>Güvenli</span>
          <span>Kritik</span>
        </div>
        {/* Current position marker */}
        <div 
          className="relative mt-1"
          style={{ left: `${score}%`, transform: 'translateX(-50%)' }}
        >
          <div 
            className="w-3 h-3 rounded-full border-2 border-white shadow"
            style={{ backgroundColor: mainColor }}
          />
        </div>
      </div>
    </div>
  );
};

export default RiskScoreGauge;
