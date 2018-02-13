# from geometry import BoundingBox, Zero, scale, translate, rotation
from geometry import BoundingBox, Zero, rotation
from readers.cxf import parse as parse_cxf
from settings import CUT_TYPE_VCARVE
# from util import fmessage

import writers
from geometry.coords import MyText
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

        self._move_origin()

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

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') is CUT_TYPE_VCARVE:
            thickness = 0.0
        # x_scale_in = self.settings.get('xscale')
        # y_scale_in = self.settings.get('yscale')
        Angle = self.settings.get('text_angle')

        # TODO image calculation
        # if self.settings.get('useIMGsize'):
        # y_scale = y_scale_in / 100
        # x_scale = x_scale_in * y_scale / 100

        x_scale, y_scale = self.get_xy_scale()

        # TODO refactor code overlap (with Gui)

        if self.settings.get('input_type') == "text":

            text_radius = self.get_plot_radius()

            # Text transformations
            alignment = self.settings.get('justify')
            mirror = self.settings.get('mirror')
            flip = self.settings.get('flip')
            upper = self.settings.get('upper')

            self.text.transform_scale(x_scale, y_scale)
            self.text.align(alignment)
            self.text.transform_on_radius(alignment, text_radius, upper)
            self.text.transform_angle(Angle)
            if mirror:
                self.text.transform_mirror()
            if flip:
                self.text.transform_flip()

            # Engrave box or circle
            if self.settings.get('plotbox'):
                if text_radius == 0:
                    delta = thickness / 2 + self.settings.get('boxgap')
                    self.text.add_box(delta, mirror, flip)
                # Don't create the circle coords here, a G-code circle command
                # is generated later (when not v-carving)
        else:
            # Image transformations
            self.image.transform_scale(x_scale, y_scale)
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

        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0
            # self.text.set_thickness(0.0)

        # TODO this assumes height_calculation = 'max_all'.
        # We should look in bounding box with max_char, maybe
        # set the string as Font parameter and set a height_calculation
        # flag in Font
        x_scale, y_scale = self.get_xy_scale()

        # text inside or outside of the circle
        radius_in = self.settings.get('text_radius')
        if radius_in == 0.0:
            radius = radius_in
        else:
            delta = thickness / 2 + self.settings.get('boxgap')
            if self.settings.get('outer'):
                # text outside circle
                if self.settings.get('upper'):
                    radius = radius_in + delta - y_scale * font_line_depth
                else:
                    radius = radius_in - delta - y_scale * font_line_height
            else:
                if self.settings.get('upper'):
                    radius = radius_in - delta - y_scale * font_line_height
                else:
                    radius = -radius_in + delta - y_scale * font_line_depth

        return radius

    def get_xy_scale(self):

        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        x_scale_in = self.settings.get('xscale')
        y_scale_in = self.settings.get('yscale')

        try:
            y_scale = (y_scale_in - thickness) / (font_line_height - font_line_depth)
        except:
            y_scale = .1

        if y_scale <= Zero:
            y_scale = .1

        y_scale = y_scale_in / 100
        x_scale = x_scale_in * y_scale / 100

        return x_scale, y_scale

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
