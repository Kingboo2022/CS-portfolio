"""Strategy that converts aggregated news sentiment into directional bias."""
from __future__ import annotations

from .base import Signal, Strategy, StrategyContext


class NewsSentimentStrategy(Strategy):
    def generate_signal(self, ctx: StrategyContext) -> Signal:
        params = {
            "bullish_threshold": 0.2,
            "bearish_threshold": -0.2,
            **self.params,
        }
        sentiment = ctx.news_sentiment
        direction = 0.0
        if sentiment >= params["bullish_threshold"]:
            direction = 1.0
        elif sentiment <= params["bearish_threshold"]:
            direction = -1.0
        confidence = min(1.0, abs(sentiment))
        return Signal(direction, confidence, {"sentiment": sentiment}).scaled(self.weight)
