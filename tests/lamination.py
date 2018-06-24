
import unittest

import flipper

class TestLamination(unittest.TestCase):
    def test_invariant_lamination(self):
        # Add more tests here.
        tests = [
            ('S_1_1', 'a'),
            ('S_1_2', 'a'),
            ('S_1_2', 'b'),
            ('S_1_2', 'c'),
            ('S_1_2', 'aB'),
            ('S_1_2', 'bbaCBAaBabcABB'),
            ('S_1_2', 'aCBACBacbaccbAaAAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'),
            ('S_2_1', 'aaabcd'),
            # ('E_12', 'aaaaBBc'),  # Really slow.
            # ('E_12', 'aaBaaBBc)'  # Really slow.
            # ('E_12', 'aaaaBBaBaBc')  # Really slow useful for profiling. Current best time 102s.
            ]
        try:
            for surface, word in tests:
                S = flipper.load(surface)
                mapping_class = S.mapping_class(word)
                mapping_class.invariant_lamination()
        except flipper.AssumptionError:
            pass  # mapping_class is not pseudo-Anosov.

