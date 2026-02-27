### Quant Research – Trend-Following Framework

A minimal, modular Python framework for backtesting a simple **trend-following strategy** (EMA crossover + MACD + ADX) on Yahoo Finance data.

---

## Features

- **Data layer**: download OHLCV data from Yahoo Finance (`yfinance`).
- **Strategy layer**: EMA crossover + MACD + ADX trend filter.
- **Backtest engine**: position generation, P&L, equity curve.
- **Metrics**: annualized return, annualized volatility, Sharpe ratio, max drawdown.
- **CLI**: run a full backtest from the command line.

---

## Installation

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt    # if present; otherwise:
pip install yfinance pandas numpy
```

Make sure `src` is on your `PYTHONPATH` when running:

```bash
export PYTHONPATH=src              # Windows PowerShell: $env:PYTHONPATH = "src"
```

---

## Project Structure

```text
src/
  quant_research/
    __init__.py
    main.py           # CLI entrypoint
    data.py           # Yahoo Finance data loader
    strategy.py       # Strategy interface
    trend_strategy.py # EMA+MACD+ADX trend strategy
    backtest.py       # Backtest engine
    metrics.py        # Performance metrics
```

---

## Usage

From the project root (with `PYTHONPATH=src`):

```bash
python -m quant_research.main \
  --ticker AAPL \
  --period 1y \
  --interval 1d
```

Typical `--period` values: `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`.  
Typical `--interval` values: `1d`, `1h`, `30m`, etc. (as supported by Yahoo Finance).

The script will:

1. Download OHLCV data for the given ticker.
2. Run the trend-following strategy and backtest.
3. Compute basic performance metrics.
4. Print the resulting DataFrame (including `signal`, `position`, `strategy_return`, `equity`, and metrics columns).

---

## Strategy Logic (High Level)

- **EMA crossover**
  - Compute fast and slow EMAs on close.
  - Detect crossovers (fast crossing above/below slow).
- **MACD**
  - `MACD = EMA_fast − EMA_slow`, with a signal line (EMA of MACD).
  - `macd_bull = MACD > MACD_signal`.
- **ADX**
  - Wilder-style ADX to measure trend strength.
  - `trend_strong = ADX > adx_threshold` (default 25).
- **Signals**
  - Long (`+1`): fast EMA crosses above slow, MACD bullish, trend strong.
  - Short (`-1`): fast EMA crosses below slow, MACD bearish, trend strong.
  - Hold (`0`): otherwise.

---

## Backtest & Metrics

- **Backtest**
  - `position = signal.shift(1)` (enter on next bar; flat before first signal).
  - `asset_return = close.pct_change()`.
  - `strategy_return = position * asset_return`.
  - `equity = (1 + strategy_return).cumprod()`.

- **Metrics**
  - **Annualized return**: based on final equity and sample length.
  - **Annualized volatility**: daily `strategy_return` std scaled by \(\sqrt{252}\).
  - **Sharpe ratio**: mean daily return / daily vol, scaled by \(\sqrt{252}\).
  - **Max drawdown**: min drawdown of equity vs rolling peak.

---

## Extending

- Implement new strategies by subclassing `Strategy` and implementing `generate_signal()`.
- Reuse `Backtest` and `Metrics` with any strategy operating on an OHLCV `DataFrame`.

---

## License

MIT (or update this section with your actual license).

