
import unittest

import flipper

class TestRealNumberField(unittest.TestCase):
    N = flipper.kernel.RealNumberField([-2, 0, 1])  # QQ(sqrt(2)).
    x = N.lmbda  # sqrt(2)
    
    def test_powers(self):
        self.assertEqual(self.x * self.x, self.x**2)
        self.assertEqual(self.x * self.x, 2)

