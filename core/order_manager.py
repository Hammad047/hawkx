# core/order_manager.py
from core.risk_management import calculate_position_size
from utils.logger import setup_logger
from datetime import datetime
from utils.email_alert import send_email
from data.storage import DataStorage

logger = setup_logger(__name__)


class OrderManager:
    def __init__(self, broker, capital_usd, risk_pct=1.0):
        self.broker = broker
        self.capital_usd = capital_usd
        self.risk_pct = risk_pct


    def execute_order(self, symbol, signal, price=None, tp=None, sl=None):
        try:
            # ✅ Fetch live price if not provided
            if price is None:
                price = self.broker.fetch_ticker(symbol)['last']

            # Ensure numeric types
            price = float(price)
            tp = float(tp) if tp is not None else None
            sl = float(sl) if sl is not None else None

            side = 'buy' if signal.upper() == 'BUY' else 'sell'

            # ✅ Use updated position size logic
            position_size = calculate_position_size(self.capital_usd, price, sl)

            logger.info(f"[ORDER] Placing {signal.upper()} for {symbol} — Size: {position_size}, Price: {price}")
            self.broker.place_order(
                symbol=symbol,
                side=side,
                amount=position_size,
                price=price,
                type='market'
            )

            timestamp = datetime.utcnow().isoformat()
            trade_log = {
                "symbol": symbol,
                "side": signal,
                "price": price,
                "stop_loss": sl,
                "take_profit": tp,
                "qty": position_size,
                "timestamp": timestamp
            }

            # ✅ Log to CSV
            DataStorage().save_trade_log_csv(trade_log)

            # ✅ Email notification
            from config.settings import SETTINGS
            email_cfg = SETTINGS['alerts']['email']
            if email_cfg and email_cfg.get("enabled"):
                message = f"""
    🚀 Trade Executed: {signal.upper()}
    📈 Symbol: {symbol}
    💰 Entry Price: {price}
    🎯 Take Profit: {tp}
    🛡 Stop Loss: {sl}
    📦 Size: {position_size}
    🕒 Time: {timestamp}
                """
                send_email(
                    subject=f"📢 Trade Executed: {signal.upper()} {symbol}",
                    body=message.strip(),
                    config=email_cfg
                )

            return trade_log

        except Exception as e:
            logger.error(f"[ORDER FAILED] {symbol}: {e}")
            return None