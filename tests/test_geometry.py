import unittest

from geometry import *


class RotnTest(unittest.TestCase):

    def test_no_rotation(self):

        x, y, alpha = Rotn(1, 1, 0, 0)

        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 1.0)
        self.assertAlmostEqual(alpha, 0)

    def test_rotate(self):
        x, y, alpha = Rotn(1, 1, 90, 0)

        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, 1.0)
        self.assertAlmostEqual(alpha, 0)

        x, y, alpha = Rotn(1, 1, -90, 100)

        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, -1.0)
        self.assertAlmostEqual(alpha, 0)

        x, y, alpha = Rotn(1, 1, 180, 100)

        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, -1.0)
        self.assertAlmostEqual(alpha, 0)
