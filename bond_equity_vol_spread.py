def bond_equity_vol_spread(vix, move, threshold=10):
    spread = vix - move
    return (spread > threshold).astype(int)