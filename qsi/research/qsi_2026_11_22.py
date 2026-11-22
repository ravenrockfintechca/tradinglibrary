"""QSI-141..145 research primitives (2026-11-22).

Pure, dependency-free math probes. No price download, orders, or paper replication.
The caller must supply point-in-time data that ended strictly before the trade.
"""
from __future__ import annotations

import math
import re


def _finite_number(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a numeric scalar")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def time_series_momentum_signal(prior_monthly_excess_returns: list[float]) -> int:
    """Sign of compounded PREVIOUS twelve monthly excess returns (QSI-141).

    Returns +1/0/-1. No volatility targeting, roll, financing or next-period fill.
    """
    if len(prior_monthly_excess_returns) != 12:
        raise ValueError("exactly 12 previous monthly returns are required")
    wealth = 1.0
    for i, value in enumerate(prior_monthly_excess_returns):
        r = _finite_number(value, f"return_{i}")
        if r <= -1.0:
            raise ValueError("simple monthly return must exceed -100%")
        wealth *= 1.0 + r
    if not math.isfinite(wealth):
        raise ValueError("compounded wealth overflow")
    return (wealth > 1.0) - (wealth < 1.0)


def inverse_variance_weight(
    lagged_returns: list[float], target_monthly_variance: float,
    max_leverage: float = 2.0,
) -> float:
    """Capped inverse lagged realized variance weight (QSI-142); not paper alpha."""
    if len(lagged_returns) < 3:
        raise ValueError("at least three previously observed returns required")
    vals = [_finite_number(v, "lagged_return") for v in lagged_returns]
    target = _finite_number(target_monthly_variance, "target_monthly_variance")
    cap = _finite_number(max_leverage, "max_leverage")
    if target <= 0 or cap <= 0:
        raise ValueError("target variance and cap must be positive")
    avg = sum(vals) / len(vals)
    var = sum((v - avg) ** 2 for v in vals) / len(vals)
    if not math.isfinite(var) or var <= 0:
        raise ValueError("lagged variance must be positive and finite")
    return min(cap, target / var)


def financial_news_negative_fraction(text: str, negative_vocabulary: set[str]) -> float:
    """Negative-word fraction in prior public firm news (QSI-143).

    Caller supplies an authorized, finance-specific dictionary and news vintage.
    Not a sentiment model, timestamp verifier, or full Tetlock replication.
    """
    if not isinstance(text, str) or not isinstance(negative_vocabulary, set):
        raise ValueError("text must be str and vocabulary must be a set")
    words = re.findall(r"[A-Za-z]+", text.casefold())
    if not words:
        raise ValueError("no alphabetic tokens")
    vocabulary = {w.casefold() for w in negative_vocabulary if isinstance(w, str)}
    if not vocabulary:
        raise ValueError("nonempty dictionary required")
    return sum(w in vocabulary for w in words) / len(words)


def fx_signed_flow_imbalance(buyer_initiated: float, seller_initiated: float) -> float:
    """Signed deal-currency order-flow ratio (QSI-144); NOT public FX volume."""
    buys = _finite_number(buyer_initiated, "buyer_initiated")
    sells = _finite_number(seller_initiated, "seller_initiated")
    if min(buys, sells) < 0 or buys + sells <= 0:
        raise ValueError("nonnegative volumes with positive gross volume required")
    return (buys - sells) / (buys + sells)


def broker_dealer_log_leverage_shock(
    current_assets: float, current_equity: float,
    prior_assets: float, prior_equity: float,
) -> float:
    """Proxy delta log(assets/equity) (QSI-145), NOT estimated SDF shock."""
    vals = [_finite_number(v, n) for n, v in (
        ("current_assets", current_assets), ("current_equity", current_equity),
        ("prior_assets", prior_assets), ("prior_equity", prior_equity),
    )]
    if any(v <= 0 for v in vals):
        raise ValueError("assets and equity must all be positive")
    a, e, pa, pe = vals
    return math.log(a / e) - math.log(pa / pe)


if __name__ == "__main__":
    import unittest

    class ResearchProbeTests(unittest.TestCase):
        def test_tsmom_positive(self):
            self.assertEqual(time_series_momentum_signal([0.01] * 12), 1)

        def test_tsmom_negative(self):
            self.assertEqual(time_series_momentum_signal([-0.01] * 12), -1)

        def test_tsmom_flat(self):
            self.assertEqual(time_series_momentum_signal([0.0] * 12), 0)

        def test_tsmom_wrong_window(self):
            with self.assertRaises(ValueError):
                time_series_momentum_signal([0.01] * 11)

        def test_tsmom_impossible_return(self):
            with self.assertRaises(ValueError):
                time_series_momentum_signal([-1.0] + [0.0] * 11)

        def test_var_weight_unit(self):
            self.assertAlmostEqual(inverse_variance_weight([0.1, -0.1, 0.1, -0.1], 0.01), 1.0)

        def test_var_weight_cap(self):
            self.assertAlmostEqual(inverse_variance_weight([0.1, -0.1, 0.1, -0.1], 0.1), 2.0)

        def test_var_zero_rejected(self):
            with self.assertRaises(ValueError):
                inverse_variance_weight([0.0, 0.0, 0.0], 0.01)

        def test_news_fraction(self):
            self.assertAlmostEqual(financial_news_negative_fraction("Loss eased but risk remains", {"loss", "risk"}), 0.4)

        def test_news_case(self):
            self.assertAlmostEqual(financial_news_negative_fraction("RISK risk", {"risk"}), 1.0)

        def test_news_no_tokens(self):
            with self.assertRaises(ValueError):
                financial_news_negative_fraction("123 !!!", {"loss"})

        def test_fx_positive(self):
            self.assertAlmostEqual(fx_signed_flow_imbalance(75, 25), 0.5)

        def test_fx_negative(self):
            self.assertAlmostEqual(fx_signed_flow_imbalance(25, 75), -0.5)

        def test_fx_zero_gross(self):
            with self.assertRaises(ValueError):
                fx_signed_flow_imbalance(0, 0)

        def test_fx_negative_volume(self):
            with self.assertRaises(ValueError):
                fx_signed_flow_imbalance(-1, 2)

        def test_dealer_flat(self):
            self.assertAlmostEqual(broker_dealer_log_leverage_shock(100, 10, 50, 5), 0.0)

        def test_dealer_increase(self):
            self.assertAlmostEqual(broker_dealer_log_leverage_shock(120, 10, 100, 10), math.log(1.2))

        def test_dealer_invalid(self):
            with self.assertRaises(ValueError):
                broker_dealer_log_leverage_shock(100, 0, 90, 9)

        def test_nonfinite(self):
            with self.assertRaises(ValueError):
                broker_dealer_log_leverage_shock(float("nan"), 10, 100, 10)

        def test_bool_rejected(self):
            with self.assertRaises(ValueError):
                fx_signed_flow_imbalance(True, 1)

    unittest.main(verbosity=2)
