import getopt
import webbrowser

from util import VERSION, PIL, POTRACE_AVAILABLE, COLOR_OK, COLOR_RECALC, position_window, message_ask_ok_cancel

from bitmap_settings import BitmapSettings
from vcarve_settings import VCarveSettings
from general_settings import GeneralSettings
from main_window import MenuBar, MainWindowTextLeft, MainWindowTextRight, MainWindowImageLeft

from geometry.font import Font
from geometry.coords import MyImage, MyText
from geometry.engrave import Engrave

from readers import *
from writers import *

from settings import CUT_TYPE_VCARVE, CUT_TYPE_ENGRAVE, INPUT_TYPE_TEXT, INPUT_TYPE_IMAGE

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
else:
    from Tkinter import *
    from tkFileDialog import *
    from pubsub import pub


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
        self.reset_error_count()

        # the main window consists of three rows and three columns
        self.grid()
        self.master.columnconfigure(0, uniform="column")
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, uniform="column")
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(2, minsize=20)

        self.engrave = Engrave(self.settings)

        self.create_widgets()

        pub.subscribe(self.increment_error_count, 'increment_error_count')

        pub.subscribe(self.menu_File_Quit, 'quit')
        pub.subscribe(self.Ctrl_font_file_changed, 'font_file_changed')

        pub.subscribe(self.menu_File_Save_Settings_File, 'save.settings_file')
        pub.subscribe(self.menu_File_Open_G_Code_File, 'open.g_code_file')
        pub.subscribe(self.menu_File_Open_DXF_File, 'open.dxf_file')
        pub.subscribe(self.menu_File_Save_G_Code_File, 'save.g_code_file')
        pub.subscribe(self.menu_File_Save_SVG_File, 'save.svg_file')
        pub.subscribe(self.menu_File_Save_DXF_File, 'save.dxf_file')
        pub.subscribe(self.menu_File_Save_DXF_File_close_loops, 'save.dxf_file_close_loops')

        pub.subscribe(self.CopyClipboard_GCode, 'copy.gcode_to_clipboard')
        pub.subscribe(self.CopyClipboard_SVG, 'copy.svg_to_clipboard')

        pub.subscribe(self.status_color, 'status_color')
        pub.subscribe(self.status_message, 'status_message')
        pub.subscribe(self.status_update_bbox, 'status_message_bbox')

        pub.subscribe(self.general_settings_window, 'general_settings_window')
        pub.subscribe(self.vcarve_settings_window, 'vcarve_settings_window')
        pub.subscribe(self.bitmap_settings_window, 'bitmap_settings_window')
        pub.subscribe(self.Settings_ReLoad_Click, 'reload')
        pub.subscribe(self.write_config_file, 'write_config_file')

        pub.subscribe(self.Recalculation_RQD, 'recalculation_required')
        pub.subscribe(self.Recalculate_Click, 'recalculate')
        pub.subscribe(self.V_Carve_Calc_Click, 'calculate_v_carve')
        pub.subscribe(self.Calculate_CLEAN_Click, 'calculate_cleanup')
        pub.subscribe(self.Ctrl_v_pplot_changed, 'v_pplot_changed')
        pub.subscribe(self.Ctrl_mode_change, 'mode_changed')

        pub.subscribe(self.menu_View_Zoom_in, 'zoom_in')
        pub.subscribe(self.menu_View_Zoom_out, 'zoom_out')
        pub.subscribe(self.menu_View_Refresh, 'refresh')

        pub.subscribe(self.calc_depth_limit, 'calc_depth_limit')

        pub.subscribe(self.Write_Clean_Click, 'write_clean_file')
        pub.subscribe(self.Write_V_Clean_Click, 'write_v_clean_file')

        # engrave progress
        pub.subscribe(self.plot_progress, 'plot_progress')

    @property
    def error_count(self):
        return self._error_count

    def reset_error_count(self):
        self._error_count = 0

    def increment_error_count(self, incr=1):
        self._error_count += incr

    def general_settings_window(self):
        general_settings_window = GeneralSettings(self, self.settings)

    def bitmap_settings_window(self):
        bitmap_settings_window = BitmapSettings(self, self.settings)

    def vcarve_settings_window(self):
        vcarve_settings_window = VCarveSettings(self, self.settings)

    def status_color(self, color=COLOR_RECALC):
        self.statusbar.configure(bg=color)

    def status_message(self, msg):
        self.statusMessage.set(msg)
        self.master.update()

    def status_update_bbox(self, color=COLOR_RECALC):
        self.statusMessage.set(self.bounding_box.get())
        self.statusbar.configure(bg=color)
        self.master.update()

    def plot_progress(self, normv, color, radius):
        self.PreviewCanvas.update_idletasks()
        cszw = int(self.PreviewCanvas.winfo_width())
        cszh = int(self.PreviewCanvas.winfo_height())
        midx, midy = self.engrave.image.get_midxy()
        self.plot_circle(normv, midx, midy, cszw, cszh, color, radius, False)

    def f_engrave_init(self):
        self.master.update()

        if self.settings.get('input_type') == INPUT_TYPE_TEXT:
            self.font = readFontFile(self.settings)
        else:
            self.load_image_file()

        self.initComplete = True
        self.Ctrl_mode_change()
        self.bind_keys()

    def bind_keys(self):
        self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind('<Escape>', self.KEY_ESC)
        self.master.bind('<F1>', self.KEY_F1)
        self.master.bind('<F2>', self.KEY_F2)
        self.master.bind('<F3>', self.KEY_F3)
        self.master.bind('<F4>', self.KEY_F4)
        self.master.bind('<F5>', self.KEY_F5)
        self.master.bind('<Prior>', self.KEY_ZOOM_IN)  # Page Up
        self.master.bind('<Next>', self.KEY_ZOOM_OUT)  # Page Down
        self.master.bind('<Control-q>', self.menu_File_Quit)
        self.master.bind('<Control-o>', self.KEY_CTRL_O)
        self.master.bind('<Control-g>', self.KEY_CTRL_G)
        self.master.bind('<Control-s>', self.KEY_CTRL_S)

    def create_widgets(self):
        self.batch = BooleanVar()

        self.v_pplot = BooleanVar()
        self.current_input_file = StringVar()
        self.bounding_box = StringVar()

        self.initialise_settings()

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

        self.command_line_parameters()

        self.create_previewcanvas()
        self.create_input()
        self.create_statusbar()

        self.menubar = MenuBar(self.master, self.settings)
        self.mainwindow_image_left = None
        self.mainwindow_text_left = None
        self.mainwindow_text_right = None

    ##########################################################################
    #                             COMMAND LINE                               #
    ##########################################################################
    def command_line_parameters(self):
        opts, args = None, None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hbg:f:d:t:",
                                       ["help", "batch", "gcode_file", "fontdir=", "defdir=", "text="])
        except GetoptError:
            fmessage('Unable to interpret the command line options')
            sys.exit()

        for option, value in opts:
            if option in ('-h', '--help'):
                fmessage(' ')
                fmessage('Usage: python oof-engrave.py [-g file | -f fontdir | -d directory | -t text | -b ]')
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
                        self.settings.set('input_type', INPUT_TYPE_TEXT)
                        self.settings.set('fontdir', dirname)
                        self.settings.set('fontfile', os.path.basename(fileName) + fileExtension)
                    else:
                        self.settings.set('input_type', INPUT_TYPE_IMAGE)
                        self.IMAGE_FILE = value
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

            fmessage('(OOF-Engrave Batch Mode)')

            if self.settings.get('input_type') == INPUT_TYPE_TEXT:
                self.font = readFontFile(self.settings)
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

    def create_mainwindow_widgets(self):
        if self.settings.get('input_type') == INPUT_TYPE_TEXT:
            if self.mainwindow_text_left is not None:
                self.mainwindow_text_left.grid_forget()
            if self.mainwindow_text_right is not None:
                self.mainwindow_text_right.grid_forget()
            self.mainwindow_text_left = MainWindowTextLeft(self.master, self.settings)
            self.mainwindow_text_right = MainWindowTextRight(self.master, self.settings)
        else:
            if self.mainwindow_image_left is not None:
                self.mainwindow_image_left.grid_forget()
            self.mainwindow_image_left = MainWindowImageLeft(self.master, self.settings)

    def create_previewcanvas(self):
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
        self.statusbar.grid(row=2, column=0, columnspan=3, sticky=NSEW)

    def initialise_settings(self):
        self.batch.set(self.settings.get('batch'))
        self.v_pplot.set(self.settings.get('v_pplot'))
        self.default_text = self.settings.get('default_text')

        self.HOME_DIR = (self.settings.get('HOME_DIR'))
        self.NGC_FILE = (self.settings.get('NGC_FILE'))
        self.IMAGE_FILE = (self.settings.get('IMAGE_FILE'))

    def write_config_file(self):

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
        except IOError:
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

        self.Check_All_Variables()
        if self.error_count > 0:
            # print("error_count: %s" % self.error_count)
            # clear clipboard, or leave unchanged
            # self.clipboard_append('')
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
        self.Check_All_Variables()
        if self.error_count > 0:
            return

        g_code = gcode(self.engrave)
        for line in g_code:
            try:
                sys.stdout.write(str(line) + '\n')
            except:
                pass
        self.Quit_Click(None)

    def Recalculate_Click(self, event=None):
        self.do_it()

    def Settings_ReLoad_Click(self, event=None, arg1="", arg2=""):
        win_id = self.grab_current()
        self.do_it()
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def Calculate_CLEAN_Click(self):

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
        self.engrave.stop_calculation()

    def v_pplot_Click(self, event):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.Ctrl_v_pplot_changed()

    def Ctrl_v_pplot_changed(self):
        if self.v_pplot.get() != self.settings.get('v_pplot'):
            self.v_pplot.set(self.settings.get('v_pplot'))
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
                bit_depth = 0

            if settings.get('bit_shape') == "FLAT":
                if depth_lim_in < 0.0:
                    depth_limit = depth_lim_in
                else:
                    depth_limit = bit_depth
            else:
                if depth_lim_in < 0.0:
                    depth_limit = max(bit_depth, depth_lim_in)
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

    def Check_All_Variables(self, new=2):
        if self.batch.get():
            return 0  # nothing to be done in batchmode

        self.reset_error_count()
        pub.sendMessage('check_all_variables', new=new)

    def V_Carve_Calc_Click(self):
        self.Check_All_Variables()
        if self.error_count > 0:
            return

        width = 600
        height = 60
        vcalc_status = Toplevel(width=width, height=height)
        # Use grab_set to prevent user input in the main window during calculations
        vcalc_status.grab_set()
        vcalc_status.resizable(0, 0)
        vcalc_status.title('Executing V-Carve')
        vcalc_status.iconname("F-Engrave")

        self.stop_button = Button(vcalc_status, text="Stop Calculation")
        self.stop_button.pack(side=LEFT, padx=10, pady=10)
        self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

        status_frame = Frame(vcalc_status)
        self.statusbar2 = Label(status_frame, textvariable=self.statusMessage, bd=1, relief=FLAT, anchor=W)
        self.statusbar2.pack(side=TOP)
        self.statusMessage.set("Starting Calculation")
        self.statusbar.configure(bg='yellow')

        self.Checkbutton_v_pplot = Checkbutton(status_frame, text="Plot During V-Carve Calculation", anchor=W)
        self.Checkbutton_v_pplot.pack(side=TOP, fill=BOTH)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)
        self.Checkbutton_v_pplot.bind("<ButtonRelease-1>", self.v_pplot_Click)

        status_frame.pack(side=LEFT, padx=10, pady=10)

        try:
            vcalc_status.iconbitmap(bitmap="@emblem64")
        except:
            pass
            try:  # attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                vcalc_status.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        position_window(vcalc_status, width, height)

        self.v_carve_it()
        self.menu_View_Refresh()
        vcalc_status.grab_release()
        try:
            vcalc_status.destroy()
        except:
            pass

    def Clean_Calc_Click(self, bit_type="straight"):

        self.Check_All_Variables()
        if self.error_count > 0:
            return True  # Stop

        if self.engrave.number_of_clean_coords() == 0:

            width = 550
            height = 60
            vcalc_status = Toplevel(width=525, height=50)
            vcalc_status.resizable(0, 0)

            # Use grab_set to prevent user input in the main window during calculations
            vcalc_status.grab_set()
            vcalc_status.title('Executing Clean Area Calculation')
            vcalc_status.iconname("F-Engrave")

            self.stop_button = Button(vcalc_status, text="Stop Calculation")
            self.stop_button.pack(side=LEFT, padx=10, pady=10)
            self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

            self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT)
            self.statusbar2.pack(side=LEFT)
            self.statusMessage.set("Starting Clean Calculation")
            self.statusbar.configure(bg='yellow')

            try:
                vcalc_status.iconbitmap(bitmap="@emblem64")
            except:
                try:  # attempt to create temporary icon bitmap file
                    temp_icon("f_engrave_icon")
                    vcalc_status.iconbitmap("@f_engrave_icon")
                    os.remove("f_engrave_icon")
                except:
                    pass

            position_window(vcalc_status, width, height)

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
        font = read_image_file(self.settings)
        if font is not None and len(font) > 0:
            stroke_list = font[ord("F")].stroke_list
            self.image.set_coords_from_strokes(stroke_list)
        else:
            self.image = MyImage()

        # the input_type may have been changed by read_image_file
        self.Ctrl_set_menu_input_type()
        self.create_mainwindow_widgets()

    def Open_G_Code_File(self, filename):

        self.delay_calc = True
        try:
            fin = open(filename, 'r')
        except IOError:
            fmessage("Unable to open file: %s" % (filename))
            return
        fin.close()

        self.settings.from_configfile(filename)
        self.initialise_settings()

        # TODO is this for backward compatibility?
        # if self.arc_fit.get() == "0":
        #     self.arc_fit.set("none")
        # elif self.arc_fit.get() == "1":
        #     self.arc_fit.set("center")

        if not self.settings.get('arc_fit') in ['none', 'center', 'radius']:
            self.settings.set('arc_fit', 'center')

        text_code = self.settings.get_text_code()
        if text_code != '':
            self.input.delete(1.0, END)
            self.input.insert(END, "%s" % text_code)

        self.calc_depth_limit()
        self.delay_calc = False

        self.Ctrl_set_menu_input_type()
        self.Ctrl_set_menu_cut_type()
        self.Ctrl_mode_change()

    def menu_File_Save_Settings_File(self):

        gcode = self.settings.to_gcode()

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
            filename, file_extension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(filename)
        else:
            filename, file_extension = os.path.splitext(self.NGC_FILE)
            init_file = os.path.basename(filename)

        filename = asksaveasfilename(defaultextension='.txt',
                                     filetypes=[("Settings File", "*.txt"), ("All Files", "*")],
                                     initialdir=init_dir,
                                     initialfile=init_file)

        if filename != '' and filename != ():
            try:
                fout = open(filename, 'w')
            except IOError:
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

        self.Check_All_Variables()
        if self.error_count > 0:
            return

        if self.engrave.number_of_v_coords() == 0 and self.settings.get('cut_type') == CUT_TYPE_VCARVE:
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

        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
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
            except IOError:
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

        self.Check_All_Variables()
        if self.error_count > 0:
            return

        g_code = write_clean_up(self.engrave, bit_type)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
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
            except IOError:
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

        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
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
            except IOError:
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
        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
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
            except IOError:
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

    def menu_File_Quit(self, event=None):
        if message_ask_ok_cancel("Exit", "Exiting OOF-Engrave...."):
            self.Quit_Click(event)

    def menu_View_Refresh(self):
        if self.initComplete and self.batch.get() is False and self.delay_calc is False:
            dummy_event = Event()
            dummy_event.widget = self.master
            self.Master_Configure(dummy_event, True)

    def menu_Help_About(self):
        about = "OOF-Engrave, refactored F-Engrave.\n\n"
        about = about + "http://github.com/Blokkendoos/OOF-Engrave\n"
        about = about + "http://www.scorchworks.com"
        message_box("About OOF-Engrave", about)

    def menu_Help_Web(self):
        webbrowser.open_new(r"http://www.scorchworks.com/Fengrave/fengrave_doc.html")

    def KEY_ESC(self, event):
        self.Stop_Click(event)

    def KEY_F1(self, event):
        self.menu_Help_About()

    def KEY_F2(self, event):
        self.general_settings_window()

    def KEY_F3(self, event):
        self.vcarve_settings_window()

    def KEY_F4(self, event):
        self.bitmap_settings_window()

    def KEY_F5(self, event):
        self.menu_View_Refresh()

    def KEY_CTRL_G(self, event):
        self.CopyClipboard_GCode()

    def KEY_CTRL_O(self, event):
        self.menu_File_Open_DXF_File()

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

        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        if abs(self.w - w) > 10 or abs(self.h - h) > 10 or update is True:
            self.w = w
            self.h = h

            # TODO get rid of window instance test
            if self.settings.get('input_type') == INPUT_TYPE_TEXT:
                self.Master_Configure_text()

            elif self.mainwindow_image_left is not None:
                self.Master_Configure_image()

            else:
                pass

            self.plot_toolpath()

    def Master_Configure_text(self):
        self.PreviewCanvas.grid_forget()
        self.input_frame.grid_forget()
        if self.mainwindow_image_left is not None:
            self.mainwindow_image_left.grid_forget()

        self.PreviewCanvas.grid(row=0, column=1, pady=10, sticky=NSEW)
        self.input_frame.grid(row=1, column=1, pady=10, sticky=NSEW)

        self.mainwindow_text_left.grid(row=0, rowspan=2, column=0, padx=10, pady=10, sticky=NSEW)
        self.mainwindow_text_right.grid(row=0, rowspan=2, column=2, padx=10, pady=10, sticky=NSEW)

        self.mainwindow_text_left.master_configure()
        self.mainwindow_text_right.master_configure()

    # callbacks

    def Ctrl_set_menu_cut_type(self):
        self.menubar.set_cut_type()
        self.Recalculation_RQD()

    def Ctrl_set_menu_input_type(self):
        self.menubar.set_input_type()
        self.Recalculation_RQD()

    def Ctrl_font_file_changed(self):
        self.font = readFontFile(self.settings)
        self.Recalculation_RQD()

    def Ctrl_mode_change(self):

        self.delay_calc = True

        self.create_mainwindow_widgets()

        dummy_event = Event()
        dummy_event.widget = self.master
        self.Master_Configure(dummy_event, True)

        self.delay_calc = False
        self.do_it()

    def Master_Configure_image(self):
        self.PreviewCanvas.grid_forget()
        self.input_frame.grid_forget()
        if self.mainwindow_text_left is not None:
            self.mainwindow_text_left.grid_forget()
            self.mainwindow_text_right.grid_forget()

        self.PreviewCanvas.grid(row=0, rowspan=2, column=1, columnspan=2, padx=10, pady=10, sticky=NSEW)
        self.mainwindow_image_left.grid(row=0, rowspan=2, column=0, pady=10, sticky=NSEW)
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
        self.PreviewCanvas.create_line(x1, y1, x2, y2, fill=color, capstyle="round", width=thick)

    def plot_circle(self, normv, midx, midy, cszw, cszh, color, rad, fill):
        XX, YY = normv
        x1 = cszw / 2 + (XX - rad - midx) / self.plot_scale
        x2 = cszw / 2 + (XX + rad - midx) / self.plot_scale
        y1 = cszh / 2 - (YY - rad - midy) / self.plot_scale
        y2 = cszh / 2 - (YY + rad - midy) / self.plot_scale
        if fill == 0:
            self.PreviewCanvas.create_oval(x1, y1, x2, y2, outline=color, fill=None, width=1)
        else:
            self.PreviewCanvas.create_oval(x1, y1, x2, y2, outline=color, fill=color, width=0)

    def recalculate_RQD_Nocalc(self, event=None):
        self.statusbar.configure(bg='yellow')
        self.input.configure(bg='yellow')
        self.statusMessage.set(" Recalculation required.")

    def Recalculation_RQD(self, event=None):
        self.recalculate_RQD_Nocalc(event)
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

        # origin
        cszw = int(self.PreviewCanvas.winfo_width())
        cszh = int(self.PreviewCanvas.winfo_height())
        buff = 10

        minx, maxx, miny, maxy = self.plot_bbox.tuple()
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
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
            plot_width = 0.0

        # show shaded background with the size of the image bounding box,
        # including the circle to be plotted, if any
        # TODO ugly hack to avoid stale text box presented when no image is loaded yet
        if (self.settings.get('input_type') == INPUT_TYPE_TEXT and len(self.text) > 0) or \
                (self.settings.get('input_type') == INPUT_TYPE_IMAGE and len(self.image) > 0):
            x_lft = cszw / 2 + (minx - midx) / plot_scale
            x_rgt = cszw / 2 + (maxx - midx) / plot_scale
            y_bot = cszh / 2 + (maxy - midy) / plot_scale
            y_top = cszh / 2 + (miny - midy) / plot_scale
            if self.settings.get('show_box'):
                self.PreviewCanvas.create_rectangle(x_lft, y_bot, x_rgt, y_top, fill="gray80",
                                                    outline="gray80",
                                                    width=0)
        # plot circle
        text_radius = self.get_text_radius()
        x_zero, y_zero = self.engrave.get_offset()

        if text_radius != 0:
            Rpx_lft = cszw / 2 + (-text_radius - midx - x_zero) / plot_scale
            Rpx_rgt = cszw / 2 + (text_radius - midx - x_zero) / plot_scale
            Rpy_bot = cszh / 2 + (text_radius + midy + y_zero) / plot_scale
            Rpy_top = cszh / 2 + (-text_radius + midy + y_zero) / plot_scale
            self.PreviewCanvas.create_oval(Rpx_lft, Rpy_bot, Rpx_rgt, Rpy_top, outline="black", width=plot_width)

        # plot the original lines
        scaled_coords = []
        if self.settings.get('input_type') == INPUT_TYPE_TEXT:
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
            self.PreviewCanvas.create_line(x1, y1, x2, y2, fill='black', width=plot_width, capstyle='round')

        # draw coordinate axis
        axis_length = (maxx - minx) / 4
        x_origin, y_origin = self.get_origin()

        axis_x1 = cszw / 2 + (x_origin - midx) / plot_scale
        axis_x2 = cszw / 2 + (x_origin - midx + axis_length) / plot_scale
        axis_y1 = cszh / 2 - (y_origin - midy) / plot_scale
        axis_y2 = cszh / 2 - (y_origin - midy + axis_length) / plot_scale

        # V-carve Plotting Stuff
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:

            r_inlay_top = self.calc_r_inlay_top()
            for XY in self.engrave.v_coords:
                new = (XY[0], XY[1])
                r = XY[2]
                color = "black"

                rbit = self.engrave.calc_vbit_radius()
                if self.settings.get('bit_shape') == "FLAT":
                    if r >= rbit:
                        self.plot_circle(new, midx, midy, cszw, cszh, color, r, 1)
                else:
                    if self.settings.get('inlay'):
                        self.plot_circle(new, midx, midy, cszw, cszh, color, r - r_inlay_top, 1)
                    else:
                        self.plot_circle(new, midx, midy, cszw, cszh, color, r, 1)

            old = (0.0, 0.0)
            loop_old = -1
            rold = -1
            for XY in self.engrave.v_coords:
                new = (XY[0], XY[1])
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
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:

            loop_old = -1
            for XY in self.engrave.clean_coords_sort:
                new = (XY[0], XY[1])
                r = XY[2]
                loop = XY[3]
                color = "brown"
                if loop == loop_old:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color, r)
                loop_old = loop
                old = new

            loop_old = -1
            for XY in self.engrave.clean_coords_sort:
                new = (XY[0], XY[1])
                loop = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                if loop == loop_old:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color)
                loop_old = loop
                old = new

            loop_old = -1
            for XY in self.engrave.v_clean_coords_sort:
                new = (XY[0], XY[1])
                loop = XY[3]
                color = "yellow"
                if loop == loop_old:
                    self.plot_line(old, new, midx, midy, cszw, cszh, color)
                loop_old = loop
                old = new

        if self.settings.get('show_axis'):
            # Plot coordinate system origin
            self.PreviewCanvas.create_line(axis_x1, axis_y1,
                                           axis_x2, axis_y1,
                                           fill='red', width=0)
            self.PreviewCanvas.create_line(axis_x1, axis_y1,
                                           axis_x1, axis_y2,
                                           fill='green', width=0)

    def do_it(self):
        """
        Show the original data and plot toolpaths, if any were generated
        """
        if self.delay_calc:
            return

        self.menu_View_Refresh()

        self.Check_All_Variables()
        if self.error_count > 0:
            return

        if not self.batch.get():
            self.statusbar.configure(bg='yellow')
            self.statusMessage.set(" Calculating.........")
            self.master.update_idletasks()
            self.PreviewCanvas.delete(ALL)

        if self.settings.get('input_type') == INPUT_TYPE_TEXT:
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

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0
        else:
            thickness = self.settings.get('line_thickness')

        self.text.set_font(self.font)
        self.text.set_char_space(self.settings.get('char_space'))
        self.text.set_line_space(self.settings.get('line_space'))
        self.text.set_word_space(self.settings.get('word_space'))
        self.text.set_thickness(thickness)

        # the text to be carved or engraved
        if self.batch.get():
            self.text.set_text(self.default_text)
        else:
            if self.settings.get('fontdex') is True:
                self.text.set_text(self.all_font_characters())
            else:
                self.text.set_text(self.input.get(1.0, END))

        self.text.set_coords_from_strokes()
        self.engrave.set_image(self.text)

        # TEST Python C-API
        # retcoords = v_carve_cpp(self.text.coords, self.settings.get_dict())
        # print "len(retcoords):%d" % len(retcoords)

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
                # thickness = self.settings.get('line_thickness')
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

            self.input.configure(bg=COLOR_OK)
            self.statusbar.configure(bg=COLOR_OK)
            self.Check_All_Variables(new=1)

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

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0
        else:
            thickness = self.settings.get('line_thickness')

        # reset the image coords (to avoid corruption, e.g. from a previous transformation)
        self.image.set_thickness(thickness)
        self.image.set_coords_from_strokes()
        self.engrave.set_image(self.image)

        # Image transformations
        mirror = self.settings.get('mirror')
        flip = self.settings.get('flip')
        angle = self.settings.get('text_angle')

        y_scale_in = self.settings.get('yscale')
        if self.settings.get('useIMGsize'):
            y_scale = y_scale_in / 100
        else:
            if self.image.get_height() > 0:
                y_scale = (y_scale_in - thickness) / (self.image.get_height() - thickness)
            else:
                y_scale = 0.1
        x_scale = self.settings.get('xscale') * y_scale / 100

        self.image.transform_scale(x_scale, y_scale)
        self.image.transform_angle(angle)
        if mirror:
            self.image.transform_mirror()
        if flip:
            self.image.transform_flip()

        x_origin, y_origin = self.get_origin()
        x_zero, y_zero = self.move_origin(self.image.bbox)
        x_offset = x_origin - x_zero
        y_offset = y_origin - y_zero
        self.image.transform_translate(x_offset, y_offset)

        self.plot_bbox = self.image.get_bbox()
        minx, maxx, miny, maxy = self.plot_bbox.tuple()

        # engrave box or circle

        if self.settings.get('plotbox'):
            delta = self.get_delta()
            self.image.add_box(delta, mirror, flip)
            self.plot_bbox = self.image.bbox
            minx, maxx, miny, maxy = self.plot_bbox.tuple()

        if not self.batch.get():
            self.input.configure(bg=COLOR_OK)
            self.statusbar.configure(bg=COLOR_OK)
            self.Check_All_Variables(new=1)

            self.bounding_box.set("Bounding Box (WxH) = " +
                                  "%.3g" % (maxx - minx) +
                                  " %s " % self.settings.get('units') +
                                  " x " +
                                  "%.3g" % (maxy - miny) +
                                  " %s " % self.settings.get('units')
                                  )
            self.statusMessage.set(self.bounding_box.get())

    def all_font_characters(self):

        ext_char = self.settings.get('ext_char')

        string = ""
        for key in self.font:
            try:
                if ext_char:
                    string += unichr(key)
                elif int(key) < 256:
                    string += unichr(key)
            except:
                pass

        string_sort = sorted(string)
        mcnt = 0

        string = ""
        if ext_char:
            pcols = int(1.5 * sqrt(len(self.font)))
        else:
            pcols = 15

        for char in string_sort:
            mcnt = mcnt + 1
            string += char
            if mcnt > pcols:
                string += '\n'
                mcnt = 0

        return string

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

        self.engrave.set_offset(x_zero, y_zero)

        return (x_zero, y_zero)

    def get_xy_scale(self):

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        x_scale_in = self.settings.get('xscale')
        y_scale_in = self.settings.get('yscale')

        # max_all
        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()
        if self.settings.get('height_calculation') == "max_use":
            font_line_height = self.text.get_font_used_height()
            font_line_depth = self.text.get_font_used_depth()

        y_scale = 0.0
        if (font_line_height - font_line_depth) > Zero:
            y_scale = (y_scale_in - thickness) / (font_line_height - font_line_depth)
        if y_scale <= Zero:
            y_scale = .1
        x_scale = x_scale_in * y_scale / 100

        return (x_scale, y_scale)

    def get_text_radius(self):

        text_radius = 0.0

        if self.settings.get('input_type') == INPUT_TYPE_TEXT:
            if self.settings.get('plotbox') and \
                    self.settings.get('cut_type') == CUT_TYPE_ENGRAVE and \
                    self.settings.get('text_radius') != 0:
                text_radius = self.settings.get('text_radius')

        return text_radius

    def get_delta(self):

        thickness = self.settings.get('line_thickness')
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            thickness = 0.0

        return thickness / 2 + self.settings.get('boxgap')

    # TODO Make this a MyFont method? Note that it is also being used in SVG and Gcode to generate textcircle

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
        self.master.resizable(False, False)

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

        self.Check_All_Variables()
        if self.error_count > 0:
            return

        if not clean:
            self.do_it()
            self.engrave.init_clean_coords()
        elif self.engrave.clean_coords_sort != [] or self.engrave.v_clean_coords_sort != []:
            # clear the screen before computing if there is existing cleanup data
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

        # in OS X, if the window position is upper left the window maximizes when resizing is enabled
        self.master.resizable(True, True)
        self.master.bind("<Configure>", self.Master_Configure)

    def ZOOM_ITEMS(self, x0, y0, z_factor):
        all = self.PreviewCanvas.find_all()
        for i in all:
            self.PreviewCanvas.scale(i, x0, y0, z_factor, z_factor)
            pw = float(self.PreviewCanvas.itemcget(i, "width")) * z_factor
            self.PreviewCanvas.itemconfig(i, width=pw)
        self.PreviewCanvas.update_idletasks()

    def ZOOM(self, z_inc):
        all = self.PreviewCanvas.find_all()
        x = int(self.PreviewCanvas.winfo_width()) / 2.0
        y = int(self.PreviewCanvas.winfo_height()) / 2.0
        for i in all:
            self.PreviewCanvas.scale(i, x, y, z_inc, z_inc)
            pw = float(self.PreviewCanvas.itemcget(i, "width")) * z_inc
            self.PreviewCanvas.itemconfig(i, width=pw)
        self.PreviewCanvas.update_idletasks()

    def KEY_ZOOM_IN(self, event):
        self.menu_View_Zoom_in()

    def KEY_ZOOM_OUT(self, event):
        self.menu_View_Zoom_out()

    def menu_View_Zoom_in(self):
        x = int(self.PreviewCanvas.winfo_width()) / 2.0
        y = int(self.PreviewCanvas.winfo_height()) / 2.0
        self.ZOOM_ITEMS(x, y, 2.0)

    def menu_View_Zoom_out(self):
        x = int(self.PreviewCanvas.winfo_width()) / 2.0
        y = int(self.PreviewCanvas.winfo_height()) / 2.0
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


def center_screen(win):
    """
    centers a tkinter window on the main screen
    Source: https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()

    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width

    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2

    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    win.deiconify()
