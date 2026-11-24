"""QSI-151..155: scalar research primitives, not executable trade strategies."""
import math
import unittest


def finite(*values):
    if not all(math.isfinite(x) for x in values):
        raise ValueError("nonfinite input")


def positive(*values):
    finite(*values)
    if any(x <= 0 for x in values):
        raise ValueError("positive input required")


def fx_fix_phase_return(entry_usd_per_foreign, exit_usd_per_foreign):
    """Ex-post foreign currency return in USD; not a forecast."""
    positive(entry_usd_per_foreign, exit_usd_per_foreign)
    return exit_usd_per_foreign / entry_usd_per_foreign - 1


def cef_catalyst_discount(price, nav, catalyst_probability):
    """Discount times externally estimated PIT catalyst probability; proxy only."""
    positive(price, nav)
    finite(catalyst_probability)
    if not 0 <= catalyst_probability <= 1:
        raise ValueError("probability outside [0,1]")
    return max(0.0, 1 - price / nav) * catalyst_probability


def ex_dividend_net_return(pre_ask, post_bid, cash_dividend, dividend_tax_rate, other_cost):
    """Simplified realized holding return; excludes capital-gain taxes."""
    positive(pre_ask, post_bid)
    finite(cash_dividend, dividend_tax_rate, other_cost)
    if cash_dividend < 0 or other_cost < 0 or not 0 <= dividend_tax_rate <= 1:
        raise ValueError("invalid dividend, tax, or cost")
    return (post_bid + cash_dividend * (1 - dividend_tax_rate) - other_cost) / pre_ask - 1


def dual_listing_log_parity(price_a, price_b, usd_per_a, usd_per_b, entitlement_a, entitlement_b):
    """Log premium of A per common economic entitlement, in USD."""
    positive(price_a, price_b, usd_per_a, usd_per_b, entitlement_a, entitlement_b)
    return math.log(price_a) + math.log(usd_per_a) - math.log(entitlement_a) - math.log(price_b) - math.log(usd_per_b) + math.log(entitlement_b)


def tips_replication_gap(nominal_dirty, tips_dirty, hedge_pv, financing_pv=0):
    """Nominal less synthetic dirty PV, per identical nominal cash flows.

    hedge_pv is signed cost of inflation swaps and other matching cash flows.
    financing_pv is a nonnegative incremental cost PV. No cash-flow matching here.
    """
    positive(nominal_dirty, tips_dirty)
    finite(hedge_pv, financing_pv)
    if financing_pv < 0:
        raise ValueError("negative cost")
    return nominal_dirty - tips_dirty - hedge_pv - financing_pv


class TestResearch(unittest.TestCase):
    def test_fx_up(self): self.assertAlmostEqual(fx_fix_phase_return(1, 1.02), .02)
    def test_fx_down(self): self.assertAlmostEqual(fx_fix_phase_return(1, .98), -.02)
    def test_fx_flat(self): self.assertEqual(fx_fix_phase_return(2, 2), 0)
    def test_fx_invalid(self):
        with self.assertRaises(ValueError): fx_fix_phase_return(0, 1)
    def test_cef_discount(self): self.assertAlmostEqual(cef_catalyst_discount(80, 100, .5), .1)
    def test_cef_premium(self): self.assertEqual(cef_catalyst_discount(105, 100, .5), 0)
    def test_cef_zero(self): self.assertEqual(cef_catalyst_discount(80, 100, 0), 0)
    def test_cef_invalid(self):
        with self.assertRaises(ValueError): cef_catalyst_discount(80, 100, 1.1)
    def test_div_flat(self): self.assertAlmostEqual(ex_dividend_net_return(100, 98, 2, 0, 0), 0)
    def test_div_tax(self): self.assertAlmostEqual(ex_dividend_net_return(100, 98, 2, .25, .1), -.006)
    def test_div_profit(self): self.assertAlmostEqual(ex_dividend_net_return(100, 99, 2, 0, 0), .01)
    def test_div_invalid(self):
        with self.assertRaises(ValueError): ex_dividend_net_return(100, 99, 2, -1, 0)
    def test_dual_parity(self): self.assertAlmostEqual(dual_listing_log_parity(50, 100, 2, 1, 1, 1), 0)
    def test_dual_ratio(self): self.assertAlmostEqual(dual_listing_log_parity(200, 100, 1, 1, 2, 1), 0)
    def test_dual_premium(self): self.assertAlmostEqual(dual_listing_log_parity(110, 100, 1, 1, 1, 1), math.log(1.1))
    def test_dual_invalid(self):
        with self.assertRaises(ValueError): dual_listing_log_parity(100, 100, 1, 1, 0, 1)
    def test_tips_gap(self): self.assertEqual(tips_replication_gap(110, 90, 5, 2), 13)
    def test_tips_signed(self): self.assertEqual(tips_replication_gap(100, 100, -2), 2)
    def test_tips_invalid(self):
        with self.assertRaises(ValueError): tips_replication_gap(100, 100, 0, -1)
    def test_nonfinite(self):
        with self.assertRaises(ValueError): tips_replication_gap(100, 100, float('nan'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
