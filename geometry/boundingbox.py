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
        assert -amount * 2 < self.width(), 'pad (%f) exceeds width (%f) of X axis' % (float(amount), self.width())
        self.xmin -= float(amount)
        self.xmax += float(amount)

        return self

    def padY(self, amount):
        assert -amount * 2 < self.height(), 'pad (%f) exceeds width (%f) of Y axis' % (float(amount), self.height())
        self.ymin -= float(amount)
        self.ymax += float(amount)

        return self

    def width(self):
        return self.xmax - self.xmin

    def height(self):
        return self.ymax - self.ymin

    def center(self):
        return (
            self.xmin + (self.width() / 2),
            self.ymin + (self.height() / 2)
        )

    def tuple(self):
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    def __eq__(self, other):
        return self.tuple() == other.tuple()

    def __str__(self):
        return 'BoundingBox([%s, %s, %s, %s])' % self.tuple()
