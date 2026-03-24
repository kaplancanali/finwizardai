"""
Sentiment analysis module using HuggingFace Transformers.

Supports Turkish language models for financial text analysis.
"""
from typing import List, Dict, Any, Optional
from functools import lru_cache

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from models.schemas import SentimentResult, SentimentLabel, KAPDisclosure, NewsArticle
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger("sentiment")


class SentimentAnalyzer:
    """
    Turkish sentiment analyzer using HuggingFace transformers.
    
    Uses a Turkish BERT model fine-tuned for sentiment classification.
    Falls back to simple rule-based analysis if transformers unavailable.
    
    Attributes:
        model_name: Name of the HuggingFace model
        pipeline: Transformers sentiment pipeline
        use_transformers: Whether transformers is available
    """
    
    # Turkish positive/negative keywords for rule-based fallback
    POSITIVE_KEYWORDS = [
        "kâr", "kar", "büyüme", "artış", "yükseliş", "yatırım", "anlaşma",
        "başarı", "kazanç", "gelir", "büyüdü", "arttı", "yükseldi", "olumlu",
        "iyi", "mükemmel", "güçlü", "rekor", "hedef", "aştı", "fırsat",
        "verimli", "etkin", "kalkınma", "gelişme", "ilerleme", "zafer"
    ]
    
    NEGATIVE_KEYWORDS = [
        "zarar", "ziyan", "kayıp", "düşüş", "azalma", "ceza", "soruşturma",
        "iflas", "batık", "kriz", "risk", "tehdit", "protesto", "protesto",
        "olumsuz", "kötü", "zayıf", "başarısız", "düştü", "azaldı", "engel",
        "sıkıntı", "problem", "belirsizlik", "endişe", "kaygı", "şok"
    ]
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        settings = get_settings()
        self.model_name = settings.SENTIMENT_MODEL
        self._pipeline: Optional[Any] = None
        self.use_transformers = TRANSFORMERS_AVAILABLE
        
        if self.use_transformers:
            try:
                logger.info(f"Loading sentiment model: {self.model_name}")
                self._pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    tokenizer=self.model_name,
                    device=-1  # CPU
                )
                logger.info("Sentiment model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load transformers model: {str(e)}")
                logger.warning("Falling back to rule-based sentiment analysis")
                self.use_transformers = False
    
    def analyze_text(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with label and confidence score
        """
        if not text or not text.strip():
            return SentimentResult(
                text="",
                label=SentimentLabel.NEUTRAL,
                score=0.5
            )
        
        if self.use_transformers and self._pipeline:
            return self._analyze_with_transformers(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_with_transformers(self, text: str) -> SentimentResult:
        """
        Analyze sentiment using HuggingFace transformers.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult
        """
        try:
            # Truncate if too long (BERT has 512 token limit)
            max_chars = 1000
            truncated_text = text[:max_chars]
            
            result = self._pipeline(truncated_text)[0]
            
            label_str = result['label'].lower()
            score = result['score']
            
            # Map to our sentiment labels
            if 'positive' in label_str or 'olumlu' in label_str:
                label = SentimentLabel.POSITIVE
            elif 'negative' in label_str or 'olumsuz' in label_str:
                label = SentimentLabel.NEGATIVE
            else:
                label = SentimentLabel.NEUTRAL
            
            return SentimentResult(
                text=text[:200] + "..." if len(text) > 200 else text,
                label=label,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Transformers analysis failed: {str(e)}")
            return self._analyze_rule_based(text)
    
    def _analyze_rule_based(self, text: str) -> SentimentResult:
        """
        Rule-based sentiment analysis as fallback.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult
        """
        text_lower = text.lower()
        
        # Count keyword occurrences
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            return SentimentResult(
                text=text[:200] + "..." if len(text) > 200 else text,
                label=SentimentLabel.NEUTRAL,
                score=0.5
            )
        
        # Calculate sentiment score
        sentiment_score = positive_count / total_keywords
        
        if sentiment_score > 0.6:
            label = SentimentLabel.POSITIVE
            confidence = sentiment_score
        elif sentiment_score < 0.4:
            label = SentimentLabel.NEGATIVE
            confidence = 1 - sentiment_score
        else:
            label = SentimentLabel.NEUTRAL
            confidence = 0.5
        
        return SentimentResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            label=label,
            score=round(confidence, 3)
        )
    
    def analyze_disclosures(
        self, 
        disclosures: List[KAPDisclosure]
    ) -> List[SentimentResult]:
        """
        Analyze sentiment of KAP disclosures.
        
        Args:
            disclosures: List of KAP disclosures
            
        Returns:
            List of sentiment results
        """
        results = []
        for disclosure in disclosures:
            # Combine title and content for analysis
            text = f"{disclosure.title}. {disclosure.content}"
            results.append(self.analyze_text(text))
        return results
    
    def analyze_news(
        self, 
        articles: List[NewsArticle]
    ) -> List[SentimentResult]:
        """
        Analyze sentiment of news articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            List of sentiment results
        """
        results = []
        for article in articles:
            # Combine title and summary for analysis
            text = f"{article.title}. {article.summary}"
            results.append(self.analyze_text(text))
        return results
    
    def aggregate_sentiment(
        self, 
        results: List[SentimentResult]
    ) -> Dict[str, Any]:
        """
        Aggregate multiple sentiment results into overall sentiment.
        
        Args:
            results: List of sentiment results
            
        Returns:
            Dictionary with aggregated sentiment and confidence
        """
        if not results:
            return {
                "label": SentimentLabel.NEUTRAL,
                "confidence": 0.5,
                "distribution": {"positive": 0, "negative": 0, "neutral": 0}
            }
        
        # Count labels
        positive_count = sum(1 for r in results if r.label == SentimentLabel.POSITIVE)
        negative_count = sum(1 for r in results if r.label == SentimentLabel.NEGATIVE)
        neutral_count = len(results) - positive_count - negative_count
        
        total = len(results)
        
        # Determine overall sentiment
        if positive_count > negative_count and positive_count > neutral_count:
            overall_label = SentimentLabel.POSITIVE
        elif negative_count > positive_count and negative_count > neutral_count:
            overall_label = SentimentLabel.NEGATIVE
        else:
            overall_label = SentimentLabel.NEUTRAL
        
        # Calculate confidence as weighted average
        avg_confidence = sum(r.score for r in results) / total
        
        return {
            "label": overall_label,
            "confidence": round(avg_confidence, 3),
            "distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            }
        }


# Singleton instance
_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """
    Get or create singleton sentiment analyzer.
    
    Returns:
        SentimentAnalyzer instance
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer
