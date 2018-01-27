from math import sqrt, hypot, sin, radians
from geometry import Zero, Get_Angle, Transform


def Line_Arc_Fit(lastx, lasty, lastz, x1, y1, z1, nextx, nexty, nextz, FLAG_arc, code,
                 R_last, x_center_last, y_center_last, FLAG_line, accuracy):

    # print lastx, lasty, lastz, x1, y1, z1, nextx, nexty, nextz
    # print FLAG_arc, code, R_last, x_center_last, y_center_last, FLAG_line, accuracy

    '''
    Line fit and arc fit (curve fit)
    '''
    dx_a = x1 - lastx
    dy_a = y1 - lasty
    dz_a = z1 - lastz

    dx_c = nextx - lastx
    dy_c = nexty - lasty
    dz_c = nextz - lastz

    if abs(dx_a) > Zero:
        line_t = dx_c / dx_a
    elif abs(dy_a) > Zero:
        line_t = dy_c / dy_a
    elif abs(dz_a) > Zero:
        line_t = dz_c / dz_a
    else:
        line_t = 0

    ex = dx_c - dx_a * line_t
    ey = dy_c - dy_a * line_t
    ez = dz_c - dz_a * line_t
    et = sqrt(ex * ex + ey * ey + ez * ez)

    L_a = dx_a * dx_a + dy_a * dy_a + dz_a * dz_a
    L_c = dx_c * dx_c + dy_c * dy_c + dz_c * dz_c

    FLAG_arc_last = FLAG_arc
    FLAG_arc = 0

    FLAG_line_last = FLAG_line
    if et > accuracy or (L_a >= L_c) or FLAG_arc_last == 1:
        FLAG_line = 0
    else:
        FLAG_line = 1
        code = "G1"

    ###############
    # Arc Fitting #
    ###############

    # TODO: fix arc_fit = bool(self.arc_fit.get()) == 1
    arc_fit = 1
    # TODO fix: seg_arc = float(self.segarc.get())
    seg_arc = 5.0

    if (FLAG_line != 1 and FLAG_line_last != 1 and line_t != 0 and arc_fit):
        dx_b = nextx - x1
        dy_b = nexty - y1
        dz_b = nextz - z1
        L_b = dx_b * dx_b + dy_b * dy_b + dz_b * dz_b

        if abs(dx_a) > Zero and abs(dx_b) > Zero:
            ma = dy_a / dx_a
            mb = dy_b / dx_b

            if abs(mb - ma) > Zero and (abs(ma) > Zero or abs(mb) > Zero):
                x_center = (ma * mb * (lasty - nexty) + mb * (lastx + x1) - ma * (x1 + nextx)) / (2 * (mb - ma))
                if abs(ma) > Zero:
                    y_center = -1 / ma * (x_center - (lastx + x1) / 2) + (lasty + y1) / 2
                elif abs(mb) > Zero:
                    y_center = -1 / mb * (x_center - (x1 + nextx) / 2) + (y1 + nexty) / 2

                R_arc = hypot(x1 - x_center, y1 - y_center)
                cord_a = hypot(dx_a, dy_a)
                cord_b = hypot(dx_b, dy_b)
                cord_limit = 2 * R_arc * sin(radians(seg_arc))

                try:
                    sagitta_a = R_arc - sqrt(R_arc ** 2 - cord_a ** 2)
                    sagitta_b = R_arc - sqrt(R_arc ** 2 - cord_b ** 2)
                    sagitta_min = min(sagitta_a, sagitta_b)
                except:
                    sagitta_min = 0.0

                SKIP = 0
                if FLAG_arc_last == 1:
                    if (
                            abs(R_last - R_arc) > Zero or
                            abs(x_center_last - x_center) > Zero or
                            abs(y_center_last - y_center) > Zero):
                        SKIP = 1

                if (
                        max(cord_a, cord_b) <= cord_limit and abs(ez) <= Zero and
                        L_a ** 2 + L_b ** 2 < L_c ** 2 and cord_a / cord_b >= 1.0 / 1.5 and
                        cord_a / cord_b <= 1.5 and sagitta_min > Zero and SKIP == 0):

                    seg_sin_test = (y1 - lasty) / cord_a
                    seg_cos_test = -(x1 - lastx) / cord_a
                    phi_test = geometry.getAngle(seg_sin_test, seg_cos_test)
                    X_test, Y_test = geometry.transform(x_center - lastx, y_center - lasty, radians(phi_test))
                    code = 'G2' if Y_test > 0.0 else 'G3'
                    x_center_last = x_center
                    y_center_last = y_center
                    R_last = R_arc
                    FLAG_arc = 1
    WRITE = 0

    if FLAG_line == 0 and FLAG_arc == 0:
        WRITE = 1

    return code, FLAG_arc, R_last, x_center_last, y_center_last, WRITE, FLAG_line
