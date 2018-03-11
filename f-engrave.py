#!/usr/bin/env python

from application.settings import Settings
from util import f_engrave_version

"""
    oof-engrave.py G-Code Generator

    A refactored version of f-engrave. More object oriented, hence the name.
    Which in turn is based on the version that Jieter started in 2014.

    Github:
    https://github.com/Blokkendoos/OOF-Engrave
    https://github.com/jieter/f-engrave

    Original:
    http://scorchworks.com/Fengrave/fengrave.html

    Original F-Engrave
    ==================
    f-engrave.py G-Code Generator
    Copyright (C) <2017>  <Scorch>
    Source was used from the following works:
              engrave-11.py G-Code Generator -- Lawrence Glaister --
              GUI framework from arcbuddy.py -- John Thornton  --
              cxf2cnc.py v0.5 font parsing code --- Ben Lipkowitz(fenn) --
              dxf.py DXF Viewer (http://code.google.com/p/dxf-reader/)
              DXF2GCODE (http://code.google.com/p/dfxf2gcode/)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    To make it a menu item in Ubuntu use the Alacarte Menu Editor and add
    the command python YourPathToThisFile/ThisFilesName.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at:
    http://wiki.linuxcnc.org/cgi-bin/emcinfo.pl?Simple_EMC_G-Code_Generators

    Version 0.1 Initial code

    Version 0.2 - Added V-Carve code
                - Fixed potential inf loop
                - Added pan and zoom
                - Moved Font file read out of calculation loop (increased speed)

    Version 0.3 - Bug fix for flip normals and flip text
                - Moved depth scalar calc out of for loop

    Version 0.4 - Added importing for DXF files
                - Added import True Type fonts using the ttf2cxf_stream helper program
                - Fixed line thickness display when zooming

    Version 0.5 - Added support for more DXF entity types POLYLINE and LEADER (leaders won't have arrow heads)
                - Added global accuracy setting
                - Added straight line detection in v-carve output (reduces number of G1 commands and output file size)
                - Improved handling of closed loops in v-carving
                - Added global variable named "Zero" for non-zero checks

    Version 0.6 - Added import Portable BitMap (PBM) images using Potrace as a helper program
                - Default directory for opening PBM and DXF files is now set to the current font directory
                - Default directory for and saving is now set to the users home directory
                - Helper programs should now be found if they are in the global search path or F-Engrave
                    script folder (Previously the helper programs needed to be in f-engrave script folder)

    Version 0.7 - Increased speed of v-carve calculation for large designs.  Approximately 20 times faster now.
                - Added window that displays status and contains a stop button for v-carve calculations
                - Fixed display so that it no longer freezes during long calculations
                - Fixed divide by zero error for certain fonts (Bug in Versions 0.5 and 0.6)

    Version 0.8 - Changed interface when working with image (DXF or PBM) files.
                - Added post processing logic to reduce number and distance of rapid moves
                - Fixed bug in DXF code that caused failure to import some DXF files.
                - Changed settings dialogs to allow recalculation and v-carving from the dialog window to preview settings
                - Added some logic for determining default .ngc names and directory when saving
                - Remove option for steps around corner (now internally calculated based on step length and bit geometry)

    Version 0.9 - Added arc fitting to g-code output
                - Fixed extended characters up to 255 (now uses numbers for the font index rather than the character)
                - Added option for a second operation g-code output file to clean-up islands and adjacent areas of a v-carving
                - Cleaned up some GUI bugs introduced in Version 0.8
                - Remove flip border normals option
                - Default to check "all" instead of current character "chr"
                - Changed the percent complete calculation to use the % of the total segment length rather than the segment count

    Version 0.91 - Fixed bug that caused Radius setting from text mode to affect image mode
                 - Fixed bug that caused some DXF files to fail erroneously

    Version 0.92 - Fixed bug that caused some buttons on the v-carve setting to not show up.

    Version 0.93 - Fixed bug that caused bad g-code in some cases.

    Version 1.00 - Added support for DXF polyline entity "bulges" (CamBam uses polyline bulges in DXF exports)
                 - Modified code to be compatible with Python 3.  (F-Engrave now works with Python 2.5 through 3.3)
                 - Removed stale references to grid the grid geometry manager
                 - Made minor user interface changes

    Version 1.01 - Fixed bug importing text information from g-code file in Python 3
                 - Put additional restriction on arc fitting to prevent arcing straight lines

    Version 1.02 - Put more restrictions on arc fitting to prevent huge erroneous circles
                 - Added key binding for CTRL-g to copy g-code to clipboard

    Version 1.10 - Added Command line option to set the default directory
                 - Added setting option for disabling the use of variable in the g-code output
                 - Added option for b-carving (using a ball end mill in v-carve mode)
                 - Added the text to be engraved to the top of the ngc file
                 - Added max depth to the v-carve settings
                 - Eliminated failure to save g-code file when the  image file name contains extended characters.
                 - Changed the default .ngc/.svg file name when saving. Now it always uses the base of the image file name.
                 - Changed the default behavior for v-carve step size. now the default in or mm value is always
                   reset (0.010in or 0.25mm) when switching between unit types.  This will ensure that metric users
                   will start with a good default step size setting.

    Version 1.11 - Fixed error when saving clean up g-code.
                 - Removed Extra spaces from beginning of g-code preamble and post-amble
                 - Added arc fitting to the variables that are saved to and read from the g-code output file

    Version 1.12 - Added logic to add newline to g-code preamble and g-code post-amble whenever a pipe character "|" is input

    Version 1.13 - Fixed bug preventing clean up tool-paths when the "Cut Depth Limit" variable is used.

    Version 1.14 - Fixed bug preventing the use of the Cut Depth Limit when b-carving
                 - Updated website info in help menu

    Version 1.20 - Added option to enable extended (Unicode) characters
                 - Also made a small change to the v-carve algorithm to fix a special case.

    Version 1.21 - Added more command line options including a batch mode with no GUI

    Version 1.22 - Fixed three bugs associated with importing dxf files
                 - Fixed bug associated with clean up calculations
                 - Changed minimum allowable line spacing from one to zero

    Version 1.30 - When importing DXF files F-Engrave no longer relies on the direction of the
                   loop (clockwise/counter-clockwise) to determines which side to cut.  Now F-Engrave
                   determines which loops are inside of other loops and flips the directions automatically.
                 - Added a new option for "V-Carve Loop Accuracy" in v-carve settings.  This setting
                   tells F-Engrave to ignore features smaller than the set value.  This allows F-Engrave
                   to ignore small DXF imperfections that resulted in bad tool paths.

    Version 1.31 - Fixed bug that was preventing batch mode from working in V1.30

    Version 1.32 - Added limit to the length of the engraved text included in g-code file
                   comment (to prevent error with long engraved text)
                 - Changed number of decimal places output when in mm mode to 3 (still 4 places for inches)
                 - Changed g-code format for G2/G3 arcs to center format arcs (generally preferred format)
                 - Hard coded G90 and G91.1 into g-code output to make sure the output will be interpreted
                   correctly by g-code interpreters.

    Version 1.33 - Added option to scale original input image size rather than specify a image height

    Version 1.34 - Eliminated G91.1 code when arc fitting is disabled.  When arc fitting is disabled
                   the code (G91.1) is not needed and it may cause problems for interpretors that do not
                   support that code (i.e. ShapeOko)

    Version 1.35 - Fixed importing of ellipse features from DXF files. Ellipse end overlapped the beginning
                   of the ellipse.
                 - Fixed saving long text to .ncg files.  Long text was truncated when a .ngc file was opened.

    Version 1.36 - Fixed major bug preventing saving .ncg files when the text was not a long string.

    Version 1.37 - Added logic to ignore very small line segments that caused problems v-carving some graphic input files.

    Version 1.38 - Changed default origin to the DXF input file origin when height is set by percentage of DXF image size.

    Version 1.39 - Fixed bug in v-carving routine resulting in failed v-carve calculation. (Bug introduced in Version 1.37)

    Version 1.40 - Added code to increased v-carving speed (based on input from geo01005)
                 - Windows executable file now generated from Python 2.5 with Psyco support (significant speed increase)
                 - Changed Default Origin behavior (for DXF/Image files) to be the origin of the DXF file or lower left
                   corner of the input image.
                 - Added automatic scaling of all linear dimensions values when changing between units (in/mm)
                 - Fixed bug in clean up function in the v-carve menu.  (the bug resulted in excessive Z motions in some cases)
                 - Fixed bug resulting in the last step of v-carving for any given loop to be skipped/incorrect.

    Version 1.41 - Adjusted global Zero value (previous value resulted in rounding errors in some cases)
                 - Removed use of accuracy (Acc) in the v-carve circle calculation

    Version 1.42 - Changed default to disable variables in g-code output.

    Version 1.43 - Fixed bug in v-carve cleanup routing that caused some areas to not be cleaned up.

    Version 1.44 - Fixed really bad bug in v-carve cleanup for bitmap images introduced in V1.43

    Version 1.45 - Added multi-pass cutting for v-carving
                 - Removed "Inside Corner Angle" and "Outside Corner Angle" options

    Version 1.46 - Fixed bug which cause double cutting of v-carve pattern when multi-pass cutting was disabled

    Version 1.47 - Added ability to read more types of DXF files (files using BLOCKS with the INSERT command)
                 - Fixed errors when running batch mode for v-carving.
                 - Added .tap to the drop down list of file extensions in the file save dialog

    Version 1.48 - Fixed another bug in the multi-pass code resulting in multi-pass cutting when multi-pass cutting was disabled.

    Version 1.49 - Added option to suppress option recovery comments in the g-code output
                 - Added button in "General Settings" to automatically save a configuration (config.ngc) file

    Version 1.50 - Modified helper program (ttf2cxf_stream) and F-Engrave interaction with it to better control
                   the line segment approximation of arcs.
                 - Added straight cutter support
                 - Added option to create prismatic cuts (inverse of v-carve).  This option opens the
                   possibility of making v-carve inlays.
                 - Fixed minor bug in the v-bit cleanup tool-path generation
                 - Changed the behavior when using inverting normals for v-carving.  Now a box is automatically
                   generated to bound the cutting on the outside of the design/lettering.  The size of the box is
                   controlled by the Box/Circle Gap setting in the general settings.
                 - Removed v-carve accuracy setting
                 - Added option for radius format g-code arcs when arc fitting.  This will help compatibility
                   with g-code interpreters that are missing support for center format arcs.

    Version 1.51 - Added Plunge feed rate setting (if set to zero the normal feed rate applies)
                 - Removed default coolant start/stop M codes for the header and footer
                 - Changed default footer to include a newline character between the M codes another Shapeoko/GRBL problem.
                 - Fixed some Python 3 incompatibilities with reading configuration files

    Version 1.52 - Fixed potential divide by zero error in DXF reader
                 - Text mode now includes space for leading carriage returns (i.e. Carriage returns before text characters)

    Version 1.53 - Changed space for leading carriage returns to only apply at 0,90,270 and 180 degree rotations.
                 - Added floating tool tips to the options on the main window (hover over the option labels to see the tool tip text)

    Version 1.54 - Fixed bug that resulted in errors if the path to a file contained the text of an F-Engrave setting variable
                 - Reduced time to open existing g-code files by eliminating unnecessary recalculation calls.
                 - Added configuration variable to remember the last. Folder location used when a configuration file is saved.
                 - Added support for most jpg, gif, tif and png files (it is still best to use Bitmaps)
                 - After saving a new configuration file the settings menu will now pop back to the top (sometimes it would get buried under other windows)
                 - Now searches current folder and home folder for image files when opening existing g-code files.
                   previously the image file needed to be in the exact path location as when the file was saved

    Version 1.55 - Fixed error in line/curve fitting that resulted in bad output with high Accuracy settings
                 - Fixed missing parentheses on file close commands (resulted in problems when using PyPy
                 - Suppress comments in g-code should now suppress all full line g-code comments
                 - Fixed error that resulted in cutting outside the lines with large Accuracy settings

    Version 1.56 - Changed line/curve fitting to use Douglas-Peucker curve fitting routine originally from LinuxCNC image2gcode
                 - Re-enabled the use of #2 variable when engraving with variable enabled (was broken in previous version)
                 - Fixed SVG export (was broken in previous version)

    Version 1.57 - Fixed feed rate. Changes in 1.56 resulted in feed rate not being written to g-code file.

    Version 1.58 - Fixed some special cases which resulted in errors being thrown (v-carve single lines)
                 - Changed the default settings to be more compatible with incomplete g-code interpretors like GRBL

    Version 1.59 - Fixed bug in arc fitting
                 - Rewrote Cleanup operation calculations (fixes a bug that resulted in some areas not being cleaned up
                 - Changed flip normals behavior, There are now two options: Flip Normals and Add Box (Flip Normals)
                 - Changed prismatic cut to allow the use of either of the two Flip normals options (one of the two
                   Flip normals options must be selected for the inlay cuts to be performed properly
                 - Added DXF Export option (with and without auto closed loops)

    Version 1.60 - Fixed divide by zero error in some cleanup sceneries.

    Version 1.61 - Fixed a bug that prevented opening DXF files that contain no features with positive Y coordinates

    Version 1.62 - Fixed a bug that resulted in bad cleanup tool paths in some situations

    Version 1.63 - Removed code that loaded _imaging module.  The module is not needed
                 - Changed "Open F-Engrave G-Code File" "Read Settings From File"
                 - Added "Save Setting to File" file option in File menu
                 - Fixed v-bit cleanup step over. Generated step was twice the input cleanup step.
                 - Updated icon.
                 - Added console version of application to windows distribution. For batch mode in Windows.

    Version 1.64 - Fixed bug that created erroneous lines in some circumstances during v-carving.
                 - Mapped save function to Control-S for easier g-code saving.

    Version 1.65 - Fixed bug in sort_for_v_carve that resulted in an error for certain designs.

    Version 1.65b - OOF-Engrave: refactored F-Engrave source code.

"""

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
    app.master.title("F-Engrave v" + f_engrave_version())
    app.master.iconname("F-Engrave")
    app.master.minsize(900, 600)

    app.f_engrave_init()

    icon.add_to_app(app)

    root.mainloop()
