"""QSI-161..165: research primitives only; no execution or market backtest."""
import math
import unittest


def finite(*xs):
    if not all(math.isfinite(x) for x in xs):
        raise ValueError("nonfinite input")


def relative_wealth(asset_return, benchmark_return):
    """Total holding-period returns, decimal units; benchmark wealth > 0."""
    finite(asset_return, benchmark_return)
    if asset_return < -1 or benchmark_return <= -1:
        raise ValueError("invalid simple return")
    return (1 + asset_return) / (1 + benchmark_return) - 1


def spinoff_shareholder_return(parent_end, child_end, child_ratio, cash, parent_start):
    """Per original parent share; child_ratio shares received, cash distributions."""
    finite(parent_end, child_end, child_ratio, cash, parent_start)
    if min(parent_end, child_end, child_ratio, cash) < 0 or parent_start <= 0:
        raise ValueError("invalid share value or ratio")
    return (parent_end + child_ratio * child_end + cash) / parent_start - 1


def index_rebalance_pressure(target_weight, current_weight, tracking_notional, dollar_adv):
    """Signed notional flow / daily dollar volume; estimate, not observed order flow."""
    finite(target_weight, current_weight, tracking_notional, dollar_adv)
    if not 0 <= target_weight <= 1 or not 0 <= current_weight <= 1 or tracking_notional < 0 or dollar_adv <= 0:
        raise ValueError("invalid weight, notional or ADV")
    return (target_weight - current_weight) * tracking_notional / dollar_adv


def dividend_strip_return(price_paid, dividend_cash):
    """Fully paid single cash-flow claim held to payment, not futures margin return."""
    finite(price_paid, dividend_cash)
    if price_paid <= 0 or dividend_cash < 0:
        raise ValueError("invalid strip price or cash")
    return dividend_cash / price_paid - 1


def excess_bond_premium(observed_spread_bp, fitted_spread_bp):
    """One residual in basis points, not the full GZ estimation procedure."""
    finite(observed_spread_bp, fitted_spread_bp)
    return observed_spread_bp - fitted_spread_bp


class Tests(unittest.TestCase):
    def test_ipo_relative(self): self.assertAlmostEqual(relative_wealth(.3447,.6186),-.16922031385)
    def test_ipo_zero(self): self.assertEqual(relative_wealth(.1,.1),0)
    def test_ipo_loss(self): self.assertEqual(relative_wealth(-1,0),-1)
    def test_ipo_invalid(self):
        with self.assertRaises(ValueError): relative_wealth(.1,-1)
    def test_spin_value(self): self.assertAlmostEqual(spinoff_shareholder_return(80,40,.5,0,100),0)
    def test_spin_cash(self): self.assertAlmostEqual(spinoff_shareholder_return(80,40,.5,5,100),.05)
    def test_spin_zero_child(self): self.assertAlmostEqual(spinoff_shareholder_return(80,0,.5,0,100),-.2)
    def test_spin_invalid(self):
        with self.assertRaises(ValueError): spinoff_shareholder_return(80,40,-.5,0,100)
    def test_pressure_buy(self): self.assertAlmostEqual(index_rebalance_pressure(.12,.1,1e9,1e8),.2)
    def test_pressure_sell(self): self.assertAlmostEqual(index_rebalance_pressure(.1,.12,1e9,1e8),-.2)
    def test_pressure_zero(self): self.assertEqual(index_rebalance_pressure(.1,.1,1e9,1e8),0)
    def test_pressure_invalid(self):
        with self.assertRaises(ValueError): index_rebalance_pressure(.1,.2,1e9,0)
    def test_strip_gain(self): self.assertAlmostEqual(dividend_strip_return(95,100),100/95-1)
    def test_strip_loss(self): self.assertAlmostEqual(dividend_strip_return(100,80),-.2)
    def test_strip_zero_cash(self): self.assertEqual(dividend_strip_return(100,0),-1)
    def test_strip_invalid(self):
        with self.assertRaises(ValueError): dividend_strip_return(0,100)
    def test_ebp_positive(self): self.assertEqual(excess_bond_premium(180,120),60)
    def test_ebp_negative(self): self.assertEqual(excess_bond_premium(90,120),-30)
    def test_ebp_zero(self): self.assertEqual(excess_bond_premium(120,120),0)
    def test_nonfinite(self):
        for fn,args in [(relative_wealth,(math.nan,0)),(spinoff_shareholder_return,(80,40,.5,0,math.inf)),(index_rebalance_pressure,(.1,.2,math.inf,10)),(dividend_strip_return,(math.nan,100)),(excess_bond_premium,(math.inf,0))]:
            with self.subTest(fn=fn.__name__), self.assertRaises(ValueError): fn(*args)


if __name__ == "__main__":
    unittest.main(verbosity=2)
