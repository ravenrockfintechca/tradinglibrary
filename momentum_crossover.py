def momentum_signal(prices, short=10, long=30):
    sma_short = prices.rolling(short).mean()
    sma_long = prices.rolling(long).mean()
    return (sma_short > sma_long).astype(int)
