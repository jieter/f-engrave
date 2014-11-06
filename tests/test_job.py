import unittest

from application.settings import Settings
from application.job import Job


class JobTest(unittest.TestCase):

    def test_initialize(self):
        Job(Settings())

    def test_write_gcode(self):
        settings = Settings(filename='tests/files/job_test_settings.ngc')

        settings.set('text', 'Jieter')
        settings.set('fontfile', 'gabriola.cxf')
        settings.set('var_dis', False)

        j = Job(settings)

        j.execute()

        with open('/home/jieter/Dropbox/cnc/test.ngc', 'w') as f:
            f.write(j.get_gcode())

        with open('/home/jieter/Dropbox/cnc/test.svg', 'w') as f:
            f.write(j.get_svg())
