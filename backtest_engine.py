def backtest(prices, signal):
    returns = prices.pct_change().shift(-1)
    strat_returns = signal.shift(1) * returns
    return strat_returns.cumsum()
