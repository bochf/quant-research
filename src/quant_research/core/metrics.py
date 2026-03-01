"""
Metrics Layer
"""

import pandas as pd
import numpy as np

TRADING_DAYS_PER_YEAR = 252


class Metrics:
    """
    Metrics Engine
    """

    def __init__(self, data: pd.DataFrame):
        self._data = data

    def evaluate(self) -> pd.DataFrame:
        """
        Evaluate the metrics
        """
        self.annual_return()
        self.annual_volatility()
        self.sharpe_ratio()
        self.max_drawdown()
        return self._data

    def annual_return(self) -> float:
        """
        Calculate the annualized return
        """
        total_days = len(self._data)
        if total_days == 0:
            return 0
        final_equity = self._data["equity"].iloc[-1]
        return final_equity ** (TRADING_DAYS_PER_YEAR / total_days) - 1

    def annual_volatility(self) -> float:
        """
        Calculate the annualized volatility
        """
        return self._data["strategy_return"].std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    def sharpe_ratio(self):
        """
        Calculate the sharpe ratio

        Columns added:
        - sharpe_ratio: The sharpe ratio
        """
        self._data["sharpe_ratio"] = (
            np.sqrt(TRADING_DAYS_PER_YEAR)
            * self._data["strategy_return"].mean()
            / self._data["strategy_return"].std()
        )

    def max_drawdown(self):
        """
        Calculate the max drawdown

        Columns added:
        - max_drawdown: The max drawdown
        """
        rolling_max = self._data["equity"].cummax()
        drawdown = self._data["equity"] / rolling_max - 1
        self._data["max_drawdown"] = drawdown.min()
