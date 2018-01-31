import unittest

from geometry import *


class RotationTest(unittest.TestCase):

    def test_no_rotation(self):

        x, y, alpha = rotation(1, 1, 0, 0)

        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 1.0)
        self.assertAlmostEqual(alpha, 0)

    def test_rotate(self):

        # radius zero
        x, y, alpha = rotation(1, 1, 90, 0)

        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, 1.0)
        self.assertAlmostEqual(alpha, 0)

        x, y, alpha = rotation(1, 1, -90, 0)

        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, -1.0)
        self.assertAlmostEqual(alpha, 0)

        x, y, alpha = rotation(1, 1, 180, 0)

        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, -1.0)
        self.assertAlmostEqual(alpha, 0)

        # with radius
        x, y, alpha = rotation(1, 1, 90, 100)

        self.assertAlmostEqual(x, -101.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(alpha, 0.0)

        x, y, alpha = rotation(1, 1, -90, 100)

        self.assertAlmostEqual(x, 101.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(alpha, 0.0)

        x, y, alpha = rotation(1, 1, 180, 100)

        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, -101.0)
        self.assertAlmostEqual(alpha, 0.0)
