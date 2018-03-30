from time import time
from math import (ceil, fabs, floor, tan)

from util import fmessage, OVD_AVAILABLE
from geometry import *
from geometry.pathsorter import sort_paths

# from sortPaths import sort_paths
# from findMaxCircle import find_max_circle as find_max_circle_CPP

from writers import douglas
# TODO How to import higher level package:
# from settings import CUT_TYPE_VCARVE

# Python Performance profiling
# https://zapier.com/engineering/profiling-python-boss/
import cProfile


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func


# TODO Use Toolbit objects

class Toolbit(object):

    def __init__(self):
        self.diameter = 0.0
        self.radius = 0.0
        self.length = 0.0

    def set_diameter(self, diameter):
        self.diameter = diameter
        self.radius = diameter / 2

    def set_radius(self, radius):
        self.radius = radius

    def set_length(self, length):
        self.length = length

    def get_type(self):
        return 'None'


class Straight(Toolbit):

    def __init__(self):
        super(Tool, self).__init__()

    def get_type(self):
        return 'Straight'


class VCarve(Toolbit):

    def __init__(self):
        super(Tool, self).__init__()

        self.angle = 0.0

    def get_type(self):
        return 'V-Bit'

    def set_angle(self, angle):
        self.angle = angle


class Engrave(object):
    """
    Generate toolpaths
    """
    def __init__(self, settings, image=None):

        self.plot_progress_callback = None
        self.status_callback = None
        self.callback_counter = 0

        self.settings = settings
        self.image = image
        self.toolbit = None

        self.set_origin(self.settings.get('xorigin'),
                        self.settings.get('yorigin'))
        self.init_coords()

        # X and Y offset
        self.xzero = 0
        self.yzero = 0

        self.accuracy = self.settings.get('accuracy')
        self.v_pplot = self.settings.get('v_pplot')
        self.stop_calc = False

    def init_coords(self):
        # Path coords format: (x1, y1, x2, y2, line_num, char_num)
        self.refresh_coords()
        self.v_coords = []
        self.clean_segment = []
        self.init_clean_coords()

    def refresh_coords(self):
        if self.image is None:
            self.coords = []
        else:
            self.coords = self.image.coords

    def init_clean_coords(self):
        # Clean coords format: (xnormv, ynormv [, rout, loop_cnt])
        self.clean_coords = []
        self.clean_coords_sort = []
        self.v_clean_coords_sort = []

    def stop_calculation(self):
        self.stop_calc = True

    def set_image(self, image):
        self.image = image
        self.init_coords()

    def set_offset(self, x_offset=0, y_offset=0):
        self.xzero = x_offset
        self.yzero = y_offset

    def get_offset(self):
        return (self.xzero, self.yzero)

    def set_origin(self, x_origin=0, y_origin=0):
        self.x_origin = x_origin
        self.y_origin = y_origin

    def set_coords(self, coords):
        self.coords = coords

    def set_plot_progress_callback(self, callback):
        self.plot_progress_callback = callback

    def set_status_callback(self, callback):
        self.status_callback = callback

    def refresh_v_pplot(self):
        self.v_pplot = self.settings.get('v_pplot')

    def number_of_clean_segments(self):
        return len(self.clean_segment)

    def number_of_v_coords(self):
        return len(self.v_coords)

    def number_of_clean_coords(self):
        return len(self.clean_coords)

    def number_of_clean_coords_sort(self):
        return len(self.clean_coords_sort)

    def number_of_v_clean_coords_sort(self):
        return len(self.v_clean_coords_sort)

    def number_of_segments(self):
        return len(self.coords)

    def get_image_bbox_tuple(self):
        return self.image.bbox.tuple()

    def get_image_width(self):
        return self.image.get_width()

    def get_image_height(self):
        return self.image.get_height()

    def get_plot_bbox(self):
        return self.image.bbox

    def get_coords(self):
        return self.coords

    def get_segments_length(self, clean):

        total_length = 0.0

        v_inc = 1
        v_start = 0
        v_end = self.number_of_segments()
        v_flop = self.get_v_flop()
        if v_flop:
            # reverse order
            v_inc = -1
            v_start = self.number_of_segments() - 1
            v_end = -1

        # determine the total length of segments
        curr_cnt = -1
        for v_index in xrange(v_start, v_end, v_inc):
            curr_cnt += 1
            line = self.coords[v_index]
            x1 = line[0]
            y1 = line[1]
            x2 = line[2]
            y2 = line[3]
            if v_flop:
                length = hypot((x1 - x2), (y1 - y2))
            else:
                length = hypot((x2 - x1), (y2 - y1))
            if clean:
                if self.clean_segment[curr_cnt] is True:
                    total_length += length
            else:
                total_length += length

        return total_length

    def get_loops_from_coords(self):
        """return a list of (closed) loops"""
        loops = []
        segments = []
        next_loop = True
        for segment in self.coords:
            seg_begin = segment[0:2]
            seg_end = segment[2:4]
            if next_loop:
                first_vertex = seg_begin
                next_loop = False
            segments.append(seg_begin)
            if abs(seg_end[0] - first_vertex[0]) < Zero and abs(seg_end[1] - first_vertex[1]) < Zero:
                # segments.append(seg_end)
                segments.reverse()
                loops.append(segments)
                next_loop = True
                segments = []
        return loops

    def v_carve(self, clean=False):

        done = False

        if OVD_AVAILABLE and self.settings.get('v_strategy') == 'voronoi':

            # experimental toolpath strategy, using Anders Wallin's openvoronoi library
            import voronoi

            def toolpath_to_v_coords(toolpath, scale):
                for loop_cnt, chain in enumerate(toolpath):
                    for move in chain:
                        for point in move:
                            p = point[0]
                            z = point[1]
                            xnormv = scale * p.x
                            ynormv = scale * p.y
                            rout = scale * (-z)
                            self.v_coords.append([xnormv, ynormv, rout, loop_cnt])

            segs = self.get_loops_from_coords()
            self.v_coords = []

            toolpath = voronoi.medial_axis(segs, clean)  # TODO return status
            toolpath_to_v_coords(toolpath, 1)

            done = True
        else:
            done = self.v_carve_scorch(clean)
        return done

    def v_carve_scorch(self, clean=False):
        xN, yN, xPartitionLength, yPartitionLength = self.setup_grid_partitions(clean)
        self.determine_active_partitions(xN, yN, xPartitionLength, yPartitionLength, clean)
        return self.make_vcarve_toolpath(xPartitionLength, yPartitionLength, clean)

    def _calc_rmax(self, clean):
        rbit = self.calc_vbit_radius()
        clean_dia = self.settings.get('clean_dia')
        if clean:
            return (rbit + clean_dia / 2)
        else:
            return rbit

    # @do_cprofile
    def make_vcarve_toolpath(self, xPartitionLength, yPartitionLength, clean):

        # set variable for first point in loop
        xa = 1e5
        ya = 1e5
        xb = 1e5
        yb = 1e5

        # set variable for the point previously calculated in a loop
        x_prev = 1e5
        y_prev = 1e5
        seg_sin_prev = None
        seg_cos_prev = None
        char_num_prev = None

        theta = 1.0e5
        loop_cnt = 0

        not_b_carve = not (self.settings.get('bit_shape') == "BALL")

        check_string = self.settings.get('v_check_all')
        if self.settings.get('input_type') != "text":
            check_string = "all"

        rmax = self._calc_rmax(clean)
        dline = self.settings.get('v_step_len')
        bit_angle = self.settings.get('v_bit_angle')
        (minx, maxx, miny, maxy) = self.image.get_bbox().tuple()

        rbit = self.calc_vbit_radius()
        dangle = degrees(dline / rbit)
        if dangle < 2.0:
            dangle = 2.0

        v_step_corner = self.settings.get('v_step_corner')
        if self.settings.get('inlay'):
            v_drv_corner = 360 - v_step_corner
        else:
            v_drv_corner = self.settings.get('v_drv_corner')

        if self.settings.get('input_type') == "image" and clean is False:
            self.coords = self._sort_for_v_carve(self.coords)

        TOT_LENGTH = self.get_segments_length(clean)
        CUR_LENGTH = 0.0
        START_TIME = time()
        done = True

        if TOT_LENGTH <= 0.0:
            return done  # there is nothing to do

        calc_flag = True
        v_index = -1
        v_inc = 1
        v_flop = self.get_v_flop()
        if v_flop:
            v_index = self.number_of_segments()
            v_inc = -1

        for curr in range(self.number_of_segments()):

            if clean is False:
                self.clean_segment.append(False)

            elif self.number_of_clean_segments() == self.number_of_segments():
                calc_flag = self.clean_segment[curr]

            else:
                fmessage('Need to Recalculate V-Carve Path')
                done = False
                break

            # estimate time to complete
            CUR_PCT = CUR_LENGTH / TOT_LENGTH * 100.0
            if CUR_PCT > 0.0:
                MIN_REMAIN = (time() - START_TIME) / 60 * (100 - CUR_PCT) / CUR_PCT
                MIN_TOTAL = 100.0 / CUR_PCT * (time() - START_TIME) / 60
            else:
                MIN_REMAIN = -1
                MIN_TOTAL = -1

            if self.status_callback is not None:
                self.callback_counter += 1
                if (self.v_pplot and not clean) or (self.callback_counter % 100) == 0:
                    msg = '%.1f %% ( %.1f Minutes Remaining | %.1f Minutes Total )' % (CUR_PCT, MIN_REMAIN, MIN_TOTAL)
                    self.status_callback(msg)

            if self.stop_calc:
                self.stop_calc = False
                if clean:
                    self.clean_coords = []
                else:
                    self.v_coords = []
                done = False
                break

            v_index += v_inc
            new_loop = False

            if v_flop:
                x1 = self.coords[v_index][2]  # x2
                y1 = self.coords[v_index][3]  # y2
                x2 = self.coords[v_index][0]  # x1
                y2 = self.coords[v_index][1]  # y1
            else:
                x1 = self.coords[v_index][0]
                y1 = self.coords[v_index][1]
                x2 = self.coords[v_index][2]
                y2 = self.coords[v_index][3]

            char_num = int(self.coords[v_index][5])
            dx = x2 - x1
            dy = y2 - y1
            Lseg = hypot(dx, dy)

            if Lseg < Zero:  # was accuracy
                continue

            # calculate the sin and cos of the coord transformation needed for the distance calculations
            seg_sin = dy / Lseg
            seg_cos = -dx / Lseg
            phi = get_angle(seg_sin, seg_cos)

            if calc_flag is True:
                CUR_LENGTH = CUR_LENGTH + Lseg
            else:
                # theta = phi         #V1.62
                # x0=x2               #V1.62
                # y0=y2               #V1.62
                # seg_sin0=seg_sin    #V1.62
                # seg_cos0=seg_cos    #V1.62
                # char_num0=char_num  #V1.62
                continue

            # another loop, or another character
            if fabs(x1 - x_prev) > Zero or fabs(y1 - y_prev) > Zero or char_num != char_num_prev:
                new_loop = True
                loop_cnt += 1

                xa = x1
                ya = y1
                xb = x2
                yb = y2
                theta = 1.0e5
                seg_sin_prev = None
                seg_cos_prev = None

            if new_loop:
                delta = 180
            else:
                xtmp1 = (x2 - x1) * seg_cos_prev - (y2 - y1) * seg_sin_prev
                ytmp1 = (x2 - x1) * seg_sin_prev + (y2 - y1) * seg_cos_prev
                Ltmp = hypot(xtmp1, ytmp1)
                d_seg_sin = ytmp1 / Ltmp
                d_seg_cos = xtmp1 / Ltmp
                delta = get_angle(d_seg_sin, d_seg_cos)

            if delta < v_drv_corner and bit_angle != 0 and not_b_carve and clean is False:
                # drive to corner
                self.v_coords.append([x1, y1, 0.0, loop_cnt])

            if delta > v_step_corner:
                # add sub-steps around corner
                xIndex = int((x1 - minx) / xPartitionLength)
                yIndex = int((y1 - miny) / yPartitionLength)
                self.add_substeps(curr, loop_cnt, xIndex, yIndex, x1, y1, rmax, rbit, char_num, dangle, delta, theta,
                                  check_string, clean)

            theta = phi
            x_prev = x2
            y_prev = y2
            seg_sin_prev = seg_sin
            seg_cos_prev = seg_cos
            char_num_prev = char_num

            # Calculate the number of steps, then dx and dy for each step.
            # Don't calculate at the joints.
            nsteps = max(floor(Lseg / dline), 2)
            dxpt = dx / nsteps
            dypt = dy / nsteps

            # this makes sure the first cut start at the begining of the first segment
            cnt = 0
            if new_loop and bit_angle != 0 and not_b_carve:
                cnt = -1

            seg_sin = dy / Lseg
            seg_cos = -dx / Lseg
            phi2 = radians(get_angle(seg_sin, seg_cos))
            while cnt < nsteps - 1:
                cnt += 1
                # determine location of next step along outline (xpt, ypt)
                xpt = x1 + dxpt * cnt
                ypt = y1 + dypt * cnt
                xIndex = int((xpt - minx) / xPartitionLength)
                yIndex = int((ypt - miny) / yPartitionLength)

                rout = self.find_max_circle(xIndex, yIndex, xpt, ypt, rmax, char_num, seg_sin, seg_cos, False, check_string)

                # make the first cut drive down at an angle instead of straight down plunge
                if cnt == 0 and not_b_carve:
                    rout = 0.0

                normv, rv, clean_seg = self.record_v_carve_data(xpt, ypt, phi2, rbit, rout, loop_cnt, clean)
                self.clean_segment[curr] = self.clean_segment[curr] or clean_seg

                if self.v_pplot and (self.plot_progress_callback is not None) and clean is False:
                    self.plot_progress_callback(normv, "blue", rv)

                if new_loop and cnt == 1:
                    xpta = xpt
                    ypta = ypt
                    phi2a = phi2
                    routa = rout

            # Check to see if we need to close an open loop
            if abs(x2 - xa) < self.accuracy and abs(y2 - ya) < self.accuracy:
                xtmp1 = (xb - xa) * seg_cos_prev - (yb - ya) * seg_sin_prev
                ytmp1 = (xb - xa) * seg_sin_prev + (yb - ya) * seg_cos_prev
                Ltmp = sqrt(xtmp1 * xtmp1 + ytmp1 * ytmp1)
                d_seg_sin = ytmp1 / Ltmp
                d_seg_cos = xtmp1 / Ltmp
                delta = get_angle(d_seg_sin, d_seg_cos)
                if delta < v_drv_corner and clean is False:
                    # drive to corner
                    self.v_coords.append([xa, ya, 0.0, loop_cnt])

                elif delta > v_step_corner:
                    # add substeps around corner
                    xIndex = int((xa - minx) / xPartitionLength)
                    yIndex = int((ya - miny) / yPartitionLength)
                    self.add_substeps(curr, loop_cnt, xIndex, yIndex, xa, ya, rmax, rbit, char_num, dangle, delta,
                                      theta, check_string, clean)
                    normv, rv, clean_seg = self.record_v_carve_data(xpta, ypta, phi2a, rbit, routa, loop_cnt, clean)
                    self.clean_segment[curr] = self.clean_segment[curr] or clean_seg

                else:
                    # add closing segment
                    normv, rv, clean_seg = self.record_v_carve_data(xpta, ypta, phi2a, rbit, routa, loop_cnt, clean)
                    self.clean_segment[curr] = self.clean_segment[curr] or clean_seg

        return done

    def add_substeps(self, curr, loop_cnt, xIndex, yIndex, x1, y1, rmax, rbit, char_num, dangle, delta, theta,
                     CHK_STRING, clean):

        phisteps = max(int(floor((delta - 180) / dangle)), 2)
        step_phi = (delta - 180) / phisteps

        for pcnt in range(phisteps - 1):
            sub_phi = radians(-pcnt * step_phi + theta)
            sub_seg_cos = cos(sub_phi)
            sub_seg_sin = sin(sub_phi)

            rout = self.find_max_circle(xIndex, yIndex, x1, y1, rmax, char_num, sub_seg_sin, sub_seg_cos, True, CHK_STRING)

            normv, rv, clean_seg = self.record_v_carve_data(x1, y1, sub_phi, rbit, rout, loop_cnt, clean)

            self.clean_segment[curr] = self.clean_segment[curr] or clean_seg

            if self.v_pplot and (self.plot_progress_callback is not None) and clean is False:
                self.plot_progress_callback(normv, "blue", rv)

    def determine_active_partitions(self, xN, yN, xPartitionLength, yPartitionLength, clean):
        """
        Determine active partitions for each line segment
        """
        # rbit = self.calc_vbit_radius()
        rmax = self._calc_rmax(clean)
        minx, maxx, miny, maxy = self.image.get_bbox().tuple()

        # for XY_R in self.coords:
        for curr, coords in enumerate(self.coords):

            XY_R = self.coords[curr][:]
            x1_R = XY_R[0]
            y1_R = XY_R[1]
            x2_R = XY_R[2]
            y2_R = XY_R[3]

            length = hypot((x2_R - x1_R), (y2_R - y1_R))
            R_R = length / 2 + rmax
            X_R = (x1_R + x2_R) / 2
            Y_R = (y1_R + y2_R) / 2

            coded_index = []

            # find the local coordinates of the line segment ends
            x1_G = XY_R[0] - minx
            y1_G = XY_R[1] - miny
            x2_G = XY_R[2] - minx
            y2_G = XY_R[3] - miny

            # find the grid box index for each line segment end
            x1_i = int(x1_G / xPartitionLength)
            x2_i = int(x2_G / xPartitionLength)
            y1_i = int(y1_G / yPartitionLength)
            y2_i = int(y2_G / yPartitionLength)

            # find the max/min grid box locations
            Xindex_min = min(x1_i, x2_i)
            Xindex_max = max(x1_i, x2_i)
            Yindex_min = min(y1_i, y2_i)
            Yindex_max = max(y1_i, y2_i)

            check_points = []
            if Xindex_max > Xindex_min and abs(x2_G - x1_G) > Zero:

                if Yindex_max > Yindex_min and abs(y2_G - y1_G) > Zero:
                    check_points.append([x1_i, y1_i])
                    check_points.append([x2_i, y2_i])

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
                        x_ind_check += 1

                    # Add check point in each partition in the range of Y values
                    y_ind_check = Yindex_min + 1
                    while y_ind_check <= Yindex_max - 1:
                        y_val = y_ind_check * yPartitionLength
                        x_val = (y_val - b_G) / m_G
                        x_ind_check = int(x_val / xPartitionLength)
                        check_points.append([x_ind_check, y_ind_check])
                        y_ind_check += 1
                else:
                    x_ind_check = Xindex_min
                    y_ind_check = Yindex_min
                    while x_ind_check <= Xindex_max:
                        check_points.append([x_ind_check, y_ind_check])
                        x_ind_check += 1
            else:
                x_ind_check = Xindex_min
                y_ind_check = Yindex_min
                while y_ind_check <= Yindex_max:
                    check_points.append([x_ind_check, y_ind_check])
                    y_ind_check += 1

            # For each grid box in check_points add the grid box and all adjacent grid boxes
            # to the list of boxes for this line segment
            for xy_point in check_points:
                xIndex = xy_point[0]
                yIndex = xy_point[1]
                for i in range(max(xIndex - 1, 0), min(xN, xIndex + 2)):
                    for j in range(max(yIndex - 1, 0), min(yN, yIndex + 2)):
                        coded_index.append(int(i + j * xN))

            coded_index = set(coded_index)  # unique tuples
            for thisIndex in coded_index:
                line_R_appended = XY_R
                line_R_appended.append(X_R)
                line_R_appended.append(Y_R)
                line_R_appended.append(R_R)
                idxq, idxr = divmod(thisIndex, xN)
                self.partition_list[idxr][idxq].append(line_R_appended)

    def setup_grid_partitions(self, clean):
        """
        Setup Grid Partitions for the cleaning toolpath
        """
        # rbit = self.calc_vbit_radius()
        rmax = self._calc_rmax(clean)
        dline = self.settings.get('v_step_len')

        x_length = max(self.image.get_bbox().width(), 1)
        y_length = max(self.image.get_bbox().height(), 1)

        # step = (2 * rmax + dline) * 1.1  # fudge-factor?
        step = 2 * rmax + dline
        x_steps = max(int(x_length / step), 1)
        y_steps = max(int(y_length / step), 1)

        x_partition_length = x_length / x_steps
        y_partition_length = y_length / y_steps

        x_steps += 1
        y_steps += 1

        self.partition_list = []
        for x in range(0, x_steps):
            self.partition_list.append([])
            for y in range(0, y_steps):
                self.partition_list[x].append([])

        return (x_steps, y_steps, x_partition_length, y_partition_length)

    def record_v_carve_data(self, x1, y1, phi, rbit, rout, loop_cnt, clean):

        Lx, Ly = transform(0, rout, -phi)
        xnormv = x1 + Lx
        ynormv = y1 + Ly

        need_clean = False
        if clean:
            if rout >= rbit:
                self.clean_coords.append([xnormv, ynormv, rout, loop_cnt])
        else:
            self.v_coords.append([xnormv, ynormv, rout, loop_cnt])
            if abs(rbit - rout) <= Zero:
                need_clean = True

        return (xnormv, ynormv), rout, need_clean

    def calc_vbit_radius(self):

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
                    pass

                else:
                    pass

        return vbit_dia / 2

    # def find_max_circle_CPP(self, xIndex, yIndex, xpt, ypt, rmin, char_num, seg_sin, seg_cos, corner, CHK_STRING):
    #     rmax = find_max_circle_CPP(self.partition_list, xIndex, yIndex, xpt, ypt, rmin, char_num, seg_sin, seg_cos, corner, CHK_STRING)
    #     return rmax

    def find_max_circle(self, xIndex, yIndex, xpt, ypt, rmin, char_num, seg_sin, seg_cos, corner, CHK_STRING):
        """
        Find the maximum radius that can be placed in the position
        xpt,ypt without interfering with other line segments (rmin is max R)
        """
        coords_check = []
        R_A = abs(rmin)
        logic_full = False

        # Loop over active partitions for the current line segment
        for line_B in self.partition_list[xIndex][yIndex]:
            X_B = line_B[len(line_B) - 3]
            Y_B = line_B[len(line_B) - 2]
            R_B = line_B[len(line_B) - 1]
            gap = hypot((X_B - xpt), (Y_B - ypt))
            if gap < abs(R_A + R_B):
                coords_check.append(line_B)

        for XYc in coords_check:
            xmaxt = max(XYc[0], XYc[2]) + rmin * 2
            xmint = min(XYc[0], XYc[2]) - rmin * 2
            ymaxt = max(XYc[1], XYc[3]) + rmin * 2
            ymint = min(XYc[1], XYc[3]) - rmin * 2

            if xpt >= xmint and ypt >= ymint and xpt <= xmaxt and ypt <= ymaxt:
                logic_full = True
            else:
                continue  # nothing to check

            if CHK_STRING == "chr":
                logic_full = logic_full and (char_num == int(XYc[5]))

            if corner:
                logic_full = logic_full and \
                             ((fabs(xpt - XYc[0]) > Zero) or (fabs(ypt - XYc[1]) > Zero)) and \
                             ((fabs(xpt - XYc[2]) > Zero) or (fabs(ypt - XYc[3]) > Zero))

            if logic_full:
                rmin = self.solve_quadratic(XYc, xpt, ypt, rmin, seg_cos, seg_sin)

        return rmin

    def solve_quadratic(self, XYc, xpt, ypt, rmin, seg_cos, seg_sin):

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

            if A != 0:
                sq_root = sqrt(B * B - 4 * A * C)
                xq1 = (-B + sq_root) / (2 * A)

                if xq1 >= min(xc1, xc2) and xq1 <= max(xc1, xc2):
                    rtmp = xq1 * sq + b
                    if rtmp >= 0.0:
                        rmin = min(rmin, rtmp)

                xq2 = (-B - sq_root) / (2 * A)
                # yq2 = m * xq2 + b

                if xq2 >= min(xc1, xc2) and xq2 <= max(xc1, xc2):
                    rtmp = xq2 * sq + b
                    if rtmp >= 0.0:
                        rmin = min(rmin, rtmp)

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

    def _sort_for_v_carve(self, sort_coords, LN_START=0):

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
                ecoords.append([x2, y2])
                oldx, oldy = x2, y2
            else:
                dist = hypot((oldx - x1), (oldy - y1))
                # check and see if we need to move to a new discontinuous start point
                if dist > Zero:
                    Lend.append(cnt)
                    cnt += 1
                    ecoords.append([x1, y1])
                    Lbeg.append(cnt)
                ecoords.append([x2, y2])
                oldx, oldy = x2, y2
            cnt += 1

        Lend.append(cnt)

        if self.status_callback is not None:
            self.status_callback('Checking Input Image Data')

        # Fully Close Closed loops and Remove Open Loops
        i = 0
        LObeg = []
        LOend = []
        while i < len(Lbeg):  # for each loop
            [Xstart, Ystart] = ecoords[Lbeg[i]]
            [Xend, Yend] = ecoords[Lend[i]]
            dist = hypot((Xend - Xstart), (Yend - Ystart))
            # if end is the same as the beginning (changed in V1.55: was Acc)
            if dist <= Zero:
                ecoords[Lend[i]] = [Xstart, Ystart]
                i += 1
            else:  # end != to beginning
                LObeg.append(Lbeg.pop(i))
                LOend.append(Lend.pop(i))

        # For Each open loop connect to the next closest
        # loop end until all of the loops are closed
        LNbeg = []
        LNend = []
        LNloop = []
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
            while OPEN and len(LObeg) > 0:
                [Xend, Yend] = ecoords[End]
                dist_beg_min = hypot((Xend - Xstart), (Yend - Ystart))
                dist_end_min = dist_beg_min
                k_min_beg = -1
                k_min_end = -1
                for k in range(len(LObeg)):
                    [Xkstart, Ykstart] = ecoords[LObeg[k]]
                    [Xkend, Ykend] = ecoords[LOend[k]]
                    dist_beg = hypot((Xend - Xkstart), (Yend - Ykstart))
                    dist_end = hypot((Xend - Xkend), (Yend - Ykend))
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

        # Make new sequential ecoords for each new loop
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

            for i in range(Start, End + step, step):
                [x1, y1] = ecoords[i]
                ecoords.append([x1, y1])

        if len(Lbeg) > len(Lend):
            Lend.append(len(ecoords) - 1)

        # Determine loop directions CW/CCW
        if self.status_callback is not None:
            self.status_callback('Calculating Initial Loop Directions (CW/CCW)')

        Lflip = []  # normvector direction in (False) or out (True) for loopsegment [i]
        Lcw = []    # loop direction clockwise (True) or counterclockwise for loopsegment [i]

        for k in range(len(Lbeg)):
            Start = Lbeg[k]
            End = Lend[k]
            step = 1

            signedArea = 0.0

            [x1, y1] = ecoords[Start]
            for i in range(Start + 1, End + step, step):
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

        # For each loop determine if other loops are inside
        for iloop in range(Nloops):

            if self.status_callback is not None:
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

        # Set Loop clockwise flag to the state of each loop
        # Could flip cut side here for auto side determination
        for iloop in range(Nloops):
            if Lflip[iloop]:
                Lcw[iloop] = not Lcw[iloop]

        # Find new order based on distance to next beginning
        if self.status_callback is not None:
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
            # min_dist = hypot(dx, dy)
            min_dist = dx * dx + dy * dy  # optimized

            inext = 0
            for j in range(1, len(Lbeg)):
                dx = Xcur - ecoords[Lbeg[j]][0]
                dy = Ycur - ecoords[Lbeg[j]][1]
                # dist = hypot(dx, dy)
                dist = dx * dx + dy * dy  # optimized
                if dist < min_dist:
                    min_dist = dist
                    inext = j

            if Lflip[inext]:
                order_out.append([Lend[inext], Lbeg[inext], Lnum[inext]])
            else:
                order_out.append([Lbeg[inext], Lend[inext], Lnum[inext]])

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

    def _find_paths_X(self, check_coords, clean_dia, Radjust, clean_step, skip):
        return self._find_paths(check_coords, clean_dia, Radjust, clean_step, skip)

    def _find_paths_Y(self, check_coords_in, clean_dia, Radjust, clean_step, skip):

        check_coords = []
        for XY in check_coords_in:
            check_coords.append([XY[1], XY[0], XY[2]])

        Xclean_coords, Xclean_coords_short = \
            self._find_paths(check_coords, clean_dia, Radjust, clean_step, skip)

        Xclean_coords_out = []
        Xclean_coords_short_out = []

        for XY in Xclean_coords:
            Xclean_coords_out.append([XY[1], XY[0], XY[2]])

        for XY in Xclean_coords_short:
            Xclean_coords_short_out.append([XY[1], XY[0], XY[2]])

        return Xclean_coords_out, Xclean_coords_short_out

    def _find_paths(self, check_coords, clean_dia, Radjust, clean_step, skip):

        minx_c = 0.0
        maxx_c = 0.0
        miny_c = 0.0
        maxy_c = 0.0

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

        # Find ends of horizontal lines for carving clean-up
        loop_cnt = 0
        Y = miny_c
        line_cnt = skip - 1
        while Y <= maxy_c:
            line_cnt += 1
            X = minx_c
            x1 = x2 = X
            x1_old = x1
            x2_old = x2

            # Find relevant clean_coord_data
            temp_coords = []
            for XY in check_coords:
                if Y < (XY[1] + XY[2]) and Y > (XY[1] - XY[2]):
                    temp_coords.append(XY)

            while X <= maxx_c:
                for XY in temp_coords:
                    h = XY[0]
                    k = XY[1]
                    R = XY[2] - Radjust
                    dist = hypot((X - h), (Y - k))
                    if dist <= R:
                        Root = sqrt(R ** 2 - (Y - k) ** 2)
                        XL = h - Root
                        XR = h + Root
                        if XL < x1:
                            x1 = XL
                        if XR > x2:
                            x2 = XR
                if x1 == x2:
                    X += DX
                    x1 = x2 = X
                elif x1 == x1_old and x2 == x2_old:
                    loop_cnt += 1
                    Xclean_coords.append([x1, Y, loop_cnt])
                    Xclean_coords.append([x2, Y, loop_cnt])
                    if line_cnt == skip:
                        Xclean_coords_short.append([x1, Y, loop_cnt])
                        Xclean_coords_short.append([x2, Y, loop_cnt])
                    X += DX
                    x1 = x2 = X
                else:
                    X = x2

                x1_old = x1
                x2_old = x2

            if line_cnt == skip:
                line_cnt = 0

            Y += DY

        return Xclean_coords, Xclean_coords_short

    def _clean_coords_to_path_coords(self, clean_coords_in):
        path_coords_out = []
        # Clean coords format ([xnormv, ynormv, rout, loop_cnt])      - self.clean_coords
        # Path coords format  ([x1, y1, x2, y2, line_cnt, char_cnt])  - self.coords
        for i in range(1, len(clean_coords_in)):
            if clean_coords_in[i][3] == clean_coords_in[i - 1][3]:
                path_coords_out.append([clean_coords_in[i - 1][0],
                                        clean_coords_in[i - 1][1],
                                        clean_coords_in[i][0],
                                        clean_coords_in[i][1],
                                        0,
                                        0])
        return path_coords_out

    # @do_cprofile
    def clean_path_calc(self, bit_type="straight"):

        v_flop = self.get_v_flop(clean=True)
        if v_flop:
            edge = 1
        else:
            edge = 0

        # reorganize clean_coords
        if bit_type == "straight":
            test_clean = self.settings.get('clean_P') + \
                         self.settings.get('clean_X') + \
                         self.settings.get('clean_Y')
        else:
            test_clean = self.settings.get('v_clean_P') + \
                         self.settings.get('v_clean_X') + \
                         self.settings.get('v_clean_Y')

        rbit = self.calc_vbit_radius()
        loop_cnt_out = 0
        check_coords = []

        if bit_type == "straight":

            if self.status_callback is not None:
                self.status_callback('Calculating Cleanup Cut Paths')

            self.clean_coords_sort = []

            # diameter of cleanup bit
            clean_dia = self.settings.get('clean_dia')

            # percentage of the cut diameter
            step_over = self.settings.get('clean_step')
            clean_step = step_over / 100.0

            Radjust = clean_dia / 2.0 + rbit
            check_coords = self.clean_coords

        elif bit_type == "v-bit":

            if self.status_callback is not None:
                self.status_callback('Calculating V-Bit Cleanup Cut Paths')

            self.v_clean_coords_sort = []

            # effective diameter of clean-up v-bit
            clean_dia = self.settings.get('clean_v')
            if clean_dia < Zero:
                return
            clean_step = 1.0

            # allow the cutter to get within 1/4 of the v-clean step of the v-carved surface
            offset = clean_dia / 4.0
            Radjust = rbit + offset
            flat_clean_r = self.settings.get('clean_dia') / 2.0
            for XY in self.clean_coords:
                R = XY[2] - Radjust
                if R > 0.0 and R < (flat_clean_r - offset - Zero):
                    check_coords.append(XY)

        # TODO use CUT_TYPE_VCARVE
        if self.settings.get('cut_type') == "v-carve" and len(self.clean_coords) > 1 and test_clean > 0:
            DX = clean_dia * clean_step
            DY = DX

            if bit_type == "straight":
                MAXD = clean_dia
            else:
                MAXD = hypot(DX, DY) * 1.1  # fudge factor  # TODO

            if bit_type == "straight":
                Xclean_coords, Yclean_coords, clean_coords_out, loop_cnt_out = \
                    self.straight_toolpath(clean_dia, clean_step, edge, loop_cnt_out, rbit)

            elif bit_type == "v-bit":
                Xclean_coords, Yclean_coords, clean_coords_out, loop_cnt_out = \
                    self.vbit_toolpath(MAXD, Radjust, check_coords, clean_dia, clean_step, loop_cnt_out, 1)

            # Now deal with the horizontal line cuts...
            if (self.settings.get('clean_X') == 1 and bit_type != "v-bit") or \
                    (self.settings.get('v_clean_X') == 1 and bit_type == "v-bit"):
                loop_cnt_out = self.line_cuts(MAXD, Xclean_coords, clean_coords_out, clean_dia, loop_cnt_out)

            # ...and deal with the vertical line cuts
            if (self.settings.get('clean_Y') == 1 and bit_type != "v-bit") or \
                    (self.settings.get('v_clean_Y') == 1 and bit_type == "v-bit"):
                self.line_cuts(MAXD, Yclean_coords, clean_coords_out, clean_dia, loop_cnt_out)

            if bit_type == "v-bit":
                self.v_clean_coords_sort = clean_coords_out
            else:
                self.clean_coords_sort = clean_coords_out

        if self.status_callback is not None:
            self.status_callback('Done Calculating Cleanup Cut Paths', color='white')

    def line_cuts(self, MAXD, clean_coords, clean_coords_out, clean_dia, loop_cnt_out):

        order_out = sort_paths(clean_coords)

        x_old = -999
        y_old = -999
        loop_old = -1
        for line in order_out:

            if line[0] > line[1]:
                step = -1
            else:
                step = 1

            for i in range(line[0], line[1] + step, step):

                x1 = clean_coords[i][0]
                y1 = clean_coords[i][1]
                loop = clean_coords[i][2]

                dx = x1 - x_old
                dy = y1 - y_old
                dist = hypot(dx, dy)
                if dist > MAXD and loop != loop_old:
                    loop_cnt_out += 1

                clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])

                x_old = x1
                y_old = y1
                loop_old = loop

        return loop_cnt_out

    def vbit_toolpath(self, MAXD, Radjust, check_coords, clean_dia,
                      clean_step, loop_cnt_out, skip):
        """
        Make V-Bit cutter toolpath
        Returns the X and Y clean_coordinates, and the number of loops
        """
        clean_coords_out = []

        # Find ends of horizontal lines for carving clean-up
        Xclean_perimeter, Xclean_coords = \
            self._find_paths_X(check_coords, clean_dia, Radjust, clean_step, skip)

        # Find ends of Vertical lines for carving clean-up
        Yclean_perimeter, Yclean_coords = \
            self._find_paths_Y(check_coords, clean_dia, Radjust, clean_step, skip)

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
                # min_dist = hypot(dx, dy)
                min_dist = dx * dx + dy * dy  # optimized

                inext = 0
                for j in range(1, len(Lbeg)):
                    dx = Xcur - ecoords[Lbeg[j]][0]
                    dy = Ycur - ecoords[Lbeg[j]][1]
                    # dist = hypot(dx, dy)
                    dist = dx * dx + dy * dy  # optimized
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
                dist = hypot(dx, dy)
                if dist > MAXD:
                    dx = x_start_loop - x_old
                    dy = y_start_loop - y_old
                    dist = hypot(dx, dy)
                    # Fully close loop if the current point is close enough to the start of the loop
                    if dist < MAXD:
                        clean_coords_out.append([x_start_loop, y_start_loop, clean_dia / 2, loop_cnt_out])
                    loop_cnt_out += 1
                    x_start_loop = x1
                    y_start_loop = y1
                clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])
                x_old = x1
                y_old = y1

        return Xclean_coords, Yclean_coords, clean_coords_out, loop_cnt_out

    def straight_toolpath(self, clean_dia, clean_step, edge, loop_cnt_out, rbit):
        """
        Make straight bit toolpath
        Returns the clean coordinates and the number of loops
        """
        DX = clean_dia * clean_step

        clean_dia = self.settings.get('clean_dia')  # diameter of cleanup bit
        step_over = self.settings.get('clean_step')  # percent of cut DIA
        clean_step = step_over / 100.0
        Rperimeter = rbit + (clean_dia / 2.0)

        MaxLoop = 0
        loop_cnt = 0
        Xclean_coords = []
        Yclean_coords = []

        # Extract straight bit points from clean_coords
        check_coords = []
        junk = -1
        for XY in self.clean_coords:
            R = XY[2]
            if R >= (Rperimeter - Zero):
                check_coords.append(XY)
            elif len(check_coords) > 0:
                junk -= 1
                check_coords.append([None, None, None, junk])
                # check_coords[len(check_coords)-1][3]=junk

        # Calculate Straight bit "Perimeter" tool path
        loop_coords = self._clean_coords_to_path_coords(check_coords)
        loop_coords = self._sort_for_v_carve(loop_coords)

        # Line fit loop_coords
        P_coords = []
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

        loop_cnt_out += MaxLoop

        if self.settings.get('clean_P') == 1:
            clean_coords_out = P_coords
        else:
            clean_coords_out = []

        offset = DX / 2.0

        if self.settings.get('clean_X') == 1:
            y_pmax -= offset
            y_pmin += offset
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
                        if (x2 - x1) > (offset * 2):
                            loop_cnt += 1
                            Xclean_coords.append([x1 + offset, y1, loop_cnt])
                            Xclean_coords.append([x2 - offset, y2, loop_cnt])

        if self.settings.get('clean_Y') == 1:
            x_pmax -= offset
            x_pmin += offset
            Xsize = x_pmax - x_pmin
            Xsteps = ceil(Xsize / (clean_dia * clean_step))
            if Xsteps > 0:
                for iX in range(0, int(Xsteps + 1)):
                    x = x_pmin + iX / Xsteps * (x_pmax - x_pmin)
                    intXYlist = detect_intersect([x, y_pmin - 1], [x, y_pmax + 1], loop_coords, XY_T_F=True)
                    intXY_len = len(intXYlist)
                    for i in range(edge, intXY_len - 1 - edge, 2):
                        x1 = intXYlist[i][0]
                        y1 = intXYlist[i][1]
                        x2 = intXYlist[i + 1][0]
                        y2 = intXYlist[i + 1][1]
                        if (y2 - y1) > (offset * 2):
                            loop_cnt += 1
                            Yclean_coords.append([x1, y1 + offset, loop_cnt])
                            Yclean_coords.append([x2, y2 - offset, loop_cnt])

        return Xclean_coords, Yclean_coords, clean_coords_out, loop_cnt_out

    def get_v_flop(self, clean=False):

        v_flop = self.settings.get('v_flop')

        if self.settings.get('input_type') == "text" and clean is False:
            if self.settings.get('plotbox'):
                v_flop = not v_flop
            if self.settings.get('mirror'):
                v_flop = not v_flop
            if self.settings.get('flip'):
                v_flop = not v_flop

        return v_flop
