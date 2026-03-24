"""Scrapers module for financial data collection."""
from .kap_scraper import get_kap_scraper, KAPScraper
from .news_scraper import get_news_scraper, NewsScraper

__all__ = ["get_kap_scraper", "KAPScraper", "get_news_scraper", "NewsScraper"]
