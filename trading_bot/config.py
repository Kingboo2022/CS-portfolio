"""Configuration loader for the educational trading bot."""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Any, Dict, List

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

ROOT = pathlib.Path(__file__).resolve().parent


def load_env(path: pathlib.Path | None = None) -> None:
    """Load environment variables from a `.env` file if present."""
    env_path = path or ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)


class StrategyConfig(BaseModel):
    type: str
    weight: float = Field(gt=0, le=1)
    params: Dict[str, Any] = Field(default_factory=dict)

    @validator("type")
    def validate_type(cls, value: str) -> str:  # noqa: N805
        if not value:
            raise ValueError("strategy type must not be empty")
        return value


class RiskConfig(BaseModel):
    max_position_size: float = Field(gt=0)
    max_leverage: float = Field(gt=0)
    stop_loss_pct: float = Field(gt=0)
    take_profit_pct: float = Field(gt=0)


class ExecutionConfig(BaseModel):
    slippage_bps: float = Field(ge=0)
    fees_pct: float = Field(ge=0)
    poll_interval: int = Field(gt=0)


class BotConfig(BaseModel):
    name: str = "default"
    base_quote: str = "BTC/USDT"
    exchange: str = "binance"
    candle_interval: str = "1h"
    warmup_candles: int = Field(default=200, gt=0)
    strategies: List[StrategyConfig]
    risk: RiskConfig
    execution: ExecutionConfig

    @classmethod
    def load(cls, path: str | pathlib.Path) -> "BotConfig":
        load_env(ROOT / ".env")
        with open(path, "r", encoding="utf-8") as fh:
            payload = yaml.safe_load(fh)
        return cls(**payload)

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_quote": self.base_quote,
            "exchange": self.exchange,
            "candle_interval": self.candle_interval,
            "strategies": [s.dict() for s in self.strategies],
            "risk": self.risk.dict(),
            "execution": self.execution.dict(),
        }


@dataclass
class IndicatorResult:
    value: float
    metadata: Dict[str, Any]
