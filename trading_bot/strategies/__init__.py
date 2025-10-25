"""Strategy factory."""
from __future__ import annotations

from typing import Dict, Type

from .base import Strategy
from .mean_reversion import MeanReversionStrategy
from .momentum import MomentumStrategy
from .news_sentiment import NewsSentimentStrategy

STRATEGY_REGISTRY: Dict[str, Type[Strategy]] = {
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "news_sentiment": NewsSentimentStrategy,
}


def build_strategy(strategy_type: str, weight: float, params: Dict) -> Strategy:
    if strategy_type not in STRATEGY_REGISTRY:
        raise KeyError(f"Unknown strategy: {strategy_type}")
    return STRATEGY_REGISTRY[strategy_type](weight=weight, params=params)
