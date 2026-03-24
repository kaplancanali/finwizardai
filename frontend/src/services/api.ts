import axios from 'axios';
import type {
  RiskAnalysisResponse,
  StocksResponse,
  MarketLeaderboardResponse,
} from '../types';

const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

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
