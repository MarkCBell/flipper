
import unittest

import flipper

class TestMatrix(unittest.TestCase):
    def test_product(self):
        M = flipper.kernel.Matrix([[2, 1], [1, 1]])
        N = flipper.kernel.Matrix([[1, -1], [-1, 2]])
        M_inv = flipper.kernel.Matrix([[1, -1], [-1, 2]])
        
        self.assertEqual(M * N, flipper.kernel.id_matrix(2))
    
    def test_characteristic_polynomial(self):
        M = flipper.kernel.Matrix([[2, 1], [1, 1]])
        self.assertEqual(M.characteristic_polynomial(), flipper.kernel.Polynomial([1, -3, 1]))
        self.assertEqual(M.characteristic_polynomial()(M), flipper.kernel.zero_matrix(2))  # Check Cayley--Hamilton theorem.
        
    def test_determinant(self):
        M = flipper.kernel.Matrix([[2, 1], [1, 1]])
        N = flipper.kernel.Matrix([[1, -1], [-1, 2]])
        self.assertEqual(M.determinant(), 1)
        self.assertEqual((M + N).determinant(), 9)
        self.assertEqual((M - N).determinant(), -5)
    
    def test_powers(self):
        M = flipper.kernel.Matrix([[2, 1], [1, 1]])
        M_inv = flipper.kernel.Matrix([[1, -1], [-1, 2]])
        self.assertEqual((M**2)**3, (M**3)**2)  # Check that powers are associative.
        self.assertEqual(M.inverse(), M_inv)

