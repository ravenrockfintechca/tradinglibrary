"""QSI-136..140: five research primitives, not full paper replications.

Dependencies: Python >=3.10, numpy >=1.24. All inputs must be point-in-time.
No trading, execution, feeds, or claimed backtested returns.
Run: python -m unittest -v qsi_2026_11_21.py
"""
from __future__ import annotations

import math
import unittest
from typing import Sequence

import numpy as np


def _finite_vector(values: Sequence[float], minimum: int) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size < minimum or not np.all(np.isfinite(arr)):
        raise ValueError("expected finite 1D vector with enough observations")
    return arr


def _r_squared(y: np.ndarray, x: np.ndarray) -> float:
    if y.ndim != 1 or x.ndim != 2 or x.shape[0] != y.size:
        raise ValueError("shape mismatch")
    centered = y - y.mean()
    total = float(centered @ centered)
    if total <= 1e-14:
        raise ValueError("zero target variance")
    fitted = x @ np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - fitted
    return float(1.0 - (residual @ residual) / total)


def market_price_delay(stock_returns: Sequence[float], market_returns: Sequence[float], lags: int = 4) -> float:
    """Hou-Moskowitz style 1 - R2(contemporaneous)/R2(contemporaneous+lagged).

    Demonstration only; the original paper adds richer controls and filtering.
    Returns NaN-free metric, not forecast or risk-adjusted alpha.
    """
    if not isinstance(lags, int) or isinstance(lags, bool) or lags < 1:
        raise ValueError("lags must be positive integer")
    stock = _finite_vector(stock_returns, lags + 8)
    market = _finite_vector(market_returns, lags + 8)
    if stock.size != market.size:
        raise ValueError("aligned equal-length returns required")
    n = stock.size
    target = stock[lags:]
    restricted = np.column_stack((np.ones(n - lags), market[lags:]))
    unrestricted = np.column_stack([np.ones(n - lags)] + [market[lags - j:n - j] for j in range(lags + 1)])
    r2_restricted = max(0.0, _r_squared(target, restricted))
    r2_unrestricted = _r_squared(target, unrestricted)
    if r2_unrestricted <= 1e-12:
        raise ValueError("unrestricted model has no explanatory power")
    return float(np.clip(1.0 - r2_restricted / r2_unrestricted, 0.0, 1.0))


def historical_earnings_volume_attention(prior_announcement_volumes: Sequence[float],
                                         prior_baseline_volumes: Sequence[float]) -> float:
    """Research ratio based ONLY on previously completed/known announcement windows."""
    announcement = _finite_vector(prior_announcement_volumes, 2)
    baseline = _finite_vector(prior_baseline_volumes, 2)
    if np.any(announcement < 0) or np.any(baseline <= 0):
        raise ValueError("invalid volume")
    return float(announcement.mean() / baseline.mean())


def intraday_opening_momentum(prior_close: float, first_half_hour_close: float) -> float:
    """First 30-minute market return measured from the PRIOR session close."""
    a, b = float(prior_close), float(first_half_hour_close)
    if not (math.isfinite(a) and math.isfinite(b) and a > 0 and b > 0):
        raise ValueError("positive finite prices required")
    return b / a - 1.0


def insurance_downgrade_sale_pressure(insurer_holding_fraction: float,
                                      constrained_insurer_fraction: float,
                                      crossed_to_speculative_grade: bool) -> float:
    """Heuristic exposure proxy, not trade-level NAIC regulatory sale prediction."""
    a, b = float(insurer_holding_fraction), float(constrained_insurer_fraction)
    if not (math.isfinite(a) and math.isfinite(b) and 0 <= a <= 1 and 0 <= b <= 1):
        raise ValueError("fractions must be finite in [0, 1]")
    if not isinstance(crossed_to_speculative_grade, bool):
        raise ValueError("crossing flag must be boolean")
    return a * b if crossed_to_speculative_grade else 0.0


def economic_uncertainty_beta(stock_returns: Sequence[float], uncertainty_innovations: Sequence[float]) -> float:
    """Cov(stock return, uncertainty innovation) / Var(uncertainty innovation).

    Caller must supply past-only innovations, not contemporaneous revised future values.
    """
    stock = _finite_vector(stock_returns, 3)
    shocks = _finite_vector(uncertainty_innovations, 3)
    if stock.size != shocks.size:
        raise ValueError("aligned equal-length observations required")
    x = shocks - shocks.mean()
    y = stock - stock.mean()
    denominator = float(x @ x)
    if denominator <= 1e-14:
        raise ValueError("zero uncertainty variance")
    return float((x @ y) / denominator)


class TestQSIResearchPrimitives(unittest.TestCase):
    def test_136_delayed_market_prices(self):
        rng = np.random.default_rng(136)
        market = rng.normal(size=220)
        stock = np.roll(market, 2) + rng.normal(0, 0.05, 220)
        self.assertGreater(market_price_delay(stock, market), 0.7)

    def test_136_contemporaneous_prices(self):
        rng = np.random.default_rng(1)
        market = rng.normal(size=220)
        self.assertLess(market_price_delay(market, market), 0.05)

    def test_136_bad_lags(self):
        with self.assertRaises(ValueError):
            market_price_delay(list(range(10)), list(range(10)), 0)

    def test_136_mismatched_length(self):
        with self.assertRaises(ValueError):
            market_price_delay(list(range(20)), list(range(21)))

    def test_137_ratio(self):
        self.assertAlmostEqual(historical_earnings_volume_attention([200, 400], [100, 100]), 3.0)

    def test_137_neutral(self):
        self.assertAlmostEqual(historical_earnings_volume_attention([100, 100], [100, 100]), 1.0)

    def test_137_zero_baseline(self):
        with self.assertRaises(ValueError):
            historical_earnings_volume_attention([100, 200], [0, 100])

    def test_137_nonfinite(self):
        with self.assertRaises(ValueError):
            historical_earnings_volume_attention([100, float("nan")], [100, 100])

    def test_138_up(self):
        self.assertAlmostEqual(intraday_opening_momentum(100, 101), 0.01)

    def test_138_down(self):
        self.assertAlmostEqual(intraday_opening_momentum(100, 99), -0.01)

    def test_138_invalid_price(self):
        with self.assertRaises(ValueError):
            intraday_opening_momentum(0, 101)

    def test_138_nonfinite(self):
        with self.assertRaises(ValueError):
            intraday_opening_momentum(100, float("inf"))

    def test_139_downgrade_pressure(self):
        self.assertAlmostEqual(insurance_downgrade_sale_pressure(0.4, 0.5, True), 0.2)

    def test_139_no_crossing(self):
        self.assertEqual(insurance_downgrade_sale_pressure(0.4, 0.5, False), 0.0)

    def test_139_invalid_share(self):
        with self.assertRaises(ValueError):
            insurance_downgrade_sale_pressure(1.2, 0.5, True)

    def test_139_invalid_flag(self):
        with self.assertRaises(ValueError):
            insurance_downgrade_sale_pressure(0.2, 0.4, 1)

    def test_140_negative_beta(self):
        self.assertAlmostEqual(economic_uncertainty_beta([-1, 0, 1], [1, 0, -1]), -1.0)

    def test_140_positive_beta(self):
        self.assertAlmostEqual(economic_uncertainty_beta([2, 4, 6], [1, 2, 3]), 2.0)

    def test_140_constant_uncertainty(self):
        with self.assertRaises(ValueError):
            economic_uncertainty_beta([1, 2, 3], [1, 1, 1])

    def test_140_invalid_length(self):
        with self.assertRaises(ValueError):
            economic_uncertainty_beta([1, 2, 3], [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
