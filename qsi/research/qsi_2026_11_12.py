"""QSI-091..095 research primitives. No live trading or backtest claims."""
import numpy as np
import pandas as pd

def avellaneda_stoikov_quotes(mid, inventory, gamma, sigma, horizon, k):
    """Symmetric fill-intensity simplification; not exchange executable quotes."""
    if min(gamma, sigma, horizon, k) <= 0:
        raise ValueError('positive gamma/sigma/horizon/k required')
    reservation = mid - inventory * gamma * sigma**2 * horizon
    spread = gamma * sigma**2 * horizon + 2 / gamma * np.log(1 + gamma / k)
    return reservation - spread / 2, reservation + spread / 2

def liquidity_beta(stock_excess_returns, liquidity_innovations):
    x = np.asarray(liquidity_innovations, float)
    y = np.asarray(stock_excess_returns, float)
    if x.shape != y.shape or x.size < 3 or np.var(x) == 0:
        raise ValueError('invalid arrays')
    return float(np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1))

def nonlinear_prediction(features, fitted_model):
    """PIT features only. fitted_model must be trained on strictly prior dates."""
    return np.asarray(fitted_model.predict(np.asarray(features, float)), float)

def same_calendar_month_seasonality(monthly_returns, target_month, years=5):
    """Series has a DatetimeIndex and contains only previously observed months."""
    s = pd.Series(monthly_returns, dtype=float)
    s = s[s.index.month == target_month].tail(years)
    return float(s.mean()) if len(s) == years else np.nan

def embedded_leverage_penalty(leverage_multiplier, expected_gross_return, annual_fee=0.0):
    if leverage_multiplier <= 0:
        raise ValueError('leverage must be positive')
    return expected_gross_return - annual_fee * leverage_multiplier

def smoke_test():
    bid, ask = avellaneda_stoikov_quotes(100, 1, 0.1, 0.2, 1, 2)
    assert bid < ask and (bid + ask)/2 < 100
    assert abs(liquidity_beta([1,2,3], [1,2,3]) - 1) < 1e-12
    class Model:
        def predict(self, x): return x[:, 0] ** 2
    assert nonlinear_prediction([[2],[3]], Model()).tolist() == [4,9]
    ix = pd.date_range('2020-01-31', periods=60, freq='ME')
    assert abs(same_calendar_month_seasonality(pd.Series(np.ones(60)*.02,index=ix),1)-.02)<1e-12
    assert abs(embedded_leverage_penalty(3, .1, .01)-.07)<1e-12
    return '5/5 PASS'
if __name__ == '__main__':
    print(smoke_test())
