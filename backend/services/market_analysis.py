"""
Market-wide analysis service for BIST30 stocks.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from models.schemas import RiskAnalysisResponse
from scoring.risk_engine import get_risk_engine
from utils.logger import get_logger

logger = get_logger("market_analysis")


BIST30_STOCKS: List[Dict[str, str]] = [
    {"symbol": "AKBNK", "name": "Akbank T.A.Ş.", "sector": "Bankacılık"},
    {"symbol": "ALARK", "name": "Alarko Holding", "sector": "Holding"},
    {"symbol": "ARCLK", "name": "Arçelik A.Ş.", "sector": "Dayanıklı Tüketim"},
    {"symbol": "ASELS", "name": "Aselsan A.Ş.", "sector": "Savunma"},
    {"symbol": "BIMAS", "name": "BİM Mağazalar", "sector": "Perakende"},
    {"symbol": "EKGYO", "name": "Emlak Konut GYO", "sector": "GYO"},
    {"symbol": "EREGL", "name": "Ereğli Demir Çelik", "sector": "Metalürji"},
    {"symbol": "FROTO", "name": "Ford Otosan", "sector": "Otomotiv"},
    {"symbol": "GARAN", "name": "Garanti Bankası", "sector": "Bankacılık"},
    {"symbol": "GUBRF", "name": "Gübre Fabrikaları", "sector": "Kimya"},
    {"symbol": "HEKTS", "name": "Hektaş A.Ş.", "sector": "Kimya"},
    {"symbol": "ISCTR", "name": "İş Bankası (C)", "sector": "Bankacılık"},
    {"symbol": "KCHOL", "name": "Koç Holding", "sector": "Holding"},
    {"symbol": "KONTR", "name": "Kontrolmatik", "sector": "Teknoloji"},
    {"symbol": "KORDS", "name": "Kordsa Global", "sector": "Tekstil"},
    {"symbol": "KOZAA", "name": "Koza Anadolu", "sector": "Madencilik"},
    {"symbol": "KOZAL", "name": "Koza Altın", "sector": "Madencilik"},
    {"symbol": "KRDMD", "name": "Kardemir (D)", "sector": "Metalürji"},
    {"symbol": "MGROS", "name": "Migros Ticaret", "sector": "Perakende"},
    {"symbol": "ODAS", "name": "Odaş Elektrik", "sector": "Enerji"},
    {"symbol": "OTKAR", "name": "Otokar Otomotiv", "sector": "Otomotiv"},
    {"symbol": "PETKM", "name": "Petkim", "sector": "Petrokimya"},
    {"symbol": "PGSUS", "name": "Pegasus Hava", "sector": "Havacılık"},
    {"symbol": "SAHOL", "name": "Sabancı Holding", "sector": "Holding"},
    {"symbol": "SASA", "name": "Sasa Polyester", "sector": "Tekstil"},
    {"symbol": "SISE", "name": "Şişecam", "sector": "Cam"},
    {"symbol": "TAVHL", "name": "TAV Havalimanları", "sector": "Havalimanı"},
    {"symbol": "TCELL", "name": "Turkcell", "sector": "Telekomünikasyon"},
    {"symbol": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"},
    {"symbol": "TOASO", "name": "Tofaş Oto", "sector": "Otomotiv"},
    {"symbol": "TUPRS", "name": "Tüpraş", "sector": "Enerji"},
    {"symbol": "YKBNK", "name": "Yapı Kredi Bankası", "sector": "Bankacılık"},
]


class MarketAnalysisService:
    def __init__(self) -> None:
        self._risk_engine = get_risk_engine()

    def _analyze_one(self, symbol: str) -> Optional[RiskAnalysisResponse]:
        try:
            return self._risk_engine.analyze_stock(symbol)
        except Exception as exc:  # pragma: no cover - best effort batch
            logger.warning(f"Failed to analyze {symbol}: {exc}")
            return None

    def leaderboard(
        self,
        sort_by: str = "risk_score",
        order: str = "desc",
        risk_level: Optional[str] = None,
        sector: Optional[str] = None,
    ) -> Dict:
        stock_meta = BIST30_STOCKS
        if sector:
            stock_meta = [s for s in stock_meta if s["sector"].lower() == sector.lower()]

        results: List[Dict] = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self._analyze_one, s["symbol"]): s for s in stock_meta}
            for future in as_completed(futures):
                meta = futures[future]
                analysis = future.result()
                if analysis is None:
                    continue
                if risk_level and analysis.risk_level != risk_level:
                    continue
                results.append(
                    {
                        "symbol": meta["symbol"],
                        "name": meta["name"],
                        "sector": meta["sector"],
                        "risk_score": analysis.risk_score,
                        "risk_level": analysis.risk_level,
                        "sentiment": analysis.sentiment,
                        "color_code": analysis.color_code,
                    }
                )

        reverse = order.lower() == "desc"
        if sort_by == "name":
            results.sort(key=lambda x: x["name"], reverse=reverse)
        elif sort_by == "sector":
            results.sort(key=lambda x: x["sector"], reverse=reverse)
        else:
            results.sort(key=lambda x: x["risk_score"], reverse=reverse)

        return {
            "count": len(results),
            "sort_by": sort_by,
            "order": order,
            "risk_level_filter": risk_level,
            "sector_filter": sector,
            "items": results,
        }


_market_analysis_service: Optional[MarketAnalysisService] = None


def get_market_analysis_service() -> MarketAnalysisService:
    global _market_analysis_service
    if _market_analysis_service is None:
        _market_analysis_service = MarketAnalysisService()
    return _market_analysis_service

