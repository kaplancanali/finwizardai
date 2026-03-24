import axios from 'axios';
import type {
  RiskAnalysisResponse,
  StocksResponse,
  MarketLeaderboardResponse,
} from '../types';

function trimBase(url: string): string {
  return url.replace(/\/$/, '');
}

/** Build-time (Vite); boşsa /api/v1, sonra initApiFromRuntimeConfig ile api-config.json güncelleyebilir */
const viteApi = import.meta.env.VITE_API_URL?.trim();
const initialBase = viteApi ? trimBase(viteApi) : '/api/v1';

const apiClient = axios.create({
  baseURL: initialBase,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

/** Şu an kullanılan taban (axios ile aynı) — hata mesajları için */
export function getEffectiveApiBase(): string {
  return trimBase(String(apiClient.defaults.baseURL || '/api/v1'));
}

/**
 * VITE_API_URL yoksa /api-config.json okur (public/ → kök URL).
 * Backend adresini buraya yazıp yeniden deploy edin; Vercel env şart değil.
 */
export async function initApiFromRuntimeConfig(): Promise<void> {
  if (viteApi) return;
  try {
    const res = await fetch('/api-config.json', { cache: 'no-store' });
    if (!res.ok) return;
    const data = (await res.json()) as { apiBase?: string };
    const b = data.apiBase?.trim();
    if (b) {
      apiClient.defaults.baseURL = trimBase(b);
    }
  } catch {
    /* ağ veya JSON yok — varsayılan /api/v1 */
  }
}

export const riskApi = {
  async analyzeStock(symbol: string): Promise<RiskAnalysisResponse> {
    const response = await apiClient.get<RiskAnalysisResponse>(`/risk/${symbol}`);
    return response.data;
  },

  async getAvailableStocks(): Promise<StocksResponse> {
    const response = await apiClient.get<StocksResponse>('/stocks');
    return response.data;
  },

  async healthCheck(): Promise<{ status: string; version: string; timestamp: number }> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  async clearCache(): Promise<{ message: string }> {
    const response = await apiClient.post('/cache/clear');
    return response.data;
  },

  async getMarketLeaderboard(params?: {
    sort_by?: 'risk_score' | 'name' | 'sector';
    order?: 'asc' | 'desc';
    risk_level?: string;
    sector?: string;
  }): Promise<MarketLeaderboardResponse> {
    const response = await apiClient.get<MarketLeaderboardResponse>('/market/leaderboard', {
      params,
    });
    return response.data;
  },
};

export default apiClient;
