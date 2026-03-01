"""
Strategy Layer
"""

import pandas as pd



class Strategy:
    """
    Interface for a strategy
    """

    def generate_signal(self) -> pd.DataFrame:
        """
        Generate a signal based on the input data
        """
        raise NotImplementedError("Subclasses must implement this method")
