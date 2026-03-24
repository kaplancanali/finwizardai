// API Response Types
export interface DetectedEvent {
  event_type: 'high_risk' | 'positive' | 'neutral';
  keyword: string;
  context: string;
  risk_impact: number;
  source_type: 'kap' | 'news';
  source_url?: string;
  source_title?: string;
}

export interface KAPDisclosure {
  title: string;
  content: string;
  date: string;
  disclosure_type?: string;
  stock_symbol: string;
}

export interface NewsArticle {
  title: string;
  summary: string;
  source?: string;
  published_at?: string;
  url?: string;
  stock_symbol?: string;
}

export interface PriceBar {
  date: string;
  close: number;
  volume?: number | null;
}

export interface PriceMetrics {
  return_1y_pct?: number | null;
  volatility_ann?: number | null;
  max_drawdown_pct?: number | null;
  bar_count: number;
  data_available: boolean;
  ticker_used?: string | null;
  /** no_series: Yahoo returned no bars; below_min_bars: not enough trading days */
  source_error?: 'no_series' | 'below_min_bars' | string | null;
}

export interface RiskBreakdown {
  kap_score: number;
  news_score: number;
  sentiment_score: number;
  market_score: number;
  kap_contribution: number;
  news_contribution: number;
  sentiment_contribution: number;
  market_contribution: number;
}

export interface DataSources {
  kap_disclosures: number;
  news_articles: number;
  detected_events: number;
  sentiment_analyses: number;
  price_bars?: number;
}

export interface RiskAnalysisResponse {
  stock: string;
  risk_score: number;
  risk_level: 'very_low' | 'low' | 'medium' | 'high' | 'critical';
  sentiment: 'positive' | 'negative' | 'neutral';
  sentiment_confidence: number;
  events: DetectedEvent[];
  explanations: string[];
  breakdown: RiskBreakdown;
  data_sources: DataSources;
  analyzed_at: string;
  // Extended data
  kap_disclosures: KAPDisclosure[];
  news_articles: NewsArticle[];
  price_history: PriceBar[];
  price_metrics?: PriceMetrics | null;
  color_code: string;
}

export interface BISTStock {
  symbol: string;
  name: string;
  sector: string;
}

export interface StocksResponse {
  count: number;
  stocks: BISTStock[];
  note: string;
}

export interface MarketLeaderboardItem {
  symbol: string;
  name: string;
  sector: string;
  risk_score: number;
  risk_level: RiskLevel;
  sentiment: 'positive' | 'negative' | 'neutral';
  color_code: string;
}

export interface MarketLeaderboardResponse {
  count: number;
  sort_by: 'risk_score' | 'name' | 'sector';
  order: 'asc' | 'desc';
  risk_level_filter?: string | null;
  sector_filter?: string | null;
  items: MarketLeaderboardItem[];
}

// Component Props Types
export interface RiskScoreGaugeProps {
  score: number;
  level: RiskAnalysisResponse['risk_level'];
  size?: 'sm' | 'md' | 'lg';
}

export interface StockSearchProps {
  onSelect: (symbol: string) => void;
  isLoading?: boolean;
}

export interface AnalysisResultsProps {
  data: RiskAnalysisResponse | null;
  isLoading: boolean;
  error: string | null;
}

export interface EventListProps {
  events: DetectedEvent[];
}

export interface ExplanationCardProps {
  explanations: string[];
}

// Utility Types
export type RiskLevel = 'very_low' | 'low' | 'medium' | 'high' | 'critical';

export const RISK_LEVEL_CONFIG: Record<RiskLevel, { 
  label: string; 
  color: string; 
  bgColor: string;
  icon: string;
}> = {
  very_low: { 
    label: 'Çok Düşük Risk', 
    color: 'text-emerald-600', 
    bgColor: 'bg-emerald-50',
    icon: '✅'
  },
  low: { 
    label: 'Düşük Risk', 
    color: 'text-emerald-500', 
    bgColor: 'bg-emerald-50',
    icon: '✓'
  },
  medium: { 
    label: 'Orta Risk', 
    color: 'text-amber-500', 
    bgColor: 'bg-amber-50',
    icon: '⚡'
  },
  high: { 
    label: 'Yüksek Risk', 
    color: 'text-red-500', 
    bgColor: 'bg-red-50',
    icon: '⚠️'
  },
  critical: { 
    label: 'Kritik Risk', 
    color: 'text-violet-600', 
    bgColor: 'bg-violet-50',
    icon: '🚨'
  },
};

export const SENTIMENT_CONFIG: Record<string, { 
  label: string; 
  color: string; 
  bgColor: string;
  icon: string;
}> = {
  positive: { 
    label: 'Pozitif', 
    color: 'text-emerald-600', 
    bgColor: 'bg-emerald-100',
    icon: '😊'
  },
  negative: { 
    label: 'Negatif', 
    color: 'text-red-600', 
    bgColor: 'bg-red-100',
    icon: '😟'
  },
  neutral: { 
    label: 'Nötr', 
    color: 'text-gray-600', 
    bgColor: 'bg-gray-100',
    icon: '😐'
  },
};

// Risk color utilities
export const getRiskColor = (score: number): string => {
  if (score <= 20) return '#10b981'; // Emerald 500 - Very safe
  if (score <= 35) return '#34d399'; // Emerald 400 - Safe  
  if (score <= 50) return '#fbbf24'; // Amber 400 - Attention
  if (score <= 65) return '#f97316'; // Orange 500 - Risky
  if (score <= 80) return '#ef4444'; // Red 500 - Dangerous
  return '#dc2626'; // Red 600 - Critical
};

export const getRiskLabel = (score: number): string => {
  if (score <= 20) return 'Çok Güvenli';
  if (score <= 35) return 'Güvenli';
  if (score <= 50) return 'Dikkat';
  if (score <= 65) return 'Riskli';
  if (score <= 80) return 'Tehlikeli';
  return 'Kritik';
};

export const RISK_GRADIENT = [
  { score: 0, color: '#10b981', label: 'Çok Güvenli' },
  { score: 20, color: '#34d399', label: 'Güvenli' },
  { score: 40, color: '#fbbf24', label: 'Dikkat' },
  { score: 60, color: '#f97316', label: 'Riskli' },
  { score: 80, color: '#ef4444', label: 'Tehlikeli' },
  { score: 100, color: '#dc2626', label: 'Kritik' },
];
