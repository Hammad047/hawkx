# utils/signal_utils.py
from collections import Counter


def finalize_signal(decisions, required_consensus=2):
    """
    Determine the final signal from a list of decisions across timeframes.
    Each decision is a tuple (timeframe, signal, metadata).

    Returns:
        - final_signal: 'BUY', 'SELL', or None
        - confidence: 'HIGH', 'LOW', or 'NO_SIGNAL'
        - metadata: associated metadata dict
    """
    aligned_signals = [s for _, s, _ in decisions if s]
    if not aligned_signals:
        return None, "NO_SIGNAL", {}

    signal_counts = Counter(aligned_signals)
    most_common_signal, count = signal_counts.most_common(1)[0]

    print(f"Aligned Signals for SIGNALLLLLLLLLLLL: {aligned_signals}")
    if count >= required_consensus:
        confidence = "HIGH"
        result_meta = next(meta for _, s, meta in decisions if s == most_common_signal)
        return most_common_signal, confidence, result_meta

    elif count >= 1:
        confidence = "LOW"
        result_meta = next(meta for _, s, meta in decisions if s == most_common_signal)
        return most_common_signal, confidence, result_meta

    return None, "NO_SIGNAL", {}
