import argparse
import asyncio
import time
import logging
from datetime import datetime
from collections import Counter

from core.okx_interface import OKXInterface
from core.signal_engine import SignalEngine
from core.risk_management import calculate_position_size, calculate_tp_sl
from data.fetcher import DataFetcher
from data.storage import DataStorage
from config.settings import SETTINGS
from utils.email_alert import send_email
from utils.signal_utils import finalize_signal


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def analyze_symbol(symbol, broker, signal_engine, capital, final_signal=None, test_mode=False):
    try:
        logger.info(f"🔍 Starting analysis for {symbol}")

        ticker = broker.fetch_ticker(symbol)
        last_price = ticker['last']
        vol = ticker.get('quoteVolume', 0)
        if last_price > SETTINGS['trading']['price_max_threshold']:
            return
        if vol < SETTINGS['trading']['volume_min_threshold']:
            return

        logger.info(f"Analyzing {symbol} — Price: {last_price}, Volume: {vol}")
        fetcher = DataFetcher(broker)
        df_dict = {tf: fetcher.get_symbol_data(symbol, tf) for tf in SETTINGS['trading']['timeframes']}

        decisions = []
        for tf, df in df_dict.items():
            if df is None or df.empty:
                continue
            result = signal_engine.generate(df)
            logger.info(f"[{symbol}][{tf}] Signal: {result.signal}, RSI: {result.rsi:.2f}, MACD: {result.macd:.4f}")
            decisions.append((tf, result.signal, result))

        print(f"decisions: {decisions}")

        final_signal, confidence, result_meta = finalize_signal(decisions, required_consensus=2)
        logger.info(f"[SIGNAL SUMMARY] {symbol} => {final_signal} (Confidence: {confidence})")

        if final_signal:
            result_meta = vars(result_meta) if result_meta else {}

            volatility = df_dict[SETTINGS['trading']['timeframes'][0]]['high'].tail(10).max() - \
                         df_dict[SETTINGS['trading']['timeframes'][0]]['low'].tail(10).min()
            tp, sl = calculate_tp_sl(last_price, volatility, final_signal)
            position_size = calculate_position_size(capital, last_price, sl)

            timestamp = df_dict[SETTINGS['trading']['timeframes'][0]].index[-1]
            message = f"""
🔔 Signal: {final_signal}
📈 Symbol: {symbol}
🕒 Time: {timestamp.strftime('%Y-%m-%d %H:%M')}
💰 Price: {last_price}
🎯 TP: {tp}, 🛡 SL: {sl}
📦 Size: {position_size}
🕒 Timeframes: {[tf for tf, _, _ in decisions]}
📊 RSI: {result_meta.get('rsi', 'N/A'):.2f}, MACD: {result_meta.get('macd', 'N/A'):.4f}
"""

            email_cfg = SETTINGS['alerts']['email']
            if email_cfg and email_cfg.get('enabled'):
                send_email(
                    subject=f"🚨 {final_signal} Signal on {symbol}",
                    body=message,
                    config=email_cfg
                )

            trade_data = {
                "symbol": symbol,
                "signal": final_signal,
                "timestamp": datetime.utcnow().isoformat(),
            }

            save_logs = DataStorage()
            x = save_logs.save_trade_log_csv(trade_data)
            print(f"X: {x}")

            # 🔁 LIVE TRADE IF NOT IN TEST MODE
            if not test_mode:
                from core.order_manager import OrderManager
                order_manager = OrderManager(broker, "20")
                order_response = order_manager.execute_order(symbol, final_signal, price=last_price, tp=tp, sl=sl)


                # 🔔 Email confirmation for live order
                if email_cfg and email_cfg.get('enabled'):
                    send_email(
                        subject=f"📤 Executed {final_signal} Order on {symbol}",
                        body=f"Order placed successfully!\n\nDetails:\n{message}",
                        config=email_cfg
                    )

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")


async def main(test_mode=False, final_signal=None, custom_symbols=None):
    broker = OKXInterface(SETTINGS['api']['okx'])
    broker.connect()

    signal_engine = SignalEngine(strategy_name=SETTINGS['trading']['strategy'])

    all_symbols = [
        s for s in broker.exchange.symbols
        if s.endswith("/USDT") and broker.exchange.markets[s]['active']
    ]

    if custom_symbols:
        normalized = []
        for sym in custom_symbols:
            sym_usdt = sym if sym.endswith('/USDT') else sym + '/USDT'
            if sym_usdt in all_symbols:
                normalized.append(sym_usdt)
            else:
                logger.warning(f"Symbol {sym_usdt} not found or inactive.")
        filtered_symbols = normalized
        logger.info(f"[MANUAL SYMBOL OVERRIDE] Running only for: {filtered_symbols}")
    else:
        filtered_symbols = []
        for s in all_symbols:
            try:
                ticker = broker.fetch_ticker(s)
                if ticker['quoteVolume'] > SETTINGS['trading']['volume_min_threshold'] and ticker['last'] < SETTINGS['trading']['price_max_threshold']:
                    filtered_symbols.append(s)
            except Exception:
                continue

    logger.info(f"Scanning {len(filtered_symbols)} symbols...")
    for symbol in filtered_symbols:
        await analyze_symbol(symbol, broker, signal_engine, SETTINGS['trading']['capital_usd'],
                             final_signal=final_signal, test_mode=test_mode)


if __name__ == '__main__':
    while True:
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--test-mode', action='store_true', help="Run in test mode without executing trades")
            parser.add_argument('--final-signal', choices=["BUY", "SELL"], help="Force a signal for testing purposes")
            parser.add_argument('--symbol', nargs='+', help="Analyze only specific symbols (e.g., RDNT ETH SOL)")
            args = parser.parse_args()

            asyncio.run(main(test_mode=args.test_mode, final_signal=args.final_signal, custom_symbols=args.symbol))

            logger.info("✅ Scan complete. Sleeping 10 min...")
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Stopped by user.")
            break
        except Exception as e:
            logger.critical(f"Unhandled error: {e}")
            time.sleep(60)
