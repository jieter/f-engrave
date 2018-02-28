from math import atan2, cos, sin, degrees, radians, hypot, sqrt

from boundingbox import BoundingBox
from util import MAXINT

Zero = 1e-5


def transform(x, y, angle):
    """
    routine takes an x and a y coords and does a coordinate transformation
    to a new coordinate system at angle from the initial coordinate system
    Returns new x,y tuple
    """
    newx = x * cos(angle) - y * sin(angle)
    newy = x * sin(angle) + y * cos(angle)

    return newx, newy


def rotation(x, y, angle, radius):
    """
    routine takes an x and y the point is rotated by angle returns new x,y,alpha
    """
    if radius == 0.0:
        alpha = 0
        xx = x
        yy = y
    else:
        # radius > 0.0 or radius < 0.0
        alpha = x / radius
        xx = (radius + y) * sin(alpha)
        yy = (radius + y) * cos(alpha)

    rad = hypot(xx, yy)
    theta = atan2(yy, xx)
    newx = rad * cos(theta + radians(angle))
    newy = rad * sin(theta + radians(angle))

    return newx, newy, alpha


def scale(x, y, xscale, yscale):
    return x * xscale, y * yscale


def translate(x1, y1, x2, y2):
    return x1 + x2, y1 + y2


def point_inside_polygon(x, y, poly):
    """
    Determine if a point is inside a given polygon. Polygon is a list of (x,y) pairs.
    The ray casting method is used here.
    Returns: 1 if a point is inside a given polygon, otherwise -1
    http://www.ariel.com.au/a/python-point-int-poly.html
    https://stackoverflow.com/questions/16625507/python-checking-if-point-is-inside-a-polygon/23453678#23453678
    """
    n = len(poly)
    inside = -1
    p1x = poly[0][0]
    p1y = poly[0][1]
    for i in range(n + 1):
        p2x = poly[i % n][0]
        p2y = poly[i % n][1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = inside * -1
        p1x, p1y = p2x, p2y

    return inside


def detect_intersect(coords0, coords1, lcoords, XY_T_F=True):
    """
    Find intersecting lines
    """
    [x0, y0] = coords0
    [x1, y1] = coords1

    global Zero

    all_intersects = []
    Xint_list = []
    numcoords = len(lcoords)
    if numcoords < 1:
        return False

    dx = x1 - x0
    dy = y1 - y0
    len_seg = sqrt(dx * dx + dy * dy)

    if len_seg < Zero:
        if XY_T_F is False:
            return False
        else:
            return []

    seg_sin = dy / len_seg
    seg_cos = dx / len_seg
    Xint_local = 0

    for ii in range(0, numcoords):
        x2 = lcoords[ii][0]
        y2 = lcoords[ii][1]
        x3 = lcoords[ii][2]
        y3 = lcoords[ii][3]

        xr0 = (x2 - x0) * seg_cos + (y2 - y0) * seg_sin
        yr0 = (x2 - x0) * seg_sin - (y2 - y0) * seg_cos
        xr1 = (x3 - x0) * seg_cos + (y3 - y0) * seg_sin
        yr1 = (x3 - x0) * seg_sin - (y3 - y0) * seg_cos

        yrmax = max(yr0, yr1)
        yrmin = min(yr0, yr1)

        if yrmin < Zero and yrmax > Zero:
            dxr = xr1 - xr0
            if (abs(dxr) < Zero):
                if (xr0 > Zero and xr0 < len_seg - Zero):
                    Xint_local = xr0  # True
            else:
                dyr = yr1 - yr0
                mr = dyr / dxr
                br = yr1 - mr * xr1
                xint = -br / mr
                if (xint > Zero and xint < len_seg - Zero):
                    Xint_local = xint  # True

            # Check if there was a intersection detected
            if Xint_local != 0:
                if XY_T_F is False:
                    return True
                else:
                    Xint_list.append(Xint_local)
                    Xint_local = 0

    if XY_T_F is False:

        return False

    else:
        if len(Xint_list) > 0:
            Xint_list.sort()
            for Xint_local in Xint_list:
                Xint = Xint_local * seg_cos + x0
                Yint = Xint_local * seg_sin + y0
                all_intersects.append([Xint, Yint])

        return all_intersects


class Line(object):

    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords

        self.xmin = min(self.xstart, self.xend)
        self.xmax = max(self.xstart, self.xend)
        self.ymin = min(self.ystart, self.yend)
        self.ymax = max(self.ystart, self.yend)

    def bounds(self):
        return BoundingBox(self.xmin, self.xmax, self.ymin, self.ymax)

    def translate(self, x, y):
        self.xmin += x
        self.xmax += x
        self.ymin += y
        self.ymin += y

        return self

    def scale(self, x, y=None):
        y = y or x

        self.xmin *= x
        self.xmax *= x
        self.ymin *= y
        self.ymax *= y

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" % (self.xstart, self.ystart, self.xend, self.yend)


"""
    Author.py
    A component of emc2
"""


def dist_lseg(l1, l2, p, z_only=False):
    """
    Compute the 3D distance from the line segment l1..l2 to the point p.
    (Those are lower case L1 and L2)
    """
    x0, y0, z0 = l1
    xa, ya, za = l2
    xi, yi, zi = p

    dx = xa - x0
    dy = ya - y0
    dz = za - z0
    d2 = dx * dx + dy * dy + dz * dz

    if d2 == 0:
        return 0

    t = (dx * (xi - x0) + dy * (yi - y0) + dz * (zi - z0)) / d2
    if t < 0:
        t = 0
    if t > 1:
        t = 1

    if (z_only is True):
        dist2 = (zi - z0 - t * dz) ** 2
    else:
        dist2 = (xi - x0 - t * dx) ** 2 + (yi - y0 - t * dy) ** 2 + (zi - z0 - t * dz) ** 2

    return dist2 ** .5


def rad1(x1, y1, x2, y2, x3, y3):
    x12 = x1 - x2
    y12 = y1 - y2
    x23 = x2 - x3
    y23 = y2 - y3
    x31 = x3 - x1
    y31 = y3 - y1

    den = abs(x12 * y23 - x23 * y12)
    if abs(den) < 1e-5:
        return MAXINT
    else:
        return hypot(float(x12), float(y12)) * hypot(float(x23), float(y23)) * hypot(float(x31), float(y31)) / 2 / den


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "<%f,%f>" % (self.x, self.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    __rmul__ = __mul__

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def mag(self):
        return hypot(self.x, self.y)

    def mag2(self):
        return self.x ** 2 + self.y ** 2


def cent1(x1, y1, x2, y2, x3, y3):
    P1 = Point(x1, y1)
    P2 = Point(x2, y2)
    P3 = Point(x3, y3)

    den = abs((P1 - P2).cross(P2 - P3))
    if abs(den) < 1e-5:
        return MAXINT, MAXINT

    alpha = (P2 - P3).mag2() * (P1 - P2).dot(P1 - P3) / 2 / den / den
    beta = (P1 - P3).mag2() * (P2 - P1).dot(P2 - P3) / 2 / den / den
    gamma = (P1 - P2).mag2() * (P3 - P1).dot(P3 - P2) / 2 / den / den

    Pc = alpha * P1 + beta * P2 + gamma * P3
    return Pc.x, Pc.y


def arc_center(plane, p1, p2, p3):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    if plane == 17:
        return cent1(x1, y1, x2, y2, x3, y3)
    if plane == 18:
        return cent1(x1, z1, x2, z2, x3, z3)
    if plane == 19:
        return cent1(y1, z1, y2, z2, y3, z3)
    return None


def arc_rad(plane, P1, P2, P3):
    if plane is None:
        return MAXINT

    x1, y1, z1 = P1
    x2, y2, z2 = P2
    x3, y3, z3 = P3

    if plane == 17:
        return rad1(x1, y1, x2, y2, x3, y3)
    if plane == 18:
        return rad1(x1, z1, x2, z2, x3, z3)
    if plane == 19:
        return rad1(y1, z1, y2, z2, y3, z3)
    return None


def get_pts(plane, x, y, z):
    if plane == 17:
        return x, y
    if plane == 18:
        return x, z
    if plane == 19:
        return y, z
    return None


def one_quadrant(plane, c, p1, p2, p3):
    xc, yc = c
    x1, y1 = get_pts(plane, p1[0], p1[1], p1[2])
    x2, y2 = get_pts(plane, p2[0], p2[1], p2[2])
    x3, y3 = get_pts(plane, p3[0], p3[1], p3[2])

    def sign(x):
        if abs(x) < 1e-5:
            return 0
        if x < 0:
            return -1
        return 1

    signs = set((
        (sign(x1 - xc), sign(y1 - yc)),
        (sign(x2 - xc), sign(y2 - yc)),
        (sign(x3 - xc), sign(y3 - yc))
    ))

    if len(signs) == 1:
        return True

    if (1, 1) in signs:
        signs.discard((1, 0))
        signs.discard((0, 1))
    if (1, -1) in signs:
        signs.discard((1, 0))
        signs.discard((0, -1))
    if (-1, 1) in signs:
        signs.discard((-1, 0))
        signs.discard((0, 1))
    if (-1, -1) in signs:
        signs.discard((-1, 0))
        signs.discard((0, -1))

    if len(signs) == 1:
        return True


def arc_dir(plane, c, p1, p2, p3):
    xc, yc = c
    x1, y1 = get_pts(plane, p1[0], p1[1], p1[2])
    x2, y2 = get_pts(plane, p2[0], p2[1], p2[2])
    x3, y3 = get_pts(plane, p3[0], p3[1], p3[2])

    # theta_start = atan2(y1-yc, x1-xc)
    # theta_mid = atan2(y2-yc, x2-xc)
    # theta_end = atan2(y3-yc, x3-xc)

    theta_start = get_angle(y1 - yc, x1 - xc)
    theta_mid = get_angle(y2 - yc, x2 - xc) - theta_start
    if (theta_mid < 0):
        theta_mid = theta_mid + 360.0
    theta_end = get_angle(y3 - yc, x3 - xc) - theta_start
    if (theta_end < 0):
        theta_end = theta_end + 360.0

    theta_start = 0.0
    if (theta_end > theta_mid):
        ccw = True
    else:
        ccw = False
        # The following values result in an incorect result
    # with the old method of determining direction
    # x1, y1 = 0.131980576, 1.103352326
    # x2, y2 = 0.092166910, 1.083988473
    # x3, y3 = 0.135566569, 1.103764645
    # xc, yc = 0.141980825, 1.032178989
    return ccw


def get_angle(s, c):
    """
    routine takes a sin and cos and returns the angle (between 0 and 360)
    """
    angle = 90.0 - degrees(atan2(c, s))

    if angle < 0:
        angle = 360 + angle

    return angle


def arc_fmt(plane, c1, c2, p1):
    x, y, z = p1
    if plane == 17:
        # return "I%.4f J%.4f" % (c1-x, c2-y)
        return [c1 - x, c2 - y]
    if plane == 18:
        # return "I%.4f K%.4f" % (c1-x, c2-z)
        return [c1 - x, c2 - z]
    if plane == 19:
        # return "J%.4f K%.4f" % (c1-y, c2-z)
        return [c1 - y, c2 - z]
