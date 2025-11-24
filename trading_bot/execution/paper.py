"""Paper trading execution engine."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

import pandas as pd

from ..portfolio.manager import PortfolioManager

logger = logging.getLogger(__name__)


@dataclass
class OrderEvent:
    timestamp: pd.Timestamp
    price: float
    signal: float


class PaperExecutionEngine:
    def __init__(self, portfolio: PortfolioManager, fee_pct: float) -> None:
        self.portfolio = portfolio
        self.fee_pct = fee_pct

    def on_signal(
        self,
        event: OrderEvent,
        max_position_size: float,
    ) -> None:
        logger.debug("Processing signal %.2f at price %.2f", event.signal, event.price)
        try:
            self.portfolio.update_position(
                signal=event.signal,
                price=event.price,
                timestamp=event.timestamp,
                max_position_size=max_position_size,
                fee_pct=self.fee_pct,
            )
        except ValueError as exc:  # e.g. insufficient cash
            logger.warning("Failed to execute order: %s", exc)
