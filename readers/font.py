import os
from subprocess import Popen, PIPE

from util import fmessage, VERSION, TTF_AVAILABLE
from . import parse_cxf


def Read_font_file(settings):
    '''
    Read a font file (.cxf, .ttf)
    '''

    font = {}
    file_full = settings.get_fontfile()

    if not os.path.isfile(file_full):
        return

    fileName, fileExtension = os.path.splitext(file_full)
    # self.current_input_file.set( os.path.basename(file_full) )

    segarc = settings.get('segarc')

    TYPE = fileExtension.upper()
    if TYPE == '.CXF':
        with open(file_full, 'r') as fontfile:
            # build stroke lists from font file
            font = parse_cxf(file, segarc)

    elif TYPE == '.TTF':
        option = '-e' if settings.get('ext_char') else ''

        cmd = ["ttf2cxf_stream", option, file_full, "STDOUT"]
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if VERSION == 3:
                fontfile = bytes.decode(stdout).split("\n")
            else:
                fontfile = stdout.split("\n")

            font = parse_cxf(fontfile, segarc)  # build stroke lists from font file
            settings.set('input_type', 'text')
        except:
            fmessage("Unable To open True Type (TTF) font file: %s" % (file_full))
    else:
        pass

    return font


def list_fonts(settings):
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
