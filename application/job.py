from geometry import BoundingBox, Zero, Scale, Translate, Rotn
from readers.cxf import parse as parse_cxf
from settings import CUT_TYPE_VCARVE
from util import fmessage

import writers


class JobError(Exception):
    pass


class Job(object):

    settings = None
    coords = []

    def __init__(self, settings):
        self.settings = settings

    def execute(self):
        # erase old data
        self.segID = []
        self.gcode = []
        self.svgcode = []
        self.coords = []
        self.vcoords = []
        self.clean_coords = []
        self.clean_segment = []
        self.clean_coords_sort = []
        self.v_clean_coords_sort = []

        self._move_origin()
        self.load_font()

        if self.settings.get('cut_type') is CUT_TYPE_VCARVE:
            self.vcarve()
        else:
            self.engrave()

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
        if font == 0:
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

    def engrave(self):
        settings = self.settings

        font = self.font
        engrave_text = self.settings.get('text')
        line_thickness = settings.get('line_thickness')

        if settings.get('height_calculation') == 'max_all':
            bbox = font.bbox
        else:
            bbox = font.get_char_bbox_used(engrave_text)

        font_line_height = bbox.ymax
        font_line_depth = bbox.ymin
        font_char_width = bbox.xmax

        font_word_space = font_char_width * (settings.get('word_space') / 100.0)

        yscale = (settings.get('yscale') - line_thickness) / (font_line_height - font_line_depth)
        if yscale <= Zero:
            yscale = .1

        xscale = settings.get('xscale') * yscale / 100

        font_char_space = font_char_width * (settings.get('char_space') / 100.0)
        font_line_space = (font_line_height - font_line_depth + line_thickness / yscale) * settings.get('line_space')

        # loop over chars and add
        line_count = 0

        xposition = 0.0
        yposition = 0.0

        text_bbox = BoundingBox()
        line_bbox = BoundingBox()
        lines_bboxes = []

        for char_count, char in enumerate(engrave_text):
            if char == ' ':
                xposition += font_word_space
                continue
            elif char == '\t':
                xposition += 3 * font_word_space
            elif char == '\n':
                xposition = 0
                yposition += font_line_space
                line_count += 1

                lines_bboxes.append(line_bbox)
                line_bbox = BoundingBox()

                continue

            line_bbox.extend(font[ord(char)])

            for stroke in font[ord(char)].stroke_list:
                x1 = stroke.xstart
                y1 = stroke.ystart
                x2 = stroke.xend
                y2 = stroke.yend

                # translate
                x1, y1 = translate(x1, y1, xposition, -yposition)
                x2, y2 = translate(x2, y2, xposition, -yposition)

                # scale
                x1, y1 = scale(x1, y1, xscale, yscale)
                x2, y2 = scale(x2, y2, xscale, yscale)

                # append
                self.coords.append([x1, y1, x2, y2, line_count, char_count])

                line_bbox.extend(BoundingBox(x1, x2, y1, y2))

            char_width = font[ord(char)].get_xmax()
            xposition += font_char_space + char_width

            text_bbox.extend(line_bbox)

        self._transform_justify()

        self._transform_radius()

        if settings.get('mirror'):
            self._transform_mirror()

        if settings.get('flip'):
            self._transform_flip()

        if settings.get('plotbox') != "no_box":
            self._draw_box()

    def _transform_justify(self):
        '''Jusitify the text'''
        justify = self.settings.get('justify')

        if justify is 'Left':
            pass
        elif justify is 'Center':
            for i, line in enumerate(self.coords):
                pass
                # TODO: implement justify center.
        elif justify is 'Right':
            for i, line in enumerate(self.coords):
                pass
                # TODO: implement justify right

    def _transform_mirror(self):
        '''Mirror in x-axis'''
        for i, line in enumerate(self.coords):
            line[0] *= -1
            line[2] *= -1

            self.coords[i] = line

    def _transform_flip(self):
        for i, line in enumerate(self.coords):
            line[1] *= -1
            line[3] *= -1

            self.coords[i] = line

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
        '''Transform the coordinates to a radius'''
        radius = self.get_plot_radius()

        # print radius
        if radius == 0.0:
            return

        min_alpha = 100000
        max_alpha = -100000
        for i, line in enumerate(self.coords):
            # print line
            line[0], line[1], alpha1 = Rotn(line[0], line[1], 0, radius)
            line[1], line[2], alpha2 = Rotn(line[1], line[2], 0, radius)
            # print line
            self.coords[i] = line
            min_alpha = min(alpha1, alpha2, min_alpha)
            max_alpha = max(alpha1, alpha2, max_alpha)

    def _draw_circle(self):
        # only for vcarving
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

        self.zero = x_zero
        self.yzero = y_zero

    def vcarve(self):
        if self.settings.get('units') == 'mm' and self.settings.get('v_step_len') <= .01:
            fmessage('v_step_len is too small, setting to default metric value')
            self.settings.reset('v_step_len')

        raise Exception('Not implemented yet.')
