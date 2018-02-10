from geometry import BoundingBox, Zero, scale, translate, rotation
from readers.cxf import parse as parse_cxf
from settings import CUT_TYPE_VCARVE
from util import fmessage

import writers
from geometry.coords import MyImage, MyText
from geometry.engrave import Engrave


class JobError(Exception):
    pass


class Job(object):

    settings = None
    coords = []
    # clean_coords = []
    # clean_coords_sort = []
    # v_coords = []
    # v_clean_coords_sort = []

    def __init__(self, settings):
        self.settings = settings

    def execute(self):
        # erase old data
        self.segID = []

        self.load_font()

        # self._move_origin()

        # if self.settings.get('cut_type') is CUT_TYPE_VCARVE:
        #     self.vcarve()
        # else:
        #     self.engrave()

        self.text = MyText()
        self.text.set_font(self.font)
        self.text.set_text(self.settings.get('default_text'))

        # self.image = MyImage()
        # stroke_list = self.font[ord("F")].stroke_list
        # self.image.set_coords_from_strokes(stroke_list)

        self.engrave = Engrave(self.settings)
        if self.settings.get('input_type') == "text":
            self.text.set_coords_from_strokes()
            self.engrave.set_image(self.text)

        elif self.settings.get('input_type.get') == "image":
            self.image.set_coords_from_strokes()
            self.engrave.set_image(self.image)

        self.coords = self.engrave.coords
        self.clean_coords = self.engrave.clean_coords
        self.clean_coords_sort = self.engrave.clean_coords_sort
        self.v_coords = self.engrave.v_coords
        self.v_clean_coords_sort = self.engrave.v_clean_coords_sort

        Thick = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == "v-carve":
            Thick = 0.0
        XScale_in = self.settings.get('xscale')
        YScale_in = self.settings.get('yscale')
        Angle = self.settings.get('text_angle')

        # TODO image calculation
        # if self.useIMGsize.get():
        YScale = YScale_in / 100
        XScale = XScale_in * YScale / 100

        # TODO reduce code overlap (with Gui)

        if self.settings.get('input_type') == "text":

            font_line_height = self.font.line_height()
            font_line_depth = self.font.line_depth()

            # text outside or inside circle
            Radius_in = self.settings.get('text_radius')
            if Radius_in != 0.0:
                if self.settings.get('outer'):
                    if self.settings.get('upper'):
                        Radius = Radius_in + Thick / 2 + YScale * (-font_line_depth)
                    else:
                        Radius = -Radius_in - Thick / 2 - YScale * (font_line_height)
                else:
                    if self.settings.get('upper'):
                        Radius = Radius_in - Thick / 2 - YScale * (font_line_height)
                    else:
                        Radius = -Radius_in + Thick / 2 + YScale * (-font_line_depth)
            else:
                Radius = Radius_in

            # Text transformations
            alignment = self.settings.get('justify')
            mirror = self.settings.get('mirror')
            flip = self.settings.get('flip')
            upper = self.settings.get('upper')

            self.text.transform_scale(XScale, YScale)
            self.text.align(alignment)
            self.text.transform_on_radius(alignment, Radius, upper)
            self.text.transform_angle(Angle)
            if mirror:
                self.text.transform_mirror()
            if flip:
                self.text.transform_flip()
        else:
            # Image transformations
            self.image.transform_scale(XScale, YScale)
            self.image.transform_angle(Angle)
            if self.settings.get('mirror'):
                self.image.transform_mirror()
            if self.settings.get('flip'):
                self.image.transform_flip()

    def get_svg(self):
        return '\n'.join(writers.svg(self)).strip()

    def get_gcode(self):
        return '\n'.join(writers.gcode(self))

    def get_font(self):
        filename = self.settings.get_fontfile()

        with open(filename) as font:
            return parse_cxf(font, self.settings.get('segarc'))

    def load_font(self):
        font = self.get_font()
        if font is None or len(font) == 0:
            raise JobError('No font file loaded')

        self.font = font

    def get_origin(self):
        return (
            self.settings.get('xorigin'),
            self.settings.get('yorigin')
        )

    def get_plot_radius(self):
        settings = self.settings

        base_radius = settings.get('text_radius')
        thickness = settings.get('line_thickness')
        font = self.font

        # TODO this assumes height_calculation = 'max_all'.
        # We should look in bounding box with max_char, maybe
        # set the string as Font parameter and set a height_calculation
        # flag in Font
        yscale = settings.get('yscale') - thickness / (font.line_height() - font.line_depth())
        if yscale <= Zero:
            yscale = 0.1

        if settings.get('outer'):
            if settings.get('upper'):
                return base_radius + thickness / 2 + yscale * -font.line_height()
            else:
                return -base_radius - thickness / 2 - yscale * font.line_depth()
        else:
            if settings.get('upper'):
                return base_radius - thickness / 2 - yscale * font.line_height()
            else:
                return -base_radius + thickness / 2 + yscale * -font.line_depth()

    def _draw_box(self):
        line_thickness = self.settings.get('line_thickness')
        delta = line_thickness / 2 + self.settings.get('boxgap')

        bbox = BoundingBox()
        for line in self.coords:
            bbox.extend(line[0], line[2], line[1], line[3])

        bbox.pad(delta)

        self.coords.append([bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymin, 0, 0])
        self.coords.append([bbox.xmax, bbox.ymin, bbox.xmax, bbox.ymax, 0, 0])
        self.coords.append([bbox.xmax, bbox.ymax, bbox.xmin, bbox.ymax, 0, 0])
        self.coords.append([bbox.xmin, bbox.ymax, bbox.xmin, bbox.ymin, 0, 0])

    def _transform_radius(self):
        """Transform the coordinates to a radius"""
        radius = self.get_plot_radius()
        if radius == 0.0:
            return

        min_alpha = 100000
        max_alpha = -100000
        for i, line in enumerate(self.coords):
            # print line
            line[0], line[1], alpha1 = rotation(line[0], line[1], 0, radius)
            line[1], line[2], alpha2 = rotation(line[1], line[2], 0, radius)
            # print line
            self.coords[i] = line
            min_alpha = min(alpha1, alpha2, min_alpha)
            max_alpha = max(alpha1, alpha2, max_alpha)

    def _draw_circle(self):
        # only for v-carving
        pass

    def _move_origin(self):

        x_zero = y_zero = 0

        origin = self.settings.get('origin')
        if origin == 'Default':
            origin = 'Arc-Center'

        vertical, horizontal = origin.split('-')
        if vertical in ('Top', 'Mid', 'Bot') and horizontal in ('Center', 'Right', 'Left'):

            if vertical is 'Top':
                y_zero = self.text_bbox.ymax
            elif vertical is 'Mid':
                y_zero = self.text_bbox.height() / 2
            elif vertical is 'Bot':
                y_zero = self.text_bbox.ymin

            if horizontal is 'Center':
                x_zero = self.text_bbox.width() / 2
            elif horizontal is 'Right':
                x_zero = self.text_bbox.xmax
            elif horizontal is 'Left':
                x_zero = self.text_bbox.xmin

        xorigin = self.settings.get('xorigin')
        yorigin = self.settings.get('yorigin')

        for i, line in enumerate(self.coords):
            self.coords[i][0] = line[0] - x_zero + xorigin
            self.coords[i][1] = line[1] - y_zero + yorigin
            self.coords[i][2] = line[2] - x_zero + xorigin
            self.coords[i][3] = line[3] - y_zero + yorigin

        self.xzero = x_zero
        self.yzero = y_zero
