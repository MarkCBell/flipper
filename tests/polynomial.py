
import unittest

import flipper

class TestPolynomial(unittest.TestCase):
    def test_derivative(self):
        f = flipper.kernel.Polynomial([-2, 0, 1])  # f = -2 + x^2.
        g = flipper.kernel.Polynomial([0, 2])  # g = 2x = f'.
        self.assertEqual(f.derivative(), g)
    
    def test_add(self):
        f = flipper.kernel.Polynomial([-2, 0, 1])  # f = -2 + x^2.
        g = flipper.kernel.Polynomial([0, 2])  # g = 2x = f'.
        h = flipper.kernel.Polynomial([-2, 2, 1])  # h = -2 + 2x + x^2 = f + g.
        self.assertEqual(f + g, h)
    
    def test_roots(self):
        
        f = flipper.kernel.Polynomial([-2, 0, 1])  # f = -2 + x^2.
        p1 = flipper.kernel.Polynomial([1, -7, 19, -26, 19, -7, 1])
        p2 = flipper.kernel.Polynomial([2, -3, 1])  # 2 - 3x + x^2 = (x - 2) (x - 1).
    
        self.assertEqual(len(f.real_roots()), 2)
        self.assertEqual(len(p1.real_roots()), 3)
        self.assertEqual(len(p2.real_roots()), 2)

