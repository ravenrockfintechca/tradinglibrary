def aurora_strategy(audjpy, vix, vix_entry_level=14, audjpy_target=100, upper_limit=107):
    '''
    AURORA Strategy:
    - Go long AUDJPY from ~96 to 100
    - During VIX decline from 16 → 14, buy OTM VIX calls as tail hedge
    - If AUDJPY hits 107, reverse to short position and watch for macro trigger
    '''
    import numpy as np
    import pandas as pd

    signal = pd.Series(0, index=audjpy.index)

    # Long AUDJPY: from 96 up to 100
    long_zone = (audjpy >= 96) & (audjpy < audjpy_target)
    signal[long_zone] = 1

    # Reverse Short AUDJPY: if > upper limit (107)
    short_zone = audjpy >= upper_limit
    signal[short_zone] = -1

    # Tail hedge: when VIX drops to 14 area (OTM call entry timing)
    vix_buy_zone = (vix.shift(1) > 14.5) & (vix <= vix_entry_level)
    vix_call_hint = pd.Series(vix_buy_zone.astype(int), index=audjpy.index)

    return signal, vix_call_hint