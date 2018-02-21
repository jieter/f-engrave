import getopt
import webbrowser
# from math import tan

# from util import VERSION, POTRACE_AVAILABLE, TTF_AVAILABLE, PIL, IN_AXIS, header_text
from util import *

# from tooltip import ToolTip
from bitmap_settings import BitmapSettings
from vcarve_settings import VCarveSettings
from general_settings import GeneralSettings
from main_window import MainWindowTextLeft, MainWindowTextRight, MainWindowImageLeft

from geometry.coords import MyImage, MyText
# from geometry.font import Font
# from geometry.engrave import Engrave, Toolbit, VCarve, Straight
from geometry.engrave import Engrave

import readers
from readers import *
from writers import *

from settings import CUT_TYPE_VCARVE, CUT_TYPE_ENGRAVE

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
    # import tkinter.messagebox
else:
    from Tkinter import *
    from tkFileDialog import *
    # import tkMessageBox


class Gui(Frame):

    def __init__(self, master, settings):

        Frame.__init__(self, master)
        self.w = 780
        self.h = 490
        self.master = master

        self.initComplete = False
        self.delay_calc = False

        self.settings = settings
        self.font = Font()
        self.text = MyText()
        self.image = MyImage()
        self.plot_bbox = BoundingBox()

        # the main window consists of three rows and three columns
        self.grid()
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1, minsize=400)
        self.master.rowconfigure(0, minsize=400)
        self.master.rowconfigure(2, minsize=20)
        # self.master.columnconfigure(0, minsize=250)
        # self.master.columnconfigure(2, minsize=250)

        self.mainwindow_image_left = MainWindowImageLeft(master, self, self.settings)
        self.mainwindow_text_left = MainWindowTextLeft(master, self, self.settings)
        self.mainwindow_text_right = MainWindowTextRight(master, self, self.settings)

        self.bind_keys()
        self.create_widgets()

        self.engrave = Engrave(self.settings)
        # engrave callbacks
        self.engrave.set_progress_callback(self.plot_toolpath)
        self.engrave.set_plot_progress_callback(self.plot_progress)
        self.engrave.set_status_callback(self.status_update)

        # callbacks (wherein this Gui/App acts as the Controller)
        self.Ctrl_Entry_units_var_Callback = None
        self.Ctrl_Scale_Linear_Inputs = None

    def general_settings_window(self):
        self.general_settings_window = GeneralSettings(self, self.settings)

    def bitmap_settings_window(self):
        self.bitmap_settings_window = BitmapSettings(self, self.settings)

    def vcarve_settings_window(self):
        self.vcarve_settings_window = VCarveSettings(self, self.settings)

    def status_update(self, msg, color='yellow'):
        self.statusMessage.set(msg)
        self.statusbar.configure(bg=color)
        self.master.update()
        # self.PreviewCanvas.update()

    def plot_progress(self, normv, color, radius):
        """
        Engrave progress callback
        """
        cszw = int(self.PreviewCanvas.cget("width"))
        cszh = int(self.PreviewCanvas.cget("height"))

        midx, midy = self.engrave.image.get_midxy()

        self.plot_circle(normv, midx, midy, cszw, cszh, color, radius, False)

    def readFontFile(self):
        self.font = readers.readFontFile(self.settings)

    def f_engrave_init(self):
        self.master.update()

        if self.settings.get('input_type') == "text":
            self.font = readers.readFontFile(self.settings)
        else:
            self.load_image_file()

        self.initComplete = True
        self.menu_mode_change()

    def bind_keys(self):
        self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind('<Escape>', self.KEY_ESC)
        self.master.bind('<F1>', self.KEY_F1)
        self.master.bind('<F2>', self.KEY_F2)
        self.master.bind('<F3>', self.KEY_F3)
        self.master.bind('<F4>', self.KEY_F4)
        self.master.bind('<F5>', self.KEY_F5)  # self.Recalculate_Click)
        self.master.bind('<Prior>', self.KEY_ZOOM_IN)  # Page Up
        self.master.bind('<Next>', self.KEY_ZOOM_OUT)  # Page Down
        self.master.bind('<Control-g>', self.KEY_CTRL_G)
        self.master.bind('<Control-s>', self.KEY_CTRL_S)  # Save

    def create_widgets(self):
        self.batch = BooleanVar()

        self.show_thick = BooleanVar()
        self.show_axis = BooleanVar()
        self.show_box = BooleanVar()

        self.fontdex = BooleanVar()
        self.v_pplot = BooleanVar()

        # self.useIMGsize = BooleanVar()

        self.cut_type = StringVar()
        self.input_type = StringVar()

        self.current_input_file = StringVar()
        self.bounding_box = StringVar()

        self.initialise_settings()

        self.segID = []
        self.font = Font()

        self.current_input_file.set(" ")
        self.bounding_box.set(" ")

        self.plot_scale = 0

        # PAN and ZOOM STUFF
        self.panx = 0
        self.panx = 0
        self.lastx = 0
        self.lasty = 0

        # Derived variables
        self.calc_depth_limit()

        config_file = "config.ngc"
        home_config1 = self.HOME_DIR + "/" + config_file
        config_file2 = ".fengraverc"
        home_config2 = self.HOME_DIR + "/" + config_file2
        if (os.path.isfile(config_file)):
            self.Open_G_Code_File(config_file)
        elif (os.path.isfile(home_config1)):
            self.Open_G_Code_File(home_config1)
        elif (os.path.isfile(home_config2)):
            self.Open_G_Code_File(home_config2)

        ##########################################################################
        #                             COMMAND LINE                               #
        ##########################################################################
        opts, args = None, None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hbg:f:d:t:",
                                       ["help", "batch", "gcode_file", "fontdir=", "defdir=", "text="])
        except:
            fmessage('Unable interpret command line options')
            sys.exit()

        for option, value in opts:
            if option in ('-h', '--help'):
                fmessage(' ')
                fmessage('Usage: python f-engrave.py [-g file | -f fontdir | -d directory | -t text | -b ]')
                fmessage('-g    : f-engrave gcode output file to read (also --gcode_file)')
                fmessage('-f    : path to font file, directory or image file (also --fontdir)')
                fmessage('-d    : default directory (also --defdir)')
                fmessage('-t    : engrave text (also --text)')
                fmessage('-b    : batch mode (also --batch)')
                fmessage('-h    : print this help (also --help)\n')
                sys.exit()

            if option in ('-g', '--gcode_file'):
                self.Open_G_Code_File(value)
                self.NGC_FILE = value

            if option in ('-f', '--fontdir'):
                if os.path.isdir(value):
                    self.settings.set('fontdir', value)
                elif os.path.isfile(value):
                    dirname = os.path.dirname(value)
                    fileName, fileExtension = os.path.splitext(value)
                    TYPE = fileExtension.upper()
                    if TYPE == '.CXF' or TYPE == '.TTF':
                        self.input_type.set('text')
                        self.settings.set('fontdir', dirname)
                        self.settings.set('fontfile.', os.path.basename(fileName) + fileExtension)
                    else:
                        self.input_type.set('image')
                        self.IMAGE_FILE = value
                    self.settings.set('input_type', self.input_type.get())
                else:
                    fmessage("File/Directory Not Found:\t%s" % value)

            if option in ('-d', '--defdir'):
                self.HOME_DIR = value
                if str.find(self.NGC_FILE, '/None') != -1:
                    self.settings.set('NGC_FILE', self.HOME_DIR + '/None')
                if str.find(self.IMAGE_FILE, '/None') != -1:
                    self.settings.set('IMAGE_FILE', self.HOME_DIR + '/None')

            if option in ('-t', '--text'):
                value = value.replace('|', '\n')

                self.default_text = value
            if option in ('-b', '--batch'):
                self.batch.set(True)
                self.settings.set('batch', True)

        if self.batch.get() is True:

            fmessage('(F-Engrave Batch Mode)')

            if self.settings.get('input_type') == "text":
                self.font = readers.readFontFile(self.settings)
            else:
                self.load_image_file()

            self.do_it()

            if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
                self.v_carve_it()

            g_code = gcode(self.engrave)
            for line in g_code:
                try:
                    sys.stdout.write(line + '\n')
                except:
                    sys.stdout.write('(skipping line)\n')

            sys.exit()

        self.create_previewcanvas()
        self.create_input()
        self.create_statusbar()

        # Make Menu Bar
        self.menuBar = Menu(self.master, relief="raised", bd=2)

        top_File = Menu(self.menuBar, tearoff=0)
        top_File.add("command", label="Save Settings to File", command=self.menu_File_Save_Settings_File)
        top_File.add("command", label="Read Settings from File", command=self.menu_File_Open_G_Code_File)
        top_File.add_separator()
        if POTRACE_AVAILABLE:
            top_File.add("command", label="Open DXF/Bitmap", command=self.menu_File_Open_DXF_File)
        else:
            top_File.add("command", label="Open DXF", command=self.menu_File_Open_DXF_File)
        top_File.add_separator()
        top_File.add("command", label="Save G-Code", command=self.menu_File_Save_G_Code_File)
        top_File.add_separator()
        top_File.add("command", label="Export SVG", command=self.menu_File_Save_SVG_File)
        top_File.add("command", label="Export DXF", command=self.menu_File_Save_DXF_File)
        top_File.add("command", label="Export DXF (close loops)", command=self.menu_File_Save_DXF_File_close_loops)
        if IN_AXIS:
            top_File.add("command", label="Write To Axis and Exit", command=self.WriteToAxis)
        else:
            top_File.add("command", label="Exit", command=self.menu_File_Quit)
        self.menuBar.add("cascade", label="File", menu=top_File)

        top_Edit = Menu(self.menuBar, tearoff=0)
        top_Edit.add("command", label="Copy G-Code Data to Clipboard", command=self.CopyClipboard_GCode)
        top_Edit.add("command", label="Copy SVG Data to Clipboard", command=self.CopyClipboard_SVG)
        self.menuBar.add("cascade", label="Edit", menu=top_Edit)

        top_View = Menu(self.menuBar, tearoff=0)
        top_View.add("command", label="Recalculate", command=self.menu_View_Recalculate)
        top_View.add_separator()

        top_View.add("command", label="Zoom In <Page Up>", command=self.menu_View_Zoom_in)
        top_View.add("command", label="Zoom Out <Page Down>", command=self.menu_View_Zoom_out)
        top_View.add("command", label="Zoom Fit <F5>", command=self.menu_View_Refresh)

        top_View.add_separator()

        top_View.add_checkbutton(label="Show Thickness", variable=self.show_thick, command=self.menu_View_Refresh)
        top_View.add_checkbutton(label="Show Origin Axis", variable=self.show_axis, command=self.menu_View_Refresh)
        top_View.add_checkbutton(label="Show Bounding Box", variable=self.show_box, command=self.menu_View_Refresh)
        self.menuBar.add("cascade", label="View", menu=top_View)
        self.show_thick.trace_variable("w", self.Entry_show_thick_Callback)
        self.show_axis.trace_variable("w", self.Entry_show_axis_Callback)
        self.show_box.trace_variable("w", self.Entry_show_box_Callback)

        top_Settings = Menu(self.menuBar, tearoff=0)
        top_Settings.add("command", label="General Settings", command=self.general_settings_window)
        top_Settings.add("command", label="V-Carve Settings", command=self.vcarve_settings_window)
        if POTRACE_AVAILABLE:
            top_Settings.add("command", label="Bitmap Import Settings", command=self.bitmap_settings_window)

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label="Engrave Mode", variable=self.cut_type, value="engrave")
        top_Settings.add_radiobutton(label="V-Carve Mode", variable=self.cut_type, value="v-carve")
        self.cut_type.trace_variable("w", self.Entry_cut_type_Callback)

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label="Text Mode (CXF/TTF)", variable=self.input_type, value="text",
                                     command=self.menu_mode_change)
        top_Settings.add_radiobutton(label="Image Mode (DXF/Bitmap)", variable=self.input_type, value="image",
                                     command=self.menu_mode_change)

        self.menuBar.add("cascade", label="Settings", menu=top_Settings)

        top_Help = Menu(self.menuBar, tearoff=0)
        top_Help.add("command", label="About (E-Mail)", command=self.menu_Help_About)
        top_Help.add("command", label="Help (Web Page)", command=self.menu_Help_Web)
        self.menuBar.add("cascade", label="Help", menu=top_Help)

        self.master.config(menu=self.menuBar)

    def create_previewcanvas(self):
        # self.PreviewCanvas = Canvas(self.master,
        #                             width=350,
        #                             height=350, background="grey")
        self.PreviewCanvas = Canvas(self.master, background="grey")

        self.PreviewCanvas.bind("<Button-4>", self._mouseZoomIn)
        self.PreviewCanvas.bind("<Button-5>", self._mouseZoomOut)
        self.PreviewCanvas.bind("<2>", self.mousePanStart)
        self.PreviewCanvas.bind("<B2-Motion>", self.mousePan)
        self.PreviewCanvas.bind("<1>", self.mouseZoomStart)
        self.PreviewCanvas.bind("<B1-Motion>", self.mouseZoom)
        self.PreviewCanvas.bind("<3>", self.mousePanStart)
        self.PreviewCanvas.bind("<B3-Motion>", self.mousePan)

    def create_input(self):
        self.input_frame = Frame(self.master)
        self.input_frame.grid_propagate(False)

        scrollbar = Scrollbar(self.input_frame, orient=VERTICAL)

        self.Input_Label = Label(self.input_frame, text="Input Text:", anchor=W)
        self.Input_Label.pack(side=TOP, anchor=W)

        self.input = Text(self.input_frame, width="40", height="6", yscrollcommand=scrollbar.set, bg='white')
        self.input.insert(END, self.default_text)
        self.input.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar.config(command=self.input.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.input.bind("<Key>", self.recalculate_RQD_Nocalc)

    def create_statusbar(self):
        self.statusMessage = StringVar()
        self.statusMessage.set("")
        self.statusbar = Label(self.master,
                               textvariable=self.statusMessage,
                               bd=1, relief=SUNKEN)
        self.statusMessage.set("Welcome to F-Engrave")
        self.statusbar.grid(row=2, column=0, columnspan=3, sticky=W + E + N + S)

    def initialise_settings(self):
        """
        Initialise the TK widgets with the values from settings
        """
        self.batch.set(self.settings.get('batch'))

        self.show_axis.set(self.settings.get('show_axis'))
        self.show_box.set(self.settings.get('show_box'))
        self.show_thick.set(self.settings.get('show_thick'))

        self.fontdex.set(self.settings.get('fontdex'))
        self.v_pplot.set(self.settings.get('v_pplot'))

        self.cut_type.set(self.settings.get('cut_type'))
        self.input_type.set(self.settings.get('input_type'))
        self.default_text = self.settings.get('default_text')

        self.HOME_DIR = (self.settings.get('HOME_DIR'))
        self.NGC_FILE = (self.settings.get('NGC_FILE'))
        self.IMAGE_FILE = (self.settings.get('IMAGE_FILE'))

    def entry_set(self, val, check_flag=0, new=0, setting=None):

        if check_flag == OK and new == 0:
            try:
                self.statusbar.configure(bg='yellow')
                val.configure(bg='yellow')
                self.statusMessage.set(" Recalculation required.")
            except:
                pass
        elif check_flag == NAN:
            try:
                val.configure(bg='red')
                self.statusbar.configure(bg='red')
                self.statusMessage.set(" Value should be a number. ")
            except:
                pass
        elif check_flag == INV:
            try:
                self.statusbar.configure(bg='red')
                val.configure(bg='red')
            except:
                pass
        elif (check_flag == OK or check_flag == NOR) and new == 1:
            try:
                self.statusbar.configure(bg='white')
                self.statusMessage.set(self.bounding_box.get())
                val.configure(bg='white')
            except:
                pass
        elif check_flag == NOR and new == 0:
            try:
                self.statusbar.configure(bg='white')
                self.statusMessage.set(self.bounding_box.get())
                val.configure(bg='white')
            except:
                pass
        elif (check_flag == OK or check_flag == NOR) and new == 2:
                return 0

        if (setting is not None) and \
                (check_flag == OK or check_flag == NOR) and \
                new == 0:
            self.settings.set(setting, val.get())

        return 1

    def write_config_file(self, event):

        gcode = []

        gcode.extend(header_text())
        gcode.extend(self.settings.to_gcode())

        config_filename = self.settings.get('config_filename')
        configname_full = self.settings.get('HOME_DIR') + "/" + config_filename
        win_id = self.grab_current()
        if (os.path.isfile(configname_full)):
            if not message_ask_ok_cancel("Replace", "Replace Exiting Configuration File?\n" + configname_full):
                try:
                    win_id.withdraw()
                    win_id.deiconify()
                except:
                    pass
                return

        try:
            fout = open(configname_full, 'w')
        except:
            self.statusMessage.set("Unable to open file for writing: %s" % (configname_full))
            self.statusbar.configure(bg='red')
            return

        for line in gcode:
            try:
                fout.write(line + '\n')
            except:
                fout.write('(skipping line)\n')
        fout.close()
        self.statusMessage.set("Configuration File Saved: %s" % (configname_full))
        self.statusbar.configure(bg='white')

        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def CopyClipboard_GCode(self):
        self.clipboard_clear()
        if self.Check_All_Variables() > 0:
            return
        g_code = gcode(self.engrave)
        for line in g_code:
            self.clipboard_append(str(line) + '\n')

    def CopyClipboard_SVG(self):
        self.clipboard_clear()

        self.engrave.refresh_coords()  # TODO
        svgcode = svg(self.engrave)

        for line in svgcode:
            self.clipboard_append(line + '\n')

    def WriteToAxis(self):
        if self.Check_All_Variables() > 0:
            return
        g_code = gcode(self.engrave)
        for line in g_code:
            try:
                sys.stdout.write(str(line) + '\n')
            except:
                pass
        self.Quit_Click(None)

    def Recalculate_Click(self, event):
        self.do_it()

    def Settings_ReLoad_Click(self, event, arg1="", arg2=""):

        win_id = self.grab_current()
        self.do_it()

        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def Calculate_CLEAN_Click(self):

        # TSTART = time() # TEST
        win_id = self.grab_current()

        if self.engrave.number_of_clean_segments == 0:
            mess = "Calculate V-Carve must be executed\n"
            mess += "prior to Calculating Cleanup"
            message_box("Cleanup Info", mess)
        else:
            stop = self.Clean_Calc_Click("straight")
            if not stop:
                self.Clean_Calc_Click("v-bit")
            self.plot_toolpath()

        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass
        # print "time for cleanup calculations: ",time()-TSTART # TEST

    def Write_Clean_Click(self):

        win_id = self.grab_current()

        if (self.settings.get('clean_P') +
            self.settings.get('clean_X') +
            self.settings.get('clean_Y') +
            self.settings.get('v_clean_P') +
            self.settings.get('v_clean_Y') +
            self.settings.get('v_clean_X')) != 0:

            if self.engrave.number_of_clean_coords_sort == 0:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message_box("Cleanup Info", mess)
            else:
                self.menu_File_Save_clean_G_Code_File("straight")
        else:
            mess = "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no V Cleanup paths were found)"
            message_box("Cleanup Info", mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_V_Clean_Click(self):

        win_id = self.grab_current()

        if (self.settings.get('clean_P') +
            self.settings.get('clean_X') +
            self.settings.get('clean_Y') +
            self.settings.get('v_clean_P') +
            self.settings.get('v_clean_Y') +
            self.settings.get('v_clean_X')) != 0:

            if self.engrave.number_of_v_clean_coords_sort == 0:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving V Cleanup G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message_box("Cleanup Info", mess)
            else:
                self.menu_File_Save_clean_G_Code_File("v-bit")
        else:
            mess = "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no Cleanup paths were found)"
            message_box("Cleanup Info", mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Close_Current_Window_Click(self):
        win_id = self.grab_current()
        win_id.destroy()

    def Stop_Click(self, event):
        self.engrave.stop_calc()

    def v_pplot_Click(self, event):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.engrave.refresh_v_pplot()

    # TODO calc_depth_limit in GCode writer too

    def calc_depth_limit(self):
        """
        Calculate depth limit
        Returns True if the resulting depth limit is valid, otherwise False
        """
        settings = self.settings

        try:
            depth_lim_in = settings.get('v_depth_lim')
            bit_shape = settings.get('bit_shape')
            v_bit_dia = settings.get('v_bit_dia')
            v_bit_angle = settings.get('v_bit_angle')

            if bit_shape == "VBIT":
                half_angle = radians(v_bit_angle) / 2.0
                bit_depth = -v_bit_dia / 2.0 / tan(half_angle)
            elif bit_shape == "BALL":
                bit_depth = -v_bit_dia / 2.0
            elif bit_shape == "FLAT":
                bit_depth = -v_bit_dia / 2.0
            else:
                pass

            if settings.get('bit_shape') != "FLAT":
                if depth_lim_in < 0.0:
                    depth_limit = max(bit_depth, depth_lim_in)
                else:
                    depth_limit = bit_depth
            else:
                if depth_lim_in < 0.0:
                    depth_limit = depth_lim_in
                else:
                    depth_limit = bit_depth

            depth_limit = "%.3f" % depth_limit
            settings.set('max_cut', depth_limit)
            return True

        except:
            # depth_limit = "error"
            return False

    def calc_r_inlay_top(self):
        half_angle = radians(self.settings.get('v_bit_angle') / 2.0)
        inlay_depth = self.settings.get('v_depth_lim')
        r_inlay_top = tan(half_angle) * inlay_depth
        return r_inlay_top

    ###############
    # Menu        #
    ###############
    def Entry_show_axis_Callback(self, varName, index, mode):
        self.settings.set('show_axis', self.show_axis.get())

    def Entry_show_box_Callback(self, varName, index, mode):
        self.settings.set('show_box', self.show_box.get())

    def Entry_show_thick_Callback(self, varName, index, mode):
        self.settings.set('show_thick', self.show_thick.get())

    def Entry_cut_type_Callback(self, varName, index, mode):
        self.settings.set('cut_type', self.cut_type.get())

    def Check_All_Variables(self):

        if self.batch.get():
            return 0  # nothing to be done in batchmode

        # TODO rid the text/image dependency
        if self.settings.get('input_type') == 'text':
            error_cnt = self.mainwindow_text_left.Check_All_Variables() + \
                        self.mainwindow_text_right.Check_All_Variables()
        else:
            error_cnt = self.mainwindow_image_left.Check_All_Variables()

        if error_cnt > 0:
            self.statusbar.configure(bg='red')
            self.statusMessage.set(" Entry Error Detected: Check Entry Values in Main Window ")

        return error_cnt

    # TODO refactor this into a separate object?

    def V_Carve_Calc_Click(self):
        if self.Check_All_Variables() > 0:
            return

        vcalc_status = Toplevel(width=525, height=60)
        # Use grab_set to prevent user input in the main window during calculations
        vcalc_status.grab_set()

        self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT, height=1, anchor=W)
        self.statusbar2.place(x=130 + 12 + 12, y=6, width=350, height=30)
        self.statusMessage.set("Starting Calculation")
        self.statusbar.configure(bg='yellow')

        self.stop_button = Button(vcalc_status, text="Stop Calculation")
        self.stop_button.place(x=12, y=17, width=130, height=30)
        self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

        self.Checkbutton_v_pplot = Checkbutton(vcalc_status, text="Plot During V-Carve Calculation", anchor=W)
        self.Checkbutton_v_pplot.place(x=130 + 12 + 12, y=34, width=300, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)
        self.Checkbutton_v_pplot.bind("<ButtonRelease-1>", self.v_pplot_Click)

        vcalc_status.resizable(0, 0)
        vcalc_status.title('Executing V-Carve')
        vcalc_status.iconname("F-Engrave")

        try:
            vcalc_status.iconbitmap(bitmap="@emblem64")
        except:
            pass
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                vcalc_status.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        self.v_carve_it()
        self.menu_View_Refresh()
        vcalc_status.grab_release()
        try:
            vcalc_status.destroy()
        except:
            pass

    def Clean_Calc_Click(self, bit_type="straight"):

        if self.Check_All_Variables() > 0:
            return True  # Stop

        if self.engrave.number_of_clean_coords() == 0:

            vcalc_status = Toplevel(width=525, height=50)

            # Use grab_set to prevent user input in the main window during calculations
            vcalc_status.grab_set()

            self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT, height=1)
            self.statusbar2.place(x=130 + 12 + 12, y=12, width=350, height=30)
            self.statusMessage.set("Starting Clean Calculation")
            self.statusbar.configure(bg='yellow')

            self.stop_button = Button(vcalc_status, text="Stop Calculation")
            self.stop_button.place(x=12, y=12, width=130, height=30)
            self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

            vcalc_status.resizable(0, 0)
            vcalc_status.title('Executing Clean Area Calculation')
            vcalc_status.iconname("F-Engrave")

            try:
                vcalc_status.iconbitmap(bitmap="@emblem64")
            except:
                try:  # Attempt to create temporary icon bitmap file
                    temp_icon("f_engrave_icon")
                    vcalc_status.iconbitmap("@f_engrave_icon")
                    os.remove("f_engrave_icon")
                except:
                    pass

            self.v_carve_it(clean=True)

            vcalc_status.grab_release()

            try:
                vcalc_status.destroy()
            except:
                pass

        # prepare statusbar(color) for progress updates
        self.statusbar.configure(bg='yellow')
        self.engrave.clean_path_calc(bit_type)

        if self.engrave.number_of_clean_coords() == 0:
            return True  # stop
        else:
            return False

    def menu_File_Open_G_Code_File(self):
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR
        fileselect = askopenfilename(filetypes=[("F-Engrave G-code Files", "*.ngc"),
                                                ("All Files", "*")],
                                     initialdir=init_dir)

        if fileselect != '' and fileselect != ():
            self.Open_G_Code_File(fileselect)

    def menu_File_Open_DXF_File(self):

        init_dir = os.path.dirname(self.IMAGE_FILE)  # TODO  settings

        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if POTRACE_AVAILABLE:
            if PIL:
                fileselect = askopenfilename(
                    filetypes=[("DXF/Bitmap Files", ("*.dxf", "*.bmp", "*.pbm", "*.ppm", "*.pgm", "*.pnm")),
                               ("DXF Files", "*.dxf"),
                               ("Bitmap Files", ("*.bmp", "*.pbm", "*.ppm", "*.pgm", "*.pnm")),
                               ("Slower Image Files", ("*.jpg", "*.png", "*.gif", "*.tif")),
                               ("All Files", "*")],
                    initialdir=init_dir)
            else:
                fileselect = askopenfilename(
                    filetypes=[("DXF/Bitmap Files", ("*.dxf", "*.bmp", "*.pbm", "*.ppm", "*.pgm", "*.pnm")),
                               ("DXF Files", "*.dxf"),
                               ("Bitmap Files", ("*.bmp", "*.pbm", "*.ppm", "*.pgm", "*.pnm")),
                               ("All Files", "*")],
                    initialdir=init_dir)
        else:
            fileselect = askopenfilename(filetypes=[("DXF Files", "*.dxf"),
                                                    ("All Files", "*")],
                                         initialdir=init_dir)

        if fileselect != '' and fileselect != ():
            self.IMAGE_FILE = fileselect
            self.settings.set('IMAGE_FILE', fileselect)
            self.load_image_file()
            self.do_it()

    def load_image_file(self):

        # TODO future read_image_file will return a MyImage instead of a Font instance
        font = readers.read_image_file(self.settings)
        if len(font) > 0:
            stroke_list = font[ord("F")].stroke_list
            self.image.set_coords_from_strokes(stroke_list)
            self.input_type.set(self.settings.get('input_type'))  # input_type may have been changed by read_image_file
        else:
            self.image = MyImage()

    def Open_G_Code_File(self, filename):

        self.delay_calc = True
        try:
            fin = open(filename, 'r')
        except:
            fmessage("Unable to open file: %s" % (filename))
            return
        fin.close()

        self.settings.from_configfile(filename)
        self.initialise_settings()

        text_codes = []
        file_full = self.settings.get_fontfile()
        fileName, fileExtension = os.path.splitext(file_full)
        TYPE = fileExtension.upper()

        if TYPE != '.CXF' and TYPE != '.TTF' and TYPE != '':
            if os.path.isfile(file_full):
                self.input_type.set("image")
                self.settings.set('input_type', self.input_type.get())

        # TODO why adjust the boxgap?
        if self.settings.get('boxsize') != "0":
            self.settings.set('boxgap', self.settings.get('boxsize') * self.settings.get('line_thickness'))

        # TODO is this for backward compatibility?
        # if self.arc_fit.get() == "0":
        #     self.arc_fit.set("none")
        # elif self.arc_fit.get() == "1":
        #     self.arc_fit.set("center")

        if not self.settings.get('arc_fit') in ['none', 'center', 'radius']:
            self.settings.set('arc_fit', 'center')

        if text_codes != []:
            try:
                self.input.delete(1.0, END)
                for Ch in text_codes:
                    try:
                        self.input.insert(END, "%c" % (unichr(int(Ch))))
                    except:
                        self.input.insert(END, "%c" % (chr(int(Ch))))
            except:
                self.default_text = ''
                for Ch in text_codes:
                    try:
                        self.default_text = self.default_text + "%c" % (unichr(int(Ch)))
                    except:
                        self.default_text = self.default_text + "%c" % (chr(int(Ch)))

        self.calc_depth_limit()

        self.delay_calc = False

        if self.initComplete:
            self.NGC_FILE = filename
            self.menu_mode_change()

    def menu_File_Save_Settings_File(self):

        gcode = self.settings.to_gcode()

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        if self.settings.get('input_type') == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(defaultextension='.txt',
                                     filetypes=[("Settings File", "*.txt"), ("All Files", "*")],
                                     initialdir=init_dir,
                                     initialfile=init_file)

        if filename != '' and filename != ():
            try:
                fout = open(filename, 'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" % (filename))
                self.statusbar.configure(bg='red')
                return
            for line in gcode:
                try:
                    fout.write(line + '\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg='white')

    def menu_File_Save_G_Code_File(self):

        if self.Check_All_Variables() > 0:
            return

        if self.engrave.number_of_v_coords() == 0 and self.cut_type.get() == CUT_TYPE_VCARVE:
            mess = "V-carve path data does not exist.  "
            mess = mess + "Only settings will be saved.\n\n"
            mess = mess + "To generate V-Carve path data Click on the"
            mess = mess + "\"Calculate V-Carve\" button on the main window."
            if not message_ask_ok_cancel("Continue", mess):
                return

        self.engrave.refresh_coords()  # TODO
        g_code = gcode(self.engrave)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.settings.get('input_type') == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(defaultextension='.ngc',
                                     filetypes=[("G-Code File", "*.ngc"), ("TAP File", "*.tap"), ("All Files", "*")],
                                     initialdir=init_dir,
                                     initialfile=init_file)

        if filename != '' and filename != ():
            self.NGC_FILE = filename
            try:
                fout = open(filename, 'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" % filename)
                self.statusbar.configure(bg='red')
                return
            for line in g_code:
                try:
                    fout.write(line + '\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" % filename)
            self.statusbar.configure(bg='white')

    def menu_File_Save_clean_G_Code_File(self, bit_type="straight"):

        if self.Check_All_Variables() > 0:
            return

        g_code = write_clean_up(self.engrave, bit_type)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.settings.get('input_type') == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
            fileName_tmp, fileExtension = os.path.splitext(init_file)
            init_file = fileName_tmp
        else:
            init_file = "text"

        if bit_type == "v-bit":
            init_file = init_file + "_v" + self.settings.get('clean_name')
        else:
            init_file = init_file + self.settings.get('clean_name')

        filename = asksaveasfilename(defaultextension='.ngc',
                                     filetypes=[("G-Code File", "*.ngc"), ("TAP File", "*.tap"), ("All Files", "*")],
                                     initialdir=init_dir,
                                     initialfile=init_file)

        if filename != '' and filename != ():
            try:
                fout = open(filename, 'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" % (filename))
                self.statusbar.configure(bg='red')
                return
            for line in g_code:
                try:
                    fout.write(line + '\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg='white')

    def menu_File_Save_SVG_File(self):

        self.engrave.refresh_coords()  # TODO
        svg_code = svg(self.engrave)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.settings.get('input_type') == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(defaultextension='.svg',
                                     filetypes=[("SVG File", "*.svg"), ("All Files", "*")],
                                     initialdir=init_dir,
                                     initialfile=init_file)

        if filename != '' and filename != ():
            try:
                fout = open(filename, 'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" % (filename))
                self.statusbar.configure(bg='red')
                return
            for line in svg_code:
                try:
                    fout.write(line + '\n')
                except:
                    pass
            fout.close()

            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg='white')

    def menu_File_Save_DXF_File_close_loops(self):
        self.menu_File_Save_DXF_File(close_loops=True)

    def menu_File_Save_DXF_File(self, close_loops=False):

        DXF_CODE = dxf(self.engrave, close_loops=close_loops)
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        # fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        if self.settings.get('input_type') != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(defaultextension='.dxf',
                                     filetypes=[("DXF File", "*.dxf"), ("All Files", "*")],
                                     initialdir=init_dir,
                                     initialfile=init_file)

        if filename != '' and filename != ():
            try:
                fout = open(filename, 'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" % (filename))
                self.statusbar.configure(bg='red')
                return
            for line in DXF_CODE:
                try:
                    fout.write(line + '\n')
                except:
                    pass
            fout.close()

            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg='white')

    def menu_File_Quit(self):
        if message_ask_ok_cancel("Exit", "Exiting F-Engrave...."):
            self.Quit_Click(None)

    def menu_View_Refresh_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_View_Refresh(self):
        if self.initComplete and self.batch.get() is False and self.delay_calc is False:
            dummy_event = Event()
            dummy_event.widget = self.master
            self.Master_Configure(dummy_event, 1)

    def menu_mode_change_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_mode_change(self):

        # TODO input
        self.settings.set('input_type', self.input_type.get())

        self.delay_calc = True
        dummy_event = Event()
        dummy_event.widget = self.master
        self.Master_Configure(dummy_event, True)
        self.delay_calc = False

        self.do_it()

    def menu_View_Recalculate(self):
        self.do_it()

    def menu_Help_About(self):
        about = "F-Engrave by Scorch.\n\n"
        about = about + "\163\143\157\162\143\150\100\163\143\157\162"
        about = about + "\143\150\167\157\162\153\163\056\143\157\155\n"
        about = about + "http://www.scorchworks.com/"
        message_box("About F-Engrave", about)

    def menu_Help_Web(self):
        webbrowser.open_new(r"http://www.scorchworks.com/Fengrave/fengrave_doc.html")

    def KEY_ESC(self, event):
        pass  # A stop calculation command may go here

    def KEY_F1(self, event):
        self.menu_Help_About()

    def KEY_F2(self, event):
        self.GEN_Settings_Window()

    def KEY_F3(self, event):
        self.vcarve_settings_window()

    def KEY_F4(self, event):
        self.bitmap_settings_window()

    def KEY_F5(self, event):
        self.menu_View_Refresh()

    def KEY_CTRL_G(self, event):
        self.CopyClipboard_GCode()

    def KEY_CTRL_S(self, event):
        self.menu_File_Save_G_Code_File()

    def Master_Configure(self, event, update=False):
        """
        The widget changed size (or location, on some platforms).
        The new size is provided in the width and height attributes of the event object passed to the callback.
        """
        if event.widget != self.master:
            return

        if self.batch.get():
            return

        # x = int(self.master.winfo_x())
        # y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())

        if abs(self.w - w) > 10 or abs(self.h - h) > 10 or update:

            self.w = w
            self.h = h

            # if self.cut_type.get() == CUT_TYPE_VCARVE:
            #     self.V_Carve_Calc.configure(state="normal", command=None)
            # else:
            #     self.V_Carve_Calc.configure(state="disabled", command=None)

            if self.settings.get('input_type') == "text":
                self.Master_Configure_text()
            else:
                self.Master_Configure_image()

            self.plot_toolpath()

    def Master_Configure_text(self):
        self.PreviewCanvas.grid_forget()
        self.input_frame.grid_forget()
        self.mainwindow_image_left.grid_forget()

        self.PreviewCanvas.grid(row=0, column=1, sticky=W + E + N + S)
        self.input_frame.grid(row=1, column=1, sticky=W + E + N + S)

        self.mainwindow_text_left.grid(row=0, rowspan=2, column=0, sticky=W + E + N + S)
        self.mainwindow_text_right.grid(row=0, rowspan=2, column=2, sticky=W + E + N + S)

        # main window callbacks
        self.Fontdir_Click = self.mainwindow_text_right.Fontdir_Click
        self.Ctrl_Entry_units_var_Callback = self.Ctrl_Entry_units_var_Callback_Text
        self.Ctrl_Scale_Linear_Inputs = self.Ctrl_Scale_Linear_Inputs_Text

        self.mainwindow_text_left.master_configure()
        self.mainwindow_text_right.master_configure()

    # callbacks (wherein this Gui/App is the Controller)

    def Ctrl_Entry_units_var_Callback_Text(self):
        self.mainwindow_text_left.Entry_units_var_Callback()
        self.mainwindow_text_right.Entry_units_var_Callback()

    def Ctrl_Scale_Linear_Inputs_Text(self, factor):
        self.mainwindow_text_left.Scale_Linear_Inputs(factor)
        self.mainwindow_text_right.Scale_Linear_Inputs(factor)

    def Master_Configure_image(self):
        self.PreviewCanvas.grid_forget()
        self.input_frame.grid_forget()
        self.mainwindow_text_left.grid_forget()
        self.mainwindow_text_right.grid_forget()

        self.PreviewCanvas.grid(row=0, rowspan=2, column=1, columnspan=2, sticky=N + E + S + W)
        self.mainwindow_image_left.grid(row=0, rowspan=2, column=0, sticky=W + E + N + S)

        # main window callbacks
        self.Fontdir_Click = None
        self.Ctrl_Entry_units_var_Callback = self.mainwindow_image_left.Entry_units_var_Callback
        self.Ctrl_Scale_Linear_Inputs = self.mainwindow_image_left.Scale_Linear_Inputs

        self.mainwindow_image_left.master_configure()

    def plot_line(self, old, new, midx, midy, cszw, cszh, color, radius=0):
        XX1, YY1 = old
        XX2, YY2 = new
        x1 = cszw / 2 + (XX1 - midx) / self.plot_scale
        x2 = cszw / 2 + (XX2 - midx) / self.plot_scale
        y1 = cszh / 2 - (YY1 - midy) / self.plot_scale
        y2 = cszh / 2 - (YY2 - midy) / self.plot_scale
        if radius == 0:
            thick = 0
        else:
            thick = radius * 2 / self.plot_scale
        self.segID.append(self.PreviewCanvas.create_line(x1, y1, x2, y2, fill=color, capstyle="round", width=thick))

    # TODO simplify circle drawing
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def plot_circle(self, normv, midx, midy, cszw, cszh, color, rad, fill):
        XX, YY = normv
        x1 = cszw / 2 + (XX - rad - midx) / self.plot_scale
        x2 = cszw / 2 + (XX + rad - midx) / self.plot_scale
        y1 = cszh / 2 - (YY - rad - midy) / self.plot_scale
        y2 = cszh / 2 - (YY + rad - midy) / self.plot_scale
        if fill == 0:
            self.segID.append(self.PreviewCanvas.create_oval(x1, y1, x2, y2, outline=color, fill=None, width=1))
        else:
            self.segID.append(self.PreviewCanvas.create_oval(x1, y1, x2, y2, outline=color, fill=color, width=0))

    def recalculate_RQD_Nocalc(self, event):
        self.statusbar.configure(bg='yellow')
        self.input.configure(bg='yellow')
        self.statusMessage.set(" Recalculation required.")

    def Recalculate_RQD_Click(self, event):
        self.statusbar.configure(bg='yellow')
        self.statusMessage.set(" Recalculation required.")
        self.do_it()

    def Recalc_RQD(self):
        self.statusbar.configure(bg='yellow')
        self.statusMessage.set(" Recalculation required.")
        self.do_it()

    def plot_toolpath(self):
        """
        Plot the toolpath for straight tool or V-bit, and the clean path, if generated
        """
        if self.delay_calc:
            return

        self.master.update_idletasks()

        # erase old segments/display objects
        self.PreviewCanvas.delete(ALL)
        self.segID = []

        # origin
        cszw = int(self.PreviewCanvas.cget("width"))
        cszh = int(self.PreviewCanvas.cget("height"))
        buff = 10

        minx, maxx, miny, maxy = self.plot_bbox.tuple()
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        if self.cut_type.get() == CUT_TYPE_VCARVE:
            thickness = 0.0
        else:
            thickness = self.settings.get('line_thickness')

        plot_scale = max((maxx - minx + thickness) / (cszw - buff), (maxy - miny + thickness) / (cszh - buff))
        if plot_scale <= 0:
            plot_scale = 1.0
        self.plot_scale = plot_scale

        if self.settings.get('show_thick'):
            plot_width = thickness / plot_scale
        else:
            plot_width = 1.0

        # show shaded background with the size of the image bounding box,
        # including the circle to be plotted, if any
        # TODO ugly hack to avoid stale text box presented when no image is loaded yet
        if (self.settings.get('input_type') == 'text' and len(self.text) > 0) or \
                (self.settings.get('input_type') == 'image' and len(self.image) > 0):
            x_lft = cszw / 2 + (minx - midx) / plot_scale
            x_rgt = cszw / 2 + (maxx - midx) / plot_scale
            y_bot = cszh / 2 + (maxy - midy) / plot_scale
            y_top = cszh / 2 + (miny - midy) / plot_scale
            if self.settings.get('show_box'):
                self.segID.append(
                    self.PreviewCanvas.create_rectangle(x_lft, y_bot, x_rgt, y_top, fill="gray80",
                                                        outline="gray80",
                                                        width=0))
        # plot circle
        text_radius = self.get_text_radius()

        # TODO
        x_zero = self.engrave.xzero
        y_zero = self.engrave.yzero

        if text_radius != 0:
            Rpx_lft = cszw / 2 + (-text_radius - midx - x_zero) / plot_scale
            Rpx_rgt = cszw / 2 + (text_radius - midx - x_zero) / plot_scale
            Rpy_bot = cszh / 2 + (text_radius + midy + y_zero) / plot_scale
            Rpy_top = cszh / 2 + (-text_radius + midy + y_zero) / plot_scale
            self.segID.append(
                self.PreviewCanvas.create_oval(Rpx_lft, Rpy_bot, Rpx_rgt, Rpy_top, outline="black", width=plot_width))

        # plot the original lines
        scaled_coords = []
        if self.settings.get('input_type') == "text":
            if len(self.text) > 0:
                for XY in self.text.get_coords():
                    # for XY in self.text.coords:
                    x1 = cszw / 2 + (XY[0] - midx) / plot_scale
                    y1 = cszh / 2 - (XY[1] - midy) / plot_scale
                    x2 = cszw / 2 + (XY[2] - midx) / plot_scale
                    y2 = cszh / 2 - (XY[3] - midy) / plot_scale
                    scaled_coords.append((x1, y1, x2, y2))
        else:
            if len(self.image) > 0:
                for XY in self.image.get_coords():
                    x1 = cszw / 2 + (XY[0] - midx) / plot_scale
                    y1 = cszh / 2 - (XY[1] - midy) / plot_scale
                    x2 = cszw / 2 + (XY[2] - midx) / plot_scale
                    y2 = cszh / 2 - (XY[3] - midy) / plot_scale
                    scaled_coords.append((x1, y1, x2, y2))

        for XY in scaled_coords:
            x1, y1, x2, y2 = XY[0], XY[1], XY[2], XY[3]
            self.segID.append(
                self.PreviewCanvas.create_line(x1, y1, x2, y2, fill='black', width=plot_width, capstyle='round'))

        # draw coordinate axis
        axis_length = (maxx - minx) / 4
        x_origin, y_origin = self.get_origin()

        axis_x1 = cszw / 2 + (x_origin - midx) / plot_scale
        axis_x2 = cszw / 2 + (x_origin - midx + axis_length) / plot_scale
        axis_y1 = cszh / 2 - (y_origin - midy) / plot_scale
        axis_y2 = cszh / 2 - (y_origin - midy + axis_length) / plot_scale

        # V-carve Plotting Stuff
        if self.cut_type.get() == CUT_TYPE_VCARVE:
            r_inlay_top = self.calc_r_inlay_top()

            for XY in self.engrave.v_coords:
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                color = "black"

                rbit = self.engrave.calc_vbit_radius()
                if self.settings.get('bit_shape') == "FLAT":
                    if r >= rbit:
                        self.plot_circle((x1, y1), midx, midy, cszw, cszh, color, r, 1)
                else:
                    if self.settings.get('inlay'):
                        self.plot_circle((x1, y1), midx, midy, cszw, cszh, color, r - r_inlay_top, 1)
                    else:
                        self.plot_circle((x1, y1), midx, midy, cszw, cszh, color, r, 1)

            loop_old = -1
            rold = -1
            for line in self.engrave.v_coords:
                new = (line[0], line[1])
                r = XY[2]
                loop = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                plot_flat = False
                if self.settings.get('bit_shape') == "FLAT":
                    if r == rold and r >= rbit:
                        plot_flat = True
                else:
                    plot_flat = True

                if loop == loop_old and plot_flat:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color)
                loop_old = loop
                rold = r
                old = new

        # Plot cleanup path
        if self.cut_type.get() == CUT_TYPE_VCARVE:

            loop_old = -1
            for line in self.engrave.clean_coords_sort:
                new = (line[0], line[1])
                r = XY[2]
                loop = XY[3]
                color = "brown"
                if loop == loop_old:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color, r)
                loop_old = loop
                old = new

            loop_old = -1
            for line in self.engrave.clean_coords_sort:
                new = (line[0], line[1])
                loop = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                if loop == loop_old:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color)
                loop_old = loop
                old = new

            loop_old = -1
            for line in self.engrave.v_clean_coords_sort:
                new = (line[0], line[1])
                loop = XY[3]
                color = "yellow"
                if loop == loop_old:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color)
                loop_old = loop
                old = new

        if self.settings.get('show_axis'):
            # Plot coordinate system origin
            self.segID.append(self.PreviewCanvas.create_line(axis_x1, axis_y1,
                                                             axis_x2, axis_y1,
                                                             fill='red', width=0))
            self.segID.append(self.PreviewCanvas.create_line(axis_x1, axis_y1,
                                                             axis_x1, axis_y2,
                                                             fill='green', width=0))

    def do_it(self):
        """
        Show the original data and plot toolpaths, if any were generated
        """
        if self.delay_calc:
            return

        self.menu_View_Refresh()

        # TODO mainwindow
        # if not self.batch.get():
        #     if self.cut_type.get() == CUT_TYPE_VCARVE:
        #         self.V_Carve_Calc.configure(state="normal", command=None)
        #     else:
        #         self.V_Carve_Calc.configure(state="disabled", command=None)
        #     if self.Check_All_Variables() > 0:
        #         return
        #
        # if not self.batch.get():
        #     self.statusbar.configure(bg='yellow')
        #     self.statusMessage.set(" Calculating.........")
        #     self.master.update_idletasks()
        #     self.PreviewCanvas.delete(ALL)

        if self.settings.get('input_type') == "text":
            self.do_it_text()
        else:
            self.do_it_image()

        if not self.batch.get():
            self.plot_toolpath()

    def do_it_text(self):

        if (self.font is None or len(self.font) == 0) and self.batch.get() is False:
            self.statusbar.configure(bg='red')
            self.statusMessage.set("No Font Characters Loaded")
            return

        self.text.set_font(self.font)
        self.text.set_word_space(self.settings.get('word_space'))
        self.text.set_line_space(self.settings.get('line_space'))
        self.text.set_char_space(self.settings.get('char_space'))

        # the text to be carved or engraved
        if self.batch.get():
            self.text.set_text(self.default_text)
        else:
            self.text.set_text(self.input.get(1.0, END))

        self.text.set_coords_from_strokes()
        self.engrave.set_image(self.text)

        font_line_height = self.font.line_height()
        if font_line_height <= -1e10:

            if not self.batch.get():
                self.statusbar.configure(bg='red')

            if self.settings.get('height_calculation') == "max_all":
                if not self.batch.get():
                    self.statusMessage.set("No Font Characters Found")
                else:
                    fmessage("(No Font Characters Found)")

            elif self.settings.get('height_calculation') == "max_use":
                error_text = "Input Characters Were Not Found in the Current Font"
                if not self.batch.get():
                    self.statusMessage.set(error_text)
                else:
                    fmessage("(" + error_text + ")")

            return

        if self.text.no_font_record == []:
            msg = ""
        else:
            msg = ", CHECK OUTPUT! Some characters not found in font file."

        # Text transformations
        alignment = self.settings.get('justify')
        mirror = self.settings.get('mirror')
        flip = self.settings.get('flip')
        upper = self.settings.get('upper')
        angle = self.settings.get('text_angle')
        radius_in = self.settings.get('text_radius')
        text_radius = self.calc_text_radius()
        x_scale, y_scale = self.get_xy_scale()

        self.text.transform_scale(x_scale, y_scale)
        self.text.align(alignment)
        self.text.transform_on_radius(alignment, text_radius, upper)
        self.text.transform_angle(angle)

        if mirror:
            self.text.transform_mirror()
        if flip:
            self.text.transform_flip()

        self.plot_bbox = self.text.bbox
        minx, maxx, miny, maxy = self.plot_bbox.tuple()

        # engrave box or circle
        if self.settings.get('plotbox'):
            if radius_in == 0:
                delta = self.get_delta()
                self.text.add_box(delta, mirror, flip)
                self.plot_bbox = self.text.bbox
                minx, maxx, miny, maxy = self.plot_bbox.tuple()
            else:
                # Don't create the circle coords here,
                # a G-code circle command is generated later (when not v-carving)
                # For the circle to fit later on, the plot bounding box is adjusted with its radius
                maxr = max(radius_in, self.text.get_max_radius())
                thickness = self.settings.get('line_thickness')
                radius_plot = maxr + thickness / 2
                minx = miny = -radius_plot
                maxx = maxy = -minx
                self.plot_bbox = BoundingBox(minx, maxx, miny, maxy)

        x_zero, y_zero = self.move_origin(self.plot_bbox)
        x_offset = -x_zero
        y_offset = -y_zero
        self.text.transform_translate(x_offset, y_offset)

        self.plot_bbox = BoundingBox(minx + x_offset, maxx + x_offset, miny + y_offset, maxy + y_offset)
        self.text.set_bbox = self.plot_bbox
        minx, maxx, miny, maxy = self.plot_bbox.tuple()

        if not self.batch.get():
            self.input.configure(bg='white')
            # self.statusbar.configure(bg='white')
            self.bounding_box.set("Bounding Box (WxH) = " +
                                  "%.3g" % (maxx - minx) +
                                  " %s " % self.settings.get('units') +
                                  " x " +
                                  "%.3g" % (maxy - miny) +
                                  " %s " % self.settings.get('units') +
                                  " %s" % msg)
            self.statusMessage.set(self.bounding_box.get())

        if self.text.no_font_record != []:
            if not self.batch.get():
                self.statusbar.configure(bg='orange')
            fmessage('Characters not found in font file:', FALSE)
            fmessage("(", FALSE)
            for entry in self.text.no_font_record:
                fmessage("%s," % (entry), FALSE)
            fmessage(")")

    def do_it_image(self):

        if len(self.image) == 0 and self.batch.get() is False:
            self.statusbar.configure(bg='red')
            self.statusMessage.set("No Image Loaded")
            return

        try:
            XScale_in = self.settings.get('xscale')
            YScale_in = self.settings.get('yscale')
            Angle = self.settings.get('text_angle')
        except:
            self.statusMessage.set(" Unable to create pamaths.  Check Settings Entry Values.")
            self.statusbar.configure(bg='red')
            return

        font_line_height = self.font.line_height()
        if font_line_height <= -1e10:

            if not self.batch.get():
                self.statusbar.configure(bg='red')

            if self.H_CALC.get() == "max_all":
                if not self.batch.get():
                    self.statusMessage.set("No Font Characters Found")
                else:
                    fmessage("(No Font Characters Found)")

            elif self.H_CALC.get() == "max_use":
                error_text = "Image contains no design information. (Empty DXF File)"
                if not self.batch.get():
                    self.statusMessage.set(error_text)
                else:
                    fmessage("(" + error_text + ")")

        # TODO image calculation
        # if self.useIMGsize.get():
        YScale = YScale_in / 100
        XScale = XScale_in * YScale / 100

        # reset the image coords (to avoid corruption, e.g. from previous transformations)
        self.image.set_coords_from_strokes()
        self.engrave.set_image(self.image)

        # Image transformations
        self.image.transform_scale(XScale, YScale)
        self.image.transform_angle(Angle)
        if self.settings.get('mirror'):
            self.image.transform_mirror()
        if self.settings.get('flip'):
            self.image.transform_flip()

        x_origin, y_origin = self.get_origin()
        x_zero, y_zero = self.move_origin(self.image.bbox)
        x_offset = x_origin - x_zero
        y_offset = y_origin - y_zero
        self.image.transform_translate(x_offset, y_offset)

        self.plot_bbox = self.image.get_bbox()
        minx, maxx, miny, maxy = self.plot_bbox.tuple()

        if not self.batch.get():
            self.bounding_box.set("Bounding Box (WxH) = " +
                                  "%.3g" % (maxx - minx) +
                                  " %s " % self.settings.get('units') +
                                  " x " +
                                  "%.3g" % (maxy - miny) +
                                  " %s " % self.settings.get('units')
                                  )
            self.statusMessage.set(self.bounding_box.get())

    def get_origin(self):
        return (
            self.settings.get('xorigin'),
            self.settings.get('yorigin')
        )

    # TODO in Job, Gui and Engrave

    def move_origin(self, bbox):

        x_zero = y_zero = 0

        minx, maxx, miny, maxy = bbox.tuple()
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        origin = self.settings.get('origin')
        if origin == 'Default':
            origin = 'Arc-Center'

        vertical, horizontal = origin.split('-')
        if vertical in ('Top', 'Mid', 'Bot') and horizontal in ('Center', 'Right', 'Left'):

            if vertical == 'Top':
                y_zero = maxy
            elif vertical == 'Mid':
                y_zero = midy
            elif vertical == 'Bot':
                y_zero = miny

            if horizontal == 'Center':
                x_zero = midx
            elif horizontal == 'Right':
                x_zero = maxx
            elif horizontal == 'Left':
                x_zero = minx

        else:  # "Default"
            pass

        # TODO use setter method
        self.engrave.xzero = x_zero
        self.engrave.yzero = y_zero

        return (x_zero, y_zero)

    def get_xy_scale(self):

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        x_scale_in = self.settings.get('xscale')
        y_scale_in = self.settings.get('yscale')

        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()
        try:
            y_scale = (y_scale_in - thickness) / (font_line_height - font_line_depth)
        except:
            y_scale = .1

        if y_scale <= Zero:
            y_scale = .1

        y_scale = y_scale_in / 100
        x_scale = x_scale_in * y_scale / 100

        return (x_scale, y_scale)

    def get_text_radius(self):

        text_radius = 0.0

        if self.settings.get('input_type') == "text":
            if self.settings.get('plotbox') and \
                    self.cut_type.get() == CUT_TYPE_ENGRAVE and \
                    self.settings.get('text_radius') != 0:
                text_radius = self.settings.get('text_radius')

        return text_radius

    def get_delta(self):

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        return thickness / 2 + self.settings.get('boxgap')

    # TODO Make this a MyFont method? Note that is being used in SVG and Gcode to generate textcircle

    def calc_text_radius(self):

        x_scale, y_scale = self.get_xy_scale()
        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()

        # text inside or outside of the circle
        radius_in = self.settings.get('text_radius')
        if radius_in == 0.0:
            radius = radius_in
        else:
            delta = self.get_delta()
            if self.settings.get('outer'):
                # text outside circle
                if self.settings.get('upper'):
                    radius = radius_in + delta - y_scale * font_line_depth
                else:
                    radius = -radius_in - delta - y_scale * font_line_height
            else:
                # text inside circle
                if self.settings.get('upper'):
                    radius = radius_in - delta - y_scale * font_line_height
                else:
                    radius = -radius_in + delta - y_scale * font_line_depth

        return radius

    def v_carve_it(self, clean=False):

        self.master.unbind("<Configure>")

        # step length value floor
        v_step_len = self.settings.get('v_step_len')
        if self.settings.get('units') == "mm":
            if v_step_len < .01:
                v_step_len = 0.01
                self.settings.set('v_step_len', v_step_len)
        else:
            if v_step_len < .0005:
                v_step_len = 0.0005
                self.settings.set('v_step_len', v_step_len)

        if self.Check_All_Variables() > 0:
            return

        if not clean:
            self.do_it()
            self.engrave.init_clean_coords()
        elif self.engrave.clean_coords_sort != [] or self.engrave.v_clean_coords_sort != []:
            # If there is existing cleanup data clear the screen before computing
            self.engrave.init_clean_coords()
            self.plot_toolpath()

        if not self.batch.get():
            self.statusbar.configure(bg='yellow')
            self.statusMessage.set('Preparing for V-Carve Calculations')
            self.master.update()

        # V-Carve Stuff
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE and \
                self.settings.get('fontdex') is False:

            if not self.batch.get():
                if self.settings.get('v_pplot') is True:
                    self.plot_toolpath()

            done = self.engrave.v_carve(clean)

            if done and self.batch.get() is False:
                self.statusMessage.set('Done -- ' + self.bounding_box.get())
                self.statusbar.configure(bg='white')

        self.master.bind("<Configure>", self.Master_Configure)

    def ZOOM_ITEMS(self, x0, y0, z_factor):
        all = self.PreviewCanvas.find_all()
        for i in all:
            self.PreviewCanvas.scale(i, x0, y0, z_factor, z_factor)
            w = self.PreviewCanvas.itemcget(i, "width")
            self.PreviewCanvas.itemconfig(i, width=float(w) * z_factor)
        self.PreviewCanvas.update_idletasks()

    def ZOOM(self, z_inc):
        all = self.PreviewCanvas.find_all()
        x = int(self.PreviewCanvas.cget("width")) / 2.0
        y = int(self.PreviewCanvas.cget("height")) / 2.0
        for i in all:
            self.PreviewCanvas.scale(i, x, y, z_inc, z_inc)
            w = self.PreviewCanvas.itemcget(i, "width")
            self.PreviewCanvas.itemconfig(i, width=float(w) * z_inc)
        self.PreviewCanvas.update_idletasks()

    def KEY_ZOOM_IN(self, event):
        self.menu_View_Zoom_in()

    def KEY_ZOOM_OUT(self, event):
        self.menu_View_Zoom_out()

    def menu_View_Zoom_in(self):
        x = int(self.PreviewCanvas.cget("width")) / 2.0
        y = int(self.PreviewCanvas.cget("height")) / 2.0
        self.ZOOM_ITEMS(x, y, 2.0)

    def menu_View_Zoom_out(self):
        x = int(self.PreviewCanvas.cget("width")) / 2.0
        y = int(self.PreviewCanvas.cget("height")) / 2.0
        self.ZOOM_ITEMS(x, y, 0.5)

    def _mouseZoomIn(self, event):
        self.ZOOM_ITEMS(event.x, event.y, 1.25)

    def _mouseZoomOut(self, event):
        self.ZOOM_ITEMS(event.x, event.y, 0.75)

    def mouseZoomStart(self, event):
        self.zoomx0 = event.x
        self.zoomy = event.y
        self.zoomy0 = event.y

    def mouseZoom(self, event):
        dy = event.y - self.zoomy
        if dy < 0.0:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 1.15)
        else:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 0.85)
        self.lasty = self.lasty + dy
        self.zoomy = event.y

    def mousePanStart(self, event):
        self.panx = event.x
        self.pany = event.y

    def mousePan(self, event):
        all = self.PreviewCanvas.find_all()
        dx = event.x - self.panx
        dy = event.y - self.pany
        for i in all:
            self.PreviewCanvas.move(i, dx, dy)
        self.lastx = self.lastx + dx
        self.lasty = self.lasty + dy
        self.panx = event.x
        self.pany = event.y

    def Quit_Click(self, event):
        self.statusMessage.set("Exiting!")
        self.master.destroy()
