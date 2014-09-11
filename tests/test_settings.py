import unittest

from application.settings import Settings


class SettingsTest(unittest.TestCase):

    def test_get(self):
        s = Settings()

        self.assertEquals(s.get('fontdir'), 'fonts')

    def test_set(self):
        s = Settings()

        s.set('fontdir', 'foobar')

        self.assertEquals(s.get('fontdir'), 'foobar')

    def test_reset(self):
        s = Settings()

        self.assertEquals(s.get('fontdir'), 'fonts')

        s.set('fontdir', 'foobaar')
        s.reset('fontdir')

        self.assertEquals(s.get('fontdir'), 'fonts')

        s.set('fontdir', 'blaat')
        s.set('gcode_preamble', 'quack')
        s.reset()

        self.assertEquals(s.get('fontdir'), 'fonts')
        self.assertNotEquals(s.get('gcode_preamble'), 'quack')

    def test_has_setting(self):
        s = Settings()

        self.assertTrue(s.has_setting('origin'))
        self.assertFalse(s.has_setting('sinterklaas'))

    def test_from_configfile(self):
        s = Settings()

        s.from_configfile('tests/files/config.ngc')

        self.assertEquals(s.get('v_bit_angle'), 60)

        # TODO: quote and unquote strings in config

    # def test_autoload(self):
    #     s = Settings(autoload=True)
