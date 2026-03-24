import { useState, useEffect, useCallback } from 'react';
import { riskApi } from '../services/api';
import type { BISTStock } from '../types';

interface UseStocksReturn {
  stocks: BISTStock[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useStocks = (): UseStocksReturn => {
  const [stocks, setStocks] = useState<BISTStock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStocks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await riskApi.getAvailableStocks();
      setStocks(response.stocks);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Hisse listesi yüklenemedi';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  return {
    stocks,
    isLoading,
    error,
    refetch: fetchStocks,
  };
};
