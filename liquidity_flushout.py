def liquidity_flush(volume, price, window=5):
    spike = volume > volume.rolling(window).mean() * 3
    dump = price.pct_change() < -0.08
    return (spike & dump).astype(int)