from subprocess import Popen, PIPE
import sys

VERSION = sys.version_info[0]


def check_ovd():
    try:
        import openvoronoi as ovd  # noqa F401
        return True
    except:
        print("openvoronoi module is not found...")

    return False


def check_ttf():
    cmd = ["ttf2cxf_stream", "TEST", "STDOUT"]
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if VERSION == 3:
            stdout = bytes.decode(stdout)
        if str.find(stdout.upper(), 'TTF2CXF') != -1:
            return True
        else:
            raise Exception("ttf2cxf_stream is not working...Bummer")
    except:
        raise Exception("ttf2cxf_stream executable is not present/working...Bummer")

    return False


def check_potrace():
    cmd = ["potrace", "-v"]
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if VERSION == 3:
            stdout = bytes.decode(stdout)
        if str.find(stdout.upper(), 'POTRACE') != -1:
            if str.find(stdout.upper(), '1.1') == -1:
                raise Exception("Requires Potrace Version 1.10 or newer.")
            return True
        else:
            raise Exception("potrace is not working...Bummer")
    except:
        raise Exception("potrace executable is not present/working...Bummer")

    return False


def check_pil():
    try:
        from PIL import Image  # noqa F401
        return True
    except:
        raise Exception("Python Imaging Library (PIL) was not found...Bummer\n\
        PIL enables more image file formats.")

    return False


def check_pubsub():
    try:
        from pubsub import pub
        print("Python pubsub API version: %s found" % pub.VERSION_API)
        return True
    except:
        raise Exception("Python pubsub is not found...")

    return False
