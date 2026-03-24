import React from 'react';
import { BarChart3 } from 'lucide-react';
import Header from './components/Header';
import Footer from './components/Footer';
import StockSearch from './components/StockSearch';
import AnalysisResults from './components/AnalysisResults';
import MarketLeaderboard from './components/MarketLeaderboard';
import { useRiskAnalysis } from './hooks/useRiskAnalysis';

const App: React.FC = () => {
  const { data, isLoading, error, analyzeStock } = useRiskAnalysis();
  const [activeTab, setActiveTab] = React.useState<'single' | 'market'>('single');

  const handleStockSelect = (symbol: string) => {
    analyzeStock(symbol);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Finansal Risk Analizi
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            BIST30 hisseleri için AI destekli risk analizi. 
            KAP açıklamaları, haberler ve duygu analizi ile kapsamlı değerlendirme.
          </p>
        </div>

        <div className="mb-6 flex justify-center gap-2">
          <button
            className={`px-4 py-2 rounded-lg border ${activeTab === 'single' ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-200'}`}
            onClick={() => setActiveTab('single')}
          >
            Tekli Analiz
          </button>
          <button
            className={`px-4 py-2 rounded-lg border ${activeTab === 'market' ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-200'}`}
            onClick={() => setActiveTab('market')}
          >
            Piyasa Sıralaması
          </button>
        </div>

        {activeTab === 'single' && (
          <>
            {/* Search Section */}
            <div className="mb-12">
              <StockSearch onSelect={handleStockSelect} isLoading={isLoading} />
            </div>

        {/* Popular Stocks Quick Select */}
        {!data && !isLoading && (
          <div className="mb-12 animate-fade-in">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4 text-center">
              Popüler Hisseler
            </h3>
            <div className="flex flex-wrap justify-center gap-3">
              {['THYAO', 'GARAN', 'ASELS', 'KCHOL', 'EREGL', 'BIMAS'].map((symbol) => (
                <button
                  key={symbol}
                  onClick={() => handleStockSelect(symbol)}
                  className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:border-primary-500 hover:text-primary-600 transition-all shadow-sm hover:shadow"
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>
        )}

            {/* Analysis Results */}
            <AnalysisResults data={data} isLoading={isLoading} error={error} />

            {/* Features Section (shown when no analysis) */}
            {!data && !isLoading && (
          <div className="mt-16 grid md:grid-cols-3 gap-8 animate-slide-up">
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">KAP Analizi</h3>
              <p className="text-gray-600 text-sm">
                Kamuyu Aydınlatma Platformu'ndaki resmi açıklamaları analiz eder.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2 2 0 00-2-2h-2" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Haber Analizi</h3>
              <p className="text-gray-600 text-sm">
                Finansal haber kaynaklarından gelişmeleri takip eder.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Duygu Analizi</h3>
              <p className="text-gray-600 text-sm">
                Türkçe BERT modeli ile metin duygu analizi yapar.
              </p>
            </div>
          </div>
            )}
          </>
        )}

        {activeTab === 'market' && <MarketLeaderboard />}
      </main>

      <Footer />
    </div>
  );
};

export default App;
