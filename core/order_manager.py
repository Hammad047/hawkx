# core/order_manager.py

from core.risk_management import calculate_position_size, calculate_tp_sl
from utils.logger import setup_logger
from utils.email_alert import send_email

logger = setup_logger(__name__)

class OrderManager:
    def __init__(self, broker, capital, email_config=None):
        self.broker = broker
        self.capital = capital
        self.email_config = email_config

    def process_signal(self, symbol, timeframe, signal, metadata):
        entry_price = metadata['entry_price']
        volatility = abs(metadata['macd_diff'])  # crude proxy
        tp, sl = calculate_tp_sl(entry_price, volatility, signal)
        position_size = calculate_position_size(self.capital, entry_price, sl)

        logger.info(f"Placing {signal} order for {symbol} [{timeframe}]")
        logger.info(f"Entry: {entry_price}, TP: {tp}, SL: {sl}, Qty: {position_size}")

        try:
            if signal == "BUY":
                order = self.broker.place_order(symbol, "buy", amount=position_size, price=None, type='market')
            elif signal == "SELL":
                order = self.broker.place_order(symbol, "sell", amount=position_size, price=None, type='market')
            else:
                logger.warning("Unknown signal, skipping.")
                return

            logger.info(f"Order placed: {order}")
            self.send_trade_alert(symbol, timeframe, signal, entry_price, tp, sl, position_size)

        except Exception as e:
            logger.error(f"Failed to place order for {symbol}: {e}")

    def send_trade_alert(self, symbol, timeframe, signal, entry, tp, sl, qty):
        if not self.email_config or not self.email_config.get('enabled'):
            return

        body = f"""
🔔 Live Trade Executed 🔔

🪙 Symbol: {symbol}
🕒 Timeframe: {timeframe}
📈 Signal: {signal}
💰 Entry Price: ${entry:.4f}
📦 Quantity: {qty}
🎯 Take Profit: ${tp}
🛡 Stop Loss: ${sl}
"""
        send_email(
            subject=f"{signal} EXECUTED: {symbol} [{timeframe}]",
            body=body,
            config=self.email_config
        )
