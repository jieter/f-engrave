import os


def cast_boolean(value):
    if type(value) is bool:
        return bool(value)
    elif len(value) > 1:
        return value == 'True'
    else:
        return bool(int(value))


def cast_string(value):
    value = str(value).strip()
    value = value.replace('\\n', '\n')

    # unquote string
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].strip()
    else:
        return value


CAST_TYPES = {
    'str': cast_string,
    'bool': cast_boolean,
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
    'v_drv_crner': 'v_drv_corner',
    'v_stp_crner': 'v_step_corner',
    'FEED': 'feedrate',
    'PLUNGE': 'plunge_rate',
    'WSPACE': 'word_space',
    'CSPACE': 'char_space',
    'LSPACE': 'line_space',
    'TANGLE': 'text_angle',
    'TCODE': 'text_code',
    'H_CALC': 'height_calculation',
    'XSCALE': 'xscale',
    'YSCALE': 'yscale',
    'STHICK': 'line_thickness',
    'TRADIUS': 'text_radius',
    'ZSAFE': 'zsafe',
    'ZCUT': 'zcut',
}

CONFIG_FILENAME = 'config.ngc'

CONFIG_MARKER = '(fengrave_set '
CONFIG_TEMPLATE = CONFIG_MARKER + '%20s %s )'
TEXT_CODE = 'text_code'

CUT_TYPE_ENGRAVE = 'engrave'
CUT_TYPE_VCARVE = 'v-carve'

HOME_DIR = os.path.expanduser("~")
NGC_FILE = (HOME_DIR + "/None")
# IMAGE_FILE = (HOME_DIR + "/None")
IMAGE_FILE = (HOME_DIR + "/Desktop/None")  # TEST


class Settings(object):
    """
    Default values for the application settings.
    """
    _defaults = {
        'HOME_DIR': HOME_DIR,
        'NGC_FILE': NGC_FILE,
        'IMAGE_FILE': IMAGE_FILE,

        'config_filename': CONFIG_FILENAME,
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

        # ball carve (ball nose cutter)
        'b_carve': False,

        # TODO is "BALL" shape valid, or is this covered by b_carve?
        # options: 'VBIT', 'FLAT', 'BALL'
        'bit_shape': 'VBIT',

        # plot during v-carve calculation [GUI]
        'v_pplot': False,

        'inlay': False,
        'no_comments': True,

        # arc fitting, options 'none', 'center', 'radius'
        'arc_fit': 'none',
        'ext_char': False,

        # disable variables in gcode [GCODE]
        'var_dis': True,

        # cleanup cut directions
        'clean_P': True,
        'clean_X': True,
        'clean_Y': False,

        # V-Bit cut directions
        'v_clean_P': False,
        'v_clean_X': True,
        'v_clean_Y': False,

        'yscale': 50.8,
        'xscale': 100.0,
        'line_space': 1.2,
        'char_space': 25,
        'word_space': 100,
        'text_angle': 0.0,

        # safe height [GCODE]
        'zsafe': 5.0,

        # engraving depth [GCODE]
        'zcut': -0.1,

        # derived value
        'max_cut': 0.0,

        'line_thickness': 0.25,
        'border_thickness': 0.5,

        # options:  'Default',
        # 'Top-Left', 'Top-Center', 'Top-Right',
        # 'Mid-Left', 'Mid-Center', 'Mid-Right',
        # 'Bot-Left', 'Bot-Center', 'Bot-Right'
        'origin': 'Default',

        # options: 'Left', 'Right', 'Center'
        'justify': 'Left',

        # options: 'in', 'mm'
        'units': 'mm',

        # options: 'in/min', 'mm/min'
        'feed_units': 'mm/min',

        # horizontal feedrate [GCODE]
        'feedrate': 60.0,

        # feedrate for plunging into stock [GCODE]
        'plunge_rate': 10.0,

        # which bounding boxes are used to calculate line height
        # options: 'max_all', 'max_use'
        'height_calculation': 'max_use',

        # Add a box/circle around plot
        'plotbox': False,

        # Gap between box and engraving
        'boxgap': 6.35,

        # font location and name
        'fontdir': 'fonts',
        'fontfile': 'normal.cxf',

        # options: 'engrave', 'v-carve'
        'cut_type': CUT_TYPE_ENGRAVE,
        # 'cut_type': CUT_TYPE_VCARVE,

        # options: 'text', 'image'
        'input_type': 'text',
        # 'input_type': 'image',

        # v-cutter parameters:

        # options: 'scorch', 'voronoi'
        'v_strategy': 'scorch',  # new in v1.65b
        'v_bit_angle': 60,
        'v_bit_dia': 3.0,
        'v_depth_lim': 0.0,
        'v_drv_corner': 135,
        'v_step_corner': 200,
        'v_step_len': 0.254,

        # v-carve loop accuracy
        'v_acc': 0.00254,
        'allowance': 0.0,

        # options: 'chr', 'all'
        'v_check_all': 'all',

        'v_rough_stk': 0.0,
        'v_max_cut': 0.0,

        # options: 'black', 'white', 'right', 'left', 'minority', 'majority', or 'random'
        'bmp_turnpol': 'minority',
        'bmp_turdsize': 2,
        'bmp_alphamax': 1.0,
        'bmp_opttolerance': 0.2,
        'bmp_longcurve': True,

        'xorigin': 0.0,
        'yorigin': 0.0,
        'segarc': 5.0,

        'accuracy': 0.001,

        # diameter of the cleanup bit
        'clean_dia': 3.0,

        # clean-up step-over as percentage of the clean-up bit diameter
        'clean_step': 50,
        # Width of the clean-up search area (obsolete before or since v1.65)
        'clean_w': 50.8,
        'clean_v': 1.27,
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

        'default_text': 'OOF-Engrave',
        'text_code': '',
    }

    def __init__(self, filename=None, autoload=False):

        self._settings = self._defaults.copy()
        self._text_code = u''

        if filename is not None:
            self.from_configfile(filename)
        elif autoload:
            files_to_try = (
                CONFIG_FILENAME,
                os.path.expanduser('~') + os.path.sep + CONFIG_FILENAME,
                os.path.expanduser('~') + os.path.sep + '.fengraverc'
            )
            available = [c for c in files_to_try if os.path.isfile(c)]
            if len(available) > 0:
                self.from_configfile(available[0])

    def __iter__(self):
        return self._settings.items()

    def type(self, name):
        return str(type(self._settings[name]))[7:-2]

    def set(self, name, value):
        if name == TEXT_CODE:
            self._set_text_code(value)
        else:
            cast = CAST_TYPES[self.type(name)]
            self._settings[name] = cast(value)

    def get(self, name):
        return self._settings[name]

    # only for use in C-API calls
    def get_dict(self):
        return self._settings

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
                    print 'Setting not found:', name  # TODO

    def to_gcode(self):
        gcode = [CONFIG_TEMPLATE % (key, str(value).replace('\n', '\\n'))
                 for key, value in self._settings.items()]
        return gcode

    def get_text_code(self):
        return self._text_code

    def _set_text_code(self, line):

        text_code = u''
        code_list = line.split()

        for char in code_list:
            try:
                text_code += "%c" % unichr(int(char))
            except:
                text_code += "%c" % chr(int(char))

        self._text_code = text_code

    def __str__(self):
        return 'Settings:\n' + ('\n'.join([', '.join(map(str, l)) for l in self._settings.items()]))
