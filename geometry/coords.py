from geometry import *


# TODO set tk root and use it as prefix in all Tkinter class and method calls
# TODO then rename MyImage to Image and MyText to Text


class MyImage(object):
    """
    Manage the loops, derived from an image file, as coordinate list.
    """
    def __init__(self):

        self.strokes = []
        self.init_coords()
        self.bbox = BoundingBox()

    def __len__(self):
        return len(self.coords)

    def init_coords(self):
        # Loop coordinates, format: ([x1, y1, x2, y2, line_cnt, char_cnt])
        self.coords = []

    def set_coords_from_strokes(self, strokes=[]):

        self.init_coords()
        line_cnt = char_cnt = 0

        if strokes == []:
            if self.strokes == []:
                raise ValueError, 'Image stroke list is missing'  # TODO deprecated
            else:
                # use the most recent strokes
                strokes = self.strokes
        else:
            self.strokes = strokes

        for line in strokes:
            x1 = line.xstart
            y1 = line.ystart
            x2 = line.xend
            y2 = line.yend
            self.coords.append([x1, y1, x2, y2, line_cnt, char_cnt])

        self._set_bbox()

    def get_coords(self):
        return self.coords

    def get_bbox_tuple(self):
        return self.bbox.tuple()

    def get_midxy(self):
        minx, maxx, miny, maxy = self.bbox.tuple()
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2
        return midx, midy

    def get_width(self):
        return self.bbox.width()

    def get_height(self):
        return self.bbox.height()

    def get_max_radius(self):
        maxr = 0
        for XY in self.coords:
            maxr = max(maxr, float(XY[0] * XY[0] + XY[1] * XY[1]), float(XY[2] * XY[2] + XY[3] * XY[3]))
        return sqrt(maxr)

    def transform_translate(self, xoffset, yoffset):
        for XY in self.coords:
            XY[0] += xoffset
            XY[1] += yoffset
            XY[2] += xoffset
            XY[3] += yoffset
        self._set_bbox()

    def transform_scale(self, xscale, yscale):
        for XY in self.coords:
            XY[0] *= xscale
            XY[1] *= yscale
            XY[2] *= xscale
            XY[3] *= yscale
        self._set_bbox()

    def transform_flip(self):
        for XY in self.coords:
            XY[1] *= -1
            XY[3] *= -1
        self._set_bbox()

    def transform_mirror(self):
        for XY in self.coords:
            XY[0] *= -1
            XY[2] *= -1
        self._set_bbox()

    def transform_angle(self, angle):
        for XY in self.coords:
            if angle != 0.0:
                XY[0], XY[1], A1 = rotation(XY[0], XY[1], angle, 0)
                XY[2], XY[3], A2 = rotation(XY[2], XY[3], angle, 0)
        self._set_bbox()

    def _set_bbox(self):

        xmin = ymin = 1e10
        xmax = ymax = -1e10

        for line in self.coords:
            xmax = max(line[0], line[2], xmax)
            ymax = max(line[1], line[3], ymax)
            xmin = min(line[0], line[2], xmin)
            ymin = min(line[1], line[3], ymin)

        self.bbox = BoundingBox(xmin, xmax, ymin, ymax)


class MyText(MyImage):
    """
    Manage the loops, derived from a textfile, as coordinate list.
    """
    def __init__(self):

        super(MyText, self).__init__()

        self.font = None
        self.text = u''

        # Keys of characters, if any, that were not found in the font set
        self.no_font_record = []

        # TODO use settings?
        self.line_space = 1.1
        self.char_space = 25
        self.word_space = 1.0

        self.angle = 0.0
        self.thickness = 0.25

    def __str__(self):
        ascii_text = self.text.encode('ascii', 'replace')
        return ascii_text

    def set_font(self, font):
        self.font = font

    def set_text(self, text):
        self.text = text

    def set_angle(self, angle):
        self.angle = angle

    def set_line_space(self, line_space):
        self.line_space = line_space

    def set_char_space(self, char_space):
        self.char_space = char_space

    def set_word_space(self, word_space):
        self.word_space = word_space

    def set_thickness(self, thickness):
        self.thickness = thickness

    def set_coords_from_strokes(self):
        """
        Create a coordinates list from character strokelists
        """
        self.init_coords()

        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()
        font_char_width = self.font.get_character_width()

        font_line_space = (font_line_height - font_line_depth + self.thickness) * self.line_space
        font_word_space = font_char_width * (self.word_space / 100.0)
        font_char_space = font_char_width * (self.char_space / 100.0)

        no_font_record = []
        line_max_vals = []
        xposition = 0
        yposition = 0
        line_cnt = 0

        xmin_tmp = ymin_tmp = 1e10
        xmax_tmp = ymax_tmp = -1e10

        for char_cnt, char in enumerate(self.text):

            # space
            if char == ' ':
                xposition += font_word_space
                continue

            # tab
            if char == '\t':
                xposition += 3 * font_word_space
                continue

            # linefeed
            if char == '\n':
                xposition = 0
                yposition += font_line_space
                line_cnt += 1

                line_max_vals.append([xmin_tmp, xmax_tmp, ymin_tmp, ymax_tmp])
                xmin_tmp = ymin_tmp = 1e10
                xmax_tmp = ymax_tmp = -1e10

                continue

            try:
                self.font[ord(char)].get_ymax()
            except:
                no_font = False
                for norec in no_font_record:
                    if norec == char:
                        no_font = True
                if no_font:
                    no_font_record.append(char)
                continue

            for stroke in self.font[ord(char)].stroke_list:
                x1 = stroke.xstart + xposition
                y1 = stroke.ystart - yposition
                x2 = stroke.xend + xposition
                y2 = stroke.yend - yposition
                self.coords.append([x1, y1, x2, y2, line_cnt, char_cnt])

                xmin_tmp = min(xmin_tmp, x1, x2)
                xmax_tmp = max(xmax_tmp, x1, x2)
                ymin_tmp = min(ymin_tmp, y1, y2)
                ymax_tmp = max(ymax_tmp, y1, y2)

            char_width = self.font[ord(char)].get_xmax()  # move over for next character
            xposition += font_char_space + char_width

        self.no_font_record = no_font_record
        self.line_max_vals = line_max_vals
        self._set_bbox()

    def align(self, alignment):

        line_minx = []
        line_maxx = []
        line_miny = []
        line_maxy = []
        for max_vals in self.line_max_vals:
            line_minx.append(max_vals[0])
            line_maxx.append(max_vals[1])
            line_miny.append(max_vals[2])
            line_maxy.append(max_vals[3])

        minx, maxx, miny, maxy = self.get_bbox_tuple()

        if alignment == "Left":
            pass

        elif alignment == "Center":
            for i, XY in enumerate(self.coords):
                line_num = int(XY[4])
                try:
                    self.coords[i][0] = XY[0] + (maxx - line_maxx[line_num]) / 2
                    self.coords[i][2] = XY[2] + (maxx - line_maxx[line_num]) / 2
                except:
                    pass

        elif alignment == "Right":
            for XY in iter(self.coords):
                line_num = int(XY[4])
                try:
                    XY[0] = XY[0] + (maxx - line_maxx[line_num])
                    XY[2] = XY[2] + (maxx - line_maxx[line_num])
                except:
                    pass

        self._set_bbox()

    def transform_scale(self, xscale, yscale):

        super(MyText, self).transform_scale(xscale, yscale)

        # adjust the line max values
        for vals in self.line_max_vals:
            vals[0] = vals[0] * xscale
            vals[1] = vals[1] * xscale
            vals[2] = vals[2] * yscale
            vals[3] = vals[3] * yscale

    def transform_on_radius(self, alignment, radius, upper):

        mina = 1e10
        maxa = -1e10

        if radius != 0.0:
            for XY in self.coords:
                XY[0], XY[1], A1 = rotation(XY[0], XY[1], 0, radius)
                XY[2], XY[3], A2 = rotation(XY[2], XY[3], 0, radius)
                maxa = max(maxa, A1, A2)
                mina = min(mina, A1, A2)
            mida = (mina + maxa) / 2

            if alignment == "Left":
                pass

            elif alignment == "Center":
                for XY in self.coords:
                    XY[0], XY[1] = transform(XY[0], XY[1], mida)
                    XY[2], XY[3] = transform(XY[2], XY[3], mida)

            elif alignment == "Right":
                for XY in self.coords:
                    if upper:
                        XY[0], XY[1] = transform(XY[0], XY[1], maxa)
                        XY[2], XY[3] = transform(XY[2], XY[3], maxa)
                    else:
                        XY[0], XY[1] = transform(XY[0], XY[1], mina)
                        XY[2], XY[3] = transform(XY[2], XY[3], mina)

            self._set_bbox()

    def add_box(self, delta, mirror, flip):
        """
        Add box outline
        """
        minx, maxx, miny, maxy = self.get_bbox_tuple()

        if mirror ^ flip:
            self.coords.append([minx - delta, miny - delta, minx - delta, maxy + delta, 0, 0])
            self.coords.append([minx - delta, maxy + delta, maxx + delta, maxy + delta, 0, 0])
            self.coords.append([maxx + delta, maxy + delta, maxx + delta, miny - delta, 0, 0])
            self.coords.append([maxx + delta, miny - delta, minx - delta, miny - delta, 0, 0])
        else:
            self.coords.append([minx - delta, miny - delta, maxx + delta, miny - delta, 0, 0])
            self.coords.append([maxx + delta, miny - delta, maxx + delta, maxy + delta, 0, 0])
            self.coords.append([maxx + delta, maxy + delta, minx - delta, maxy + delta, 0, 0])
            self.coords.append([minx - delta, maxy + delta, minx - delta, miny - delta, 0, 0])

        self._set_bbox()
