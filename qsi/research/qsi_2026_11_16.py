"""QSI 2026-11-16: five research-only numerical primitives. No trading or backtesting."""
import math
import numpy as np

def pair_ssd(a,b):
    x=np.asarray(a,dtype=float); y=np.asarray(b,dtype=float)
    if x.shape!=y.shape or x.ndim!=1 or x.size<3 or not np.isfinite(x).all() or not np.isfinite(y).all() or min(x.min(),y.min())<=0: raise ValueError("invalid price series")
    return float(np.sum((x/x[0]-y/y[0])**2))

def opening_put_call_ratio(buyer_open_puts,buyer_open_calls):
    p=float(buyer_open_puts); c=float(buyer_open_calls)
    if not all(map(math.isfinite,[p,c])) or p<0 or c<=0: raise ValueError("invalid opening option volume")
    return p/c

def long_straddle_mark_to_market(call_entry,put_entry,call_exit,put_exit):
    v=np.asarray([call_entry,put_entry,call_exit,put_exit],float)
    if not np.isfinite(v).all() or np.any(v<0) or v[0]+v[1]<=0: raise ValueError("invalid option prices")
    return float((v[2]+v[3])/(v[0]+v[1])-1)

def index_addition_event(announced_at,tradable_at):
    """Signal must not be tradable before public announcement; times are comparable numeric timestamps."""
    a=float(announced_at); t=float(tradable_at)
    if not math.isfinite(a) or not math.isfinite(t): raise ValueError("invalid timestamp")
    return int(t>=a)

def momentum_crash_risk_scale(market_drawdown,realized_vol,drawdown_threshold=-0.15,vol_threshold=0.30):
    """Illustrative risk overlay, NOT the paper's optimized conditional mean-variance model."""
    d=float(market_drawdown); v=float(realized_vol)
    if not math.isfinite(d) or not math.isfinite(v) or v<0: raise ValueError("invalid risk inputs")
    return 0.25 if d<=drawdown_threshold and v>=vol_threshold else 1.0

def smoke_test():
    assert abs(pair_ssd([10,11,12],[20,22,24]))<1e-12
    assert opening_put_call_ratio(10,20)==0.5
    assert abs(long_straddle_mark_to_market(2,3,3,4)-0.4)<1e-12
    assert index_addition_event(10,9)==0 and index_addition_event(10,10)==1
    assert momentum_crash_risk_scale(-.2,.4)==.25
    for fn,args in [(pair_ssd,([1,2],[1,2])),(opening_put_call_ratio,(1,0)),(long_straddle_mark_to_market,(0,0,1,1)),(momentum_crash_risk_scale,(-.2,-.1))]:
        try: fn(*args)
        except ValueError: pass
        else: raise AssertionError("invalid input accepted")
    return "9/9 PASS"

if __name__=="__main__": print(smoke_test())
