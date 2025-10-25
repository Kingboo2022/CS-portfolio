"""Real-time orchestrator for paper trading."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import pandas as pd

from .config import BotConfig
from .data.market_data import MarketDataClient, candles_to_dataframe
from .data.news import NewsSentimentClient
from .execution.paper import OrderEvent, PaperExecutionEngine
from .logging_config import configure_logging
from .portfolio.manager import PortfolioManager
from .strategies import build_strategy
from .strategies.base import StrategyContext

logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.market_client = MarketDataClient(exchange=config.exchange)
        self.news_client = NewsSentimentClient()
        self.portfolio = PortfolioManager()
        self.execution = PaperExecutionEngine(self.portfolio, fee_pct=config.execution.fees_pct)
        self.strategies = [build_strategy(s.type, s.weight, s.params) for s in config.strategies]
        self.price_history: pd.DataFrame | None = None

    async def warmup(self) -> None:
        candles = await self.market_client.fetch_ohlcv(
            self.config.base_quote, self.config.candle_interval, self.config.warmup_candles
        )
        self.price_history = candles_to_dataframe(candles)
        logger.info("Warmup complete with %s candles", len(self.price_history))

    async def step(self) -> None:
        assert self.price_history is not None
        candle = await self.market_client.fetch_ohlcv(
            self.config.base_quote, self.config.candle_interval, limit=1
        )
        last = candles_to_dataframe(candle)
        self.price_history = pd.concat([self.price_history, last]).drop_duplicates()
        sentiment, _ = self.news_client.summarise_sentiment(
            lookback_minutes=self.config.execution.poll_interval * 3, query="cryptocurrency"
        )
        timestamp = self.price_history.index[-1]
        ctx = StrategyContext(
            prices=self.price_history,
            config=self.config.describe(),
            timestamp=timestamp,
            news_sentiment=sentiment,
        )
        signal_total = 0.0
        for strategy in self.strategies:
            signal = strategy.generate_signal(ctx)
            signal_total += signal.direction * signal.confidence
        price = float(self.price_history.iloc[-1]["close"])
        event = OrderEvent(timestamp=timestamp, price=price, signal=signal_total)
        self.execution.on_signal(event, max_position_size=self.config.risk.max_position_size)
        logger.info(
            "Signal %.2f executed at %.2f | Portfolio value %.2f",
            signal_total,
            price,
            self.portfolio.current_value(price),
        )

    async def run(self) -> None:
        await self.warmup()
        poll_interval = self.config.execution.poll_interval
        while True:
            await self.step()
            await asyncio.sleep(poll_interval)

    async def close(self) -> None:
        await self.market_client.close()


async def main_async(config_path: str, log_level: str = "INFO") -> None:
    configure_logging(getattr(logging, log_level.upper(), logging.INFO))
    cfg = BotConfig.load(config_path)
    bot = TradingBot(cfg)
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down bot")
    finally:
        await bot.close()


def main() -> None:
    config_path = os.environ.get("BOT_CONFIG", str(Path(__file__).parent / "configs" / "example_momentum.yaml"))
    asyncio.run(main_async(config_path))


if __name__ == "__main__":
    main()
