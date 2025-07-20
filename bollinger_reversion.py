def bollinger_signal(prices, window=20, k=2):
    ma = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    upper, lower = ma + k*std, ma - k*std
    return ((prices < lower) | (prices > upper)).astype(int)
