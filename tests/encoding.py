
import unittest

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

class TestEncoding(unittest.TestCase):
    def test_old(self):
        S = flipper.load('S_1_1')
        f, g = S.mapping_class('aB'), S.mapping_class('bA')  # Some pseudo-Anosov ones.
        h, i = S.mapping_class('ab'), S.mapping_class('')  # Some finite order ones.
        
        tests = [
            h != i,
            h**6 == i,
            h**-3 == h**3,
            h**0 == i,
            h.order() == 6,
            f != g,
            f.is_conjugate_to(g),
            not f.is_conjugate_to(h),
            not h.is_conjugate_to(i),
            ]
        self.assertTrue(all(tests))
    
    def test_nt_type(self):
        examples = [
            ('S_1_1', 'a', NT_TYPE_REDUCIBLE),
            ('S_1_1', 'ab', NT_TYPE_PERIODIC),
            ('S_1_1', 'aB', NT_TYPE_PSEUDO_ANOSOV),
            ('S_1_2', 'a', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'b', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'c', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'aB', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'bbaCBAaBabcABB', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', NT_TYPE_PSEUDO_ANOSOV),
            ('S_2_1', 'aaabcd', NT_TYPE_PSEUDO_ANOSOV),
            ('S_2_1', 'abcdeF', NT_TYPE_PSEUDO_ANOSOV),
            # ('E_12', 'aaaaBBp', NT_TYPE_PSEUDO_ANOSOV),
            # ('E_12', 'aaBaaBBp', NT_TYPE_REDUCIBLE),
            # ('E_12', 'aaaaBBaBaBp', NT_TYPE_PSEUDO_ANOSOV),
            ]
        
        for surface, word, mapping_class_type in examples:
            h = flipper.load(surface).mapping_class(word)
            self.assertEqual(h.nielsen_thurston_type(), mapping_class_type)
    
    def test_package(self):
        examples = [
            ('S_1_1', 'a', NT_TYPE_REDUCIBLE),
            ('S_1_1', 'ab', NT_TYPE_PERIODIC),
            ('S_1_1', 'aB', NT_TYPE_PSEUDO_ANOSOV),
            ('S_1_2', 'a', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'b', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'c', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'aB', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'bbaCBAaBabcABB', NT_TYPE_REDUCIBLE),
            ('S_1_2', 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', NT_TYPE_PSEUDO_ANOSOV),
            ('S_2_1', 'aaabcd', NT_TYPE_PSEUDO_ANOSOV),
            ('S_2_1', 'abcdeF', NT_TYPE_PSEUDO_ANOSOV),
            # ('E_12', 'aaaaBBp', NT_TYPE_PSEUDO_ANOSOV),
            # ('E_12', 'aaBaaBBp', NT_TYPE_REDUCIBLE),
            # ('E_12', 'aaaaBBaBaBp', NT_TYPE_PSEUDO_ANOSOV),
            ]
        
        for surface, word, mapping_class_type in examples:
            h = flipper.load(surface).mapping_class(word)
            self.assertEqual(h.package(), h.source_triangulation.encode(h.package()).package())
    
    def test_canonical_idempotence(self):
        examples = [
            ('SB_4', 's_0S_1s_2S_3s_1S_2', NT_TYPE_PSEUDO_ANOSOV),
            ('S_1_1', 'aB', NT_TYPE_PSEUDO_ANOSOV),
            ('S_1_2', 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', NT_TYPE_PSEUDO_ANOSOV),
            ('S_2_1', 'aaabcd', NT_TYPE_PSEUDO_ANOSOV),
            ('S_2_1', 'abcdeF', NT_TYPE_PSEUDO_ANOSOV),
            ]
        
        for surface, word, nt_type in examples:
            h = flipper.load(surface).mapping_class(word)
            self.assertEqual(h.canonical(), h.canonical().canonical())

