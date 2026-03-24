"""
Risk scoring engine for financial analysis.

Combines signals from KAP disclosures, news sentiment, and event detection
to produce an overall risk score with detailed explanations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.schemas import (
    KAPDisclosure,
    NewsArticle,
    SentimentResult,
    DetectedEvent,
    EventType,
    SentimentLabel,
    RiskAnalysisResponse,
    RiskBreakdown,
    PriceMetrics,
)
from utils.config import get_settings
from utils.logger import get_logger
from utils.cache import cached
from scrapers.kap_scraper import get_kap_scraper
from scrapers.news_scraper import get_news_scraper
from nlp.sentiment import get_sentiment_analyzer
from nlp.event_detector import get_event_detector
from services.price_history import (
    calculate_market_risk_score,
    get_price_history_service,
)

logger = get_logger("risk_engine")


class RiskScoringEngine:
    """
    Main risk scoring engine that combines multiple data sources.
    
    Calculates risk scores using weighted combination of:
    - KAP disclosure analysis
    - News sentiment analysis
    - Overall sentiment score
    - Market / price volatility (configurable weight, Yahoo Finance daily history)
    
    Attributes:
        weights: Dictionary of scoring weights
        thresholds: Risk level thresholds
    """
    
    def __init__(self):
        """Initialize the risk scoring engine with configuration."""
        settings = get_settings()
        
        self.weights = {
            "kap": settings.KAP_WEIGHT,
            "news": settings.NEWS_WEIGHT,
            "sentiment": settings.SENTIMENT_WEIGHT,
            "price": settings.PRICE_WEIGHT,
        }
        
        self.thresholds = {
            "low": settings.RISK_LOW_THRESHOLD,
            "medium": settings.RISK_MEDIUM_THRESHOLD,
            "high": settings.RISK_HIGH_THRESHOLD
        }
        
        # Initialize components
        self.kap_scraper = get_kap_scraper()
        self.news_scraper = get_news_scraper()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.event_detector = get_event_detector()
        self.price_history = get_price_history_service()

        logger.info(
            f"Risk engine initialized with weights: "
            f"KAP={self.weights['kap']}, "
            f"News={self.weights['news']}, "
            f"Sentiment={self.weights['sentiment']}, "
            f"Price={self.weights['price']}"
        )
    
    @cached(ttl=300)  # Cache for 5 minutes
    def analyze_stock(self, stock_symbol: str) -> RiskAnalysisResponse:
        """
        Perform complete risk analysis for a stock symbol.
        
        Args:
            stock_symbol: Stock symbol (e.g., "THYAO", "GARAN")
            
        Returns:
            RiskAnalysisResponse with full analysis results
        """
        logger.info(f"Starting risk analysis for {stock_symbol}")
        start_time = datetime.utcnow()
        
        # 1. Fetch data
        logger.info(f"Fetching data sources for {stock_symbol}")
        disclosures = self.kap_scraper.fetch_disclosures(stock_symbol)
        news_articles = self.news_scraper.fetch_news(stock_symbol)

        price_bars, price_metrics, price_sufficient = self.price_history.get_history(stock_symbol)
        market_score = calculate_market_risk_score(
            price_metrics.return_1y_pct,
            price_metrics.volatility_ann,
            price_metrics.max_drawdown_pct,
            price_metrics.data_available,
        )

        settings = get_settings()
        w_kap = settings.KAP_WEIGHT
        w_news = settings.NEWS_WEIGHT
        w_sent = settings.SENTIMENT_WEIGHT
        w_price = settings.PRICE_WEIGHT
        if (not price_sufficient or not price_metrics.data_available) and settings.PRICE_WEIGHT_ZERO_IF_MISSING:
            rest = w_kap + w_news + w_sent
            if rest > 0:
                scale = 1.0 / rest
                w_kap, w_news, w_sent = w_kap * scale, w_news * scale, w_sent * scale
            w_price = 0.0

        # 2. Analyze sentiment
        logger.info(f"Analyzing sentiment for {stock_symbol}")
        kap_sentiments = self.sentiment_analyzer.analyze_disclosures(disclosures)
        news_sentiments = self.sentiment_analyzer.analyze_news(news_articles)
        all_sentiments = kap_sentiments + news_sentiments
        
        # 3. Detect events
        logger.info(f"Detecting events for {stock_symbol}")
        kap_events = self.event_detector.analyze_disclosures(disclosures)
        news_events = self.event_detector.analyze_news(news_articles)
        all_events = kap_events + news_events
        
        # 4. Calculate component scores
        kap_score = self._calculate_kap_score(disclosures, kap_events, kap_sentiments)
        news_score = self._calculate_news_score(news_articles, news_events, news_sentiments)
        sentiment_score = self._calculate_sentiment_score(all_sentiments)
        
        # 5. Calculate weighted overall score
        overall_score = (
            w_kap * kap_score +
            w_news * news_score +
            w_sent * sentiment_score +
            w_price * market_score
        )
        
        # Normalize and convert to integer 0-100
        final_risk_score = int(round(max(0.0, min(100.0, overall_score))))
        
        # 6. Determine risk level
        risk_level = self._get_risk_level(final_risk_score)
        
        # 7. Aggregate sentiment
        aggregated_sentiment = self.sentiment_analyzer.aggregate_sentiment(all_sentiments)
        
        # 8. Generate explanations
        explanations = self._generate_explanations(
            final_risk_score,
            kap_score,
            news_score,
            sentiment_score,
            market_score,
            price_metrics,
            w_kap,
            w_news,
            w_sent,
            w_price,
            all_events,
            disclosures,
            news_articles,
        )
        
        # 9. Build response
        analysis_duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Risk analysis completed for {stock_symbol}: "
            f"score={final_risk_score}, level={risk_level}, "
            f"duration={analysis_duration:.2f}s"
        )
        
        return RiskAnalysisResponse(
            stock=stock_symbol.upper(),
            risk_score=final_risk_score,
            risk_level=risk_level,
            sentiment=aggregated_sentiment["label"],
            sentiment_confidence=aggregated_sentiment["confidence"],
            events=all_events[:10],  # Limit to top 10 events
            explanations=explanations,
            breakdown=RiskBreakdown(
                kap_score=round(kap_score, 2),
                news_score=round(news_score, 2),
                sentiment_score=round(sentiment_score, 2),
                market_score=round(market_score, 2),
                kap_contribution=round(kap_score * w_kap, 2),
                news_contribution=round(news_score * w_news, 2),
                sentiment_contribution=round(sentiment_score * w_sent, 2),
                market_contribution=round(market_score * w_price, 2),
            ),
            data_sources={
                "kap_disclosures": len(disclosures),
                "news_articles": len(news_articles),
                "detected_events": len(all_events),
                "sentiment_analyses": len(all_sentiments),
                "price_bars": len(price_bars),
            },
            analyzed_at=datetime.utcnow(),
            # Extended data for detailed analysis
            kap_disclosures=disclosures,
            news_articles=news_articles,
            price_history=price_bars,
            price_metrics=price_metrics,
            color_code=self._get_color_code(final_risk_score),
        )
    
    def _calculate_kap_score(
        self, 
        disclosures: List[KAPDisclosure],
        events: List[DetectedEvent],
        sentiments: List[SentimentResult]
    ) -> float:
        """
        Calculate KAP disclosure risk score.
        
        Args:
            disclosures: List of KAP disclosures
            events: Detected events from disclosures
            sentiments: Sentiment analysis results
            
        Returns:
            Risk score 0-100
        """
        if not disclosures:
            return 50.0  # Neutral baseline
        
        # Start with base score from event detection
        base_score = self.event_detector.calculate_event_risk_score(events)
        
        # Adjust based on sentiment
        if sentiments:
            negative_ratio = sum(
                1 for s in sentiments if s.label == SentimentLabel.NEGATIVE
            ) / len(sentiments)
            
            # More negative sentiment = higher risk
            sentiment_adjustment = negative_ratio * 15
        else:
            sentiment_adjustment = 0
        
        # Adjust for disclosure count (more disclosures = more information = slightly lower risk)
        volume_adjustment = max(-5, -len(disclosures) * 0.5)
        
        score = base_score + sentiment_adjustment + volume_adjustment
        return max(0.0, min(100.0, score))
    
    def _calculate_news_score(
        self,
        articles: List[NewsArticle],
        events: List[DetectedEvent],
        sentiments: List[SentimentResult]
    ) -> float:
        """
        Calculate news-based risk score.
        
        Args:
            articles: List of news articles
            events: Detected events from news
            sentiments: Sentiment analysis results
            
        Returns:
            Risk score 0-100
        """
        if not articles:
            return 50.0  # Neutral baseline
        
        # Base score from events
        base_score = self.event_detector.calculate_event_risk_score(events)
        
        # Adjust based on news sentiment
        if sentiments:
            negative_count = sum(1 for s in sentiments if s.label == SentimentLabel.NEGATIVE)
            positive_count = sum(1 for s in sentiments if s.label == SentimentLabel.POSITIVE)
            
            # News is often more sensational - weight negative more heavily
            if negative_count > positive_count:
                sentiment_adjustment = 10 * (negative_count - positive_count) / len(sentiments)
            elif positive_count > negative_count:
                sentiment_adjustment = -5 * (positive_count - negative_count) / len(sentiments)
            else:
                sentiment_adjustment = 0
        else:
            sentiment_adjustment = 0
        
        # Volume adjustment (more news can indicate volatility)
        volume_adjustment = min(10, len(articles) * 1.0)
        
        score = base_score + sentiment_adjustment + volume_adjustment
        return max(0.0, min(100.0, score))
    
    def _calculate_sentiment_score(self, sentiments: List[SentimentResult]) -> float:
        """
        Calculate overall sentiment-based risk score.
        
        Args:
            sentiments: All sentiment results
            
        Returns:
            Risk score 0-100 (higher = more risk/negative)
        """
        if not sentiments:
            return 50.0  # Neutral baseline
        
        # Count sentiments
        negative_count = sum(1 for s in sentiments if s.label == SentimentLabel.NEGATIVE)
        positive_count = sum(1 for s in sentiments if s.label == SentimentLabel.POSITIVE)
        neutral_count = len(sentiments) - negative_count - positive_count
        
        total = len(sentiments)
        
        # Calculate weighted score
        # 100 = all negative, 0 = all positive, 50 = neutral
        negative_weight = negative_count / total
        positive_weight = positive_count / total
        neutral_weight = neutral_count / total
        
        score = (negative_weight * 100) + (neutral_weight * 50) + (positive_weight * 0)
        
        return max(0.0, min(100.0, score))
    
    def _get_risk_level(self, score: int) -> str:
        """
        Convert numeric score to risk level label.
        
        Args:
            score: Risk score 0-100
            
        Returns:
            Risk level string
        """
        if score >= self.thresholds["high"]:
            return "high"
        elif score >= self.thresholds["medium"]:
            return "medium"
        elif score >= self.thresholds["low"]:
            return "low"
        else:
            return "very_low"
    
    def _get_color_code(self, score: int) -> str:
        """
        Return hex color based on risk score (gradient from green to red).
        
        Args:
            score: Risk score 0-100
            
        Returns:
            Hex color code
        """
        if score <= 20:
            return "#10b981"  # Emerald 500 - Very safe
        elif score <= 35:
            return "#34d399"  # Emerald 400 - Safe
        elif score <= 50:
            return "#fbbf24"  # Amber 400 - Attention
        elif score <= 65:
            return "#f97316"  # Orange 500 - Risky
        elif score <= 80:
            return "#ef4444"  # Red 500 - Dangerous
        else:
            return "#dc2626"  # Red 600 - Critical
    
    def _generate_explanations(
        self,
        final_score: int,
        kap_score: float,
        news_score: float,
        sentiment_score: float,
        market_score: float,
        price_metrics: PriceMetrics,
        w_kap: float,
        w_news: float,
        w_sent: float,
        w_price: float,
        events: List[DetectedEvent],
        disclosures: List[KAPDisclosure],
        articles: List[NewsArticle],
    ) -> List[str]:
        """
        Generate human-readable explanations for the risk score.
        """
        explanations = []

        # Overall risk assessment
        if final_score >= 70:
            explanations.append(f"⚠️ Yüksek risk seviyesi ({final_score}/100). Dikkatli yaklaşım önerilir.")
        elif final_score >= 50:
            explanations.append(f"⚡ Orta risk seviyesi ({final_score}/100). Risk faktörleri mevcut.")
        elif final_score >= 30:
            explanations.append(f"✓ Düşük-orta risk seviyesi ({final_score}/100). Makul risk seviyesi.")
        else:
            explanations.append(f"✅ Düşük risk seviyesi ({final_score}/100). Favorable görünüm.")

        explanations.append(
            "Toplam skor; KAP, haberler, duygu analizi ve (varsa) yaklaşık 1 yıllık fiyat oynaklığı "
            "bileşenlerinin ağırlıklı birleşimidir."
        )

        explanations.append(
            f"Skor bileşenleri: KAP ({kap_score:.1f} × {w_kap:.2f}), Haber ({news_score:.1f} × {w_news:.2f}), "
            f"Duygu ({sentiment_score:.1f} × {w_sent:.2f}), Piyasa/fiyat ({market_score:.1f} × {w_price:.2f})"
        )

        if not price_metrics.data_available:
            if getattr(price_metrics, "source_error", None) == "no_series":
                explanations.append(
                    "Yahoo Finance bu sembol için günlük fiyat serisi döndürmedi; piyasa ağırlığı diğer "
                    f"bileşenlere yeniden dağıtıldı (sorgu: {price_metrics.ticker_used or '—'})."
                )
            elif getattr(price_metrics, "source_error", None) == "below_min_bars":
                explanations.append(
                    "Fiyat serisi çok kısa; piyasa ağırlığı diğer bileşenlere yeniden dağıtıldı "
                    f"(eşik: {get_settings().MIN_PRICE_BARS} işlem günü)."
                )
            else:
                explanations.append(
                    "Fiyat serisi yetersiz veya alınamadı; piyasa ağırlığı diğer bileşenlere yeniden dağıtıldı "
                    f"(eşik: {get_settings().MIN_PRICE_BARS} işlem günü)."
                )
        elif (
            price_metrics.return_1y_pct is not None
            and price_metrics.volatility_ann is not None
            and price_metrics.max_drawdown_pct is not None
        ):
            explanations.append(
                f"Fiyat metrikleri (~1 yıl): getiri %{price_metrics.return_1y_pct:.1f}, "
                f"yıllık volatilite %{price_metrics.volatility_ann * 100:.1f}, "
                f"maks. düşüş %{price_metrics.max_drawdown_pct:.1f} "
                f"({price_metrics.ticker_used or ''})."
            )
        
        # Data sources summary
        explanations.append(
            f"Analiz edilen kaynaklar: {len(disclosures)} KAP açıklaması, "
            f"{len(articles)} haber makalesi, {len(events)} olay tespiti, "
            f"{price_metrics.bar_count} günlük fiyat gözlemi"
        )
        
        # Event-specific explanations
        high_risk_events = [e for e in events if e.event_type == EventType.HIGH_RISK]
        positive_events = [e for e in events if e.event_type == EventType.POSITIVE]
        
        if high_risk_events:
            risk_keywords = list(set(e.keyword for e in high_risk_events))[:3]
            explanations.append(
                f"🚨 Risk sinyalleri: {', '.join(risk_keywords)} "
                f"({len(high_risk_events)} adet)"
            )
        
        if positive_events:
            positive_keywords = list(set(e.keyword for e in positive_events))[:3]
            explanations.append(
                f"📈 Pozitif gelişmeler: {', '.join(positive_keywords)} "
                f"({len(positive_events)} adet)"
            )
        
        # Component-specific insights
        if kap_score > 60:
            explanations.append("KAP açıklamalarında risk sinyalleri öne çıkıyor.")
        elif kap_score < 40:
            explanations.append("KAP açıklamaları genel olumlu görünüm sergiliyor.")
        
        if news_score > 60:
            explanations.append("Haber akışında negatif eğilim gözlemleniyor.")
        elif news_score < 40:
            explanations.append("Medya haberleri pozitif algı yaratıyor.")

        if w_price > 0 and price_metrics.data_available:
            if market_score >= 65:
                explanations.append(
                    "Son dönem fiyat hareketleri yüksek oynaklık veya belirgin düşüş içeriyor (piyasa riski)."
                )
            elif market_score <= 35:
                explanations.append("Son dönem fiyat hareketleri görece sakin (düşük piyasa riski sinyali).")

        return explanations


# Singleton instance
_risk_engine: Optional[RiskScoringEngine] = None


def get_risk_engine() -> RiskScoringEngine:
    """
    Get or create singleton risk scoring engine.
    
    Returns:
        RiskScoringEngine instance
    """
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskScoringEngine()
    return _risk_engine
