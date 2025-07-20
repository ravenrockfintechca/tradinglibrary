def atr_breakout(prices, atr, factor=1.5):
    entry = prices.shift(1) + atr.shift(1) * factor
    return (prices > entry).astype(int)