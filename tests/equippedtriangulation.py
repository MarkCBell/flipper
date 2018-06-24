
import unittest

import flipper

class TestEquippedTriangulation(unittest.TestCase):
    def test_random_word(self):
        S = flipper.load('S_1_2')
        all_words = set(S.all_words(5, equivalence='none'))
        for _ in range(10):
            word = S.random_word(5)
            self.assertIn(word, all_words)
    
    def test_composition(self):
        S = flipper.load('S_1_2')
        self.assertEqual(S.mapping_class('abababababab'), S.mapping_class('xx'))

