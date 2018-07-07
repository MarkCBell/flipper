
import unittest
try:
    import snappy
except ImportError:
    snappy = None

import flipper

tests = [
    ('S_1_1', 'aB', 'm004'),
    ('S_1_1', 'Ba', 'm004'),
    ('S_1_1', 'Ab', 'm004'),
    ('S_1_1', 'bA', 'm004'),
    ('S_1_1', 'aBababab', 'm003'),
    ('S_1_1', 'Baababab', 'm003'),
    ('S_1_1', 'Abababab', 'm003'),
    ('S_1_1', 'bAababab', 'm003'),
    ('S_1_1', 'aBaB', 'm206'), ('S_1_1', 'aBaBababab', 'm207'),  # Double covers.
    ('S_1_2', 'abC', 'm129'),
    ('S_2_1', 'aaabcd', 'm036'),
    ('S_2_1', 'abcdeF', 'm038')
    ]

twister_tests = [
    ('S_1_1', 'aB')
    ]

class TestTriangulation3(unittest.TestCase):
    def assertManifoldsIsometric(self, manifold, target):
        for _ in range(100):
            try:
                if manifold.is_isometric_to(target):
                    return True
            except RuntimeError:
                pass  # SnapPy couldn't decide if these are isometric or not.
            manifold.randomize()
        
        return False
    
    def test_snappy(self):
        if snappy is None: return
        for surface, word, target_manifold in tests:
            manifold = snappy.Manifold(flipper.load(surface).mapping_class(word).bundle(veering=False))
            self.assertManifoldsIsometric(manifold, snappy.Manifold(target_manifold))
    
    def test_twister(self):
        if snappy is None: return
        for surface, word in twister_tests:
            manifold = snappy.Manifold(flipper.load(surface).mapping_class(word).bundle(veering=False))
            self.assertManifoldsIsometric(manifold, snappy.twister.Surface(surface).bundle(word))

