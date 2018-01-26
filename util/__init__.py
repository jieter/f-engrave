import sys
import os

import externals

IN_AXIS = "AXIS_PROGRESS_BAR" in os.environ

# Setting QUIET to True will stop almost all console messages
QUIET = False

VERSION = sys.version_info[0]

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
    import tkinter.messagebox
else:
    from Tkinter import *
    from tkFileDialog import *
    import tkMessageBox


def fmessage(text, newline=True):
    if IN_AXIS or QUIET:
        return
    try:
        sys.stdout.write(text)
        if newline:
            sys.stdout.write("\n")
    except:
        pass


try:
    PIL = externals.check_pil()
    TTF_AVAILABLE = externals.check_ttf()
    POTRACE_AVAILABLE = externals.check_potrace()
except Exception, e:
    fmessage(e)


#TODO remove?
def message_box(title, message):
    if VERSION == 3:
        tkinter.messagebox.showinfo(title, message)
    else:
        tkMessageBox.showinfo(title, message)
        pass


def message_ask_ok_cancel(title, message):
    if VERSION == 3:
        result = tkinter.messagebox.askokcancel(title, message)
    else:
        result = tkMessageBox.askokcancel(title, message)
    return result
