def gamma_squeeze(vol_change, price_return, vol_threshold=0.5):
    return ((vol_change > vol_threshold) & (price_return > 0.03)).astype(int)