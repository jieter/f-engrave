from subprocess import Popen, PIPE

from util import fmessage, VERSION


def checkExternalBinaries():
    cmd = ["ttf2cxf_stream", "TEST", "STDOUT"]
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if VERSION == 3:
            stdout = bytes.decode(stdout)
        if str.find(stdout.upper(), 'TTF2CXF') != -1:
            TTF_AVAIL = True
        else:
            TTF_AVAIL = False
            fmessage("ttf2cxf_stream is not working...Bummer")
    except:
        fmessage("ttf2cxf_stream executable is not present/working...Bummer")
        TTF_AVAIL = False

    cmd = ["potrace", "-v"]
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if VERSION == 3:
            stdout = bytes.decode(stdout)
        if str.find(stdout.upper(), 'POTRACE') != -1:
            POTRACE_AVAIL = True
            if str.find(stdout.upper(), '1.1') == -1:
                fmessage("F-Engrave Requires Potrace Version 1.10 or Newer.")
        else:
            POTRACE_AVAIL = False
            fmessage("potrace is not working...Bummer")
    except:
        fmessage("potrace executable is not present/working...Bummer")
        POTRACE_AVAIL = False

    return {
        'TTF': TTF_AVAIL,
        'POTRACE': POTRACE_AVAIL
    }
