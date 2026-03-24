import React, { useState, useRef, useEffect } from 'react';
import { Search, ChevronDown, Loader2 } from 'lucide-react';
import { useStocks } from '../hooks/useStocks';
import type { StockSearchProps } from '../types';

const StockSearch: React.FC<StockSearchProps> = ({ onSelect, isLoading = false }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const { stocks, isLoading: stocksLoading } = useStocks();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter stocks based on search term
  const filteredStocks = stocks.filter(
    (stock) =>
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.sector.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (symbol: string) => {
    setSearchTerm(symbol);
    setIsOpen(false);
    onSelect(symbol);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      onSelect(searchTerm.trim().toUpperCase());
      setIsOpen(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto" ref={dropdownRef}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <Search className="absolute left-4 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder="Hisse senedi ara (örn: THYAO, GARAN, ASELS...)"
            className="w-full pl-12 pr-32 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none transition-colors"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            className="absolute right-24 p-2 text-gray-400 hover:text-gray-600"
            disabled={isLoading}
          >
            <ChevronDown className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
          <button
            type="submit"
            disabled={isLoading || !searchTerm.trim()}
            className="absolute right-2 px-6 py-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analiz...
              </>
            ) : (
              'Analiz Et'
            )}
          </button>
        </div>

        {/* Dropdown */}
        {isOpen && !isLoading && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-80 overflow-y-auto z-50">
            {stocksLoading ? (
              <div className="p-4 text-center text-gray-500">
                <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                Hisse listesi yükleniyor...
              </div>
            ) : filteredStocks.length > 0 ? (
              <div className="p-2">
                <div className="text-xs font-semibold text-gray-400 uppercase px-3 py-2">
                  BIST30 Hisseleri
                </div>
                {filteredStocks.map((stock) => (
                  <button
                    key={stock.symbol}
                    type="button"
                    onClick={() => handleSelect(stock.symbol)}
                    className="w-full text-left px-3 py-3 rounded-lg hover:bg-gray-50 flex items-center justify-between group transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                        <span className="text-primary-700 font-bold text-sm">
                          {stock.symbol.slice(0, 3)}
                        </span>
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{stock.symbol}</div>
                        <div className="text-sm text-gray-500">{stock.name}</div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                      {stock.sector}
                    </div>
                  </button>
                ))}
              </div>
            ) : searchTerm ? (
              <div className="p-4 text-center text-gray-500">
                <p>"{searchTerm}" için sonuç bulunamadı</p>
                <p className="text-sm mt-1">Enter ile aramaya devam edebilirsiniz</p>
              </div>
            ) : (
              <div className="p-4 text-center text-gray-400">
                Aramaya başlamak için yazın...
              </div>
            )}
          </div>
        )}
      </form>
    </div>
  );
};

export default StockSearch;
