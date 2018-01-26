#!/usr/bin/env python
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

version = '1.40'

#TODO insert psyco / pypy

from application.settings import Settings

settings = Settings(autoload=True)

#TODO: parse command line options.

if settings.get('batch'):
    # batch processing
    pass

else:
    print 'GUI is under construction...'
    #TEST print settings

    from util import icon
    from application.gui import Gui

    try:
        from tkinter import *
        from tkinter.filedialog import *
        import tkinter.messagebox
    except:
        from Tkinter import *
        from tkFileDialog import *
        import tkMessageBox

    root = Tk()
    app = Gui(root, settings)
    app.master.title("F-Engrave V" + version)
    app.master.iconname("F-Engrave")
    app.master.minsize(780, 540)

    #app.f_engrave_init()
    icon.add_to_app(app)

    root.mainloop()
