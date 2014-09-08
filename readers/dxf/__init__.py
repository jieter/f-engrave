from util.mathutil import Character, Line

from dxf_class import DXF_CLASS


def parse(dxf_file, segarc, new_origin=True):
    # Initialize / reset
    font = {}
    key = None
    stroke_list = []
    xmax, ymax = -1e10, -1e10
    xmin, ymin = 1e10, 1e10

    DXF_source = " "
    dxf_import = DXF_CLASS()
    dxf_import.GET_DXF_DATA(dxf_file, tol_deg=segarc)
    dxfcoords = dxf_import.DXF_COORDS_GET(new_origin)

    if "POTRACE" in dxf_import.comment.upper():
        DXF_source = "POTRACE"
    if "INKSCAPE" in dxf_import.comment.upper():
        DXF_source = "INKSCAPE"

    # save the character to our dictionary
    key = ord("F")
    stroke_list = []
    for line in dxfcoords:
        XY = line
        stroke_list += [
            Line([XY[0], XY[1], XY[2], XY[3]])
        ]
        xmax = max(xmax, XY[0], XY[2])
        ymax = max(ymax, XY[1], XY[3])
        xmin = min(xmin, XY[0], XY[2])
        ymin = min(ymin, XY[1], XY[3])

    font[key] = Character(key)
    font[key].stroke_list = stroke_list
    font[key].xmax = xmax
    font[key].ymax = ymax
    font[key].xmin = xmin
    font[key].ymin = ymin

    return font, DXF_source
