
import unittest

import flipper


class TestInterval(unittest.TestCase):
    def test_product(self):
        w = flipper.kernel.Interval.from_string('1.0000')
        self.assertEqual(w.sign(), +1)

