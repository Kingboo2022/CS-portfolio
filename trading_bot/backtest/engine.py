"""Simple vectorised backtesting engine."""
from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

from ..config import BotConfig
from ..data.market_data import MarketDataClient, candles_to_dataframe
from ..data.news import NewsSentimentClient
from ..logging_config import configure_logging
from ..portfolio.manager import PortfolioManager
from ..strategies import build_strategy
from ..strategies.base import StrategyContext

logger = logging.getLogger(__name__)


class BacktestResult:
    def __init__(self, equity_curve: pd.Series, trades: List[Dict], summary: Dict[str, float]):
        self.equity_curve = equity_curve
        self.trades = trades
        self.summary = summary

    def to_dict(self) -> Dict:
        return {
            "final_value": float(self.equity_curve.iloc[-1]),
            "summary": self.summary,
            "trades": self.trades,
        }


async def run_backtest(config_path: Path) -> BacktestResult:
    cfg = BotConfig.load(config_path)
    market_client = MarketDataClient(exchange=cfg.exchange)
    candles = await market_client.fetch_ohlcv(cfg.base_quote, cfg.candle_interval, cfg.warmup_candles)
    await market_client.close()
    prices = candles_to_dataframe(candles)

    news_client = NewsSentimentClient()
    sentiment, items = news_client.summarise_sentiment(lookback_minutes=180)

    strategies = [build_strategy(s.type, s.weight, s.params) for s in cfg.strategies]
    portfolio = PortfolioManager()

    equity_values = []
    combined_signals = []
    for timestamp, row in prices.iterrows():
        ctx = StrategyContext(prices=prices.loc[:timestamp], config=cfg.describe(), timestamp=timestamp, news_sentiment=sentiment)
        signal_total = 0.0
        for strategy in strategies:
            signal = strategy.generate_signal(ctx)
            signal_total += signal.direction * signal.confidence
        combined_signals.append(signal_total)
        price = row["close"]
        portfolio.update_position(
            signal=signal_total,
            price=price,
            timestamp=timestamp,
            max_position_size=cfg.risk.max_position_size,
            fee_pct=cfg.execution.fees_pct,
        )
        equity_values.append((timestamp, portfolio.current_value(price)))

    equity_curve = pd.Series(dict(equity_values)).sort_index()
    summary = portfolio.summary()
    trades = [
        {
            "timestamp": trade.timestamp.isoformat(),
            "side": trade.side,
            "quantity": trade.quantity,
            "price": trade.price,
            "fee": trade.fee,
        }
        for trade in portfolio.trade_history
    ]
    return BacktestResult(equity_curve=equity_curve, trades=trades, summary=summary)


async def main_async(args: argparse.Namespace) -> None:
    result = await run_backtest(Path(args.config))
    logger.info("Backtest finished. Final value %.2f", result.equity_curve.iloc[-1])
    logger.info("Summary: %s", result.summary)
    logger.info("Trades: %s", result.trades)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a sample backtest")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--log-level", type=str, default="INFO")
    args = parser.parse_args()
    configure_logging(getattr(logging, args.log_level.upper(), logging.INFO))
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
