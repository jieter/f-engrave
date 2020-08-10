from geometry import BoundingBox, Zero, rotation
from readers.cxf import parse as parse_cxf
from application.settings import CUT_TYPE_VCARVE

import readers
import writers

from geometry.coords import MyImage, MyText
from geometry.engrave import Engrave


class JobError(Exception):
    pass


class Job(object):

    settings = None

    def __init__(self, settings):
        self.settings = settings

    def execute(self):

        self.load_font()
        self.engrave = Engrave(self.settings)

        if self.settings.get('input_type') == "text":
            self.job_text()
        else:
            self.job_image()

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.engrave.v_carve()

    def job_text(self):
        self.text = MyText()

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0
        else:
            thickness = self.settings.get('line_thickness')

        self.text.set_font(self.font)
        self.text.set_char_space(self.settings.get('char_space'))
        self.text.set_line_space(self.settings.get('line_space'))
        self.text.set_word_space(self.settings.get('word_space'))
        self.text.set_thickness(thickness)

        # the text to be carved or engraved
        if len(self.settings.get('default_text')) > 0:
            self.text.set_text(self.settings.get('default_text'))
        else:
            self.text.set_text(self.settings.get_text_code())

        self.text.set_coords_from_strokes()
        self.engrave.set_image(self.text)

        font_line_height = self.font.line_height()
        if font_line_height <= -1e10:
            if self.settings.get('height_calculation') == "max_all":
                raise JobError('No Font Characters Found')
            elif self.settings.get('height_calculation') == "max_use":
                raise JobError('Input Characters Were Not Found in the Current Font')
            return

        # Text transformations
        alignment = self.settings.get('justify')
        mirror = self.settings.get('mirror')
        flip = self.settings.get('flip')
        upper = self.settings.get('upper')
        angle = self.settings.get('text_angle')
        radius_in = self.settings.get('text_radius')
        text_radius = self.calc_text_radius()
        x_scale, y_scale = self.get_xy_scale()

        self.text.transform_scale(x_scale, y_scale)
        self.text.align(alignment)
        self.text.transform_on_radius(alignment, text_radius, upper)
        self.text.transform_angle(angle)

        if mirror:
            self.text.transform_mirror()
        if flip:
            self.text.transform_flip()

        self.plot_bbox = self.text.bbox
        minx, maxx, miny, maxy = self.plot_bbox.tuple()

        # engrave box or circle
        if self.settings.get('plotbox'):
            if radius_in == 0:
                delta = self.get_delta()
                self.text.add_box(delta, mirror, flip)
                self.plot_bbox = self.text.bbox
                minx, maxx, miny, maxy = self.plot_bbox.tuple()
            else:
                # Don't create the circle coords here,
                # a G-code circle command is generated later (when not v-carving)
                # For the circle to fit later on, the plot bounding box is adjusted with its radius
                maxr = max(radius_in, self.text.get_max_radius())
                # thickness = self.settings.get('line_thickness')
                radius_plot = maxr + thickness / 2
                minx = miny = -radius_plot
                maxx = maxy = -minx
                self.plot_bbox = BoundingBox(minx, maxx, miny, maxy)

        x_zero, y_zero = self.move_origin(self.plot_bbox)
        x_offset = -x_zero
        y_offset = -y_zero
        self.text.transform_translate(x_offset, y_offset)

        self.plot_bbox = BoundingBox(minx + x_offset, maxx + x_offset, miny + y_offset, maxy + y_offset)
        self.text.bbox = self.plot_bbox

    def job_image(self):
        # self.image = MyImage()
        self.load_image()
        self.engrave.set_image(self.image)

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0
        else:
            thickness = self.settings.get('line_thickness')

        # Image transformations
        mirror = self.settings.get('mirror')
        flip = self.settings.get('flip')
        angle = self.settings.get('text_angle')

        y_scale_in = self.settings.get('yscale')
        if self.settings.get('useIMGsize'):
            y_scale = y_scale_in / 100
        else:
            if self.image.get_height() > 0:
                y_scale = (y_scale_in - thickness) / (self.image.get_height() - thickness)
            else:
                y_scale = 0.1
        x_scale = self.settings.get('xscale') * y_scale / 100

        self.image.transform_scale(x_scale, y_scale)
        self.image.transform_angle(angle)
        if mirror:
            self.image.transform_mirror()
        if flip:
            self.image.transform_flip()

        x_origin, y_origin = self.get_origin()
        x_zero, y_zero = self.move_origin(self.image.bbox)
        x_offset = x_origin - x_zero
        y_offset = y_origin - y_zero
        self.image.transform_translate(x_offset, y_offset)

        # engrave box or circle
        if self.settings.get('plotbox'):
            delta = self.get_delta()
            self.image.add_box(delta, mirror, flip)

    def get_svg(self):
        return '\n'.join(writers.svg(self.engrave)).strip()

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

    # Read CXF or TTF
    # def load_font(self):
    #     font = readers.readFontFile(self.settings)
    #     if font is None or len(font) == 0:
    #         raise JobError('No font file loaded')
    #     self.font = font

    def load_image(self):
        self.image = MyImage()
        font = readers.read_image_file(self.settings)
        if len(font) > 0:
            stroke_list = font[ord("F")].stroke_list
            self.image.set_coords_from_strokes(stroke_list)

    def get_origin(self):
        return (
            self.settings.get('xorigin'),
            self.settings.get('yorigin')
        )

    # TODO in Job, Gui and Engrave
    def calc_text_radius(self):

        x_scale, y_scale = self.get_xy_scale()

        # TODO this assumes height_calculation = 'max_all'.
        # We should look in bounding box with max_char, maybe
        # set the string as Font parameter and set a height_calculation
        # flag in Font
        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()

        # text inside or outside of the circle
        radius_in = self.settings.get('text_radius')
        if radius_in == 0.0:
            radius = radius_in
        else:
            delta = self.get_delta()
            if self.settings.get('outer'):
                # text outside circle
                if self.settings.get('upper'):
                    radius = radius_in + delta - y_scale * font_line_depth
                else:
                    radius = -radius_in - delta - y_scale * font_line_height
            else:
                # text inside circle
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

        # max_all
        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()
        if self.settings.get('height_calculation') == "max_use":
            font_line_height = self.text.get_font_used_height()
            font_line_depth = self.text.get_font_used_depth()

        y_scale = 0.0
        if (font_line_height - font_line_depth) > Zero:
            y_scale = (y_scale_in - thickness) / (font_line_height - font_line_depth)
        if y_scale <= Zero:
            y_scale = .1
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

    # TODO in Job, Gui and Engrave
    def get_delta(self):

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        return thickness / 2 + self.settings.get('boxgap')

    # TODO in Job, Gui and Engrave
    def move_origin(self, bbox):

        x_zero = y_zero = 0

        minx, maxx, miny, maxy = bbox.tuple()
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        origin = self.settings.get('origin')
        if origin == 'Default':
            origin = 'Arc-Center'

        vertical, horizontal = origin.split('-')
        if vertical in ('Top', 'Mid', 'Bot') and horizontal in ('Center', 'Right', 'Left'):

            if vertical == 'Top':
                y_zero = maxy
            elif vertical == 'Mid':
                y_zero = midy
            elif vertical == 'Bot':
                y_zero = miny

            if horizontal == 'Center':
                x_zero = midx
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
