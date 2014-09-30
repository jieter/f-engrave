import os

CAST_TYPES = {
    'bool': bool,
    'int': int,
    'str': str,
    'int': int,
    'float': float
}

# Old names to maintain backwards compatibility while reading
# config files. Only supported while loading values
# from config files.
OLD_SETTING_NAMES = {
    'gpost': 'gcode_postamble',
    'gpre': 'gcode_preamble',
    'bmp_long': 'bmp_longcurve',
    'bmp_optto': 'bmp_opttolerance',
    'bmp_turnp': 'bmp_turnpol',
    'bmp_turds': 'bmp_turdsize',
    'bmp_alpha': 'bmp_alphamax',
    'FEED': 'feedrate',
    'WSPACE': 'word_space',
    'CSPACE': 'char_space',
    'LSPACE': 'line_space',
    'H_CALC': 'height_calculation',
    'XSCALE': 'xscale',
    'YSCALE': 'yscale',
    'STHICK': 'line_thickness',
    'TRADIUS': 'text_radius',
}

CONFIG_MARKER = '(fengrave_set '
CONFIG_TEMPLATE = CONFIG_MARKER + '%20s %s )'

CUT_TYPE_ENGRAVE = 'engrave'
CUT_TYPE_VCARVE = 'v-carve'


class Settings(object):

    '''
    Default values for the application settings.
    '''
    _defaults = {
        'batch': False,
        'show_axis': True,
        'show_box': True,
        'show_thick': True,
        'flip': False,
        'mirror': False,

        # text plotted on a circle with radius
        'text_radius': 0.0,
        'outer': True,  # outside circle
        'upper': True,  # on top of cirle
        'fontdex': False,
        'useIMGsize': False,

        # flip normals (V-carve side)
        'v_flop': False,
        'b_carve': False,
        'v_pplot': True,
        'arc_fit': True,
        'ext_char': False,
        'var_dis': False,

        'clean_P': True,
        'clean_X': True,
        'clean_Y': False,
        'v_clean_P': False,
        'v_clean_X': True,
        'v_clean_Y': False,

        'yscale': 2.0,
        'xscale': 100.0,
        'line_space': 1.1,
        'char_space': 25,
        'word_space': 100,
        'TANGLE': 0.0,
        'ZSAFE': 0.25,
        'ZCUT': -0.005,
        'line_thickness': 0.01,

        # Options:  "Default",
        # "Top-Left", "Top-Center", "Top-Right",
        # "Mid-Left", "Mid-Center", "Mid-Right",
        # "Bot-Left", "Bot-Center", "Bot-Right"
        'origin': 'Default',

        # options: 'Left', 'Right', 'Center'
        'justify': 'Left',

        # options: 'in', 'mm'
        'units': 'mm',
        'feedrate': 5.0,
        'fontfile': 'normal.cxf',

        # which bounding boxes are used to calculate line height
        # options: 'max_all', 'max_use'
        'height_calculation': 'max_use',
        'plotbox': 'no_box',
        'boxgap': 0.25,
        'fontdir': 'fonts',

        # options: 'engrave', 'v-carve'
        'cut_type': CUT_TYPE_ENGRAVE,

        # options: 'text', 'image'
        'input_type': 'text',

        'v_bit_angle': 90,
        'v_bit_dia': 0.5,
        'v_depth_lim': 0.0,
        'v_drv_crner': 135,
        'v_stp_crner': 200,
        'v_step_len': 0.25,

        # V-carve loop accuracy
        'v_acc': 0.001,

        # options: 'chr', 'all'
        'v_check_all': 'all',

        # options: black, white, right, left, minority, majority, or random
        'bmp_turnpol': 'minority',
        'bmp_turdsize': 2,
        'bmp_alphamax': 1,
        'bmp_opttolerance': 0.2,
        'bmp_longcurve': True,

        'xorigin': 0.0,
        'yorigin': 0.0,
        'segarc': 5.0,
        'accuracy': 0.001,

        'clean_w': 2.0,
        'clean_v': 0.05,
        # diameter of the cleanup bit
        'clean_dia': 0.25,

        # Clean-up step-over as percent of clean-up bit diameter
        'clean_step': 50,
        'clean_name': '_clean',


        # G-Code Default Preamble
        #
        # G17        : sets XY plane
        # G64 P0.003 : G64 P- (motion blending tolerance set to 0.003 (units))
        #              G64 without P option keeps the best speed possible, no matter how
        #              far away from the programmed point you end up.
        # M3 S3000   : Spindle start at 3000
        # M7         : Turn mist coolant on
        'gcode_preamble': 'G17 G64 P0.003 M3 S3000 M7',

        # G-Code Default Postamble
        #
        # M5 : Stop Spindle
        # M9 : Turn all coolant off
        # M2 : End Program
        'gcode_postamble': 'M5 M9 M2',

        'text': 'F-engrave'
    }

    def __init__(self, filename=None, autoload=False):
        self._settings = self._defaults.copy()

        if filename is not None:
            self.from_configfile(filename)
        elif autoload:
            files_to_try = (
                'config.ngc',
                os.path.expanduser('~') + os.path.sep + '.fengraverc',
                os.path.expanduser('~') + os.path.sep + 'config.ngc',
            )
            available = [c for c in files_to_try if os.path.isfile(c)]
            if len(available) > 0:
                self.from_configfile(available[0])

    def __iter__(self):
        return self._settings.items()

    def type(self, name):
        return str(type(self._settings[name]))[7:-2]

    def set(self, name, value):
        cast = CAST_TYPES[self.type(name)]

        value = cast(value)
        # unquote string
        if self.type(name) == 'str' and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        self._settings[name] = value

    def get(self, name):
        return self._settings[name]

    def reset(self, name=None):
        if name is None:
            self._settings = self._defaults.copy()
        else:
            self.set(name, self._defaults[name])

    def has_setting(self, name):
        return name in self._settings

    def get_fontfile(self):
        return self.get('fontdir') + os.path.sep + self.get('fontfile')

    def from_configfile(self, filename):
        with open(filename, 'r') as config:
            for line in config.readlines():
                if not line.startswith(CONFIG_MARKER):
                    continue

                line = line[len(CONFIG_MARKER):].strip()

                name = line.split(' ')[0].strip()
                setting = line[len(name):-1].strip()

                if not self.has_setting(name) and name in OLD_SETTING_NAMES:
                    name = OLD_SETTING_NAMES[name]

                try:
                    self.set(name, setting)
                except KeyError:
                    # care.
                    pass
                    # print '?? ', name

    def to_gcode(self):
        return '\n'.join([CONFIG_TEMPLATE % l for l in self._settings.items()])

    def __str__(self):
        return 'Settings:\n' + ('\n'.join([', '.join(map(str, l)) for l in self._settings.items()]))
