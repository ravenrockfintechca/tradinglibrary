def delta_neutral_signal(delta, threshold=0.05):
    return (abs(delta) < threshold).astype(int)
