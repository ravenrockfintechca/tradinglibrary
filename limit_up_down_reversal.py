def detect_limit_reversal(prices, limit_pct=0.09):
    returns = prices.pct_change()
    return ((returns.shift(1) > limit_pct) & (returns < -0.03)).astype(int)