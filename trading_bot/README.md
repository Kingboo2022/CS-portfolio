# AI Crypto Trading Bot (Educational Template)

> ⚠️ **Huge disclaimer:** Trading cryptocurrencies is extremely risky. This project is provided for educational purposes only. It is not investment advice. You are responsible for testing and verifying every single behaviour before connecting it to a live exchange account.

This folder contains a from-scratch, end-to-end Python template for a crypto trading bot that combines:

> 🆕 **Need hand-holding?** Follow the [Step-by-Step Quickstart](QUICKSTART.md) if you just cloned the repo and want a checklist-style walkthrough. It repeats the essentials from this README with extra context for every command.

* Multiple classical technical analysis strategies (momentum and mean reversion)
* Real-time news sentiment scoring
* Backtesting utilities so that you can replay past markets
* A paper-trading execution layer
* A Streamlit web UI so you can tweak parameters and monitor the bot

The code is intentionally verbose and heavily commented. Read the sections below **in order** and you will have a working development environment on Windows (or WSL) that you can expand into your own project.

---

## 0. Prerequisites (Windows + optional WSL)

1. Install **Python 3.11** from [python.org](https://www.python.org/downloads/release/python-3110/). During installation, tick the option *"Add python.exe to PATH"*.
2. Install **Git** from [git-scm.com](https://git-scm.com/download/win).
3. Optional but recommended: Install **Windows Subsystem for Linux (WSL)** via PowerShell (run as Administrator):
   ```powershell
   wsl --install -d Ubuntu
   ```
   Restart your machine, open the Ubuntu app, and finish the installation prompts. You can run everything either in regular Windows or inside WSL; the steps are identical.
4. Install **VS Code** or another editor so you can open and edit the project comfortably.
5. Create a free [NewsAPI](https://newsapi.org/) account (for news headlines) and a [CryptoCompare](https://min-api.cryptocompare.com/) or [Binance](https://www.binance.com/en/binance-api) API key (for price data). We never hard-code keys in the repository; you will place them in an `.env` file later.

---

## 1. Clone and set up the repository

Open PowerShell (or WSL) and run:

```powershell
mkdir C:\projects
cd C:\projects
# Clone your repo (replace with your GitHub URL if needed)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO\trading_bot
python -m venv .venv
.\.venv\Scripts\activate  # If you use WSL: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> ✅ Always activate the virtual environment (`.\\venv\\Scripts\\activate` on Windows CMD/PowerShell, `source .venv/bin/activate` on WSL) before running any scripts.

---

## 2. Configure secrets and runtime options

1. Copy the sample environment file and edit it with your keys:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` and fill in the placeholders:
   ```ini
   NEWS_API_KEY=your_newsapi_key_here
   EXCHANGE=binance
   EXCHANGE_API_KEY=your_public_key
   EXCHANGE_API_SECRET=your_secret_key
   ```
3. For pure backtesting you can leave `EXCHANGE_API_KEY` and `EXCHANGE_API_SECRET` blank. Paper trading uses synthetic balances and does not require real keys.

---

## 3. Run a quick smoke test

With the virtual environment activated, run the included example backtest:

```powershell
python -m trading_bot.backtest.engine --config configs/example_momentum.yaml
```

You should see logs summarising trades, PnL, and strategy metrics. If you encounter `TA-Lib` installation issues on Windows, follow the comment in `requirements.txt` that links to precompiled wheels.

---

## 4. Launch the Streamlit UI

The UI lets you toggle strategies, change parameters, and start/stop paper trading:

```powershell
streamlit run trading_bot/ui/app.py
```

A browser window will open (http://localhost:8501) displaying the dashboard. The UI calls the same orchestrator as the CLI but gives you forms and charts to interact with live.

---

## 5. Project tour (read alongside the source files)

| Folder/File | What it does |
|-------------|--------------|
| `trading_bot/config.py` | Loads configuration values from YAML and `.env`, merges defaults, and performs validation. |
| `trading_bot/data/market_data.py` | Fetches historical candles (via CCXT) and streams live price updates. |
| `trading_bot/data/news.py` | Pulls the latest crypto headlines and performs a simple sentiment score using Hugging Face transformers. |
| `trading_bot/strategies/` | Contains abstract base class + concrete implementations (momentum, mean reversion, news sentiment overlay). |
| `trading_bot/portfolio/manager.py` | Keeps track of account balance, open positions, and risk limits. |
| `trading_bot/execution/paper.py` | Simulated exchange that reads signals, executes orders, and emits fills. |
| `trading_bot/backtest/engine.py` | Runs fast vectorised backtests over historical candles using the strategies. |
| `trading_bot/bot.py` | The orchestrator that wires everything together for real-time paper trading. |
| `trading_bot/ui/app.py` | Streamlit UI for monitoring and interacting with the bot. |
| `trading_bot/logging_config.py` | Centralised logging configuration so CLI + UI share the same log formatting. |
| `configs/` | YAML strategy configurations (weights, timeframes, indicator parameters). |

---

## 6. Extend the bot safely

1. **Add more strategies**: create a new class in `trading_bot/strategies/` that inherits `Strategy`. Register it in `trading_bot/strategies/__init__.py` and reference it from a YAML config.
2. **Replace data sources**: if you prefer another news API or exchange, swap out the client in `market_data.py` / `news.py`. Keep the interface identical (`get_latest_candles`, `stream_live_prices`, `fetch_news`).
3. **Connect a real exchange**: implement a new execution handler inside `trading_bot/execution` that talks to the official REST/WebSocket APIs. Keep paper trading running in parallel until you are confident.
4. **Automate backtests**: convert the CLI backtester into unit tests. Use `pytest` to assert the strategy behaviour remains consistent when you refactor.
5. **Deploy**: run the bot on a dedicated machine (Raspberry Pi, VPS, cloud instance). Use `tmux`/`systemd`/`Docker` to keep it alive.

> 💡 **Tip:** Before risking real money, run *months* of paper trading. Observe performance, log anomalies, and verify risk controls.

---

## 7. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | Ensure the virtual environment is activated and `pip install -r requirements.txt` succeeded. |
| `ta-lib` build fails | Visit https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib and download the wheel matching your Python version/architecture, then `pip install path\to\TA_Lib‑...whl`. |
| `streamlit` UI cannot connect | Make sure the bot server is running (`python -m trading_bot.bot`). If using WSL, open the browser inside Windows at http://localhost:8501. |
| Rate limit errors | Lower your polling frequency in the YAML config (`data.poll_interval`), and consider caching news responses. |

---

## 8. Next steps for learning

* Read "Advances in Financial Machine Learning" by Marcos López de Prado.
* Explore reinforcement learning frameworks like Stable Baselines for algorithmic trading.
* Add more robust risk management: max drawdown stops, volatility targeting, Kelly sizing.
* Integrate websockets instead of polling for lower latency.

Good luck, and trade responsibly! 
