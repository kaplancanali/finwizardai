"""
Rule-based event detection for financial risk signals.

Detects financial events using keyword matching and context analysis
for Turkish financial text.
"""
import re
from typing import List, Optional
from dataclasses import dataclass

from models.schemas import DetectedEvent, EventType, KAPDisclosure, NewsArticle
from utils.kap_urls import kap_company_ozet_url
from utils.logger import get_logger

logger = get_logger("event_detector")


@dataclass
class RiskPattern:
    """Risk pattern definition for event detection."""
    keywords: List[str]
    event_type: EventType
    risk_impact: int
    category: str
    description: str


class EventDetector:
    """
    Rule-based financial event detector for Turkish text.
    
    Scans text for high-risk and positive event keywords,
    extracting context and calculating risk impact scores.
    
    Attributes:
        patterns: List of risk patterns to match
    """
    
    # Define risk patterns with Turkish financial keywords
    RISK_PATTERNS = [
        # HIGH RISK PATTERNS
        RiskPattern(
            keywords=["zarar", "ziyan", "kayıp", "loss"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-8,
            category="financial_loss",
            description="Finansal zarar/kayıp bildirimi"
        ),
        RiskPattern(
            keywords=["ceza", "para cezası", "idari ceza", "penalty", "fine"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-7,
            category="regulatory_penalty",
            description="Düzenleyici ceza"
        ),
        RiskPattern(
            keywords=["soruşturma", "etik soruşturma", "inceleme", "investigation"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-6,
            category="investigation",
            description="Soruşturma/inceleme"
        ),
        RiskPattern(
            keywords=["iflas", "konkordato", "batık", "bankruptcy", "insolvency"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-10,
            category="bankruptcy",
            description="İflas riski"
        ),
        RiskPattern(
            keywords=["dava", "mahkeme", "tazminat", "dava açıldı", "lawsuit"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-5,
            category="legal",
            description="Hukuki dava/uyuşmazlık"
        ),
        RiskPattern(
            keywords=["istifa", "görevden alma", "yönetim değişikliği", "resignation"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-4,
            category="leadership_change",
            description="Yönetim değişikliği"
        ),
        RiskPattern(
            keywords=["kredi notu düştü", "not indirimi", "negatif", "downgrade"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-6,
            category="credit_rating",
            description="Kredi notu indirimi"
        ),
        RiskPattern(
            keywords=["sermaye artırımı", "bedelsiz", "bedelli", "hisse artırım"],
            event_type=EventType.HIGH_RISK,
            risk_impact=-3,
            category="capital_increase",
            description="Sermaye artırımı (dilution riski)"
        ),
        
        # POSITIVE PATTERNS
        RiskPattern(
            keywords=["kâr", "kar", "kazanç", "net kar", "profit", "earnings"],
            event_type=EventType.POSITIVE,
            risk_impact=5,
            category="profit",
            description="Kâr/kazanç bildirimi"
        ),
        RiskPattern(
            keywords=["yatırım", "proje", "fabrika", "tesis", "investment"],
            event_type=EventType.POSITIVE,
            risk_impact=4,
            category="investment",
            description="Yatırım/gelişme"
        ),
        RiskPattern(
            keywords=["büyüme", "artış", "yükseliş", "rekor", "growth"],
            event_type=EventType.POSITIVE,
            risk_impact=4,
            category="growth",
            description="Büyüme/artış"
        ),
        RiskPattern(
            keywords=["anlaşma", "sözleşme", "ihale", "contract", "deal"],
            event_type=EventType.POSITIVE,
            risk_impact=3,
            category="contract",
            description="Yeni anlaşma/sözleşme"
        ),
        RiskPattern(
            keywords=["temettü", "kar payı", "temettü dağıtım", "dividend"],
            event_type=EventType.POSITIVE,
            risk_impact=3,
            category="dividend",
            description="Temettü/kar payı"
        ),
        RiskPattern(
            keywords=["ihracat", "dış satım", "export", "ihracat artışı"],
            event_type=EventType.POSITIVE,
            risk_impact=4,
            category="export",
            description="İhracat başarısı"
        ),
        RiskPattern(
            keywords=["kredi notu yükseldi", "not artırımı", "upgrade", "pozitif"],
            event_type=EventType.POSITIVE,
            risk_impact=5,
            category="credit_rating",
            description="Kredi notu yükseltimi"
        ),
        RiskPattern(
            keywords=["pay geri alım", "hibe", "stock buyback"],
            event_type=EventType.POSITIVE,
            risk_impact=2,
            category="buyback",
            description="Pay geri alımı"
        ),
    ]
    
    def __init__(self):
        """Initialize the event detector with risk patterns."""
        self.patterns = self.RISK_PATTERNS
        logger.info(f"Event detector initialized with {len(self.patterns)} patterns")
    
    def detect_events(self, text: str) -> List[DetectedEvent]:
        """
        Detect financial events in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected events
        """
        events = []
        text_lower = text.lower()
        
        for pattern in self.patterns:
            for keyword in pattern.keywords:
                if keyword in text_lower:
                    # Extract context around the keyword
                    context = self._extract_context(text, keyword)
                    
                    # Check if we already detected this event type with similar context
                    if not self._is_duplicate_event(events, pattern.event_type, keyword):
                        event = DetectedEvent(
                            event_type=pattern.event_type,
                            keyword=keyword,
                            context=context,
                            risk_impact=pattern.risk_impact
                        )
                        events.append(event)
                        
                        logger.debug(
                            f"Detected event: {pattern.category} "
                            f"(impact: {pattern.risk_impact})"
                        )
        
        return events
    
    def analyze_disclosures(
        self, 
        disclosures: List[KAPDisclosure]
    ) -> List[DetectedEvent]:
        """
        Detect events in KAP disclosures.
        
        Args:
            disclosures: List of KAP disclosures
            
        Returns:
            List of detected events
        """
        all_events = []
        for disclosure in disclosures:
            text = f"{disclosure.title}. {disclosure.content}"
            events = self.detect_events(text)
            # Add source information to each event
            for event in events:
                event.source_type = "kap"
                event.source_url = kap_company_ozet_url(disclosure.stock_symbol)
                event.source_title = disclosure.title
            all_events.extend(events)
        return all_events
    
    def analyze_news(
        self, 
        articles: List[NewsArticle]
    ) -> List[DetectedEvent]:
        """
        Detect events in news articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            List of detected events
        """
        all_events = []
        for article in articles:
            text = f"{article.title}. {article.summary}"
            events = self.detect_events(text)
            # Add source information to each event
            for event in events:
                event.source_type = "news"
                event.source_url = article.url or ""
                event.source_title = article.title
            all_events.extend(events)
        return all_events
    
    def _extract_context(self, text: str, keyword: str, window: int = 80) -> str:
        """
        Extract context around a keyword.
        
        Args:
            text: Full text
            keyword: Keyword to find
            window: Number of characters before and after
            
        Returns:
            Context string with keyword highlighted
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Find keyword position
        pos = text_lower.find(keyword_lower)
        if pos == -1:
            return text[:100] + "..." if len(text) > 100 else text
        
        # Calculate window boundaries
        start = max(0, pos - window)
        end = min(len(text), pos + len(keyword) + window)
        
        # Extract context
        context = text[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context.strip()
    
    def _is_duplicate_event(
        self, 
        existing_events: List[DetectedEvent], 
        event_type: EventType, 
        keyword: str
    ) -> bool:
        """
        Check if a similar event is already detected.
        
        Args:
            existing_events: Already detected events
            event_type: Event type to check
            keyword: Keyword to check
            
        Returns:
            True if similar event exists
        """
        for event in existing_events:
            if event.event_type == event_type and event.keyword == keyword:
                return True
        return False
    
    def calculate_event_risk_score(self, events: List[DetectedEvent]) -> float:
        """
        Calculate overall risk score from detected events.
        
        Args:
            events: List of detected events
            
        Returns:
            Normalized risk score (0-100)
        """
        if not events:
            return 50.0  # Neutral baseline
        
        # Sum up risk impacts
        total_impact = sum(event.risk_impact for event in events)
        
        # Count high-risk vs positive events
        high_risk_count = sum(1 for e in events if e.event_type == EventType.HIGH_RISK)
        positive_count = sum(1 for e in events if e.event_type == EventType.POSITIVE)
        
        # Calculate base score from impacts
        # Risk impacts are -10 to +5, we want to map this to 0-100
        # More negative = higher risk score
        
        # Normalize total impact
        max_possible_negative = len(events) * -10
        max_possible_positive = len(events) * 5
        
        if total_impact < 0:
            # More negative impact = higher risk
            normalized = 50 + (abs(total_impact) / abs(max_possible_negative)) * 50
        else:
            # Positive impact = lower risk
            normalized = 50 - (total_impact / max_possible_positive) * 50
        
        # Adjust for event count - more high-risk events = higher score
        if high_risk_count > positive_count:
            normalized += 10 * (high_risk_count - positive_count)
        elif positive_count > high_risk_count:
            normalized -= 10 * (positive_count - high_risk_count)
        
        # Clamp to 0-100
        return max(0.0, min(100.0, normalized))
    
    def get_event_summary(self, events: List[DetectedEvent]) -> List[str]:
        """
        Generate human-readable event summaries.
        
        Args:
            events: List of detected events
            
        Returns:
            List of summary strings
        """
        if not events:
            return ["Önemli bir finansal olay tespit edilmedi."]
        
        summaries = []
        
        # Group events by type
        high_risk_events = [e for e in events if e.event_type == EventType.HIGH_RISK]
        positive_events = [e for e in events if e.event_type == EventType.POSITIVE]
        
        # Generate summary for high-risk events
        if high_risk_events:
            keywords = list(set(e.keyword for e in high_risk_events))
            summaries.append(
                f"{len(high_risk_events)} adet risk sinyali tespit edildi: "
                f"{', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}"
            )
        
        # Generate summary for positive events
        if positive_events:
            keywords = list(set(e.keyword for e in positive_events))
            summaries.append(
                f"{len(positive_events)} adet pozitif gelişme: "
                f"{', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}"
            )
        
        return summaries


# Singleton instance
_detector: Optional[EventDetector] = None


def get_event_detector() -> EventDetector:
    """
    Get or create singleton event detector.
    
    Returns:
        EventDetector instance
    """
    global _detector
    if _detector is None:
        _detector = EventDetector()
    return _detector
