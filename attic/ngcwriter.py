class NgcWriter:
    """
    A basic G-Code writer, for testing purpose
    """
    clearance_height = 20
    feed_height = 10
    feed = 200
    plunge_feed = 100
    metric = True
    scale = 1

    def __init__(self, filename="output.ngc"):
        self.filename = filename
        self.out = open(filename, 'w')

    def write(self, cmd):
        self.out.write("{}\n".format(cmd))

    def pen_up(self):
        self.write("G0 Z{}".format(self.feed_height))

    def xy_rapid_to(self, x, y):
        self.write("G0 X{} Y{}".format(x, y))

    def pen_down(self, z):
        self.write("G0 Z{}".format(z))

    def line_to(self, x, y, z):
        self.write("G1 X{} Y{} Z{} F{}".format(x, y, z, self.feed))


def print_toolpath(toolpath, scale=1.0):
    ngc = NgcWriter()

    for chain in toolpath:
        first_point = True
        for move in chain:
            for point in move:
                if first_point:  # don't draw anything on the first iteration
                    first_point = False
                    p = point[0]
                    zdepth = scale * point[1]  # derive Z height from MIC
                    ngc.pen_up()
                    ngc.xy_rapid_to(scale * p.x, scale * p.y)
                    ngc.pen_down(z=-zdepth)
                else:
                    p = point[0]
                    z = point[1]
                    ngc.line_to(scale * p.x, scale * p.y, scale * (-z))

    ngc.pen_up()  # final engraver up

    return
