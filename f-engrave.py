#!/usr/bin/env python
"""
    f-engrave.py G-Code Generator
    Copyright (C) <2014>  <Scorch>
    Source was used from the following works:
              engrave-11.py G-Code Generator -- Lawrence Glaister --
              GUI framework from arcbuddy.py -- John Thornton  --
              cxf2cnc.py v0.5 font parsing code --- Ben Lipkowitz(fenn) --
              dxf.py DXF Viewer (http://code.google.com/p/dxf-reader/)
              DXF2GCODE (http://code.google.com/p/dfxf2gcode/)
"""

version = '1.40'

# TODO insert psyco / pypy
#
from application.settings import Settings

settings = Settings(autoload=True)

# TODO: parse command line options.

if settings.get('batch'):
    # batch processing
    pass

else:
    from util import icon, Tk
    from application.gui import Gui

    root = Tk()
    app = Gui(root, settings)
    app.master.title("F-Engrave V" + version)
    app.master.iconname("F-Engrave")
    app.master.minsize(780, 540)

    icon.add_to_app(app)

    root.mainloop()
