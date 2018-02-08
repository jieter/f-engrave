from time import time
from math import ceil, fabs, floor, sqrt, tan

from util import fmessage
from geometry import *
from geometry.pathsorter import sort_paths

from writers import douglas


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
                raise ValueError, 'Image stroke list is missing'
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

    def get_bbox(self):
        return self.bbox.tuple()

    def transform_scale(self, xscale, yscale):
        for XY in self.coords:
            XY[0] = XY[0] * xscale
            XY[1] = XY[1] * yscale
            XY[2] = XY[2] * xscale
            XY[3] = XY[3] * yscale
        self._set_bbox()

    def transform_flip(self):
        for XY in self.coords:
            XY[1] = -XY[1]
            XY[3] = -XY[3]
        self._set_bbox()

    def transform_mirror(self):
        for XY in self.coords:
            XY[0] = -XY[0]
            XY[2] = -XY[2]
        self._set_bbox()

    def transform_angle(self, angle):

        maxr = 0

        for XY in self.coords:

            if angle != 0.0:
                XY[0], XY[1], A1 = rotation(XY[0], XY[1], angle, 0)
                XY[2], XY[3], A2 = rotation(XY[2], XY[3], angle, 0)

            maxr = max(maxr, float(XY[0]*XY[0]+XY[1]*XY[1]), float(XY[2]*XY[2]+XY[3]*XY[3]))

        self._set_bbox()

        return maxr

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

        # TODO handle unicode string
        self.text = u''
        self.nrlines = 0
        self.line_max_vals = []

        # Keys of characters, if any, that were not found in the font set
        self.no_font_record = []

        self.line_space = 1.1  # TODO set LSPACE
        self.char_space = 25   # TODO set CSPACE
        self.word_space = 1.0  # TODO set WSPACE

        self.radius = 0.0
        self.angle = 0.0
        self.thickness = 0.25

    def __str__(self):
        ascii_text = self.text.encode('ascii','replace')
        return ascii_text

    def set_font(self, font):
        self.font = font

    def set_text(self, text):
        self.text = text

    def set_angle(self, angle):
        self.angle = angle

    def set_radius(self, radius):
        self.radius = radius

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

        font_line_space = (font_line_height - font_line_depth + self.thickness ) * self.line_space
        font_word_space = font_char_width * (self.word_space / 100.0)
        font_char_space = font_char_width * (self.char_space /100.0)

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
                null = self.font[ord(char)].get_ymax()
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
        self.nrlines = line_cnt

        self.line_max_vals = line_max_vals
        self._set_bbox()

    def align(self, alignment):

        line_minx = []
        line_maxx = []
        line_miny = []
        line_maxy = []
        for max_vals in self.line_max_vals:
            line_minx.append( max_vals[0] )
            line_maxx.append( max_vals[1] )
            line_miny.append( max_vals[2] )
            line_maxy.append( max_vals[3] )

        minx, maxx, miny, maxy = self.get_bbox()

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
        minx, maxx, miny, maxy = self.get_bbox()

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


# TODO cutter tool objects

class Tool(object):

    def __init__(self):
        self.diameter = 0.0
        self.radius = 0.0

    def set_diameter(self, diameter):
        self.diameter = diameter
        self.radius = diameter / 2

    def set_radius(self, radius):
        self.radius = radius

    def get_type(self):
        return 'None'


class Straight(Tool):

    def __init__(self):
        super(Tool, self).__init__()

    def get_type(self):
        return 'Straight'


class VCarve(Tool):

    def __init__(self):
        super(Tool, self).__init__()

    def get_type(self):
        return 'V-Bit'


class Engrave(object):
    """
    Generate toolpaths
    """
    def __init__(self, settings, image=None):

        self.progress_callback = None
        self.plot_progress_callback = None
        self.status_callback = None

        self.settings = settings
        self.image = image

        self.init_coords()

        self.accuracy = self.settings.get('accuracy')
        self.v_pplot = self.settings.get('v_pplot')
        self.STOP_CALC = False

    def init_coords(self):
        # Path coords format: ([x1, y1, x2, y2, line_cnt, char_cnt]) ?
        if self.image is None:
            self.coords = []
        else:
            self.coords = self.image.coords
        self.vcoords = []
        self.init_clean_coords()

    def init_clean_coords(self):
        # Clean coords format: ([xnormv, ynormv, rout, loop_cnt])
        self.clean_coords = []
        self.clean_coords_sort = []
        self.v_clean_coords_sort = []
        self.clean_segment = []

    def stop_calc(self):
        self.STOP_CALC = True

    def set_image(self, image):
        self.image = image
        self.init_coords()

    def set_coords(self, coords):
        self.coords = coords

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def set_plot_progress_callback(self, callback):
        self.plot_progress_callback = callback

    def set_status_callback(self, callback):
        self.status_callback = callback

    def refresh_v_pplot(self):
        self.v_pplot = self.settings.get('v_pplot')

    def number_of_clean_segments(self):
        return len(self.clean_segment)

    def number_of_v_coords(self):
        return len(self.vcoords)

    def number_of_clean_coords(self):
        return len(self.clean_coords)

    def number_of_clean_coords_sort(self):
        return len(self.clean_coords_sort)

    def number_of_v_clean_coords_sort(self):
        return len(self.v_clean_coords_sort)

    def number_of_segments(self):
        return len(self.coords)

    def get_segments_length(self, i_x1, i_y1, i_x2, i_y2, clean):

        total_length = 0.0

        # determine the total length of segments
        for idx, line in enumerate(self.coords):
            x1 = line[i_x1]
            y1 = line[i_y1]
            x2 = line[i_x2]
            y2 = line[i_y2]
            length = sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
            if clean:
                if self.clean_segment[idx] != 0:
                    total_length += length
            else:
                total_length += length

        return total_length

    def v_carve(self, clean=False):

        rbit = self.calc_vbit_radius()
        dline = self.settings.get('v_step_len')
        clean_dia = self.settings.get('clean_dia')
        if clean:
            rmax = rbit + clean_dia / 2
        else:
            rmax = rbit

        # TODO Extracted code, to be further refactored
        xN, xPartitionLength, yN, yPartitionLength = self.setup_grid_partitions(dline, rmax)

        # TODO Extracted code, to be further refactored
        self.determine_active_partitions(rmax, xN, xPartitionLength, yN, yPartitionLength)

        # Update GUI with the modified toolpath
        if not self.progress_callback is None:
            self.progress_callback()

        return self.make_vcarve_toolpath(clean, dline, rbit, rmax)

    def make_vcarve_toolpath(self, clean, dline, rbit, rmax):

        # set variable for first point in loop
        xa = 9999
        ya = 9999
        xb = 9999
        yb = 9999

        # set variable for the point previously calculated in a loop
        x0 = 9999
        y0 = 9999
        seg_sin0 = 2
        seg_cos0 = 2
        char_num0 = -1
        theta = 9999.0
        loop_cnt = 0  # the number of loops in this model

        v_flop = self.get_flop_status(clean)
        if v_flop:
            v_inc = -1
            v_index = self.number_of_segments()
            i_x1 = 2
            i_y1 = 3
            i_x2 = 0
            i_y2 = 1
        else:
            v_inc = 1
            v_index = -1
            i_x1 = 0
            i_y1 = 1
            i_x2 = 2
            i_y2 = 3

        not_b_carve = not bool(self.settings.get('bit_shape') == "BALL")
        CHK_STRING = self.settings.get('v_check_all')
        # TODO has CHK_STRING not been set before, else add set check in settings
        if self.settings.get('input_type') != "text":
            CHK_STRING = "all"

        bit_angle = self.settings.get('v_bit_angle')

        dangle = degrees(dline / rbit)
        if dangle < 2.0:
            dangle = 2.0

        v_step_corner = self.settings.get('v_step_corner')
        if self.settings.get('inlay'):
            v_drv_corner = 360 - v_step_corner
        else:
            v_drv_corner = self.settings.get('v_drv_corner')

        TOT_LENGTH = self.get_segments_length(i_x1, i_y1, i_x2, i_y2, clean)
        CUR_LENGTH = 0.0
        START_TIME = time()

        done = True

        if TOT_LENGTH > 0.0:

            calc_flag = 1

            for curr in range(self.number_of_segments()):

                if not clean:
                    self.clean_segment.append(0)
                elif self.number_of_clean_segments() == self.number_of_segments():
                    calc_flag = self.clean_segment[curr]
                else:
                    fmessage('Need to Recalculate V-Carve Path')
                    done = False
                    break

                CUR_PCT = float(CUR_LENGTH) / TOT_LENGTH * 100.0
                if CUR_PCT > 0.0:
                    MIN_REMAIN = (time() - START_TIME) / 60 * (100 - CUR_PCT) / CUR_PCT
                    MIN_TOTAL = 100.0 / CUR_PCT * (time() - START_TIME) / 60
                else:
                    MIN_REMAIN = -1
                    MIN_TOTAL = -1

                if not self.status_callback is None:
                    self.status_callback(
                        '%.1f %% ( %.1f Minutes Remaining | %.1f Minutes Total )' % (CUR_PCT, MIN_REMAIN, MIN_TOTAL))

                if self.STOP_CALC:
                    self.STOP_CALC = False
                    if clean:
                        self.clean_coords = []
                        calc_flag = 0
                    else:
                        self.vcoords = []
                    done = False
                    break

                v_index = v_index + v_inc
                New_Loop = 0
                x1 = self.coords[v_index][i_x1]
                y1 = self.coords[v_index][i_y1]
                x2 = self.coords[v_index][i_x2]
                y2 = self.coords[v_index][i_y2]
                char_num = int(self.coords[v_index][5])
                dx = x2 - x1
                dy = y2 - y1
                Lseg = sqrt(dx * dx + dy * dy)

                if Lseg < Zero:  # was accuracy
                    continue

                # calculate the sin and cos of the coord transformation needed for
                # the distance calculations
                seg_sin = dy / Lseg
                seg_cos = -dx / Lseg
                phi = get_angle(seg_sin, seg_cos)

                if calc_flag != 0:
                    CUR_LENGTH = CUR_LENGTH + Lseg
                else:
                    # theta = phi         #V1.62
                    # x0=x2               #V1.62
                    # y0=y2               #V1.62
                    # seg_sin0=seg_sin    #V1.62
                    # seg_cos0=seg_cos    #V1.62
                    # char_num0=char_num  #V1.62
                    continue

                if fabs(x1 - x0) > Zero or fabs(y1 - y0) > Zero or char_num != char_num0:
                    New_Loop = 1
                    loop_cnt += 1
                    xa = float(x1)
                    ya = float(y1)
                    xb = float(x2)
                    yb = float(y2)
                    theta = 9999.0
                    seg_sin0 = 2
                    seg_cos0 = 2

                if seg_cos0 > 1.0:
                    delta = 180
                else:
                    xtmp1 = (x2 - x1) * seg_cos0 - (y2 - y1) * seg_sin0
                    ytmp1 = (x2 - x1) * seg_sin0 + (y2 - y1) * seg_cos0
                    Ltmp = sqrt(xtmp1 * xtmp1 + ytmp1 * ytmp1)
                    d_seg_sin = ytmp1 / Ltmp
                    d_seg_cos = xtmp1 / Ltmp
                    delta = get_angle(d_seg_sin, d_seg_cos)

                if delta < v_drv_corner and bit_angle != 0 and not_b_carve and not clean:
                    # drive to corner
                    self.vcoords.append([x1, y1, 0.0, loop_cnt])

                if delta > float(v_step_corner):
                    ###########################
                    # add sub-steps around corner
                    ###########################
                    phisteps = max(floor((delta - 180) / dangle), 2)
                    step_phi = (delta - 180) / phisteps
                    pcnt = 0
                    while pcnt < phisteps - 1:
                        pcnt = pcnt + 1
                        sub_phi = radians(-pcnt * step_phi + theta)
                        sub_seg_cos = cos(sub_phi)
                        sub_seg_sin = sin(sub_phi)

                        rout = self.find_max_circle(x1, y1, rmax, char_num, sub_seg_sin, sub_seg_cos, 1, CHK_STRING)
                        normv, rv, clean_seg = self.record_v_carve_data(x1, y1, sub_phi, rout, loop_cnt, clean)
                        self.clean_segment[curr] = bool(self.clean_segment[curr]) or bool(clean_seg)

                        if self.v_pplot and (not self.plot_progress_callback is None) and (not clean):
                            self.plot_progress_callback(normv, "blue", rv, 0)

                theta = phi
                x0 = x2
                y0 = y2
                seg_sin0 = seg_sin
                seg_cos0 = seg_cos
                char_num0 = char_num

                # Calculate the number of steps, then dx and dy for each step.
                # Don't calculate at the joints.
                nsteps = max(floor(Lseg / dline), 2)
                dxpt = dx / nsteps
                dypt = dy / nsteps

                # this makes sure the first cut start at the begining of the first segment
                cnt = 0
                if New_Loop == 1 and bit_angle != 0 and not_b_carve:
                    cnt = -1

                seg_sin = dy / Lseg
                seg_cos = -dx / Lseg
                phi2 = radians(get_angle(seg_sin, seg_cos))
                while cnt < nsteps - 1:
                    cnt += 1
                    # determine location of next step along outline (xpt, ypt)
                    xpt = x1 + dxpt * cnt
                    ypt = y1 + dypt * cnt

                    rout = self.find_max_circle(xpt, ypt, rmax, char_num, seg_sin, seg_cos, 0, CHK_STRING)
                    # make the first cut drive down at an angle instead of straight down plunge
                    if cnt == 0 and not_b_carve:
                        rout = 0.0
                    normv, rv, clean_seg = self.record_v_carve_data(xpt, ypt, phi2, rout, loop_cnt, clean)
                    self.clean_segment[curr] = bool(self.clean_segment[curr]) or bool(clean_seg)

                    if self.v_pplot and (not self.plot_progress_callback is None) and (not clean):
                        self.plot_progress_callback(normv, "blue", rv, 0)

                    if New_Loop == 1 and cnt == 1:
                        xpta = xpt
                        ypta = ypt
                        phi2a = phi2
                        routa = rout

                #################################################
                # Check to see if we need to close an open loop
                #################################################
                if abs(x2 - xa) < self.accuracy and abs(y2 - ya) < self.accuracy:
                    xtmp1 = (xb - xa) * seg_cos0 - (yb - ya) * seg_sin0
                    ytmp1 = (xb - xa) * seg_sin0 + (yb - ya) * seg_cos0
                    Ltmp = sqrt(xtmp1 * xtmp1 + ytmp1 * ytmp1)
                    d_seg_sin = ytmp1 / Ltmp
                    d_seg_cos = xtmp1 / Ltmp
                    delta = get_angle(d_seg_sin, d_seg_cos)
                    if delta < v_drv_corner and not clean:
                        # drive to corner
                        self.vcoords.append([xa, ya, 0.0, loop_cnt])

                    elif delta > v_step_corner:
                        # add substeps around corner
                        phisteps = max(floor((delta - 180) / dangle), 2)
                        step_phi = (delta - 180) / phisteps
                        pcnt = 0

                        while pcnt < phisteps - 1:
                            pcnt = pcnt + 1
                            sub_phi = radians(-pcnt * step_phi + theta)
                            sub_seg_cos = cos(sub_phi)
                            sub_seg_sin = sin(sub_phi)

                            rout = self.find_max_circle(xa, ya, rmax, char_num, sub_seg_sin, sub_seg_cos, 1, CHK_STRING)
                            normv, rv, clean_seg = self.record_v_carve_data(xa, ya, sub_phi, rout, loop_cnt, clean)
                            self.clean_segment[curr] = bool(self.clean_segment[curr]) or bool(clean_seg)

                            if self.v_pplot and (not self.plot_progress_callback is None) and (not clean):
                                self.plot_progress_callback(normv, "blue", rv, 0)

                        normv, rv, clean_seg = self.record_v_carve_data(xpta, ypta, phi2a, routa, loop_cnt, clean)
                        self.clean_segment[curr] = bool(self.clean_segment[curr]) or bool(clean_seg)

                    else:
                        # add closing segment
                        normv, rv, clean_seg = self.record_v_carve_data(xpta, ypta, phi2a, routa, loop_cnt, clean)
                        self.clean_segment[curr] = bool(self.clean_segment[curr]) or bool(clean_seg)
        return done

    def determine_active_partitions(self, rmax, xN, xPartitionLength, yN, yPartitionLength):
        """
        Determine active paritions for each line segment
        """
        for curr, coords in enumerate(self.coords):

            XY_R = self.coords[curr][:]
            x1_R = XY_R[0]
            y1_R = XY_R[1]
            x2_R = XY_R[2]
            y2_R = XY_R[3]
            length = sqrt((x2_R - x1_R) * (x2_R - x1_R) + (y2_R - y1_R) * (y2_R - y1_R))

            R_R = length / 2 + rmax
            X_R = (x1_R + x2_R) / 2
            Y_R = (y1_R + y2_R) / 2

            coded_index = []

            # find the local coordinates of the line segment ends
            minx, maxx, miny, maxy = self.image.get_bbox()
            x1_G = XY_R[0] - minx
            y1_G = XY_R[1] - miny
            x2_G = XY_R[2] - minx
            y2_G = XY_R[3] - miny

            # find the grid box index for each line segment end
            X1i = int(x1_G / xPartitionLength)
            X2i = int(x2_G / xPartitionLength)
            Y1i = int(y1_G / yPartitionLength)
            Y2i = int(y2_G / yPartitionLength)

            # find the max/min grid box locations
            Xindex_min = min(X1i, X2i)
            Xindex_max = max(X1i, X2i)
            Yindex_min = min(Y1i, Y2i)
            Yindex_max = max(Y1i, Y2i)

            check_points = []
            if Xindex_max > Xindex_min and abs(x2_G - x1_G) > Zero:

                if Yindex_max > Yindex_min and abs(y2_G - y1_G) > Zero:
                    check_points.append([X1i, Y1i])
                    check_points.append([X2i, Y2i])

                    # Establish line equation variables: y=m*x+b
                    m_G = (y2_G - y1_G) / (x2_G - x1_G)
                    b_G = y1_G - m_G * x1_G

                    # Add check point in each partition in the range of X values
                    x_ind_check = Xindex_min + 1
                    while x_ind_check <= Xindex_max - 1:
                        x_val = x_ind_check * xPartitionLength
                        y_val = m_G * x_val + b_G
                        y_ind_check = int(y_val / yPartitionLength)
                        check_points.append([x_ind_check, y_ind_check])
                        x_ind_check = x_ind_check + 1

                    # Add check point in each partition in the range of Y values
                    y_ind_check = Yindex_min + 1
                    while y_ind_check <= Yindex_max - 1:
                        y_val = y_ind_check * yPartitionLength
                        x_val = (y_val - b_G) / m_G
                        x_ind_check = int(x_val / xPartitionLength)
                        check_points.append([x_ind_check, y_ind_check])
                        y_ind_check = y_ind_check + 1
                else:
                    x_ind_check = Xindex_min
                    y_ind_check = Yindex_min
                    while x_ind_check <= Xindex_max:
                        check_points.append([x_ind_check, y_ind_check])
                        x_ind_check = x_ind_check + 1
            else:
                x_ind_check = Xindex_min
                y_ind_check = Yindex_min
                while y_ind_check <= Yindex_max:
                    check_points.append([x_ind_check, y_ind_check])
                    y_ind_check = y_ind_check + 1

            #  For each grid box in check_points add the grid box and all adjacent grid boxes
            #  to the list of boxes for this line segment
            for xy_point in check_points:
                xy_p = xy_point
                xIndex = xy_p[0]
                yIndex = xy_p[1]
                for i in range(max(xIndex - 1, 0), min(xN, xIndex + 2)):
                    for j in range(max(yIndex - 1, 0), min(yN, yIndex + 2)):
                        coded_index.append(int(i + j * xN))

            codedIndexSet = set(coded_index)

            for thisCode in codedIndexSet:
                thisIndex = thisCode
                line_R_appended = XY_R
                line_R_appended.append(X_R)
                line_R_appended.append(Y_R)
                line_R_appended.append(R_R)
                self.partitionList[int(thisIndex % xN)][int(thisIndex / xN)].append(line_R_appended)

        return

    def setup_grid_partitions(self, dline, rmax):
        """
        Setup Grid Partitions for the cleaning toolpath
        """
        minx, maxx, miny, maxy = self.image.get_bbox()
        xLength = maxx - minx
        yLength = maxy - miny

        xN_minus_1 = max(int(xLength / ((2 * rmax + dline) * 1.1)), 1)
        yN_minus_1 = max(int(yLength / ((2 * rmax + dline) * 1.1)), 1)

        xPartitionLength = xLength / xN_minus_1
        yPartitionLength = yLength / yN_minus_1

        xN = xN_minus_1 + 1
        yN = yN_minus_1 + 1

        if xPartitionLength < Zero:
            xPartitionLength = 1

        if yPartitionLength < Zero:
            yPartitionLength = 1

        self.xPartitionLength = xPartitionLength
        self.yPartitionLength = yPartitionLength

        self.partitionList = []
        for xCount in range(0, xN):
            self.partitionList.append([])
            for yCount in range(0, yN):
                self.partitionList[xCount].append([])

        return xN, xPartitionLength, yN, yPartitionLength


    # TODO optimize (now vbit radius calc is within a loop)

    def record_v_carve_data(self, x1, y1, phi, rout, loop_cnt, clean):

        rbit = self.calc_vbit_radius()

        Lx, Ly = transform(0, rout, -phi)
        xnormv = x1 + Lx
        ynormv = y1 + Ly

        need_clean = 0
        if clean:
            if rout >= rbit:
                self.clean_coords.append([xnormv, ynormv, rout, loop_cnt])
        else:
            self.vcoords.append([xnormv, ynormv, rout, loop_cnt])
            if abs(rbit - rout) <= Zero:
                need_clean = 1

        return (xnormv, ynormv), rout, need_clean

    def calc_vbit_radius(self):
        """
        Calculate the V-Bit radius
        """
        vbit_dia = self.settings.get('v_bit_dia')
        depth_lim = self.settings.get('v_depth_lim')
        half_angle = radians(self.settings.get('v_bit_angle') / 2.0)

        if self.settings.get('inlay') and self.settings.get('bit_shape') == "VBIT":
            allowance = self.settings.get('allowance')
            vbit_dia = -2 * allowance * tan(half_angle)
            vbit_dia = max(vbit_dia, 0.001)
        else:
            if depth_lim < 0.0:
                if self.settings.get('bit_shape') == "VBIT":
                    vbit_dia = -2 * depth_lim * tan(half_angle)

                elif self.settings.get('bit_shape') == "BALL":
                    R = vbit_dia / 2.0
                    if depth_lim > -R:
                        vbit_dia = 2 * sqrt(R ** 2 - (R + depth_lim) ** 2)
                    else:
                        pass

                elif self.settings.get('bit_shape') == "FLAT":
                    # R = vbit_dia / 2.0
                    pass

                else:
                    pass

        return vbit_dia / 2

    def find_max_circle(self, xpt, ypt, rmin, char_num, seg_sin, seg_cos, corner, CHK_STRING):
        """
        Routine finds the maximum radius that can be placed in the position
        xpt,ypt without interfering with other line segments (rmin is max R LOL)
        """
        rtmp = rmin

        # TODO make x/yPartitionLength function parameters
        minx, maxx, miny, maxy = self.image.get_bbox()
        xIndex = int((xpt - minx) / self.xPartitionLength)
        yIndex = int((ypt - miny) / self.yPartitionLength)

        coords_check= []

        R_A = abs(rmin)
        Bcnt = -1

        ############################################################
        # Loop over active partitions for the current line segment #
        ############################################################
        for line_B in self.partitionList[xIndex][yIndex]:
            Bcnt = Bcnt + 1
            X_B = line_B[len(line_B) - 3]
            Y_B = line_B[len(line_B) - 2]
            R_B = line_B[len(line_B) - 1]
            gap = sqrt((X_B - xpt) * (X_B - xpt) + (Y_B - ypt) * (Y_B - ypt))
            if gap < abs(R_A + R_B):
                coords_check.append(line_B)

        for linec in coords_check:
            XYc = linec
            xmaxt = max(XYc[0], XYc[2]) + rmin * 2
            xmint = min(XYc[0], XYc[2]) - rmin * 2
            ymaxt = max(XYc[1], XYc[3]) + rmin * 2
            ymint = min(XYc[1], XYc[3]) - rmin * 2
            if xpt >= xmint and ypt >= ymint and xpt <= xmaxt and ypt <= ymaxt:
                logic_full = True
            else:
                logic_full = False
                continue

            if CHK_STRING == "chr":
                logic_full = logic_full and (char_num == int(XYc[5]))

            if corner == 1:
                logic_full = logic_full and \
                             ((fabs(xpt - XYc[0]) > Zero) or (fabs(ypt - XYc[1]) > Zero)) and \
                             ((fabs(xpt - XYc[2]) > Zero) or (fabs(ypt - XYc[3]) > Zero))

            if logic_full:
                xc1 = (XYc[0] - xpt) * seg_cos - (XYc[1] - ypt) * seg_sin
                yc1 = (XYc[0] - xpt) * seg_sin + (XYc[1] - ypt) * seg_cos
                xc2 = (XYc[2] - xpt) * seg_cos - (XYc[3] - ypt) * seg_sin
                yc2 = (XYc[2] - xpt) * seg_sin + (XYc[3] - ypt) * seg_cos

                if fabs(xc2 - xc1) < Zero and fabs(yc2 - yc1) > Zero:
                    rtmp = fabs(xc1)
                    if max(yc1, yc2) >= rtmp and min(yc1, yc2) <= rtmp:
                        rmin = min(rmin, rtmp)

                elif fabs(yc2 - yc1) < Zero and fabs(xc2 - xc1) > Zero:
                    if max(xc1, xc2) >= 0.0 and min(xc1, xc2) <= 0.0 and yc1 > Zero:
                        rtmp = yc1 / 2.0
                        rmin = min(rmin, rtmp)

                if fabs(yc2 - yc1) > Zero and fabs(xc2 - xc1) > Zero:
                    m = (yc2 - yc1) / (xc2 - xc1)
                    b = yc1 - m * xc1
                    sq = m + 1 / m
                    A = 1 + m * m - 2 * m * sq
                    B = -2 * b * sq
                    C = -b * b
                    try:
                        sq_root = sqrt(B * B - 4 * A * C)
                        xq1 = (-B + sq_root) / (2 * A)

                        if xq1 >= min(xc1, xc2) and xq1 <= max(xc1, xc2):
                            rtmp = xq1 * sq + b
                            if rtmp >= 0.0:
                                rmin = min(rmin, rtmp)

                        xq2 = (-B - sq_root) / (2 * A)
                        yq2 = m * xq2 + b

                        if xq2 >= min(xc1, xc2) and xq2 <= max(xc1, xc2):
                            rtmp = xq2 * sq + b
                            if rtmp >= 0.0:
                                rmin = min(rmin, rtmp)
                    except:
                        pass

                if yc1 > Zero:
                    rtmp = (xc1 * xc1 + yc1 * yc1) / (2 * yc1)
                    rmin = min(rmin, rtmp)

                if yc2 > Zero:
                    rtmp = (xc2 * xc2 + yc2 * yc2) / (2 * yc2)
                    rmin = min(rmin, rtmp)

                if abs(yc1) < Zero and abs(xc1) < Zero:
                    if yc2 > Zero:
                        rmin = 0.0

                if abs(yc2) < Zero and abs(xc2) < Zero:
                    if yc1 > Zero:
                        rmin = 0.0

        return rmin

    # TODO Do not change the self.coords object, use intermediate, preferably not a deep copy...

    def sort_for_v_carve(self, LN_START=0):
        self.coords = self._sort_for_v_carve(self.coords, LN_START)

    def _sort_for_v_carve(self, sort_coords, LN_START):

        ecoords = []
        Lbeg = []
        Lend = []
        cnt = 0

        for i in range(len(sort_coords)):

            [x1, y1, x2, y2, dummy1, dummy2] = sort_coords[i]

            if i == 0:
                cnt = 0
                ecoords.append([x1, y1])
                Lbeg.append(cnt)
                cnt = cnt + 1
                ecoords.append([x2, y2])
                oldx, oldy = x2, y2
            else:
                dist = sqrt((oldx - x1) ** 2 + (oldy - y1) ** 2)
                # check and see if we need to move
                # to a new discontinuous start point
                if dist > Zero:
                    Lend.append(cnt)
                    cnt = cnt + 1
                    ecoords.append([x1, y1])
                    Lbeg.append(cnt)
                cnt += 1
                ecoords.append([x2, y2])
                oldx, oldy = x2, y2

        Lend.append(cnt)

        if not self.status_callback is None:
            self.status_callback('Checking Input Image Data')

        ######################################################
        ### Fully Close Closed loops and Remove Open Loops ###
        ######################################################
        i = 0
        LObeg = []
        LOend = []
        while i < len(Lbeg):  # for each loop
            [Xstart, Ystart] = ecoords[Lbeg[i]]
            [Xend, Yend] = ecoords[Lend[i]]
            dist = sqrt((Xend - Xstart) ** 2 + (Yend - Ystart) ** 2)
            if dist <= Zero:  # if end is the same as the beginning (changed in V1.55: was Acc)
                ecoords[Lend[i]] = [Xstart, Ystart]
                i += 1
            else:  # end != to beginning
                LObeg.append(Lbeg.pop(i))
                LOend.append(Lend.pop(i))

        LNbeg = []
        LNend = []
        LNloop = []

        #######################################################
        ###  For Each open loop connect to the next closest ###
        ###  loop end until all of the loops are closed     ###
        #######################################################
        Lcnt = 0
        while len(LObeg) > 0:  # for each Open Loop
            Start = LObeg.pop(0)
            End = LOend.pop(0)
            Lcnt += 1
            LNloop.append(Lcnt)
            LNbeg.append(Start)
            LNend.append(End)
            [Xstart, Ystart] = ecoords[Start]

            OPEN = True
            while OPEN == True and len(LObeg) > 0:
                [Xend, Yend] = ecoords[End]
                dist_beg_min = sqrt((Xend - Xstart) ** 2 + (Yend - Ystart) ** 2)
                dist_end_min = dist_beg_min
                k_min_beg = -1
                k_min_end = -1
                for k in range(len(LObeg)):
                    [Xkstart, Ykstart] = ecoords[LObeg[k]]
                    [Xkend, Ykend] = ecoords[LOend[k]]
                    dist_beg = sqrt((Xend - Xkstart) ** 2 + (Yend - Ykstart) ** 2)
                    dist_end = sqrt((Xend - Xkend) ** 2 + (Yend - Ykend) ** 2)
                    if dist_beg < dist_beg_min:
                        dist_beg_min = dist_beg
                        k_min_beg = k
                    if dist_end < dist_end_min:
                        dist_end_min = dist_end
                        k_min_end = k

                if k_min_beg == -1 and k_min_end == -1:
                    ecoords.append(ecoords[End])
                    ecoords.append(ecoords[Start])

                    LNloop.append(Lcnt)
                    LNbeg.append(len(ecoords) - 2)
                    LNend.append(len(ecoords) - 1)
                    OPEN = False
                elif dist_end_min < dist_beg_min:
                    kend = LObeg.pop(k_min_end)
                    kbeg = LOend.pop(k_min_end)

                    ecoords.append(ecoords[End])
                    ecoords.append(ecoords[kbeg])

                    LNloop.append(Lcnt)
                    LNbeg.append(len(ecoords) - 2)
                    LNend.append(len(ecoords) - 1)
                    LNloop.append(Lcnt)
                    LNbeg.append(kbeg)
                    LNend.append(kend)
                    End = kend
                else:
                    kbeg = LObeg.pop(k_min_beg)
                    kend = LOend.pop(k_min_beg)

                    ecoords.append(ecoords[End])
                    ecoords.append(ecoords[kbeg])

                    LNloop.append(Lcnt)
                    LNbeg.append(len(ecoords) - 2)
                    LNend.append(len(ecoords) - 1)
                    LNloop.append(Lcnt)
                    LNbeg.append(kbeg)
                    LNend.append(kend)
                    End = kend

            if OPEN and len(LObeg) == 0:
                ecoords.append(ecoords[End])
                ecoords.append(ecoords[Start])
                LNloop.append(Lcnt)
                LNbeg.append(len(ecoords) - 2)
                LNend.append(len(ecoords) - 1)

        #######################################################
        ### Make new sequential ecoords for each new loop   ###
        #######################################################
        Loop_last = -1
        for k in range(len(LNbeg)):
            Start = LNbeg[k]
            End = LNend[k]
            Loop = LNloop[k]
            if Loop != Loop_last:
                Lbeg.append(len(ecoords))
                if Loop_last != -1:
                    Lend.append(len(ecoords) - 1)
                Loop_last = Loop

            if Start > End:
                step = -1
            else:
                step = 1
            for i in range(Start, End+step, step):
                [x1, y1] = ecoords[i]
                ecoords.append([x1, y1])
        if len(Lbeg) > len(Lend):
            Lend.append(len(ecoords) - 1)

        ###########################################
        ###   Determine loop directions CW/CCW  ###
        ###########################################
        if not self.status_callback is None:
            self.status_callback('Calculating Initial Loop Directions (CW/CCW)')

        Lflip = [] # normvector direction in (False) or out (True) for loopsegment [i]
        Lcw = []   # loop direction clockwise (True) or counterclockwise for loopsegment [i]

        for k in range(len(Lbeg)):
            Start = Lbeg[k]
            End = Lend[k]
            step = 1

            signedArea = 0.0

            [x1, y1] = ecoords[Start]
            for i in range(Start+1, End+step, step):
                [x2, y2] = ecoords[i]
                signedArea += (x2 - x1) * (y2 + y1)
                x1 = x2
                y1 = y2
            if signedArea > 0.0:
                Lflip.append(False)
                Lcw.append(True)
            else:
                Lflip.append(True)
                Lcw.append(False)

        Nloops = len(Lbeg)
        LoopTree = []
        Lnum = []

        for iloop in range(LN_START, Nloops + LN_START):
            LoopTree.append([iloop, [], []])
            Lnum.append(iloop)

        #####################################################
        # For each loop determine if other loops are inside #
        #####################################################
        for iloop in range(Nloops):

            if not self.status_callback is None:
                self.status_callback('Determining Which Side of Loop to Cut: %d of %d' % (iloop + 1, Nloops))

            ipoly = ecoords[Lbeg[iloop]:Lend[iloop]]

            # Check points in other loops (could just check one)
            if ipoly != []:
                for jloop in range(Nloops):
                    if jloop != iloop:
                        inside = 0
                        jval = Lbeg[jloop]
                        inside = inside + point_inside_polygon(ecoords[jval][0], ecoords[jval][1], ipoly)
                        if inside > 0:
                            Lflip[jloop] = not Lflip[jloop]
                            LoopTree[iloop][1].append(jloop)
                            LoopTree[jloop][2].append(iloop)

        #####################################################
        # Set Loop clockwise flag to the state of each loop #
        #####################################################
        # could flip cut side here for auto side determination
        for iloop in range(Nloops):
            if Lflip[iloop]:
                Lcw[iloop] = not Lcw[iloop]

        #################################################
        # Find new order based on distance to next beg  #
        #################################################
        if not self.status_callback is None:
            self.status_callback('Re-Ordering Loops')

        order_out = []
        if len(Lflip) > 0:
            if Lflip[0]:
                order_out.append([Lend[0], Lbeg[0], Lnum[0]])
            else:
                order_out.append([Lbeg[0], Lend[0], Lnum[0]])

        inext = 0
        total = len(Lbeg)
        for i in range(total - 1):
            Lbeg.pop(inext)
            ii = Lend.pop(inext)
            Lflip.pop(inext)
            Lnum.pop(inext)

            Xcur = ecoords[ii][0]
            Ycur = ecoords[ii][1]

            dx = Xcur - ecoords[Lbeg[0]][0]
            dy = Ycur - ecoords[Lbeg[0]][1]
            min_dist = dx * dx + dy * dy

            inext = 0
            for j in range(1, len(Lbeg)):
                dx = Xcur - ecoords[Lbeg[j]][0]
                dy = Ycur - ecoords[Lbeg[j]][1]
                dist = dx * dx + dy * dy
                if dist < min_dist:
                    min_dist = dist
                    inext = j

            if Lflip[inext]:
                order_out.append([Lend[inext], Lbeg[inext], Lnum[inext]])
            else:
                order_out.append([Lbeg[inext], Lend[inext], Lnum[inext]])

        ###########################################################
        temp_coords = []
        for k in range(len(order_out)):
            [Start, End, LN] = order_out[k]
            if Start > End:
                step = -1
            else:
                step = 1
            xlast = ""
            ylast = ""
            xa, ya = ecoords[Start]
            for i in range(Start + step, End + step, step):
                if xlast != "" and ylast != "":
                    x1 = xlast
                    y1 = ylast
                else:
                    [x1, y1] = ecoords[i - step]
                [x2, y2] = ecoords[i]

                Lseg = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if Lseg >= self.accuracy:
                    temp_coords.append([x1, y1, x2, y2, LN, 0])
                    xlast = ""
                    ylast = ""
                else:
                    xlast = x1
                    ylast = y1

            if xlast != "" and ylast != "":
                Llast = sqrt((x1 - xa) * (x1 - xa) + (y1 - ya) * (y1 - ya))
                if len(temp_coords) > 1:
                    if Llast <= self.accuracy and LN == temp_coords[-1][4]:
                        temp_coords[-1][2] = xa
                        temp_coords[-1][3] = ya
                    else:
                        temp_coords.append([x1, y1, xa, ya, LN, 0])
        return temp_coords

    def _find_paths(self, check_coords_in, clean_dia, Radjust, clean_step, skip, direction):

        check_coords = []

        if direction == "Y":
            cnt = -1
            for XY in check_coords_in:
                cnt += 1
                check_coords.append([XY[1], XY[0], XY[2]])
        else:
            check_coords = check_coords_in

        minx_c = 0
        maxx_c = 0
        miny_c = 0
        maxy_c = 0

        if len(check_coords) > 0:
            minx_c = check_coords[0][0] - check_coords[0][2]
            maxx_c = check_coords[0][0] + check_coords[0][2]
            miny_c = check_coords[0][1] - check_coords[0][2]
            maxy_c = check_coords[0][1] + check_coords[0][2]

        for XY in check_coords:
            minx_c = min(minx_c, XY[0] - XY[2])
            maxx_c = max(maxx_c, XY[0] + XY[2])
            miny_c = min(miny_c, XY[1] - XY[2])
            maxy_c = max(maxy_c, XY[1] + XY[2])

        DX = clean_dia * clean_step
        DY = DX
        Xclean_coords = []
        Xclean_coords_short = []

        if direction != "None":
            #########################################################################
            # Find ends of horizontal lines for carving clean-up
            #########################################################################
            loop_cnt = 0
            Y = miny_c
            line_cnt = skip - 1
            while Y <= maxy_c:
                line_cnt = line_cnt + 1
                X = minx_c
                x1 = X
                x2 = X
                x1_old = x1
                x2_old = x2

                # Find relevant clean_coord_data
                ################################
                temp_coords = []
                for line in check_coords:
                    XY = line
                    if Y < XY[1] + XY[2] and Y > XY[1] - XY[2]:
                        temp_coords.append(XY)
                ################################

                while X <= maxx_c:
                    for line in temp_coords:
                        XY = line
                        h = XY[0]
                        k = XY[1]
                        R = XY[2] - Radjust
                        dist = sqrt((X - h) ** 2 + (Y - k) ** 2)
                        if dist <= R:
                            Root = sqrt(R ** 2 - (Y - k) ** 2)
                            XL = h - Root
                            XR = h + Root
                            if XL < x1:
                                x1 = XL
                            if XR > x2:
                                x2 = XR
                    if x1 == x2:
                        X = X + DX
                        x1 = X
                        x2 = X
                    elif x1 == x1_old and x2 == x2_old:
                        loop_cnt += 1
                        Xclean_coords.append([x1, Y, loop_cnt])
                        Xclean_coords.append([x2, Y, loop_cnt])
                        if line_cnt == skip:
                            Xclean_coords_short.append([x1, Y, loop_cnt])
                            Xclean_coords_short.append([x2, Y, loop_cnt])

                        X = X + DX
                        x1 = X
                        x2 = X
                    else:
                        X = x2
                    x1_old = x1
                    x2_old = x2
                if line_cnt == skip:
                    line_cnt = 0
                Y = Y + DY

        Xclean_coords_out = []
        Xclean_coords_short_out = []

        if direction == "Y":
            cnt = -1
            for XY in Xclean_coords:
                cnt += 1
                Xclean_coords_out.append([XY[1], XY[0], XY[2]])
            cnt = -1
            for XY in Xclean_coords_short:
                cnt += 1
                Xclean_coords_short_out.append([XY[1], XY[0], XY[2]])
        else:
            Xclean_coords_out = Xclean_coords
            Xclean_coords_short_out = Xclean_coords_short

        return Xclean_coords_out, Xclean_coords_short_out

    def _clean_coords_to_path_coords(self, clean_coords_in):
        path_coords_out = []
        # Clean coords format ([xnormv, ynormv, rout, loop_cnt])      - self.clean_coords
        # Path coords format  ([x1, y1, x2, y2, line_cnt, char_cnt])  - self.coords
        for i in range(1, len(clean_coords_in)):
            if clean_coords_in[i][3] == clean_coords_in[i-1][3]:
                path_coords_out.append([clean_coords_in[i-1][0],
                                        clean_coords_in[i-1][1],
                                        clean_coords_in[i][0],
                                        clean_coords_in[i][1],
                                        0,
                                        0])
        return path_coords_out

    def clean_path_calc(self, bit_type="straight"):

        v_flop = self.get_flop_status(CLEAN=True)
        if v_flop:
            edge = 1
        else:
            edge = 0

        rbit = self.calc_vbit_radius()

        loop_cnt = 0
        loop_cnt_out = 0

        # reorganize clean_coords
        if bit_type == "straight":
            test_clean = self.settings.get('clean_P') + \
                         self.settings.get('clean_X') + \
                         self.settings.get('clean_Y')
        else:
            test_clean = self.settings.get('v_clean_P') + \
                         self.settings.get('v_clean_X') + \
                         self.settings.get('v_clean_Y')

        check_coords = []

        if bit_type == "straight":
            # self.controller.statusMessage.set('Calculating Cleanup Cut Paths')
            # self.controller.master.update()
            if not self.status_callback is None:
                self.status_callback('Calculating Cleanup Cut Paths')

            self.clean_coords_sort = []
            clean_dia = self.settings.get('clean_dia')  # diameter of cleanup bit
            v_step_len = self.settings.get('v_step_len')
            step_over = self.settings.get('clean_step')  # percent of cut DIA
            clean_step = step_over / 100.0
            Radjust = clean_dia / 2.0 + rbit
            check_coords = self.clean_coords

        elif bit_type == "v-bit":

            if not self.status_callback is None:
                self.status_callback('Calculating V-Bit Cleanup Cut Paths')

            # TODO What is being skipped?
            skip = 1
            clean_step = 1.0

            self.v_clean_coords_sort = []

            # effective diameter of clean-up v-bit
            clean_dia = self.settings.get('clean_dia')
            if float(clean_dia) < Zero:
                return

            # allow the cutter to get within 1/4 of the v-clean step of the v-carved surface
            offset = clean_dia / 4.0
            Radjust = rbit + offset
            flat_clean_r = self.settings.get('clean_dia') / 2.0
            for line in self.clean_coords:
                XY = line
                R = XY[2] - Radjust
                if R > 0.0 and R < flat_clean_r - offset - Zero:
                    check_coords.append(XY)

        if self.settings.get('cut_type') == "v-carve" and len(self.clean_coords) > 1 and test_clean > 0:
            DX = clean_dia * clean_step
            DY = DX

            if bit_type == "straight":
                MAXD = clean_dia
            else:
                MAXD = sqrt(DX ** 2 + DY ** 2) * 1.1  # fudge factor

            Xclean_coords = []
            Yclean_coords = []
            clean_coords_out = []

            if bit_type == "straight":
                clean_coords_out, loop_cnt_out = \
                    self.straight_toolpath(DX, Xclean_coords, Yclean_coords, clean_coords_out, edge, loop_cnt, loop_cnt_out, rbit)

            elif bit_type == "v-bit":
                Xclean_coords, Yclean_coords, loop_cnt_out = \
                    self.vbit_toolpath(MAXD, Radjust, Xclean_coords, Yclean_coords, check_coords, clean_coords_out, clean_dia, clean_step, loop_cnt_out, skip)

            # Now deal with the horizontal line cuts...
            if (self.settings.get('clean_X') == 1 and bit_type != "v-bit") or \
                    (self.settings.get('v_clean_X') == 1 and bit_type == "v-bit"):
                loop_cnt_out = self.line_cuts(MAXD, Xclean_coords, clean_coords_out, clean_dia, loop_cnt_out)

            # ...and deal with the vertical line cuts
            if (self.settings.get('clean_Y') == 1 and bit_type != "v-bit") or \
                    (self.settings.get('v_clean_Y') == 1 and bit_type == "v-bit"):
                null = self.line_cuts(MAXD, Yclean_coords, clean_coords_out, clean_dia, loop_cnt_out)

            # TODO move to controller
            # self.controller.entry_set(self.controller.Entry_CLEAN_DIA, self.controller.Entry_CLEAN_DIA_Check(), 1)
            # self.controller.entry_set(self.controller.Entry_STEP_OVER, self.controller.Entry_STEP_OVER_Check(), 1)
            # self.controller.entry_set(self.controller.Entry_V_CLEAN, self.controller.Entry_V_CLEAN_Check(), 1)

            if bit_type == "v-bit":
                self.v_clean_coords_sort = clean_coords_out
            else:
                self.clean_coords_sort = clean_coords_out

        if not self.status_callback is None:
            self.status_callback('Done Calculating Cleanup Cut Paths', color='white')

    def line_cuts(self, MAXD, clean_coords, clean_coords_out, clean_dia, loop_cnt_out):

        x_old = -999
        y_old = -999

        order_out = sort_paths(clean_coords)

        loop_old = -1
        for line in order_out:

            if line[0] > line[1]:
                step = -1
            else:
                step = 1

            for i in range(line[0], line[1]+step, step):

                x1 = clean_coords[i][0]
                y1 = clean_coords[i][1]
                loop = clean_coords[i][2]

                dx = x1 - x_old
                dy = y1 - y_old
                dist = sqrt(dx * dx + dy * dy)

                if dist > MAXD and loop != loop_old:
                    loop_cnt_out += 1

                clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])

                x_old = x1
                y_old = y1
                loop_old = loop

        return loop_cnt_out

    def vbit_toolpath(self, MAXD, Radjust, Xclean_coords, Yclean_coords, check_coords, clean_coords_out, clean_dia,
                      clean_step, loop_cnt_out, skip):
        """
        Make V-Bit cutter toolpath
        Returns the X and Y clean_coordinates, and the number of loops
        """
        # Find ends of horizontal lines for carving clean-up
        Xclean_perimeter, Xclean_coords = \
            self._find_paths(check_coords, clean_dia, Radjust, clean_step, skip, "X")

        # Find ends of Vertical lines for carving clean-up
        Yclean_perimeter, Yclean_coords = \
            self._find_paths(check_coords, clean_dia, Radjust, clean_step, skip, "Y")

        # Find new order based on distance
        if self.settings.get('v_clean_P') == 1:

            ecoords = []
            for XY in Xclean_perimeter:
                ecoords.append([XY[0], XY[1]])

            for XY in Yclean_perimeter:
                ecoords.append([XY[0], XY[1]])

            # ends
            Lbeg = []
            for i in range(1, len(ecoords)):
                Lbeg.append(i)

            order_out = []
            if len(ecoords) > 0:
                order_out.append(Lbeg[0])
            inext = 0
            total = len(Lbeg)
            for i in range(total - 1):
                ii = Lbeg.pop(inext)
                Xcur = ecoords[ii][0]
                Ycur = ecoords[ii][1]
                dx = Xcur - ecoords[Lbeg[0]][0]
                dy = Ycur - ecoords[Lbeg[0]][1]
                min_dist = dx * dx + dy * dy

                inext = 0
                for j in range(1, len(Lbeg)):
                    dx = Xcur - ecoords[Lbeg[j]][0]
                    dy = Ycur - ecoords[Lbeg[j]][1]
                    dist = dx * dx + dy * dy
                    if dist < min_dist:
                        min_dist = dist
                        inext = j

                order_out.append(Lbeg[inext])

            x_start_loop = -8888
            y_start_loop = -8888
            x_old = -999
            y_old = -999
            for i in order_out:
                x1 = ecoords[i][0]
                y1 = ecoords[i][1]
                dx = x1 - x_old
                dy = y1 - y_old
                dist = sqrt(dx * dx + dy * dy)
                if dist > MAXD:
                    dx = x_start_loop - x_old
                    dy = y_start_loop - y_old
                    dist = sqrt(dx * dx + dy * dy)
                    # Fully close loop if the current point is close enough to the start of the loop
                    if dist < MAXD:
                        clean_coords_out.append([x_start_loop, y_start_loop, clean_dia / 2, loop_cnt_out])
                    loop_cnt_out = loop_cnt_out + 1
                    x_start_loop = x1
                    y_start_loop = y1
                clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])
                x_old = x1
                y_old = y1

        return Xclean_coords, Yclean_coords, loop_cnt_out

    def straight_toolpath(self, DX, Xclean_coords, Yclean_coords, clean_coords_out, edge, loop_cnt,
                          loop_cnt_out, rbit):
        """
        Make straight bit toolpath
        Returns the clean coordinates and the number of loops
        """
        MaxLoop = 0
        clean_dia = self.settings.get('clean_dia')  # diameter of cleanup bit
        step_over = self.settings.get('clean_step')  # percent of cut DIA
        clean_step = step_over / 100.0
        Rperimeter = rbit + (clean_dia / 2.0)

        # Extract straight bit points from clean_coords
        check_coords = []
        junk = -1
        for line in self.clean_coords:
            XY = line
            R = XY[2]
            if R >= Rperimeter - Zero:
                check_coords.append(XY)
            elif len(check_coords) > 0:
                junk = junk - 1
                check_coords.append([None, None, None, junk])
                # check_coords[len(check_coords)-1][3]=junk

        # Calculate Straight bit "Perimeter" tool path
        P_coords = []
        loop_coords = self._clean_coords_to_path_coords(check_coords)
        loop_coords = self._sort_for_v_carve(loop_coords, LN_START=0)

        # Line fit loop_coords
        if loop_coords:
            cuts = []
            Ln_last = loop_coords[0][4]
            for i in range(len(loop_coords)):
                Ln = loop_coords[i][4]
                if Ln != Ln_last:
                    for move, (x, y, z), cent in douglas(cuts, tolerance=0.0001, plane=None):
                        P_coords.append([x, y, clean_dia / 2, Ln_last])
                    cuts = []
                cuts.append([loop_coords[i][0], loop_coords[i][1], 0])
                cuts.append([loop_coords[i][2], loop_coords[i][3], 0])
                Ln_last = Ln
            if cuts:
                for move, (x, y, z), cent in douglas(cuts, tolerance=0.0001, plane=None):
                    P_coords.append([x, y, clean_dia / 2, Ln_last])

        loop_coords = self._clean_coords_to_path_coords(P_coords)

        # Find min/max values for x,y and the highest loop number
        x_pmin = 99999
        x_pmax = -99999
        y_pmin = 99999
        y_pmax = -99999
        for i in range(len(P_coords)):
            MaxLoop = max(MaxLoop, P_coords[i][3])
            x_pmin = min(x_pmin, P_coords[i][0])
            x_pmax = max(x_pmax, P_coords[i][0])
            y_pmin = min(y_pmin, P_coords[i][1])
            y_pmax = max(y_pmax, P_coords[i][1])

        loop_cnt_out = loop_cnt_out + MaxLoop

        if self.settings.get('clean_P') == 1:
            clean_coords_out = P_coords

        offset = DX / 2.0

        if self.settings.get('clean_X') == 1:
            y_pmax = y_pmax - offset
            y_pmin = y_pmin + offset
            Ysize = y_pmax - y_pmin
            Ysteps = ceil(Ysize / (clean_dia * clean_step))
            if Ysteps > 0:
                for iY in range(0, int(Ysteps + 1)):
                    y = y_pmin + iY / Ysteps * (y_pmax - y_pmin)
                    intXYlist = detect_intersect([x_pmin - 1, y], [x_pmax + 1, y], loop_coords, XY_T_F=True)
                    intXY_len = len(intXYlist)

                    for i in range(edge, intXY_len - 1 - edge, 2):
                        x1 = intXYlist[i][0]
                        y1 = intXYlist[i][1]
                        x2 = intXYlist[i + 1][0]
                        y2 = intXYlist[i + 1][1]
                        if x2 - x1 > offset * 2:
                            loop_cnt += 1
                            Xclean_coords.append([x1 + offset, y1, loop_cnt])
                            Xclean_coords.append([x2 - offset, y2, loop_cnt])

        if self.settings.get('clean_Y') == 1:
            x_pmax = x_pmax - offset
            x_pmin = x_pmin + offset
            Xsize = x_pmax - x_pmin
            Xsteps = ceil(Xsize / (clean_dia * clean_step))
            if Xsteps > 0:
                for iX in range(0, int(Xsteps + 1)):
                    x = x_pmin + iX / Xsteps * (x_pmax - x_pmin)
                    intXYlist = []
                    intXYlist = detect_intersect([x, y_pmin - 1], [x, y_pmax + 1], loop_coords, XY_T_F=True)
                    intXY_len = len(intXYlist)
                    for i in range(edge, intXY_len - 1 - edge, 2):
                        x1 = intXYlist[i][0]
                        y1 = intXYlist[i][1]
                        x2 = intXYlist[i + 1][0]
                        y2 = intXYlist[i + 1][1]
                        if y2 - y1 > offset * 2:
                            loop_cnt += 1
                            Yclean_coords.append([x1, y1 + offset, loop_cnt])
                            Yclean_coords.append([x2, y2 - offset, loop_cnt])

        return clean_coords_out, loop_cnt_out

    def get_flop_status(self, CLEAN=False):

        v_flop = self.settings.get('v_flop')

        if self.settings.get('input_type') == "text" and CLEAN == False:
            if self.settings.get('plotbox'):
                v_flop = not (v_flop)
            if self.settings.get('mirror'):
                v_flop = not (v_flop)
            if self.settings.get('flip'):
                v_flop = not (v_flop)

        return v_flop
