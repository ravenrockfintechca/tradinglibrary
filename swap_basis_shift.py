def detect_basis_shift(spot, forward, ir_spread, threshold=0.01):
    basis = forward - spot - ir_spread
    return (basis.abs() > threshold).astype(int)