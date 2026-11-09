"""QSI-076..080 research primitives; not production trading strategies."""
import numpy as np
import pandas as pd

def ipca_exposure(characteristics, gamma):
    return np.asarray(characteristics, float) @ np.asarray(gamma, float)

def max_daily_return(daily_returns, window=21):
    return pd.DataFrame(daily_returns).rolling(window, min_periods=window).max()

def sentiment_conditional_score(sentiment_z, speculative_exposure):
    return -float(sentiment_z) * np.asarray(speculative_exposure, float)

def fund_flow_ownership_pressure(fund_flows, fund_stock_weights):
    return np.asarray(fund_flows, float) @ np.asarray(fund_stock_weights, float)

def accruals_to_assets(net_income, operating_cashflow, lagged_assets):
    return (np.asarray(net_income, float) - np.asarray(operating_cashflow, float)) / np.asarray(lagged_assets, float)

def smoke_test():
    assert ipca_exposure([[1,2]], [[1],[2]]).shape == (1,1)
    assert max_daily_return([.01,.03,-.02],3).iloc[-1,0] == .03
    assert sentiment_conditional_score(2,[1])[0] == -2
    assert fund_flow_ownership_pressure([-10],[[.5,.5]]).tolist() == [-5,-5]
    assert abs(accruals_to_assets([20],[12],[100])[0]-.08)<1e-12
    return '5/5 PASS'
if __name__ == '__main__': print(smoke_test())
