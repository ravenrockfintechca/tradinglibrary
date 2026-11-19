"""QSI-126..130 research primitives (2026-11-19).

No pricing feeds, live orders, backtest or paper replication. Stdlib only.
The distress function requires externally FIT and time-stamped coefficients.
The CDS residual requires an EXTERNALLY calibrated model CDS spread.
"""
from __future__ import annotations

import math
import unittest
from collections.abc import Mapping, Sequence


def _finite(value: float) -> float:
    if isinstance(value, bool):
        raise ValueError("Boolean is not a market numeric value")
    try:
        v = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("Expected finite numeric value") from exc
    if not math.isfinite(v):
        raise ValueError("Non-finite data are forbidden")
    return v


def distress_logit_probability(features: Mapping[str, float], coefficients: Mapping[str, float], intercept: float = 0.0) -> float:
    """Stable logistic mapping; not a fitted Campbell-Hilscher-Szilagyi model."""
    if not features or set(features) != set(coefficients):
        raise ValueError("Feature/parameter names must match and be nonempty")
    z = _finite(intercept)
    for key in features:
        z += _finite(features[key]) * _finite(coefficients[key])
    return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))


def industry_sales_hhi(firm_sales: Sequence[float]) -> float:
    """HHI in [0,1]; define industry and time-eligible constituents upstream."""
    sales = [_finite(s) for s in firm_sales]
    if not sales or any(s < 0 for s in sales) or sum(sales) <= 0:
        raise ValueError("Need nonnegative sales and a positive industry total")
    total = sum(sales)
    return sum((s / total) ** 2 for s in sales)


def credit_rating_transition(old_rating: str, new_rating: str, ranks: Mapping[str, int]) -> int:
    """-1 downgrade; +1 upgrade; 0 unchanged. Smaller rank = safer."""
    if old_rating not in ranks or new_rating not in ranks:
        raise ValueError("Rating missing from one consistent historical ladder")
    old = _finite(ranks[old_rating])
    new = _finite(ranks[new_rating])
    return -1 if new > old else (1 if new < old else 0)


def fund_active_share(fund: Mapping[str, float], benchmark: Mapping[str, float]) -> float:
    """One half of the absolute holdings-weight deviation from a benchmark."""
    if not fund or not benchmark:
        raise ValueError("Both portfolios must be nonempty")
    for portfolio in (fund, benchmark):
        weights = [_finite(w) for w in portfolio.values()]
        if any(w < 0 for w in weights) or abs(sum(weights) - 1) > 1e-6:
            raise ValueError("Long-only holdings weights must sum to one")
    return 0.5 * sum(abs(_finite(fund.get(k, 0)) - _finite(benchmark.get(k, 0))) for k in set(fund) | set(benchmark))


def cds_equity_spread_residual(market_cds_bp: float, equity_model_cds_bp: float) -> float:
    """Market minus independently model-implied CDS spread in basis points."""
    market, model = _finite(market_cds_bp), _finite(equity_model_cds_bp)
    if market < 0 or model < 0:
        raise ValueError("Spreads must be nonnegative in this simplified primitive")
    return market - model


class ResearchPrimitiveTests(unittest.TestCase):
    def test_distress_probability_center(self):
        self.assertAlmostEqual(distress_logit_probability({"leverage": 0}, {"leverage": 2}), 0.5)

    def test_distress_probability_positive(self):
        self.assertGreater(distress_logit_probability({"leverage": 2}, {"leverage": 1}), 0.5)

    def test_distress_probability_extreme(self):
        self.assertAlmostEqual(distress_logit_probability({"x": -1000}, {"x": 1}), 0.0)

    def test_distress_reject_mismatched_features(self):
        with self.assertRaises(ValueError):
            distress_logit_probability({"x": 1}, {"y": 1})

    def test_distress_reject_nonfinite(self):
        with self.assertRaises(ValueError):
            distress_logit_probability({"x": math.nan}, {"x": 1})

    def test_hhi_equal_competitors(self):
        self.assertAlmostEqual(industry_sales_hhi([50, 50]), 0.5)

    def test_hhi_monopoly(self):
        self.assertAlmostEqual(industry_sales_hhi([10]), 1.0)

    def test_hhi_reject_negative(self):
        with self.assertRaises(ValueError):
            industry_sales_hhi([5, -1])

    def test_hhi_reject_all_zero(self):
        with self.assertRaises(ValueError):
            industry_sales_hhi([0, 0])

    def test_rating_downgrade(self):
        self.assertEqual(credit_rating_transition("A", "BBB", {"A": 1, "BBB": 2}), -1)

    def test_rating_upgrade(self):
        self.assertEqual(credit_rating_transition("BBB", "A", {"A": 1, "BBB": 2}), 1)

    def test_rating_unchanged(self):
        self.assertEqual(credit_rating_transition("A", "A", {"A": 1}), 0)

    def test_rating_reject_unknown(self):
        with self.assertRaises(ValueError):
            credit_rating_transition("A", "ZZZ", {"A": 1})

    def test_active_share_identical(self):
        self.assertAlmostEqual(fund_active_share({"A": .6, "B": .4}, {"A": .6, "B": .4}), 0)

    def test_active_share_disjoint(self):
        self.assertAlmostEqual(fund_active_share({"A": 1}, {"B": 1}), 1)

    def test_active_share_partial(self):
        self.assertAlmostEqual(fund_active_share({"A": .8, "B": .2}, {"A": .5, "B": .5}), .3)

    def test_active_share_reject_bad_weights(self):
        with self.assertRaises(ValueError):
            fund_active_share({"A": .8}, {"A": 1})

    def test_cds_residual_positive(self):
        self.assertAlmostEqual(cds_equity_spread_residual(200, 150), 50)

    def test_cds_residual_negative(self):
        self.assertAlmostEqual(cds_equity_spread_residual(100, 120), -20)

    def test_cds_reject_negative(self):
        with self.assertRaises(ValueError):
            cds_equity_spread_residual(-10, 40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
