from math import cos, sin, degrees, acos

Zero = 0.0000001


############################################################################
# routine takes an x and a y coords and does a coordinate transformation   #
# to a new coordinate system at angle from the initial coordinate system   #
# Returns new x,y tuple                                                    #
############################################################################
def Transform(x, y, angle):
    newx = x * cos(angle) - y * sin(angle)
    newy = x * sin(angle) + y * cos(angle)
    return newx, newy


############################################################################
# routine takes an sin and cos and returns the angle (between 0 and 360)   #
############################################################################
def Get_Angle(s, c):
    if (s >= 0.0 and c >= 0.0):
        angle = degrees(acos(c))
    elif (s >= 0.0 and c < 0.0):
        angle = degrees(acos(c))
    elif (s < 0.0 and c <= 0.0):
        angle = 360 - degrees(acos(c))
    elif (s < 0.0 and c > 0.0):
        angle = 360 - degrees(acos(c))
    else:
        pass

    if angle < 0.001 and s < 0:
        angle == 360.0
    if angle > 359.999 and s >= 0:
        angle == 0.0
    return angle


class Character(object):
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%%s" % (self.stroke_list)

    def bounds(self):
        return BoundingBox(
            self.get_xmin(),
            self.get_xmax(),
            self.get_ymin(),
            self.get_ymax())

    def get_xmin(self):
        try:
            return min([s.xmin for s in self.stroke_list[:]])
        except ValueError:
            return 0

    def get_xmax(self):
        try:
            return max([s.xmax for s in self.stroke_list[:]])
        except ValueError:
            return 0

    def get_ymax(self):
        try:
            return max([s.ymax for s in self.stroke_list[:]])
        except ValueError:
            return 0

    def get_ymin(self):
        try:
            return min([s.ymin for s in self.stroke_list[:]])
        except ValueError:
            return 0


class Line(object):
    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords

        self.xmin = min(self.xstart, self.xend)
        self.xmax = max(self.xstart, self.xend)
        self.ymin = min(self.ystart, self.yend)
        self.ymax = max(self.ystart, self.yend)

    def bounds(self):
        return BoundingBox(self.xmin, self.xmax, self.ymin, self.ymax)

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" % (self.xstart, self.ystart, self.xend, self.yend)


class BoundingBox(object):
    def __init__(self, xmin=1e10, xmax=-1e10, ymin=1e10, ymax=-1e10):
        self.xmin = float(xmin)
        self.xmax = float(xmax)
        self.ymin = float(ymin)
        self.ymax = float(ymax)

    def extend(self, *args):
        if len(args) is 1:
            obj = args[0]
            if type(obj) is BoundingBox:
                self.xmin = min(self.xmin, obj.xmin)
                self.xmax = max(self.xmax, obj.xmax)

                self.ymin = min(self.ymin, obj.ymin)
                self.ymax = max(self.ymax, obj.ymax)

            elif hasattr(obj, 'bounds'):
                self.extend(obj.bounds())

        elif len(args) == 4:
            self.extend(BoundingBox(*args))

        elif len(args) == 2:
            self.extend(BoundingBox(args[0], args[0], args[1], args[1]))

        return self

    def pad(self, amount):
        self.padX(amount)
        self.padY(amount)

        return self

    def padX(self, amount):
        self.xmin -= float(amount)
        self.xmax += float(amount)

        return self

    def padY(self, amount):
        self.ymin -= float(amount)
        self.ymax += float(amount)

        return self

    def tuple(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    def __eq__(self, other):
        return self.tuple() == other.tuple()

    def __str__(self):
        return 'BoundingBox([%s, %s, %s, %s])' % self.tuple()
