import os
from subprocess import Popen, PIPE

from util import fmessage, VERSION, PIL
from readers.dxf import parse
from geometry.font import *

if PIL:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None


def read_image_file(settings):

    font = Font()

    file_full = settings.get('IMAGE_FILE')
    if not os.path.isfile(file_full):
        return

    fileName, fileExtension = os.path.splitext(file_full)

    if settings.get('useIMGsize'):
        new_origin = False
    else:
        new_origin = True

    segarc = settings.get('segarc')

    filetype = fileExtension.upper()
    if filetype == '.DXF':
        try:
            with open(file_full) as dxf_file:
                # build stroke lists from image file
                font, DXF_source = parse(dxf_file, segarc, new_origin)
                # font['DXF_source'] = DXF_source
                settings.set('input_type', "image")

        except Exception as e:
            fmessage("Unable to open Drawing Exchange File (DXF), error: {}".format(e))

    elif filetype in ('.BMP', '.PBM', '.PPM', '.PGM', '.PNM'):
        try:
            # cmd = ["potrace","-b","dxf",file_full,"-o","-"]
            cmd = ["potrace",
                   "-z", settings.get('bmp_turnpol'),
                   "-t", settings.get('bmp_turdsize'),
                   "-a", settings.get('bmp_alphamax'),
                   "-n",
                   "-b", "dxf", file_full, "-o", "-"]
            if settings.get('bmp_longcurve'):
                cmd.extend(("-O", settings.get('bmp_opttolerance')))

            cmd = ' '.join(map(str, cmd))
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = p.communicate()

            if VERSION == 3:
                dxf_file = bytes.decode(stdout).split("\n")
            else:
                dxf_file = stdout.split("\n")

            # build stroke lists from font file
            font, DXF_source = parse(dxf_file, segarc, new_origin)
            # font['DXF_source'] = DXF_source
            settings.set('input_type', "image")

        except Exception as e:
            fmessage("Unable to create path data from bitmap file, error: {}".format(e))

    elif filetype in ('.JPG', '.PNG', '.GIF', '.TIF'):
        if PIL:
            try:
                PIL_im = Image.open(file_full)
                mode = PIL_im.mode
                if len(mode) > 3:
                    blank = Image.new("RGB", PIL_im.size, (255, 255, 255))
                    blank.paste(PIL_im, (0, 0), PIL_im)
                    PIL_im = blank

                PIL_im = PIL_im.convert("1")
                file_full_tmp = settings.get('HOME_DIR') + "/fengrave_tmp.bmp"
                PIL_im.save(file_full_tmp, "bmp")

                # TODO create a separate potrace method
                # cmd = ["potrace","-b","dxf",file_full,"-o","-"]
                cmd = ["potrace",
                       "-z", settings.get('bmp_turnpol'),
                       "-t", settings.get('bmp_turdsize'),
                       "-a", settings.get('bmp_alphamax'),
                       "-n",
                       "-b", "dxf", file_full_tmp, "-o", "-"]
                if settings.get('bmp_longcurve'):
                    cmd.extend(("-O", settings.get('bmp_opttolerance')))

                cmd = ' '.join(map(str, cmd))
                p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
                stdout, stderr = p.communicate()

                if VERSION == 3:
                    dxf_file = bytes.decode(stdout).split("\n")
                else:
                    dxf_file = stdout.split("\n")

                # build stroke lists from font file
                font, DXF_source = parse(dxf_file, segarc, new_origin)
                settings.set('input_type', "image")
                try:
                    os.remove(file_full_tmp)
                except:
                    pass
            except:
                fmessage("PIL encountered an error. Unable to create path data from the selected image file.")
                fmessage("Converting the image file to a BMP file may resolve the issue.")
        else:
            fmessage("PIL is required for reading JPG, PNG, GIF and TIF files.")
    else:
        fmessage("Unknown filetype: " + fileExtension)

    return font
