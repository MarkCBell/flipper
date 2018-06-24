
import unittest

import flipper

class TestTriangulation(unittest.TestCase):
    def test_isometries(self):
        tests = [
            ('S_0_4', 2),
            ('S_1_1', 6),
            ('S_1_2', 4),
            ('S_2_1', 2),
            ('S_3_1', 2),
            ('E_12', 12),
            ('E_24', 24),
            ('E_36', 36)
            ]
        for surface, num_isoms in tests:
            self.assertEqual(len(flipper.load(surface).triangulation.self_isometries()), num_isoms)
            
    def test_sig(self):
        for surface in ['S_0_4', 'S_1_1', 'S_1_2', 'S_2_1', 'S_3_1', 'E_12', 'E_24', 'E_36']:
            T = flipper.load(surface).triangulation
            T2 = flipper.triangulation_from_iso_sig(T.iso_sig())
            self.assertTrue(T.is_isometric_to(T2))
            self.assertEqual(T.iso_sig(), T2.iso_sig())

