import sys

from math import tan
from geometry import *
from geometry.pathsorter import sort_paths

from douglas import douglas

from util import header_text, fmessage, f_engrave_version
# TODO How to import higher level package:
# from settings import CUT_TYPE_VCARVE, CUT_TYPE_ENGRAVE


def gcode(job):
    settings = job.settings

    code = []

    code.extend(header_text())
    code.extend(settings.to_gcode())

    # String_short = String
    # max_len = 40
    # if len(String) > max_len:
    #     String_short = String[0:max_len] + '___'

    # accuracy = settings.get('accuracy')
    dp, dpfeed = get_nr_of_decimals(job)

    safe_z = settings.get('zsafe')
    depth = settings.get('zcut')
    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % safe_z
        # depth_val = FORMAT % depth
    else:
        FORMAT = '#1 = %%.%df  ( Safe Z )' % (dp)
        code.append(FORMAT % safe_z)
        FORMAT = '#2 = %%.%df  ( Engraving depth Z )' % (dp)
        code.append(FORMAT % depth)
        safe_val = '#1'
        # depth_val = '#2'

    # G90  ; Sets absolute distance mode
    code.append('G90')

    # G91.1  ; Sets Incremental Distance Mode for I, J & K arc offsets.
    if settings.get('arc_fit') == "center":
        code.append('G91.1')

    if settings.get('units') == "in":
        # G20  ; sets units to inches
        code.append('G20')
    else:
        # G21  ; sets units to mm
        code.append('G21')

    for line in settings.get('gcode_preamble').split('|'):
        code.append(line)

    code.append("(##########################################)")

    # The actual cutting is done here
    if settings.get('cut_type') == "engrave" or \
            settings.get('bit_shape') == "FLAT":  # TODO use settings CUT_TYPE_VCARVE
        code.extend(engrave_gcode(job))
    else:
        code.extend(vcarve_gcode(job))

    code.append('G0 Z%s' % safe_val)  # final engraver up

    for line in settings.get('gcode_postamble').split('|'):
        code.append(line)

    return code


def engrave_gcode(job):

    settings = job.settings
    code = []

    accuracy = settings.get('accuracy')
    dp, dpfeed = get_nr_of_decimals(job)

    oldx = oldy = -1e10
    first_stroke = True

    safe_z = settings.get('zsafe')
    depth = settings.get('zcut')
    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % safe_z
        depth_val = FORMAT % depth
    else:
        FORMAT = '#1 = %%.%df  ( Safe Z )' % (dp)
        code.append(FORMAT % safe_z)
        FORMAT = '#2 = %%.%df  ( Engraving depth Z )' % (dp)
        code.append(FORMAT % depth)
        safe_val = '#1'
        depth_val = '#2'

    # TODO add GCode object to job?
    # g_target = lambda s: sys.stdout.write(s + "\n")  # TEST
    g = Gcode(safetyheight=safe_z,
              tolerance=accuracy,
              target=lambda s: code.append(s),
              arc_fit=settings.get('arc_fit'))
    g.dp = dp
    g.dpfeed = dpfeed
    g.set_plane(17)

    # Feed rate
    FORMAT = '%%.%df' % dpfeed
    feed_str = FORMAT % settings.get('feedrate')
    plunge_str = FORMAT % settings.get('plunge_rate')
    zero_feed = FORMAT % 0.0

    code.append("F%s" % feed_str)
    if plunge_str == zero_feed:
        plunge_str = feed_str

    # Set up variables for multipass cutting
    maxDZ = settings.get('v_max_cut')
    rough_stock = settings.get('v_rough_stk')
    zmin = 0.0
    roughing = True
    rough_again = False

    ecoords = []

    if settings.get('bit_shape') == "FLAT" and settings.get('cut_type') != "engrave":

        # Create Flat Cut ECOORDS

        accuracy = settings.get('v_step_len') * 1.5  # fudge factor

        if job.number_of_v_coords() > 0:
            rbit = calc_vbit_dia(job) / 2.0
            loopa_old = job.v_coords[0][3]
            loop = 0
            for i in range(1, job.number_of_v_coords()):
                xa = job.v_coords[i][0]
                ya = job.v_coords[i][1]
                ra = job.v_coords[i][2]
                loopa = job.v_coords[i][3]

                if loopa_old != loopa:
                    loop = loop + 1
                if ra >= rbit:
                    ecoords.append([xa, ya, loop])
                    loopa_old = loopa
                else:
                    loop = loop + 1

        depth = settings.get('max_cut')
        # depth = settings.get('v_max_cut')

        if rough_stock > 0:
            rough_again = True

        if rough_stock > 0 and -maxDZ < rough_stock:
            rough_stock = -maxDZ

    else:

        # Create ECOORDS

        loop = 0
        for line in job.coords:
            XY = line
            x1 = XY[0]
            y1 = XY[1]
            x2 = XY[2]
            y2 = XY[3]
            dx = oldx - x1
            dy = oldy - y1
            dist = hypot(dx, dy)

            # check and see if we need to move to a new discontinuous start point
            if dist > accuracy or first_stroke:
                loop = loop + 1
                first_stroke = False
                ecoords.append([x1, y1, loop])

            ecoords.append([x2, y2, loop])
            oldx, oldy = x2, y2

    order_out = sort_paths(ecoords)

    while rough_again or roughing:

        if rough_again is False:
            roughing = False
            maxDZ = -1e10

        rough_again = False
        zmin = zmin + maxDZ

        z1 = depth
        if roughing:
            z1 = z1 + rough_stock

        if z1 < zmin:
            z1 = zmin
            rough_again = True

        # zmax = zmin - maxDZ

        if settings.get('bit_shape') == "FLAT" and settings.get('cut_type') != "engrave":
            FORMAT = '%%.%df' % (dp)
            depth_val = FORMAT % (z1)

        # dist = 999
        lastx = -999
        lasty = -999
        # lastz = 0
        # z1 = 0
        # nextz = 0

        # code.append("G0 Z%s" %(safe_val))
        for line in order_out:

            temp = line
            if temp[0] > temp[1]:
                step = -1
            else:
                step = 1

            # R_last = 999
            # x_center_last = 999
            # y_center_last = 999
            # FLAG_arc = 0
            # FLAG_line = 0
            # code = []

            loop_old = -1

            for i in range(temp[0], temp[1] + step, step):
                x1 = ecoords[i][0]
                y1 = ecoords[i][1]
                loop = ecoords[i][2]

                # if i + 1 < temp[1] + step:
                #     nextx = ecoords[i + 1][0]
                #     nexty = ecoords[i + 1][1]
                #     nextloop = ecoords[i + 1][2]
                # else:
                #     nextx = 0
                #     nexty = 0
                #     nextloop = -99  # don't change this dummy number it is used below

                # check and see if we need to move to a new discontinuous start point
                if loop != loop_old:
                    g.flush()
                    dx = x1 - lastx
                    dy = y1 - lasty
                    dist = hypot(dx, dy)
                    if dist > accuracy:

                        # lift engraver
                        code.append("G0 Z%s" % safe_val)

                        # rapid to current position
                        FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                        code.append(FORMAT % (x1, y1))

                        # drop cutter
                        if feed_str == plunge_str:
                            code.append('G1 Z%s' % depth_val)
                        else:
                            code.append('G1 Z%s F%s' % (depth_val, plunge_str))
                            g.set_feed(feed_str)

                        lastx = x1
                        lasty = y1
                        g.cut(x1, y1)
                else:
                    g.cut(x1, y1)
                    lastx = x1
                    lasty = y1

                loop_old = loop

            g.flush()
        g.flush()
    g.flush()

    # Make Circle
    plot_radius = settings.get('text_radius')
    if settings.get('input_type') == 'text' and \
            settings.get('plotbox') and \
            plot_radius != 0 and \
            settings.get('cut_type') == "engrave":  # TODO use CUT_TYPE_ENGRAVE

        xorigin = settings.get('xorigin')
        yorigin = settings.get('yorigin')

        # lift engraver to safe height
        code.append('( Engraving Circle )')
        code.append('G0 Z%s' % safe_val)

        FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
        code.append(FORMAT % (xorigin - job.xzero - plot_radius, yorigin - job.yzero))

        if feed_str == plunge_str:
            feed_string = ""
        else:
            feed_string = " F" + plunge_str
            g.set_feed(feed_str)

        code.append('G1 Z%s' % depth_val + feed_string)

        if feed_str == plunge_str:
            feed_string = ""
        else:
            feed_string = " F" + feed_str

        FORMAT = 'G2 I%%.%df J%%.%df' % (dp, dp)
        code.append(FORMAT % (plot_radius, 0.0) + feed_string)

    return code


def vcarve_gcode(job):

    settings = job.settings
    code = []

    accuracy = settings.get('accuracy')
    dp, dpfeed = get_nr_of_decimals(job)

    safe_z = settings.get('zsafe')
    depth = settings.get('zcut')
    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % safe_z
        # depth_val = FORMAT % depth
    else:
        FORMAT = '#1 = %%.%df  ( Safe Z )' % dp
        code.append(FORMAT % safe_z)
        FORMAT = '#2 = %%.%df  ( Engraving depth Z )' % dp
        code.append(FORMAT % depth)
        safe_val = '#1'
        # depth_val = '#2'

    # g_target = lambda s: sys.stdout.write(s + "\n")  # TEST
    g = Gcode(safetyheight=safe_z,
              tolerance=accuracy,
              target=lambda s: code.append(s),
              arc_fit=settings.get('arc_fit'))
    g.dp = dp
    g.dpfeed = dpfeed
    g.set_plane(17)

    # Feed rate
    FORMAT = '%%.%df' % dpfeed
    feed_str = FORMAT % settings.get('feedrate')
    code.append("F%s" % feed_str)

    # Set up variables for multipass cutting
    maxDZ = settings.get('v_max_cut')
    rough_stock = settings.get('v_rough_stk')
    zmin = 0.0
    roughing = True
    rough_again = False

    # find loop ends
    Lbeg = []
    Lend = []
    Lbeg.append(0)

    if job.number_of_v_coords() > 0:

        loop_old = job.v_coords[0][3]
        for i in range(1, job.number_of_v_coords()):
            loop = job.v_coords[i][3]
            if loop != loop_old:
                Lbeg.append(i)
                Lend.append(i - 1)
            loop_old = loop
        Lend.append(i)

        # Find new order based on distance to next beginning
        order_out = []
        order_out.append([Lbeg[0], Lend[0]])
        inext = 0
        total = len(Lbeg)
        for i in range(total - 1):
            ii = Lend.pop(inext)
            Lbeg.pop(inext)
            Xcur = job.v_coords[ii][0]
            Ycur = job.v_coords[ii][1]

            dx = Xcur - job.v_coords[Lbeg[0]][0]
            dy = Ycur - job.v_coords[Lbeg[0]][1]
            # min_dist = hypot(dx, dy)
            min_dist = dx * dx + dy * dy  # optimized

            inext = 0
            for j in range(1, len(Lbeg)):
                dx = Xcur - job.v_coords[Lbeg[j]][0]
                dy = Ycur - job.v_coords[Lbeg[j]][1]
                # dist = hypot(dx, dy)
                dist = dx * dx + dy * dy  # optimized
                if dist < min_dist:
                    min_dist = dist
                    inext = j
            order_out.append([Lbeg[inext], Lend[inext]])

        new_coords = []
        for line in order_out:
            temp = line
            for i in range(temp[0], temp[1] + 1):
                new_coords.append(job.v_coords[i])

        bit_shape = settings.get('bit_shape')
        half_angle = radians(settings.get('v_bit_angle') / 2.0)
        bit_radius = settings.get('v_bit_dia') / 2.0

        # V-carve stuff
        if rough_stock > 0:
            rough_again = True

        if rough_stock > 0 and -maxDZ < rough_stock:
            rough_stock = -maxDZ

        while rough_again or roughing:

            if rough_again is False:
                roughing = False
                maxDZ = -1e10

            rough_again = False
            zmin += maxDZ

            loop_old = -1
            v_index = -1

            while v_index < len(new_coords) - 1:
                v_index += 1
                x1 = new_coords[v_index][0]
                y1 = new_coords[v_index][1]
                r1 = new_coords[v_index][2]
                loop = new_coords[v_index][3]

                if (v_index + 1) < len(new_coords):
                    nextr = new_coords[v_index + 1][2]
                else:
                    nextr = 0

                if bit_shape == "VBIT":
                    z1 = -r1 / tan(half_angle)
                    nextz = -nextr / tan(half_angle)
                    if settings.get('inlay'):
                        inlay_depth = settings.get('max_cut')
                        # inlay_depth = settings.get('v_max_cut')
                        z1 = z1 + inlay_depth
                        nextz = nextz + inlay_depth

                elif bit_shape == "BALL":
                    theta = acos(r1 / bit_radius)
                    z1 = -bit_radius * (1 - sin(theta))

                    next_theta = acos(nextr / bit_radius)
                    nextz = -bit_radius * (1 - sin(next_theta))

                elif bit_shape == "FLAT":
                    # This case should have been caught in the
                    # engraving section above
                    pass

                else:
                    pass

                if roughing:
                    z1 += rough_stock
                    nextz += rough_stock

                if z1 < zmin:
                    z1 = zmin
                    rough_again = True

                if nextz < zmin:
                    nextz = zmin
                    rough_again = True

                zmax = zmin - maxDZ  # + rough_stock
                if z1 > zmax and nextz > zmax and roughing:
                    loop_old = -1
                    continue

                # check and see if we need to move to a new discontinuous start point
                if loop != loop_old:
                    g.flush()

                    # lift engraver
                    code.append("G0 Z%s ( Safe Z )" % safe_val)

                    # rapid to current position
                    FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1))

                    # drop cutter to z depth
                    FORMAT = 'G1 Z%%.%df' % (dp)
                    code.append(FORMAT % z1)

                    # lastx = x1
                    # lasty = y1
                    # lastz = z1
                    g.cut(x1, y1, z1)
                else:
                    g.cut(x1, y1, z1)
                    # lastx = x1
                    # lasty = y1
                    # lastz = z1

                loop_old = loop

            g.flush()
        g.flush()
    g.flush()

    return code


def write_clean_up(job, bit_type="straight"):
    """
    Write clean-up G-Code
    """
    settings = job.settings
    code = []

    calc_depth_limit(job)
    depth = settings.get('max_cut')
    # depth = settings.get('v_max_cut')
    if settings.get('inlay'):
        depth = depth + settings.get('allowance')

    # accuracy = settings.get('accuracy')
    dp, dpfeed = get_nr_of_decimals(job)

    if bit_type == "straight":
        coords_out = job.clean_coords_sort
    else:
        coords_out = job.v_clean_coords_sort

    if settings.get('no_comments') is False:
        code.append('( Code generated by f-engrave-' + f_engrave_version() + '.py )')
        code.append('( by Scorch - 2017 )')
        code.append('( This file is a secondary operation for )')
        code.append('( cleaning up a V-carve. )')

        if bit_type == "straight":
            code.append('( The tool paths were calculated based )')
            code.append('( on using a bit with a )')
            code.append('( Diameter of %.4f %s)' % (settings.get('clean_dia'), settings.get('units')))
        else:
            code.append('( The tool paths were calculated based )')
            code.append('( on using a v-bit with a)')
            code.append('( angle of %.4f Degrees)' % settings.get('v_bit_angle'))

        code.append("(==========================================)")

    safe_z = settings.get('zsafe')
    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % safe_z
        # depth_val = FORMAT % depth
    else:
        FORMAT = '#1 = %%.%df  ( Safe Z )' % dp
        code.append(FORMAT % safe_z)
        safe_val = '#1'

    code.append("(##########################################)")

    # G90  ; Sets absolute distance mode
    code.append('G90')

    # G91.1  ; Sets Incremental Distance Mode for I, J & K arc offsets.
    if settings.get('arc_fit') == "center":
        code.append('G91.1')

    if settings.get('units') == "in":
        # G20  ; sets units to inches
        code.append('G20')
    else:
        # G21  ; sets units to mm
        code.append('G21')

    for line in settings.get('gcode_preamble').split('|'):
        code.append(line)

    # code.append( 'G0 Z%s' %(safe_val))

    FORMAT = '%%.%df' % (dp)
    feed_str = FORMAT % settings.get('feedrate')
    plunge_str = FORMAT % settings.get('plunge_rate')
    feed_current = FORMAT % 0.0
    if plunge_str == feed_current:
        plunge_str = feed_str

    # Multipass stuff

    # Cleanup
    maxDZ = settings.get('v_max_cut')
    rough_stock = settings.get('v_rough_stk')
    zmin = 0.0
    roughing = True
    rough_again = False
    if rough_stock > 0:
        rough_again = True

    if rough_stock > 0 and -maxDZ < rough_stock:
        rough_stock = -maxDZ

    while rough_again or roughing:

        if rough_again is False:
            roughing = False
            maxDZ = -1e10

        rough_again = False
        zmin += maxDZ

        # code.append( 'G0 Z%s' % safe_val)
        # oldx = oldy = -1e10
        # first_stroke = True

        # The clean coords have already been sorted so we can just write them
        order_out = sort_paths(coords_out, 3)
        new_coords = []
        for line in order_out:
            if line[0] < line[1]:
                step = 1
            else:
                step = -1
            for i in range(line[0], line[1] + step, step):
                new_coords.append(coords_out[i])
        coords_out = new_coords

        if len(coords_out) > 0:

            loop_old = -1
            v_index = -1

            while v_index < len(coords_out) - 1:
                v_index += 1
                x1 = coords_out[v_index][0]
                y1 = coords_out[v_index][1]
                # r1 = coords_out[v_index][2]
                loop = coords_out[v_index][3]

                # check and see if we need to move to a new discontinuous start point
                if loop != loop_old:

                    # lift engraver
                    code.append("G0 Z%s" % safe_val)

                    # rapid to current position
                    FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1))

                    z1 = depth
                    if roughing:
                        z1 = depth + rough_stock  # depth

                    if z1 < zmin:
                        z1 = zmin
                        rough_again = True

                    FORMAT = '%%.%df' % dp
                    depth_val = FORMAT % z1

                    if feed_current == plunge_str:
                        feed_string = ""
                    else:
                        feed_string = " F" + plunge_str
                        feed_current = plunge_str

                    code.append("G1 Z%s" % (depth_val) + feed_string)
                    # lastx = x1
                    # lasty = y1
                else:
                    if feed_str == feed_current:
                        feed_string = ""
                    else:
                        feed_string = " F" + feed_str
                        feed_current = feed_str

                    FORMAT = 'G1 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1) + feed_string)
                    # lastx = x1
                    # lasty = y1

                loop_old = loop

    code.append('G0 Z%s' % safe_val)  # final engraver up

    for line in settings.get('gcode_postamble').split('|'):
        code.append(line)

    return code


def calc_vbit_dia(job):
    settings = job.settings

    bit_shape = settings.get('bit_shape')
    bit_dia = settings.get('v_bit_dia')
    depth_lim = settings.get('v_depth_lim')
    half_angle = radians(settings.get('v_bit_angle') / 2.0)

    if settings.get('inlay') and bit_shape == "VBIT":
        allowance = settings.get('allowance')
        bit_dia = -2 * allowance * tan(half_angle)
        bit_dia = max(bit_dia, 0.001)

    elif depth_lim < 0.0:

        if bit_shape == "VBIT":
            bit_dia = -2 * depth_lim * tan(half_angle)

        elif bit_shape == "BALL":
            R = bit_dia / 2.0
            if depth_lim > -R:
                bit_dia = 2 * sqrt(R ** 2 - (R + depth_lim) ** 2)
            else:
                bit_dia = float(self.v_bit_dia.get())

        elif bit_shape == "FLAT":
            R = bit_dia / 2.0
        else:
            pass

    return bit_dia

# TODO calc_depth_limit in Gui too


def calc_depth_limit(job):
    """
    Calculate depth limit
    Returns True if the resulting depth limit is valid, otherwise False
    """
    settings = job.settings

    try:
        depth_lim_in = settings.get('v_depth_lim')
        bit_shape = settings.get('bit_shape')
        v_bit_dia = settings.get('v_bit_dia')
        v_bit_angle = settings.get('v_bit_angle')

        if bit_shape == "VBIT":
            half_angle = radians(v_bit_angle) / 2.0
            bit_depth = -v_bit_dia / 2.0 / tan(half_angle)
        elif bit_shape == "BALL":
            bit_depth = -v_bit_dia / 2.0
        elif bit_shape == "FLAT":
            bit_depth = -v_bit_dia.get / 2.0
        else:
            pass

        if bit_shape == "FLAT":
            if depth_lim_in < 0.0:
                depth_limit = depth_lim_in
            else:
                depth_limit = bit_depth
        else:
            if depth_lim_in < 0.0:
                depth_limit = max(bit_depth, depth_lim_in)
            else:
                depth_limit = bit_depth

        depth_limit = "%.3f" % depth_limit
        settings.set('max_cut', depth_limit)
        return True

    except:
        # depth_limit = "error"
        return False


def calc_r_inlay_top(job):
    half_angle = radians(job.settings.get('v_bit_angle') / 2.0)
    inlay_depth = job.settings.get('inlay')
    r_inlay_top = tan(half_angle) * inlay_depth
    return r_inlay_top


def get_nr_of_decimals(job):
    if job.settings.get('units') == "in":
        dp = 4
        dpfeed = 2
    else:
        dp = 3
        dpfeed = 1
    return dp, dpfeed


class Gcode:

    def __init__(self,
                 safetyheight=0.04,
                 tolerance=0.001,
                 target=lambda s: sys.stdout.write(s + "\n"),
                 arc_fit="none"
                 ):

        self.lastx = self.lasty = self.lastz = self.lastf = None
        self.feed = None
        self.lastgcode = self.lastfeed = None
        self.plane = None
        self.cuts = []
        self.dp = 4
        self.dpfeed = 2

        self.safetyheight = self.lastz = safetyheight
        self.tolerance = tolerance
        self.write = target
        self.arc_fit = arc_fit

    def set_plane(self, p):
        if (self.arc_fit != "none"):
            assert p in (17, 18, 19)
            if p != self.plane:
                self.plane = p
                self.write("G%d" % p)

    def flush(self):
        '''
        If any 'cut' moves are stored up, send them to the simplification algorithm
        and actually output them.
        This function is usually used internally (e.g., when changing from a cut
        to a rapid) but can be called manually as well.  For instance, when
        a contouring program reaches the end of a row, it may be desirable to enforce
        that the last 'cut' coordinate is actually in the output file, and it may
        give better performance because this means that the simplification algorithm
        will examine fewer points per run.
        '''
        if not self.cuts:
            return

        for move, (x, y, z), cent in douglas(self.cuts, self.tolerance, self.plane):
            if cent:
                self._move_common(x, y, z, i=cent[0], j=cent[1], gcode=move)
            else:
                self._move_common(x, y, z, gcode="G1")

        self.cuts = []

    def end(self):
        self.flush()
        self.safety()

    def rapid(self, x=None, y=None, z=None):
        """Perform a rapid move to the specified coordinates"""
        self.flush()
        self._move_common(x, y, z, gcode="G0")

    def _move_common(self, x=None, y=None, z=None, i=None, j=None, gcode="G0"):
        """
        G0 and G1 moves
        """
        xstring = ystring = zstring = Istring = Jstring = Rstring = fstring = ""
        if x is None:
            x = self.lastx
        if y is None:
            y = self.lasty
        if z is None:
            z = self.lastz

        if (self.feed != self.lastf):
            fstring = self.feed
            self.lastf = self.feed

        FORMAT = "%%.%df" % (self.dp)

        if (gcode == "G2" or gcode == "G3"):
            XC = self.lastx + i
            YC = self.lasty + j
            R_check_1 = sqrt((XC - self.lastx) ** 2 + (YC - self.lasty) ** 2)
            R_check_2 = sqrt((XC - x) ** 2 + (YC - y) ** 2)

            Rstring = " R" + FORMAT % ((R_check_1 + R_check_2) / 2.0)
            if abs(R_check_1 - R_check_2) > Zero:
                fmessage("-- G-Code Curve Fitting Anomaly - Check Output --")
                fmessage("R_start: %f R_end %f" % (R_check_1, R_check_2))
                fmessage("Begining and end radii do not match: delta = %f" % (abs(R_check_1 - R_check_2)))

        if x != self.lastx:
            xstring = " X" + FORMAT % (x)
            self.lastx = x
        if y != self.lasty:
            ystring = " Y" + FORMAT % (y)
            self.lasty = y
        if z != self.lastz:
            zstring = " Z" + FORMAT % (z)
            self.lastz = z
        if i is not None:
            Istring = " I" + FORMAT % (i)
        if j is not None:
            Jstring = " J" + FORMAT % (j)
        if xstring == ystring == zstring == fstring == "":
            return

        if (self.arc_fit == "radius"):
            cmd = "".join([gcode, xstring, ystring, zstring, Rstring, fstring])
        else:
            cmd = "".join([gcode, xstring, ystring, zstring, Istring, Jstring, fstring])

        if cmd:
            self.write(cmd)

    def set_feed(self, feed):
        self.flush()
        self.feed = "F%s" % feed
        self.lastf = None

    def cut(self, x=None, y=None, z=None):
        """
        Perform a cutting move at the specified feed rate to the specified coordinates
        """
        if self.cuts:
            lastx, lasty, lastz = self.cuts[-1]
        else:
            lastx, lasty, lastz = self.lastx, self.lasty, self.lastz
        if x is None:
            x = lastx
        if y is None:
            y = lasty
        if z is None:
            z = lastz
        self.cuts.append([x, y, z])

    def safety(self):
        '''Go to the 'safety' height at rapid speed'''
        self.flush()
        self.rapid(z=self.safetyheight)
