"""QSI-096..100: educational signal primitives, no backtesting/execution."""
import numpy as np
import pandas as pd

def high52_proximity(close, high, window=252):
    c, h = pd.Series(close, dtype=float), pd.Series(high, dtype=float)
    peak = h.rolling(window, min_periods=window).max()
    return c.div(peak).where(peak > 0)

def amihud_illiq(returns, dollar_volume):
    r, v = np.asarray(returns, dtype=float), np.asarray(dollar_volume, dtype=float)
    return np.divide(np.abs(r), v, out=np.full(np.broadcast_shapes(r.shape,v.shape), np.nan), where=v>0)

def capital_gain_overhang(prices, turnover):
    """Simple turnover-weighted reference price, not Grinblatt-Han full estimator."""
    p, t = np.asarray(prices,float), np.asarray(turnover,float)
    if p.shape != t.shape or p.ndim != 1 or len(p)==0 or np.any(t<0): raise ValueError('invalid price/turnover')
    weights = t / np.sum(t) if np.sum(t)>0 else np.full(len(t),1/len(t))
    reference = np.dot(weights,p)
    return (p[-1]-reference)/p[-1] if p[-1]>0 else np.nan

def dividend_policy_event(previous_dividend, new_dividend):
    a,b=float(previous_dividend),float(new_dividend)
    if a<0 or b<0: raise ValueError('negative dividend')
    return 1 if a==0 and b>0 else (-1 if a>0 and b==0 else 0)

def split_announcement_signal(new_shares_per_old_share):
    """Split ratio >1; corporate-action event, not adjusted price jump."""
    ratio=float(new_shares_per_old_share)
    if ratio<=0: raise ValueError("invalid ratio")
    return np.log(ratio) if ratio>1 else 0.0

def test_primitives():
    assert abs(high52_proximity([9,10,8],[9,10,8],3).iloc[-1]-0.8)<1e-12
    assert abs(amihud_illiq([0.02],[100000])[0]-2e-7)<1e-14
    assert capital_gain_overhang([80,100],[1,1])>0
    assert dividend_policy_event(0,1)==1 and dividend_policy_event(1,0)==-1
    assert abs(split_announcement_signal(2)-np.log(2))<1e-12
    return '5/5 PASS'

if __name__=='__main__': print(test_primitives())
