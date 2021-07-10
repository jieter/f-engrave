import sys
from math import (
    atan, atan2, acos,
    sin, cos,
    radians, degrees,
    sqrt,
    ceil, floor
)

from geometry import get_angle, transform, Zero
from util import fmessage, VERSION

from readers.dxf.elements import *
from readers.dxf.nurbs import NURBSClass

if VERSION < 3 and sys.version_info[1] < 6:
    def next(item):
        return item.next()


class DXF_CLASS(object):

    def __init__(self):
        self.coords = []
        strings = []
        floats = []
        ints = []

        strings += list(range(0, 10))       # String (255 characters maximum; less for Unicode strings)
        floats += list(range(10, 60))       # Double precision 3D point
        ints += list(range(60, 80))         # 16-bit integer value
        ints += list(range(90, 100))        # 32-bit integer value
        strings += [100]                    # String (255 characters maximum; less for Unicode strings)
        strings += [102]                    # String (255 characters maximum; less for Unicode strings
        strings += [105]                    # String representing hexadecimal (hex) handle value
        floats += list(range(140, 148))     # Double precision scalar floating-point value
        ints += list(range(170, 176))       # 16-bit integer value
        ints += list(range(280, 290))       # 8-bit integer value
        strings += list(range(300, 310))    # Arbitrary text string
        strings += list(range(310, 320))    # String representing hex value of binary chunk
        strings += list(range(320, 330))    # String representing hex handle value
        strings += list(range(330, 369))    # String representing hex object IDs
        strings += [999]                    # Comment (string)
        strings += list(range(1000, 1010))  # String (255 characters maximum; less for Unicode strings)
        floats += list(range(1010, 1060))   # Floating-point value
        ints += list(range(1060, 1071))     # 16-bit integer value
        ints += [1071]                      # 32-bit integer value

        self.funs = []
        for i in range(0, 1072):
            self.funs.append(self.read_none)

        for i in strings:
            self.funs[i] = self.read_string

        for i in floats:
            self.funs[i] = self.read_float

        for i in ints:
            self.funs[i] = self.read_int

    def read_int(self, data):
        return int(float(data))

    def read_float(self, data):
        return float(data)

    def read_string(self, data):
        return str(data)

    def read_none(self, data):
        return None

    def read_dxf_data(self, fd, data):
        self.comment = "None"
        Skip = True
        fd_iter = iter(fd)
        for line in fd_iter:
            try:
                group_code = int(line)
                value = next(fd_iter).replace('\r', '')
                value = value.replace('\n', '')
                value = value.lstrip(' ')
                value = value.rstrip(' ')
                value = self.funs[group_code](value)
                if (value != "SECTION") and Skip:
                    if group_code == 999:
                        self.comment = value
                    continue
                else:
                    Skip = False
                data.append((group_code, value))
            except:
                pass

    def bulge_coords(self, x0, y0, x1, y1, bulge, tol_deg=20):

        # global Zero

        bcoords = []
        if bulge < 0.0:
            sign = 1
            bulge = abs(bulge)
            # bcoords.append([x0,y0,x1,y1])
            # return bcoords
        else:
            sign = -1

        dx = x1 - x0
        dy = y1 - y0
        c = sqrt(dx ** 2 + dy ** 2)
        alpha = 2.0 * (atan(bulge))
        R = c / (2 * sin(alpha))
        L = R * cos(alpha)
        steps = ceil(2 * alpha / radians(tol_deg))

        if abs(c) < Zero:
            phi = 0
            bcoords.append([x0, y0, x1, y1])
            return bcoords

        seg_sin = dy / c
        seg_cos = dx / c
        phi = get_angle(seg_sin, seg_cos)

        d_theta = 2 * alpha / steps
        theta = alpha - d_theta

        xa = x0
        ya = y0
        for i in range(1, int(steps)):
            xp = c / 2 - R * sin(theta)
            yp = R * cos(theta) - L
            xb, yb = transform(xp, yp * sign, radians(phi))
            xb = xb + x0
            yb = yb + y0

            bcoords.append([xa, ya, xb, yb])
            xa = xb
            ya = yb
            theta = theta - d_theta
        bcoords.append([xa, ya, x1, y1])
        return bcoords

    def GET_DXF_DATA(self, fd, tol_deg=20):
        data = []
        try:
            self.read_dxf_data(fd, data)
        except:
            fmessage("\nUnable to read input DXF data!")
            return 1

        data = iter(data)
        g_code, value = None, None
        sections = dict()

        he = Header()
        bl = Blocks()
        while value != "EOF":
            g_code, value = next(data)
            if value == "SECTION":
                g_code, value = next(data)
                sections[value] = []

                while value != "ENDSEC":
                    if value == "HEADER":
                        while True:
                            g_code, value = next(data)
                            if value == "ENDSEC":
                                break
                            elif g_code == 9:
                                he.new_var(value)
                            else:
                                he.new_val((g_code, value))

                    elif value == "BLOCKS":
                        while True:
                            g_code, value = next(data)
                            if value == "ENDSEC":
                                break
                            elif value == "ENDBLK":
                                continue
                            elif value == "BLOCK":
                                bl.new_block()
                            elif g_code == 0 and value != "BLOCK":
                                bl.new_entity(value)
                            else:
                                bl.update((g_code, value))

                    elif value == "ENTITIES":
                        TYPE = ""
                        en = Entities()
                        g_code_last = False
                        while True:
                            g_code, value = next(data)

                            if g_code == 0:
                                TYPE = value
                            if TYPE == "LWPOLYLINE" and g_code == 10 and g_code_last == 20:
                                # Add missing code 42
                                en.update((42, 0.0))
                            g_code_last = g_code

                            if value == "ENDSEC":
                                break
                            elif g_code == 0 and value != "ENDSEC":
                                en.new_entity(value)
                            else:
                                en.update((g_code, value))
                    try:
                        g_code, value = next(data)
                    except:
                        break

        for e in en.entities:
            # LINE ############
            if e.type == "LINE":
                x0 = e.data["10"]
                y0 = e.data["20"]
                x1 = e.data["11"]
                y1 = e.data["21"]
                self.coords.append([x0, y0, x1, y1])
            # ARC #############
            elif e.type == "ARC":
                x = e.data["10"]
                y = e.data["20"]
                r = e.data["40"]
                start = e.data["50"]
                end = e.data["51"]

                if end < start:
                    end = end + 360.0
                delta = end - start
                angle_steps = max(floor(delta / tol_deg), 2)

                start_r = radians(start)
                end_r = radians(end)

                step_phi = radians(delta / angle_steps)
                x0 = x + r * cos(start_r)
                y0 = y + r * sin(start_r)
                pcnt = 1
                while pcnt < angle_steps + 1:
                    phi = start_r + pcnt * step_phi
                    x1 = x + r * cos(phi)
                    y1 = y + r * sin(phi)
                    self.coords.append([x0, y0, x1, y1])
                    x0 = x1
                    y0 = y1
                    pcnt += 1

            # LWPOLYLINE ##########
            elif e.type == "LWPOLYLINE":
                flag = 0
                lpcnt = -1
                try:
                    xy_data = zip(e.data["10"], e.data["20"])
                except:
                    fmessage("DXF Import zero length %s ignored" % (e.type))
                    xy_data = []
                for x, y in xy_data:
                    x1 = x
                    y1 = y
                    lpcnt = lpcnt + 1
                    try:
                        bulge1 = e.data["42"][lpcnt]
                    except:
                        bulge1 = 0

                    if flag == 0:
                        x0 = x1
                        y0 = y1
                        bulge0 = bulge1
                        flag = 1
                    else:
                        if bulge0 != 0:
                            bcoords = self.bulge_coords(x0, y0, x1, y1, bulge0, tol_deg)
                            for line in bcoords:
                                self.coords.append(line)
                        else:
                            self.coords.append([x0, y0, x1, y1])
                        x0 = x1
                        y0 = y1
                        bulge0 = bulge1

                if e.data["70"] != 0:
                    try:
                        x1 = e.data["10"][0]
                        y1 = e.data["20"][0]
                    except:
                        x1 = e.data["10"]
                        y1 = e.data["20"]

                    if bulge0 != 0:
                        bcoords = self.bulge_coords(x0, y0, x1, y1, bulge1, tol_deg)
                        for line in bcoords:
                            self.coords.append(line)
                    else:
                        self.coords.append([x0, y0, x1, y1])

            # CIRCLE ############
            elif e.type == "CIRCLE":
                x = e.data["10"]
                y = e.data["20"]
                r = e.data["40"]

                start = 0
                end = 360
                if end < start:
                    end = end + 360.0
                delta = end - start
                angle_steps = max(floor(delta) / tol_deg, 2)

                start_r = radians(start)
                end_r = radians(end)

                step_phi = radians(delta / angle_steps)
                x0 = x + r * cos(start_r)
                y0 = y + r * sin(start_r)
                pcnt = 1
                while pcnt < angle_steps + 1:
                    phi = start_r + pcnt * step_phi
                    x1 = x + r * cos(phi)
                    y1 = y + r * sin(phi)
                    self.coords.append([x0, y0, x1, y1])
                    x0 = x1
                    y0 = y1
                    pcnt += 1

            # SPLINE ###########
            elif e.type == "SPLINE":
                self.Spline_flag = []
                self.degree = 1
                self.Knots = []
                self.Weights = []
                self.CPoints = []

                self.Spline_flag = int(e.data["70"])
                self.degree = int(e.data["71"])
                self.Knots = e.data["40"]
                try:
                    self.Weights = e.data["41"]
                except:
                    for K in self.Knots:
                        self.Weights.append(1)
                    pass

                try:
                    xy_data = zip(e.data["10"], e.data["20"])
                except:
                    fmessage("DXF Import zero length %s Ignored" % (e.type))
                    xy_data = []
                for x, y in xy_data:
                    self.CPoints.append(PointClass(float(x), float(y)))

                self.MYNURBS = NURBSClass(degree=self.degree,
                                          Knots=self.Knots,
                                          Weights=self.Weights,
                                          CPoints=self.CPoints)

                mypoints = self.MYNURBS.calc_curve(n=0, tol_deg=tol_deg)
                flag = 0
                for XY in mypoints:
                    x1 = XY.x
                    y1 = XY.y
                    if flag == 0:
                        x0 = x1
                        y0 = y1
                        flag = 1
                    else:
                        self.coords.append([x0, y0, x1, y1])
                        x0 = x1
                        y0 = y1

            # ELLIPSE ###########
            elif e.type == "ELLIPSE":
                # X and Y center points
                xcp = e.data["10"]
                ycp = e.data["20"]

                # X and Y of major axis end point
                xma = e.data["11"]
                yma = e.data["21"]

                # Ratio of minor axis to major axis
                ratio = e.data["40"]

                # Start and end angles (in radians 0 and 2pi for full ellipse)
                start = degrees(e.data["41"])
                end = degrees(e.data["42"])

                rotation = atan2(yma, xma)
                a = sqrt(xma ** 2 + yma ** 2)
                b = a * ratio

                # #################
                if end < start:
                    end = end + 360.0
                delta = end - start

                start_r = radians(start)
                end_r = radians(end)

                tol = radians(tol_deg)

                phi = start_r
                x1 = xcp + (a * cos(phi) * cos(rotation) - b * sin(phi) * sin(rotation))
                y1 = ycp + (a * cos(phi) * sin(rotation) + b * sin(phi) * cos(rotation))
                step = tol
                while phi < end_r:
                    if (phi + step > end_r):
                        step = end_r - phi

                    x2 = xcp + (a * cos(phi + step) * cos(rotation) - b * sin(phi + step) * sin(rotation))
                    y2 = ycp + (a * cos(phi + step) * sin(rotation) + b * sin(phi + step) * cos(rotation))

                    x_test = xcp + (a * cos(phi + step / 2) * cos(rotation) - b * sin(phi + step / 2) * sin(rotation))
                    y_test = ycp + (a * cos(phi + step / 2) * sin(rotation) + b * sin(phi + step / 2) * cos(rotation))

                    dx1 = (x_test - x1)
                    dy1 = (y_test - y1)
                    L1 = sqrt(dx1 * dx1 + dy1 * dy1)

                    dx2 = (x2 - x_test)
                    dy2 = (y2 - y_test)
                    L2 = sqrt(dx2 * dx2 + dy2 * dy2)

                    angle = acos(dx1 / L1 * dx2 / L2 + dy1 / L1 * dy2 / L2)

                    if angle > tol:
                        step = step / 2
                    else:
                        phi += step
                        self.coords.append([x1, y1, x2, y2])
                        step = step * 2
                        x1 = x2
                        y1 = y2

            # OLD_ELLIPSE ###########
            elif e.type == "OLD_ELLIPSE":
                # X and Y center points
                xcp = e.data["10"]
                ycp = e.data["20"]
                # X and Y of major axis end point
                xma = e.data["11"]
                yma = e.data["21"]
                # Ratio of minor axis to major axis
                ratio = e.data["40"]
                # Start and end angles (in radians 0 and 2pi for full ellipse)
                start = degrees(e.data["41"])
                end = degrees(e.data["42"])

                rotation = atan2(yma, xma)
                a = sqrt(xma ** 2 + yma ** 2)
                b = a * ratio

                ##################
                if end < start:
                    end = end + 360.0
                delta = end - start
                angle_steps = max(floor(delta / tol_deg), 2)

                start_r = radians(start)
                end_r = radians(end)

                step_phi = radians(delta / angle_steps)
                x0 = xcp + (a * cos(start_r) * cos(rotation) - b * sin(start_r) * sin(rotation))
                y0 = ycp + (a * cos(start_r) * sin(rotation) + b * sin(start_r) * cos(rotation))
                pcnt = 1
                while pcnt < angle_steps + 1:
                    phi = start_r + pcnt * step_phi
                    x1 = xcp + (a * cos(phi) * cos(rotation) - b * sin(phi) * sin(rotation))
                    y1 = ycp + (a * cos(phi) * sin(rotation) + b * sin(phi) * cos(rotation))
                    self.coords.append([x0, y0, x1, y1])
                    x0 = x1
                    y0 = y1
                    pcnt += 1

            # LEADER ###########
            elif e.type == "LEADER":
                flag = 0
                try:
                    xy_data = zip(e.data["10"], e.data["20"])
                except:
                    fmessage("DXF Import zero length %s Ignored" % (e.type))
                    xy_data = []
                for x, y in xy_data:
                    x1 = x
                    y1 = y
                    if flag == 0:
                        x0 = x1
                        y0 = y1
                        flag = 1
                    else:
                        self.coords.append([x0, y0, x1, y1])
                        x0 = x1
                        y0 = y1

            # POLYLINE ###########
            elif e.type == "POLYLINE":
                self.POLY_CLOSED = 0
                self.POLY_FLAG = -1
                try:
                    TYPE = e.data["70"]
                    if TYPE >= 128:
                        # print "#128 = The linetype pattern is generated continuously around the vertices of this polyline."
                        TYPE -= 128
                    if TYPE >= 64:
                        # print "#64 = The polyline is a polyface mesh."
                        TYPE -= 64
                    if TYPE >= 32:
                        # print "#32 = The polygon mesh is closed in the N direction."
                        TYPE -= 32
                    if TYPE >= 16:
                        # print "#16 = This is a 3D polygon mesh."
                        TYPE -= 16
                    if TYPE >= 8:
                        # print "#8 = This is a 3D polyline."
                        TYPE -= 8
                    if TYPE >= 4:
                        # print "#4 = Spline-fit vertices have been added."
                        TYPE -= 4
                    if TYPE >= 2:
                        # print "#2 = Curve-fit vertices have been added."
                        TYPE -= 2
                    if TYPE >= 1:
                        # print "#1 = This is a closed polyline (or a polygon mesh closed in the M direction)."
                        self.POLY_CLOSED = 1
                        TYPE -= 1
                except:
                    pass

            # SEQEND ###########
            elif e.type == "SEQEND":
                if (self.POLY_FLAG != 0):
                    self.POLY_FLAG = 0
                    if (self.POLY_CLOSED == 1):
                        self.POLY_CLOSED == 0
                        x0 = self.PX
                        y0 = self.PY
                        x1 = self.PX0
                        y1 = self.PY0

                        if self.bulge != 0:
                            bcoords = self.bulge_coords(x0, y0, x1, y1, self.bulge, tol_deg)
                            for line in bcoords:
                                self.coords.append(line)
                        else:
                            self.coords.append([x0, y0, x1, y1])

                else:
                    fmessage("DXF Import Ignored: - %s - Entity" % (e.type))

            # VERTEX ###########
            elif e.type == "VERTEX":

                if (self.POLY_FLAG == -1):
                    self.PX = e.data["10"]
                    self.PY = e.data["20"]
                    self.PX0 = self.PX
                    self.PY0 = self.PY
                    try:
                        self.bulge = e.data["42"]
                    except:
                        self.bulge = 0

                    self.POLY_FLAG = 1
                elif (self.POLY_FLAG == 1):
                    x0 = self.PX
                    y0 = self.PY
                    x1 = e.data["10"]
                    y1 = e.data["20"]
                    self.PX = x1
                    self.PY = y1

                    if self.bulge != 0:
                        bcoords = self.bulge_coords(x0, y0, x1, y1, self.bulge, tol_deg)
                        for line in bcoords:
                            self.coords.append(line)
                    else:
                        self.coords.append([x0, y0, x1, y1])

                    try:
                        self.bulge = e.data["42"]
                    except:
                        self.bulge = 0
                else:
                    fmessage("DXF Import Ignored: - %s - Entity" % (e.type))
                    pass
            # END VERTEX ###########
            else:
                fmessage("DXF Import Ignored: %s Entity" % (e.type))
                pass

    def DXF_COORDS_GET(self, new_origin=True):
        if new_origin is True:
            ymin = 99999
            xmin = 99999
            for line in self.coords:
                XY = line
                if XY[0] < xmin:
                    xmin = XY[0]
                if XY[1] < ymin:
                    ymin = XY[1]
                if XY[2] < xmin:
                    xmin = XY[2]
                if XY[3] < ymin:
                    ymin = XY[3]
        else:
            xmin = 0
            ymin = 0

        coords_out = []
        for line in self.coords:
            XY = line
            coords_out.append([XY[0] - xmin, XY[1] - ymin, XY[2] - xmin, XY[3] - ymin])
        return coords_out
