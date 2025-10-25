"""Mean reversion strategy using z-score of closing prices."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Signal, Strategy, StrategyContext


class MeanReversionStrategy(Strategy):
    def generate_signal(self, ctx: StrategyContext) -> Signal:
        params = {
            "lookback": 20,
            "z_entry": 1.5,
            "z_exit": 0.5,
            **self.params,
        }
        window = ctx.prices["close"].tail(params["lookback"])
        if len(window) < params["lookback"]:
            return Signal(0.0, 0.0, {"reason": "insufficient_data"})
        mean = window.mean()
        std = window.std()
        if std == 0:
            return Signal(0.0, 0.0, {"reason": "no_volatility"})
        zscore = (window.iloc[-1] - mean) / std
        direction = 0.0
        if zscore > params["z_entry"]:
            direction = -1.0
        elif zscore < -params["z_entry"]:
            direction = 1.0
        elif abs(zscore) < params["z_exit"]:
            direction = 0.0
        info = {"zscore": float(zscore), "mean": float(mean), "std": float(std)}
        confidence = float(min(1.0, abs(zscore) / (params["z_entry"] + 1e-6)))
        return Signal(direction, confidence, info).scaled(self.weight)
