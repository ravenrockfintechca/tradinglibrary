"""ZTrader QSI 2026-11-15: five research primitives, not full paper replication."""
import numpy as np

def common_tail_proxy(returns, q=0.05):
    """Rows=dates, columns=stocks; negative cross-sectional tail mean per date."""
    a=np.asarray(returns,dtype=float)
    if a.ndim!=2 or not 0<q<1: raise ValueError("2D returns and 0<q<1 required")
    threshold=np.nanquantile(a,q,axis=1)
    return np.array([np.nanmean(row[row<=cut]) for row,cut in zip(a,threshold)])

def supplier_customer_signal(customer_returns, revenue_weights):
    """Matrix supplier x customer times lagged customer returns."""
    w=np.asarray(revenue_weights,dtype=float); r=np.asarray(customer_returns,dtype=float)
    if w.ndim!=2 or r.ndim!=1 or w.shape[1]!=len(r) or np.any(w<0): raise ValueError("shape/weights")
    return w@r

def total_asset_growth(assets_now,assets_prior):
    a=np.asarray(assets_now,dtype=float); b=np.asarray(assets_prior,dtype=float)
    if np.any(b<=0): raise ValueError("lagged assets must be positive")
    return (a-b)/b

def operating_leverage_proxy(revenue_now,revenue_prior,op_income_now,op_income_prior,eps=1e-4):
    rn=np.asarray(revenue_now,dtype=float);rp=np.asarray(revenue_prior,dtype=float)
    en=np.asarray(op_income_now,dtype=float);ep=np.asarray(op_income_prior,dtype=float)
    if np.any(rp<=0) or np.any(np.abs(ep)<eps): raise ValueError("unstable prior base")
    rev_change=(rn-rp)/rp
    if np.any(np.abs(rev_change)<eps): raise ValueError("near-zero sales growth")
    return ((en-ep)/np.abs(ep))/rev_change

def intangible_return_proxy(past_return,accounting_explained_return):
    """Residual from separately trained PIT fundamental-news return model."""
    return np.asarray(past_return,dtype=float)-np.asarray(accounting_explained_return,dtype=float)

def smoke_test():
    assert np.allclose(common_tail_proxy([[-.2,.1,.03],[-.1,.04,.02]]),[-.2,-.1])
    assert np.allclose(supplier_customer_signal([.1,-.2],[[.6,.4],[0,1]]),[-.02,-.2])
    assert np.allclose(total_asset_growth([110,90],[100,100]),[.1,-.1])
    assert np.allclose(operating_leverage_proxy(110,100,24,20),2.)
    assert np.allclose(intangible_return_proxy([.2,.1],[.08,.05]),[.12,.05])
    for fn,args in [(total_asset_growth,(10,0)),(operating_leverage_proxy,(100,100,20,20))]:
        try: fn(*args)
        except ValueError: pass
        else: raise AssertionError("missing invalid-input guard")
    return "7/7 PASS"
if __name__=="__main__": print(smoke_test())
