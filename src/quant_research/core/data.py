"""
Data Layer
"""

import yfinance as yf
import pandas as pd


def load_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Load data from Yahoo Finance for a given ticker, period, and interval
    Args:
        ticker: The ticker symbol of the stock to load data for
        period: The period of time to load data for
        interval: The interval of time to load data for
    Returns:
        A pandas DataFrame containing the loaded data
    """
    return yf.download(ticker, period=period, interval=interval)
