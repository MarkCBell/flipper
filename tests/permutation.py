
from hypothesis import given
import hypothesis.strategies as st
import numpy as np
import pickle
import unittest

import flipper
import strategies

class TestPermutation(unittest.TestCase):
    def assertEqualArray(self, M, N):
        self.assertTrue(np.array_equal(M, N), msg='AssertionError: %s != %s' % (M, N))
    
    @given(strategies.permutations())
    def test_pickle(self, perm):
        self.assertEqual(perm, pickle.loads(pickle.dumps(perm)))
    
    @given(st.data())
    def test_hash(self, data):
        perm1 = data.draw(strategies.permutations())
        perm2 = data.draw(strategies.permutations(len(perm1)))
        self.assertTrue(perm1 != perm2 or hash(perm1) == hash(perm2))
    
    @given(strategies.permutations())
    def test_equal(self, perm):
        self.assertEqual(perm, perm)
    
    @given(st.data())
    def test_inverse(self, data):
        perm1 = data.draw(strategies.permutations())
        perm2 = data.draw(strategies.permutations(len(perm1)))
        identity = flipper.kernel.permutation.id_permutation(len(perm1))
        self.assertEqual(~(~perm1), perm1)
        self.assertEqual(perm1 * ~perm1, identity)
        self.assertEqual(~perm1 * perm1, identity)
        self.assertEqual(~(perm1 * perm2), ~perm2 * ~perm1)
    
    @given(st.data())
    def test_powers(self, data):
        perm = data.draw(strategies.permutations())
        power = data.draw(st.integers())
        self.assertEqual(perm**power, (~perm)**(-power))
        power = data.draw(st.integers(min_value=0))  # Numpy doesn't like inverting integer matrices.
        self.assertEqualArray((perm.matrix())**power, (perm**power).matrix())
    
    @given(strategies.permutations())
    def test_involution(self, perm):
        self.assertTrue(perm.order() <= 2 or perm != perm.inverse())
    
    @given(st.data())
    def test_even(self, data):
        perm1 = data.draw(strategies.permutations())
        perm2 = data.draw(strategies.permutations(len(perm1)))
        self.assertEqual(perm1.is_even() == perm2.is_even(), (perm1 * perm2).is_even())
        self.assertEqual(perm1.is_even() == perm2.is_even(), (perm2 * perm1).is_even())
    
    @given(strategies.permutations())
    def test_order(self, perm):
        identity = flipper.kernel.permutation.id_permutation(len(perm))
        for i in range(1, perm.order()):
            self.assertNotEqual(perm**i, identity)
        self.assertEqual(perm**perm.order(), identity)

