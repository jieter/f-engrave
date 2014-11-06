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

    def test_from_old_configfile(self):
        s = Settings(filename='tests/files/config.ngc')

        # test integers
        self.assertEquals(s.get('v_bit_angle'), 60)
        self.assertEquals(s.get('xscale'), 100)

        # test booleans
        self.assertEquals(s.get('var_dis'), False)
        self.assertEquals(s.get('upper'), True)

        # test strings
        # TODO: quote and unquote strings in config

    def test_new_configfile(self):
        s = Settings(filename='tests/files/config_newstyle.ngc')

        # test integers
        self.assertEquals(s.get('v_bit_angle'), 60)
        self.assertEquals(s.get('xscale'), 100)

        # test booleans
        self.assertEquals(s.get('var_dis'), False)
        self.assertEquals(s.get('upper'), True)

        # test strings
        self.assertEquals(s.get('fontfile'), 'courier.cxf')
        self.assertEquals(s.get('gcode_preamble'), 'G17 G64 P0.003 M3 S3000 M7')

    def test_casting(self):
        s = Settings()

        for var in ('yscale', 'text', 'v_bit_angle'):
            a = type(s.get(var))
            s.set(var, 1)
            self.assertEquals(a, type(s.get(var)))
            s.set(var, 1.0)
            self.assertEquals(a, type(s.get(var)))

    def test_cast_string(self):
        s = Settings()

        s.set('text', '  "Test123 "   ')
        self.assertEquals(s.get('text'), 'Test123')

        s.set('text', '"bla bla "foo" bla bla"')
        self.assertEquals(s.get('text'), 'bla bla "foo" bla bla')

    # def test_autoload(self):
    #     s = Settings(autoload=True)
