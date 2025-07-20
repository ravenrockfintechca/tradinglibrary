def move_vix_spike(move, vix, zscore_thresh=2):
    spread = (vix - move)
    zscore = (spread - spread.rolling(20).mean()) / spread.rolling(20).std()
    return (zscore > zscore_thresh).astype(int)