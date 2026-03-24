"""
Market overview routes for full-list risk ranking.
"""
from typing import Optional

from fastapi import APIRouter, Query

from services.market_analysis import get_market_analysis_service

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/leaderboard")
async def market_leaderboard(
    sort_by: str = Query(default="risk_score", pattern="^(risk_score|name|sector)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    risk_level: Optional[str] = Query(default=None),
    sector: Optional[str] = Query(default=None),
) -> dict:
    service = get_market_analysis_service()
    return service.leaderboard(
        sort_by=sort_by,
        order=order,
        risk_level=risk_level,
        sector=sector,
    )

