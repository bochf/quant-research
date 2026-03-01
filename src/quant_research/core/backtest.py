"""
Backtest Engine
"""

import numpy as np
import pandas as pd

from quant_research.strategies import Strategy


class Backtest:
    """
    Backtest Engine
    """

    def __init__(self, strategy: Strategy):
        self._strategy = strategy
        self._data = None

    def run(self) -> pd.DataFrame:
        """
        Run the backtest
        """
        self._data = self._strategy.generate_signal()
        self.calculate_position()
        self.calculate_returns()
        self.equity()
        return self._data

    def calculate_position(self):
        """
        Get the position at a given time
        The position is the signal shifted by 1 period
        The position is 0 if the signal is NaN

        Columns added:
        - position: The position at a given time
        """
        self._data["position"] = self._data["signal"].shift(1).fillna(0)

    def calculate_returns(self):
        """
        Calculate the returns at a given time

        Columns added:
        - asset_return: The return of the asset
        - strategy_return: The return of the strategy
        """
        self._data["asset_return"] = self._data["Close"].pct_change()
        self._data["strategy_return"] = (
            self._data["position"] * self._data["asset_return"]
        )

    def equity(self):
        """
        Calculate the equity curve

        Columns added:
        - equity: The equity curve
        """
        self._data["equity"] = (1 + self._data["strategy_return"]).cumprod()
