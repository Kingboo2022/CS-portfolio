# Step-by-Step Quickstart Guide

> **Audience:** Absolute beginners following the repo for the first time on Windows or WSL. Every step is included and ordered so you can tick them off as you go.

## 1. One-time PC preparation

1. Install [Python 3.11](https://www.python.org/downloads/release/python-3110/) and check the box **"Add python.exe to PATH"** during installation.
2. Install [Git for Windows](https://git-scm.com/download/win). Accept the defaults.
3. Optional but recommended: enable [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/install) by running `wsl --install -d Ubuntu` from an **Administrator PowerShell** window and reboot.
4. Install [Visual Studio Code](https://code.visualstudio.com/) so you can edit the files comfortably.

## 2. Download the project

```powershell
# Create a folder to store the project
mkdir C:\projects
cd C:\projects

# Download this repository (replace URL with your fork if needed)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Enter the trading bot folder
cd .\YOUR_REPO\trading_bot
```

You should now see files like `bot.py`, `README.md`, and the `configs/` folder when you run `dir`.

## 3. Create an isolated Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate  # WSL/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you see an error mentioning `TA-Lib`, download a pre-built wheel from <https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib> and install it with `pip install <downloaded-file.whl>`, then rerun `pip install -r requirements.txt`.

> ✅ **Always** activate `.\.venv\Scripts\activate` before running any Python command for this project. Your PowerShell prompt will show `(.venv)` when it is active.

## 4. Create your `.env` secrets file

```powershell
copy .env.example .env
notepad .env
```

Fill in the following values inside Notepad:

```
NEWS_API_KEY=your_newsapi_key_here
EXCHANGE=binance
EXCHANGE_API_KEY=your_public_key   # Leave blank for pure backtests/paper trading
EXCHANGE_API_SECRET=your_secret_key
```

Save and close the file.

## 5. Run a historical backtest

```powershell
python -m trading_bot.backtest.engine --config configs/example_momentum.yaml
```

This command loads past price candles, evaluates the bundled strategies, and prints metrics. Expect the first run to download indicator libraries; that can take a minute.

## 6. Start the paper-trading bot with logging

Open a **second** terminal, activate the virtual environment again, then run:

```powershell
python -m trading_bot.bot --config configs/example_momentum.yaml --paper
```

You will see log lines describing price updates, generated signals, and simulated trades. The default configuration never connects to a real exchange.

## 7. Launch the Streamlit dashboard (optional but recommended)

In another terminal:

```powershell
streamlit run trading_bot/ui/app.py
```

A browser window opens on <http://localhost:8501>. Use the sidebar to tweak parameters, start/stop paper trading, and inspect PnL charts.

## 8. Plan your next customizations

- Duplicate a YAML file in `configs/`, change the strategy weights/parameters, and point the CLI/UI commands to the new file.
- Add more indicators by creating new classes in `trading_bot/strategies/` and registering them in `trading_bot/strategies/__init__.py`.
- Replace the placeholder news or market data adapters with real exchange APIs once you finish weeks of paper trading.

> 🛡️ **Safety reminder:** Never trade real money until your backtests, paper trades, and manual reviews are consistent for an extended period. Always log every action.
