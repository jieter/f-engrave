import os
from . import fmessage


def add_to_app(app):
    try:
        tempfile = 'f_engrave_icon'
        f = open(tempfile, 'w')
        f.write("#define f_engrave_icon_width 16\n")
        f.write("#define f_engrave_icon_height 16\n")
        f.write("static unsigned char f_engrave_icon_bits[] = {\n")
        f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
        f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
        f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
        f.close()
        app.master.iconbitmap("@%s" % tempfile)
        os.remove(tempfile)
    except:
        fmessage("Unable to create temporary icon file.")
