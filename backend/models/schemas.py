"""
Pydantic models for the Financial Risk Analysis System.
"""
from datetime import date as DateScalar
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class SentimentLabel(str, Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EventType(str, Enum):
    """Types of financial events detected."""
    HIGH_RISK = "high_risk"
    POSITIVE = "positive"
    NEUTRAL = "neutral"


class KAPDisclosure(BaseModel):
    """KAP (Public Disclosure Platform) disclosure model."""
    title: str = Field(..., description="Disclosure title")
    content: str = Field(..., description="Disclosure content/body")
    date: datetime = Field(..., description="Publication date")
    disclosure_type: Optional[str] = Field(None, description="Type of disclosure")
    stock_symbol: str = Field(..., description="Stock symbol (e.g., THYAO)")


class NewsArticle(BaseModel):
    """News article model."""
    title: str = Field(..., description="Article headline")
    summary: str = Field(..., description="Article summary or content")
    source: Optional[str] = Field(None, description="News source")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    url: Optional[str] = Field(None, description="Article URL")
    stock_symbol: Optional[str] = Field(None, description="Related stock symbol")


class SentimentResult(BaseModel):
    """Sentiment analysis result."""
    text: str = Field(..., description="Analyzed text snippet")
    label: SentimentLabel = Field(..., description="Sentiment classification")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class DetectedEvent(BaseModel):
    """Detected financial event from text analysis."""
    event_type: EventType = Field(..., description="Type of event detected")
    keyword: str = Field(..., description="Trigger keyword")
    context: str = Field(..., description="Text context around the keyword")
    risk_impact: int = Field(..., ge=-10, le=10, description="Risk impact score (-10 to +10)")
    source_type: str = Field(default="kap", description="Source: 'kap' or 'news'")
    source_url: Optional[str] = Field(None, description="Link to source")
    source_title: Optional[str] = Field(None, description="Title of source document")


class PriceBar(BaseModel):
    """Single daily price observation for charts."""
    date: DateScalar = Field(..., description="Trading session date")
    close: float = Field(..., description="Adjusted close price")
    volume: Optional[float] = Field(None, description="Volume if available")


class PriceMetrics(BaseModel):
    """Derived metrics from ~1 year of daily closes."""
    return_1y_pct: Optional[float] = Field(None, description="Total return over window (percent)")
    volatility_ann: Optional[float] = Field(
        None, description="Annualized volatility from log returns (decimal, e.g. 0.28 = 28%)"
    )
    max_drawdown_pct: Optional[float] = Field(
        None, description="Maximum drawdown over window (negative percent, e.g. -32.5)"
    )
    bar_count: int = Field(0, description="Number of trading days used")
    data_available: bool = Field(False, description="Whether MIN_PRICE_BARS threshold was met")
    ticker_used: Optional[str] = Field(None, description="Yahoo Finance ticker queried")
    source_error: Optional[str] = Field(
        None,
        description="no_series: provider returned no bars; below_min_bars: fewer than MIN_PRICE_BARS",
    )


class RiskBreakdown(BaseModel):
    """Detailed breakdown of risk score components."""
    kap_score: float = Field(..., ge=0.0, le=100.0)
    news_score: float = Field(..., ge=0.0, le=100.0)
    sentiment_score: float = Field(..., ge=0.0, le=100.0)
    market_score: float = Field(..., ge=0.0, le=100.0, description="Price/volatility risk 0-100")
    kap_contribution: float = Field(..., description="Weighted contribution from KAP")
    news_contribution: float = Field(..., description="Weighted contribution from news")
    sentiment_contribution: float = Field(..., description="Weighted contribution from sentiment")
    market_contribution: float = Field(..., description="Weighted contribution from market/price")


class RiskAnalysisResponse(BaseModel):
    """Main API response for risk analysis."""
    stock: str = Field(..., description="Stock symbol (e.g., THYAO)")
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    sentiment: SentimentLabel = Field(..., description="Overall sentiment")
    sentiment_confidence: float = Field(..., ge=0.0, le=1.0)
    events: List[DetectedEvent] = Field(default_factory=list, description="Detected events")
    explanations: List[str] = Field(default_factory=list, description="Human-readable explanations")
    breakdown: RiskBreakdown = Field(..., description="Score breakdown")
    data_sources: dict = Field(default_factory=dict, description="Summary of data sources used")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    # Extended data for detailed analysis
    kap_disclosures: List[KAPDisclosure] = Field(default_factory=list, description="Full KAP disclosures")
    news_articles: List[NewsArticle] = Field(default_factory=list, description="Full news articles")
    price_history: List[PriceBar] = Field(default_factory=list, description="~1y daily closes for charting")
    price_metrics: Optional[PriceMetrics] = Field(None, description="Derived price statistics")
    color_code: str = Field(default="#10b981", description="Hex color based on risk score")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(default="1.0.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
