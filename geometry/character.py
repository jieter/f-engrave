from boundingbox import BoundingBox


class Character(object):
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __str__(self):
        return "%%s" % (self.stroke_list)

    def bounds(self):
        return BoundingBox(
            self.get_xmin(),
            self.get_xmax(),
            self.get_ymin(),
            self.get_ymax()
        )

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
