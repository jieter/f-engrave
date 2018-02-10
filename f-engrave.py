#!/usr/bin/env python

from application.settings import Settings

"""
    f-engrave.py G-Code Generator
    Copyright (C) <2017>  <Scorch>
    Source was used from the following works:
              engrave-11.py G-Code Generator -- Lawrence Glaister --
              GUI framework from arcbuddy.py -- John Thornton  --
              cxf2cnc.py v0.5 font parsing code --- Ben Lipkowitz(fenn) --
              dxf.py DXF Viewer (http://code.google.com/p/dxf-reader/)
              DXF2GCODE (http://code.google.com/p/dfxf2gcode/)
"""

version = '1.65'

# TODO insert psyco / pypy

settings = Settings(autoload=True)

if settings.get('batch'):
    # batch processing
    pass

else:
    from util import icon
    from application.gui import Gui

    try:
        from tkinter import *
        from tkinter.filedialog import *
    except:
        from Tkinter import *
        from tkFileDialog import *

    root = Tk()
    app = Gui(root, settings)
    app.master.title("F-Engrave v" + version)
    app.master.iconname("F-Engrave")
    app.master.minsize(780, 540)

    app.f_engrave_init()

    icon.add_to_app(app)

    root.mainloop()
