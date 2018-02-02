def dxf(coords, close_loops=False):

    if close_loops:
        self.v_carve_it(clean=False, DXF_FLAG=close_loops)

    dxf_code = []
    # Create a header section just in case the reading software needs it
    dxf_code.append("999")
    dxf_code.append("DXF created by G-Code Ripper <by Scorch, www.scorchworks.com>")
    dxf_code.append("0")
    dxf_code.append("SECTION")
    dxf_code.append("2")
    dxf_code.append("HEADER")
    # dxf_code.append("9")
    # dxf_code.append("$INSUNITS")
    # dxf_code.append("70")
    # dxf_code.append("1") #units 1 = Inches; 4 = Millimeters;
    dxf_code.append("0")
    dxf_code.append("ENDSEC")

    #
    # Tables Section
    # These can be used to specify predefined constants, line styles, text styles, view
    # tables, user coordinate systems, etc. We will only use tables to define some layers
    # for use later on. Note: not all programs that support DXF import will support
    # layers and those that do usually insist on the layers being defined before use
    #
    # The following will initialise layers 1 and 2 for use with moves and rapid moves.
    dxf_code.append("0")
    dxf_code.append("SECTION")
    dxf_code.append("2")
    dxf_code.append("TABLES")
    dxf_code.append("0")
    dxf_code.append("TABLE")
    dxf_code.append("2")
    dxf_code.append("LTYPE")
    dxf_code.append("70")
    dxf_code.append("1")
    dxf_code.append("0")
    dxf_code.append("LTYPE")
    dxf_code.append("2")
    dxf_code.append("CONTINUOUS")
    dxf_code.append("70")
    dxf_code.append("64")
    dxf_code.append("3")
    dxf_code.append("Solid line")
    dxf_code.append("72")
    dxf_code.append("65")
    dxf_code.append("73")
    dxf_code.append("0")
    dxf_code.append("40")
    dxf_code.append("0.000000")
    dxf_code.append("0")
    dxf_code.append("ENDTAB")
    dxf_code.append("0")
    dxf_code.append("TABLE")
    dxf_code.append("2")
    dxf_code.append("LAYER")
    dxf_code.append("70")
    dxf_code.append("6")
    dxf_code.append("0")
    dxf_code.append("LAYER")
    dxf_code.append("2")
    dxf_code.append("1")
    dxf_code.append("70")
    dxf_code.append("64")
    dxf_code.append("62")
    dxf_code.append("7")
    dxf_code.append("6")
    dxf_code.append("CONTINUOUS")
    dxf_code.append("0")
    dxf_code.append("LAYER")
    dxf_code.append("2")
    dxf_code.append("2")
    dxf_code.append("70")
    dxf_code.append("64")
    dxf_code.append("62")
    dxf_code.append("7")
    dxf_code.append("6")
    dxf_code.append("CONTINUOUS")
    dxf_code.append("0")
    dxf_code.append("ENDTAB")
    dxf_code.append("0")
    dxf_code.append("TABLE")
    dxf_code.append("2")
    dxf_code.append("STYLE")
    dxf_code.append("70")
    dxf_code.append("0")
    dxf_code.append("0")
    dxf_code.append("ENDTAB")
    dxf_code.append("0")
    dxf_code.append("ENDSEC")

    # This block section is not necessary but apperantly it's good form to include one anyway.
    # The following is an empty block section.
    dxf_code.append("0")
    dxf_code.append("SECTION")
    dxf_code.append("2")
    dxf_code.append("BLOCKS")
    dxf_code.append("0")
    dxf_code.append("ENDSEC")

    # Start entities section
    dxf_code.append("0")
    dxf_code.append("SECTION")
    dxf_code.append("2")
    dxf_code.append("ENTITIES")
    dxf_code.append("  0")

    #################################
    ## GCODE WRITING for Dxf_Write ##
    #################################
    for XY in coords:
        dxf_code.append("LINE")
        dxf_code.append("  5")
        dxf_code.append("30")
        dxf_code.append("100")
        dxf_code.append("AcDbEntity")
        dxf_code.append("  8")  # layer Code #dxf_code.append("0")

        dxf_code.append("1")
        dxf_code.append(" 62")  # color code
        dxf_code.append("150")

        dxf_code.append("100")
        dxf_code.append("AcDbLine")
        dxf_code.append(" 10")
        dxf_code.append("%.4f" % (XY[0]))  # x1 coord
        dxf_code.append(" 20")
        dxf_code.append("%.4f" % (XY[1]))  # y1 coord
        dxf_code.append(" 30")
        dxf_code.append("%.4f" % (0))  # z1 coord
        dxf_code.append(" 11")
        dxf_code.append("%.4f" % (XY[2]))  # x2 coord
        dxf_code.append(" 21")
        dxf_code.append("%.4f" % (XY[3]))  # y2 coord
        dxf_code.append(" 31")
        dxf_code.append("%.4f" % (0))  # z2 coord
        dxf_code.append("  0")

    dxf_code.append("ENDSEC")
    dxf_code.append("0")
    dxf_code.append("EOF")

    return dxf_code