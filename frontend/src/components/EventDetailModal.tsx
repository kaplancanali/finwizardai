import React from 'react';
import { X, ExternalLink, AlertTriangle, TrendingUp, Minus } from 'lucide-react';
import type { DetectedEvent } from '../types';

interface EventDetailModalProps {
  events: DetectedEvent[];
  onClose: () => void;
  stockSymbol: string;
}

const EventDetailModal: React.FC<EventDetailModalProps> = ({ 
  events, 
  onClose, 
  stockSymbol 
}) => {
  if (!events.length) return null;

  // Group events by type
  const highRiskEvents = events.filter(e => e.event_type === 'high_risk');
  const positiveEvents = events.filter(e => e.event_type === 'positive');
  const neutralEvents = events.filter(e => e.event_type === 'neutral');

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-gray-50 to-white">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{stockSymbol} - Tüm Olaylar</h2>
            <p className="text-sm text-gray-500 mt-1">
              {events.length} olay tespit edildi
              {highRiskEvents.length > 0 && (
                <span className="ml-2 text-red-600 font-medium">
                  ({highRiskEvents.length} risk sinyali)
                </span>
              )}
            </p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 border-b">
          <div className="bg-white rounded-lg p-3 text-center shadow-sm">
            <div className="text-2xl font-bold text-red-600">{highRiskEvents.length}</div>
            <div className="text-xs text-gray-500">Risk Sinyali</div>
          </div>
          <div className="bg-white rounded-lg p-3 text-center shadow-sm">
            <div className="text-2xl font-bold text-emerald-600">{positiveEvents.length}</div>
            <div className="text-xs text-gray-500">Pozitif</div>
          </div>
          <div className="bg-white rounded-lg p-3 text-center shadow-sm">
            <div className="text-2xl font-bold text-gray-600">{neutralEvents.length}</div>
            <div className="text-xs text-gray-500">Nötr</div>
          </div>
        </div>

        {/* Event List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {events.map((event, index) => (
            <div 
              key={index}
              className={`p-4 rounded-xl border-l-4 shadow-sm hover:shadow-md transition-shadow ${
                event.event_type === 'high_risk' ? 'border-red-500 bg-red-50' :
                event.event_type === 'positive' ? 'border-emerald-500 bg-emerald-50' :
                'border-gray-400 bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  {event.event_type === 'high_risk' && <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />}
                  {event.event_type === 'positive' && <TrendingUp className="w-5 h-5 text-emerald-500 flex-shrink-0" />}
                  {event.event_type === 'neutral' && <Minus className="w-5 h-5 text-gray-500 flex-shrink-0" />}
                  <div>
                    <h4 className="font-semibold text-gray-900">{event.keyword}</h4>
                    {event.source_title && (
                      <p className="text-sm text-gray-500">{event.source_title}</p>
                    )}
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  event.risk_impact > 0 ? 'bg-emerald-100 text-emerald-700' :
                  event.risk_impact < 0 ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  Etki: {event.risk_impact > 0 ? '+' : ''}{event.risk_impact}
                </span>
              </div>
              
              <p className="mt-3 text-gray-700 text-sm leading-relaxed">
                {event.context}
              </p>
              
              {event.source_url && (
                <a
                  href={event.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 font-medium hover:underline"
                >
                  <ExternalLink className="w-4 h-4" />
                  Kaynağı Görüntüle
                </a>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 text-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};

export default EventDetailModal;
