
import unittest

import readers.dxf as dxf
import readers.cxf as cxf


class DXFReaderTest(unittest.TestCase):

    tolerance = 5.0
    key = ord('F')

    def test_line(self):
        with open('tests/files/line.dxf', 'r') as raw_dxf:
            parsed, source = dxf.parse(raw_dxf, self.tolerance)

            self.assertEquals(
                str(parsed[self.key].stroke_list[0]),
                'Line([0.0, 0.0, 100.0, 100.0])')

    def test_polyline(self):
        with open('tests/files/polyline.dxf', 'r') as raw_dxf:
            parsed, source = dxf.parse(raw_dxf, self.tolerance)

            for i, line in enumerate(parsed[self.key].stroke_list):
                line = str(line)
                if i == 0:
                    self.assertEquals(line, 'Line([0.0, 0.0, 50.0, 50.0])')
                elif i == 1:
                    self.assertEquals(line, 'Line([50.0, 50.0, 40.0, 0.0])')

    def test_circle(self):
        with open('tests/files/circle.dxf', 'r') as raw_dxf:
            parsed, source = dxf.parse(raw_dxf, self.tolerance)

            # circles are approximated
            self.assertEquals(
                len(parsed[self.key].stroke_list),
                72)


class CXFReaderTest(unittest.TestCase):

    def test_one(self):
        # test a couple of fonts, check their expected number of charaters.
        testfonts = (
            ('fonts/normal.cxf', 102),
            ('fonts/courier.cxf', 122),
        )

        for fontfile, numchars in testfonts:
            with open(fontfile, 'r', encoding='ISO-8859-1', errors='ignore') as f:
                font = cxf.parse(f, 1.0)

                self.assertEquals(len(font), numchars)
