
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import os

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

def add_indicators(df):
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    df['ema_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
    return df

def evaluate_signals(df):
    buy_signals = []
    sell_signals = []

    for i in range(1, len(df)):
        rsi = df['rsi'].iloc[i]
        macd_diff = df['macd_diff'].iloc[i]
        close = df['close'].iloc[i]
        ema_50 = df['ema_50'].iloc[i]

        if rsi < 50 and macd_diff > 0 and close > ema_50:
            buy_signals.append((df.index[i], rsi, macd_diff))
        elif rsi > 50 and macd_diff < 0 and close < ema_50:
            sell_signals.append((df.index[i], rsi, macd_diff))

    return buy_signals, sell_signals

def summarize(signals, label):
    if not signals:
        print(f"No {label} signals detected.")
        return
    avg_rsi = sum([r[1] for r in signals]) / len(signals)
    avg_macd = sum([r[2] for r in signals]) / len(signals)
    print(f"{label} signals: {len(signals)}")
    print(f"Average RSI at signal: {avg_rsi:.2f}")
    print(f"Average MACD diff at signal: {avg_macd:.4f}")

if __name__ == '__main__':
    file_path = 'sample_ohlcv.csv'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        exit()

    df = load_data(file_path)
    df = add_indicators(df)
    buy_signals, sell_signals = evaluate_signals(df)

    summarize(buy_signals, "BUY")
    summarize(sell_signals, "SELL")