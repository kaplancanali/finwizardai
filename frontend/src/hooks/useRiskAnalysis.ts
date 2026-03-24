import { useState, useCallback } from 'react';
import { riskApi } from '../services/api';
import { formatApiError } from '../utils/apiError';
import type { RiskAnalysisResponse } from '../types';

interface UseRiskAnalysisReturn {
  data: RiskAnalysisResponse | null;
  isLoading: boolean;
  error: string | null;
  analyzeStock: (symbol: string) => Promise<void>;
  clearError: () => void;
}

export const useRiskAnalysis = (): UseRiskAnalysisReturn => {
  const [data, setData] = useState<RiskAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeStock = useCallback(async (symbol: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await riskApi.analyzeStock(symbol);
      setData(response);
    } catch (err) {
      setError(formatApiError(err));
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    data,
    isLoading,
    error,
    analyzeStock,
    clearError,
  };
};
