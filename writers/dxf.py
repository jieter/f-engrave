
# A header section just in case the reading software needs it
header_section = '''\
999
DXF created by F-Engrave <by Scorch, www.scorchworks.com>
0
SECTION
2
HEADER
0
ENDSEC'''

# Tables Section
# These can be used to specify predefined constants, line styles, text styles, view
# tables, user coordinate systems, etc. We will only use tables to define some layers
# for use later on. Note: not all programs that support DXF import will support
# layers and those that do usually insist on the layers being defined before use
#
# The following will initialise layers 1 and 2 for use with moves and rapid moves.
tables_section = '''\
0
SECTION
2
TABLES
0
TABLE
2
LTYPE
70
1
0
LTYPE
2
CONTINUOUS
70
64
3
Solid line
72
65
73
0
40
0.000000
0
ENDTAB
0
TABLE
2
LAYER
70
6
0
LAYER
2
1
70
64
62
7
6
CONTINUOUS
0
LAYER
2
2
70
64
62
7
6
CONTINUOUS
0
ENDTAB
0
TABLE
2
STYLE
70
0
0
ENDTAB
0
ENDSEC'''

# This block section is not necessary but apperantly it's good form to include one anyway.
# The following is an empty block section.
empty_block_section = '''\
0
SECTION
2
BLOCKS
0
ENDSEC'''

# Start entities section
start_entities_section = '''\
0
SECTION
2
ENTITIES
  0'''

end_entities_section = '''\
ENDSEC
0
EOF'''

gcode_template = '''\
LINE
  5
30
100
AcDbEntity
  8
1
 62
150
100
AcDbLine
 10
%(x1).4f
 20
%(y1).4f
 30
%(z1).4f
 11
%(x2).4f
 21
%(y2).4f
 31
%(z2).4f
  0'''


def dxf(job, close_loops=False):

    if close_loops:
        job.v_carve(clean=False)

    coords = job.coords

    dxf_code = []

    dxf_code.append(header_section)
    dxf_code.append(tables_section)
    dxf_code.append(empty_block_section)
    dxf_code.append(start_entities_section)

    for XY in coords:
        dxf_code.append(gcode_template % {
            'x1': XY[0],
            'y1': XY[1],
            'z1': 0.0,
            'x2': XY[2],
            'y2': XY[3],
            'z2': 0.0
        })

    dxf_code.append(end_entities_section)

    return dxf_code
