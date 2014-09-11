


def gcode(job):
    settings = job.settings

    code = []


    code.append(settings.to_gcode())

    code.append("(#########################################################)")
    # G90 Sets absolute distance mode
    code.append('G90')

    if settings.get('arc_fit'):
        # G91.1 Sets Incremental Distance Mode for I, J & K arc offsets.
        code.append('G91.1')

    if settings.get('units') == "in":
        # G20 sets units to inches
        code.append('G20')
    else:
        # G21 sets units to mm
        code.append('G21')

    for line in settings.get('gcode_preamble').split('|'):
         code.append(line)



    for line in settings.get('gcode_postamble').split('|'):
         code.append(line)

    return code


def engrave_gcode(job):
    code = []

    return code

def vcarve_gcode(job):
    code = []
    return code
