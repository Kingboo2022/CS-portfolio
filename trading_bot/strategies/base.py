"""Strategy interfaces and utilities."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


class Signal:
    """Represents a trading signal from a strategy."""

    __slots__ = ("direction", "confidence", "info")

    def __init__(self, direction: float, confidence: float = 1.0, info: Optional[Dict] = None) -> None:
        self.direction = max(-1.0, min(1.0, direction))
        self.confidence = max(0.0, min(1.0, confidence))
        self.info = info or {}

    def scaled(self, weight: float) -> "Signal":
        return Signal(self.direction * weight, self.confidence, self.info)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"Signal(direction={self.direction:.2f}, confidence={self.confidence:.2f})"


@dataclass
class StrategyContext:
    prices: pd.DataFrame
    config: Dict
    timestamp: pd.Timestamp
    news_sentiment: float = 0.0


class Strategy(abc.ABC):
    """Abstract strategy interface."""

    def __init__(self, weight: float, params: Dict) -> None:
        self.weight = weight
        self.params = params

    @abc.abstractmethod
    def generate_signal(self, ctx: StrategyContext) -> Signal:
        raise NotImplementedError
