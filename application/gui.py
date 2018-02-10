import getopt
import webbrowser

# from util import VERSION, POTRACE_AVAILABLE, TTF_AVAILABLE, PIL, IN_AXIS, header_text
from util import *

from tooltip import ToolTip
from bitmap_settings import BitmapSettings
from vcarve_settings import VCarveSettings
from general_settings import GeneralSettings

# from geometry.font import Font
from geometry.coords import MyImage, MyText
from geometry.font import Font
# from geometry.engrave import Engrave, Toolbit, VCarve, Straight
from geometry.engrave import Engrave, Toolbit

import readers
from readers import *
from writers import *

if VERSION == 3:
    from tkinter import *
    # from tkinter.filedialog import *
    # import tkinter.messagebox
else:
    from Tkinter import *
    # from tkFileDialog import *
    # import tkMessageBox


class Gui(Frame):

    def __init__(self, master, settings):
        Frame.__init__(self, master)
        self.w = 780
        self.h = 490
        self.master = master
        self.x = -1
        self.y = -1
        self.initComplete = False
        self.delay_calc = False

        self.settings = settings
        self.engrave = Engrave(self.settings)

        self.font = Font()
        self.text = MyText()
        self.image = MyImage()
        self.tool = Toolbit()

        self.bind_keys()
        self.create_widgets()

        self.engrave.set_progress_callback(self.plot_toolpath)
        self.engrave.set_plot_progress_callback(self.plot_progress)
        self.engrave.set_status_callback(self.status_update)

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

    def plot_progress(self, normv, color, radius, fill=False):
        """Engraver progress callback"""
        cszw = int(self.PreviewCanvas.cget("width"))
        cszh = int(self.PreviewCanvas.cget("height"))

        minx, maxx, miny, maxy = self.engrave.image.get_bbox()
        midx = (maxx + minx) / 2
        midy = (maxy + miny) / 2

        self.plot_circle(normv, midx, midy, cszw, cszh, color, radius, fill)

    def f_engrave_init(self):
        self.master.update()
        self.initComplete = True
        self.menu_mode_change()
        self.STOP_CALC = False

    def bind_keys(self):
        self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind('<Escape>', self.KEY_ESC)
        self.master.bind('<F1>', self.KEY_F1)
        self.master.bind('<F2>', self.KEY_F2)
        self.master.bind('<F3>', self.KEY_F3)
        self.master.bind('<F4>', self.KEY_F4)
        self.master.bind('<F5>', self.KEY_F5)  # self.Recalculate_Click)
        self.master.bind('<Control-Up>', self.Listbox_Key_Up)
        self.master.bind('<Control-Down>', self.Listbox_Key_Down)
        self.master.bind('<Prior>', self.KEY_ZOOM_IN)  # Page Up
        self.master.bind('<Next>', self.KEY_ZOOM_OUT)  # Page Down
        self.master.bind('<Control-g>', self.KEY_CTRL_G)
        self.master.bind('<Control-s>', self.KEY_CTRL_S)

    def create_widgets(self):
        self.batch = BooleanVar()
        self.show_axis = BooleanVar()
        self.show_box = BooleanVar()
        self.show_thick = BooleanVar()
        self.flip = BooleanVar()
        self.mirror = BooleanVar()
        self.outer = BooleanVar()
        self.upper = BooleanVar()
        self.fontdex = BooleanVar()
        self.v_pplot = BooleanVar()
        self.inlay = BooleanVar()
        self.no_comments = BooleanVar()
        self.ext_char = BooleanVar()
        self.var_dis = BooleanVar()
        self.useIMGsize = BooleanVar()
        self.plotbox = BooleanVar()

        self.arc_fit = StringVar()
        self.YSCALE = StringVar()
        self.XSCALE = StringVar()
        self.LSPACE = StringVar()
        self.CSPACE = StringVar()
        self.WSPACE = StringVar()
        self.TANGLE = StringVar()
        self.TRADIUS = StringVar()
        self.ZSAFE = StringVar()
        self.ZCUT = StringVar()
        self.STHICK = StringVar()
        self.origin = StringVar()
        self.justify = StringVar()
        self.units = StringVar()

        self.xorigin = StringVar()
        self.yorigin = StringVar()
        self.segarc = StringVar()
        self.accuracy = StringVar()

        self.funits = StringVar()
        self.FEED = StringVar()
        self.PLUNGE = StringVar()
        self.fontfile = StringVar()
        self.H_CALC = StringVar()
        self.boxgap = StringVar()
        self.fontdir = StringVar()
        self.cut_type = StringVar()
        self.input_type = StringVar()

        self.current_input_file = StringVar()
        self.bounding_box = StringVar()

        self.initialise_settings()

        self.segID = []
        self.font = Font()

        self.RADIUS_PLOT = 0
        self.MAXX = 0
        self.MINX = 0
        self.MAXY = 0
        self.MINY = 0

        self.xzero = float(0.0)
        self.yzero = float(0.0)
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
                        self.input_type.set("text")
                        self.settings.set('fontdir', dirname)
                        self.settings.set('fontfile.', os.path.basename(fileName) + fileExtension)
                    else:
                        self.settings.set('input_type', 'image')
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

        if self.batch.get():
            fmessage('(F-Engrave Batch Mode)')

            if self.settings.get('input_type') == "text":
                self.font = readers.readFontFile(self.settings)
            else:
                readers.read_image_file(self.settings)

            self.do_it()

            if self.settings.get('cut_type') == "v-carve":
                self.v_carve_it()

            g_code = gcode(self.engrave)
            for line in g_code:
                try:
                    sys.stdout.write(line + '\n')
                except:
                    sys.stdout.write('(skipping line)\n')
            sys.exit()

        # make a Status Bar
        self.statusMessage = StringVar()
        self.statusMessage.set("")
        self.statusbar = Label(self.master, textvariable=self.statusMessage, bd=1, relief=SUNKEN, height=1)
        self.statusbar.pack(anchor=SW, fill=X, side=BOTTOM)
        self.statusMessage.set("Welcome to F-Engrave")

        # Buttons
        self.Recalculate = Button(self.master, text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

        # Canvas
        lbframe = Frame(self.master)
        self.PreviewCanvas_frame = lbframe
        self.PreviewCanvas = Canvas(lbframe,
                                    width=self.w - 525,
                                    height=self.h - 200, background="grey")
        self.PreviewCanvas.pack(side=LEFT, fill=BOTH, expand=1)
        self.PreviewCanvas_frame.place(x=230, y=10)

        self.PreviewCanvas.bind("<Button-4>", self._mouseZoomIn)
        self.PreviewCanvas.bind("<Button-5>", self._mouseZoomOut)
        self.PreviewCanvas.bind("<2>", self.mousePanStart)
        self.PreviewCanvas.bind("<B2-Motion>", self.mousePan)
        self.PreviewCanvas.bind("<1>", self.mouseZoomStart)
        self.PreviewCanvas.bind("<B1-Motion>", self.mouseZoom)
        self.PreviewCanvas.bind("<3>", self.mousePanStart)
        self.PreviewCanvas.bind("<B3-Motion>", self.mousePan)

        # Left Column #
        self.Label_font_prop = Label(self.master, text="Text Font Properties:", anchor=W)

        self.Label_Yscale = Label(self.master, text="Text Height", anchor=CENTER)
        self.Label_Yscale_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Label_Yscale_pct = Label(self.master, text="%", anchor=W)
        self.Entry_Yscale = Entry(self.master, width="15")
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)
        self.Label_Yscale_ToolTip = ToolTip(self.Label_Yscale,
                                            text='Character height of a single line of text.')
        # or the height of an imported image. (DXF, BMP, etc.)')

        self.NORmalColor = self.Entry_Yscale.cget('bg')

        self.Label_Sthick = Label(self.master, text="Line Thickness")
        self.Label_Sthick_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self.master, width="15")
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick,
                                            text='Thickness or width of engraved lines. Set this to your engraving cutter diameter.  \
        This setting only affects the displayed lines not the g-code output.')

        self.Label_Xscale = Label(self.master, text="Text Width", anchor=CENTER)
        self.Label_Xscale_u = Label(self.master, text="%", anchor=W)
        self.Entry_Xscale = Entry(self.master, width="15")
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale,
                                            text='Scaling factor for the width of characters.')

        self.Label_useIMGsize = Label(self.master, text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command=self.useIMGsize_var_Callback)

        self.Label_Cspace = Label(self.master, text="Char Spacing", anchor=CENTER)
        self.Label_Cspace_u = Label(self.master, text="%", anchor=W)
        self.Entry_Cspace = Entry(self.master, width="15")
        self.Entry_Cspace.configure(textvariable=self.CSPACE)
        self.Entry_Cspace.bind('<Return>', self.Recalculate_Click)
        self.CSPACE.trace_variable("w", self.Entry_Cspace_Callback)
        self.Label_Cspace_ToolTip = ToolTip(self.Label_Cspace,
                                            text='Character spacing as a percent of character width.')

        self.Label_Wspace = Label(self.master, text="Word Spacing", anchor=CENTER)
        self.Label_Wspace_u = Label(self.master, text="%", anchor=W)
        self.Entry_Wspace = Entry(self.master, width="15")
        self.Entry_Wspace.configure(textvariable=self.WSPACE)
        self.Entry_Wspace.bind('<Return>', self.Recalculate_Click)
        self.WSPACE.trace_variable("w", self.Entry_Wspace_Callback)
        self.Label_Wspace_ToolTip = ToolTip(self.Label_Wspace,
                                            text='Width of the space character. \
                                            This is determined as a percentage of the maximum width of the characters in the currently selected font.')

        self.Label_Lspace = Label(self.master, text="Line Spacing", anchor=CENTER)
        self.Entry_Lspace = Entry(self.master, width="15")
        self.Entry_Lspace.configure(textvariable=self.LSPACE)
        self.Entry_Lspace.bind('<Return>', self.Recalculate_Click)
        self.LSPACE.trace_variable("w", self.Entry_Lspace_Callback)
        self.Label_Lspace_ToolTip = ToolTip(self.Label_Lspace,
                                            text='The vertical spacing between lines of text. This is a multiple of the text height previously input. \
                                            A vertical spacing of 1.0 could result in consecutive lines of text touching each other if the maximum  \
                                            height character is directly below a character that extends the lowest (like a "g").')

        self.Label_pos_orient = Label(self.master, text="Text Position and Orientation:", anchor=W)

        self.Label_Tangle = Label(self.master, text="Text Angle", anchor=CENTER)
        self.Label_Tangle_u = Label(self.master, text="deg", anchor=W)
        self.Entry_Tangle = Entry(self.master, width="15")
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle, text='Rotation of the text or image from horizontal.')

        self.Label_Justify = Label(self.master, text="Justify", anchor=CENTER)
        self.Justify_OptionMenu = OptionMenu(self.master, self.justify, "Left", "Center",
                                             "Right", command=self.Recalculate_RQD_Click)
        self.Label_Justify_ToolTip = ToolTip(self.Label_Justify,
                                             text='Justify determins how to align multiple lines of text. Left side, Right side or Centered.')
        self.justify.trace_variable("w", self.Entry_recalc_var_Callback)

        self.Label_Origin = Label(self.master, text="Origin", anchor=CENTER)
        self.Origin_OptionMenu = OptionMenu(self.master, self.origin, "Top-Left", "Top-Center", "Top-Right", "Mid-Left",
                                            "Mid-Center", "Mid-Right", "Bot-Left", "Bot-Center", "Bot-Right", "Default",
                                            command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin,
                                            text='Origin determins where the X and Y zero position is located relative to the engraving.')

        self.Label_flip = Label(self.master, text="Flip Text")
        self.Checkbutton_flip = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip,
                                          text='Selecting Flip Text/Image mirrors the design about a horizontal line.')

        self.Label_mirror = Label(self.master, text="Mirror Text")
        self.Checkbutton_mirror = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror,
                                            text='Selecting Mirror Text/Image mirrors the design about a vertical line.')

        self.Label_text_on_arc = Label(self.master, text="Text on Circle Properties:", anchor=W)

        self.Label_Tradius = Label(self.master, text="Circle Radius", anchor=CENTER)
        self.Label_Tradius_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Tradius = Entry(self.master, width="15")
        self.Entry_Tradius.configure(textvariable=self.TRADIUS)
        self.Entry_Tradius.bind('<Return>', self.Recalculate_Click)
        self.TRADIUS.trace_variable("w", self.Entry_Tradius_Callback)
        self.Label_Tradius_ToolTip = ToolTip(self.Label_Tradius,
                                             text='Circle radius is the radius of the circle that the text in the input box is placed on. \
                                             If the circle radius is set to 0.0 the text is not placed on a circle.')

        self.Label_outer = Label(self.master, text="Outside circle")
        self.Checkbutton_outer = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=self.outer)
        self.outer.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_outer_ToolTip = ToolTip(self.Label_outer,
                                           text='Select whether the text is placed so that is falls on the inside of \
                                           the circle radius or the outside of the circle radius.')

        self.Label_upper = Label(self.master, text="Top of Circle")
        self.Checkbutton_upper = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=self.upper)
        self.upper.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_upper_ToolTip = ToolTip(self.Label_upper,
                                           text='Select whether the text is placed on the top of the circle of on the bottom of the circle  \
                                           (i.e. concave down or concave up).')

        self.separator1 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(height=2, bd=1, relief=SUNKEN)
        # end Left Column

        # Right Column
        self.Label_gcode_opt = Label(self.master, text="Gcode Properties:", anchor=W)

        self.Label_Feed = Label(self.master, text="Feed Rate")
        self.Label_Feed_u = Label(self.master, textvariable=self.funits, anchor=W)
        self.Entry_Feed = Entry(self.master, width="15")
        self.Entry_Feed.configure(textvariable=self.FEED)
        self.Entry_Feed.bind('<Return>', self.Recalculate_Click)
        self.FEED.trace_variable("w", self.Entry_Feed_Callback)
        self.Label_Feed_ToolTip = ToolTip(self.Label_Feed,
                                          text='Specify the tool feed rate that is output in the g-code output file.')

        self.Label_Plunge = Label(self.master, text="Plunge Rate")
        self.Label_Plunge_u = Label(self.master, textvariable=self.funits, anchor=W)
        self.Entry_Plunge = Entry(self.master, width="15")
        self.Entry_Plunge.configure(textvariable=self.PLUNGE)
        self.Entry_Plunge.bind('<Return>', self.Recalculate_Click)
        self.PLUNGE.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(self.Label_Plunge,
                                            text='Plunge Rate sets the feed rate for vertical moves into the material being cut.\n\n \
                                            When Plunge Rate is set to zero plunge feeds are equal to Feed Rate.')

        self.Label_Zsafe = Label(self.master, text="Z Safe")
        self.Label_Zsafe_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self.master, width="15")
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(self.Label_Zsafe,
                                           text='Z location that the tool will be sent to prior to any rapid moves.')

        self.Label_Zcut = Label(self.master, text="Engrave Depth")
        self.Label_Zcut_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self.master, width="15")
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(self.Label_Zcut,
                                          text='Depth of the engraving cut. This setting has no effect when the v-carve option is selected.')

        self.Checkbutton_fontdex = Checkbutton(self.master, text="Show All Font Characters", anchor=W)
        self.fontdex.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Checkbutton_fontdex.configure(variable=self.fontdex)
        self.Label_fontfile = Label(self.master, textvariable=self.current_input_file, anchor=W, foreground='grey50')
        self.Label_List_Box = Label(self.master, text="Font Files:", foreground="#101010", anchor=W)
        lbframe = Frame(self.master)
        self.Listbox_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Listbox_1 = Listbox(lbframe, selectmode="single", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Listbox_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Listbox_1.pack(side=LEFT, fill=BOTH, expand=1)

        self.Listbox_1.bind("<ButtonRelease-1>", self.Listbox_1_Click)
        self.Listbox_1.bind("<Up>", self.Listbox_Key_Up)
        self.Listbox_1.bind("<Down>", self.Listbox_Key_Down)

        # default font
        try:
            font_files = os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files = " "

        for name in font_files:
            if str.find(name.upper(), '.CXF') != -1 or (str.find(name.upper(), '.TTF') != -1 and TTF_AVAILABLE):
                self.Listbox_1.insert(END, name)

        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")

        self.settings.set('fontfile', self.fontfile.get())
        self.fontdir.trace_variable("w", self.Entry_fontdir_Callback)

        self.V_Carve_Calc = Button(self.master, text="Calc V-Carve", command=self.V_Carve_Calc_Click)

        self.Radio_Cut_E = Radiobutton(self.master, text="Engrave", value="engrave", anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type)
        self.Radio_Cut_V = Radiobutton(self.master, text="V-Carve", value="v-carve", anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type)

        self.cut_type.trace_variable("w", self.Entry_recalc_var_Callback)
        # End Right Column #

        # Text Box
        self.Input_Label = Label(self.master, text="Input Text:", anchor=W)

        lbframe = Frame(self.master)
        self.Input_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Input = Text(lbframe, width="40", height="12", yscrollcommand=scrollbar.set, bg='white')
        self.Input.insert(END, self.default_text)
        scrollbar.config(command=self.Input.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Input.pack(side=LEFT, fill=BOTH, expand=1)
        self.Input.bind("<Key>", self.recalculate_RQD_Nocalc)

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

        top_Settings = Menu(self.menuBar, tearoff=0)
        top_Settings.add("command", label="General Settings", command=self.general_settings_window)
        top_Settings.add("command", label="V-Carve Settings", command=self.vcarve_settings_window)
        if POTRACE_AVAILABLE:
            top_Settings.add("command", label="Bitmap Import Settings", command=self.bitmap_settings_window)

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label="Engrave Mode", variable=self.cut_type, value="engrave")
        top_Settings.add_radiobutton(label="V-Carve Mode", variable=self.cut_type, value="v-carve")

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

    def initialise_settings(self):
        """
        Initialise the TK widgets with the values from settings
        """
        self.batch.set(self.settings.get('batch'))
        self.show_axis.set(self.settings.get('show_axis'))
        self.show_box.set(self.settings.get('show_box'))
        self.show_thick.set(self.settings.get('show_thick'))
        self.flip.set(self.settings.get('flip'))
        self.mirror.set(self.settings.get('mirror'))
        self.outer.set(self.settings.get('outer'))
        self.upper.set(self.settings.get('upper'))
        self.fontdex.set(self.settings.get('fontdex'))
        self.useIMGsize.set(self.settings.get('useIMGsize'))
        self.plotbox.set(self.settings.get('plotbox'))

        self.v_pplot.set(self.settings.get('v_pplot'))
        self.inlay.set(self.settings.get('inlay'))
        self.no_comments.set(self.settings.get('no_comments'))
        self.ext_char.set(self.settings.get('ext_char'))
        self.var_dis.set(self.settings.get('var_dis'))

        self.arc_fit.set(self.settings.get('arc_fit'))
        self.YSCALE.set(self.settings.get('yscale'))
        self.XSCALE.set(self.settings.get('xscale'))
        self.LSPACE.set(self.settings.get('line_space'))
        self.CSPACE.set(self.settings.get('char_space'))
        self.WSPACE.set(self.settings.get('word_space'))
        self.TANGLE.set(self.settings.get('text_angle'))
        self.TRADIUS.set(self.settings.get('text_radius'))
        self.ZSAFE.set(self.settings.get('zsafe'))
        self.ZCUT.set(self.settings.get('zcut'))
        self.STHICK.set(self.settings.get('line_thickness'))
        self.origin.set(self.settings.get('origin'))

        self.justify.set(self.settings.get('justify'))
        self.units.set(self.settings.get('units'))
        self.funits.set(self.settings.get('feed_units'))
        self.FEED.set(self.settings.get('feedrate'))
        self.PLUNGE.set(self.settings.get('plunge_rate'))
        self.fontfile.set(self.settings.get('fontfile'))
        self.H_CALC.set(self.settings.get('height_calculation'))
        self.boxgap.set(self.settings.get('boxgap'))
        self.fontdir.set(self.settings.get('fontdir'))
        self.cut_type.set(self.settings.get('cut_type'))
        self.input_type.set(self.settings.get('input_type'))

        self.xorigin.set(self.settings.get('xorigin'))
        self.yorigin.set(self.settings.get('yorigin'))
        self.segarc.set(self.settings.get('segarc'))
        self.accuracy.set(self.settings.get('accuracy'))

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

        if (setting is not None) and check_flag == OK and new == 0:
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

    def Quit_Click(self, event):
        self.statusMessage.set("Exiting!")
        self.master.destroy()

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

    def Recalculate_Click(self, event):
        self.do_it()

    def Settings_ReLoad_Click(self, event, arg1="", arg2=""):

        win_id = self.grab_current()

        if self.settings.get('input_type') == "text":
            self.font = readers.readFontFile(self.settings)
        else:
            self.font = readers.read_image_file(self.settings)

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

        if (self.settings('clean_P') +
            self.settings('clean_X') +
            self.settings('clean_Y') +
            self.settings('v_clean_P') +
            self.settings('v_clean_Y') +
            self.settings('v_clean_X')) != 0:

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

        if (self.settings('clean_P') +
            self.settings('clean_X') +
            self.settings('clean_Y') +
            self.settings('v_clean_P') +
            self.settings('v_clean_Y') +
            self.settings('v_clean_X')) != 0:

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
        self.STOP_CALC = True
        self.engrave.stop_calc()

    def v_pplot_Click(self, event):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.engrave.refresh_v_pplot()

    def calc_depth_limit(self):
        try:
            bit_shape = self.settings.get('bit_shape')
            v_bit_dia = self.settings.get('v_bit_dia')
            v_bit_angle = self.settings.get('v_bit_angle')

            if bit_shape == "VBIT":
                half_angle = radians(v_bit_angle) / 2.0
                bit_depth = -v_bit_dia / 2.0 / tan(half_angle)
            elif bit_shape == "BALL":
                bit_depth = -v_bit_dia / 2.0
            elif bit_shape == "FLAT":
                bit_depth = -v_bit_dia.get / 2.0
            else:
                pass

            depth_lim = self.settings.get('v_depth_lim')
            if bit_shape != "FLAT":
                if depth_lim < 0.0:
                    self.settings.set('maxcut', max(bit_depth, depth_lim))
                else:
                    self.settings.set('maxcut', bit_depth)
            else:
                if depth_lim < 0.0:
                    self.settings.set('maxcut', depth_lim)
                else:
                    self.settings.set('maxcut', bit_depth)
            # self.maxcut.set("%.3f", self.settings.get('maxcut'))
        except:
            # self.maxcut.set("error")
            pass

    def calc_r_inlay_top(self):
        half_angle = radians(self.settings.get('v_bit_angle') / 2.0)
        inlay_depth = self.settings.get('v_depth_lim')
        r_inlay_top = tan(half_angle) * inlay_depth
        return r_inlay_top

    ###############
    # Left Column #
    ###############
    def Entry_Yscale_Check(self):
        try:
            value = float(self.YSCALE.get())
            if value <= 0.0:
                self.statusMessage.set(" Height should be greater than 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Yscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), setting='yscale')

    def Entry_Xscale_Check(self):
        try:
            value = float(self.XSCALE.get())
            if value <= 0.0:
                self.statusMessage.set(" Width should be greater than 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Xscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), setting='xscale')

    def Entry_Sthick_Check(self):
        try:
            value = float(self.STHICK.get())
            if value < 0.0:
                self.statusMessage.set(" Thickness should be greater than 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Sthick_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), setting='line_thickness')

    def Entry_Lspace_Check(self):
        try:
            value = float(self.LSPACE.get())
            if value < 0.0:
                self.statusMessage.set(" Line space should be greater than or equal to 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Lspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), setting='line_space')

    def Entry_Cspace_Check(self):
        try:
            value = float(self.CSPACE.get())
            if value < 0.0:
                self.statusMessage.set(" Character space should be greater than or equal to 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Cspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), setting='char_space')

    def Entry_Wspace_Check(self):
        try:
            value = float(self.WSPACE.get())
            if value < 0.0:
                self.statusMessage.set(" Word space should be greater than or equal to 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Wspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), setting='word_space')

    def Entry_Tangle_Check(self):
        try:
            value = float(self.TANGLE.get())
            if value <= -360.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between -360 and 360 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Tangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), setting='text_angle')

    def Entry_Tradius_Check(self):
        try:
            value = float(self.TRADIUS.get())
            if value < 0.0:
                self.statusMessage.set(" Radius should be greater than or equal to 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Tradius_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), setting='text_radius')

    ################
    # Right Column #
    ################
    def Entry_Feed_Check(self):
        try:
            value = float(self.FEED.get())
            if value <= 0.0:
                self.statusMessage.set(" Feed should be greater than 0.0 ")
                return INV
        except:
            return NAN
        return NOR

    def Entry_Feed_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), setting='feedrate')

    def Entry_Plunge_Check(self):
        try:
            value = float(self.PLUNGE.get())
            if value < 0.0:
                self.statusMessage.set(" Plunge rate should be greater than or equal to 0.0 ")
                return INV
        except:
            return NAN
        return NOR

    def Entry_Plunge_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), setting='plunge_rate')

    def Entry_Zsafe_Check(self):
        try:
            float(self.ZSAFE.get())
        except:
            return NAN
        return NOR

    def Entry_Zsafe_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), setting='zsafe')

    def Entry_Zcut_Check(self):
        try:
            float(self.ZCUT.get())
        except:
            return NAN
        return NOR

    def Entry_Zcut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), setting='zcut')

    def Fontdir_Click(self, event):
        win_id = self.grab_current()
        newfontdir = askdirectory(mustexist=1, initialdir=self.fontdir.get())
        if newfontdir != "" and newfontdir != ():
            self.fontdir.set(newfontdir.encode("utf-8"))
            self.settings.set('fontdir', self.fontdir.get())
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def Check_All_Variables(self):
        """
        Check all variables set.
        :return: the number of vars in error, 0 if all variables are Ok.
        """
        if self.batch.get():
            return 0  # nothing to be done in batchmode

        MAIN_error_cnt = \
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 2) + \
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 2) + \
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 2) + \
            self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), 2) + \
            self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), 2) + \
            self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), 2) + \
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 2) + \
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), 2) + \
            self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 2) + \
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 2) + \
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 2) + \
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 2)

        # TODO
        GEN_error_cnt = 0

        # GEN_error_cnt= \
        # self.entry_set(self.Entry_Xoffset,  self.Entry_Xoffset_Check() , 2) +\
        # self.entry_set(self.Entry_Yoffset,  self.Entry_Yoffset_Check() , 2) +\
        # self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2) +\
        # self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2) +\
        # self.entry_set(self.Entry_BoxGap,   self.Entry_BoxGap_Check()  , 2) +\
        # self.entry_set(self.Entry_Xoffset,  self.Entry_Xoffset_Check() , 2) +\
        # self.entry_set(self.Entry_Yoffset,  self.Entry_Yoffset_Check() , 2) +\
        # self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2) +\
        # self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2) +\
        # self.entry_set(self.Entry_BoxGap,   self.Entry_BoxGap_Check()  , 2)

        # TODO
        VCARVE_error_cnt = 0

        # VCARVE_error_cnt= \
        # self.entry_set(self.Entry_Vbitangle,    self.Entry_Vbitangle_Check()   , 2) +\
        # self.entry_set(self.Entry_Vbitdia,      self.Entry_Vbitdia_Check()     , 2) +\
        # self.entry_set(self.Entry_InsideAngle,  self.Entry_InsideAngle_Check() , 2) +\
        # self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check(), 2) +\
        # self.entry_set(self.Entry_StepSize,     self.Entry_StepSize_Check()    , 2) +\
        # self.entry_set(self.Entry_CLEAN_DIA,    self.Entry_CLEAN_DIA_Check()   , 2) +\
        # self.entry_set(self.Entry_STEP_OVER,    self.Entry_STEP_OVER_Check()   , 2) +\
        # self.entry_set(self.Entry_Allowance,    self.Entry_Allowance_Check()   , 2) +\
        # self.entry_set(self.Entry_VDepthLimit,  self.Entry_VDepthLimit_Check() , 2)

        # TODO
        BMP_error_cnt = 0

        # BMP_error_cnt= \
        # self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2) +\
        # self.entry_set(self.Entry_BMPturdsize,     self.Entry_BMPturdsize_Check()    , 2) +\
        # self.entry_set(self.Entry_BMPalphamax,     self.Entry_BMPalphamax_Check()    , 2)

        ERROR_cnt = MAIN_error_cnt + GEN_error_cnt + VCARVE_error_cnt + BMP_error_cnt

        if ERROR_cnt > 0:
            self.statusbar.configure(bg='red')
        if BMP_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in BMP Settings Window ")
        if VCARVE_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in V-Carve Settings Window ")
        if GEN_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in General Settings Window ")
        if MAIN_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in Main Window ")

        return ERROR_cnt

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

    def Entry_recalc_var_Callback(self, varName, index, mode):
        # TODO check whether these vars indeed have been set already
        self.settings.set('justify', self.justify.get())
        self.settings.set('flip', self.flip.get())
        self.settings.set('mirror', self.mirror.get())
        self.settings.set('outer', self.outer.get())
        self.settings.set('upper', self.upper.get())
        self.settings.set('cut_type', self.cut_type.get())
        self.Recalc_RQD()

    def Scale_Linear_Inputs(self, factor=1.0):
        try:
            self.YSCALE.set('%.3g' % (self.settings.get('yscale') * factor))
            self.TRADIUS.set('%.3g' % (self.settings.get('text_radius') * factor))
            self.ZSAFE.set('%.3g' % (self.settings.get('zsafe') * factor))
            self.ZCUT.set('%.3g' % (self.settings.get('zcut') * factor))
            self.STHICK.set('%.3g' % (self.settings.get('STHICK') * factor))
            self.FEED.set('%.3g' % (self.settings.get('feedrate') * factor))
            self.PLUNGE.set('%.3g' % (self.settings.get('plunge_rate') * factor))
            self.boxgap.set('%.3g' % (self.settings.get('boxgap') * factor))

            # TODO use settings instead of GUI vars

            # self.v_bit_dia.set(  '%.3g' %(self.settings.get('v_bit_dia')  *factor) )
            # self.v_depth_lim.set('%.3g' %(self.settings.get('v_depth_lim')*factor) )
            # self.v_step_len.set( '%.3g' %(self.settings.get('v_step_len') *factor) )
            # self.allowance.set(  '%.3g' %(self.settings.get('allowance')  *factor) )
            # self.v_max_cut.set(  '%.3g' %(self.settings.get('v_max_cut')  *factor) )
            # self.v_rough_stk.set('%.3g' %(self.settings.get('v_rough_stk')*factor) )
            # self.xorigin.set(    '%.3g' %(self.settings.get('xorigin')    *factor) )

            self.yorigin.set('%.3g' % (self.settings.get('yorigin') * factor))
            self.accuracy.set('%.3g' % (self.settings.get('accuracy') * factor))
            # self.clean_v.set(    '%.3g' %(self.settings.get('clean_v')    *factor) )
            # self.clean_dia.set(  '%.3g' %(self.settings.get('clean_dia')  *factor) )
        except:
            pass

    def Entry_fontdir_Callback(self, varName, index, mode):
        self.Listbox_1.delete(0, END)
        self.Listbox_1.configure(bg=NORmalColor)
        try:
            font_files = os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files = " "

        for name in font_files:
            if (str.find(name.upper(), '.TTF') != -1 and TTF_AVAILABLE) \
                    or str.find(name.upper(), '.CXF') != -1:
                self.Listbox_1.insert(END, name)
        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")

        self.settings.set('fontfile', self.fontfile.get())

        self.font = readers.readFontFile(self.settings)
        self.Recalc_RQD()

    def useIMGsize_var_Callback(self):
        if self.input_type.get() != "text":
            readers.read_image_file()
        try:
            ymx = max(self.font[key].get_ymax() for key in self.font)
            ymn = min(self.font[key].get_ymin() for key in self.font)
            image_height = ymx - ymn
        except:
            if self.units.get() == 'in':
                image_height = 2
            else:
                image_height = 50

        if self.useIMGsize.get():
            self.YSCALE.set('%.3g' % (100 * float(self.YSCALE.get()) / image_height))
        else:
            self.YSCALE.set('%.3g' % (float(self.YSCALE.get()) / 100 * image_height))

        self.menu_View_Refresh()
        self.Recalc_RQD()

    def Listbox_1_Click(self, event):
        labelL = []
        for i in self.Listbox_1.curselection():
            labelL.append(self.Listbox_1.get(i))
        try:
            self.fontfile.set(labelL[0])
        except:
            return

        self.settings.set('fontfile', self.fontfile.get())

        self.font = readers.readFontFile(self.settings)
        self.do_it()

    def Listbox_Key_Up(self, event):
        try:
            select_new = int(self.Listbox_1.curselection()[0]) - 1
        except:
            select_new = self.Listbox_1.size() - 2
        self.Listbox_1.selection_clear(0, END)
        self.Listbox_1.select_set(select_new)
        try:
            self.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return

        self.settings.set('fontfile', self.fontfile.get())

        self.font = readers.readFontFile(self.settings)
        self.do_it()

    def Listbox_Key_Down(self, event):
        try:
            select_new = int(self.Listbox_1.curselection()[0]) + 1
        except:
            select_new = 1
        self.Listbox_1.selection_clear(0, END)
        self.Listbox_1.select_set(select_new)
        try:
            self.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return

        self.settings.set('fontfile', self.fontfile.get())

        self.font = readers.readFontFile(self.settings)
        self.do_it()

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

            # TODO future read_image_file will return a MyImage instead of a Font instance
            self.font = readers.read_image_file(self.settings)
            stroke_list = self.font[ord("F")].stroke_list
            self.image.set_coords_from_strokes(stroke_list)

            self.input_type.set(self.settings.get('input_type'))  # input_type may have been changed by read_image_file
            self.do_it()

    def Open_G_Code_File(self, filename):

        self.delay_calc = True
        boxsize = "0"
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

        if boxsize != "0":
            self.boxgap.set(float(boxsize) * self.settings.get('line_thickness'))

        # TODO is this for backward compatibility?
        # if self.arc_fit.get() == "0":
        #     self.arc_fit.set("none")
        # elif self.arc_fit.get() == "1":
        #     self.arc_fit.set("center")

        # TODO update settings instead of tkinter var
        if not self.settings.get('arc_fit') in ['none', 'center', 'radius']:
            self.settings.set('arc_fit', 'center')
            # self.arc_fit.set("center")

        if text_codes != []:
            try:
                self.Input.delete(1.0, END)
                for Ch in text_codes:
                    try:
                        self.Input.insert(END, "%c" % (unichr(int(Ch))))
                    except:
                        self.Input.insert(END, "%c" % (chr(int(Ch))))
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
        if self.input_type.get() == "image":
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

        if self.engrave.number_of_v_coords() == 0 and self.cut_type.get() == "v-carve":
            mess = "V-carve path data does not exist.  "
            mess = mess + "Only settings will be saved.\n\n"
            mess = mess + "To generate V-Carve path data Click on the"
            mess = mess + "\"Calculate V-Carve\" button on the main window."
            if not message_ask_ok_cancel("Continue", mess):
                return

        g_code = gcode(self.engrave)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.input_type.get() == "image":
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

        if self.input_type.get() == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
            fileName_tmp, fileExtension = os.path.splitext(init_file)
            init_file = fileName_tmp
        else:
            init_file = "text"

        if bit_type == "v-bit":
            init_file = init_file + "_v" + self.clean_name.get()
        else:
            init_file = init_file + self.clean_name.get()

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

        svg_code = svg(self.engrave)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.input_type.get() == "image":
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
        if self.input_type.get() != "text":
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
        if self.initComplete and (not self.batch.get()) and (not self.delay_calc):
            dummy_event = Event()
            dummy_event.widget = self.master
            self.Master_Configure(dummy_event, 1)

    def menu_mode_change_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_mode_change(self):
        self.delay_calc = True
        dummy_event = Event()
        dummy_event.widget = self.master
        self.Master_Configure(dummy_event, 1)
        self.delay_calc = False
        if self.input_type.get() == "text":
            self.font = readers.readFontFile(self.settings)
        else:
            self.font = readers.read_image_file(self.settings)

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

    def KEY_ZOOM_IN(self, event):
        self.menu_View_Zoom_in()

    def KEY_ZOOM_OUT(self, event):
        self.menu_View_Zoom_out()

    def KEY_CTRL_G(self, event):
        self.CopyClipboard_GCode()

    def KEY_CTRL_S(self, event):
        self.menu_File_Save_G_Code_File()

    def Master_Configure(self, event, update=0):
        """
        The widget changed size (or location, on some platforms).
        The new size is provided in the width and height attributes of the event object passed to the callback.
        """
        if event.widget != self.master:
            return

        if self.batch.get():
            return

        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())

        if (self.x, self.y) == (-1, -1):
            self.x, self.y = x, y

        if abs(self.w - w) > 10 or abs(self.h - h) > 10 or update == 1:

            self.w = w
            self.h = h

            if self.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)

            if self.input_type.get() == "text":
                self.master_configure_text()
            else:
                self.master_configure_image()

            self.plot_toolpath()

    def master_configure_text(self):

        self.Label_font_prop.configure(text="Text Font Properties:")
        self.Label_Yscale.configure(text="Text Height")
        self.Label_Xscale.configure(text="Text Width")
        self.Label_pos_orient.configure(text="Text Position and Orientation:")
        self.Label_Tangle.configure(text="Text Angle")
        self.Label_flip.configure(text="Flip Text")
        self.Label_mirror.configure(text="Mirror Text")

        self.Label_useIMGsize.place_forget()
        self.Checkbutton_useIMGsize.place_forget()

        # Begin Left Column
        w_label = 90
        w_entry = 60
        w_units = 35

        x_label_L = 10
        x_entry_L = x_label_L + w_label + 10
        x_units_L = x_entry_L + w_entry + 5

        Yloc = 6
        self.Label_font_prop.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)
        Yloc = Yloc + 24
        self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Yscale_pct.place_forget()
        self.Label_Yscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Yscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_Sthick.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Sthick_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Sthick.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        if self.cut_type.get() == "engrave":
            self.Entry_Sthick.configure(state="normal")
            self.Label_Sthick.configure(state="normal")
            self.Label_Sthick_u.configure(state="normal")
        else:
            self.Entry_Sthick.configure(state="disabled")
            self.Label_Sthick.configure(state="disabled")
            self.Label_Sthick_u.configure(state="disabled")

        Yloc = Yloc + 24
        self.Label_Xscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Xscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Xscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_Cspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Cspace_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Cspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_Wspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Wspace_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Wspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_Lspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Entry_Lspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24 + 12
        self.separator1.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)
        Yloc = Yloc + 6
        self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_Justify.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Justify_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24 + 12
        self.separator2.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)
        Yloc = Yloc + 6
        self.Label_text_on_arc.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Label_Tradius.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Tradius_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Tradius.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_outer.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_outer.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_upper.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_upper.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24 + 12
        self.separator3.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)

        # Begin Right Column
        w_label = 90
        w_entry = 60
        w_units = 35

        x_label_R = self.w - 220
        x_entry_R = x_label_R + w_label + 10
        x_units_R = x_entry_R + w_entry + 5

        Yloc = 6
        self.Label_gcode_opt.place(x=x_label_R, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Entry_Feed.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)
        self.Label_Feed.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Feed_u.place(x=x_units_R, y=Yloc, width=w_units + 15, height=21)

        Yloc = Yloc + 24
        self.Entry_Plunge.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)
        self.Label_Plunge.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Plunge_u.place(x=x_units_R, y=Yloc, width=w_units + 15, height=21)

        Yloc = Yloc + 24
        self.Entry_Zsafe.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)
        self.Label_Zsafe.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Zsafe_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)

        Yloc = Yloc + 24
        self.Label_Zcut.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Zcut_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)
        self.Entry_Zcut.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)

        if self.cut_type.get() == "engrave":
            self.Entry_Zcut.configure(state="normal")
            self.Label_Zcut.configure(state="normal")
            self.Label_Zcut_u.configure(state="normal")
        else:
            self.Entry_Zcut.configure(state="disabled")
            self.Label_Zcut.configure(state="disabled")
            self.Label_Zcut_u.configure(state="disabled")

        Yloc = Yloc + 24 + 6
        self.Label_List_Box.place(x=x_label_R + 0, y=Yloc, width=113, height=22)

        Yloc = Yloc + 24
        self.Listbox_1_frame.place(x=x_label_R + 0, y=Yloc, width=160 + 25, height=self.h - 324)
        self.Label_fontfile.place(x=x_label_R, y=self.h - 165, width=w_label + 75, height=21)
        self.Checkbutton_fontdex.place(x=x_label_R, y=self.h - 145, width=185, height=23)

        # Buttons etc.
        Ybut = self.h - 60
        self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

        Ybut = self.h - 60
        self.V_Carve_Calc.place(x=x_label_R, y=Ybut, width=100, height=30)

        Ybut = self.h - 105
        self.Radio_Cut_E.place(x=x_label_R, y=Ybut, width=185, height=23)
        Ybut = self.h - 85
        self.Radio_Cut_V.place(x=x_label_R, y=Ybut, width=185, height=23)

        self.PreviewCanvas.configure(width=self.w - 455, height=self.h - 160)
        self.PreviewCanvas_frame.place(x=220, y=10)
        self.Input_Label.place(x=222, y=self.h - 130, width=112, height=21, anchor=W)
        self.Input_frame.place(x=222, y=self.h - 110, width=self.w - 455, height=75)

    def master_configure_image(self):

        self.Label_font_prop.configure(text="Image Properties:")
        self.Label_Yscale.configure(text="Image Height")
        self.Label_Xscale.configure(text="Image Width")
        self.Label_pos_orient.configure(text="Image Position and Orientation:")
        self.Label_Tangle.configure(text="Image Angle")
        self.Label_flip.configure(text="Flip Image")
        self.Label_mirror.configure(text="Mirror Image")

        # Left Column
        w_label = 90
        w_entry = 60
        w_units = 35

        x_label_L = 10
        x_entry_L = x_label_L + w_label + 10
        x_units_L = x_entry_L + w_entry + 5

        Yloc = 6
        self.Label_font_prop.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)
        Yloc = Yloc + 24
        self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        if self.useIMGsize.get():
            self.Label_Yscale_u.place_forget()
            self.Label_Yscale_pct.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        else:
            self.Label_Yscale_pct.place_forget()
            self.Label_Yscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)

        self.Entry_Yscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_useIMGsize.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_useIMGsize.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_Sthick.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Sthick_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Sthick.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)
        if self.cut_type.get() == "engrave":
            self.Entry_Sthick.configure(state="normal")
            self.Label_Sthick.configure(state="normal")
            self.Label_Sthick_u.configure(state="normal")
        else:
            self.Entry_Sthick.configure(state="disabled")
            self.Label_Sthick.configure(state="disabled")
            self.Label_Sthick_u.configure(state="disabled")

        Yloc = Yloc + 24
        self.Label_Xscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Xscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Xscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        self.Label_Cspace.place_forget()
        self.Label_Cspace_u.place_forget()
        self.Entry_Cspace.place_forget()

        self.Label_Wspace.place_forget()
        self.Label_Wspace_u.place_forget()
        self.Entry_Wspace.place_forget()

        self.Label_Lspace.place_forget()
        self.Entry_Lspace.place_forget()

        Yloc = Yloc + 24 + 12
        self.separator1.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)
        Yloc = Yloc + 6
        self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        self.Label_Justify.place_forget()
        self.Justify_OptionMenu.place_forget()

        Yloc = Yloc + 24
        self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        self.Label_text_on_arc.place_forget()
        self.Label_Tradius.place_forget()
        self.Label_Tradius_u.place_forget()
        self.Entry_Tradius.place_forget()
        self.Label_outer.place_forget()
        self.Checkbutton_outer.place_forget()
        self.Label_upper.place_forget()
        self.Checkbutton_upper.place_forget()

        # Right Column
        x_label_R = x_label_L
        x_entry_R = x_entry_L
        x_units_R = x_units_L

        Yloc = Yloc + 24 + 12
        self.separator2.place(x=x_label_R, y=Yloc, width=w_label + 75 + 40, height=2)

        Yloc = Yloc + 6
        self.Label_gcode_opt.place(x=x_label_R, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Entry_Feed.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)
        self.Label_Feed.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Feed_u.place(x=x_units_R, y=Yloc, width=w_units + 15, height=21)

        Yloc = Yloc + 24
        self.Entry_Plunge.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)
        self.Label_Plunge.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Plunge_u.place(x=x_units_R, y=Yloc, width=w_units + 15, height=21)

        Yloc = Yloc + 24
        self.Entry_Zsafe.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)
        self.Label_Zsafe.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Zsafe_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)

        Yloc = Yloc + 24
        self.Label_Zcut.place(x=x_label_R, y=Yloc, width=w_label, height=21)
        self.Label_Zcut_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)
        self.Entry_Zcut.place(x=x_entry_R, y=Yloc, width=w_entry, height=23)

        if self.cut_type.get() == "engrave":
            self.Entry_Zcut.configure(state="normal")
            self.Label_Zcut.configure(state="normal")
            self.Label_Zcut_u.configure(state="normal")
        else:
            self.Entry_Zcut.configure(state="disabled")
            self.Label_Zcut.configure(state="disabled")
            self.Label_Zcut_u.configure(state="disabled")

        self.Label_List_Box.place_forget()
        self.Listbox_1_frame.place_forget()
        self.Checkbutton_fontdex.place_forget()

        Yloc = Yloc + 24 + 12
        self.separator3.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)
        Yloc = Yloc + 6
        self.Label_fontfile.place(x=x_label_R, y=Yloc, width=w_label + 75, height=21)

        # Buttons etc.
        offset_R = 100
        Ybut = self.h - 60
        self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

        Ybut = self.h - 60
        self.V_Carve_Calc.place(x=x_label_R + offset_R, y=Ybut, width=100, height=30)

        Ybut = self.h - 105
        self.Radio_Cut_E.place(x=x_label_R + offset_R, y=Ybut, width=w_label, height=23)
        Ybut = self.h - 85
        self.Radio_Cut_V.place(x=x_label_R + offset_R, y=Ybut, width=w_label, height=23)

        self.PreviewCanvas.configure(width=self.w - 240, height=self.h - 45)
        self.PreviewCanvas_frame.place(x=230, y=10)
        self.Input_Label.place_forget()
        self.Input_frame.place_forget()

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
        self.Input.configure(bg='yellow')
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
        Plot the toolpath for straight tool or V-bit, and the clean path
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

        if self.input_type.get() == "text":
            minx, maxx, miny, maxy = self.text.get_bbox()
        else:
            minx, maxx, miny, maxy = self.image.get_bbox()
        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        if self.cut_type.get() == "v-carve":
            Thick = 0.0
        else:
            Thick = float(self.STHICK.get())

        if self.input_type.get() == "text":
            Radius_in = float(self.TRADIUS.get())
        else:
            Radius_in = 0.0

        plot_scale = max((maxx - minx + Thick) / (cszw - buff), (maxy - miny + Thick) / (cszh - buff))
        if plot_scale <= 0:
            plot_scale = 1.0
        self.plot_scale = plot_scale

        Radius_plot = 0
        if self.plotbox.get() and self.cut_type.get() == "engrave":
            if Radius_in != 0:
                Radius_plot = float(self.RADIUS_PLOT)

        x_lft = cszw / 2 + (minx - midx) / plot_scale
        x_rgt = cszw / 2 + (maxx - midx) / plot_scale
        y_bot = cszh / 2 + (maxy - midy) / plot_scale
        y_top = cszh / 2 + (miny - midy) / plot_scale
        # show shaded background with the size of the image bounding box
        if self.show_box.get():
            self.segID.append(
                self.PreviewCanvas.create_rectangle(x_lft, y_bot, x_rgt, y_top, fill="gray80",
                                                    outline="gray80",
                                                    width=0))

        if Radius_in != 0:
            Rx_lft = cszw / 2 + (-Radius_in - midx) / plot_scale
            Rx_rgt = cszw / 2 + (Radius_in - midx) / plot_scale
            Ry_bot = cszh / 2 + (Radius_in + midy) / plot_scale
            Ry_top = cszh / 2 + (-Radius_in + midy) / plot_scale
            self.segID.append(
                self.PreviewCanvas.create_oval(Rx_lft, Ry_bot, Rx_rgt, Ry_top, outline="gray90", width=0, dash=3))

        if self.show_thick.get():
            plot_width = Thick / plot_scale
        else:
            plot_width = 1.0

        # Plot circle
        x_zero = self.xzero
        y_zero = self.yzero

        if self.settings.get('outer'):
            Radius_plot -= 2 * self.settings.get('boxgap')
            Radius_plot -= self.settings.get('yscale')

        if Radius_plot != 0:
            Rpx_lft = cszw / 2 + (-Radius_plot - midx - x_zero) / plot_scale
            Rpx_rgt = cszw / 2 + (Radius_plot - midx - x_zero) / plot_scale
            Rpy_bot = cszh / 2 + (Radius_plot + midy + y_zero) / plot_scale
            Rpy_top = cszh / 2 + (-Radius_plot + midy + y_zero) / plot_scale
            self.segID.append(
                self.PreviewCanvas.create_oval(Rpx_lft, Rpy_bot, Rpx_rgt, Rpy_top, outline="black", width=plot_width))

        # Plot the original lines
        scaled_coords = []
        if self.input_type.get() == "text":
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
        XOrigin = float(self.xorigin.get())
        YOrigin = float(self.yorigin.get())

        axis_length = (maxx - minx) / 4
        axis_x1 = cszw / 2 + (-midx + XOrigin) / plot_scale
        axis_x2 = cszw / 2 + (axis_length - midx + XOrigin) / plot_scale
        axis_y1 = cszh / 2 - (-midy + YOrigin) / plot_scale
        axis_y2 = cszh / 2 - (axis_length - midy + YOrigin) / plot_scale

        # V-carve Plotting Stuff
        if self.cut_type.get() == "v-carve":
            r_inlay_top = self.calc_r_inlay_top()

            for XY in self.engrave.vcoords:
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                color = "black"

                rbit = self.engrave.calc_vbit_radius()
                if self.settings.get('bit_shape') == "FLAT":
                    if r >= rbit:
                        self.plot_circle((x1, y1), midx, midy, cszw, cszh, color, r, 1)
                else:
                    if self.inlay.get():
                        self.plot_circle((x1, y1), midx, midy, cszw, cszh, color, r - r_inlay_top, 1)
                    else:
                        self.plot_circle((x1, y1), midx, midy, cszw, cszh, color, r, 1)

            loop_old = -1
            rold = -1
            for line in self.engrave.vcoords:
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
        if self.cut_type.get() == "v-carve":
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

        if self.show_axis.get():
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

        if not self.batch.get:
            if self.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)
            if self.Check_All_Variables() > 0:
                return

        if not self.batch.get():
            self.statusbar.configure(bg='yellow')
            self.statusMessage.set(" Calculating.........")
            self.master.update_idletasks()
            self.PreviewCanvas.delete(ALL)

        self.segID = []

        if self.input_type.get() == "text":
            self.engrave.set_image(self.text)
            self.do_it_text()

        elif self.input_type.get() == "image":
            self.engrave.set_image(self.image)
            self.do_it_image()

        else:
            pass  # TODO cannot occur

        if not self.batch.get():
            self.plot_toolpath()

    def do_it_text(self):

        if (self.font is None or len(self.font) == 0) and (not self.batch.get()):
            self.statusbar.configure(bg='red')
            self.statusMessage.set("No Font Characters Loaded")
            return

        # # TODO Check completeness necessary? All vars should have a valid entry?
        # try:
        #     SegArc = float(self.segarc.get())
        #     XScale_in = float(self.XSCALE.get())
        #     YScale_in = float(self.YSCALE.get())
        #     CSpaceP = float(self.CSPACE.get())
        #     WSpaceP = float(self.WSPACE.get())
        #     LSpace = float(self.LSPACE.get())
        #     Angle = float(self.TANGLE.get())
        #     Thick = float(self.STHICK.get())
        #     XOrigin = float(self.xorigin.get())
        #     YOrigin = float(self.yorigin.get())
        # except:
        #     self.statusMessage.set(" Unable to create paths.  Check Settings Entry Values.")
        #     self.statusbar.configure(bg='red')
        #     return

        try:
            Angle = self.settings.get('text_angle')
            XOrigin = self.settings.get('xorigin')
            YOrigin = self.settings.get('yorigin')
            Thick = self.settings.get('line_thickness')
            # Thick_Border = self.settings.get('border_thickness')
        except:
            self.statusMessage.set(" Unable to create paths.  Check Settings Entry Values.")
            self.statusbar.configure(bg='red')
            return

        self.text.set_font(self.font)
        self.text.set_radius(self.settings.get('text_radius'))
        self.text.set_word_space(self.settings.get('word_space'))
        self.text.set_line_space(self.settings.get('line_space'))
        self.text.set_char_space(self.settings.get('char_space'))

        if self.batch.get():
            self.text.set_text(self.default_text)
        else:
            self.text.set_text(self.Input.get(1.0, END))

        self.text.set_coords_from_strokes()

        # TODO use font properties (settings to be set in font selection)

        font_line_height = self.font.line_height()
        font_line_depth = self.font.line_depth()
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

        if self.cut_type.get() == "v-carve":
            Thick = 0.0
            # self.text.set_thickness(0.0)

        # X/Y Scale
        XScale_in = self.settings.get('xscale')
        YScale_in = self.settings.get('yscale')
        try:
            YScale = (YScale_in - Thick) / (font_line_height - font_line_depth)
        except:
            YScale = .1
        if YScale <= Zero:
            YScale = .1
        XScale = XScale_in * YScale / 100

        # text outside or inside circle
        Radius_in = self.settings.get('text_radius')
        if Radius_in != 0.0:
            if self.settings.get('outer'):
                if self.settings.get('upper'):
                    Radius = Radius_in + Thick / 2 + YScale * (-font_line_depth)
                else:
                    Radius = -Radius_in - Thick / 2 - YScale * (font_line_height)
            else:
                if self.settings.get('upper'):
                    Radius = Radius_in - Thick / 2 - YScale * (font_line_height)
                else:
                    Radius = -Radius_in + Thick / 2 + YScale * (-font_line_depth)
        else:
            Radius = Radius_in

        # there were characters missing in the Font set
        if self.text.no_font_record == []:
            msg = ""
        else:
            msg = ", CHECK OUTPUT! Some characters not found in font file."

        # Text transformations
        alignment = self.settings.get('justify')
        mirror = self.settings.get('mirror')
        flip = self.settings.get('flip')
        upper = self.settings.get('upper')

        self.text.transform_scale(XScale, YScale)
        self.text.align(alignment)
        self.text.transform_on_radius(alignment, Radius, upper)
        maxr2 = self.text.transform_angle(Angle)
        if mirror:
            self.text.transform_mirror()
        if flip:
            self.text.transform_flip()

        # minx, maxx, miny, maxy = self.text.get_bbox()

        if self.settings.get('plotbox'):
            delta = Thick / 2 + self.settings.get('boxgap')
            if Radius_in == 0 or self.settings.get('cut_type') == "v-carve":
                self.text.add_box(delta, mirror, flip)
            else:
                Radius_plot = sqrt(maxr2) + Thick + float(self.boxgap.get())
                minx = -Radius_plot - Thick / 2
                maxx = -minx
                miny = minx
                maxy = maxx
                midx = 0
                midy = 0
                self.RADIUS_PLOT = Radius_plot
                # Don't create the circle coords here, a G-code circle command
                # is generated later when not v-carving
                # self.text.add_circle()

            # TODO adjust bounding box?
            # if self.cut_type.get() != "v-carve":
            #     delta = delta + Thick / 2
            # minx = minx - delta
            # maxx = maxx + delta
            # miny = miny - delta
            # maxy = maxy + delta

        ##########################################
        #         ORIGIN LOCATING STUFF          #
        ##########################################
        # TODO single out method (maxx, maxy, ... object properties, e.g. the Boundingbox or similar class)
        origin = self.settings.get('origin')
        if origin == 'Default':
            origin = 'Arc-Center'

        x_zero = y_zero = 0
        vertical, horizontal = origin.split('-')
        if vertical in ('Top', 'Mid', 'Bot') and horizontal in ('Center', 'Right', 'Left'):
            if vertical is 'Top':
                y_zero = maxy
            elif vertical is 'Mid':
                y_zero = midy
            elif vertical is 'Bot':
                y_zero = miny

            if horizontal is 'Center':
                x_zero = midx
            elif horizontal is 'Right':
                x_zero = maxx
            elif horizontal is 'Left':
                x_zero = minx
        else:  # "Default"
            pass

        for i, XY in enumerate(self.text.coords):
            self.text.coords[i][0] = XY[0] - x_zero + XOrigin
            self.text.coords[i][1] = XY[1] - y_zero + YOrigin
            self.text.coords[i][2] = XY[2] - x_zero + XOrigin
            self.text.coords[i][3] = XY[3] - y_zero + YOrigin

        minx, maxx, miny, maxy = self.text.get_bbox()
        if not self.batch.get():
            # Reset Status Bar and Entry Fields
            self.Input.configure(bg='white')
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 1)
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 1)
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 1)
            self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), 1)
            self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), 1)
            self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), 1)
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 1)
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), 1)
            self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 1)
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 1)
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 1)
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 1)

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

        if len(self.image) == 0 and (not self.batch.get()):
            self.statusbar.configure(bg='red')
            self.statusMessage.set("No Image Loaded")
            return

        try:
            XScale_in = self.settings.get('xscale')
            YScale_in = self.settings.get('yscale')
            Angle = self.settings.get('text_angle')
        except:
            self.statusMessage.set(" Unable to create paths.  Check Settings Entry Values.")
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

        # Image transformations
        self.image.transform_scale(XScale, YScale)
        self.image.transform_angle(Angle)
        if self.settings.get('mirror'):
            self.image.transform_mirror()
        if self.settings.get('flip'):
            self.image.transform_flip()

        minx, maxx, miny, maxy = self.image.bbox.tuple()
        if not self.batch.get():
            # Reset Status Bar and Entry Fields
            self.Input.configure(bg='white')
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 1)
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 1)
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 1)
            self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), 1)
            self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), 1)
            self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), 1)
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 1)
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), 1)
            self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 1)
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 1)
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 1)
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 1)

            self.bounding_box.set("Bounding Box (WxH) = " +
                                  "%.3g" % (maxx - minx) +
                                  " %s " % self.settings.get('units') +
                                  " x " +
                                  "%.3g" % (maxy - miny) +
                                  " %s " % self.settings.get('units')
                                  )

            self.statusMessage.set(self.bounding_box.get())

    def v_carve_it(self, clean=False):

        self.master.unbind("<Configure>")
        self.STOP_CALC = False

        v_step_len = self.settings.get('v_step_len')
        if self.units.get() == "mm":
            if v_step_len < .01:
                v_step_len = 0.01
                self.settings.set('v_step_len', v_step_len)
        else:
            if fv_step_len < .0005:
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
        if self.cut_type.get() == "v-carve" and not self.fontdex.get():

            if not self.batch.get():
                if self.v_pplot.get() == 1:
                    self.plot_toolpath()

            # TODO move this to Model
            if self.input_type.get() == "image" and not clean:
                self.engrave.sort_for_v_carve()

            done = self.engrave.v_carve(clean)

            # Reset Entry Fields in V-Carve Settings

            # TODO refresh from settings?
            # if not self.batch.get():
            #     self.entry_set(self.Entry_Vbitangle,   self.Entry_Vbitangle_Check()   ,1)
            #     self.entry_set(self.Entry_Vbitdia,     self.Entry_Vbitdia_Check()     ,1)
            #     self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() ,1)
            #     self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() ,1)
            #     self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check(),1)
            #     self.entry_set(self.Entry_StepSize,    self.Entry_StepSize_Check()    ,1)
            #     self.entry_set(self.Entry_Allowance,   self.Entry_Allowance_Check()   ,1)
            #     self.entry_set(self.Entry_Accuracy,    self.Entry_Accuracy_Check()    ,1)
            #     self.entry_set(self.Entry_CLEAN_DIA,   self.Entry_CLEAN_DIA_Check()   ,1)
            #     self.entry_set(self.Entry_STEP_OVER,   self.Entry_STEP_OVER_Check()   ,1)
            #     self.entry_set(self.Entry_V_CLEAN,     self.Entry_V_CLEAN_Check()     ,1)

            if done and (not self.batch.get()):
                self.statusMessage.set('Done -- ' + self.bounding_box.get())
                self.statusbar.configure(bg='white')

        self.master.bind("<Configure>", self.Master_Configure)
