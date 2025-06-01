# strategies/rsi_macd_strategy.py

import pandas as pd
import ta


class RSIMACDStrategy:
    def __init__(self, rsi_low=46, rsi_high=60):
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high

    def generate_signal(self, df: pd.DataFrame):
        # Safety check
        if len(df) < 50:
            return None, {}

        # Calculate indicators (if not already present)
        if 'rsi' not in df.columns:
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

        if 'ema_50' not in df.columns:
            df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()

        if 'macd' not in df.columns or 'macd_diff' not in df.columns:
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_diff'] = macd.macd_diff()

        # Drop NA to avoid access issues
        df = df.dropna()

        # Get last values
        rsi = df['rsi'].iloc[-1]
        macd = df['macd'].iloc[-1]
        macd_diff = df['macd_diff'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        close = df['close'].iloc[-1]

        signal = None
        if rsi < self.rsi_low and macd_diff > -0.0005 and close > ema_50 * 0.98:
            signal = 'BUY'
        elif rsi > self.rsi_high and macd_diff < 0.0005 and close < ema_50 * 1.02:
            signal = 'SELL'

        print(f"Debug: RSI={rsi}, MCD Diff={macd_diff}, Close={close}, EMA50={ema_50}, Signal={signal}")

        return signal, {
            'rsi': rsi,
            'macd': macd,
            'macd_diff': macd_diff,
            'ema_50': ema_50,
            'entry_price': close
        }

