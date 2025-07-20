def combo_signal(trend_sig, vix_sig, audjpy_sig):
    return (trend_sig * vix_sig * audjpy_sig).astype(int)