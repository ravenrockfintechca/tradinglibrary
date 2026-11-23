"""ZTrader QSI-146..150: five research *primitives*, not trading strategies.

Synthetic tests only. No historical market data or broker connectivity.
Paper claims and DOI are documented in qsi/daily/2026-11-23.md.
"""
from __future__ import annotations

import math
import unittest


def _real(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name}: finite number required")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name}: finite number required")
    return value


def friday_earnings_attention_signal(earnings_surprise: float, weekday: int, is_public: bool) -> int:
    """Proxy for QSI-146: signed surprise on Fri=4 after publication only.

    It is not the DellaVigna-Pollet portfolio, nor evidence of positive net returns.
    Weekdays follow datetime.weekday(): Monday=0, Friday=4.
    """
    s = _real(earnings_surprise, "earnings_surprise")
    if isinstance(weekday, bool) or not isinstance(weekday, int) or not 0 <= weekday <= 4:
        raise ValueError("weekday must be integer 0..4")
    if not isinstance(is_public, bool):
        raise ValueError("is_public must be bool")
    return (1 if s > 0 else -1 if s < 0 else 0) if weekday == 4 and is_public else 0


def etf_ownership_fraction(etf_held_shares: float, shares_outstanding: float) -> float:
    """QSI-147: ETF-held shares / company shares. NOT future volatility alpha."""
    held, total = _real(etf_held_shares, "etf_held_shares"), _real(shares_outstanding, "shares_outstanding")
    if total <= 0 or held < 0 or held > total:
        raise ValueError("shares must satisfy 0<=ETF-held<=outstanding and outstanding>0")
    return held / total


def analyst_recommendation_revision(previous: int, current: int) -> int:
    """QSI-148: signed change on 1=Strong Buy to 5=Strong Sell scale."""
    for rating in (previous, current):
        if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError("rating must be integer 1..5")
    return (1 if current < previous else -1 if current > previous else 0)


def treasury_auction_price_pattern(pre_auction: float, auction_window: float, post_auction: float) -> tuple[float, float]:
    """QSI-149: preauction concession and postauction rebound in price basis points.

    Positive preauction result denotes falling price going into auction.
    No DV01/financing/total-return adjustment; prices must be clean/consistent.
    """
    p, a, q = (_real(x, n) for x, n in [(pre_auction, "pre_auction"),
                                         (auction_window, "auction_window"),
                                         (post_auction, "post_auction")])
    if min(p, a, q) <= 0:
        raise ValueError("all prices must be positive")
    return (10_000 * (p - a) / p, 10_000 * (q - a) / a)


def cds_bond_basis_bp(cds_spread_bp: float, matched_bond_spread_bp: float) -> float:
    """QSI-150: CDS spread minus matched bond credit spread, in basis points.

    Credit spread must already be curve/seniority/maturity-adjusted externally.
    This raw basis is NOT an executable arbitrage profit.
    """
    return _real(cds_spread_bp, "cds_spread_bp") - _real(matched_bond_spread_bp, "matched_bond_spread_bp")


class SyntheticTests(unittest.TestCase):
    def test_146_positive_friday(self):
        self.assertEqual(friday_earnings_attention_signal(.03, 4, True), 1)

    def test_146_negative_friday(self):
        self.assertEqual(friday_earnings_attention_signal(-.03, 4, True), -1)

    def test_146_not_public(self):
        self.assertEqual(friday_earnings_attention_signal(.03, 4, False), 0)

    def test_146_invalid_weekday(self):
        with self.assertRaises(ValueError):
            friday_earnings_attention_signal(.01, 5, True)

    def test_147_ratio(self):
        self.assertAlmostEqual(etf_ownership_fraction(2, 10), .2)

    def test_147_zero(self):
        self.assertEqual(etf_ownership_fraction(0, 10), 0.)

    def test_147_invalid_total(self):
        with self.assertRaises(ValueError):
            etf_ownership_fraction(1, 0)

    def test_147_invalid_owned(self):
        with self.assertRaises(ValueError):
            etf_ownership_fraction(11, 10)

    def test_148_upgrade(self):
        self.assertEqual(analyst_recommendation_revision(3, 1), 1)

    def test_148_downgrade(self):
        self.assertEqual(analyst_recommendation_revision(2, 4), -1)

    def test_148_hold(self):
        self.assertEqual(analyst_recommendation_revision(3, 3), 0)

    def test_148_invalid_rating(self):
        with self.assertRaises(ValueError):
            analyst_recommendation_revision(0, 3)

    def test_149_pattern(self):
        fall, rebound = treasury_auction_price_pattern(100, 99, 100)
        self.assertAlmostEqual(fall, 100)
        self.assertAlmostEqual(rebound, 10000 / 99)

    def test_149_no_change(self):
        self.assertEqual(treasury_auction_price_pattern(100, 100, 100), (0., 0.))

    def test_149_negative_concession(self):
        self.assertLess(treasury_auction_price_pattern(99, 100, 101)[0], 0)

    def test_149_zero_price(self):
        with self.assertRaises(ValueError):
            treasury_auction_price_pattern(0, 100, 101)

    def test_150_positive(self):
        self.assertEqual(cds_bond_basis_bp(150, 120), 30)

    def test_150_negative(self):
        self.assertEqual(cds_bond_basis_bp(100, 140), -40)

    def test_150_zero(self):
        self.assertEqual(cds_bond_basis_bp(75, 75), 0)

    def test_150_nonfinite(self):
        with self.assertRaises(ValueError):
            cds_bond_basis_bp(float("nan"), 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
