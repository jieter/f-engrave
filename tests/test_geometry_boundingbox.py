import unittest
import csv

from geometry import *
from geometry.boundingbox import BoundingBox

INFINITY = 1e10


class BoundingBoxTest(unittest.TestCase):

    def test_initizialize(self):
        bbox = BoundingBox()

        self.assertEquals(bbox.xmin, INFINITY)
        self.assertEquals(bbox.xmax, -INFINITY)
        self.assertEquals(bbox.ymin, INFINITY)
        self.assertEquals(bbox.ymax, -INFINITY)

        xmin, xmax, ymin, ymax = (0, 12, 123, 400)
        bbox = BoundingBox(xmin, xmax, ymin, ymax)

        self.assertEquals(bbox.xmin, xmin)
        self.assertEquals(bbox.xmax, xmax)
        self.assertEquals(bbox.ymin, ymin)
        self.assertEquals(bbox.ymax, ymax)

    def test_extend_with_bbox(self):
        bbox = BoundingBox()
        bbox.extend(BoundingBox(0, 1.0, 2, 4))
        bbox.extend(BoundingBox(1, 4, 8, 100))

        self.assertEquals(bbox, BoundingBox(0.0, 4, 2, 100))

    def test_extend_with_2tuple(self):
        bbox = BoundingBox(0, 1, 2, 4).extend(100, 500)

        self.assertEquals(bbox, BoundingBox(0, 100, 2, 500))

    def test_extend_with_4tuple(self):
        bbox = BoundingBox(0, 1, 2, 4).extend(0, 1, 3, 8)

        self.assertEquals(bbox, BoundingBox(0, 1, 2, 8))

    def test_extend_with_line(self):
        bbox = BoundingBox(0, 0, 0, 0)

        bbox.extend(Line((0, 0, 100, 100)))

        self.assertEquals(bbox, BoundingBox(0, 100, 0, 100))

    def test_extend_with_lines(self):
        bbox = BoundingBox()

        with open('tests/files/lines.csv', 'r') as csvfile:
            lines = [map(float, line) for line in csv.reader(csvfile, delimiter=',')]

            minx, maxx, miny, maxy = (INFINITY, -INFINITY, INFINITY, -INFINITY)
            for line in lines:
                bbox.extend(Line(map(float, line)))

                minx = min(minx, line[0], line[2])
                maxx = max(maxx, line[0], line[2])

                miny = min(miny, line[1], line[3])
                maxy = max(maxy, line[1], line[3])

            self.assertEquals(str(bbox), str(BoundingBox(minx, maxx, miny, maxy)))

    def test_pad(self):
        bbox = BoundingBox(0, 100, 0, 100).pad(10)

        self.assertEquals(bbox, BoundingBox(-10, 110, -10, 110))

    def test_str(self):
        bbox = BoundingBox(0, 1, 2, 3)

        self.assertEquals(str(bbox), 'BoundingBox([0.0, 1.0, 2.0, 3.0])')
