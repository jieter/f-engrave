import sys
import datetime
from math import hypot, tan, radians, sqrt

from geometry import *
from geometry.pathsorter import sort_paths
from geometry.linearcfitter import line_arc_fit

from util import date_and_time, fmessage, icon


def gcode(job):
    settings = job.settings

    code = []

    code += settings.to_gcode()

    code.append("(#########################################################)")
    code.append('( F-Engrave G-Code, generated %s )' % date_and_time())
    code.append("(#########################################################)")

    # G90 Sets absolute distance mode
    code.append('G90')

    if settings.get('arc_fit'):
        # G91.1 Sets Incremental Distance Mode for I, J & K arc offsets.
        code.append('G91.1')

    if settings.get('units') == "in":
        # G20 sets units to inches
        code.append('G20')
    else:
        # G21 sets units to mm
        code.append('G21')

    for line in settings.get('gcode_preamble').split('|'):
        code.append(line)

    # The actual cutting is done here:
    if settings.get('cut_type') == "engrave":
        code.extend(engrave_gcode(job))
    else:
        code.extend(vcarve_gcode(job))

    for line in settings.get('gcode_postamble').split('|'):
        code.append(line)

    return code


def engrave_gcode(job):

    settings = job.settings
    accuracy = settings.get('accuracy')

    code = []

    # number of decimals
    if settings.get('units') == 'in':
        dp = 4
        dpfeed = 2
    else:
        dp = 3
        dpfeed = 1

    SafeZ = settings.get('zsafe')
    Depth = settings.get('zcut')

    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % SafeZ
        depth_val = FORMAT % Depth
    else:
        raise Exception('Not implemented')

        FORMAT = '#1 = %%.%df  ( safe Z )' % (dp)
        code.append(FORMAT % SafeZ)

        FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' % (dp)
        code.append(FORMAT % Depth)
        safe_val = '#1'
        depth_val = '#2'

    FORMAT = 'F%%.%df  ( Set Feed Rate )' % dpfeed
    code.append("(#########################################################)")
    code.append(FORMAT % settings.get('feedrate'))

    oldx = oldy = -1.0e5
    first_stroke = True

    # Create ECOORDS
    loop = 0
    ecoords = []
    for line in job.coords:
        x1, y1, x2, y2 = line[0:4]

        dx = oldx - x1
        dy = oldy - y1
        distance = hypot(dx, dy)
        # check and see if we need to move to a new discontinuous start point
        if (distance > accuracy) or first_stroke:
            loop = loop + 1
            first_stroke = False
            ecoords.append([x1, y1, loop])

        ecoords.append([x2, y2, loop])
        oldx, oldy = x2, y2

    order_out = sort_paths(ecoords)

    dist = 999
    lastx = -999
    lasty = -999
    lastz = 0
    z1 = 0
    nextz = 0

    # lift engraver
    # code.append("G0 Z%s ( safe Z )" % safe_val)

    for line in order_out:
        temp = line
        if temp[0] > temp[1]:
            step = -1
        else:
            step = 1

        R_last = 999
        x_center_last = 999
        y_center_last = 999
        FLAG_arc = 0
        FLAG_line = 0
        arccode = " "

        loop_old = -1
        for i in range(temp[0], temp[1] + step, step):
            x1 = ecoords[i][0]
            y1 = ecoords[i][1]
            loop = ecoords[i][2]

            if (i + 1 < temp[1] + step):
                nextx = ecoords[i + 1][0]
                nexty = ecoords[i + 1][1]
                nextloop = ecoords[i + 1][2]
            else:
                nextx = 0
                nexty = 0
                nextloop = -99  # don't change this dummy number it is used below

            # check and see if we need to move to a new discontinuous start point
            if loop != loop_old:
                dx = x1 - lastx
                dy = y1 - lasty
                dist = hypot(dx, dy)
                if dist > accuracy:
                    # lift engraver
                    code.append("G0 Z%s ( safe Z )" % safe_val)

                    # rapid to current position
                    FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1))

                    # drop cutter
                    code.append('G1 Z%s' % (depth_val))

                    x_center_last = 0
                    y_center_last = 0
                    R_last = 0
                    FLAG_arc = 0
                    FLAG_line = 0
                    arccode = " "
                    lastx = x1
                    lasty = y1
            else:
                # Line fit and arc fit (curve fit)
                [arccode, FLAG_arc, R_last, x_center_last, y_center_last, WRITE, FLAG_line] = \
                    line_arc_fit(lastx, lasty, lastz, x1, y1, z1,
                                 nextx, nexty, nextz,
                                 FLAG_arc, arccode,
                                 R_last, x_center_last, y_center_last, FLAG_line, accuracy)

                if (WRITE == 1 or nextloop == -99):
                    if arccode in ('G2', 'G3'):
                        R_check_1 = abs((x1 - x_center_last) ** 2 + (y1 - y_center_last) ** 2 - R_last ** 2)
                        R_check_2 = abs((lastx - x_center_last) ** 2 + (lasty - y_center_last) ** 2 - R_last ** 2)

                        if R_check_1 > Zero or R_check_2 > Zero:
                            fmessage("-- G-Code Curve Fitting Anomaly - Check Output --")
                            code.append('(---Curve Fitting Anomaly - Check Output. Error = %.6f ---)' % (
                                max(R_check_1, R_check_2)))

                            FORMAT = 'G1 X%%.%df Y%%.%df' % (dp, dp)
                            code.append(FORMAT % (lastx, lasty))
                            code.append(FORMAT % (x1, y1))
                            code.append('(------------------ End Anomaly Resolution -------------------)')
                        else:
                            Ival = x_center_last - lastx
                            Jval = y_center_last - lasty
                            FORMAT = '%%s X%%.%df Y%%.%df I%%.%df J%%.%df' % (dp, dp, dp, dp)

                            code.append(FORMAT % (arccode, x1, y1, Ival, Jval))

                            # This is the code for the old format for arcs
                            # FORMAT = '%%s X%%.%df Y%%.%df R%%.%df' %(dp, dp, dp)
                            # code.append(FORMAT %(code,x1,y1,R_last))
                    else:
                        FORMAT = 'G1 X%%.%df Y%%.%df' % (dp, dp)
                        code.append(FORMAT % (x1, y1))
                    x_center_last = 0
                    y_center_last = 0
                    R_last = 0
                    FLAG_arc = 0
                    FLAG_line = 0
                    arccode = " "
                    lastx = x1
                    lasty = y1
                # End Line and Arc Fitting

            loop_old = loop

    # Make Circle
    xorigin, yorigin = settings.get('xorigin'), settings.get('yorigin')
    plot_radius = settings.get('text_radius')

    if plot_radius != 0 and settings.get('cut_type') == "engrave":
        code.append('( Engraving Circle )')
        code.append('G0 Z%s' % safe_val)

        FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
        code.append(FORMAT % (-plot_radius - job.xzero + xorigin, yorigin - job.yzero))
        code.append('G1 Z%s' % depth_val)
        FORMAT = 'G2 I%%.%df J%%.%df' % (dp, dp)
        code.append(FORMAT % (plot_radius, 0.0))
    # End Circle

    # final engraver up
    code.append('G0 Z%s' % safe_val)

    return code


def vcarve_gcode(job):

    settings = job.settings
    accuracy = settings.get('accuracy')

    code = []

    # number of decimals
    if settings.get('units') == 'in':
        dp = 4
        dpfeed = 2
    else:
        dp = 3
        dpfeed = 1

    SafeZ = settings.get('zsafe')
    Depth = settings.get('zcut')

    # g_target = lambda s: sys.stdout.write(s + "\n") #TEST
    g = Gcode(safetyheight=SafeZ,
              tolerance=accuracy,
              target=lambda s: code.append(s),
              arc_fit=settings.get('arc_fit') )
    g.dp = dp
    g.dpfeed = dpfeed
    g.set_plane(17)

    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % SafeZ
        # depth_val = FORMAT % Depth
    else:
        FORMAT = '#1 = %%.%df  ( safe Z )' % (dp)
        code.append(FORMAT % SafeZ)
        FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' % (dp)
        code.append(FORMAT % Depth)
        safe_val = '#1'
        # depth_val = '#2'

    FORMAT = 'F%%.%df  ( Set Feed Rate )' % dpfeed
    code.append("(#########################################################)")
    code.append(FORMAT % settings.get('feedrate'))
    # lift engraver
    # code.append('G0 Z%s' % safe_val)

    #########################
    ###  find loop ends   ###
    #########################
    Lbeg = []
    Lend = []
    Lbeg.append(0)
    if job.number_of_v_coords() > 0:
        loop_old = job.vcoords[0][3]
        for i in range(1, job.number_of_v_coords() ):
            loop = job.vcoords[i][3]
            if loop != loop_old:
                Lbeg.append(i)
                Lend.append(i - 1)
            loop_old = loop
        Lend.append(i)

        #####################################################
        # Find new order based on distance to next begining #
        #####################################################
        order_out = []
        order_out.append([Lbeg[0], Lend[0]])
        inext = 0
        total = len(Lbeg)
        for i in range(total - 1):
            ii = Lend.pop(inext)
            Lbeg.pop(inext)
            Xcur = job.vcoords[ii][0]
            Ycur = job.vcoords[ii][1]

            dx = Xcur - job.vcoords[Lbeg[0]][0]
            dy = Ycur - job.vcoords[Lbeg[0]][1]
            min_dist = dx * dx + dy * dy

            inext = 0
            for j in range(1, len(Lbeg)):
                dx = Xcur - job.vcoords[Lbeg[j]][0]
                dy = Ycur - job.vcoords[Lbeg[j]][1]
                dist = dx * dx + dy * dy
                if dist < min_dist:
                    min_dist = dist
                    inext = j
            order_out.append([Lbeg[inext], Lend[inext]])
        #####################################################

        new_coords = []
        for line in order_out:
            temp = line
            for i in range(temp[0], temp[1] + 1):
                new_coords.append(job.vcoords[i])

        bit_shape = settings.get('bit_shape')
        half_angle = radians(settings.get('v_bit_angle') / 2.0)
        bit_radius = settings.get('v_bit_dia') / 2.0

        zmin = 0.0
        maxDZ = settings.get('v_max_cut')
        roughing = True
        rough_again = False
        rough_stock = settings.get('v_rough_stk')

        if rough_stock > 0:
            rough_again = True

        if (rough_stock > 0) and (-maxDZ < rough_stock):
            rough_stock = -maxDZ

        while rough_again or roughing:
            if rough_again == False:
                roughing = False
                maxDZ = -99999
            rough_again = False
            zmin = zmin + maxDZ

            loop_old = -1

            #TODO These variables are set, but not used?
            # R_last = 999
            # x_center_last = 999
            # y_center_last = 999
            # FLAG_arc = 0
            # FLAG_line = 0
            # code = []

            v_index = -1

            while v_index < len(new_coords) - 1:
                v_index = v_index + 1
                x1 = new_coords[v_index][0]
                y1 = new_coords[v_index][1]
                r1 = new_coords[v_index][2]
                loop = new_coords[v_index][3]

                if (v_index + 1) < len(new_coords):
                    nextx = new_coords[v_index + 1][0]
                    nexty = new_coords[v_index + 1][1]
                    nextr = new_coords[v_index + 1][2]
                    nextloop = new_coords[v_index + 1][3]
                else:
                    nextx = 0
                    nexty = 0
                    nextr = 0
                    nextloop = -99  # don't change this dummy number it is used below

                if bit_shape == "VBIT":
                    z1 = -r1 / tan(half_angle)
                    nextz = -nextr / tan(half_angle)
                    if settings.get('inlay'):
                        inlay_depth = settings.get('inlay')
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
                    z1 = z1 + rough_stock
                    nextz = nextz + rough_stock
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
                    code.append("G0 Z%s ( safe Z )" % (safe_val))

                    # rapid to current position
                    FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1))

                    # drop cutter to z depth
                    FORMAT = 'G1 Z%%.%df' % (dp)
                    code.append(FORMAT % (z1))

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

    code.append('G0 Z%s' % safe_val)  # final engraver up

    return code


def write_clean_up(job, bit_type="straight"):
    '''
    Write Cleanup G-code File
    '''
    settings = job.settings

    code = []

    SafeZ = settings.get('zsafe')
    BitDia = settings.get('clean_dia')

    calc_depth_limit(job)
    Depth = settings.get('v_max_cut')
    if settings.get('inlay'):
        Depth = Depth + settings.get('allowance')

    Units = settings.get('units')

    if bit_type== "straight":
        coords_out = job.clean_coords_sort
    else:
        coords_out = job.v_clean_coords_sort

    if settings.get('no_comments') == False:
        code.append('( Code generated by f-engrave-' + version + '.py )')
        code.append('( by Scorch - 2017 )')
        code.append('( This file is a secondary operation for )')
        code.append('( cleaning up a V-carve. )')

        if bit_type == "straight":
            code.append('( The tool paths were calculated based )')
            code.append('( on using a bit with a )')
            code.append('( Diameter of %.4f %s)' % (BitDia, Units))
        else:
            code.append('( The tool paths were calculated based )')
            code.append('( on using a v-bit with a)')
            code.append('( angle of %.4f Degrees)' % settings.get('v_bit_angle'))

        code.append("(==========================================)")

    # number of decimals
    if Units == "in":
        dp = 4
        dpfeed = 2
    else:
        dp = 3
        dpfeed = 1

    if settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % SafeZ
        depth_val = FORMAT % Depth
    else:
        FORMAT = '#1 = %%.%df  ( Safe Z )' % (dp)
        code.append(FORMAT % (SafeZ))
        safe_val = '#1'

    code.append("(##########################################)")

    # G90  ; sets absolute distance mode
    code.append('G90')

    # G91.1  ; sets Incremental Distance Mode for I, J & K arc offsets.
    if settings.get('arc_fit') == "center":
        code.append('G91.1')
    
    if Units == "in":
        # G20  ; sets units to inches
        code.append('G20')
    else:
        # G21  ; sets units to mm
        code.append('G21')

    for line in settings.get('gcode_preamble').split('|'):
        code.append(line)

    # initial feedrate
    FORMAT = '%%.%df' % (dpfeed)
    feed_str = FORMAT % settings.get('feedrate')
    code.append("F" + feed_str)

    code.append("(##########################################)")

    plunge_str = FORMAT % settings.get('plunge_rate')
    feed_current = FORMAT % (float(0.0))
    # fmessage(feed_str +" "+plunge_str)
    if plunge_str == feed_current:
        plunge_str = feed_str

    ###################
    # Multipass stuff #
    ###################

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

        if not rough_again:
            roughing = False
            maxDZ = -99999

        rough_again = False
        zmin = zmin + maxDZ

        # code.append( 'G0 Z%s' %(safe_val))
        oldx = oldy = -99990.0
        first_stroke = True

        ########################################################################
        # The clean coords have already been sorted so we can just write them  #
        ########################################################################
        order_out = sort_paths(coords_out, 3)  # TODO
        new_coords = []
        for line in order_out:
            temp = line
            if temp[0] < temp[1]:
                step = 1
            else:
                step = -1
            for i in range(temp[0], temp[1] + step, step):
                new_coords.append(coords_out[i])
        coords_out = new_coords

        # TODO FLAG_, next_, and last_ vars are not used
        if len(coords_out) > 0:
            loop_old = -1
            # FLAG_arc = 0
            # FLAG_line = 0
            # code = []
            v_index = -1
            while v_index < len(coords_out) - 1:
                v_index = v_index + 1
                x1 = coords_out[v_index][0]
                y1 = coords_out[v_index][1]
                r1 = coords_out[v_index][2]
                loop = coords_out[v_index][3]

                #TODO Variables are set, but not used?
                # if v_index + 1 < len(coords_out):
                #     nextx = coords_out[v_index + 1][0]
                #     nexty = coords_out[v_index + 1][1]
                #     nextr = coords_out[v_index + 1][2]
                #     nextloop = coords_out[v_index + 1][3]
                # else:
                #     nextx = 0
                #     nexty = 0
                #     nextr = 0
                #     nextloop = -99

                # check and see if we need to move to a new discontinuous start point
                if loop == loop_old:
                    if feed_str == feed_current:
                        FEED_STRING = ""
                    else:
                        FEED_STRING = " F" + feed_str
                        feed_current = feed_str

                    FORMAT = 'G1 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1) + FEED_STRING)
                    # lastx = x1
                    # lasty = y1
                else:
                    # lift engraver
                    code.append("G0 Z%s" % (safe_val))

                    # rapid to current position
                    FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                    code.append(FORMAT % (x1, y1))

                    z1 = Depth
                    if roughing:
                        z1 = Depth + rough_stock  # Depth
                    if z1 < zmin:
                        z1 = zmin
                        rough_again = True

                    FORMAT = '%%.%df' % (dp)
                    depth_val = FORMAT % (z1)

                    if feed_current == plunge_str:
                        FEED_STRING = ""
                    else:
                        FEED_STRING = " F" + plunge_str
                        feed_current = plunge_str

                    code.append("G1 Z%s" % (depth_val) + FEED_STRING)

                    # lastx = x1
                    # lasty = y1

                loop_old = loop

    # End multipass loop

    code.append('G0 Z%s' % (safe_val))  # final engraver up

    for line in settings.get('gcode_postamble').split('|'):
        code.append(line)

    return code


def calc_depth_limit(job):
    try:
        settings = job.settings

        bit_shape = settings.get('bit_shape')

        if bit_shape == "VBIT":
            half_angle = radians( settings.get('v_bit_angle') / 2.0 )
            bit_depth = -settings.get('v_bit_dia') / 2.0 / tan(half_angle)
        elif bit_shape == "BALL":
            bit_depth = -settings.get('v_bit_dia') / 2.0
        elif bit_shape() == "FLAT":
            bit_depth = -settings.get('v_bit_dia') / 2.0
        else:
            pass

        depth_lim = settings.get('v_depth_lim')
        if bit_shape == "FLAT":
            if depth_lim < 0.0:
                # self.maxcut.set("%.3f" % (depth_lim))
                settings.set('v_max_cut', "%.3f" % depth_lim)
            else:
                # self.maxcut.set("%.3f" % (bit_depth))
                settings.set('v_max_cut', "%.3f" % bit_depth)
        else:
            if depth_lim < 0.0:
                # self.maxcut.set("%.3f" % (max(bit_depth, depth_lim)))
                settings.set('v_max_cut', "%.3f" % max(bit_depth, depth_lim))
            else:
                # self.maxcut.set("%.3f" % (bit_depth))
                settings.set('v_max_cut', "%.3f" % bit_depth)

        # TODO set maxcut in GUI (using settings)
        # self.maxcut.set("%.3f" % (depth_lim))
        # settings.get('v_max_cut')
        # self.maxcut.set(settings.get('v_max_cut'))

    except:
        settings.set('v_max_cut', "error")


def calc_r_inlay_top(job):
    half_angle = radians(job.settings.get('.v_bit_angle') / 2.0)
    inlay_depth = job.settings.get('inlay')
    r_inlay_top = tan(half_angle) * inlay_depth
    return r_inlay_top


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
                self._move_common(x, y, z, I=cent[0], J=cent[1], gcode=move)
            else:
                self._move_common(x, y, z, gcode="G1")

        self.cuts = []

    def end(self):
        self.flush()
        self.safety()

    def rapid(self, x=None, y=None, z=None):
        '''Perform a rapid move to the specified coordinates'''
        self.flush()
        self._move_common(x, y, z, gcode="G0")

    def _move_common(self, x=None, y=None, z=None, I=None, J=None, gcode="G0"):
        '''
        G0 and G1 moves
        '''
        xstring = ystring = zstring = Istring = Jstring = Rstring = fstring = ""
        if x is None: x = self.lastx
        if y is None: y = self.lasty
        if z is None: z = self.lastz

        if (self.feed != self.lastf):
            fstring = self.feed
            self.lastf = self.feed

        FORMAT = "%%.%df" % (self.dp)

        if (gcode == "G2" or gcode == "G3"):
            XC = self.lastx + I
            YC = self.lasty + J
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
        if I != None:
            Istring = " I" + FORMAT % (I)
        if J != None:
            Jstring = " J" + FORMAT % (J)
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
        '''
        Perform a cutting move at the specified feed rate to the specified coordinates
        '''
        if self.cuts:
            lastx, lasty, lastz = self.cuts[-1]
        else:
            lastx, lasty, lastz = self.lastx, self.lasty, self.lastz
        if x is None: x = lastx
        if y is None: y = lasty
        if z is None: z = lastz
        self.cuts.append([x, y, z])

    def safety(self):
        '''Go to the 'safety' height at rapid speed'''
        self.flush()
        self.rapid(z=self.safetyheight)


def douglas(st, tolerance=.001, plane=None, _first=True):
    '''
    Perform Douglas-Peucker simplification on the path 'st' with the specified
    tolerance.  The '_first' argument is for internal use only.

    The Douglas-Peucker simplification algorithm finds a subset of the input points
    whose path is never more than 'tolerance' away from the original input path.

    If 'plane' is specified as 17, 18, or 19, it may find helical arcs in the given
    plane in addition to lines.

    -- I [scorch] modified the code so the note below does not apply when using plane 17 --
    Note that if there is movement in the plane
    perpendicular to the arc, it will be distorted, so 'plane' should usually
    be specified only when there is only movement on 2 axes
    '''

    if len(st) == 1:
        yield "G1", st[0], None
        return
    # if len(st) < 1:
    #    print "whaaaa!?"
    #    #yield "G1", st[0], None
    #    return

    L1 = st[0]
    L2 = st[-1]

    last_point = None
    while (abs(L1[0] - L2[0]) < Zero) \
            and (abs(L1[1] - L2[1]) < Zero) \
            and (abs(L1[2] - L2[2]) < Zero):
        last_point = st.pop()
        try:
            L2 = st[-1]
        except:
            return

    worst_dist = 0
    worst_distz = 0  # added to fix out of plane inaccuracy problem
    worst = 0
    min_rad = MAXINT
    max_arc = -1

    ps = st[0]
    pe = st[-1]

    for i, p in enumerate(st):
        if p is L1 or p is L2: continue
        dist = dist_lseg(L1, L2, p)
        distz = dist_lseg(L1, L2, p, z_only=True)  # added to fix out of plane inacuracy problem
        if dist > worst_dist:
            worst = i
            worst_dist = dist
            rad = arc_rad(plane, ps, p, pe)
            if rad < min_rad:
                max_arc = i
                min_rad = rad
        if distz > worst_distz:  # added to fix out of plane inacuracy problem
            worst_distz = distz  # added to fix out of plane inacuracy problem

    worst_arc_dist = 0
    if min_rad != MAXINT:
        c1, c2 = arc_center(plane, ps, st[max_arc], pe)
        Lx, Ly, Lz = st[0]
        if one_quadrant(plane, (c1, c2), ps, st[max_arc], pe):
            for i, (x, y, z) in enumerate(st):
                if plane == 17:
                    dist1 = abs(hypot(c1 - x, c2 - y) - min_rad)
                    dist = sqrt(worst_distz ** 2 + dist1 ** 2)  # added to fix out of plane inacuracy problem
                elif plane == 18:
                    dist = abs(hypot(c1 - x, c2 - z) - min_rad)
                elif plane == 19:
                    dist = abs(hypot(c1 - y, c2 - z) - min_rad)
                else:
                    dist = MAXINT

                if dist > worst_arc_dist: worst_arc_dist = dist

                mx = (x + Lx) / 2
                my = (y + Ly) / 2
                mz = (z + Lz) / 2
                if plane == 17:
                    dist = abs(hypot(c1 - mx, c2 - my) - min_rad)
                elif plane == 18:
                    dist = abs(hypot(c1 - mx, c2 - mz) - min_rad)
                elif plane == 19:
                    dist = abs(hypot(c1 - my, c2 - mz) - min_rad)
                else:
                    dist = MAXINT
                Lx, Ly, Lz = x, y, z
        else:
            worst_arc_dist = MAXINT
    else:
        worst_arc_dist = MAXINT

    if worst_arc_dist < tolerance and worst_arc_dist < worst_dist:
        ccw = arc_dir(plane, (c1, c2), ps, st[max_arc], pe)
        if plane == 18:
            ccw = not ccw
        yield "G1", ps, None
        if ccw:
            yield "G3", st[-1], arc_fmt(plane, c1, c2, ps)
        else:
            yield "G2", st[-1], arc_fmt(plane, c1, c2, ps)
    elif worst_dist > tolerance:
        if _first: yield "G1", st[0], None
        for i in douglas(st[:worst + 1], tolerance, plane, False):
            yield i
        yield "G1", st[worst], None
        for i in douglas(st[worst:], tolerance, plane, False):
            yield i
        if _first: yield "G1", st[-1], None
    else:
        if _first: yield "G1", st[0], None
        if _first: yield "G1", st[-1], None

    if last_point != None:  # added to fix closed loop problem
        yield "G1", st[0], None  # added to fix closed loop problem
