# core/signal_engine.py

import pandas as pd
from strategies.rsi_macd_strategy import RSIMACDStrategy
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SignalResult:
    def __init__(self, signal, rsi, macd, macd_diff, ema_50, entry_price):
        self.signal = signal        # 'BUY', 'SELL', or None
        self.rsi = rsi
        self.macd = macd
        self.macd_diff = macd_diff
        self.ema_50 = ema_50
        self.entry_price = entry_price


class SignalEngine:
    def __init__(self, strategy_name="rsi_macd", **kwargs):
        if strategy_name == "rsi_macd":
            self.strategy = RSIMACDStrategy(**kwargs)
        else:
            raise NotImplementedError(f"Strategy '{strategy_name}' not supported.")

    def generate(self, df: pd.DataFrame) -> SignalResult:
        signal, meta = self.strategy.generate_signal(df)
        return SignalResult(
            signal=signal,
            rsi=meta['rsi'],
            macd=meta['macd'],
            macd_diff=meta['macd_diff'],
            ema_50=meta['ema_50'],
            entry_price=meta['entry_price']
        )
