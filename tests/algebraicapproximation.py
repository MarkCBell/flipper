
import unittest

import flipper

algebraic_approximation = flipper.kernel.AlgebraicApproximation.from_tuple

class TestAlgerbraicApproximation(unittest.TestCase):
    def test_arithmetic(self):
        x = algebraic_approximation('1.4142135623730950488016887242096980785696718753769480', 2, 2)
        y = algebraic_approximation('1.4142135623730950488016887242096980', 2, 2)
        z = algebraic_approximation('1.000000000000', 2, 2)
        
        self.assertEqual(x, y)
        self.assertNotEqual(z, y)
        self.assertEqual(x + y, x + x)
        self.assertEqual(x * x, 2)
        self.assertEqual(y * y, 2)
        self.assertEqual(y * y + x, 2 + x)
        self.assertEqual(y * (y + x), 4)
        self.assertEqual(y * y, x * x)
        self.assertGreater(x + x, 0)
        self.assertLess(-(x + x), 0)
        self.assertTrue(0 < z < x)

