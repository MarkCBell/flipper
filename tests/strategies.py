
from hypothesis import given
import hypothesis.strategies as st
import unittest

import flipper

@st.composite
def permutations(draw, N=None):
    if N is None: N = draw(st.integers(min_value=1, max_value=10))
    return flipper.kernel.Permutation(draw(st.permutations(range(N))))


class TestStrategiesHealth(unittest.TestCase):
    @given(permutations())
    def test_permutations(self, perm):
        self.assertIsInstance(perm, flipper.kernel.Permutation)

if __name__ == '__main__':
    unittest.main()

