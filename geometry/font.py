from geometry.boundingbox import BoundingBox


class Character(object):
    """
    The strokes which make up a fontcharacter
    """
    def __init__(self, key, stroke_list):
        self.key = key
        self.stroke_list = stroke_list

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


class Font(object):
    """
    The complete characterset of a font
    """
    def __init__(self):
        self.characters = {}
        self.bbox = BoundingBox()

    def __len__(self):
        return len(self.characters)

    def __getitem__(self, key):

        # Space or Linefeed
        if key in (32, 10):
            return Character(' ', [])

        return self.characters[key]

    def __iter__(self):
        for char in self.characters:
            yield char

    def add_character(self, char):
        self.characters[char.key] = char
        self.bbox.extend(char.bounds())

    def get_char_bbox_used(self, string):
        bbox = BoundingBox()

        for char in string:
            bbox.extend(self[ord(char)])

        return bbox

    def get_character_width(self):
        return max(self.characters[key].get_xmax() for key in self.characters)

    def line_height(self):
        return self.bbox.ymax

    def line_depth(self):
        return self.bbox.ymin
