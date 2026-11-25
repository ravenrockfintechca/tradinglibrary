"""QSI-156..160: research primitives only; no market data or execution."""
import math
import unittest


def finite(x):
    if not math.isfinite(x):
        raise ValueError('nonfinite input')
    return x


def cashflow_duration(years, present_values):
    if not years or len(years) != len(present_values):
        raise ValueError('invalid cashflow vectors')
    if any(finite(t) < 0 for t in years) or any(finite(v) < 0 for v in present_values):
        raise ValueError('requires nonnegative times and PVs')
    total = sum(present_values)
    if total <= 0:
        raise ValueError('positive PV required')
    return sum(t*v for t, v in zip(years, present_values))/total


def pension_underfunding(assets, obligation, market_cap):
    if finite(assets) < 0 or finite(obligation) < 0 or finite(market_cap) <= 0:
        raise ValueError('invalid pension inputs')
    return (obligation-assets)/market_cap


def cpr_from_smm(smm):
    if not 0 <= finite(smm) <= 1:
        raise ValueError('SMM outside [0,1]')
    return 1-(1-smm)**12


def strike_distance(price, strike):
    if finite(price) <= 0 or finite(strike) <= 0:
        raise ValueError('positive prices required')
    return (price-strike)/strike


def cape(real_price, real_annual_earnings):
    if finite(real_price) <= 0 or len(real_annual_earnings) != 120:
        raise ValueError('positive price and 120 monthly observations required')
    avg = sum(finite(e) for e in real_annual_earnings)/120
    if avg <= 0:
        raise ValueError('positive average earnings required')
    return real_price/avg


class Tests(unittest.TestCase):
    def test_01_duration(self): self.assertAlmostEqual(cashflow_duration([1,3],[25,75]),2.5)
    def test_02_duration_single(self): self.assertEqual(cashflow_duration([5],[10]),5)
    def test_03_duration_shape(self): self.assertRaises(ValueError,cashflow_duration,[1],[1,2])
    def test_04_duration_zero(self): self.assertRaises(ValueError,cashflow_duration,[1],[0])
    def test_05_pension(self): self.assertAlmostEqual(pension_underfunding(80,100,200),.1)
    def test_06_surplus(self): self.assertAlmostEqual(pension_underfunding(120,100,200),-.1)
    def test_07_pension_cap(self): self.assertRaises(ValueError,pension_underfunding,80,100,0)
    def test_08_pension_nan(self): self.assertRaises(ValueError,pension_underfunding,float('nan'),100,200)
    def test_09_cpr(self): self.assertAlmostEqual(cpr_from_smm(.01),.11361512828387077)
    def test_10_cpr_zero(self): self.assertEqual(cpr_from_smm(0),0)
    def test_11_cpr_one(self): self.assertEqual(cpr_from_smm(1),1)
    def test_12_cpr_invalid(self): self.assertRaises(ValueError,cpr_from_smm,1.1)
    def test_13_strike(self): self.assertAlmostEqual(strike_distance(102,100),.02)
    def test_14_strike_below(self): self.assertAlmostEqual(strike_distance(98,100),-.02)
    def test_15_strike_zero(self): self.assertRaises(ValueError,strike_distance,100,0)
    def test_16_strike_inf(self): self.assertRaises(ValueError,strike_distance,float('inf'),100)
    def test_17_cape(self): self.assertEqual(cape(100,[5]*120),20)
    def test_18_cape_loss_month(self): self.assertAlmostEqual(cape(100,[-5]+[5]*119),100/(590/120))
    def test_19_cape_length(self): self.assertRaises(ValueError,cape,100,[5]*119)
    def test_20_cape_zero(self): self.assertRaises(ValueError,cape,100,[0]*120)


if __name__ == '__main__':
    unittest.main(verbosity=2)
