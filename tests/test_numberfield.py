
import unittest

import flipper

class TestNumberField(unittest.TestCase):
    N = flipper.kernel.NumberField.from_tuple([-2, 0, 1], '1.4142135623')  # QQ(sqrt(2)).
    x = N.lmbda  # sqrt(2)
    
    def test_powers(self):
        self.assertEqual(self.x * self.x, self.x**2)
        self.assertEqual(self.x * self.x, 2)

