"""QSI-101..105 research primitives, NOT executable trading strategies."""
import math


def noa_ratio(operating_assets, operating_liabilities, lagged_assets):
    if lagged_assets <= 0: raise ValueError('lagged assets must be positive')
    return (operating_assets - operating_liabilities) / lagged_assets


def org_capital_step(prior_stock, sga, depreciation=0.15):
    if prior_stock < 0 or sga < 0 or not 0 <= depreciation <= 1:
        raise ValueError('invalid organizational capital inputs')
    return (1-depreciation)*prior_stock + sga


def convertible_delta_hedge(conversion_ratio, stock_delta, bond_units=1):
    if conversion_ratio < 0 or not 0 <= stock_delta <= 1 or bond_units <= 0:
        raise ValueError('invalid delta hedge inputs')
    return bond_units * conversion_ratio * stock_delta


def fx_risk_reversal(call_iv, put_iv):
    if call_iv < 0 or put_iv < 0: raise ValueError('negative implied volatility')
    return call_iv - put_iv


def curve_butterfly(y_short, y_mid, y_long, w_short=0.5, w_long=0.5):
    if not math.isclose(w_short+w_long, 1, abs_tol=1e-10):
        raise ValueError('weights must sum to 1')
    return y_mid - w_short*y_short - w_long*y_long


def smoke_test():
    assert math.isclose(noa_ratio(120, 50, 100), .7)
    assert math.isclose(org_capital_step(100, 20), 105)
    assert math.isclose(convertible_delta_hedge(20, .4, 2), 16)
    assert math.isclose(fx_risk_reversal(.12, .14), -.02)
    assert math.isclose(curve_butterfly(.03, .04, .05), 0)
    for f, args in [(noa_ratio, (1, 0, 0)), (org_capital_step, (-1, 2)), (fx_risk_reversal, (-.1, .2))]:
        try: f(*args)
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    return '8/8 PASS'


if __name__ == '__main__':
    print(smoke_test())
