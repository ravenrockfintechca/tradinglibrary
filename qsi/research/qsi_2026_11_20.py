"""QSI-131..135 independent research primitives, 2026-11-20.

Deterministic arithmetic only, not the cited papers' full replication.
No data downloads, broker access, orders or backtest claims.
Units: all returns and fees are decimal fractions; forwards are annual rates
in the same unit; short quantities are shares in the same observation window.
"""
from __future__ import annotations

import math
import unittest
from collections.abc import Sequence


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def informed_short_sale_fraction(short_shares: float, total_shares: float) -> float:
    """Share of observed traded volume classified as short sales.

    Public aggregate short-sale volume is NOT institutional nonprogram
    proprietary NYSE flow and cannot replicate Boehmer-Jones-Zhang (2008).
    """
    short = _finite(short_shares, "short_shares")
    total = _finite(total_shares, "total_shares")
    if total <= 0 or short < 0 or short > total:
        raise ValueError("require 0 <= short_shares <= total_shares and total_shares > 0")
    return short / total


def employee_hiring_rate(employees_now: float, employees_prior: float) -> float:
    """Year-over-year headcount growth; not a calibrated labor risk premium."""
    now = _finite(employees_now, "employees_now")
    prior = _finite(employees_prior, "employees_prior")
    if now < 0 or prior <= 0:
        raise ValueError("require employees_now >= 0 and employees_prior > 0")
    return now / prior - 1.0


def corporate_bond_formation_return(monthly_total_returns: Sequence[float]) -> float:
    """Compounded historical bond TOTAL return over explicitly supplied months.

    Caller must supply coupon-inclusive, non-stale, comparable bond returns,
    strictly before formation date; this routine does not choose lookback.
    """
    if isinstance(monthly_total_returns, (str, bytes)) or not monthly_total_returns:
        raise ValueError("nonempty monthly_total_returns required")
    gross = 1.0
    for r in monthly_total_returns:
        rr = _finite(r, "monthly_return")
        if rr <= -1:
            raise ValueError("monthly total return must exceed -100%")
        gross *= 1.0 + rr
    return gross - 1.0


def treasury_forward_rate_score(forward_rates: Sequence[float], trained_weights: Sequence[float]) -> float:
    """Linear forward-rate factor score using caller-supplied PIT-trained weights.

    The weights are NOT Cochrane-Piazzesi published coefficients; estimate
    weights on a strictly earlier training sample, evaluate out of sample.
    """
    if isinstance(forward_rates, (str, bytes)) or isinstance(trained_weights, (str, bytes)):
        raise TypeError("forward_rates and trained_weights must be numeric sequences")
    if not forward_rates or len(forward_rates) != len(trained_weights):
        raise ValueError("forward_rates and trained_weights must have equal nonzero length")
    return sum(_finite(rate, "forward_rate") * _finite(weight, "trained_weight")
               for rate, weight in zip(forward_rates, trained_weights))


def mutual_fund_return_gap(reported_return: float, disclosed_holdings_return: float,
                           monthly_expense_fraction: float) -> float:
    """Reported net fund return minus stale-disclosed-holdings net proxy.

    Gap = R_reported - (R_stale_holdings - monthly_expense_fraction).
    Fund returns must share the same calendar month and total-return basis.
    """
    actual = _finite(reported_return, "reported_return")
    proxy = _finite(disclosed_holdings_return, "disclosed_holdings_return")
    fee = _finite(monthly_expense_fraction, "monthly_expense_fraction")
    if fee < 0 or fee >= 1:
        raise ValueError("monthly expense fraction must be in [0,1)")
    return actual - (proxy - fee)


class ResearchPrimitiveTests(unittest.TestCase):
    def test_short_normal(self):
        self.assertAlmostEqual(informed_short_sale_fraction(12.9, 100), .129)

    def test_short_zero(self):
        self.assertEqual(informed_short_sale_fraction(0, 10), 0)

    def test_short_invalid(self):
        with self.assertRaises(ValueError): informed_short_sale_fraction(11, 10)

    def test_short_nonfinite(self):
        with self.assertRaises(ValueError): informed_short_sale_fraction(math.nan, 10)

    def test_hiring_up(self):
        self.assertAlmostEqual(employee_hiring_rate(110, 100), .1)

    def test_hiring_down(self):
        self.assertAlmostEqual(employee_hiring_rate(90, 100), -.1)

    def test_hiring_invalid(self):
        with self.assertRaises(ValueError): employee_hiring_rate(1, 0)

    def test_hiring_nonfinite(self):
        with self.assertRaises(ValueError): employee_hiring_rate(math.inf, 10)

    def test_bond_compound(self):
        self.assertAlmostEqual(corporate_bond_formation_return([.1, -.1]), -.01)

    def test_bond_zero(self):
        self.assertEqual(corporate_bond_formation_return([0, 0]), 0)

    def test_bond_empty(self):
        with self.assertRaises(ValueError): corporate_bond_formation_return([])

    def test_bond_invalid(self):
        with self.assertRaises(ValueError): corporate_bond_formation_return([-.999, -1])

    def test_forward_score(self):
        self.assertAlmostEqual(treasury_forward_rate_score([.01,.02,.03], [1, -1, .5]), .005)

    def test_forward_signed(self):
        self.assertAlmostEqual(treasury_forward_rate_score([.03], [-2]), -.06)

    def test_forward_lengths(self):
        with self.assertRaises(ValueError): treasury_forward_rate_score([1], [1,2])

    def test_forward_nonfinite(self):
        with self.assertRaises(ValueError): treasury_forward_rate_score([math.nan], [1])

    def test_gap_positive(self):
        self.assertAlmostEqual(mutual_fund_return_gap(.03, .02, .001), .011)

    def test_gap_negative(self):
        self.assertAlmostEqual(mutual_fund_return_gap(-.02, -.01, .002), -.008)

    def test_gap_invalid_expense(self):
        with self.assertRaises(ValueError): mutual_fund_return_gap(.02, .01, -0.01)

    def test_gap_nonfinite(self):
        with self.assertRaises(ValueError): mutual_fund_return_gap(math.inf, .01, .001)


if __name__ == "__main__":
    unittest.main(verbosity=2)
