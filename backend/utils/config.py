"""
Configuration management for the financial risk analysis system.
"""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_TITLE: str = "Financial Risk Analysis API"
    API_VERSION: str = "1.0.0"
    API_DEBUG: bool = True
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # NLP Model Settings
    SENTIMENT_MODEL: str = "savasy/bert-base-turkish-cased-sentiment"
    # Alternative: "savasy/bert-base-turkish-cased-sentiment"
    # Fallback to English if Turkish model unavailable: "distilbert-base-uncased-finetuned-sst-2-english"
    
    # Scraper Settings
    KAP_BASE_URL: str = "https://www.kap.org.tr"
    # BIST code -> KAP özet path segment, e.g. {"TUPRS":"123-tupras-..."}; merges over data/kap_ozet_slugs.json
    KAP_OZET_SLUG_OVERRIDES_JSON: str = ""
    REQUEST_TIMEOUT: int = 30
    MAX_DISCLOSURES: int = 10
    MAX_NEWS_ARTICLES: int = 10
    
    # Cache Settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Risk Engine Settings (must sum to 1.0 with PRICE_WEIGHT)
    KAP_WEIGHT: float = 0.45
    NEWS_WEIGHT: float = 0.25
    SENTIMENT_WEIGHT: float = 0.15
    PRICE_WEIGHT: float = 0.15

    # Price history (Yahoo Finance: BIST tickers use suffix, e.g. THYAO.IS)
    PRICE_TICKER_SUFFIX: str = ".IS"
    PRICE_LOOKBACK_DAYS: int = 365
    MIN_PRICE_BARS: int = 20
    # If True and price data is missing or below MIN_PRICE_BARS, price weight is redistributed.
    PRICE_WEIGHT_ZERO_IF_MISSING: bool = True
    # Optional JSON object: BIST code -> Yahoo ticker, e.g. {"KOZAL":"THYAO.IS"} if you have a working mapping.
    PRICE_YAHOO_TICKER_OVERRIDES_JSON: str = ""

    # Risk Thresholds
    RISK_LOW_THRESHOLD: int = 30
    RISK_MEDIUM_THRESHOLD: int = 50
    RISK_HIGH_THRESHOLD: int = 70
    
    # Logging
    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def validate_risk_weights_sum(self) -> "Settings":
        total = (
            self.KAP_WEIGHT
            + self.NEWS_WEIGHT
            + self.SENTIMENT_WEIGHT
            + self.PRICE_WEIGHT
        )
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"KAP_WEIGHT + NEWS_WEIGHT + SENTIMENT_WEIGHT + PRICE_WEIGHT must equal 1.0, got {total}"
            )
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()
