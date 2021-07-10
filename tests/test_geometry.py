import unittest

from geometry import *


class RotationTest(unittest.TestCase):

    def test_no_rotation(self):
        x, y, alpha = rotation(1, 1, 0, 0)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 1.0)
        self.assertAlmostEqual(alpha, 0)

    def test_rotate(self):
        radius = 0

        x, y, alpha = rotation(1, 1, 90, radius)
        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, 1.0)
        self.assertAlmostEqual(alpha, 0)

        x, y, alpha = rotation(1, 1, -90, radius)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, -1.0)
        self.assertAlmostEqual(alpha, 0)

        x, y, alpha = rotation(1, 1, 180, radius)
        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, -1.0)
        self.assertAlmostEqual(alpha, 0)

        # with radius
        radius = 100

        x, y, alpha = rotation(1, 1, 90, radius)
        # TODO 0.005049957916810399 difference
        self.assertAlmostEqual(x, -101.0, places=1)
        # TODO 0.00998316675082389 difference
        self.assertAlmostEqual(y, 1.0, places=1)
        self.assertAlmostEqual(alpha, 0.01)

        x, y, alpha = rotation(1, 1, -90, radius)
        # TODO 0.005049957916810399 difference
        self.assertAlmostEqual(x, 101.0, places=1)
        # TODO 0.0099831667508339 difference
        self.assertAlmostEqual(y, -1.0, places=1)
        self.assertAlmostEqual(alpha, 0.01)

        x, y, alpha = rotation(1, 1, 180, radius)
        # TODO 0.00998316675083 difference)
        self.assertAlmostEqual(x, -1.0, places=1)
        # TODO 0.005049957916810399 difference
        self.assertAlmostEqual(y, -101.0, places=1)
        self.assertAlmostEqual(alpha, 0.01)
