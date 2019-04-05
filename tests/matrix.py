
import unittest

import flipper

class TestMatrix(unittest.TestCase):
    def test_product(self):
        M = flipper.kernel.Matrix([[2, 1], [1, 1]])
        N = flipper.kernel.Matrix([[1, -1], [-1, 2]])
        
        self.assertEqual(M * N, flipper.kernel.id_matrix(2))
    
    def test_powers(self):
        M = flipper.kernel.Matrix([[2, 1], [1, 1]])
        self.assertEqual((M**2)**3, (M**3)**2)  # Check that powers are associative.

