import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from harbor.risk import tail,solve,evaluate,validate_quantity

class RiskTests(unittest.TestCase):
    def test_fractional_tail(self):
        self.assertAlmostEqual(tail(range(28))['cvar'],(27+26+.8*25)/2.8)
        self.assertEqual(tail(range(28))['var'],25)
    def test_negative_and_tied_tail(self):
        self.assertEqual(tail([-5]*28)['cvar'],-5)
        self.assertEqual(tail([1,1,1,1],.5)['cvar'],1)
        self.assertEqual(tail([1,2,3],0)['cvar'],2)
    def test_invalid_tail(self):
        for v,a in [([], .9),([float('nan')],.9),([1],1),([1],-.1)]:
            with self.assertRaises(ValueError):tail(v,a)
    def test_analytic_mean_schedule(self):
        S=np.tile(np.r_[np.ones(16)*10,np.ones(16)*100],(28,1))
        s=solve(S)
        np.testing.assert_allclose(s['quantity'][:16],.25)
        np.testing.assert_allclose(s['quantity'][16:],0)
        self.assertAlmostEqual(s['expected_cost'],42)
    def test_risk_budget_changes_toy_schedule(self):
        S=np.zeros((28,32));S[:,16:]=50;S[-3:,:16]=1000
        constrained=solve(S,0);unconstrained=solve(S)
        self.assertLessEqual(constrained['cvar'],1e-5)
        self.assertGreater(unconstrained['cvar'],0)
        self.assertGreater(constrained['expected_cost'],unconstrained['expected_cost'])
    def test_relaxing_budget_cannot_raise_expected_optimum(self):
        rng=np.random.default_rng(4);S=rng.normal(50,100,(28,32))
        costs=[solve(S,b)['expected_cost'] for b in (0,25,100,None)]
        self.assertTrue(all(a>=b-1e-6 for a,b in zip(costs,costs[1:])))
    def test_uniform_has_zero_excess(self):
        S=np.arange(28*96).reshape(28,96)
        s=solve(S,0,uniform=True);self.assertEqual(s['cvar'],0)
        self.assertAlmostEqual(sum(s['quantity']),4)
    def test_negative_prices_and_fee(self):
        self.assertAlmostEqual(evaluate([-10]*16,[.25]*16),-38)
    def test_bad_inputs(self):
        for S,b in [([],0),([[1]*8],0),([[1]*96],-1),([[float('inf')]*96],0)]:
            with self.assertRaises(ValueError):solve(S,b)
        with self.assertRaises(ValueError):validate_quantity([1]*4)
        with self.assertRaises(ValueError):evaluate([1],[.25]*16)
    def test_failure_is_not_silent(self):
        with patch('harbor.risk.linprog',return_value=SimpleNamespace(status=1,message='limit')):
            with self.assertRaises(RuntimeError):solve(np.ones((28,96)),25)

if __name__=='__main__':unittest.main()
