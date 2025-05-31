# strategies/rsi_macd_strategy.py

import pandas as pd
import ta

class RSIMACDStrategy:
    def __init__(self, rsi_low=30, rsi_high=70):
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()

        rsi = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        macd = ta.trend.MACD(close=df['close'])
        ema_50 = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()

        df['rsi'] = rsi
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        df['ema_50'] = ema_50

        signal = None
        if df['rsi'].iloc[-1] < self.rsi_low and df['macd_diff'].iloc[-1] > 0 and df['close'].iloc[-1] > df['ema_50'].iloc[-1]:
            signal = 'BUY'
        elif df['rsi'].iloc[-1] > self.rsi_high and df['macd_diff'].iloc[-1] < 0 and df['close'].iloc[-1] < df['ema_50'].iloc[-1]:
            signal = 'SELL'

        return signal, {
            'rsi': rsi.iloc[-1],
            'macd': df['macd'].iloc[-1],
            'macd_diff': df['macd_diff'].iloc[-1],
            'ema_50': df['ema_50'].iloc[-1],
            'entry_price': df['close'].iloc[-1]
        }
