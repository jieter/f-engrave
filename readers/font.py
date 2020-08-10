import os
from subprocess import Popen, PIPE

from util import fmessage, VERSION, TTF_AVAILABLE
from . import cxf as parse_cxf


def readFontFile(settings):
    """
    Read a (.cxf, .ttf) font file
    """
    filename = settings.get_fontfile()

    if not os.path.isfile(filename):
        return

    fileName, fileExtension = os.path.splitext(filename)

    segarc = settings.get('segarc')
    TYPE = fileExtension.upper()

    if TYPE == '.CXF':
        with open(filename, 'r', encoding='ISO-8859-1') as fontfile:
            # build stroke lists from font file
            return parse_cxf.parse(fontfile, segarc)

    elif TYPE == '.TTF':
        # convert TTF to CXF
        option = '-e' if settings.get('ext_char') else ''
        cmd = ["ttf2cxf_stream", option, filename, "STDOUT"]
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if VERSION == 3:
                fontfile = bytes.decode(stdout).split("\n")
            else:
                fontfile = stdout.split("\n")

            # build stroke lists from font file
            settings.set('input_type', "text")
            return parse_cxf.parse(fontfile, segarc)
        except:
            fmessage("Unable To open True Type (TTF) font file: %s" % (filename))
    else:
        pass


def listFonts(settings):
    try:
        font_files = os.listdir(settings.get('fontdir'))
        font_files.sort()
    except:
        font_files = " "

    font_list = []
    for name in font_files:
        if 'CXF' in name.upper() or ('TTF' in name.upper() and TTF_AVAILABLE):
            font_list.append(name)

    return font_list
