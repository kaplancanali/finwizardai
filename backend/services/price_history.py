"""
Fetch ~1 year of daily prices (Yahoo Finance) and derive market risk inputs.
"""
from __future__ import annotations

import json
from datetime import date
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from models.schemas import PriceBar, PriceMetrics
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger("price_history")


def _yahoo_ticker_overrides(settings) -> dict:
    raw = (getattr(settings, "PRICE_YAHOO_TICKER_OVERRIDES_JSON", "") or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        logger.warning("PRICE_YAHOO_TICKER_OVERRIDES_JSON is not valid JSON; ignoring")
        return {}


def _resolve_yahoo_ticker(bist_symbol: str, settings) -> str:
    sym = bist_symbol.upper().strip()
    overrides = _yahoo_ticker_overrides(settings)
    mapped = overrides.get(sym)
    if mapped and str(mapped).strip():
        return str(mapped).strip().upper()
    return f"{sym}{settings.PRICE_TICKER_SUFFIX}"


def _dataframe_to_close_volume(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Normalize yfinance output (flat or MultiIndex columns) to Close + Volume."""
    if df is None or df.empty or "Close" not in df.columns:
        return None
    out = pd.DataFrame(index=df.index)
    c = df["Close"]
    if isinstance(c, pd.DataFrame):
        c = c.squeeze(axis=1)
    out["Close"] = c
    if "Volume" in df.columns:
        v = df["Volume"]
        if isinstance(v, pd.DataFrame):
            v = v.squeeze(axis=1)
        out["Volume"] = v
    return out


def calculate_market_risk_score(
    return_1y_pct: Optional[float],
    volatility_ann: Optional[float],
    max_drawdown_pct: Optional[float],
    data_available: bool,
) -> float:
    """
    Map price metrics to 0-100 risk (higher = riskier).
    Higher vol and deeper drawdown increase score; positive return gives slight relief.
    """
    if not data_available or volatility_ann is None:
        return 50.0

    vol = float(volatility_ann)
    dd = float(max_drawdown_pct) if max_drawdown_pct is not None else 0.0
    ret = float(return_1y_pct) if return_1y_pct is not None else 0.0

    # Vol: 0% -> 0 pts contribution cap; ~35% annual vol -> strong risk
    vol_component = min(100.0, max(0.0, vol * 220.0))

    # Drawdown is negative; magnitude adds risk
    dd_frac = abs(min(0.0, dd / 100.0))
    dd_component = min(100.0, dd_frac * 130.0)

    relief = min(12.0, max(0.0, ret * 0.35)) if ret > 0 else 0.0
    penalty = min(12.0, max(0.0, -ret * 0.30)) if ret < 0 else 0.0

    combined = 0.48 * vol_component + 0.42 * dd_component + 5.0 - relief + penalty
    return float(max(0.0, min(100.0, combined)))


def _to_price_bars(series: pd.Series, volumes: Optional[pd.Series]) -> List[PriceBar]:
    bars: List[PriceBar] = []
    for idx, close in series.items():
        if pd.isna(close):
            continue
        d = idx.date() if hasattr(idx, "date") else idx
        if not isinstance(d, date):
            d = pd.Timestamp(idx).date()
        vol = None
        if volumes is not None and idx in volumes.index:
            v = volumes.loc[idx]
            vol = float(v) if not pd.isna(v) else None
        bars.append(PriceBar(date=d, close=float(close), volume=vol))
    return bars


def fetch_price_history(stock_symbol: str) -> Tuple[List[PriceBar], PriceMetrics, bool]:
    """
    Download daily history and build metrics.

    Returns:
        bars, metrics, sufficient_data (>= MIN_PRICE_BARS)
    """
    settings = get_settings()
    sym = stock_symbol.upper().strip()
    ticker_str = _resolve_yahoo_ticker(sym, settings)

    empty_metrics = PriceMetrics(
        bar_count=0,
        data_available=False,
        ticker_used=ticker_str,
        source_error="no_series",
    )

    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance not installed; skipping price history")
        return [], empty_metrics, False

    hist: Optional[pd.DataFrame] = None
    err_parts: List[str] = []

    # Primary: download(period=) uses a different code path and works when Ticker.history+date range returns empty JSON.
    try:
        raw = yf.download(
            ticker_str,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )
        hist = _dataframe_to_close_volume(raw)
    except Exception as exc:  # pragma: no cover - network
        err_parts.append(f"download:{exc!s}"[:180])

    # Fallback: Ticker.history with period (not start/end)
    if hist is None or hist["Close"].dropna().shape[0] < 2:
        try:
            raw = yf.Ticker(ticker_str).history(period="1y", interval="1d", auto_adjust=True)
            hist = _dataframe_to_close_volume(raw)
        except Exception as exc:  # pragma: no cover - network
            err_parts.append(f"history:{exc!s}"[:180])

    if hist is None or hist.empty:
        logger.info("No price rows for %s (%s)", ticker_str, "; ".join(err_parts) or "empty frame")
        return [], PriceMetrics(
            bar_count=0,
            data_available=False,
            ticker_used=ticker_str,
            source_error="no_series",
        ), False

    closes = hist["Close"].dropna()
    vols = hist["Volume"] if "Volume" in hist.columns else None
    if len(closes) < 2:
        return [], PriceMetrics(
            bar_count=len(closes),
            data_available=False,
            ticker_used=ticker_str,
            source_error="below_min_bars" if len(closes) > 0 else "no_series",
        ), False

    bars = _to_price_bars(closes, vols)

    log_ret = np.log(closes / closes.shift(1)).dropna()
    vol_ann = float(log_ret.std() * np.sqrt(252)) if len(log_ret) > 1 else 0.0

    first, last = float(closes.iloc[0]), float(closes.iloc[-1])
    return_1y_pct = ((last / first) - 1.0) * 100.0 if first > 0 else 0.0

    cummax = closes.cummax()
    underwater = closes / cummax - 1.0
    max_dd_pct = float(underwater.min() * 100.0)

    sufficient = len(closes) >= settings.MIN_PRICE_BARS
    metrics = PriceMetrics(
        return_1y_pct=round(return_1y_pct, 2),
        volatility_ann=round(vol_ann, 4),
        max_drawdown_pct=round(max_dd_pct, 2),
        bar_count=len(closes),
        data_available=sufficient,
        ticker_used=ticker_str,
        source_error=None if sufficient else "below_min_bars",
    )

    return bars, metrics, sufficient


class PriceHistoryService:
    """Thin wrapper for testing / future caching."""

    def get_history(self, stock_symbol: str) -> Tuple[List[PriceBar], PriceMetrics, bool]:
        return fetch_price_history(stock_symbol)


_price_history_service: Optional[PriceHistoryService] = None


def get_price_history_service() -> PriceHistoryService:
    global _price_history_service
    if _price_history_service is None:
        _price_history_service = PriceHistoryService()
    return _price_history_service
