"""Market data helpers (historical + live)."""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Iterable, List

import ccxt.async_support as ccxt_async
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_row(self) -> Dict[str, float]:
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


class MarketDataClient:
    """Thin wrapper around CCXT for fetching candles."""

    def __init__(self, exchange: str = "binance") -> None:
        exchange_class = getattr(ccxt_async, exchange)
        self._client = exchange_class({
            "apiKey": os.getenv("EXCHANGE_API_KEY"),
            "secret": os.getenv("EXCHANGE_API_SECRET"),
            "enableRateLimit": True,
        })

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str, limit: int = 200
    ) -> List[Candle]:
        logger.info("Fetching %s candles (%s, limit=%s)", symbol, timeframe, limit)
        raw = await self._client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        candles = [Candle(*row) for row in raw]
        return candles

    async def stream_live_prices(
        self, symbol: str, timeframe: str, poll_interval: int = 60
    ) -> AsyncIterator[Candle]:
        """Poll candles in a loop. Replace with websockets for production."""
        while True:
            candles = await self.fetch_ohlcv(symbol, timeframe, limit=2)
            yield candles[-1]
            await asyncio.sleep(poll_interval)

    async def close(self) -> None:
        await self._client.close()


def candles_to_dataframe(candles: Iterable[Candle]) -> pd.DataFrame:
    df = pd.DataFrame([c.to_row() for c in candles])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    return df


def compute_returns(df: pd.DataFrame) -> pd.Series:
    return df["close"].pct_change().fillna(0.0)


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    resampled = df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })
    return resampled.dropna()
