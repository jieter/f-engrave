import unittest

from application.settings import Settings
from application.job import Job


class JobTest(unittest.TestCase):

    def _save_testfiles(self, job, filename):
        basename = '/Users/johan/Desktop/cnc/%s.%s'

        with open(basename % (filename, 'ngc'), 'w') as f:
            f.write(job.get_gcode())

        with open(basename % (filename, 'svg'), 'w') as f:
            f.write(job.get_svg())

    def _job_with_settings(self, *args):
        settings = Settings(filename='tests/files/job_test_settings.ngc')

        for key, value in args:
            settings.set(key, value)

        job = Job(settings)
        job.execute()

        return job

    def test_text_code(self):
        job = self._job_with_settings(
            # ('fontfile', 'unicode.cxf'),
            # ('fontfile', 'ttf/LucidaBright.ttf'),
            # ('text_code', '116  101  115  116'),  # "test"
            ('text_code', '070 045 069 110 103 114 097 118 101'),  # "F-Engrave"
            ('default_text', ''),
        )
        self._save_testfiles(job, 'text_code')

    def test_max_used(self):
        job = self._job_with_settings(('height_calculation', 'max_used'))
        self._save_testfiles(job, 'simple-max_used')

    def test_text_radius(self):
        job = self._job_with_settings(
            ('default_text', 'radius=100'),
            ('text_radius', 100),
        )
        self._save_testfiles(job, 'radius')

    def test_write_max_all(self):
        job = self._job_with_settings(('height_calculation', 'max_all'))
        self._save_testfiles(job, 'simple-max_all')

    def test_write_mirror(self):
        job = self._job_with_settings(
            ('default_text', 'mirror'),
            ('mirror', True),
        )
        self._save_testfiles(job, 'mirror')

    def test_write_flip(self):
        job = self._job_with_settings(
            ('default_text', 'flip'),
            ('flip', True),
        )
        self._save_testfiles(job, 'flip')

    def test_write_box(self):
        job = self._job_with_settings(
            ('default_text', 'plotbox\nboxgap=50mm'),
            ('plotbox', 'True'),
            ('boxgap', 50),
        )
        self._save_testfiles(job, 'box')

    def test_write_box_inch(self):
        job = self._job_with_settings(
            ('default_text', 'plotbox\nboxgap=2\"'),
            ('units', 'in'),
            ('feed_units', 'in/mm'),
            ('accuracy', 0.00254),
            ('plotbox', 'True'),
            ('boxgap', 2),
            ('yscale', 2),
            ('v_bit_dia', 0.118),
            ('line_thickness', 0.01),
            ('zcut', -0.00394),
            ('clean_dia', 0.118),
            ('feedrate', 2.36),
            ('plunge_rate', 0.395),
            ('zsafe', 0.197),
            ('v_step_len', 0.01),
        )
        self._save_testfiles(job, 'box_inch')

    def test_write_circle(self):
        job = self._job_with_settings(
            ('default_text', 'plotcircle\nboxgap=5mm\n'),
            ('plotbox', 'True'),
            ('text_radius', '30.0'),
            ('boxgap', 5),
        )
        self._save_testfiles(job, 'circle')

    def test_write_circle_midleft(self):
        job = self._job_with_settings(
            ('default_text', 'plotcircle\nboxgap=5\nmidleft\n'),
            ('plotbox', 'True'),
            ('text_radius', '30.0'),
            ('boxgap', 5),
            ('origin', 'Mid-Left'),
        )
        self._save_testfiles(job, 'circle_midleft')

    def test_vcarve(self):
        job = self._job_with_settings(
            ('default_text', 'V-Carve'),
            ('cut_type', 'v-carve'),
        )
        self._save_testfiles(job, 'vcarve')

    # TODO add clean step
    def test_vcarve_box(self):
        job = self._job_with_settings(
            ('default_text', 'L'),
            ('fontfile', 'kochigothic.cxf'),
            ('cut_type', 'v-carve'),
            ('plotbox', 'True'),
            ('boxgap', '5'),
            ('yscale', '500'),
        )
        self._save_testfiles(job, 'vcarve_box')

    def test_image(self):
        job = self._job_with_settings(
            ('input_type', 'image'),
            ('IMAGE_FILE', 'tests/files/ring.dxf'),
        )
        self._save_testfiles(job, 'image')
