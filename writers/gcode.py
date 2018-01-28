from math import hypot

from geometry import Zero
from geometry.pathsorter import sort_paths
from geometry.linearcfitter import line_arc_fit

from util import fmessage


def gcode(job):
    settings = job.settings

    code = []

    code.append(settings.to_gcode())

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

    # The actual cutting is done here.
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

    if settings.get('units') == 'in':
        dp = 4
        dpfeed = 2
    else:
        dp = 3
        dpfeed = 1

    SafeZ = settings.get('zsafe')
    Depth = settings.get('zcut')

    if not settings.get('var_dis'):
        FORMAT = '%%.%df' % dp
        safe_val = FORMAT % SafeZ
        depth_val = FORMAT % Depth
    else:
        raise Exception('Not implemented')
        FORMAT = '#1 = %%.%df  ( Safe Z )' % (dp)
        code.append(FORMAT % SafeZ)
        FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' % (dp)
        code.append(FORMAT % Depth)
        safe_val = '#1'
        depth_val = '#2'

    FORMAT = 'F%%.%df  ( Set Feed Rate )' % dpfeed
    code.append("(#########################################################)")
    code.append(FORMAT % settings.get('feedrate'))
    code.append('G0 Z%s' % safe_val)

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

    code.append("G0 Z%s" % settings.get('zsafe'))

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
                    code.append("G0 Z%s" % settings.get('zsafe'))
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
    code = []
    return code
