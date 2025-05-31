
def calculate_position_size(capital: float, entry_price: float, stop_loss_price: float) -> float:
    # e.g., risk 2% of capital per trade
    risk_per_trade = capital * 0.02
    stop_loss_amount = abs(entry_price - stop_loss_price)
    position_size = risk_per_trade / stop_loss_amount if stop_loss_amount else 0
    return round(position_size, 4)

def calculate_tp_sl(price: float, volatility: float, signal: str) -> tuple:
    if signal == "BUY":
        tp = price + volatility * 0.5
        sl = price - volatility * 0.5
    elif signal == "SELL":
        tp = price - volatility * 0.5
        sl = price + volatility * 0.5
    else:
        tp = sl = price  # fallback
    return round(tp, 4), round(sl, 4)
