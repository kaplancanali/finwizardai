import React from 'react';
import { AlertTriangle, TrendingUp, Minus, ExternalLink, FileText } from 'lucide-react';
import type { EventListProps, DetectedEvent } from '../types';

interface ExtendedEventListProps extends EventListProps {
  onViewAll?: () => void;
}

const EventList: React.FC<ExtendedEventListProps> = ({ events, onViewAll }) => {
  if (events.length === 0) {
    return (
      <div className="bg-gray-50 rounded-xl p-6 text-center">
        <Minus className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-500">Tespit edilen olay bulunamadı</p>
      </div>
    );
  }

  const getEventIcon = (type: DetectedEvent['event_type']) => {
    switch (type) {
      case 'high_risk':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'positive':
        return <TrendingUp className="w-5 h-5 text-emerald-500" />;
      default:
        return <Minus className="w-5 h-5 text-gray-400" />;
    }
  };

  const getEventTypeLabel = (type: DetectedEvent['event_type']) => {
    switch (type) {
      case 'high_risk':
        return 'Risk Sinyali';
      case 'positive':
        return 'Pozitif Gelişme';
      default:
        return 'Olay';
    }
  };

  const getEventTypeColor = (type: DetectedEvent['event_type']) => {
    switch (type) {
      case 'high_risk':
        return 'bg-red-50 border-red-200';
      case 'positive':
        return 'bg-emerald-50 border-emerald-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getImpactColor = (impact: number) => {
    if (impact <= -7) return 'text-red-600 bg-red-100';
    if (impact <= -4) return 'text-orange-600 bg-orange-100';
    if (impact >= 4) return 'text-emerald-600 bg-emerald-100';
    if (impact > 0) return 'text-green-600 bg-green-100';
    return 'text-gray-600 bg-gray-100';
  };

  // Group events by type
  const highRiskEvents = events.filter(e => e.event_type === 'high_risk');
  const positiveEvents = events.filter(e => e.event_type === 'positive');
  const neutralEvents = events.filter(e => e.event_type === 'neutral');

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-red-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-600">{highRiskEvents.length}</div>
          <div className="text-xs text-red-600">Risk Sinyali</div>
        </div>
        <div className="bg-emerald-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-emerald-600">{positiveEvents.length}</div>
          <div className="text-xs text-emerald-600">Pozitif</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-600">{neutralEvents.length}</div>
          <div className="text-xs text-gray-600">Nötr</div>
        </div>
      </div>

      {/* Event List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {events.map((event, index) => (
          <div
            key={index}
            className={`p-4 rounded-xl border ${getEventTypeColor(event.event_type)} transition-all hover:shadow-md`}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5">{getEventIcon(event.event_type)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-gray-900">
                    {event.keyword}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getImpactColor(event.risk_impact)}`}>
                    Etki: {event.risk_impact > 0 ? '+' : ''}{event.risk_impact}
                  </span>
                  <span className="text-xs text-gray-500 bg-white px-2 py-0.5 rounded-full border">
                    {getEventTypeLabel(event.event_type)}
                  </span>
                </div>
                
                {/* Source Information */}
                {event.source_title && (
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <FileText className="w-3 h-3" />
                    <span className="truncate max-w-xs">{event.source_title}</span>
                    <span className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">
                      {event.source_type === 'kap' ? 'KAP' : 'Haber'}
                    </span>
                  </div>
                )}
                
                <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                  {event.context}
                </p>
                
                {/* Action Links */}
                {(event.source_url || onViewAll) && (
                  <div className="mt-3 flex gap-2">
                    {event.source_url && (
                      <a
                        href={event.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs px-3 py-1.5 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1 text-gray-700"
                      >
                        <ExternalLink className="w-3 h-3" />
                        Kaynağı Gör
                      </a>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* View All Button */}
      {events.length > 0 && onViewAll && (
        <button
          onClick={onViewAll}
          className="w-full mt-4 py-2 text-sm text-primary-600 font-medium hover:bg-primary-50 rounded-lg transition-colors"
        >
          Tüm {events.length} Olayı Görüntüle →
        </button>
      )}
    </div>
  );
};

export default EventList;
