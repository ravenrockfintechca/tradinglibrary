def donchian_signal(prices, window=20):
    high = prices.rolling(window).max()
    low = prices.rolling(window).min()
    return ((prices > high.shift(1)) - (prices < low.shift(1))).fillna(0)
