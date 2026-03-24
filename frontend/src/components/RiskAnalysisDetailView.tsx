import React from 'react';
import { AlertCircle, Activity, Clock, FileText, Newspaper, ExternalLink } from 'lucide-react';
import type { RiskAnalysisResponse } from '../types';
import { SENTIMENT_CONFIG } from '../types';
import RiskScoreGauge from './RiskScoreGauge';
import EventList from './EventList';
import ExplanationCard from './ExplanationCard';
import PriceHistoryChart from './PriceHistoryChart';

export interface RiskAnalysisDetailViewProps {
  data: RiskAnalysisResponse;
  /** Örn. sıralama tablosundan gelen şirket adı */
  companyName?: string;
}

const RiskAnalysisDetailView: React.FC<RiskAnalysisDetailViewProps> = ({ data, companyName }) => {
  const sentimentConfig = SENTIMENT_CONFIG[data.sentiment];
  const formattedDate = new Date(data.analyzed_at).toLocaleString('tr-TR', {
    dateStyle: 'long',
    timeStyle: 'short',
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-primary-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold text-primary-700">{data.stock}</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{data.stock}</h2>
              {companyName && <p className="text-gray-600 text-sm">{companyName}</p>}
              <p className="text-gray-500 flex items-center gap-2 text-sm mt-1">
                <Clock className="w-4 h-4" />
                Analiz: {formattedDate}
              </p>
            </div>
          </div>

          <div
            className={`px-4 py-2 rounded-full ${sentimentConfig.bgColor} ${sentimentConfig.color} font-semibold flex items-center gap-2`}
          >
            <span>{sentimentConfig.icon}</span>
            <span>{sentimentConfig.label}</span>
            <span className="text-xs opacity-75">({(data.sentiment_confidence * 100).toFixed(0)}%)</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          <div className="flex justify-center">
            <RiskScoreGauge score={data.risk_score} level={data.risk_level} size="lg" />
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Skor Bileşenleri</h3>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    KAP Açıklamaları
                  </span>
                  <span className="font-semibold text-right">
                    skor {data.breakdown.kap_score.toFixed(1)} → katkı {data.breakdown.kap_contribution.toFixed(2)}
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${data.breakdown.kap_score}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 flex items-center gap-2">
                    <Newspaper className="w-4 h-4" />
                    Haber Analizi
                  </span>
                  <span className="font-semibold text-right">
                    skor {data.breakdown.news_score.toFixed(1)} → katkı {data.breakdown.news_contribution.toFixed(2)}
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 rounded-full" style={{ width: `${data.breakdown.news_score}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Duygu Analizi</span>
                  <span className="font-semibold text-right">
                    skor {data.breakdown.sentiment_score.toFixed(1)} → katkı{' '}
                    {data.breakdown.sentiment_contribution.toFixed(2)}
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{ width: `${data.breakdown.sentiment_score}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    Piyasa / fiyat (volatilite)
                  </span>
                  <span className="font-semibold text-right">
                    skor {data.breakdown.market_score.toFixed(1)} → katkı {data.breakdown.market_contribution.toFixed(2)}
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-violet-500 rounded-full"
                    style={{ width: `${data.breakdown.market_score}%` }}
                  />
                </div>
                {data.price_metrics && !data.price_metrics.data_available && (
                  <p className="text-xs text-amber-600 mt-1">
                    {data.price_metrics.source_error === 'no_series'
                      ? `Yahoo Finance bu sembol için günlük fiyat döndürmedi (${data.price_metrics.ticker_used ?? '—'}). Sembol veri akışında olmayabilir. Piyasa ağırlığı diğer bileşenlere dağıtıldı.`
                      : data.price_metrics.source_error === 'below_min_bars'
                        ? 'Çok az işlem günü var; piyasa ağırlığı diğer bileşenlere dağıtıldı.'
                        : 'Yetersiz günlük veri; piyasa ağırlığı diğer bileşenlere dağıtıldı.'}
                  </p>
                )}
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-gray-900">Toplam Risk Skoru</span>
                <span className="text-2xl font-bold text-primary-600">{data.risk_score}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl shadow p-4 text-center">
          <div className="text-3xl font-bold text-primary-600">{data.data_sources.kap_disclosures}</div>
          <div className="text-sm text-gray-500">KAP Açıklaması</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 text-center">
          <div className="text-3xl font-bold text-amber-600">{data.data_sources.news_articles}</div>
          <div className="text-sm text-gray-500">Haber Makalesi</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 text-center">
          <div className="text-3xl font-bold text-red-600">{data.data_sources.detected_events}</div>
          <div className="text-sm text-gray-500">Tespit Edilen Olay</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 text-center">
          <div className="text-3xl font-bold text-emerald-600">{data.data_sources.sentiment_analyses}</div>
          <div className="text-sm text-gray-500">Duygu Analizi</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 text-center col-span-2 sm:col-span-1">
          <div className="text-3xl font-bold text-violet-600">{data.data_sources.price_bars ?? 0}</div>
          <div className="text-sm text-gray-500">Günlük Fiyat</div>
        </div>
      </div>

      {((data.price_history?.length ?? 0) > 0 || data.price_metrics?.data_available) && (
        <div className="space-y-4">
          {data.price_metrics?.data_available && (
            <div className="grid sm:grid-cols-3 gap-3">
              <div className="bg-white rounded-xl shadow p-4 text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {data.price_metrics.return_1y_pct != null
                    ? `${data.price_metrics.return_1y_pct >= 0 ? '+' : ''}${data.price_metrics.return_1y_pct.toFixed(1)}%`
                    : '—'}
                </div>
                <div className="text-xs text-gray-500">1 yıl getiri</div>
              </div>
              <div className="bg-white rounded-xl shadow p-4 text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {data.price_metrics.volatility_ann != null
                    ? `${(data.price_metrics.volatility_ann * 100).toFixed(1)}%`
                    : '—'}
                </div>
                <div className="text-xs text-gray-500">Yıllık volatilite</div>
              </div>
              <div className="bg-white rounded-xl shadow p-4 text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {data.price_metrics.max_drawdown_pct != null
                    ? `${data.price_metrics.max_drawdown_pct.toFixed(1)}%`
                    : '—'}
                </div>
                <div className="text-xs text-gray-500">Maks. düşüş</div>
              </div>
            </div>
          )}
          {(data.price_history?.length ?? 0) > 0 && (
            <PriceHistoryChart bars={data.price_history ?? []} tickerLabel={data.price_metrics?.ticker_used} />
          )}
        </div>
      )}

      {(data.kap_disclosures.length > 0 || data.news_articles.length > 0) && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-600" />
              KAP açıklama metinleri
            </h3>
            {data.kap_disclosures.length === 0 ? (
              <p className="text-sm text-gray-500">KAP içeriği yok.</p>
            ) : (
              <ul className="space-y-4 max-h-[28rem] overflow-y-auto pr-1">
                {data.kap_disclosures.map((d, i) => (
                  <li key={`${d.title}-${i}`} className="border border-gray-100 rounded-xl p-4 bg-gray-50/80">
                    <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
                      <span className="font-medium text-gray-900 text-sm">{d.title}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(d.date).toLocaleDateString('tr-TR')}
                        {d.disclosure_type ? ` · ${d.disclosure_type}` : ''}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap break-words max-h-40 overflow-y-auto">
                      {d.content}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Newspaper className="w-5 h-5 text-amber-600" />
              Haber içerikleri
            </h3>
            {data.news_articles.length === 0 ? (
              <p className="text-sm text-gray-500">Haber içeriği yok.</p>
            ) : (
              <ul className="space-y-4 max-h-[28rem] overflow-y-auto pr-1">
                {data.news_articles.map((a, i) => (
                  <li key={`${a.title}-${i}`} className="border border-gray-100 rounded-xl p-4 bg-gray-50/80">
                    <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                      <span className="font-medium text-gray-900 text-sm">{a.title}</span>
                      {a.published_at && (
                        <span className="text-xs text-gray-500 shrink-0">
                          {new Date(a.published_at).toLocaleString('tr-TR')}
                        </span>
                      )}
                    </div>
                    {a.source && <p className="text-xs text-gray-500 mb-2">Kaynak: {a.source}</p>}
                    <p className="text-sm text-gray-700 whitespace-pre-wrap break-words max-h-36 overflow-y-auto">
                      {a.summary}
                    </p>
                    {a.url && (
                      <a
                        href={a.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 mt-3 text-xs text-primary-600 hover:underline"
                      >
                        <ExternalLink className="w-3 h-3" />
                        Habere git
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Tespit Edilen Olaylar
          </h3>
          <EventList events={data.events} />
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Analiz Açıklamaları
          </h3>
          <ExplanationCard explanations={data.explanations} />
        </div>
      </div>
    </div>
  );
};

export default RiskAnalysisDetailView;
