from geometry import BoundingBox, Line
# TODO How to import higher level package:
# from settings import CUT_TYPE_VCARVE

color = 'blue'

header_template = '''
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%(width_in)f%(units)s" height="%(height_in)f%(units)s" \
viewBox="0 0 %(width)f %(height)f" xmlns="http://www.w3.org/2000/svg" version="1.1">
    <title>F-engrave Output</title>
    <desc>SVG File Created By F-Engrave</desc>'''

path_template = '<path d="M %f %f L %f %f" fill="none" stroke="' + color + '" ' + \
    'stroke-width="%f" stroke-linecap="round" stroke-linejoin="round" />'

circle_template = '<circle cx="%f" cy="%f" r="%f" fill="none" stroke="' + color + '" stroke-width="%f" />'


def svg(job):

    settings = job.settings

    if settings.get('cut_type') == "v-carve":  # TODO use CUT_TYPE_VCARVE
        thickness = 0.001
    else:
        thickness = settings.get('line_thickness')

    dpi = 100

    bbox = BoundingBox()
    for line in job.coords:
        bbox.extend(Line(line[0:4]))

    # plot_radius = job.get_plot_radius()
    # if plot_radius != 0:
    #     origin = job.get_origin()

    # if radius_plot != 0:
    #     maxx = max(maxx, origin[0] + plot_radus - job.xzero)
    #     minx = min(minx, origin[0] - plot_radus - job.xzero)
    #     miny = min(miny, origin[1] - plot_radus - job.yzero)
    #     maxy = max(maxy, origin[1] + plot_radus - job.yzero)

    bbox.pad(thickness / 2)
    width_in = bbox.xmax - bbox.xmin
    height_in = bbox.ymax - bbox.ymin

    width = width_in * dpi
    height = height_in * dpi

    svgcode = []
    svgcode.append(header_template % {
        'width_in': width_in,
        'height_in': height_in,
        'units': settings.get('units'),
        'width': width,
        'height': height
    })

    # # Make Circle
    # if plot_radius != 0 and settings.get('cut_type') != CUT_TYPE_ENGRAVE:
    #     params = ( )
    #
    #     svgcode.append(circle_template % (
    #                 ( XOrigin - job.Xzero - minx) * dpi,
    #                 (-YOrigin + job.Yzero + maxy) * dpi,
    #                   Radius_plot               ) * dpi,
    #                   thickness                   * dpi)
    # # End Circle

    for l in job.coords:
        # translate
        line = [
            l[0] - bbox.xmin, -l[1] + bbox.ymax,
            l[2] - bbox.xmin, -l[3] + bbox.ymax
        ]
        # scale
        line = map(lambda x: x * dpi, line)

        svgcode.append(path_template % (tuple(line) + (thickness * dpi, )))

    svgcode.append('</svg>')

    return svgcode
