"""QSI-166..170 research primitives; synthetic tests, no market backtest."""
import math
import unittest


def finite(*xs):
    if not all(math.isfinite(x) for x in xs):
        raise ValueError('non-finite input')


def restricted_revenue_share(restricted, total):
    finite(restricted, total)
    if total <= 0 or not 0 <= restricted <= total:
        raise ValueError('invalid revenue')
    return restricted / total


def local_ownership_share(local_shares, outstanding):
    finite(local_shares, outstanding)
    if outstanding <= 0 or not 0 <= local_shares <= outstanding:
        raise ValueError('invalid shares')
    return local_shares / outstanding


def voting_class_premium(high_price, low_price, high_rights=1, low_rights=1):
    finite(high_price, low_price, high_rights, low_rights)
    if min(high_price, low_price, high_rights, low_rights) <= 0:
        raise ValueError('nonpositive price or cashflow entitlement')
    return (high_price / high_rights) / (low_price / low_rights) - 1


def muni_after_tax_gap(muni_yield, taxable_yield, tax_rate):
    finite(muni_yield, taxable_yield, tax_rate)
    if not 0 <= tax_rate < 1:
        raise ValueError('invalid tax rate')
    return muni_yield - taxable_yield * (1 - tax_rate)


def volume_percentile(current, history):
    history = tuple(history)
    finite(current, *history)
    if not history or current < 0 or min(history) < 0:
        raise ValueError('invalid volume history')
    return (sum(v < current for v in history) + 0.5 * sum(v == current for v in history)) / len(history)


class TestPrimitives(unittest.TestCase):
    def test_restricted_normal(self): self.assertAlmostEqual(restricted_revenue_share(30, 100), .3)
    def test_restricted_zero(self): self.assertEqual(restricted_revenue_share(0, 100), 0)
    def test_restricted_invalid(self): self.assertRaises(ValueError, restricted_revenue_share, 101, 100)
    def test_restricted_nan(self): self.assertRaises(ValueError, restricted_revenue_share, math.nan, 100)
    def test_local_normal(self): self.assertAlmostEqual(local_ownership_share(12, 100), .12)
    def test_local_full(self): self.assertEqual(local_ownership_share(100, 100), 1)
    def test_local_zero_denominator(self): self.assertRaises(ValueError, local_ownership_share, 0, 0)
    def test_local_negative(self): self.assertRaises(ValueError, local_ownership_share, -1, 100)
    def test_vote_normal(self): self.assertAlmostEqual(voting_class_premium(110, 100), .1)
    def test_vote_entitlement(self): self.assertEqual(voting_class_premium(200, 100, 2, 1), 0)
    def test_vote_negative_premium(self): self.assertAlmostEqual(voting_class_premium(90, 100), -.1)
    def test_vote_zero(self): self.assertRaises(ValueError, voting_class_premium, 10, 0)
    def test_muni_normal(self): self.assertAlmostEqual(muni_after_tax_gap(.035, .05, .30), 0)
    def test_muni_negative(self): self.assertAlmostEqual(muni_after_tax_gap(.03, .05, .20), -.01)
    def test_muni_zero_tax(self): self.assertAlmostEqual(muni_after_tax_gap(.04, .05, 0), -.01)
    def test_muni_invalid(self): self.assertRaises(ValueError, muni_after_tax_gap, .04, .05, 1)
    def test_volume_top(self): self.assertEqual(volume_percentile(5, [1, 2, 3]), 1)
    def test_volume_tie(self): self.assertEqual(volume_percentile(2, [1, 2, 2, 3]), .5)
    def test_volume_empty(self): self.assertRaises(ValueError, volume_percentile, 1, [])
    def test_volume_negative(self): self.assertRaises(ValueError, volume_percentile, 1, [-1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
