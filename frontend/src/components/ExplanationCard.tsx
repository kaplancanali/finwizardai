import React from 'react';
import { Info, AlertCircle, CheckCircle, AlertTriangle, Zap } from 'lucide-react';
import type { ExplanationCardProps } from '../types';

const ExplanationCard: React.FC<ExplanationCardProps> = ({ explanations }) => {
  const getIconForExplanation = (text: string) => {
    if (text.includes('⚠️') || text.includes('yüksek') || text.includes('kritik')) {
      return <AlertTriangle className="w-5 h-5 text-red-500" />;
    }
    if (text.includes('⚡') || text.includes('orta')) {
      return <Zap className="w-5 h-5 text-amber-500" />;
    }
    if (text.includes('✅') || text.includes('✓') || text.includes('düşük')) {
      return <CheckCircle className="w-5 h-5 text-emerald-500" />;
    }
    if (text.includes('📈') || text.includes('pozitif')) {
      return <Info className="w-5 h-5 text-emerald-500" />;
    }
    if (text.includes('🚨') || text.includes('risk')) {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
    return <Info className="w-5 h-5 text-blue-500" />;
  };

  const getBgColorForExplanation = (text: string) => {
    if (text.includes('⚠️') || text.includes('🚨') || text.includes('yüksek') || text.includes('kritik')) {
      return 'bg-red-50 border-red-200';
    }
    if (text.includes('⚡') || text.includes('orta')) {
      return 'bg-amber-50 border-amber-200';
    }
    if (text.includes('✅') || text.includes('✓') || text.includes('düşük') || text.includes('olumlu')) {
      return 'bg-emerald-50 border-emerald-200';
    }
    if (text.includes('📈')) {
      return 'bg-blue-50 border-blue-200';
    }
    return 'bg-gray-50 border-gray-200';
  };

  return (
    <div className="space-y-3">
      {explanations.map((explanation, index) => (
        <div
          key={index}
          className={`p-4 rounded-xl border ${getBgColorForExplanation(explanation)} flex items-start gap-3 transition-all hover:shadow-sm`}
        >
          <div className="mt-0.5 flex-shrink-0">
            {getIconForExplanation(explanation)}
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {explanation}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ExplanationCard;
