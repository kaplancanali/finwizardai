"""
Risk analysis API routes.

Provides endpoints for financial risk analysis of BIST stocks.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from models.schemas import RiskAnalysisResponse, HealthResponse
from scoring.risk_engine import get_risk_engine
from utils.logger import get_logger
from utils.cache import cache

logger = get_logger("api")
router = APIRouter(prefix="/api/v1", tags=["risk-analysis"])


@router.get(
    "/risk/{stock_symbol}",
    response_model=RiskAnalysisResponse,
    summary="Analyze stock risk",
    description="Perform comprehensive risk analysis for a given BIST stock symbol.",
    responses={
        200: {
            "description": "Successful risk analysis",
            "model": RiskAnalysisResponse
        },
        400: {
            "description": "Invalid stock symbol"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def analyze_stock_risk(
    stock_symbol: str = Path(
        ...,
        title="Stock Symbol",
        description="BIST stock symbol (e.g., THYAO, GARAN, ASELS)",
        min_length=2,
        max_length=10,
        examples=["THYAO", "GARAN", "ASELS"]
    ),
    use_cache: bool = Query(
        default=True,
        description="Use cached results if available"
    )
) -> RiskAnalysisResponse:
    """
    Analyze financial risk for a given stock symbol.
    
    This endpoint performs a comprehensive risk analysis including:
    - KAP disclosure analysis
    - News sentiment analysis
    - Event detection
    - Risk scoring with explanations
    
    Args:
        stock_symbol: BIST stock symbol (case insensitive)
        use_cache: Whether to use cached results
        
    Returns:
        RiskAnalysisResponse with full analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    # Validate stock symbol
    symbol = stock_symbol.upper().strip()
    
    if not symbol or len(symbol) < 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid stock symbol. Must be at least 2 characters."
        )
    
    logger.info(f"API request: Risk analysis for {symbol}")
    
    try:
        # Get risk engine and perform analysis
        engine = get_risk_engine()
        
        # Clear cache if requested
        if not use_cache:
            cache_key = f"analyze_stock|{symbol}|"
            cache.delete(cache_key)
            logger.info(f"Cache cleared for {symbol}")
        
        # Perform analysis
        result = engine.analyze_stock(symbol)
        
        logger.info(f"Analysis completed for {symbol}: score={result.risk_score}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/risk/batch",
    response_model=List[RiskAnalysisResponse],
    summary="Batch risk analysis",
    description="Analyze multiple stocks in a single request."
)
async def analyze_batch(
    symbols: List[str] = Query(
        ...,
        title="Stock Symbols",
        description="List of BIST stock symbols",
        examples=["THYAO", "GARAN", "ASELS"]
    )
) -> List[RiskAnalysisResponse]:
    """
    Perform batch risk analysis for multiple stocks.
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        List of RiskAnalysisResponse objects
    """
    if len(symbols) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 symbols allowed per batch request"
        )
    
    logger.info(f"Batch analysis request for {len(symbols)} symbols")
    
    results = []
    engine = get_risk_engine()
    
    for symbol in symbols:
        try:
            result = engine.analyze_stock(symbol.upper().strip())
            results.append(result)
        except Exception as e:
            logger.error(f"Error in batch analysis for {symbol}: {str(e)}")
            # Continue with other symbols even if one fails
    
    logger.info(f"Batch analysis completed: {len(results)}/{len(symbols)} successful")
    return results


@router.get(
    "/stocks",
    summary="Available stocks",
    description="Get list of commonly analyzed BIST30 stocks."
)
async def get_available_stocks() -> dict:
    """
    Get list of commonly available BIST30 stocks for analysis.
    
    Returns:
        Dictionary with stock list
    """
    bist30_stocks = [
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
    
    return {
        "count": len(bist30_stocks),
        "stocks": bist30_stocks,
        "note": "Use these symbols with /risk/{symbol} endpoint"
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health status."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with status information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.post(
    "/cache/clear",
    summary="Clear cache",
    description="Clear the analysis cache."
)
async def clear_cache() -> dict:
    """
    Clear the in-memory cache.
    
    Returns:
        Success message
    """
    cache.clear()
    logger.info("Cache cleared via API")
    return {"message": "Cache cleared successfully"}
