"""QSI-116..120 research-only signal primitives; not a trading system."""
def cash_holdings_change(cash_t, assets_t, cash_prev, assets_prev):
    if min(assets_t, assets_prev) <= 0: raise ValueError("assets must be positive")
    return cash_t/assets_t-cash_prev/assets_prev

def innovative_efficiency(patents, rd_spend):
    if rd_spend <= 0: raise ValueError("R&D must be positive")
    return patents/rd_spend

def employee_satisfaction_signal(is_publicly_ranked, publication_known):
    return int(bool(is_publicly_ranked) and bool(publication_known))

def advertising_change(ad_t, sales_t, ad_prev, sales_prev):
    if min(sales_t, sales_prev) <= 0: raise ValueError("sales must be positive")
    return ad_t/sales_t-ad_prev/sales_prev

def tax_loss_pressure(prior_return, december, taxable_market=True):
    return max(0.,-float(prior_return)) if december and taxable_market else 0.

def smoke_test():
    assert abs(cash_holdings_change(30,100,20,100)-.1)<1e-12
    assert innovative_efficiency(12,6)==2
    assert employee_satisfaction_signal(True,True)==1
    assert employee_satisfaction_signal(True,False)==0
    assert abs(advertising_change(4,100,2,100)-.02)<1e-12
    assert tax_loss_pressure(-.3,True)==.3
    assert tax_loss_pressure(-.3,False)==0
    for fn,args in [(cash_holdings_change,(1,0,1,1)),(innovative_efficiency,(1,0)),(advertising_change,(1,0,1,1))]:
        try: fn(*args)
        except ValueError: pass
        else: raise AssertionError("invalid input not rejected")
    return "10/10 PASS"
if __name__=="__main__": print(smoke_test())
