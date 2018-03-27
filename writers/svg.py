# TODO How to import higher level package:
# from settings import CUT_TYPE_VCARVE, CUT_TYPE_ENGRAVE

color = 'blue'

header_template = '''
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%(width_in)f%(units)s" height="%(height_in)f%(units)s" \
viewBox="0 0 %(width)f %(height)f" xmlns="http://www.w3.org/2000/svg" version="1.1">
    <title>F-engrave Output</title>
    <desc>SVG File Created By OOF-Engrave</desc>'''

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

    bbox = job.get_plot_bbox()
    bbox.pad(thickness / 2)
    minx, maxx, miny, maxy = bbox.tuple()
    width_in = bbox.width()
    height_in = bbox.height()

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

    # Make Circle
    plot_radius = settings.get('text_radius')
    if settings.get('input_type') == 'text' and \
            settings.get('plotbox') and \
            plot_radius != 0 and \
            settings.get('cut_type') == "engrave":  # TODO use CUT_TYPE_ENGRAVE

        x_origin = settings.get('xorigin')
        y_origin = settings.get('yorigin')

        svgcode.append(circle_template % (
            (x_origin - job.xzero - minx) * dpi,
            (-y_origin + job.yzero + maxy) * dpi,
            plot_radius * dpi,
            thickness * dpi))

    # The image
    for l in job.coords:
        # translate
        line = [
            l[0] - minx, -l[1] + maxy,
            l[2] - minx, -l[3] + maxy
        ]
        # scale
        line = map(lambda x: x * dpi, line)

        svgcode.append(path_template % (tuple(line) + (thickness * dpi, )))

    svgcode.append('</svg>')

    return svgcode
