# strategies/base_strategy.py

from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Each strategy must implement the `generate_signal` method.
    """

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> tuple[str | None, dict]:
        """
        Parameters:
            df (pd.DataFrame): Historical OHLCV data with indicators

        Returns:
            signal (str | None): "BUY", "SELL", or None
            metadata (dict): Extra info such as confidence score, reasons, etc.
        """
        pass
