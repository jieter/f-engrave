
import unittest

import readers


class DXFReaderTest(unittest.TestCase):
    tolerance = 5.0
    key = ord('F')

    def test_line(self):
        with open('tests/files/line.dxf', 'r') as raw_dxf:
            parsed, source = readers.dxf(raw_dxf, self.tolerance)

            self.assertEquals(
                str(parsed[self.key].stroke_list[0]),
                'Line([0.0, 0.0, 100.0, 100.0])')

    def test_polyline(self):
        with open('tests/files/polyline.dxf', 'r') as raw_dxf:
            parsed, source = readers.dxf(raw_dxf, self.tolerance)

            for i, line in enumerate(parsed[self.key].stroke_list):
                line = str(line)
                if i is 0:
                    self.assertEquals(line, 'Line([0.0, 0.0, 50.0, 50.0])')
                elif i is 1:
                    self.assertEquals(line, 'Line([50.0, 50.0, 40.0, 0.0])')

    def test_circle(self):
        with open('tests/files/circle.dxf', 'r') as raw_dxf:
            parsed, source = readers.dxf(raw_dxf, self.tolerance)

            # circles are approximated
            self.assertEquals(
                len(parsed[self.key].stroke_list),
                72)


class CXFReaderTest(unittest.TestCase):
    pass
