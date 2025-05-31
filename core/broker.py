from abc import ABC, abstractmethod

from utils.logger import setup_logger

logger = setup_logger(__name__)


class Broker(ABC):
    """
    Abstract base class for all exchange implementations.
    """

    def __init__(self, exchange_interface):
        self.exchange = exchange_interface

    @abstractmethod
    def connect(self):
        """Connect to the broker using API credentials."""
        pass

    def fetch_ticker(self, symbol: str) -> dict:
        return self.exchange.fetch_ticker(symbol)

    @abstractmethod
    def get_balance(self, asset: str) -> float:
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, amount: float, price: float = None, type: str = 'market'):
        pass

    # 🔻 THESE MUST NOT BE ABSTRACT since they are implemented already
    def cancel_order(self, order_id: str):
        return self.exchange.cancel_order(order_id)

    def get_open_orders(self, symbol: str = None):
        return self.exchange.fetch_open_orders(symbol) if symbol else self.exchange.fetch_open_orders()

    def get_position(self, symbol: str):
        return {
            'symbol': symbol,
            'position': 0  # Placeholder
        }
