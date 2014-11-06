from geometry import BoundingBox, Zero, Scale, Translate
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

        self.RADIUS_PLOT = 0

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

    def engrave(self):
        settings = self.settings

        engrave_text = self.settings.get('text')

        line_thickness = settings.get('line_thickness')

        # v_flop = settings.get('v_flop')

        # if settings.get('input_type') == "image":
        #     if len(self.image) == 0:
        #         raise JobError('No image file loaded')
        font = self.get_font()

        if font == 0:
            raise JobError('No font file loaded')

        font_bbox = BoundingBox()

        if settings.get('height_calculation') == 'max_all':
            # Use the maximum height from all the characters in the font
            for char in font:
                font_bbox.extend(font[ord(char)])
        else:
            # 'max_use'
            for char in engrave_text:
                font_bbox.extend(font[ord(char)])

        font_line_height = font_bbox.ymax
        font_line_depth = font_bbox.ymin
        font_char_width = font_bbox.xmax

        font_word_space = font_char_width * (settings.get('word_space') / 100.0)

        yscale = (settings.get('yscale') - line_thickness) / (font_line_height - font_line_depth)
        if yscale <= Zero:
            yscale = .1

        xscale = settings.get('xscale') * yscale / 100
        font_char_space = font_char_width * (settings.get('char_space') / 100.0)

        radius = settings.get('text_radius')
        if radius != 0.0:
            if settings.get('outer'):
                if settings.get('upper'):
                    radius = radius + line_thickness / 2 + yscale * (-font_line_depth)
                else:
                    radius = -radius - line_thickness / 2 - yscale * (font_line_height)
            else:
                if settings.get('upper'):
                    radius = radius - line_thickness / 2 - yscale * (font_line_height)
                else:
                    radius = -radius + line_thickness / 2 + yscale * (-font_line_depth)

        font_line_space = (font_line_height - font_line_depth + line_thickness / yscale) * settings.get('line_space')

        # loop over chars and add
        char_count = 0
        line_count = 0

        xposition = 0.0
        yposition = 0.0

        text_bbox = BoundingBox()
        line_bbox = BoundingBox()
        lines_bboxes = []

        for char in engrave_text:
            char_count += 1

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

                raise Exception('Only one line for now...')
                # continue
                break

            line_bbox.extend(font[ord(char)])

            for stroke in font[ord(char)].stroke_list:
                x1 = stroke.xstart
                y1 = stroke.ystart
                x2 = stroke.xend
                y2 = stroke.yend

                # translate
                x1, y1 = Translate(x1, y1, xposition, -yposition)
                x2, y2 = Translate(x2, y2, xposition, -yposition)

                # scale
                x1, y1 = Scale(x1, y1, xscale, yscale)
                x2, y2 = Scale(x2, y2, xscale, yscale)

                # append
                self.coords.append([x1, y1, x2, y2, line_count, char_count])

                line_bbox.extend(BoundingBox(x1, x2, y1, y2))

            char_width = font[ord(char)].get_xmax()
            xposition += font_char_space + char_width

            text_bbox.extend(line_bbox)

        # end for char in engrave_text

        # Justification
        justify = settings.get('justify')

        if justify is 'Left':
            pass
        elif justify is 'Center':
            for i, line in enumerate(self.coords):
                pass
        elif justify is 'Right':
            for i, line in enumerate(self.coords):
                pass

        self.text_bbox = text_bbox.pad(line_thickness)

    def _move_origin(self):
        settings = self.settings

        x_zero = y_zero = 0

        vertical, horizontal = settings.get('origin').split('-')
        if vertical in ('Top', 'Mid', 'Bot') and horizontal in ('Center', 'Right', 'Left'):
            if vertical is 'Top':
                y_zero = self.text_bbox.maxy
            elif vertical is 'Mid':
                y_zero = self.text_bbox.height() / 2
            elif vertical is 'Bot':
                y_zero = self.text_bbox.miny

            if horizontal is 'Center':
                x_zero = self.text_bbox.width() / 2
            elif horizontal is 'Right':
                x_zero = self.text_bbox.maxx
            elif horizontal is 'Left':
                x_zero = self.text_bbox.minx

        xorigin = settings.get('xorigin')
        yorigin = settings.get('yorigin')
        for i, line in enumerate(self.coords):
            self.coords[i][0] = line[0] - x_zero + xorigin
            self.coords[i][1] = line[1] - y_zero + yorigin
            self.coords[i][2] = line[2] - x_zero + xorigin
            self.coords[i][3] = line[3] - y_zero + yorigin

        self.xzero = x_zero
        self.yzero = y_zero

    def vcarve(self):
        if self.settings.get('units') == 'mm' and self.settings.get('v_step_len') <= .01:
            fmessage('v_step_len is too small, setting to default metric value')
            self.settings.reset('v_step_len')
