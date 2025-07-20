def vix_filter(vix_series, threshold=20):
    return (vix_series < threshold).astype(int)