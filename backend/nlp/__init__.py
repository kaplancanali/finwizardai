"""NLP module for sentiment analysis and event detection."""
from .sentiment import SentimentAnalyzer, get_sentiment_analyzer
from .event_detector import EventDetector, get_event_detector

__all__ = [
    "SentimentAnalyzer", 
    "get_sentiment_analyzer",
    "EventDetector",
    "get_event_detector"
]
