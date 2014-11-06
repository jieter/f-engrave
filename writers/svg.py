from geometry import BoundingBox, Line

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
    if settings.get('cut_type') == "v-carve":
        thickness = 0.001
    else:
        thickness = settings.get('line_thickness')

    dpi = 100

    bbox = BoundingBox()
    for line in job.coords:
        bbox.extend(Line(line[0:4]))

    # XOrigin, YOrigin = (settings.get('xorigin'), settings.get('yorigin'))
    # Radius_plot=  app.RADIUS_PLOT)
    # if Radius_plot != 0:
    #     maxx = max(maxx, XOrigin + Radius_plot - app.Xzero)
    #     minx = min(minx, XOrigin - Radius_plot - app.Xzero)
    #     miny = min(miny, YOrigin - Radius_plot - app.Yzero)
    #     maxy = max(maxy, YOrigin + Radius_plot - app.Yzero)

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
    # if Radius_plot != 0 and settings.get('cut_type.get') == "engrave":
    #     svgcode.append(circle_template % (
    #                 ( XOrigin - app.Xzero - minx) * dpi,
    #                 (-YOrigin + app.Yzero + maxy) * dpi,
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
