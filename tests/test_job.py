import unittest

from application.settings import Settings
from application.job import Job


class JobTest(unittest.TestCase):

    def _save_testfiles(self, job, filename):
        basename = '/home/jieter/Dropbox/cnc/%s.%s'

        with open(basename % (filename, 'ngc'), 'w') as f:
            f.write(job.get_gcode())

        with open(basename % (filename, 'svg'), 'w') as f:
            f.write(job.get_svg())

    def test_initialize(self):
        Job(Settings())

    def _job_with_settings(self, *args):
        settings = Settings(filename='tests/files/job_test_settings.ngc')
        settings.set('text', 'Jieter')

        for key, value in args:
            settings.set(key, value)

        job = Job(settings)
        job.execute()

        return job

    def test_max_used(self):
        job = self._job_with_settings(('height_calculation', 'max_used'))
        self._save_testfiles(job, 'simple-max_used')

    def test_text_radius(self):
        job = self._job_with_settings(('text_radius', 100))

        self._save_testfiles(job, 'radius')

    def test_write_max_all(self):
        job = self._job_with_settings(('height_calculation', 'max_all'))
        self._save_testfiles(job, 'simple-max_all')

    def test_write_mirror(self):
        job = self._job_with_settings(('mirror', True))
        self._save_testfiles(job, 'mirror')

    def test_write_flip(self):
        job = self._job_with_settings(('flip', True))
        self._save_testfiles(job, 'flip')