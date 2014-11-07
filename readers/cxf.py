################################################################################
# This routine parses the .cxf font file and builds a font dictionary of       #
# line segment strokes required to cut each character.                         #
# Arcs (only used in some fonts) are converted to a number of line             #
# segments based on the angular length of the arc. Since the idea of           #
# this font description is to make it support independent x and y scaling,     #
# we do not use native arcs in the g-code.                                     #
################################################################################

from math import sin, cos, radians
import re

from geometry import Character, Line, Font


def parse(file, segarc):
    font = Font()

    key = None
    stroke_list = []
    xmax, ymax = 0, 0
    for text_in in file:
        text = text_in + " "

        # format for a typical letter (lower-case r):
        # #comment, with a blank line after it
        #
        # [r] 3  (or "[0072] r" where 0072 is the HEX value of the character)
        # L 0,0,0,6
        # L 0,6,2,6
        # A 2,5,1,0,90
        #
        end_char = len(text)
        # save the character to our dictionary
        if end_char and key:
            font.add_character(
                Character(key=key, stroke_list=stroke_list)
            )

        new_cmd = re.match('^\[(.*)\]\s', text)

        # new character
        if new_cmd:
            key_tmp = new_cmd.group(1)
            if len(new_cmd.group(1)) == 1:
                # key = key_tmp
                key = ord(key_tmp)
            else:
                if len(key_tmp) == 5:
                    key_tmp = key_tmp[1:]
                if len(key_tmp) == 4:
                    try:
                        # key=chr(int(key_tmp,16))
                        key = int(key_tmp, 16)
                    except:
                        key = None
                        stroke_list = []
                        xmax, ymax = 0, 0
                        continue
                else:
                    key = None
                    stroke_list = []
                    xmax, ymax = 0, 0
                    continue
            stroke_list = []
            xmax, ymax = 0, 0

        line_cmd = re.match('^L (.*)', text)
        if line_cmd:
            coords = line_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            stroke_list += [Line(coords)]
            xmax = max(xmax, coords[0], coords[2])

        arc_cmd = re.match('^A (.*)', text)
        if arc_cmd:
            coords = arc_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            xcenter, ycenter, radius, start_angle, end_angle = coords

            # since font definition has arcs as ccw, we need some font foo
            if end_angle < start_angle:
                start_angle -= 360.0

            # approximate arc with line seg every "segarc" degrees
            segs = int((end_angle - start_angle) / segarc) + 1
            angleincr = (end_angle - start_angle) / segs
            xstart = cos(radians(start_angle)) * radius + xcenter
            ystart = sin(radians(start_angle)) * radius + ycenter
            angle = start_angle

            for i in range(segs):
                angle += angleincr
                xend = cos(radians(angle)) * radius + xcenter
                yend = sin(radians(angle)) * radius + ycenter
                coords = [xstart, ystart, xend, yend]
                stroke_list += [Line(coords)]
                xmax = max(xmax, coords[0], coords[2])
                ymax = max(ymax, coords[1], coords[3])
                xstart = xend
                ystart = yend
    return font
