def intervention_rebound(price, spike_thresh=0.05):
    move = price.pct_change()
    return ((move < -spike_thresh) & (move.shift(1) > spike_thresh)).astype(int)