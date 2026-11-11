"""QSI-086..090 numerical research primitives. No orders or backtest."""
def buyback_announcement_score(repurchase_fraction, book_to_market):
    return float(repurchase_fraction)*float(book_to_market)
def hedger_pressure(net_commercial_short, open_interest):
    if open_interest<=0: raise ValueError("open_interest must be positive")
    return float(net_commercial_short)/float(open_interest)
def variance_risk_premium(implied_variance, forecast_realized_variance):
    return float(implied_variance)-float(forecast_realized_variance)
def relative_call_put_iv(call_iv, put_iv):
    return float(call_iv)-float(put_iv)
def seo_dilution_fraction(new_shares, pre_issue_shares):
    if pre_issue_shares<=0: raise ValueError("pre_issue_shares must be positive")
    return float(new_shares)/float(pre_issue_shares)
def smoke_test():
    assert abs(buyback_announcement_score(.1,.8)-.08)<1e-12
    assert abs(hedger_pressure(25,100)-.25)<1e-12
    assert abs(variance_risk_premium(.09,.04)-.05)<1e-12
    assert abs(relative_call_put_iv(.28,.23)-.05)<1e-12
    assert abs(seo_dilution_fraction(10,100)-.1)<1e-12
    try: hedger_pressure(1,0)
    except ValueError: pass
    else: raise AssertionError("zero open interest should fail")
    print("6/6 PASS (synthetic arithmetic only)")
if __name__=="__main__": smoke_test()
