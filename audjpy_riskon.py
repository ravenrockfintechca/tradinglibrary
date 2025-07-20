def audjpy_riskon(audjpy, window=10):
    return (audjpy.pct_change(window) > 0).astype(int)