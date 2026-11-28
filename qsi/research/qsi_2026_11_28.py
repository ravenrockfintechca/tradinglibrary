"""QSI 171-175: synthetic research primitives, not trading models."""
import math
import unittest


def finite(*values):
    if not all(math.isfinite(x) for x in values):
        raise ValueError('nonfinite input')


def cay_residual(consumption, wealth, income, intercept, beta_a, beta_y):
    finite(consumption, wealth, income, intercept, beta_a, beta_y)
    if min(consumption, wealth, income) <= 0:
        raise ValueError('levels must be positive')
    return math.log(consumption) - intercept - beta_a * math.log(wealth) - beta_y * math.log(income)


def commodity_skewness(returns):
    r = tuple(returns)
    finite(*r)
    if len(r) < 3:
        raise ValueError('at least three returns required')
    mean = math.fsum(r) / len(r)
    d = [x - mean for x in r]
    scale = max(map(abs, d))
    if scale == 0:
        raise ValueError('zero variance')
    z = [x / scale for x in d]
    m2 = math.fsum(x*x for x in z) / len(z)
    m3 = math.fsum(x*x*x for x in z) / len(z)
    return m3 / m2**1.5


def open_interest_growth(current, previous):
    finite(current, previous)
    if min(current, previous) <= 0:
        raise ValueError('positive matched open interest required')
    return math.log(current) - math.log(previous)


def fx_commodity_forecast(fx_log_changes, coefficients, intercept=0.0):
    x, b = tuple(fx_log_changes), tuple(coefficients)
    finite(*x, *b, intercept)
    if not x or len(x) != len(b):
        raise ValueError('nonempty aligned inputs required')
    result = intercept + math.fsum(a*c for a, c in zip(x, b))
    finite(result)
    return result


def disclosed_customer_hhi(shares):
    s = tuple(shares)
    finite(*s)
    if not s or min(s) < 0 or math.fsum(s) > 1:
        raise ValueError('invalid or missing disclosed revenue shares')
    return math.fsum(x*x for x in s)


class TestPrimitives(unittest.TestCase):
    def test_cay_identity(self): self.assertAlmostEqual(cay_residual(100,100,100,0,.4,.6),0)
    def test_cay_direction(self): self.assertGreater(cay_residual(110,100,100,0,.4,.6),0)
    def test_cay_zero(self): self.assertRaises(ValueError,cay_residual,0,100,100,0,.4,.6)
    def test_cay_nan(self): self.assertRaises(ValueError,cay_residual,100,100,100,0,float('nan'),.6)
    def test_skew_symmetric(self): self.assertAlmostEqual(commodity_skewness([-1,0,1]),0)
    def test_skew_negative(self): self.assertLess(commodity_skewness([-5,1,1,1]),0)
    def test_skew_constant(self): self.assertRaises(ValueError,commodity_skewness,[1,1,1])
    def test_skew_short(self): self.assertRaises(ValueError,commodity_skewness,[1,2])
    def test_oi_growth(self): self.assertAlmostEqual(open_interest_growth(120,100),math.log(1.2))
    def test_oi_flat(self): self.assertEqual(open_interest_growth(100,100),0)
    def test_oi_zero(self): self.assertRaises(ValueError,open_interest_growth,0,100)
    def test_oi_inf(self): self.assertRaises(ValueError,open_interest_growth,float('inf'),100)
    def test_fx_forecast(self): self.assertAlmostEqual(fx_commodity_forecast([.02,-.01],[.5,.2],.001),.009)
    def test_fx_empty(self): self.assertRaises(ValueError,fx_commodity_forecast,[],[])
    def test_fx_length(self): self.assertRaises(ValueError,fx_commodity_forecast,[.1],[.2,.3])
    def test_fx_nan(self): self.assertRaises(ValueError,fx_commodity_forecast,[float('nan')],[.2])
    def test_hhi_partial(self): self.assertAlmostEqual(disclosed_customer_hhi([.3,.2]),.13)
    def test_hhi_full(self): self.assertEqual(disclosed_customer_hhi([1]),1)
    def test_hhi_missing(self): self.assertRaises(ValueError,disclosed_customer_hhi,[])
    def test_hhi_invalid(self): self.assertRaises(ValueError,disclosed_customer_hhi,[.7,.4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
