def copper_gold_signal(copper, gold, window=30):
    ratio = copper / gold
    return (ratio - ratio.rolling(window).mean()) > 0