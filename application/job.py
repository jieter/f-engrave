from geometry import BoundingBox, Zero, rotation
from readers.cxf import parse as parse_cxf
from settings import CUT_TYPE_VCARVE

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
        # self.segID = []

        self.load_font()

        self.text = MyText()
        self.text.set_font(self.font)
        self.text.set_text(self.settings.get('default_text'))

        self.image = MyImage()
        # stroke_list = self.font[ord("F")].stroke_list
        # self.image.set_coords_from_strokes(stroke_list)

        self.engrave = Engrave(self.settings)
        if self.settings.get('input_type') == "text":
            self.text.set_coords_from_strokes()
            self.engrave.set_image(self.text)
        elif self.settings.get('input_type') == "image":
            self.image.set_coords_from_strokes()
            self.engrave.set_image(self.image)

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        x_origin, y_origin = self.get_origin()

        # TODO refactor code overlap (with Gui)

        if self.settings.get('input_type') == "text":

            text_radius = self.calc_text_radius()

            # Text transformations
            alignment = self.settings.get('justify')
            mirror = self.settings.get('mirror')
            flip = self.settings.get('flip')
            upper = self.settings.get('upper')
            angle = self.settings.get('text_angle')

            x_scale, y_scale = self.get_xy_scale()
            self.text.transform_scale(x_scale, y_scale)
            self.text.align(alignment)
            self.text.transform_on_radius(alignment, text_radius, upper)
            self.text.transform_angle(angle)
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
            x_zero, y_zero = self._move_origin()
            x_offset = x_origin - x_zero
            y_offset = y_origin - y_zero
            self.text.transform_translate(x_offset, y_offset)
        else:
            # TODO image calculation
            # if self.settings.get('useIMGsize'):
            # y_scale = y_scale_in / 100
            # x_scale = x_scale_in * y_scale / 100

            # Image transformations
            self.image.transform_scale(x_scale, y_scale)
            self.image.transform_angle(angle)
            if self.settings.get('mirror'):
                self.image.transform_mirror()
            if self.settings.get('flip'):
                self.image.transform_flip()

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.engrave.v_carve()

        engrave = self.engrave
        # engrave.refresh_coords()  # TODO
        self.coords = engrave.coords
        self.v_coords = engrave.v_coords
        # self.clean_coords = engrave.clean_coords
        # self.clean_coords_sort = engrave.clean_coords_sort
        # self.v_clean_coords_sort = engrave.v_clean_coords_sort

    def get_svg(self):
        return '\n'.join(writers.svg(self)).strip()

    def get_gcode(self):
        return '\n'.join(writers.gcode(self.engrave))

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

    def calc_text_radius(self):

        x_scale, y_scale = self.get_xy_scale()

        # TODO this assumes height_calculation = 'max_all'.
        # We should look in bounding box with max_char, maybe
        # set the string as Font parameter and set a height_calculation
        # flag in Font
        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0
            # self.text.set_thickness(0.0)

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

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        x_scale_in = self.settings.get('xscale')
        y_scale_in = self.settings.get('yscale')

        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()
        try:
            y_scale = (y_scale_in - thickness) / (font_line_height - font_line_depth)
        except:
            y_scale = .1

        if y_scale <= Zero:
            y_scale = .1

        y_scale = y_scale_in / 100
        x_scale = x_scale_in * y_scale / 100

        return (x_scale, y_scale)

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
        radius = self.calc_text_radius()
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

    # TODO in Job, Gui and Engrave

    def _move_origin(self):

        x_zero = y_zero = 0

        minx, maxx, miny, maxy = self.text.get_bbox_tuple()
        midx, midy = self.text.get_midxy()

        origin = self.settings.get('origin')
        if origin == 'Default':
            origin = 'Arc-Center'

        vertical, horizontal = origin.split('-')
        if vertical in ('Top', 'Mid', 'Bot') and horizontal in ('Center', 'Right', 'Left'):

            if vertical == 'Top':
                y_zero = maxy
            elif vertical == 'Mid':
                y_zero = midy  # height / 2
            elif vertical == 'Bot':
                y_zero = miny

            if horizontal == 'Center':
                x_zero = midx  # width / 2
            elif horizontal == 'Right':
                x_zero = maxx
            elif horizontal == 'Left':
                x_zero = minx

        else:  # "Default"
            pass

        # TODO use setter method
        self.engrave.xzero = x_zero
        self.engrave.yzero = y_zero

        return (x_zero, y_zero)
