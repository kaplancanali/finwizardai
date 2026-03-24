import React from 'react';
import { AlertCircle, Loader2, Database } from 'lucide-react';
import type { AnalysisResultsProps } from '../types';
import RiskAnalysisDetailView from './RiskAnalysisDetailView';

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
        <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Analiz Yapılıyor...</h3>
        <p className="text-gray-500">KAP açıklamaları, haberler ve duygu analizi işleniyor</p>
        <div className="mt-6 flex justify-center gap-2">
          <span className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-red-900 mb-2">Analiz Hatası</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-12 text-center">
        <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-600 mb-2">Henüz Analiz Yapılmadı</h3>
        <p className="text-gray-500">Yukarıdan bir hisse senedi seçerek risk analizi başlatabilirsiniz</p>
      </div>
    );
  }

  return <RiskAnalysisDetailView data={data} />;
};

export default AnalysisResults;
