"""ZTrader QSI-121..125, 2026-11-18. Research-only signal primitives.

No EDGAR, 13F, market-data downloading, execution, backtest or performance claim.
All inputs must be from an as-of-publication timestamped point-in-time dataset.
"""
from __future__ import annotations

import math
import unittest
from collections.abc import Mapping


def _finite(name: str, value: float) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean")
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return v


def _nonnegative(name: str, value: float) -> float:
    v = _finite(name, value)
    if v < 0:
        raise ValueError(f"{name} must be nonnegative")
    return v


def _positive(name: str, value: float) -> float:
    v = _finite(name, value)
    if v <= 0:
        raise ValueError(f"{name} must be positive")
    return v


def insider_cluster_buying_intensity(purchases_usd: float, market_cap_usd: float, distinct_buyers: int) -> float:
    """QSI-121: open-market Form 4 'P' purchases over a fixed disclosed window.

    Research proxy: purchase value / market cap * sqrt(unique buying insiders).
    Does not score sales, option exercise, or trades not yet publicly filed.
    """
    amount = _nonnegative("purchases_usd", purchases_usd)
    cap = _positive("market_cap_usd", market_cap_usd)
    if isinstance(distinct_buyers, bool) or not isinstance(distinct_buyers, int) or distinct_buyers < 0:
        raise ValueError("distinct_buyers must be a nonnegative integer")
    if (amount > 0) != (distinct_buyers > 0):
        raise ValueError("purchase amount and buyer count must both be zero or both positive")
    return amount / cap * math.sqrt(distinct_buyers)


def ownership_breadth_delta(current_holders: int, previous_holders: int,
                            current_reporting_managers: int, previous_reporting_managers: int) -> float:
    """QSI-122: change in fraction of *observable/publicly reported* 13F managers owning the stock.

    Not valid before each filing is publicly available. Not identical to the full paper estimator.
    """
    vals = [current_holders, previous_holders, current_reporting_managers, previous_reporting_managers]
    if any(isinstance(v, bool) or not isinstance(v, int) for v in vals):
        raise ValueError("all holder/manager counts must be integers")
    if min(vals) < 0 or current_reporting_managers == 0 or previous_reporting_managers == 0:
        raise ValueError("manager denominators must be positive, holders nonnegative")
    if current_holders > current_reporting_managers or previous_holders > previous_reporting_managers:
        raise ValueError("holder count cannot exceed reporting manager count")
    return current_holders / current_reporting_managers - previous_holders / previous_reporting_managers


_FSCORE_KEYS = ("net_income", "operating_cash_flow", "total_assets", "long_term_debt",
                "current_assets", "current_liabilities", "shares_outstanding",
                "gross_profit", "revenue")


def piotroski_f_score(current: Mapping[str, float], previous: Mapping[str, float]) -> int:
    """QSI-123: nine binary accounting signs; use only after source filings are public.

    Proxy requires aligned annual statements and comparable share counts; no universe selection.
    Stocks must also be screened into a contemporaneous high-book-to-market universe.
    """
    c = {k: _finite("current." + k, current[k]) for k in _FSCORE_KEYS}
    p = {k: _finite("previous." + k, previous[k]) for k in _FSCORE_KEYS}
    for label, d in (("current", c), ("previous", p)):
        for key in ("total_assets", "current_liabilities", "revenue"):
            if d[key] <= 0:
                raise ValueError(f"{label}.{key} must be positive")
        if d["shares_outstanding"] <= 0:
            raise ValueError(f"{label}.shares_outstanding must be positive")
    roa = c["net_income"] / c["total_assets"]
    old_roa = p["net_income"] / p["total_assets"]
    return sum((
        roa > 0,
        c["operating_cash_flow"] > 0,
        roa > old_roa,
        c["operating_cash_flow"] > c["net_income"],
        c["long_term_debt"] / c["total_assets"] < p["long_term_debt"] / p["total_assets"],
        c["current_assets"] / c["current_liabilities"] > p["current_assets"] / p["current_liabilities"],
        c["shares_outstanding"] <= p["shares_outstanding"],
        c["gross_profit"] / c["revenue"] > p["gross_profit"] / p["revenue"],
        c["revenue"] / c["total_assets"] > p["revenue"] / p["total_assets"],
    ))


def activist_13d_objective_flag(is_public: bool, confirmed_activist: bool,
                                objective: str) -> int:
    """QSI-124: research-only categorical Item 4 event flag, after public 13D acceptance.

    2=sale/spinoff objective, 1=operating-strategy objective, 0=other or not observable.
    Values are NOT calibrated probabilities or expected returns.
    """
    if not isinstance(is_public, bool) or not isinstance(confirmed_activist, bool):
        raise ValueError("publication and activism flags must be booleans")
    if not is_public or not confirmed_activist:
        return 0
    if objective == "sale_or_spinoff":
        return 2
    if objective == "business_strategy":
        return 1
    if objective in ("governance_only", "capital_structure_only", "other"):
        return 0
    raise ValueError("unknown Item 4 objective; classify manually rather than guessing")


def treasury_liquidity_convergence_proxy(
    old_yield_pct_entry: float, new_yield_pct_entry: float,
    old_yield_pct_exit: float, new_yield_pct_exit: float,
    repo_carry_dv01_equiv_bp: float, roundtrip_cost_dv01_equiv_bp: float,
) -> float:
    """QSI-125: yield-spread convergence minus financed carry, in DV01-equivalent bp.

    Positive off-run minus on-run yield spread may narrow. NOT total return or P&L.
    Requires maturity/DV01 matched bonds, repo specialness and hedge execution.
    """
    iy = _finite("old_yield_pct_entry", old_yield_pct_entry) - _finite("new_yield_pct_entry", new_yield_pct_entry)
    fy = _finite("old_yield_pct_exit", old_yield_pct_exit) - _finite("new_yield_pct_exit", new_yield_pct_exit)
    carry = _nonnegative("repo_carry_dv01_equiv_bp", repo_carry_dv01_equiv_bp)
    fee = _nonnegative("roundtrip_cost_dv01_equiv_bp", roundtrip_cost_dv01_equiv_bp)
    return 100.0 * (iy - fy) - carry - fee


class SyntheticTests(unittest.TestCase):
    def setUp(self):
        self.p = {"net_income": 5, "operating_cash_flow": 4, "total_assets": 100,
                  "long_term_debt": 35, "current_assets": 30, "current_liabilities": 20,
                  "shares_outstanding": 10, "gross_profit": 20, "revenue": 100}
        self.c = {"net_income": 12, "operating_cash_flow": 16, "total_assets": 110,
                  "long_term_debt": 30, "current_assets": 42, "current_liabilities": 20,
                  "shares_outstanding": 10, "gross_profit": 29, "revenue": 120}

    def test_insider_cluster(self):
        self.assertAlmostEqual(insider_cluster_buying_intensity(200_000, 100_000_000, 4), .004)

    def test_insider_empty(self):
        self.assertEqual(insider_cluster_buying_intensity(0, 1e8, 0), 0)

    def test_insider_reject_inconsistent(self):
        with self.assertRaises(ValueError):
            insider_cluster_buying_intensity(100, 1e8, 0)

    def test_insider_reject_zero_cap(self):
        with self.assertRaises(ValueError):
            insider_cluster_buying_intensity(100, 0, 1)

    def test_breadth_change(self):
        self.assertAlmostEqual(ownership_breadth_delta(60, 45, 100, 100), .15)

    def test_breadth_changing_denominator(self):
        self.assertAlmostEqual(ownership_breadth_delta(60, 45, 120, 100), .05)

    def test_breadth_invalid(self):
        with self.assertRaises(ValueError):
            ownership_breadth_delta(200, 45, 100, 100)

    def test_fscore_nine(self):
        self.assertEqual(piotroski_f_score(self.c, self.p), 9)

    def test_fscore_zero(self):
        poor = {**self.p, "net_income": -10, "operating_cash_flow": -20, "total_assets": 120,
                "long_term_debt": 90, "current_assets": 10, "current_liabilities": 30,
                "shares_outstanding": 15, "gross_profit": 10, "revenue": 60}
        self.assertEqual(piotroski_f_score(poor, self.p), 0)

    def test_fscore_bad_assets(self):
        with self.assertRaises(ValueError):
            piotroski_f_score({**self.c, "total_assets": 0}, self.p)

    def test_activist_nonpublic(self):
        self.assertEqual(activist_13d_objective_flag(False, True, "sale_or_spinoff"), 0)

    def test_activist_flag(self):
        self.assertEqual(activist_13d_objective_flag(True, True, "business_strategy"), 1)
        self.assertEqual(activist_13d_objective_flag(True, True, "sale_or_spinoff"), 2)

    def test_activist_reject_unknown(self):
        with self.assertRaises(ValueError):
            activist_13d_objective_flag(True, True, "unclassified")

    def test_treasury_convergence(self):
        # Entry spread 10bp, exit spread 6bp, carry 3bp and execution 2bp -> -1bp.
        self.assertAlmostEqual(treasury_liquidity_convergence_proxy(4.10, 4.00, 4.06, 4.00, 3, 2), -1)

    def test_treasury_reject_negative_cost(self):
        with self.assertRaises(ValueError):
            treasury_liquidity_convergence_proxy(4.10, 4, 4.06, 4, -1, 1)

    def test_reject_nan(self):
        with self.assertRaises(ValueError):
            insider_cluster_buying_intensity(float("nan"), 1e8, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
