"""Simple portfolio accounting for paper trading and backtesting."""
from __future__ import annotations

import dataclasses
import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Position:
    side: str
    quantity: float
    entry_price: float


@dataclasses.dataclass
class Trade:
    timestamp: pd.Timestamp
    side: str
    quantity: float
    price: float
    fee: float


class PortfolioManager:
    def __init__(self, starting_balance: float = 10_000.0) -> None:
        self.starting_balance = starting_balance
        self.cash = starting_balance
        self.position: Position | None = None
        self.trade_history: List[Trade] = []

    def _close_position(self, price: float, timestamp: pd.Timestamp, fee_pct: float) -> None:
        if not self.position:
            return
        qty = self.position.quantity
        fee = abs(price * qty) * fee_pct
        pnl = (price - self.position.entry_price) * qty if self.position.side == "long" else (
            (self.position.entry_price - price) * qty
        )
        self.cash += pnl - fee
        self.trade_history.append(
            Trade(timestamp=timestamp, side="close", quantity=qty, price=price, fee=fee)
        )
        logger.info("Closed %s position qty=%.4f at %.2f (PnL=%.2f)", self.position.side, qty, price, pnl - fee)
        self.position = None

    def _open_position(
        self, side: str, quantity: float, price: float, timestamp: pd.Timestamp, fee_pct: float
    ) -> None:
        fee = abs(price * quantity) * fee_pct
        cost = price * quantity
        if side == "long":
            if cost + fee > self.cash:
                raise ValueError("Insufficient cash")
            self.cash -= cost + fee
        else:  # short
            self.cash -= fee  # assume borrow with zero initial cost for paper trading
        self.position = Position(side=side, quantity=quantity, entry_price=price)
        self.trade_history.append(
            Trade(timestamp=timestamp, side=side, quantity=quantity, price=price, fee=fee)
        )
        logger.info("Opened %s position qty=%.4f at %.2f", side, quantity, price)

    def update_position(
        self,
        signal: float,
        price: float,
        timestamp: pd.Timestamp,
        max_position_size: float,
        fee_pct: float,
    ) -> None:
        desired_side = "long" if signal > 0 else "short" if signal < 0 else "flat"
        quantity = max_position_size
        if desired_side == "flat":
            self._close_position(price, timestamp, fee_pct)
            return

        if self.position and self.position.side == desired_side:
            return  # already aligned

        # Flip or open new position
        if self.position:
            self._close_position(price, timestamp, fee_pct)
        self._open_position(desired_side, quantity, price, timestamp, fee_pct)

    def current_value(self, price: float) -> float:
        if not self.position:
            return self.cash
        if self.position.side == "long":
            return self.cash + self.position.quantity * price
        return self.cash + (self.position.entry_price - price) * self.position.quantity

    def summary(self) -> Dict[str, float]:
        pnl = self.cash - self.starting_balance
        return {"cash": self.cash, "pnl": pnl, "return_pct": pnl / self.starting_balance}
