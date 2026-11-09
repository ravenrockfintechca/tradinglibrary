"""QSI-081..085 numerical primitives. Research only; not execution/backtests."""
from datetime import date
from statistics import pstdev, mean

def merger_spread(target_price, cash_offer, break_price, completion_probability):
    """Cash-only merger; expected gross P&L per share, excluding time/cost."""
    assert 0 <= completion_probability <= 1 and target_price > 0
    spread = cash_offer / target_price - 1
    expected = (completion_probability * cash_offer + (1-completion_probability) * break_price) / target_price - 1
    return {"gross_spread": spread, "expected_return": expected}

def fx_ppp_value(spot_quote_usd_per_ccy, ppp_quote_usd_per_ccy):
    """Positive means foreign currency cheap versus PPP (USD per unit)."""
    assert spot_quote_usd_per_ccy > 0 and ppp_quote_usd_per_ccy > 0
    return ppp_quote_usd_per_ccy / spot_quote_usd_per_ccy - 1

def treasury_net_basis(cash_dirty_price, futures_price, conversion_factor, carry_to_delivery):
    """Cash minus converted futures minus net carry; all same price units."""
    assert conversion_factor > 0 and futures_price > 0
    return cash_dirty_price - futures_price * conversion_factor - carry_to_delivery

def turn_of_month_flag(trading_dates, last_old_month=1, first_new_month=3):
    """Label last trading day and first 3 trading days of each month; no calendar-day assumption."""
    ds = [date.fromisoformat(x) if isinstance(x, str) else x for x in trading_dates]
    assert ds == sorted(set(ds)), 'unique ascending trading dates required'
    result = [False] * len(ds)
    bymonth = {}
    for i, d in enumerate(ds): bymonth.setdefault((d.year, d.month), []).append(i)
    months = list(bymonth)
    for j, month in enumerate(months):
        ix = bymonth[month]
        if j > 0:
            for i in ix[:first_new_month]: result[i] = True
        if j < len(months)-1:
            for i in ix[-last_old_month:]: result[i] = True
    return result

def analyst_forecast_dispersion(forecasts, consensus_floor=0.01):
    """Std of point-in-time EPS forecasts / max(abs(mean),floor)."""
    assert len(forecasts) >= 2 and consensus_floor > 0
    return pstdev(forecasts) / max(abs(mean(forecasts)), consensus_floor)

def smoke_tests():
    a = merger_spread(90, 100, 50, 0.9)
    assert abs(a['gross_spread'] - 1/9) < 1e-12
    assert abs(a['expected_return'] - (95/90-1)) < 1e-12
    assert abs(fx_ppp_value(1.0, 1.2) - 0.2) < 1e-12
    assert abs(treasury_net_basis(101, 100, 0.99, 1) - 1) < 1e-12
    assert turn_of_month_flag(['2026-10-29','2026-10-30','2026-11-02','2026-11-04','2026-11-05']) == [False,True,True,True,True]
    assert abs(analyst_forecast_dispersion([1, 2, 3]) - (2/3)**0.5 / 2) < 1e-12
    return '5/5 PASS'

if __name__ == '__main__': print(smoke_tests())
