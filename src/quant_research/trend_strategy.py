"""
Trend-Following Trading Strategy
=================================
Signals are generated using a combination of:
  1. EMA Crossover   — primary signal (fast EMA crosses slow EMA)
  2. MACD            — momentum confirmation
  3. ADX             — trend strength filter (only trade in strong trends)

Signal Values:
  +1 = Long  (bullish trend confirmed)
  -1 = Short (bearish trend confirmed)
   0 = Hold  (no clear trend or weak trend)

Input:
  df : pd.DataFrame
       index   : datetime
       columns : open, high, low, close, volume

Output:
  df : pd.DataFrame (original columns + 'signal' column)
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass

from quant_research.strategy import Strategy


class TrendStrategy(Strategy):
    """
    Trend Strategy
    """

    @dataclass
    class TrendStrategyConfig:
        """
        Config for the Trend Strategy
        """

        fast_span: int = 12
        slow_span: int = 26
        signal_span: int = 9
        adx_period: int = 14
        adx_threshold: int = 25

    def __init__(self, data: pd.DataFrame, config: TrendStrategyConfig = TrendStrategyConfig()):
        self._data = data
        self._config = config

        # validate config
        if self._config.fast_span >= self._config.slow_span:
            raise ValueError("Fast span must be less than slow span")
        if self._config.signal_span >= self._config.fast_span:
            raise ValueError("Signal span must be less than fast span")
        if self._config.adx_period < 1:
            raise ValueError("ADX period must be greater than 0")

        # compute EMA, MACD, and ADX

    def generate_signal(self) -> pd.DataFrame:
        """
        Generate trend-following signals for the given OHLCV DataFrame.

        Parameters
        ----------
        df            : OHLCV DataFrame (datetime index, columns: open high low close volume)
        ema_fast      : Fast EMA period (default 12)
        ema_slow      : Slow EMA period (default 26)
        macd_fast     : MACD fast EMA period (default 12)
        macd_slow     : MACD slow EMA period (default 26)
        macd_signal   : MACD signal line period (default 9)
        adx_period    : ADX smoothing period (default 14)
        adx_threshold : Minimum ADX to consider trend strong (default 25)

        Returns
        -------
        df with an additional 'signal' column: {-1, 0, 1}
        """
        # compute EMA, MACD, and ADX
        self.compute_crossover()
        self.compute_macd()
        self.compute_adx()

        # generate signal combining crossover, ema_curr, macd_bull, and trend_strong
        # LONG  (+1): EMA fast crosses above slow  AND  MACD bullish  AND  ADX strong
        # SHORT (-1): EMA fast crosses below slow  AND  MACD bearish  AND  ADX strong
        # HOLD   (0): No crossover, or trend too weak, or MACD disagrees
        crossover_long = self._data["crossover"] & (self._data["ema_curr"] == 1)
        crossover_short = self._data["crossover"] & (self._data["ema_curr"] == -1)

        long_cond = (
            crossover_long & self._data["macd_bull"] & self._data["trend_strong"]
        )
        short_cond = (
            crossover_short & ~self._data["macd_bull"] & self._data["trend_strong"]
        )

        self._data["signal"] = np.where(long_cond, 1, np.where(short_cond, -1, 0))
        return self._data

    def compute_ema(self, span: int, series_name: str = "close", column_name: str = ""):
        """
        Compute the EMA for a given span from the close price and add it to the data frame
        Args:
            span: The span of the EMA
            series_name: The name of the series to compute the EMA from, default is "close"
            column_name: The name of the column to add the EMA to
        """
        new_name = column_name or f"ema_{span}"
        if new_name in self._data.columns:
            return

        base_name = series_name or "close"
        if base_name not in self._data.columns:
            raise ValueError(f"Series {base_name} not found in data")

        self._data[new_name] = self._data[base_name].ewm(span=span).mean()

    def compute_crossover(self):
        """
        Compute the crossover of two series
        The crossover is a boolean series that is True on the bar where the fast EMA crosses the slow EMA

        Columns added:
        - ema_fast: Fast EMA
        - ema_slow: Slow EMA
        - ema_curr: Current EMA direction: +1 when fast > slow, -1 otherwise
        - ema_prev: Previous EMA direction
        - crossover: True on the bar where cross happens
        """
        # Get the fast and slow EMA
        if "ema_fast" not in self._data.columns:
            self.compute_ema(self._config.fast_span, column_name="ema_fast")
        if "ema_slow" not in self._data.columns:
            self.compute_ema(self._config.slow_span, column_name="ema_slow")

        # Raw crossover direction: +1 when fast > slow, -1 otherwise
        self._data["ema_curr"] = np.where(
            self._data["ema_fast"] > self._data["ema_slow"], 1, -1
        )
        self._data["ema_prev"] = self._data["ema_curr"].shift(1)
        self._data["crossover"] = (
            self._data["ema_curr"] != self._data["ema_prev"]
        )  # True on the bar where cross happens

    def compute_macd(self):
        """
        Compute the MACD for a given fast span, slow span, and signal span from the close price and add it to the data frame

        Columns added:
        - macd: MACD line (fast EMA - slow EMA)
        - macd_signal: Signal line (EMA of MACD line)
        - macd_bull: True when macd > macd_signal
        """
        if "ema_fast" not in self._data.columns:
            self.compute_ema(self._config.fast_span, column_name="ema_fast")
        if "ema_slow" not in self._data.columns:
            self.compute_ema(self._config.slow_span, column_name="ema_slow")

        # compute MACD
        self._data["macd"] = self._data["ema_fast"] - self._data["ema_slow"]

        # compute signal EMA
        self.compute_ema(self._config.signal_span, "macd", "macd_signal")

        # compute MACD bullish when macd > macd_signal
        self._data["macd_bull"] = self._data["macd"] > self._data["macd_signal"]

    def compute_adx(self):
        """
        Average Directional Index (ADX).
        Measures trend strength regardless of direction.
        ADX > 25 is typically considered a strong trend.

        Columns added:
        - adx: Average Directional Index
        - trend_strong: True when adx > adx_threshold
        """
        # compute previous high, low, and close
        high = self._data["high"]
        low = self._data["low"]
        close = self._data["close"]
        prev_high = high.shift(1)
        prev_low = low.shift(1)
        prev_close = close.shift(1)

        # compute true range
        # True Range = Max(High - Low, abs(High - Previous Close), abs(Low - Previous Close))
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)

        # compute positive and negative directional movement
        # The direction is determined by the high-low average of the current and previous period
        # If the high-low average is above the previous high-low average, then the direction is up
        # If the high-low average is below the previous high-low average, then the direction is down
        # Positive Directional Movement = High - Previous High if High > Previous High
        pdm = np.where(
            (high + low) > (prev_high + prev_low), np.maximum(high - prev_high, 0), 0
        )
        pdm = pd.Series(pdm, index=close.index)
        # Negative Directional Movement = Previous Low - Low if Low < Previous Low
        ndm = np.where(
            (prev_high + prev_low) > (high + low), np.maximum(prev_low - low, 0), 0
        )
        ndm = pd.Series(ndm, index=close.index)

        # compute average true range (ATR)
        # ATR = (ATR * (period - 1) + TR) / period
        # smooth the ART with Wilder's method
        art = tr.ewm(alpha=1 / self._config.adx_period, adjust=False).mean()
        pdi = (
            100 * pdm.ewm(alpha=1 / self._config.adx_period, adjust=False).mean() / art
        )
        ndi = (
            100 * ndm.ewm(alpha=1 / self._config.adx_period, adjust=False).mean() / art
        )

        # compute directional index (DX)
        dx = (np.abs(pdi - ndi) / (pdi + ndi).replace(0, np.nan)).abs()
        # compute average directional index (ADX)
        self._data["adx"] = dx.ewm(
            alpha=1 / self._config.adx_period, adjust=False
        ).mean()

        # compute trend strong when adx > adx_threshold
        self._data["trend_strong"] = self._data["adx"] > self._config.adx_threshold
