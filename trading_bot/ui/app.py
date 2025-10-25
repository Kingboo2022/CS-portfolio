"""Streamlit dashboard for the educational trading bot."""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from ..backtest.engine import run_backtest
from ..config import BotConfig
from ..logging_config import configure_logging

logger = logging.getLogger(__name__)


@lru_cache
def load_config(path: str) -> BotConfig:
    return BotConfig.load(path)


async def async_backtest(config_path: str) -> Dict:
    result = await run_backtest(Path(config_path))
    return {
        "equity_curve": result.equity_curve,
        "summary": result.summary,
        "trades": result.trades,
    }


def main() -> None:
    st.set_page_config(page_title="AI Crypto Bot", layout="wide")
    st.title("AI Crypto Trading Bot (Educational)")
    st.warning(
        "This project is for **education only**. Do not risk money without extensive testing."
    )

    config_files = list(Path(__file__).resolve().parents[1].glob("configs/*.yaml"))
    if not config_files:
        st.error("No config files found.")
        return
    config_map = {cfg.stem: cfg for cfg in config_files}
    choice = st.sidebar.selectbox("Strategy config", list(config_map.keys()))
    config_path = str(config_map[choice])
    cfg = load_config(config_path)

    st.sidebar.subheader("Execution")
    poll_interval = st.sidebar.slider("Poll interval (seconds)", 30, 300, cfg.execution.poll_interval)
    max_position_size = st.sidebar.number_input(
        "Max position size", min_value=0.01, value=float(cfg.risk.max_position_size)
    )

    st.subheader("Strategies")
    for strat in cfg.strategies:
        st.write(f"**{strat.type}** — weight {strat.weight}")
        st.json(strat.params)

    if st.button("Run backtest", type="primary"):
        with st.spinner("Running backtest..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_backtest(config_path))
            finally:
                loop.close()
        st.success("Backtest finished")
        st.line_chart(result["equity_curve"])
        st.json(result["summary"])
        st.write("Trades")
        st.dataframe(pd.DataFrame(result["trades"]))

    st.info(
        "To start paper trading, open a terminal and run: `python -m trading_bot.bot`."
    )


if __name__ == "__main__":
    configure_logging()
    main()
