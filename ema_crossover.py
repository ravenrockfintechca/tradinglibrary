def ema_crossover(prices, short=9, long=21):
    ema_s = prices.ewm(span=short).mean()
    ema_l = prices.ewm(span=long).mean()
    return (ema_s > ema_l).astype(int)