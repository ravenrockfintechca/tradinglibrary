def detect_quote_stuffing(order_counts, threshold=50):
    return (order_counts.diff().rolling(5).max() > threshold).astype(int)