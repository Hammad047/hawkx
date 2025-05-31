import ccxt

from hawkx.core.broker import Broker, logger


class OKXInterface(Broker):
    def __init__(self, config: dict):
        exchange = ccxt.okx({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'password': config['api_passphrase'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }

        })
        super().__init__(exchange)

    def connect(self):
        """Loads market data and establishes the connection."""
        self.exchange.load_markets()

    def get_balance(self, asset: str) -> float:
        balance = self.exchange.fetch_balance()
        return balance.get(asset, {}).get('free', 0.0)

    def get_price(self, symbol: str) -> float:
        return self.exchange.fetch_ticker(symbol)['last']

    def safe_fetch_ohlcv(self, symbol, timeframe, limit=100):
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV from OKX for {symbol} [{timeframe}]: {e}")
            return None

    def place_order(self, symbol: str, side: str, amount: float, price: float = None, type: str = 'market'):
        return self.exchange.create_order(symbol, type, side, amount, price)
