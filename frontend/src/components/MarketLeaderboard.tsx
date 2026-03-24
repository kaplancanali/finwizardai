import React, { useMemo, useState, useCallback, useEffect } from 'react';
import { Loader2, RefreshCcw, X } from 'lucide-react';

import { riskApi } from '../services/api';
import { formatApiError } from '../utils/apiError';
import type { MarketLeaderboardItem, RiskAnalysisResponse, RiskLevel } from '../types';
import { RISK_LEVEL_CONFIG } from '../types';
import RiskAnalysisDetailView from './RiskAnalysisDetailView';

const levelOptions: Array<{ value: '' | RiskLevel; label: string }> = [
  { value: '', label: 'Tümü' },
  { value: 'very_low', label: 'Çok Düşük' },
  { value: 'low', label: 'Düşük' },
  { value: 'medium', label: 'Orta' },
  { value: 'high', label: 'Yüksek' },
];

const MarketLeaderboard: React.FC = () => {
  const [items, setItems] = useState<MarketLeaderboardItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [riskLevel, setRiskLevel] = useState<string>('');
  const [sortBy, setSortBy] = useState<'risk_score' | 'name' | 'sector'>('risk_score');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');

  const [detailOpen, setDetailOpen] = useState(false);
  const [detailItem, setDetailItem] = useState<MarketLeaderboardItem | null>(null);
  const [detailData, setDetailData] = useState<RiskAnalysisResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const sectors = useMemo(
    () => Array.from(new Set(items.map((x) => x.sector))).sort((a, b) => a.localeCompare(b)),
    [items]
  );
  const [sector, setSector] = useState<string>('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await riskApi.getMarketLeaderboard({
        sort_by: sortBy,
        order,
        risk_level: riskLevel || undefined,
        sector: sector || undefined,
      });
      setItems(data.items);
    } catch (e) {
      setError(formatApiError(e));
    } finally {
      setLoading(false);
    }
  };

  const closeDetail = useCallback(() => {
    setDetailOpen(false);
    setDetailItem(null);
    setDetailData(null);
    setDetailError(null);
    setDetailLoading(false);
  }, []);

  const openDetail = useCallback(async (item: MarketLeaderboardItem) => {
    setDetailItem(item);
    setDetailOpen(true);
    setDetailData(null);
    setDetailError(null);
    setDetailLoading(true);
    try {
      const analysis = await riskApi.analyzeStock(item.symbol);
      setDetailData(analysis);
    } catch (e) {
      setDetailError(formatApiError(e));
    } finally {
      setDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!detailOpen) return;
    const onKey = (ev: KeyboardEvent) => {
      if (ev.key === 'Escape') closeDetail();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [detailOpen, closeDetail]);

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900">Piyasa Risk Sıralaması (BIST30)</h3>
        <button
          onClick={load}
          className="px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 flex items-center gap-2"
          disabled={loading}
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCcw className="w-4 h-4" />}
          Hepsini Analiz Et
        </button>
      </div>

      <p className="text-sm text-gray-500 mb-4">
        Satıra tıklayarak o hissenin KAP / haber metinleri, olaylar ve skor detayını görüntüleyebilirsiniz.
      </p>

      <div className="grid md:grid-cols-4 gap-3 mb-4">
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'risk_score' | 'name' | 'sector')}
          className="border rounded-lg px-3 py-2"
        >
          <option value="risk_score">Skora Göre</option>
          <option value="name">İsme Göre</option>
          <option value="sector">Sektöre Göre</option>
        </select>
        <select value={order} onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')} className="border rounded-lg px-3 py-2">
          <option value="desc">Azalan</option>
          <option value="asc">Artan</option>
        </select>
        <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)} className="border rounded-lg px-3 py-2">
          {levelOptions.map((opt) => (
            <option key={opt.label} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <select value={sector} onChange={(e) => setSector(e.target.value)} className="border rounded-lg px-3 py-2">
          <option value="">Tüm Sektörler</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="p-3 rounded bg-red-50 text-red-600 mb-3 text-sm whitespace-pre-wrap break-words">{error}</div>
      )}

      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2 pr-2">#</th>
              <th className="py-2 pr-2">Sembol</th>
              <th className="py-2 pr-2">Şirket</th>
              <th className="py-2 pr-2">Sektör</th>
              <th className="py-2 pr-2">Risk</th>
              <th className="py-2 pr-2">Seviye</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr
                key={item.symbol}
                role="button"
                tabIndex={0}
                onClick={() => openDetail(item)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openDetail(item);
                  }
                }}
                className="border-b hover:bg-primary-50/60 cursor-pointer transition-colors"
              >
                <td className="py-2 pr-2">{idx + 1}</td>
                <td className="py-2 pr-2 font-semibold">{item.symbol}</td>
                <td className="py-2 pr-2">{item.name}</td>
                <td className="py-2 pr-2">{item.sector}</td>
                <td className="py-2 pr-2">
                  <span className="font-semibold" style={{ color: item.color_code }}>
                    {item.risk_score}
                  </span>
                </td>
                <td className="py-2 pr-2">
                  <span
                    className={`px-2 py-1 rounded-full text-xs ${RISK_LEVEL_CONFIG[item.risk_level].bgColor} ${RISK_LEVEL_CONFIG[item.risk_level].color}`}
                  >
                    {RISK_LEVEL_CONFIG[item.risk_level].label}
                  </span>
                </td>
              </tr>
            ))}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-gray-500">
                  Henüz analiz yapılmadı. &quot;Hepsini Analiz Et&quot; butonuna basın.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {detailOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="leaderboard-detail-title"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) closeDetail();
          }}
        >
          <div className="bg-gray-100 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden">
            <div className="flex items-center justify-between gap-3 px-4 py-3 border-b bg-white shrink-0">
              <h2 id="leaderboard-detail-title" className="text-lg font-semibold text-gray-900 truncate">
                {detailItem ? `${detailItem.symbol} — ${detailItem.name}` : 'Detay'}
              </h2>
              <button
                type="button"
                onClick={closeDetail}
                className="p-2 rounded-full hover:bg-gray-100 text-gray-600 shrink-0"
                aria-label="Kapat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {detailLoading && (
                <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                  <Loader2 className="w-10 h-10 text-primary-600 animate-spin mx-auto mb-3" />
                  <p className="text-gray-600">Analiz detayı yükleniyor…</p>
                </div>
              )}
              {!detailLoading && detailError && (
                <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center text-red-700">{detailError}</div>
              )}
              {!detailLoading && detailData && detailItem && (
                <RiskAnalysisDetailView data={detailData} companyName={detailItem.name} />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketLeaderboard;
