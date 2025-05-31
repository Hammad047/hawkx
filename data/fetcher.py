# === HawkX/data/fetcher.py ===
import logging

import pandas as pd
from hawkx.core.broker import Broker
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, broker: Broker):
        self.broker = broker


    def get_symbol_data(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV data and return as a pandas DataFrame.
        """
        try:
            raw = self.broker.safe_fetch_ohlcv(symbol, timeframe, limit)
            df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV for {symbol} [{timeframe}]: {e}")
            return None

    def get_latest_price(self, symbol: str) -> float:
        """
        Fetch the latest price of a symbol.
        """
        ticker = self.broker.fetch_ticker(symbol)
        return ticker['last'] if 'last' in ticker else None

    def get_volume_24h(self, symbol: str) -> float:
        """
        Fetch the 24-hour volume of a symbol.
        """
        ticker = self.broker.fetch_ticker(symbol)
        return ticker.get('quoteVolume', 0)

    def get_market_snapshot(self, symbol: str) -> dict:
        """
        Return a snapshot of latest price, high, low, volume, and change %.
        """
        ticker = self.broker.fetch_ticker(symbol)
        return {
            "price": ticker.get("last"),
            "high": ticker.get("high"),
            "low": ticker.get("low"),
            "volume": ticker.get("quoteVolume"),
            "change": ticker.get("percentage")
        }
