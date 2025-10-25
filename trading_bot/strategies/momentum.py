"""Momentum strategy combining moving averages and RSI."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import talib

from .base import Signal, Strategy, StrategyContext

logger = logging.getLogger(__name__)


class MomentumStrategy(Strategy):
    def generate_signal(self, ctx: StrategyContext) -> Signal:
        params = {
            "fast_ma": 12,
            "slow_ma": 26,
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            **self.params,
        }
        close = ctx.prices["close"].values
        fast_ma = talib.EMA(close, timeperiod=params["fast_ma"])
        slow_ma = talib.EMA(close, timeperiod=params["slow_ma"])
        rsi = talib.RSI(close, timeperiod=params["rsi_period"])

        direction = 0.0
        if np.isnan(fast_ma[-1]) or np.isnan(slow_ma[-1]) or np.isnan(rsi[-1]):
            return Signal(direction, 0.0, {"reason": "insufficient_data"})

        if fast_ma[-1] > slow_ma[-1] and rsi[-1] < params["rsi_overbought"]:
            direction = 1.0
        elif fast_ma[-1] < slow_ma[-1] and rsi[-1] > params["rsi_oversold"]:
            direction = -1.0

        info = {
            "fast_ma": float(fast_ma[-1]),
            "slow_ma": float(slow_ma[-1]),
            "rsi": float(rsi[-1]),
        }
        return Signal(direction, confidence=1.0, info=info).scaled(self.weight)
