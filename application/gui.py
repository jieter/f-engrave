import getopt
from time import time
from math import *
import webbrowser

from util import *
from tooltip import ToolTip

from geometry import *
from geometry.model import Model

import readers
from writers import engrave_gcode

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
    import tkinter.messagebox
else:
    from Tkinter import *
    from tkFileDialog import *
    #import tkMessageBox

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
        self.model = Model(controller=self, settings=self.settings)

        self.bind_keys()
        self.create_widgets()

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
        self.v_flop = BooleanVar()
        self.v_pplot = BooleanVar()
        self.inlay = BooleanVar()
        self.no_comments = BooleanVar()
        self.ext_char = BooleanVar()
        self.var_dis = BooleanVar()
        self.useIMGsize = BooleanVar()
        self.plotbox = BooleanVar()

        self.clean_P = BooleanVar()
        self.clean_X = BooleanVar()
        self.clean_Y = BooleanVar()
        self.v_clean_P = BooleanVar()
        self.v_clean_X = BooleanVar()
        self.v_clean_Y = BooleanVar()

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
        # self.plotbox = StringVar()
        self.boxgap = StringVar()
        self.fontdir = StringVar()
        self.cut_type = StringVar()
        self.input_type = StringVar()

        self.bit_shape = StringVar()
        self.v_bit_angle = StringVar()
        self.v_bit_dia = StringVar()
        self.v_depth_lim = StringVar()
        self.v_drv_corner = StringVar()
        self.v_step_corner = StringVar()
        self.v_step_len = StringVar()
        self.allowance = StringVar()
        self.v_check_all = StringVar()
        self.v_max_cut = StringVar()
        self.v_rough_stk = StringVar()

        self.clean_dia = StringVar()
        self.clean_step = StringVar()
        self.clean_v = StringVar()
        self.clean_name = StringVar()

        self.gpre = StringVar()
        self.gpost = StringVar()

        self.bmp_turnpol = StringVar()
        self.bmp_turdsize = StringVar()
        self.bmp_alphamax = StringVar()
        self.bmp_opttolerance = StringVar()
        self.bmp_longcurve = BooleanVar()

        self.maxcut = StringVar()
        self.current_input_file = StringVar()
        self.bounding_box = StringVar()

        self.initialise_settings()

        self.segID = []
        self.gcode = []
        self.svgcode = []

        self.font = {}

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

        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.funits.set('mm/min')

        #TODO settings
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
        ###                           COMMAND LINE                             ###
        ##########################################################################
        opts, args = None, None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hbg:f:d:t:",["help","batch","gcode_file","fontdir=","defdir=","text="])
        except:
            fmessage('Unable interpret command line options')
            sys.exit()
        for option, value in opts:
            if option in ('-h','--help'):
                fmessage(' ')
                fmessage('Usage: python f-engrave.py [-g file | -f fontdir | -d directory | -t text | -b ]')
                fmessage('-g    : f-engrave gcode output file to read (also --gcode_file)')
                fmessage('-f    : path to font file, directory or image file (also --fontdir)')
                fmessage('-d    : default directory (also --defdir)')
                fmessage('-t    : engrave text (also --text)')
                fmessage('-b    : batch mode (also --batch)')
                fmessage('-h    : print this help (also --help)\n')
                sys.exit()
            if option in ('-g','--gcode_file'):
                self.Open_G_Code_File(value)
                self.NGC_FILE = value
            if option in ('-f','--fontdir'):
                if os.path.isdir(value):
                    self.fontdir.set(value)
                elif os.path.isfile(value):
                    dirname = os.path.dirname(value)
                    fileName, fileExtension = os.path.splitext(value)
                    TYPE=fileExtension.upper()
                    if TYPE=='.CXF' or TYPE=='.TTF':
                        self.input_type.set("text")
                        self.fontdir.set(dirname)
                        self.fontfile.set(os.path.basename(fileName)+fileExtension)
                    else:
                        self.input_type.set("image")
                        self.IMAGE_FILE = value
                else:
                    fmessage("File/Directory Not Found:\t%s" %(value) )

            if option in ('-d','--defdir'):
                self.HOME_DIR = value
                if str.find(self.NGC_FILE,'/None') != -1:
                    self.NGC_FILE = (self.HOME_DIR+"/None")
                if str.find(self.IMAGE_FILE,'/None') != -1:
                    self.IMAGE_FILE = (self.HOME_DIR+"/None")
            if option in ('-t','--text'):
                value = value.replace('|', '\n')

                self.default_text = value
            if option in ('-b','--batch'):
                self.batch.set(1)

        if self.batch.get():
            fmessage('(F-Engrave Batch Mode)')

            if self.input_type.get() == "text":
                self.font = readers.readFontFile(self.settings)
            else:
                readers.read_image_file(self.settings)

            self.do_it()

            if self.cut_type.get() == "v-carve":
                self.v_carve_it()

            #self.write_gcode()
            self.coords = self.model.coords
            self.gcode = engrave_gcode(self)

            for line in self.gcode:
                try:
                    sys.stdout.write(line+'\n')
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

        self.PreviewCanvas.bind("<Button-4>" , self._mouseZoomIn)
        self.PreviewCanvas.bind("<Button-5>" , self._mouseZoomOut)
        self.PreviewCanvas.bind("<2>"        , self.mousePanStart)
        self.PreviewCanvas.bind("<B2-Motion>", self.mousePan)
        self.PreviewCanvas.bind("<1>"        , self.mouseZoomStart)
        self.PreviewCanvas.bind("<B1-Motion>", self.mouseZoom)
        self.PreviewCanvas.bind("<3>"        , self.mousePanStart)
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
        self.Label_Yscale_ToolTip = ToolTip(self.Label_Yscale, text= \
            'Character height of a single line of text.')
        # or the height of an imported image. (DXF, BMP, etc.)')

        self.NormalColor = self.Entry_Yscale.cget('bg')

        self.Label_Sthick = Label(self.master, text="Line Thickness")
        self.Label_Sthick_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self.master, width="15")
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick, text= \
            'Thickness or width of engraved lines. Set this to your engraving cutter diameter.  This setting only affects the displayed lines not the g-code output.')

        self.Label_Xscale = Label(self.master, text="Text Width", anchor=CENTER)
        self.Label_Xscale_u = Label(self.master, text="%", anchor=W)
        self.Entry_Xscale = Entry(self.master, width="15")
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale, text= \
            'Scaling factor for the width of characters.')

        self.Label_useIMGsize = Label(self.master, text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command=self.useIMGsize_var_Callback)

        self.Label_Cspace = Label(self.master, text="Char Spacing", anchor=CENTER)
        self.Label_Cspace_u = Label(self.master, text="%", anchor=W)
        self.Entry_Cspace = Entry(self.master, width="15")
        self.Entry_Cspace.configure(textvariable=self.CSPACE)
        self.Entry_Cspace.bind('<Return>', self.Recalculate_Click)
        self.CSPACE.trace_variable("w", self.Entry_Cspace_Callback)
        self.Label_Cspace_ToolTip = ToolTip(self.Label_Cspace, text= \
            'Character spacing as a percent of character width.')

        self.Label_Wspace = Label(self.master, text="Word Spacing", anchor=CENTER)
        self.Label_Wspace_u = Label(self.master, text="%", anchor=W)
        self.Entry_Wspace = Entry(self.master, width="15")
        self.Entry_Wspace.configure(textvariable=self.WSPACE)
        self.Entry_Wspace.bind('<Return>', self.Recalculate_Click)
        self.WSPACE.trace_variable("w", self.Entry_Wspace_Callback)
        self.Label_Wspace_ToolTip = ToolTip(self.Label_Wspace, text= \
            'Width of the space character. This is determined as a percentage of the maximum width of the characters in the currently selected font.')

        self.Label_Lspace = Label(self.master, text="Line Spacing", anchor=CENTER)
        self.Entry_Lspace = Entry(self.master, width="15")
        self.Entry_Lspace.configure(textvariable=self.LSPACE)
        self.Entry_Lspace.bind('<Return>', self.Recalculate_Click)
        self.LSPACE.trace_variable("w", self.Entry_Lspace_Callback)
        self.Label_Lspace_ToolTip = ToolTip(self.Label_Lspace, text= \
            'The vertical spacing between lines of text. This is a multiple of the text height previously input. A vertical spacing of 1.0 could result in consecutive lines of text touching each other if the maximum height character is directly below a character that extends the lowest (like a "g").')

        self.Label_pos_orient = Label(self.master, text="Text Position and Orientation:", anchor=W)

        self.Label_Tangle = Label(self.master, text="Text Angle", anchor=CENTER)
        self.Label_Tangle_u = Label(self.master, text="deg", anchor=W)
        self.Entry_Tangle = Entry(self.master, width="15")
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle, text= \
            'Rotation of the text or image from horizontal.')

        self.Label_Justify = Label(self.master, text="Justify", anchor=CENTER)
        self.Justify_OptionMenu = OptionMenu(self.master, self.justify, "Left", "Center",
                                             "Right", command=self.Recalculate_RQD_Click)
        self.Label_Justify_ToolTip = ToolTip(self.Label_Justify, text= \
            'Justify determins how to align multiple lines of text. Left side, Right side or Centered.')

        self.Label_Origin = Label(self.master, text="Origin", anchor=CENTER)
        self.Origin_OptionMenu = OptionMenu(self.master, self.origin,
                                            "Top-Left",
                                            "Top-Center",
                                            "Top-Right",
                                            "Mid-Left",
                                            "Mid-Center",
                                            "Mid-Right",
                                            "Bot-Left",
                                            "Bot-Center",
                                            "Bot-Right",
                                            "Default", command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin, text= \
            'Origin determins where the X and Y zero position is located relative to the engraving.')

        self.Label_flip = Label(self.master, text="Flip Text")
        self.Checkbutton_flip = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip, text= \
            'Selecting Flip Text/Image mirrors the design about a horizontal line')

        self.Label_mirror = Label(self.master, text="Mirror Text")
        self.Checkbutton_mirror = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror, text= \
            'Selecting Mirror Text/Image mirrors the design about a vertical line.')

        self.Label_text_on_arc = Label(self.master, text="Text on Circle Properties:", anchor=W)

        self.Label_Tradius = Label(self.master, text="Circle Radius", anchor=CENTER)
        self.Label_Tradius_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Tradius = Entry(self.master, width="15")
        self.Entry_Tradius.configure(textvariable=self.TRADIUS)
        self.Entry_Tradius.bind('<Return>', self.Recalculate_Click)
        self.TRADIUS.trace_variable("w", self.Entry_Tradius_Callback)
        self.Label_Tradius_ToolTip = ToolTip(self.Label_Tradius, text= \
            'Circle radius is the radius of the circle that the text in the input box is placed on. If the circle radius is set to 0.0 the text is not placed on a circle.')

        self.Label_outer = Label(self.master, text="Outside circle")
        self.Checkbutton_outer = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=self.outer)
        self.outer.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_outer_ToolTip = ToolTip(self.Label_outer, text= \
            'Select whether the text is placed so that is falls on the inside of the circle radius or the outside of the circle radius.')

        self.Label_upper = Label(self.master, text="Top of Circle")
        self.Checkbutton_upper = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=self.upper)
        self.upper.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_upper_ToolTip = ToolTip(self.Label_upper, text= \
            'Select whether the text is placed on the top of the circle of on the bottom of the circle (i.e. concave down or concave up).')

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
        self.Label_Feed_ToolTip = ToolTip(self.Label_Feed, text= \
            'Specify the tool feed rate that is output in the g-code output file.')

        self.Label_Plunge = Label(self.master, text="Plunge Rate")
        self.Label_Plunge_u = Label(self.master, textvariable=self.funits, anchor=W)
        self.Entry_Plunge = Entry(self.master, width="15")
        self.Entry_Plunge.configure(textvariable=self.PLUNGE)
        self.Entry_Plunge.bind('<Return>', self.Recalculate_Click)
        self.PLUNGE.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(self.Label_Plunge, text= \
            'Plunge Rate sets the feed rate for vertical moves into the material being cut.\n\nWhen Plunge Rate is set to zero plunge feeds are equal to Feed Rate.')

        self.Label_Zsafe = Label(self.master, text="Z Safe")
        self.Label_Zsafe_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self.master, width="15")
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(self.Label_Zsafe, text= \
            'Z location that the tool will be sent to prior to any rapid moves.')

        self.Label_Zcut = Label(self.master, text="Engrave Depth")
        self.Label_Zcut_u = Label(self.master, textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self.master, width="15")
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(self.Label_Zcut, text= \
            'Depth of the engraving cut. This setting has no effect when the v-carve option is selected.')

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
            if  str.find(name.upper(), '.CXF') != -1 \
            or (str.find(name.upper(), '.TTF') != -1 and TTF_AVAILABLE):
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
        self.Input_Label = Label(self.master, text="Input Text:",anchor=W)

        lbframe = Frame(self.master)
        self.Input_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Input = Text(lbframe, width="40", height="12", yscrollcommand=scrollbar.set, bg='white')
        self.Input.insert(END, self.default_text)
        scrollbar.config(command=self.Input.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Input.pack(side=LEFT, fill=BOTH, expand=1)
        self.Input.bind("<Key>", self.recalculate_RQD_Nocalc)
        ## self.master.unbind("<Alt>")

        # GEN Setting Window Entry initialization
        self.Entry_Xoffset = Entry()
        self.Entry_Yoffset = Entry()
        self.Entry_BoxGap = Entry()
        self.Entry_ArcAngle = Entry()
        self.Entry_Accuracy = Entry()
        # Bitmap Setting Window Entry initialization
        self.Entry_BMPturdsize = Entry()
        self.Entry_BMPalphamax = Entry()
        self.Entry_BMPoptTolerance = Entry()
        # V-Carve Setting Window Entry initialization
        self.Entry_Vbitangle = Entry()
        self.Entry_Vbitdia = Entry()
        self.Entry_VDepthLimit = Entry()
        self.Entry_InsideAngle = Entry()
        self.Entry_OutsideAngle = Entry()
        self.Entry_StepSize = Entry()
        self.Entry_Allowance = Entry()
        self.Entry_W_CLEAN = Entry()
        self.Entry_CLEAN_DIA = Entry()
        self.Entry_STEP_OVER = Entry()
        self.Entry_V_CLEAN = Entry()

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
        top_Settings.add("command", label="General Settings", command=self.GEN_Settings_Window)
        top_Settings.add("command", label="V-Carve Settings", command=self.VCARVE_Settings_Window)
        if POTRACE_AVAILABLE:
            top_Settings.add("command", label="Bitmap Import Settings", command=self.PBM_Settings_Window)

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
        '''
        Initialise the TK widgets with the values from settings
        '''
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

        self.v_flop.set(self.settings.get('v_flop'))
        self.v_pplot.set(self.settings.get('v_pplot'))
        self.inlay.set(self.settings.get('inlay'))
        self.no_comments.set(self.settings.get('no_comments'))
        self.ext_char.set(self.settings.get('ext_char'))
        self.var_dis.set(self.settings.get('var_dis'))

        self.clean_P.set(self.settings.get('clean_P'))
        self.clean_X.set(self.settings.get('clean_X'))
        self.clean_Y.set(self.settings.get('clean_Y'))
        self.v_clean_P.set(self.settings.get('v_clean_P'))
        self.v_clean_Y.set(self.settings.get('v_clean_Y'))
        self.v_clean_X.set(self.settings.get('v_clean_X'))

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
        self.FEED.set(self.settings.get('feedrate'))
        self.PLUNGE.set(self.settings.get('plunge_rate'))
        self.fontfile.set(self.settings.get('fontfile'))
        self.H_CALC.set(self.settings.get('height_calculation'))
        # self.plotbox.set()
        self.boxgap.set(self.settings.get('boxgap'))
        self.fontdir.set(self.settings.get('fontdir'))
        self.cut_type.set(self.settings.get('cut_type'))
        self.input_type.set(self.settings.get('input_type'))

        self.gpre.set(self.settings.get('gcode_preamble'))
        self.gpost.set(self.settings.get('gcode_postamble'))

        self.bit_shape.set(self.settings.get('bit_shape'))
        self.v_bit_angle.set(self.settings.get('v_bit_angle'))
        self.v_bit_dia.set(self.settings.get('v_bit_dia'))
        self.v_depth_lim.set(self.settings.get('v_depth_lim'))
        self.v_drv_corner.set(self.settings.get('v_drv_corner'))
        self.v_step_corner.set(self.settings.get('v_step_corner'))
        self.v_step_len.set(self.settings.get('v_step_len'))
        self.allowance.set(self.settings.get('allowance'))
        self.v_check_all.set(self.settings.get('v_check_all'))
        self.v_rough_stk.set(self.settings.get('v_rough_stk'))
        self.v_max_cut.set(self.settings.get('v_max_cut'))

        self.bmp_turnpol.set(self.settings.get('bmp_turnpol'))
        self.bmp_turdsize.set(self.settings.get('bmp_turdsize'))
        self.bmp_alphamax.set(self.settings.get('bmp_alphamax'))
        self.bmp_opttolerance.set(self.settings.get('bmp_opttolerance'))
        self.bmp_longcurve.set(self.settings.get('bmp_longcurve'))

        self.xorigin.set(self.settings.get('xorigin'))
        self.yorigin.set(self.settings.get('yorigin'))
        self.segarc.set(self.settings.get('segarc'))
        self.accuracy.set(self.settings.get('accuracy'))

        self.clean_v.set(self.settings.get('clean_v'))
        self.clean_dia.set(self.settings.get('clean_dia'))
        self.clean_step.set(self.settings.get('clean_step'))
        self.clean_name.set(self.settings.get('clean_name'))

        self.default_text = self.settings.get('default_text')

        self.HOME_DIR = (self.settings.get('HOME_DIR'))
        self.NGC_FILE = (self.settings.get('NGC_FILE'))
        self.IMAGE_FILE = (self.settings.get('IMAGE_FILE'))

    def entry_set(self, val2, calc_flag=0, new=0):
        if calc_flag == 0 and new == 0:
            try:
                self.statusbar.configure(bg='yellow')
                val2.configure(bg='yellow')
                self.statusMessage.set(" Recalculation required.")
            except:
                pass
        elif calc_flag == 3:
            try:
                val2.configure(bg='red')
                self.statusbar.configure(bg='red')
                self.statusMessage.set(" Value should be a number. ")
            except:
                pass
        elif calc_flag == 2:
            try:
                self.statusbar.configure(bg='red')
                val2.configure(bg='red')
            except:
                pass
        elif (calc_flag == 0 or calc_flag == 1) and new == 1:
            try:
                self.statusbar.configure(bg='white')
                self.statusMessage.set(self.bounding_box.get())
                val2.configure(bg='white')
            except:
                pass
        elif (calc_flag == 1) and new == 0:
            try:
                self.statusbar.configure(bg='white')
                self.statusMessage.set(self.bounding_box.get())
                val2.configure(bg='white')
            except:
                pass

        elif (calc_flag == 0 or calc_flag == 1) and new == 2:
            return 0
        return 1

    #TODO Compare to save_settings
    def write_config_file(self, event):

        self.gcode = self.settings.to_gcode()

        config_filename = self.settings.get('config_filename')
        configname_full = self.settings.get('HOME_DIR')+ "/" + config_filename

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
        for line in self.gcode:
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

    #TODO Remove (replaced by engrave_gcode())
    # def write_gcode(self):
    #     '''
    #     Generate and write G-code
    #     '''
    #     self.gcode = []
    #
    #     SafeZ = float(self.ZSAFE.get())
    #     Depth = float(self.ZCUT.get())
    #     Acc = float(self.accuracy.get())
    #
    #     if self.batch.get():
    #         String = self.default_text
    #     else:
    #         String = self.Input.get(1.0, END)
    #
    #     String_short = String
    #     max_len = 40
    #     if len(String)  >  max_len:
    #         String_short = String[0:max_len] + '___'
    #
    #     if self.units.get() == "in":
    #         dp = 4
    #         dpfeed = 2
    #     else:
    #         dp = 3
    #         dpfeed = 1
    #
    #     g_target = lambda s: sys.stdout.write(s + "\n")
    #     g = Gcode(safetyheight=SafeZ,
    #               tolerance=Acc,
    #               target=lambda s: self.gcode.append(s),
    #               arc_fit=self.arc_fit.get())
    #
    #     g.dp = dp
    #     g.dpfeed = dpfeed
    #     g.set_plane(17)
    #
    #     if not self.var_dis.get():
    #         FORMAT = '#1 = %%.%df  ( Safe Z )' % (dp)
    #         self.gcode.append(FORMAT % (SafeZ))
    #         FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' % (dp)
    #         self.gcode.append(FORMAT % (Depth))
    #         safe_val = '#1'
    #         depth_val = '#2'
    #     else:
    #         FORMAT = '%%.%df' % (dp)
    #         safe_val = FORMAT % (SafeZ)
    #         depth_val = FORMAT % (Depth)
    #
    #     # G90        ; Sets absolute distance mode
    #     self.gcode.append('G90')
    #     # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
    #     if self.arc_fit.get() == "center":
    #         self.gcode.append('G91.1')
    #     if self.units.get() == "in":
    #         # G20 ; sets units to inches
    #         self.gcode.append('G20')
    #     else:
    #         # G21 ; sets units to mm
    #         self.gcode.append('G21')
    #
    #     for line in self.gpre.get().split('|'):
    #         self.gcode.append(line)
    #
    #     FORMAT = '%%.%df' % (dpfeed)
    #     feed_str = FORMAT % (float(self.FEED.get()))
    #     plunge_str = FORMAT % (float(self.PLUNGE.get()))
    #     zero_feed = FORMAT % (float(0.0))
    #
    #     # Set Feed rate
    #     self.gcode.append("F%s" % feed_str)
    #
    #     if plunge_str == zero_feed:
    #         plunge_str = feed_str
    #
    #     oldx = oldy = -99990.0
    #
    #     # Set up variables for multipass cutting
    #     maxDZ = float(self.v_max_cut.get())
    #     rough_stock = float(self.v_rough_stk.get())
    #     zmin = 0.0
    #
    #     first_stroke = True
    #     roughing = True
    #     rough_again = False
    #
    #     if self.cut_type.get() == "engrave" or self.bit_shape.get() == "FLAT":
    #
    #         ecoords = []
    #
    #         if (self.bit_shape.get() == "FLAT") and (self.cut_type.get() != "engrave"):
    #             Acc = float(self.v_step_len.get()) * 1.5  # fudge factor
    #             ###################################
    #             ###   Create Flat Cut ECOORDS   ###
    #             ###################################
    #             if self.model.number_of_v_segments() > 0:
    #                 rbit = self.calc_vbit_dia() / 2.0
    #                 loopa_old = self.model.vcoords[0][3]
    #                 loop = 0
    #                 for i in range(1, self.model.number_of_v_segments()):
    #                     xa = self.model.vcoords[i][0]
    #                     ya = self.model.vcoords[i][1]
    #                     ra = self.model.vcoords[i][2]
    #                     loopa = self.model.vcoords[i][3]
    #
    #                     if (loopa_old != loopa):
    #                         loop = loop + 1
    #                     if ra >= rbit:
    #                         ecoords.append([xa, ya, loop])
    #                         loopa_old = loopa
    #                     else:
    #                         loop = loop + 1
    #             Depth = float(self.maxcut.get())
    #             if rough_stock > 0:
    #                 rough_again = True
    #             if (rough_stock > 0 and -maxDZ < rough_stock):
    #                 rough_stock = -maxDZ
    #
    #         else:
    #             ##########################
    #             ###   Create ECOORDS   ###
    #             ##########################
    #             loop = 0
    #             for line in self.model.coords:
    #                 XY = line
    #                 x1 = XY[0]
    #                 y1 = XY[1]
    #                 x2 = XY[2]
    #                 y2 = XY[3]
    #                 dx = oldx - x1
    #                 dy = oldy - y1
    #                 dist = sqrt(dx * dx + dy * dy)
    #                 # check and see if we need to move to a new discontinuous start point
    #                 if dist > Acc or first_stroke:
    #                     loop += 1
    #                     first_stroke = False
    #                     ecoords.append([x1, y1, loop])
    #                 ecoords.append([x2, y2, loop])
    #                 oldx, oldy = x2, y2
    #
    #         order_out = sort_paths(ecoords)  # TODO sort_paths
    #
    #         while rough_again or roughing:
    #             if rough_again == False:
    #                 roughing = False
    #                 maxDZ = -99999
    #             rough_again = False
    #             zmin = zmin + maxDZ
    #
    #             z1 = Depth
    #             if roughing:
    #                 z1 = z1 + rough_stock
    #             if z1 < zmin:
    #                 z1 = zmin
    #                 rough_again = True
    #             zmax = zmin - maxDZ
    #
    #             if (self.bit_shape.get() == "FLAT") and (self.cut_type.get() != "engrave"):
    #                 FORMAT = '%%.%df' % (dp)
    #                 depth_val = FORMAT % (z1)
    #
    #             dist = 999
    #             lastx = -999
    #             lasty = -999
    #             lastz = 0
    #             z1 = 0
    #             nextz = 0
    #
    #             # self.gcode.append("G0 Z%s" %(safe_val))
    #             for line in order_out:
    #                 temp = line
    #                 if temp[0] > temp[1]:
    #                     step = -1
    #                 else:
    #                     step = 1
    #
    #                 R_last = 999
    #                 x_center_last = 999
    #                 y_center_last = 999
    #                 FLAG_arc = 0
    #                 FLAG_line = 0
    #                 code = " "
    #
    #                 loop_old = -1
    #
    #                 for i in range(temp[0], temp[1] + step, step):
    #                     x1 = ecoords[i][0]
    #                     y1 = ecoords[i][1]
    #                     loop = ecoords[i][2]
    #
    #                     if (i + 1 < temp[1] + step):
    #                         nextx = ecoords[i + 1][0]
    #                         nexty = ecoords[i + 1][1]
    #                         nextloop = ecoords[i + 1][2]
    #                     else:
    #                         nextx = 0
    #                         nexty = 0
    #                         nextloop = -99  # don't change this dummy number it is used below
    #
    #                     # check and see if we need to move to a new discontinuous start point
    #                     if loop != loop_old:
    #                         g.flush()
    #                         dx = x1 - lastx
    #                         dy = y1 - lasty
    #                         dist = sqrt(dx * dx + dy * dy)
    #                         if dist > Acc:
    #                             # lift engraver
    #                             self.gcode.append("G0 Z%s" % (safe_val))
    #                             # rapid to current position
    #
    #                             FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
    #                             self.gcode.append(FORMAT % (x1, y1))
    #                             # drop cutter
    #                             if (feed_str == plunge_str):
    #                                 self.gcode.append('G1 Z%s' % (depth_val))
    #                             else:
    #                                 self.gcode.append('G1 Z%s F%s' % (depth_val, plunge_str))
    #                                 g.set_feed(feed_str)
    #                             lastx = x1
    #                             lasty = y1
    #                             g.cut(x1, y1)
    #                     else:
    #                         g.cut(x1, y1)
    #                         lastx = x1
    #                         lasty = y1
    #
    #                     loop_old = loop
    #                 g.flush()
    #             g.flush()
    #         g.flush()
    #     # END engraving
    #     else:
    #         # V-carve stuff
    #         plunge_str = feed_str
    #         ##########################
    #         ###   find loop ends   ###
    #         ##########################
    #         Lbeg = []
    #         Lend = []
    #         Lbeg.append(0)
    #         if self.model.number_of_v_segments() > 0:
    #             loop_old = self.model.vcoords[0][3]
    #             for i in range(1, self.model.number_of_v_segments()):
    #                 loop = self.model.vcoords[i][3]
    #                 if loop != loop_old:
    #                     Lbeg.append(i)
    #                     Lend.append(i - 1)
    #                 loop_old = loop
    #             Lend.append(i)
    #             #####################################################
    #             # Find new order based on distance to next begining #
    #             #####################################################
    #             order_out = []
    #             order_out.append([Lbeg[0], Lend[0]])
    #             inext = 0
    #             total = len(Lbeg)
    #             for i in range(total - 1):
    #                 ii = Lend.pop(inext)
    #                 Lbeg.pop(inext)
    #                 Xcur = self.model.vcoords[ii][0]
    #                 Ycur = self.model.vcoords[ii][1]
    #
    #                 dx = Xcur - self.model.vcoords[Lbeg[0]][0]
    #                 dy = Ycur - self.model.vcoords[Lbeg[0]][1]
    #                 min_dist = dx * dx + dy * dy
    #
    #                 inext = 0
    #                 for j in range(1, len(Lbeg)):
    #                     dx = Xcur - self.model.vcoords[Lbeg[j]][0]
    #                     dy = Ycur - self.model.vcoords[Lbeg[j]][1]
    #                     dist = dx * dx + dy * dy
    #                     if dist < min_dist:
    #                         min_dist = dist
    #                         inext = j
    #                 order_out.append([Lbeg[inext], Lend[inext]])
    #             #####################################################
    #             new_coords = []
    #             for line in order_out:
    #                 temp = line
    #                 for i in range(temp[0], temp[1] + 1):
    #                     new_coords.append(self.model.vcoords[i])
    #
    #             half_angle = radians(float(self.v_bit_angle.get()) / 2.0)
    #             bit_radius = float(self.v_bit_dia.get()) / 2.0
    #
    #             ################################
    #             # V-carve stuff
    #             # maxDZ = float(self.v_max_cut.get())
    #             # rough_stock =  float(self.v_rough_stk.get())
    #             # zmin = 0.0
    #             # roughing = True
    #             # rough_again = False
    #             if rough_stock > 0:
    #                 rough_again = True
    #             ################################
    #             if (rough_stock > 0) and (-maxDZ < rough_stock):
    #                 rough_stock = -maxDZ
    #             while rough_again or roughing:
    #                 if rough_again == False:
    #                     roughing = False
    #                     maxDZ = -99999
    #                 rough_again = False
    #                 zmin = zmin + maxDZ
    #
    #                 loop_old = -1
    #                 R_last = 999
    #                 x_center_last = 999
    #                 y_center_last = 999
    #                 FLAG_arc = 0
    #                 FLAG_line = 0
    #                 code = " "
    #
    #                 v_index = -1
    #
    #                 while v_index < len(new_coords) - 1:
    #                     v_index = v_index + 1
    #                     x1 = new_coords[v_index][0]
    #                     y1 = new_coords[v_index][1]
    #                     r1 = new_coords[v_index][2]
    #                     loop = new_coords[v_index][3]
    #
    #                     if (v_index + 1) < len(new_coords):
    #                         nextx = new_coords[v_index + 1][0]
    #                         nexty = new_coords[v_index + 1][1]
    #                         nextr = new_coords[v_index + 1][2]
    #                         nextloop = new_coords[v_index + 1][3]
    #                     else:
    #                         nextx = 0
    #                         nexty = 0
    #                         nextr = 0
    #                         nextloop = -99  # don't change this dummy number it is used below
    #
    #                     if self.bit_shape.get() == "VBIT":
    #                         z1 = -r1 / tan(half_angle)
    #                         nextz = -nextr / tan(half_angle)
    #                         if self.inlay.get():
    #                             inlay_depth = self.calc_r_inlay_depth()
    #                             z1 = z1 + inlay_depth
    #                             nextz = nextz + inlay_depth
    #
    #                     elif self.bit_shape.get() == "BALL":
    #                         theta = acos(r1 / bit_radius)
    #                         z1 = -bit_radius * (1 - sin(theta))
    #
    #                         next_theta = acos(nextr / bit_radius)
    #                         nextz = -bit_radius * (1 - sin(next_theta))
    #                     elif self.bit_shape.get() == "FLAT":
    #                         # This case should have been caught in the
    #                         # engraving section above
    #                         pass
    #                     else:
    #                         pass
    #
    #                     if roughing:
    #                         z1 = z1 + rough_stock
    #                         nextz = nextz + rough_stock
    #                     if z1 < zmin:
    #                         z1 = zmin
    #                         rough_again = True
    #                     if nextz < zmin:
    #                         nextz = zmin
    #                         rough_again = True
    #
    #                     zmax = zmin - maxDZ  # + rough_stock
    #                     if z1 > zmax and nextz > zmax and roughing:
    #                         loop_old = -1
    #                         continue
    #                     # check and see if we need to move to a new discontinuous start point
    #                     if loop != loop_old:
    #                         g.flush()
    #                         # lift engraver
    #                         self.gcode.append("G0 Z%s" % (safe_val))
    #                         # rapid to current position
    #                         FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
    #                         self.gcode.append(FORMAT % (x1, y1))
    #                         # drop cutter to z depth
    #                         FORMAT = 'G1 Z%%.%df' % (dp)
    #                         self.gcode.append(FORMAT % (z1))
    #
    #                         lastx = x1
    #                         lasty = y1
    #                         lastz = z1
    #                         g.cut(x1, y1, z1)
    #                     else:
    #                         g.cut(x1, y1, z1)
    #                         lastx = x1
    #                         lasty = y1
    #                         lastz = z1
    #                     loop_old = loop
    #                 g.flush()
    #             g.flush()
    #         g.flush()
    #         # End V-carve stuff
    #
    #     # Make Circle
    #     XOrigin = float(self.xorigin.get())
    #     YOrigin = float(self.yorigin.get())
    #     Radius_plot = float(self.RADIUS_PLOT)
    #     if Radius_plot != 0 and self.cut_type.get() == "engrave":
    #         self.gcode.append('G0 Z%s' % (safe_val))
    #
    #         FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
    #         self.gcode.append(FORMAT % (-Radius_plot - self.xzero + XOrigin, YOrigin - self.yzero))
    #
    #         if feed_str == plunge_str:
    #             FEED_STRING = ""
    #         else:
    #             FEED_STRING = " F" + plunge_str
    #             g.set_feed(feed_str)
    #
    #         self.gcode.append('G1 Z%s' % (depth_val) + FEED_STRING)
    #
    #         if feed_str == plunge_str:
    #             FEED_STRING = ""
    #         else:
    #             FEED_STRING = " F" + feed_str
    #
    #         FORMAT = 'G2 I%%.%df J%%.%df' % (dp, dp)
    #         self.gcode.append(FORMAT % (Radius_plot, 0.0) + FEED_STRING)
    #     # End Circle
    #
    #     self.gcode.append('G0 Z%s' % (safe_val))  # final engraver up
    #
    #     for line in self.gpost.get().split('|'):
    #         self.gcode.append(line)

    #############################
    # Write Cleanup G-code File #
    #############################
    def WRITE_CLEAN_UP(self, bit_type="straight"):
        self.gcode = []
        SafeZ = float(self.ZSAFE.get())
        BitDia = float(self.clean_dia.get())

        self.calc_depth_limit()
        Depth = float(self.maxcut.get())
        if self.inlay.get():
            Depth = Depth + float(self.allowance.get())

        Acc = float(self.accuracy.get())
        Units = self.units.get()

        if bit_type == "straight":
            coords_out = self.model.clean_coords_sort
        else:
            coords_out = self.model.v_clean_coords_sort

        if not self.no_comments.get():
            self.gcode.append('( Code generated by f-engrave-' + version + '.py )')
            self.gcode.append('( by Scorch - 2017 )')
            self.gcode.append('( This file is a secondary operation for )')
            self.gcode.append('( cleaning up a V-carve. )')

            if bit_type == "straight":
                self.gcode.append('( The tool paths were calculated based )')
                self.gcode.append('( on using a bit with a )')
                self.gcode.append('( Diameter of %.4f %s)' % (BitDia, Units))
            else:
                self.gcode.append('( The tool paths were calculated based )')
                self.gcode.append('( on using a v-bit with a)')
                self.gcode.append('( angle of %.4f Degrees)' % (float(self.v_bit_angle.get())))

            self.gcode.append("(==========================================)")

        if self.units.get() == "in":
            dp = 4
            dpfeed = 2
        else:
            dp = 3
            dpfeed = 1

        if not self.var_dis.get():
            FORMAT = '#1 = %%.%df  ( Safe Z )' % (dp)
            self.gcode.append(FORMAT % (SafeZ))
            safe_val = '#1'
        else:
            FORMAT = '%%.%df' % (dp)
            safe_val = FORMAT % (SafeZ)
            depth_val = FORMAT % (Depth)

        self.gcode.append("(##########################################)")
        # G90        ; Sets absolute distance mode
        self.gcode.append('G90')
        # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
        if self.arc_fit.get() == "center":
            self.gcode.append('G91.1')
        if self.units.get() == "in":
            # G20 ; sets units to inches
            self.gcode.append('G20')
        else:
            # G21 ; sets units to mm
            self.gcode.append('G21')

        for line in self.gpre.get().split('|'):
            self.gcode.append(line)

        # self.gcode.append( 'G0 Z%s' %(safe_val))

        FORMAT = '%%.%df' % (dp)
        feed_str = FORMAT % (float(self.FEED.get()))
        plunge_str = FORMAT % (float(self.PLUNGE.get()))
        feed_current = FORMAT % (float(0.0))
        # fmessage(feed_str +" "+plunge_str)
        if plunge_str == feed_current:
            plunge_str = feed_str

        # Multipass stuff
        ################################
        # Cleanup
        maxDZ = float(self.v_max_cut.get())
        rough_stock = float(self.v_rough_stk.get())
        zmin = 0.0
        roughing = True
        rough_again = False
        if rough_stock > 0:
            rough_again = True
        ################################
        if ((rough_stock > 0) and (-maxDZ < rough_stock)):
            rough_stock = -maxDZ
        while rough_again or roughing:
            if not rough_again:
                roughing = False
                maxDZ = -99999
            rough_again = False
            zmin = zmin + maxDZ

            # self.gcode.append( 'G0 Z%s' %(safe_val))
            oldx = oldy = -99990.0
            first_stroke = True
            ########################################################################
            # The clean coords have already been sorted so we can just write them  #
            ########################################################################

            order_out = sort_paths(coords_out, 3)  # TODO
            new_coords = []
            for line in order_out:
                temp = line
                if temp[0] < temp[1]:
                    step = 1
                else:
                    step = -1
                for i in range(temp[0], temp[1] + step, step):
                    new_coords.append(coords_out[i])
            coords_out = new_coords

            if len(coords_out) > 0:
                loop_old = -1
                FLAG_arc = 0
                FLAG_line = 0
                code = " "
                v_index = -1
                while v_index < len(coords_out) - 1:
                    v_index = v_index + 1
                    x1 = coords_out[v_index][0]
                    y1 = coords_out[v_index][1]
                    r1 = coords_out[v_index][2]
                    loop = coords_out[v_index][3]

                    if v_index + 1 < len(coords_out):
                        nextx = coords_out[v_index + 1][0]
                        nexty = coords_out[v_index + 1][1]
                        nextr = coords_out[v_index + 1][2]
                        nextloop = coords_out[v_index + 1][3]
                    else:
                        nextx = 0
                        nexty = 0
                        nextr = 0
                        nextloop = -99

                    # check and see if we need to move to a new discontinuous start point
                    if loop != loop_old:
                        # lift engraver
                        self.gcode.append("G0 Z%s" % (safe_val))
                        # rapid to current position
                        FORMAT = 'G0 X%%.%df Y%%.%df' % (dp, dp)
                        self.gcode.append(FORMAT % (x1, y1))

                        z1 = Depth;
                        if roughing:
                            z1 = Depth + rough_stock  # Depth
                        if z1 < zmin:
                            z1 = zmin
                            rough_again = True

                        FORMAT = '%%.%df' % (dp)
                        depth_val = FORMAT % (z1)

                        if feed_current == plunge_str:
                            FEED_STRING = ""
                        else:
                            FEED_STRING = " F" + plunge_str
                            feed_current = plunge_str

                        self.gcode.append("G1 Z%s" % (depth_val) + FEED_STRING)

                        lastx = x1
                        lasty = y1
                    else:
                        if feed_str == feed_current:
                            FEED_STRING = ""
                        else:
                            FEED_STRING = " F" + feed_str
                            feed_current = feed_str

                        FORMAT = 'G1 X%%.%df Y%%.%df' % (dp, dp)
                        self.gcode.append(FORMAT % (x1, y1) + FEED_STRING)
                        lastx = x1
                        lasty = y1
                    loop_old = loop

        # End multipass loop

        self.gcode.append('G0 Z%s' % (safe_val))  # final engraver up

        for line in self.gpost.get().split('|'):
            self.gcode.append(line)

    #TODO move to Writers
    def WriteSVG(self):
        '''Write SVG'''
        if self.cut_type.get() == "v-carve":
            Thick = 0.001
        else:
            Thick = float(self.STHICK.get())

        dpi=100

        maxx = -99919.0
        maxy = -99929.0
        maxa = -99939.0
        mina =  99949.0
        miny =  99959.0
        minx =  99969.0
        for line in self.model.coords:
            XY = line
            maxx = max(maxx, XY[0], XY[2])
            minx = min(minx, XY[0], XY[2])
            miny = min(miny, XY[1], XY[3])
            maxy = max(maxy, XY[1], XY[3])

        XOrigin = float(self.xorigin.get())
        YOrigin = float(self.yorigin.get())
        Radius_plot = float(self.RADIUS_PLOT)
        if Radius_plot != 0:
            maxx = max(maxx, XOrigin+Radius_plot - self.xzero)
            minx = min(minx, XOrigin-Radius_plot - self.xzero)
            miny = min(miny, YOrigin-Radius_plot - self.yzero)
            maxy = max(maxy, YOrigin+Radius_plot - self.yzero)

        maxx = maxx + Thick/2
        minx = minx - Thick/2
        miny = miny - Thick/2
        maxy = maxy + Thick/2

        width_in = maxx-minx
        height_in = maxy-miny
        width = ((maxx-minx)*dpi)
        height = ((maxy-miny)*dpi)

        self.svgcode = []
        self.svgcode.append('<?xml version="1.0" standalone="no"?>')
        self.svgcode.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"  ')
        self.svgcode.append('  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">  ')
        self.svgcode.append('<svg width="%f%s" height="%f%s" viewBox="0 0 %f %f"  ' \
                            %(width_in, self.units.get(), height_in, self.units.get(), width, height) )
        self.svgcode.append('     xmlns="http://www.w3.org/2000/svg" version="1.1">')
        self.svgcode.append('  <title> F-engrave Output </title>')
        self.svgcode.append('  <desc>SVG File Created By F-Engrave</desc>')

        # Make Circle
        if Radius_plot != 0 and self.cut_type.get() == "engrave":
            self.svgcode.append('  <circle cx="%f" cy="%f" r="%f"' %(
                        ( XOrigin-self.xzero-minx)*dpi,
                        (-YOrigin+self.yzero+maxy)*dpi,
                        ( Radius_plot            )*dpi) )
            self.svgcode.append('        fill="none" stroke="blue" stroke-width="%f"/>' %(Thick*dpi))
        # End Circle

        for line in self.model.coords:
            XY = line
            self.svgcode.append('  <path d="M %f %f L %f %f"' %(
                    ( XY[0]-minx)*dpi,
                    (-XY[1]+maxy)*dpi,
                    ( XY[2]-minx)*dpi,
                    (-XY[3]+maxy)*dpi) )
            self.svgcode.append('        fill="none" stroke="blue" stroke-width="%f" stroke-linecap="round" stroke-linejoin="round"/>' %(Thick*dpi))

        if self.input_type.get() == "text":
            Radius_in =  float(self.TRADIUS.get())
        else:
            Radius_in = 0.0

        Thick = float(self.STHICK.get() )
        #if self.plotbox.get() != "no_box":
        if self.plotbox.get():
            if Radius_in != 0:
                Delta = Thick/2 + float(self.boxgap.get())
        self.svgcode.append('</svg>')

    #TODO move to Writers
    def WriteDXF(self,close_loops=False):
        '''Write G-Code DXF'''
        if close_loops:
            self.v_carve_it(clean_flag=0,DXF_FLAG = close_loops)
        
        dxf_code = []
        # Create a header section just in case the reading software needs it
        dxf_code.append("999")
        dxf_code.append("DXF created by G-Code Ripper <by Scorch, www.scorchworks.com>")
        dxf_code.append("0")
        dxf_code.append("SECTION")
        dxf_code.append("2")
        dxf_code.append("HEADER")
        #dxf_code.append("9")
        #dxf_code.append("$INSUNITS")
        #dxf_code.append("70")
        #dxf_code.append("1") #units 1 = Inches; 4 = Millimeters;
        dxf_code.append("0")
        dxf_code.append("ENDSEC")

        #         
        #Tables Section
        #These can be used to specify predefined constants, line styles, text styles, view 
        #tables, user coordinate systems, etc. We will only use tables to define some layers 
        #for use later on. Note: not all programs that support DXF import will support 
        #layers and those that do usually insist on the layers being defined before use
        #
        # The following will initialise layers 1 and 2 for use with moves and rapid moves.
        dxf_code.append("0")
        dxf_code.append("SECTION")
        dxf_code.append("2")
        dxf_code.append("TABLES")
        dxf_code.append("0")
        dxf_code.append("TABLE")
        dxf_code.append("2")
        dxf_code.append("LTYPE")
        dxf_code.append("70")
        dxf_code.append("1")
        dxf_code.append("0")
        dxf_code.append("LTYPE")
        dxf_code.append("2")
        dxf_code.append("CONTINUOUS")
        dxf_code.append("70")
        dxf_code.append("64")
        dxf_code.append("3")
        dxf_code.append("Solid line")
        dxf_code.append("72")
        dxf_code.append("65")
        dxf_code.append("73")
        dxf_code.append("0")
        dxf_code.append("40")
        dxf_code.append("0.000000")
        dxf_code.append("0")
        dxf_code.append("ENDTAB")
        dxf_code.append("0")
        dxf_code.append("TABLE")
        dxf_code.append("2")
        dxf_code.append("LAYER")
        dxf_code.append("70")
        dxf_code.append("6")
        dxf_code.append("0")
        dxf_code.append("LAYER")
        dxf_code.append("2")
        dxf_code.append("1")
        dxf_code.append("70")
        dxf_code.append("64")
        dxf_code.append("62")
        dxf_code.append("7")
        dxf_code.append("6")
        dxf_code.append("CONTINUOUS")
        dxf_code.append("0")
        dxf_code.append("LAYER")
        dxf_code.append("2")
        dxf_code.append("2")
        dxf_code.append("70")
        dxf_code.append("64")
        dxf_code.append("62")
        dxf_code.append("7")
        dxf_code.append("6")
        dxf_code.append("CONTINUOUS")
        dxf_code.append("0")
        dxf_code.append("ENDTAB")
        dxf_code.append("0")
        dxf_code.append("TABLE")
        dxf_code.append("2")
        dxf_code.append("STYLE")
        dxf_code.append("70")
        dxf_code.append("0")
        dxf_code.append("0")
        dxf_code.append("ENDTAB")
        dxf_code.append("0")
        dxf_code.append("ENDSEC")
        
        #This block section is not necessary but apperantly it's good form to include one anyway.
        #The following is an empty block section.
        dxf_code.append("0")
        dxf_code.append("SECTION")
        dxf_code.append("2")
        dxf_code.append("BLOCKS")
        dxf_code.append("0")
        dxf_code.append("ENDSEC")

        # Start entities section
        dxf_code.append("0")
        dxf_code.append("SECTION")
        dxf_code.append("2")
        dxf_code.append("ENTITIES")
        dxf_code.append("  0")

        #################################
        ## GCODE WRITING for Dxf_Write ##
        #################################
        #for line in side:
        for line in self.model.coords:
            XY = line
            
            #if line[0] == 1 or (line[0] == 0 and Rapids):
            dxf_code.append("LINE")
            dxf_code.append("  5")
            dxf_code.append("30")
            dxf_code.append("100")
            dxf_code.append("AcDbEntity")
            dxf_code.append("  8") #layer Code #dxf_code.append("0")

            ##########################
            #if line[0] == 1:
            #    dxf_code.append("1")
            #else:
            #    dxf_code.append("2")    
            #dxf_code.append(" 62") #color code
            #if line[0] == 1:
            #    dxf_code.append("10")
            #else:
            #    dxf_code.append("150")
            dxf_code.append("1")
            dxf_code.append(" 62") #color code
            dxf_code.append("150")
            ###########################
            
            dxf_code.append("100")
            dxf_code.append("AcDbLine")
            dxf_code.append(" 10")
            dxf_code.append("%.4f" %(line[0])) #x1 coord
            dxf_code.append(" 20")
            dxf_code.append("%.4f" %(line[1])) #y1 coord
            dxf_code.append(" 30")
            dxf_code.append("%.4f" %(0))       #z1 coord
            dxf_code.append(" 11")
            dxf_code.append("%.4f" %(line[2])) #x2 coord
            dxf_code.append(" 21")
            dxf_code.append("%.4f" %(line[3])) #y2 coord
            dxf_code.append(" 31")
            dxf_code.append("%.4f" %(0))       #z2 coord
            dxf_code.append("  0")

        dxf_code.append("ENDSEC")
        dxf_code.append("0")
        dxf_code.append("EOF")
        ######################################
        ## END G-CODE WRITING for Dxf_Write ##
        ######################################
        return dxf_code


    def CopyClipboard_GCode(self):
        self.clipboard_clear()
        if self.Check_All_Variables() > 0:
            return
        #self.write_gcode()
        self.coords = self.model.coords
        self.gcode = engrave_gcode(self)
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def CopyClipboard_SVG(self):
        self.clipboard_clear()
        self.WriteSVG()
        for line in self.svgcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        if self.Check_All_Variables() > 0:
            return
        self.coords = self.model.coords
        self.gcode = engrave_gcode(self)
        for line in self.gcode:
            try:
                sys.stdout.write(line+'\n')
            except:
                pass
        self.Quit_Click(None)

    def Quit_Click(self, event):
        self.statusMessage.set("Exiting!")
        self.master.destroy()

    def ZOOM_ITEMS(self,x0,y0,z_factor):
        all = self.PreviewCanvas.find_all()
        for i in all:
            self.PreviewCanvas.scale(i, x0, y0, z_factor, z_factor)
            w=self.PreviewCanvas.itemcget(i,"width")
            self.PreviewCanvas.itemconfig(i, width=float(w)*z_factor)
        self.PreviewCanvas.update_idletasks()

    def ZOOM(self,z_inc):
        all = self.PreviewCanvas.find_all()
        x = int(self.PreviewCanvas.cget("width" ))/2.0
        y = int(self.PreviewCanvas.cget("height"))/2.0
        for i in all:
            self.PreviewCanvas.scale(i, x, y, z_inc, z_inc)
            w=self.PreviewCanvas.itemcget(i,"width")
            self.PreviewCanvas.itemconfig(i, width=float(w)*z_inc)
        self.PreviewCanvas.update_idletasks()

    def menu_View_Zoom_in(self):
        x = int(self.PreviewCanvas.cget("width" ))/2.0
        y = int(self.PreviewCanvas.cget("height"))/2.0
        self.ZOOM_ITEMS(x, y, 2.0)

    def menu_View_Zoom_out(self):
        x = int(self.PreviewCanvas.cget("width" ))/2.0
        y = int(self.PreviewCanvas.cget("height"))/2.0
        self.ZOOM_ITEMS(x, y, 0.5)

    def _mouseZoomIn(self,event):
        self.ZOOM_ITEMS(event.x, event.y, 1.25)

    def _mouseZoomOut(self,event):
        self.ZOOM_ITEMS(event.x, event.y, 0.75)

    def mouseZoomStart(self,event):
        self.zoomx0 = event.x
        self.zoomy = event.y
        self.zoomy0 = event.y

    def mouseZoom(self,event):
        dy = event.y-self.zoomy
        if dy < 0.0:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 1.15)
        else:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 0.85)
        self.lasty = self.lasty + dy
        self.zoomy = event.y

    def mousePanStart(self,event):
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
        if self.input_type.get() == "text":
            self.font = readers.readFontFile(self.settings)
        else:
            self.font = readers.read_image_file(self.settings)
        self.do_it()
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def VCARVE_Recalculate_Click(self):
        win_id = self.grab_current()
        self.V_Carve_Calc_Click()
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def CLEAN_Recalculate_Click(self):
        TSTART = time()
        win_id = self.grab_current()
        if self.model.clean_segment == []:
            mess = "Calculate V-Carve must be executed\n"
            mess = mess + "prior to Calculating Cleanup"
            message_box("Cleanup Info", mess)
        else:
            stop = self.Clean_Calc_Click("straight")
            if stop != 1:
                self.Clean_Calc_Click("v-bit")
            self.plot_data()

        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass
        # print "time for cleanup calculations: ",time()-TSTART

    def Write_Clean_Click(self):
        win_id = self.grab_current()
        if (self.clean_P.get() +
            self.clean_X.get() +
            self.clean_Y.get() +
            self.v_clean_P.get() +
            self.v_clean_Y.get() +
            self.v_clean_X.get()) != 0:
            if self.model.clean_coords_sort == []:
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
        if (self.clean_P.get() +
            self.clean_X.get() +
            self.clean_Y.get() +
            self.v_clean_P.get() +
            self.v_clean_Y.get() +
            self.v_clean_X.get()) != 0:
            if self.model.v_clean_coords_sort == []:
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
        STOP_CALC = True
        self.model.stop_calc()

    def calc_vbit_dia(self):
        bit_dia = float(self.v_bit_dia.get())
        depth_lim = float(self.v_depth_lim.get())
        half_angle = radians(float(self.v_bit_angle.get()) / 2.0)

        if self.inlay.get() and (self.bit_shape.get() == "VBIT"):
            allowance = float(self.allowance.get())
            bit_dia = -2 * allowance * tan(half_angle)
            bit_dia = max(bit_dia, 0.001)
            return bit_dia

        if depth_lim < 0.0:
            if self.bit_shape.get() == "VBIT":
                bit_dia = -2 * depth_lim * tan(half_angle)
            elif self.bit_shape.get() == "BALL":
                R = bit_dia / 2.0
                if depth_lim > -R:
                    bit_dia = 2 * sqrt(R ** 2 - (R + depth_lim) ** 2)
                else:
                    bit_dia = float(self.v_bit_dia.get())
            elif self.bit_shape.get() == "FLAT":
                R = bit_dia / 2.0
            else:
                pass
        return bit_dia

    def calc_depth_limit(self):
        try:
            if self.bit_shape.get() == "VBIT":
                half_angle = radians(float(self.v_bit_angle.get()) / 2.0)
                bit_depth = -float(self.v_bit_dia.get()) / 2.0 / tan(half_angle)
            elif self.bit_shape.get() == "BALL":
                bit_depth = -float(self.v_bit_dia.get()) / 2.0
            elif self.bit_shape.get() == "FLAT":
                bit_depth = -float(self.v_bit_dia.get()) / 2.0
            else:
                pass

            depth_lim = float(self.v_depth_lim.get())
            if self.bit_shape.get() != "FLAT":
                if depth_lim < 0.0:
                    self.maxcut.set("%.3f" % (max(bit_depth, depth_lim)))
                else:
                    self.maxcut.set("%.3f" % (bit_depth))
            else:
                if depth_lim < 0.0:
                    self.maxcut.set("%.3f" % (depth_lim))
                else:
                    self.maxcut.set("%.3f" % (bit_depth))
        except:
            self.maxcut.set("error")

    def calc_r_inlay_top(self):
        half_angle = radians(float(self.v_bit_angle.get()) / 2.0)
        inlay_depth = self.calc_r_inlay_depth()
        r_inlay_top = tan(half_angle) * inlay_depth
        return r_inlay_top

    def calc_r_inlay_depth(self):
        inlay_depth = float(self.maxcut.get())
        return inlay_depth

    ###############
    # Left Column #
    ###############
    def Entry_Yscale_Check(self):
        try:
            value = float(self.YSCALE.get())
            if value <= 0.0:
                self.statusMessage.set(" Height should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Yscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check())
        self.settings.set('yscale', self.YSCALE.get())

    def Entry_Xscale_Check(self):
        try:
            value = float(self.XSCALE.get())
            if value <= 0.0:
                self.statusMessage.set(" Width should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Xscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check())
        self.settings.set('xscale', self.XSCALE.get())

    def Entry_Sthick_Check(self):
        try:
            value = float(self.STHICK.get())
            if value < 0.0:
                self.statusMessage.set(" Thickness should be greater than 0 ")
                return 2  # Value is invalid number
        except:
            return 3  # Value not a number
        return 0  # Value is a valid number

    def Entry_Sthick_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check())
        self.settings.set('line_thickness', self.STHICK.get())

    def Entry_Lspace_Check(self):
        try:
            value = float(self.LSPACE.get())
            if value < 0.0:
                self.statusMessage.set(" Line space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Lspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check())
        self.settings.set('line_space', self.LSPACE.get())

    def Entry_Cspace_Check(self):
        try:
            value = float(self.CSPACE.get())
            if value < 0.0:
                self.statusMessage.set(" Character space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Cspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check())
        self.settings.set('char_space', self.CSPACE.get())

    def Entry_Wspace_Check(self):
        try:
            value = float(self.WSPACE.get())
            if value < 0.0:
                self.statusMessage.set(" Word space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Wspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check())
        self.settings.set('word_space', self.WSPACE.get())

    def Entry_Tangle_Check(self):
        try:
            value = float(self.TANGLE.get())
            if value <= -360.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between -360 and 360 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Tangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check())
        self.settings.set('text_angle', self.TANGLE.get())

    def Entry_Tradius_Check(self):
        try:
            value = float(self.TRADIUS.get())
            if value < 0.0:
                self.statusMessage.set(" Radius should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Tradius_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check())
        self.settings.set('text_radius', self.TRADIUS.get())

    ################
    # Right Column #
    ################
    def Entry_Feed_Check(self):
        try:
            value = float(self.FEED.get())
            if value <= 0.0:
                self.statusMessage.set(" Feed should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Feed_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Feed, self.Entry_Feed_Check())
        self.settings.set('feedrate', self.FEED.get())

    def Entry_Plunge_Check(self):
        try:
            value = float(self.PLUNGE.get())
            if value < 0.0:
                self.statusMessage.set(" Plunge rate should be greater than or equal to 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Plunge_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check())
        self.settings.set('plunge_rate', self.PLUNGE.get())

    def Entry_Zsafe_Check(self):
        try:
            value = float(self.ZSAFE.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Zsafe_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check())
        self.settings.set('zsafe', self.ZSAFE.get())

    def Entry_Zcut_Check(self):
        try:
            value = float(self.ZCUT.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Zcut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check())
        self.settings.set('zcut', self.ZCUT.get())

    ######################################
    #    Settings Window Call Backs      #
    ######################################
    def Entry_Xoffset_Check(self):
        try:
            value = float(self.xorigin.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Xoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check())
        #TODO settings

    def Entry_Yoffset_Check(self):
        try:
            value = float(self.yorigin.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Yoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check())

    def Entry_ArcAngle_Check(self):
        try:
            value = float(self.segarc.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_ArcAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check())

    def Entry_Accuracy_Check(self):
        try:
            value = float(self.accuracy.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Accuracy_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check())

    def Entry_Gpre_Callback(self, varName, index, mode):
        self.settings.set('gcode_preamble', self.gpre.get())

    def Entry_Gpost_Callback(self, varName, index, mode):
        self.settings.set('gcode_postamble', self.gpost.get())

    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
            if value <= 0.0:
                self.statusMessage.set(" Gap should be greater than zero.")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_BoxGap_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check())
        try:
            if not bool(self.plotbox.get()):
                self.Label_BoxGap.configure(state="disabled")
                self.Entry_BoxGap.configure(state="disabled")
                self.Label_BoxGap_u.configure(state="disabled")
            else:
                self.Label_BoxGap.configure(state="normal")
                self.Entry_BoxGap.configure(state="normal")
                self.Label_BoxGap_u.configure(state="normal")
        except:
            pass

    def Entry_v_pplot_Callback(self, varName, index, mode):
        self.settings.set('v_pplot', self.v_pplot.get())

    def Entry_Box_Callback(self, varName, index, mode):
        try:
            self.Entry_BoxGap_Callback(varName, index, mode)
        except:
            pass
        self.Recalc_RQD()

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

    ######################################
    #    V-Carve Settings Call Backs     #
    ######################################
    def Entry_Vbitangle_Check(self):
        try:
            value = float(self.v_bit_angle.get())
            if value < 0.0 or value > 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_Vbitangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check() )
        #TODO settings
        self.calc_depth_limit()

    def Entry_Vbitdia_Check(self):
        try:
            value = float(self.v_bit_dia.get())
            if value <= 0.0:
                self.statusMessage.set(" Diameter should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Vbitdia_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check() )
        self.calc_depth_limit()

    def Entry_VDepthLimit_Check(self):
        try:
            value = float(self.v_depth_lim.get())
            if value > 0.0:
                self.statusMessage.set(" Depth should be less than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_VDepthLimit_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() )
        self.calc_depth_limit()

    def Entry_InsideAngle_Check(self):
        try:
            value = float(self.v_drv_corner.get())
            if value <= 0.0 or value >= 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_InsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() )

    def Entry_OutsideAngle_Check(self):
        try:
            value = float(self.v_step_corner.get())
            if value <= 180.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between 180 and 360 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_OutsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check() )

    def Entry_StepSize_Check(self):
        try:
            value = float(self.v_step_len.get())
            if value <= 0.0:
                self.statusMessage.set(" Step size should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_StepSize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check() )

    def Entry_Allowance_Check(self):
        try:
            value = float(self.allowance.get())
            if value > 0.0:
                self.statusMessage.set(" Allowance should be less than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_Allowance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check() )

    def Entry_Prismatic_Callback(self, varName, index, mode):
        try:
            if not bool(self.inlay.get()):
                self.Label_Allowance.configure(state="disabled")
                self.Entry_Allowance.configure(state="disabled")
                self.Label_Allowance_u.configure(state="disabled")
            else:
                self.Label_Allowance.configure(state="normal")
                self.Entry_Allowance.configure(state="normal")
                self.Label_Allowance_u.configure(state="normal")
        except:
            pass
        self.Recalc_RQD()
        
    def Entry_v_max_cut_Check(self):
        try:
            value = float(self.v_max_cut.get())
            if value >= 0.0:
                self.statusMessage.set(" Max Depth per Pass should be less than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc

    def Entry_v_max_cut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check() )

    def Entry_v_rough_stk_Check(self):
        try:
            value = float(self.v_rough_stk.get())
            if value < 0.0:
                self.statusMessage.set(" Finish Pass Stock should be positive or zero (Zero disables multi-pass)")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        try:
            if float(self.v_rough_stk.get()) == 0.0:
                self.Label_v_max_cut.configure(state="disabled")
                self.Label_v_max_cut_u.configure(state="disabled")
                self.Entry_v_max_cut.configure(state="disabled")
            else:
                self.Label_v_max_cut.configure(state="normal")
                self.Label_v_max_cut_u.configure(state="normal")
                self.Entry_v_max_cut.configure(state="normal")
        except:
            pass
        return 1         # Value is a valid number changes do not require recalc

    def Entry_v_rough_stk_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check() )

    def Entry_V_CLEAN_Check(self):
        try:
            value = float(self.clean_v.get())
            if value < 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_V_CLEAN_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check() )

    def Entry_CLEAN_DIA_Check(self):
        try:
            value = float(self.clean_dia.get())
            if value <= 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_CLEAN_DIA_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check() )
        self.model.clean_coords=[]
        self.model.v_clean_coords=[]

    def Entry_STEP_OVER_Check(self):
        try:
            value = float(self.clean_step.get())
            if value <= 0.0:
                self.statusMessage.set(" Step Over should be between 0% and 100% ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_STEP_OVER_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check() )

    def Entry_Bit_Shape_Check(self):
        self.calc_depth_limit()

        try:
            if   self.bit_shape.get() == "VBIT":
                self.Label_Vbitangle.configure(state="normal")
                self.Label_Vbitangle_u.configure(state="normal")
                self.Entry_Vbitangle.configure(state="normal")
                self.Label_photo.configure(state="normal")
                self.Label_Vbitdia.configure(text="V-Bit Diameter")
            elif self.bit_shape.get() == "BALL":
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_Vbitdia.configure(text="Ball Nose Bit Diameter")
            elif self.bit_shape.get() == "FLAT":
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_Vbitdia.configure(text="Straight Bit Diameter")
            else:
                pass
        except:
            pass

    def Entry_Bit_Shape_var_Callback(self, varName, index, mode):
        self.Entry_Bit_Shape_Check()

    ######################################
    # Bitmap Settings Window Call Backs  #
    ######################################
    def Entry_BMPturdsize_Check(self):
        try:
            value = float(self.bmp_turdsize.get())
            if value < 1.0:
                self.statusMessage.set(" Step size should be greater or equal to 1.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_BMPturdsize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check() )
        #TODO settings

    def Entry_BMPalphamax_Check(self):
        try:
            value = float(self.bmp_alphamax.get())
            if value < 0.0 or value > 4.0/3.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_BMPalphamax_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check() )

    def Entry_BMPoptTolerance_Check(self):
        try:
            value = float(self.bmp_opttolerance.get())
            if value < 0.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_BMPoptTolerance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check() )

    def Check_All_Variables(self):

        if self.batch.get():
            return 0

        MAIN_error_cnt= \
        self.entry_set(self.Entry_Yscale,  self.Entry_Yscale_Check()  , 2) +\
        self.entry_set(self.Entry_Xscale,  self.Entry_Xscale_Check()  , 2) +\
        self.entry_set(self.Entry_Sthick,  self.Entry_Sthick_Check()  , 2) +\
        self.entry_set(self.Entry_Lspace,  self.Entry_Lspace_Check()  , 2) +\
        self.entry_set(self.Entry_Cspace,  self.Entry_Cspace_Check()  , 2) +\
        self.entry_set(self.Entry_Wspace,  self.Entry_Wspace_Check()  , 2) +\
        self.entry_set(self.Entry_Tangle,  self.Entry_Tangle_Check()  , 2) +\
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() , 2) +\
        self.entry_set(self.Entry_Feed,    self.Entry_Feed_Check()    , 2) +\
        self.entry_set(self.Entry_Plunge,  self.Entry_Plunge_Check()  , 2) +\
        self.entry_set(self.Entry_Zsafe,   self.Entry_Zsafe_Check()   , 2) +\
        self.entry_set(self.Entry_Zcut,    self.Entry_Zcut_Check()    , 2)

        GEN_error_cnt= \
        self.entry_set(self.Entry_Xoffset,  self.Entry_Xoffset_Check() , 2) +\
        self.entry_set(self.Entry_Yoffset,  self.Entry_Yoffset_Check() , 2) +\
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2) +\
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2) +\
        self.entry_set(self.Entry_BoxGap,   self.Entry_BoxGap_Check()  , 2) +\
        self.entry_set(self.Entry_Xoffset,  self.Entry_Xoffset_Check() , 2) +\
        self.entry_set(self.Entry_Yoffset,  self.Entry_Yoffset_Check() , 2) +\
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2) +\
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2) +\
        self.entry_set(self.Entry_BoxGap,   self.Entry_BoxGap_Check()  , 2)

        VCARVE_error_cnt= \
        self.entry_set(self.Entry_Vbitangle,    self.Entry_Vbitangle_Check()   , 2) +\
        self.entry_set(self.Entry_Vbitdia,      self.Entry_Vbitdia_Check()     , 2) +\
        self.entry_set(self.Entry_InsideAngle,  self.Entry_InsideAngle_Check() , 2) +\
        self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check(), 2) +\
        self.entry_set(self.Entry_StepSize,     self.Entry_StepSize_Check()    , 2) +\
        self.entry_set(self.Entry_CLEAN_DIA,    self.Entry_CLEAN_DIA_Check()   , 2) +\
        self.entry_set(self.Entry_STEP_OVER,    self.Entry_STEP_OVER_Check()   , 2) +\
        self.entry_set(self.Entry_Allowance,    self.Entry_Allowance_Check()   , 2) +\
        self.entry_set(self.Entry_VDepthLimit,  self.Entry_VDepthLimit_Check() , 2)

        PBM_error_cnt= \
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2) +\
        self.entry_set(self.Entry_BMPturdsize,     self.Entry_BMPturdsize_Check()    , 2) +\
        self.entry_set(self.Entry_BMPalphamax,     self.Entry_BMPalphamax_Check()    , 2)

        ERROR_cnt = MAIN_error_cnt + GEN_error_cnt + VCARVE_error_cnt +PBM_error_cnt

        if ERROR_cnt > 0:
            self.statusbar.configure( bg='red' )
        if PBM_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in PBM Settings Window ")
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

    def Clean_Calc_Click(self,bit_type="straight"):

        if self.Check_All_Variables() > 0:
            return 1

        if self.clean_coords == []:
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

            clean_cut = 1
            self.v_carve_it(clean_cut)
            vcalc_status.grab_release()
            try:
                vcalc_status.destroy()
            except:
                pass

        self._clean_path_calc(bit_type)

        if self.clean_coords == []:
            return 1
        else:
            return 0

    ######################################
    #    General Settings Call Backs     #
    ######################################
    def Entry_recalc_var_Callback(self, varName, index, mode):
        self.Recalc_RQD()

    def Entry_units_var_Callback(self):
        if self.units.get() == 'in' and self.funits.get() == 'mm/min':
            self.Scale_Linear_Inputs(1 / 25.4)
            self.funits.set('in/min')
        elif self.units.get() == 'mm' and self.funits.get() == 'in/min':
            self.Scale_Linear_Inputs(25.4)
            self.funits.set('mm/min')
        self.Recalc_RQD()

    def Scale_Linear_Inputs(self, factor=1.0):
        try:
            self.YSCALE.set(     '%.3g' %(float(self.YSCALE.get()     )*factor) )
            self.TRADIUS.set(    '%.3g' %(float(self.TRADIUS.get()    )*factor) )
            self.ZSAFE.set(      '%.3g' %(float(self.ZSAFE.get()      )*factor) )
            self.ZCUT.set(       '%.3g' %(float(self.ZCUT.get()       )*factor) )
            self.STHICK.set(     '%.3g' %(float(self.STHICK.get()     )*factor) )
            self.FEED.set(       '%.3g' %(float(self.FEED.get()       )*factor) )
            self.PLUNGE.set(     '%.3g' %(float(self.PLUNGE.get()     )*factor) )
            self.boxgap.set(     '%.3g' %(float(self.boxgap.get()     )*factor) )
            self.v_bit_dia.set(  '%.3g' %(float(self.v_bit_dia.get()  )*factor) )
            self.v_depth_lim.set('%.3g' %(float(self.v_depth_lim.get())*factor) )
            self.v_step_len.set( '%.3g' %(float(self.v_step_len.get() )*factor) )
            self.allowance.set(  '%.3g' %(float(self.allowance.get()  )*factor) )
            self.v_max_cut.set(  '%.3g' %(float(self.v_max_cut.get()  )*factor) )
            self.v_rough_stk.set('%.3g' %(float(self.v_rough_stk.get())*factor) )
            self.xorigin.set(    '%.3g' %(float(self.xorigin.get()    )*factor) )
            self.yorigin.set(    '%.3g' %(float(self.yorigin.get()    )*factor) )
            self.accuracy.set(   '%.3g' %(float(self.accuracy.get()   )*factor) )
            self.clean_v.set(    '%.3g' %(float(self.clean_v.get()    )*factor) )
            self.clean_dia.set(  '%.3g' %(float(self.clean_dia.get()  )*factor) )
        except:
            pass

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

    def Entry_fontdir_Callback(self, varName, index, mode):
        self.Listbox_1.delete(0, END)
        self.Listbox_1.configure(bg=self.NormalColor)
        try:
            font_files = os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files = " "

        for name in font_files:
            if  str.find(name.upper(), '.CXF') != -1 \
            or (str.find(name.upper(), '.TTF') != -1 and TTF_AVAILABLE):
                self.Listbox_1.insert(END, name)
        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")

        self.settings.set('fontfile', self.fontfile.get())

        self.font = readers.readFontFile(self.settings)
        self.Recalc_RQD()

    # End General Settings Callbacks

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
            self.font = readers.read_image_file(self.settings)
            self.input_type.set(self.settings.get('input_type')) # input_type may have been changed by read_image_file
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

        text_codes=[]
        #file_full = self.fontdir.get() + "/" + self.fontfile.get()
        file_full = self.settings.get_fontfile()
        fileName, fileExtension = os.path.splitext(file_full)
        TYPE = fileExtension.upper()

        if TYPE != '.CXF' and TYPE != '.TTF' and TYPE != '':
            if os.path.isfile(file_full):
                self.input_type.set("image")

        if boxsize != "0":
            self.boxgap.set(float(boxsize) * float(self.STHICK.get()))

        if self.arc_fit.get() == "0":
            self.arc_fit.set("none")
        elif self.arc_fit.get() == "1":
            self.arc_fit.set("center")

        if self.arc_fit.get() != "none" \
            and self.arc_fit.get() != "center" \
            and self.arc_fit.get() != "radius":
            self.arc_fit.set("center")

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

        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.units.set('mm')
            self.funits.set('mm/min')

        self.calc_depth_limit()

        temp_name, fileExtension = os.path.splitext(filename)
        file_base = os.path.basename(temp_name)

        self.delay_calc = False
        if self.initComplete:
            self.NGC_FILE = filename
            self.menu_mode_change()

    def menu_File_Save_Settings_File(self):

        gcode = self.settings.to_gcode()

        # TODO use settings
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)

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

        if self.model.vcoords == [] and self.cut_type.get() == "v-carve":
            mess = "V-carve path data does not exist.  "
            mess = mess + "Only settings will be saved.\n\n"
            mess = mess + "To generate V-Carve path data Click on the"
            mess = mess + "\"Calculate V-Carve\" button on the main window."
            if not message_ask_ok_cancel("Continue", mess):
                return

        #self.write_gcode()
        self.coords = self.model.coords
        self.gcode = engrave_gcode(self)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)

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
                self.statusMessage.set("Unable to open file for writing: %s" % (filename))
                self.statusbar.configure(bg='red')
                return
            for line in self.gcode:
                try:
                    fout.write(line + '\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg='white')

    def menu_File_Save_clean_G_Code_File(self, bit_type="straight"):
        if self.Check_All_Variables() > 0:
            return

        self.WRITE_CLEAN_UP(bit_type)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)

        if self.input_type.get() != "text":
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
            for line in self.gcode:
                try:
                    fout.write(line + '\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg='white')

    def menu_File_Save_SVG_File(self):
        self.WriteSVG()

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)
        if self.input_type.get() != "text":
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
            for line in self.svgcode:
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

        DXF_CODE = self.WriteDXF(close_loops=close_loops)
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)
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
        if (not self.batch.get()) and self.initComplete and (not self.delay_calc):
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
        self.VCARVE_Settings_Window()

    def KEY_F4(self, event):
        self.PBM_Settings_Window()

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
            ###################################################
            #  Form changed Size (resized) adjust as required #
            ###################################################
            self.w = w
            self.h = h
            # canvas
            if self.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)

            if self.input_type.get() == "text":
                self.Label_font_prop.configure(text="Text Font Properties:")
                self.Label_Yscale.configure(text="Text Height")
                self.Label_Xscale.configure(text="Text Width")
                self.Label_pos_orient.configure(text="Text Position and Orientation:")
                self.Label_Tangle.configure(text="Text Angle")
                self.Label_flip.configure(text="Flip Text")
                self.Label_mirror.configure(text="Mirror Text")

                self.Label_useIMGsize.place_forget()
                self.Checkbutton_useIMGsize.place_forget()

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

                # Start Right Column
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

            else:
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

            ###########################################################
            if self.cut_type.get() == "v-carve":
                pass
            else:
                pass
            ###########################################################
            self.plot_data()


    #TODO move to geometry?
    def coord_scale(self, x, y, xscale, yscale):
        '''
        routine takes an x and a y scales are applied and returns new x,y tuple
        '''
        newx = x * xscale
        newy = y * yscale
        return newx, newy

    def plot_line(self, XX1, YY1, XX2, YY2, midx, midy, cszw, cszh, col, radius=0):
        x1 = cszw / 2 + (XX1 - midx) / self.plot_scale
        x2 = cszw / 2 + (XX2 - midx) / self.plot_scale
        y1 = cszh / 2 - (YY1 - midy) / self.plot_scale
        y2 = cszh / 2 - (YY2 - midy) / self.plot_scale
        if radius == 0:
            thick = 0
        else:
            thick = radius * 2 / self.plot_scale
        self.segID.append(self.PreviewCanvas.create_line(x1, y1, x2, y2, fill=col, capstyle="round", width=thick))

    def plot_circle(self, XX1, YY1, midx, midy, cszw, cszh, color, Rad, fill):
        dd = Rad
        x1 = cszw / 2 + (XX1 - dd - midx) / self.plot_scale
        x2 = cszw / 2 + (XX1 + dd - midx) / self.plot_scale
        y1 = cszh / 2 - (YY1 - dd - midy) / self.plot_scale
        y2 = cszh / 2 - (YY1 + dd - midy) / self.plot_scale
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


    def plot_data(self):
        '''
        Canvas plotting stuff
        '''
        if self.delay_calc:
            return

        self.master.update_idletasks()

        # erase old segs/display objects
        self.PreviewCanvas.delete(ALL)
        self.segID = []

        cszw = int(self.PreviewCanvas.cget("width"))
        cszh = int(self.PreviewCanvas.cget("height"))
        buff=10

        maxx = self.MAXX
        minx = self.MINX
        maxy = self.MAXY
        miny = self.MINY
        midx = (maxx+minx)/2
        midy = (maxy+miny)/2

        if self.cut_type.get() == "v-carve":
            Thick = 0.0
        else:
            Thick = float(self.STHICK.get())

        if self.input_type.get() == "text":
            Radius_in = float(self.TRADIUS.get())
        else:
            Radius_in = 0.0

        plot_scale = max((maxx-minx+Thick)/(cszw-buff), (maxy-miny+Thick)/(cszh-buff))
        if plot_scale <= 0:
            plot_scale = 1.0
        self.plot_scale = plot_scale

        Radius_plot = 0
        if self.plotbox.get() and self.cut_type.get() == "engrave":
            if Radius_in != 0:
                Radius_plot=  float(self.RADIUS_PLOT)

        x_lft = cszw/2 + (minx-midx) / plot_scale
        x_rgt = cszw/2 + (maxx-midx) / plot_scale
        y_bot = cszh/2 + (maxy-midy) / plot_scale
        y_top = cszh/2 + (miny-midy) / plot_scale

        if self.show_box.get() == True:
            self.segID.append(
                self.PreviewCanvas.create_rectangle(x_lft, y_bot, x_rgt, y_top, fill="gray80",
                                                    outline="gray80",
                                                    width=0))

        if Radius_in != 0:
            Rx_lft = cszw/2 + ( -Radius_in-midx)  / plot_scale
            Rx_rgt = cszw/2 + (  Radius_in-midx)  / plot_scale
            Ry_bot = cszh/2 + (  Radius_in+midy)  / plot_scale
            Ry_top = cszh/2 + ( -Radius_in+midy)  / plot_scale
            self.segID.append(
                self.PreviewCanvas.create_oval(Rx_lft, Ry_bot, Rx_rgt, Ry_top, outline="gray90", width=0, dash=3))

        if self.show_thick.get() == True:
            plot_width = Thick / plot_scale
        else:
            plot_width = 1.0

        x_zero = self.xzero
        y_zero = self.yzero
        
        # Plot circle radius with radius equal to Radius_plot
        if Radius_plot != 0:
            Rpx_lft = cszw/2 + ( -Radius_plot-midx - x_zero) / plot_scale
            Rpx_rgt = cszw/2 + (  Radius_plot-midx - x_zero)  / plot_scale
            Rpy_bot = cszh/2 + (  Radius_plot+midy + y_zero)  / plot_scale
            Rpy_top = cszh/2 + ( -Radius_plot+midy + y_zero)  / plot_scale
            self.segID.append(
                self.PreviewCanvas.create_oval(Rpx_lft, Rpy_bot, Rpx_rgt, Rpy_top, outline="black", width=plot_width))

        for line in self.model.coords:
            XY = line
            x1 =  cszw/2 + (XY[0]-midx) / plot_scale
            x2 =  cszw/2 + (XY[2]-midx) / plot_scale
            y1 =  cszh/2 - (XY[1]-midy) / plot_scale
            y2 =  cszh/2 - (XY[3]-midy) / plot_scale
            self.segID.append(
                self.PreviewCanvas.create_line(x1, y1, x2, y2, fill='black', width=plot_width, capstyle='round'))

        XOrigin = float(self.xorigin.get())
        YOrigin = float(self.yorigin.get())
        axis_length = (maxx-minx)/4
        axis_x1 = cszw/2 + (-midx + XOrigin)/plot_scale
        axis_x2 = cszw/2 + (axis_length - midx + XOrigin)/plot_scale
        axis_y1 = cszh/2 - (-midy + YOrigin)/plot_scale
        axis_y2 = cszh/2 - (axis_length - midy+YOrigin)/plot_scale

        #########################################
        # V-carve Plotting Stuff
        #########################################
        if self.cut_type.get() == "v-carve":
            loop_old = -1
            r_inlay_top = self.calc_r_inlay_top()

            for line in self.model.vcoords:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                color = "black"

                rbit = self.calc_vbit_dia()/2.0
                if self.bit_shape.get() == "FLAT":
                    if r >= rbit:
                        self.plot_circle(x1, y1, midx, midy, cszw, cszh, color, r, 1)
                else:
                    if self.inlay.get():
                        self.plot_circle(x1, y1, midx, midy, cszw, cszh, color, r-r_inlay_top, 1)
                    else:
                        self.plot_circle(x1, y1, midx, midy, cszw, cszh, color, r, 1)

            loop_old = -1
            rold = -1
            for line in self.model.vcoords:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                loop = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                plot_flat = False
                if self.bit_shape.get() == "FLAT":
                    if r == rold and r >= rbit:
                        plot_flat = True
                else:
                    plot_flat = True

                if loop == loop_old and plot_flat:
                    self.plot_line(xold, yold, x1, y1, midx, midy, cszw, cszh, color)
                loop_old = loop
                rold = r
                xold = x1
                yold = y1

        ########################################
        # Plot cleanup data
        ########################################
        if self.cut_type.get() == "v-carve":
            loop_old = -1
            for line in self.model.clean_coords_sort:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                loop = XY[3]
                color = "brown"
                if loop == loop_old:
                    self.plot_line(xold, yold, x1, y1, midx, midy, cszw, cszh, color, r)
                loop_old = loop
                xold = x1
                yold = y1

            loop_old = -1
            for line in self.model.clean_coords_sort:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                loop = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                if loop == loop_old:
                    self.plot_line(xold, yold, x1, y1, midx, midy, cszw, cszh, color)
                loop_old = loop
                xold = x1
                yold = y1

            loop_old = -1
            for line in self.model.v_clean_coords_sort:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                loop = XY[3]
                color = "yellow"
                if loop == loop_old:
                    self.plot_line(xold, yold, x1, y1, midx, midy, cszw, cszh, color)
                loop_old = loop
                xold = x1
                yold = y1

        #########################################
        # End V-carve Plotting Stuff
        #########################################

        if self.show_axis.get() == True:
            # Plot coordinate system origin
            self.segID.append( self.PreviewCanvas.create_line(axis_x1, axis_y1,
                                                                  axis_x2, axis_y1,
                                                                  fill='red', width=0))
            self.segID.append( self.PreviewCanvas.create_line(axis_x1, axis_y1,
                                                                  axis_x1, axis_y2,
                                                                  fill='green', width=0))

    def do_it(self):
        '''
        Perform  Calculations
        '''
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

        # erase old data
        self.segID = []
        self.gcode = []
        self.svgcode = []
        self.model.init_coords()

        self.RADIUS_PLOT = 0

        if (self.font is None or len(self.font) == 0) and (not self.batch.get()):
            self.statusbar.configure( bg='red' )
            if self.input_type.get() == "text":
                self.statusMessage.set("No Font Characters Loaded")
            else:
                self.statusMessage.set("No Image Loaded")
            return

        if self.input_type.get() == "text":
            if not self.batch.get():
                String = self.Input.get(1.0, END)
            else:
                String = self.default_text
            Radius_in = float(self.TRADIUS.get())
        else:
            String = "F"
            Radius_in = 0.0

        try:
            SegArc    = float(self.segarc.get())
            YScale_in = float(self.YSCALE.get() )
            CSpaceP   = float(self.CSPACE.get() )
            WSpaceP   = float(self.WSPACE.get() )
            LSpace    = float(self.LSPACE.get() )
            Angle     = float(self.TANGLE.get() )
            Thick     = float(self.STHICK.get() )
            XOrigin   = float(self.xorigin.get())
            YOrigin   = float(self.yorigin.get())
            v_flop    = bool(self.v_flop.get())
        except:
            self.statusMessage.set(" Unable to create paths.  Check Settings Entry Values.")
            self.statusbar.configure( bg='red' )
            return

        if self.cut_type.get() == "v-carve":
            Thick = 0.0

        line_maxx = []
        line_maxy = []
        line_maxa = []
        line_mina = []
        line_minx = []
        line_miny = []

        maxx_tmp = -99991.0
        maxy_tmp = -99992.0
        maxa_tmp = -99993.0
        mina_tmp =  99993.0
        miny_tmp =  99994.0
        minx_tmp =  99995.0

        font_word_space = 0
        INF = 1e10
        font_line_height = -INF
        font_char_width =  -INF
        font_used_height = -INF
        font_used_width  = -INF
        font_used_depth  =  INF

        ################################
        ##      Font Index Preview    ##
        ################################
        # if self.fontdex.get() == True:
        #     Radius_in = 0.0
        #     String = ""
        #     for key in self.font:
        #         if self.ext_char:
        #             String = String + unichr(key)
        #         elif int(key) < 256:
        #             String = String + unichr(key)
        #
        #     Strings = sorted(String)
        #     mcnt = 0
        #     String = ""
        #
        #     if self.ext_char.get():
        #         pcols = int(1.5 * sqrt(float(len(self.font))))
        #     else:
        #         pcols = 15
        #
        #     for char in Strings:
        #         mcnt += 1
        #         String += char
        #         if mcnt > pcols:
        #             String = String + '\n'
        #             mcnt = 0

        ##################################
        ## Font Height/Width Calculation #
        ##################################
        for char in String:
            try:
                font_used_height = max( self.font[ord(char)].get_ymax(), font_used_height )
                font_used_width = max( self.font[ord(char)].get_xmax(), font_used_width  )
                font_used_depth = min( self.font[ord(char)].get_ymin(), font_used_depth  )
            except:
                pass

        if self.H_CALC.get() == "max_all":
            font_line_height = max(self.font[key].get_ymax() for key in self.font)
            font_line_depth = min(self.font[key].get_ymin() for key in self.font)
        elif self.H_CALC.get() == "max_use":
            font_line_height = font_used_height
            font_line_depth = font_used_depth

        if font_line_height > -INF:
            if self.useIMGsize.get() and self.input_type.get() == "image":
                YScale = YScale_in / 100.0
            else:
                try:
                    YScale = (YScale_in - Thick) / (font_line_height - font_line_depth)
                except:
                    YScale = .1
                if YScale <= Zero:
                    YScale = .1
        else:
            if not self.batch.get(): self.statusbar.configure( bg='red' )
            if self.H_CALC.get() == "max_all":
                if not self.batch.get():
                    self.statusMessage.set("No Font Characters Found")
                else:
                    fmessage("(No Font Characters Found)")
            elif self.H_CALC.get() == "max_use":
                if self.input_type.get()=="image":
                    error_text = "Image contains no design information. (Empty DXF File)"
                else:
                    error_text = "Input Characters Were Not Found in the Current Font"
                    
                if not self.batch.get():
                    self.statusMessage.set(error_text)
                else:
                    fmessage( "("+error_text+")" )
            return

        font_char_width = self.font.get_character_width()
        font_word_space = font_char_width * (WSpaceP / 100.0)

        XScale = float(self.XSCALE.get()) * YScale / 100
        font_char_space = font_char_width * (CSpaceP / 100.0)

        if Radius_in != 0.0:
            if self.outer.get() == True:
                if self.upper.get() == True:
                    Radius = Radius_in + Thick/2 + YScale*(-font_line_depth)
                else:
                    Radius = -Radius_in - Thick/2 - YScale*(font_line_height)
            else:
                if self.upper.get() == True:
                    Radius = Radius_in - Thick/2 - YScale*(font_line_height)
                else:
                    Radius = -Radius_in + Thick/2 + YScale*(-font_line_depth)
        else:
            Radius = Radius_in

        font_line_space = (font_line_height - font_line_depth + Thick/YScale) * LSpace

        max_vals = []

        xposition = 0.0
        yposition = 0.0
        line_cnt = 0.0
        char_cnt = 0
        no_font_record = []
        message2 = ""
        for char in String:
            char_cnt += 1

            if char == ' ':
                xposition += font_word_space
                continue
            if char == '\t':
                xposition += 3 * font_word_space
                continue
            if char == '\n':
                xposition = 0
                yposition += font_line_space
                line_cnt = line_cnt + 1
                line_minx.append(minx_tmp)
                line_miny.append(miny_tmp)
                line_maxx.append(maxx_tmp)
                line_maxy.append(maxy_tmp)
                line_maxa.append(maxa_tmp)
                line_mina.append(mina_tmp)
                maxx_tmp = -99919.0
                maxy_tmp = -99929.0
                maxa_tmp = -99939.0
                mina_tmp = 99949.0
                miny_tmp = 99959.0
                minx_tmp = 99969.0
                continue

            first_stroke = True
            try:
                font_line_height = self.font[ord(char)].get_ymax()
            except:
                flag = 0
                for norec in no_font_record:
                    if norec == char:
                        flag = 1
                if flag == 0:
                    no_font_record.append(char)
                    message2 = ", CHECK OUTPUT! Some characters not found in font file."
                continue
                
            for stroke in self.font[ord(char)].stroke_list:
                x1 = stroke.xstart + xposition
                y1 = stroke.ystart - yposition
                x2 = stroke.xend + xposition
                y2 = stroke.yend - yposition

                # Perform scaling
                x1,y1 = self.coord_scale(x1,y1,XScale,YScale)
                x2,y2 = self.coord_scale(x2,y2,XScale,YScale)

                self.model.coords.append([x1, y1, x2, y2, line_cnt, char_cnt])

                maxx_tmp = max(maxx_tmp, x1, x2)
                minx_tmp = min(minx_tmp, x1, x2)
                miny_tmp = min(miny_tmp, y1, y2)
                maxy_tmp = max(maxy_tmp, y1, y2)

            char_width = self.font[ord(char)].get_xmax() # move over for next character
            xposition += font_char_space + char_width
        #END Char in String

        maxx = maxy = -99999.0
        miny = minx = 99999.0
        cnt=0

        for maxx_val in line_maxx:
            maxx = max( maxx, line_maxx[cnt] )
            minx = min( minx, line_minx[cnt] )
            miny = min( miny, line_miny[cnt] )
            maxy = max( maxy, line_maxy[cnt] )
            cnt += 1

        ##########################################
        #      TEXT LEFT JUSTIFY STUFF           #
        ##########################################
        if self.justify.get() == "Left":
            pass
            
        ##########################################
        #          TEXT CENTERING STUFF          #
        ##########################################
        if self.justify.get() == "Center":
            cnt=0
            for line in self.model.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    self.model.coords[cnt][0]=XY[0] + (maxx - line_maxx[line_num])/2
                    self.model.coords[cnt][2]=XY[2] + (maxx - line_maxx[line_num])/2
                except:
                    pass
                cnt += 1

        ##########################################
        #        TEXT RIGHT JUSTIFY STUFF        #
        ##########################################
        if self.justify.get() == "Right":
            for line in self.model.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    XY[0]=XY[0] + (maxx - line_maxx[line_num])
                    XY[2]=XY[2] + (maxx - line_maxx[line_num])
                except:
                    pass
                cnt += 1

        ##########################################
        #         TEXT ON RADIUS STUFF           #
        ##########################################
        mina = 99996.0
        maxa = -99993.0
        if Radius != 0.0:
            for line in self.model.coords:
                XY = line
                XY[0], XY[1], A1 = rotation(XY[0], XY[1], 0, Radius)
                XY[2], XY[3], A2 = rotation(XY[2], XY[3], 0, Radius)
                maxa = max(maxa, A1, A2)
                mina = min(mina, A1, A2)
            mida = (mina + maxa) / 2
            ##########################################
            #         TEXT LEFT JUSTIFY STUFF        #
            ##########################################
            if self.justify.get() == "Left":
                pass
            ##########################################
            #          TEXT CENTERING STUFF          #
            ##########################################
            if self.justify.get() == "Center":
                for line in self.model.coords:
                    XY = line
                    XY[0], XY[1] = transform(XY[0], XY[1], mida)
                    XY[2], XY[3] = transform(XY[2], XY[3], mida)
            ##########################################
            #        TEXT RIGHT JUSTIFY STUFF        #
            ##########################################
            if self.justify.get() == "Right":
                for line in self.model.coords:
                    XY = line
                    if self.upper.get() == True:
                        XY[0], XY[1] = transform(XY[0], XY[1], maxa)
                        XY[2], XY[3] = transform(XY[2], XY[3], maxa)
                    else:
                        XY[0], XY[1] = transform(XY[0], XY[1], mina)
                        XY[2], XY[3] = transform(XY[2], XY[3], mina)

        ##########################################
        #    TEXT FLIP / MIRROR STUFF / ANGLE    #
        ##########################################
        mirror_flag = self.mirror.get()
        flip_flag = self.flip.get()
            
        maxx = -99991.0
        maxy = -99992.0
        miny =  99994.0
        minx =  99995.0

        if Angle == 0.0:
            if flip_flag:
                miny = -font_line_height*YScale
            else:
                maxy = font_line_height*YScale
                
        elif Angle == 90.0 or Angle == -270.0:
            if not mirror_flag:
                minx = -font_line_height*YScale
            else:
                maxx = font_line_height*YScale

        elif Angle == 270.0 or Angle == -90.0:
            if not mirror_flag:
                maxx = font_line_height*YScale
            else:
                minx = -font_line_height*YScale

        elif Angle == 180.0 or Angle == -180.0:
            if flip_flag:
                maxy = font_line_height*YScale
            else:
                miny = -font_line_height*YScale

        maxr2 =  0.0

        for line in self.model.coords:
            XY = line
            if Angle != 0.0:
                XY[0], XY[1], A1 = rotation(XY[0], XY[1], Angle, 0)
                XY[2], XY[3], A2 = rotation(XY[2], XY[3], Angle, 0)

            if mirror_flag == True:
                XY[0] = -XY[0]
                XY[2] = -XY[2]
                v_flop = not(v_flop)

            if flip_flag == True:
                XY[1] = -XY[1]
                XY[3] = -XY[3]
                v_flop = not(v_flop)

            maxx = max(maxx, XY[0], XY[2])
            maxy = max(maxy, XY[1], XY[3])

            minx = min(minx, XY[0], XY[2])
            miny = min(miny, XY[1], XY[3])

            maxr2 = max(maxr2, float(XY[0]*XY[0]+XY[1]*XY[1]), float(XY[2]*XY[2]+XY[3]*XY[3]))

        maxx = maxx + Thick/2
        maxy = maxy + Thick/2
        minx = minx - Thick/2
        miny = miny - Thick/2

        midx = (minx+maxx)/2
        midy = (miny+maxy)/2

        #############################
        #   Engrave Box or circle   #
        #############################
        Delta = 0
        Radius_plot = 0
        Thick_Border = float(self.STHICK.get() )
        Delta = Thick/2 + float(self.boxgap.get())

        if self.plotbox.get(): #and self.cut_type.get() != "v-carve":

            if Radius_in == 0 or self.cut_type.get() == "v-carve":
                if bool(self.mirror.get()) ^ bool(self.flip.get()):
                    self.model.coords.append([ minx-Delta, miny-Delta, minx-Delta, maxy+Delta, 0, 0])
                    self.model.coords.append([ minx-Delta, maxy+Delta, maxx+Delta, maxy+Delta, 0, 0])
                    self.model.coords.append([ maxx+Delta, maxy+Delta, maxx+Delta, miny-Delta, 0, 0])
                    self.model.coords.append([ maxx+Delta, miny-Delta, minx-Delta, miny-Delta, 0, 0])
                else:
                    self.model.coords.append([ minx-Delta, miny-Delta, maxx+Delta, miny-Delta, 0, 0])
                    self.model.coords.append([ maxx+Delta, miny-Delta, maxx+Delta, maxy+Delta, 0, 0])
                    self.model.coords.append([ maxx+Delta, maxy+Delta, minx-Delta, maxy+Delta, 0, 0])
                    self.model.coords.append([ minx-Delta, maxy+Delta, minx-Delta, miny-Delta, 0, 0])
                
                if self.cut_type.get() != "v-carve":
                    Delta = Delta + Thick/2
                minx = minx - Delta
                maxx = maxx + Delta
                miny = miny - Delta
                maxy = maxy + Delta

            else:
                Radius_plot = sqrt(maxr2) + Thick + float(self.boxgap.get())
                minx = -Radius_plot - Thick/2
                maxx = -minx
                miny = minx
                maxy = maxx
                midx = 0
                midy = 0
                self.RADIUS_PLOT = Radius_plot
                # Don't create the circle coords here a g-code circle command
                # is generated later when not v-carving

        ##########################################
        #         ORIGIN LOCATING STUFF          #
        ##########################################
        CASE = str(self.origin.get())
        if   CASE == "Top-Left":
            x_zero = minx
            y_zero = maxy
        elif CASE == "Top-Center":
            x_zero = midx
            y_zero = maxy
        elif CASE == "Top-Right":
            x_zero = maxx
            y_zero = maxy
        elif CASE == "Mid-Left":
            x_zero = minx
            y_zero = midy
        elif CASE == "Mid-Center":
            x_zero = midx
            y_zero = midy
        elif CASE == "Mid-Right":
            x_zero = maxx
            y_zero = midy
        elif CASE == "Bot-Left":
            x_zero = minx
            y_zero = miny
        elif CASE == "Bot-Center":
            x_zero = midx
            y_zero = miny
        elif CASE == "Bot-Right":
            x_zero = maxx
            y_zero = miny
        elif CASE == "Arc-Center":
            x_zero = 0
            y_zero = 0
        else:          #"Default"
            x_zero = 0
            y_zero = 0

        cnt=0
        for line in self.model.coords:
            XY = line
            self.model.coords[cnt][0] = XY[0] - x_zero + XOrigin
            self.model.coords[cnt][1] = XY[1] - y_zero + YOrigin
            self.model.coords[cnt][2] = XY[2] - x_zero + XOrigin
            self.model.coords[cnt][3] = XY[3] - y_zero + YOrigin
            cnt += 1

        self.MAXX = maxx - x_zero + XOrigin
        self.MINX = minx - x_zero + XOrigin
        self.MAXY = maxy - y_zero + YOrigin
        self.MINY = miny - y_zero + YOrigin
        
        #TODO fix variables (crossing App and Model)
        self.model.setMaxX(self.MAXX)
        self.model.setMinX(self.MINX)
        self.model.setMaxY(self.MAXY)
        self.model.setMinY(self.MINY)

        self.xzero = x_zero
        self.yzero = y_zero

        if not self.batch.get():
            # Reset Status Bar and Entry Fields
            self.Input.configure( bg='white' )
            self.entry_set(self.Entry_Yscale,  self.Entry_Yscale_Check()  ,1)
            self.entry_set(self.Entry_Xscale,  self.Entry_Xscale_Check()  ,1)
            self.entry_set(self.Entry_Sthick,  self.Entry_Sthick_Check()  ,1)
            self.entry_set(self.Entry_Lspace,  self.Entry_Lspace_Check()  ,1)
            self.entry_set(self.Entry_Cspace,  self.Entry_Cspace_Check()  ,1)
            self.entry_set(self.Entry_Wspace,  self.Entry_Wspace_Check()  ,1)
            self.entry_set(self.Entry_Tangle,  self.Entry_Tangle_Check()  ,1)
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() ,1)
            self.entry_set(self.Entry_Feed,    self.Entry_Feed_Check()    ,1)
            self.entry_set(self.Entry_Plunge,  self.Entry_Plunge_Check()  ,1)
            self.entry_set(self.Entry_Zsafe,   self.Entry_Zsafe_Check()   ,1)
            self.entry_set(self.Entry_Zcut,    self.Entry_Zcut_Check()    ,1)
            self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,1)
            self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(),1)

            self.bounding_box.set("Bounding Box (WxH) = "    +
                                   "%.3g" % (maxx-minx)      +
                                   " %s " % self.units.get() +
                                   " x " +
                                   "%.3g" % (maxy-miny)      +
                                   " %s " % self.units.get() +
                                   " %s" % message2)
            self.statusMessage.set(self.bounding_box.get())

        if no_font_record != []:
            if not self.batch.get():
                self.statusbar.configure( bg='orange' )
            fmessage('Characters not found in font file:',FALSE)
            fmessage("(",FALSE)
            for entry in no_font_record:
                fmessage( "%s," %(entry),FALSE)
            fmessage(")")

        if not self.batch.get():
            self.plot_data()

    def get_flop_status(self, CLEAN_FLAG=False):
        v_flop = bool(self.v_flop.get())

        if self.input_type.get() == "text" and CLEAN_FLAG == False:
            if self.plotbox.get():
                v_flop = not(v_flop) 
            if self.mirror.get():
                v_flop = not(v_flop)
            if self.flip.get():
                v_flop = not(v_flop)
        return v_flop

    def v_carve_it(self, clean_flag=0, DXF_FLAG=False):

        self.master.unbind("<Configure>")
        self.STOP_CALC = False

        if self.units.get() == "mm":
            if float( self.v_step_len.get() ) < .01:
                self.v_step_len.set("0.01")
        else:
            if float( self.v_step_len.get() ) < .0005:
                self.v_step_len.set("0.0005")

        if self.Check_All_Variables() > 0:
            return
            
        if clean_flag != 1:
            self.do_it()
            self.model.init_clean_coords()

        elif self.model.clean_coords_sort != [] or self.model.v_clean_coords_sort != []:
            # If there is existing cleanup data clear the screen before computing
            self.model.init_clean_coords()
            self.plot_data()

        if not self.batch.get():
            self.statusbar.configure( bg='yellow' )
            self.statusMessage.set('Preparing for V-Carve Calculations')
            self.master.update()

        #########################################
        # V-Carve Stuff
        #########################################
        if self.cut_type.get() == "v-carve" and self.fontdex.get() == False:

            if not self.batch.get():
                cszw = int(self.PreviewCanvas.cget("width"))
                cszh = int(self.PreviewCanvas.cget("height"))
                if self.v_pplot.get() == 1:
                    self.plot_data()

            if (self.input_type.get() == "image" and clean_flag == 0):
                #self.model.coords = self.model.sort_for_v_carve(self.model.coords)
                self.model.sort_for_v_carve()

            if DXF_FLAG:
                return

            done = self.model.v_carve(self.get_flop_status(), clean_flag, DXF_FLAG)

            #Reset Entry Fields in V-Carve Settings
            if not self.batch.get():
                self.entry_set(self.Entry_Vbitangle,   self.Entry_Vbitangle_Check()   ,1)
                self.entry_set(self.Entry_Vbitdia,     self.Entry_Vbitdia_Check()     ,1)
                self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() ,1)
                self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() ,1)
                self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check(),1)
                self.entry_set(self.Entry_StepSize,    self.Entry_StepSize_Check()    ,1)
                self.entry_set(self.Entry_Allowance,   self.Entry_Allowance_Check()   ,1)
                self.entry_set(self.Entry_Accuracy,    self.Entry_Accuracy_Check()    ,1)
                self.entry_set(self.Entry_CLEAN_DIA,   self.Entry_CLEAN_DIA_Check()   ,1)
                self.entry_set(self.Entry_STEP_OVER,   self.Entry_STEP_OVER_Check()   ,1)
                self.entry_set(self.Entry_V_CLEAN,     self.Entry_V_CLEAN_Check()     ,1)

            if done and (not self.batch.get()):
                self.statusMessage.set('Done -- ' + self.bounding_box.get())
                self.statusbar.configure( bg='white' )
                
        self.master.bind("<Configure>", self.Master_Configure)

    ################################################################################
    #                         Bitmap Settings Window                              #
    ################################################################################
    #Algorithm options:
    # -z, --turnpolicy policy    - how to resolve ambiguities in path decomposition
    # -t, --turdsize n           - suppress speckles of up to this size (default 2)
    # -a, --alphama n           - corner threshold parameter (default 1)
    # -n, --longcurve            - turn off curve optimization
    # -O, --opttolerance n       - curve optimization tolerance (default 0.2)
    def PBM_Settings_Window(self):
        pbm_settings = Toplevel(width=525, height=250)
        pbm_settings.grab_set() # Use grab_set to prevent user input in the main window during calculations
        pbm_settings.resizable(0,0)
        pbm_settings.title('Bitmap Settings')
        pbm_settings.iconname("Bitmap Settings")

        D_Yloc = 12
        D_dY = 24
        xd_label_L = 12

        w_label = 100
        w_entry = 60
        w_units = 35
        xd_entry_L = xd_label_L+w_label+10
        xd_units_L = xd_entry_L+w_entry+5

        D_Yloc = D_Yloc+D_dY
        self.Label_BMPturnpol = Label(pbm_settings, text="Turn Policy")
        self.Label_BMPturnpol.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.BMPturnpol_OptionMenu = OptionMenu(pbm_settings, self.bmp_turnpol,
                                                    "black",
                                                    "white",
                                                    "right",
                                                     "left",
                                                     "minority",
                                                     "majority",
                                                     "random")
        self.BMPturnpol_OptionMenu.place(x=xd_entry_L, y=D_Yloc, width=w_entry+40, height=23)

        D_Yloc = D_Yloc+D_dY
        self.Label_BMPturdsize = Label(pbm_settings, text="Turd Size")
        self.Label_BMPturdsize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPturdsize = Entry(pbm_settings, width="15")
        self.Entry_BMPturdsize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPturdsize.configure(textvariable=self.bmp_turdsize)
        self.bmp_turdsize.trace_variable("w", self.Entry_BMPturdsize_Callback)
        self.Label_BMPturdsize2 = Label(pbm_settings, text="Suppress speckles of up to this pixel size")
        self.Label_BMPturdsize2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 2)

        D_Yloc = D_Yloc+D_dY+5
        self.Label_BMPalphamax = Label(pbm_settings, text="Alpha Max")
        self.Label_BMPalphamax.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPalphamax = Entry(pbm_settings, width="15")
        self.Entry_BMPalphamax.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPalphamax.configure(textvariable=self.bmp_alphamax)
        self.bmp_alphamax.trace_variable("w", self.Entry_BMPalphamax_Callback)
        self.Label_BMPalphamax2 = Label(pbm_settings, text="0.0 = sharp corners, 1.33 = smoothed corners")
        self.Label_BMPalphamax2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 2)

        D_Yloc = D_Yloc+D_dY
        self.Label_BMP_longcurve = Label(pbm_settings, text="Long Curve")
        self.Label_BMP_longcurve.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_BMP_longcurve = Checkbutton(pbm_settings, text="", anchor=W)
        self.Checkbutton_BMP_longcurve.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_BMP_longcurve.configure(variable=self.bmp_longcurve)
        self.Label_BMP_longcurve2 = Label(pbm_settings, text="Enable Curve Optimization")
        self.Label_BMP_longcurve2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)

        D_Yloc = D_Yloc+D_dY
        self.Label_BMPoptTolerance = Label(pbm_settings, text="Opt Tolerance")
        self.Label_BMPoptTolerance.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPoptTolerance = Entry(pbm_settings, width="15")
        self.Entry_BMPoptTolerance.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPoptTolerance.configure(textvariable=self.bmp_opttolerance)
        self.bmp_opttolerance.trace_variable("w", self.Entry_BMPoptTolerance_Callback)
        self.Label_BMPoptTolerance2 = Label(pbm_settings, text="Curve Optimization Tolerance")
        self.Label_BMPoptTolerance2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2)

        pbm_settings.update_idletasks()
        Ybut=int(pbm_settings.winfo_height())-30
        Xbut=int(pbm_settings.winfo_width()/2)

        self.PBM_Reload = Button(pbm_settings, text="Re-Load Image")
        self.PBM_Reload.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")
        self.PBM_Reload.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.PBM_Close = Button(pbm_settings, text="Close",command=self.Close_Current_Window_Click)
        self.PBM_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")

        try:
            pbm_settings.iconbitmap(bitmap="@emblem64")
        except:
            try: #Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                pbm_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

    ################################################################################
    #                         General Settings Window                              #
    ################################################################################
    def GEN_Settings_Window(self):
        gen_settings = Toplevel(width=600, height=500)
        gen_settings.grab_set()  # Use grab_set to prevent user input in the main window during calculations
        gen_settings.resizable(0, 0)
        gen_settings.title('Settings')
        gen_settings.iconname("Settings")

        try:
            gen_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                gen_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        D_Yloc = 6
        D_dY = 24
        xd_label_L = 12

        dlta = 40
        w_label = 110 + 25 + dlta
        w_entry = 60
        w_units = 35
        xd_entry_L = xd_label_L + w_label + 10 + dlta
        xd_units_L = xd_entry_L + w_entry + 5
        x_radio_offset = 62

        # Radio Button
        D_Yloc = D_Yloc + D_dY
        self.Label_Units = Label(gen_settings, text="Units")
        self.Label_Units.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Radio_Units_IN = Radiobutton(gen_settings, text="inch", value="in", width="100", anchor=W)
        self.Radio_Units_IN.place(x=w_label + x_radio_offset, y=D_Yloc, width=75, height=23)
        self.Radio_Units_IN.configure(variable=self.units, command=self.Entry_units_var_Callback)

        self.Radio_Units_MM = Radiobutton(gen_settings, text="mm", value="mm", width="100", anchor=W)
        self.Radio_Units_MM.place(x=w_label + x_radio_offset + 60, y=D_Yloc, width=75, height=23)
        self.Radio_Units_MM.configure(variable=self.units, command=self.Entry_units_var_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_Xoffset = Label(gen_settings, text="X Offset")
        self.Label_Xoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Xoffset_u = Label(gen_settings, textvariable=self.units, anchor=W)
        self.Label_Xoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Xoffset = Entry(gen_settings, width="15")
        self.Entry_Xoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Xoffset.configure(textvariable=self.xorigin)
        self.xorigin.trace_variable("w", self.Entry_Xoffset_Callback)
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Yoffset = Label(gen_settings, text="Y Offset")
        self.Label_Yoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Yoffset_u = Label(gen_settings, textvariable=self.units, anchor=W)
        self.Label_Yoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Yoffset = Entry(gen_settings, width="15")
        self.Entry_Yoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Yoffset.configure(textvariable=self.yorigin)
        self.yorigin.trace_variable("w", self.Entry_Yoffset_Callback)
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_ArcAngle = Label(gen_settings, text="Arc Angle")
        self.Label_ArcAngle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_ArcAngle_u = Label(gen_settings, text="deg", anchor=W)
        self.Label_ArcAngle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_ArcAngle = Entry(gen_settings, width="15")
        self.Entry_ArcAngle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_ArcAngle.configure(textvariable=self.segarc)
        self.segarc.trace_variable("w", self.Entry_ArcAngle_Callback)
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Accuracy = Label(gen_settings, text="Accuracy")
        self.Label_Accuracy.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Accuracy_u = Label(gen_settings, textvariable=self.units, anchor=W)
        self.Label_Accuracy_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Accuracy = Entry(gen_settings, width="15")
        self.Entry_Accuracy.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Accuracy.configure(textvariable=self.accuracy)
        self.accuracy.trace_variable("w", self.Entry_Accuracy_Callback)
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_ext_char = Label(gen_settings, text="Extended Characters")
        self.Label_ext_char.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_ext_char = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_ext_char.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_ext_char.configure(variable=self.ext_char)
        self.ext_char.trace_variable("w", self.Settings_ReLoad_Click)

        D_Yloc = D_Yloc + D_dY
        self.Label_arcfit = Label(gen_settings, text="Arc Fitting")
        self.Label_arcfit.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_arcfit_none = Radiobutton(gen_settings, text="None", \
                                             value="none", width="110", anchor=W)
        self.Radio_arcfit_none.place(x=w_label + x_radio_offset, y=D_Yloc, width=90, height=23)
        self.Radio_arcfit_none.configure(variable=self.arc_fit)
        self.Radio_arcfit_radius = Radiobutton(gen_settings, text="Radius Format", \
                                               value="radius", width="110", anchor=W)
        self.Radio_arcfit_radius.place(x=w_label + x_radio_offset + 65, y=D_Yloc, width=100, height=23)
        self.Radio_arcfit_radius.configure(variable=self.arc_fit)
        self.Radio_arcfit_center = Radiobutton(gen_settings, text="Center Format", \
                                               value="center", width="110", anchor=W)
        self.Radio_arcfit_center.place(x=w_label + x_radio_offset + 65 + 115, y=D_Yloc, width=100, height=23)
        self.Radio_arcfit_center.configure(variable=self.arc_fit)

        D_Yloc = D_Yloc + D_dY
        self.Label_no_com = Label(gen_settings, text="Suppress Comments")
        self.Label_no_com.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_no_com = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_no_com.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_no_com.configure(variable=self.no_comments)

        D_Yloc = D_Yloc + D_dY
        self.Label_Gpre = Label(gen_settings, text="G Code Header")
        self.Label_Gpre.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpre = Entry(gen_settings, width="15")
        self.Entry_Gpre.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpre.configure(textvariable=self.gpre)
        self.gpre.trace_variable("w", self.Entry_Gpre_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_Gpost = Label(gen_settings, text="G Code Postscript")
        self.Label_Gpost.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpost = Entry(gen_settings)
        self.Entry_Gpost.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpost.configure(textvariable=self.gpost)
        self.gpost.trace_variable("w", self.Entry_Gpost_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_var_dis = Label(gen_settings, text="Disable Variables")
        self.Label_var_dis.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_var_dis = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_var_dis.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_var_dis.configure(variable=self.var_dis)

        D_Yloc = D_Yloc + D_dY
        font_entry_width = 215
        self.Label_Fontdir = Label(gen_settings, text="Font Directory")
        self.Label_Fontdir.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Fontdir = Entry(gen_settings, width="15")
        self.Entry_Fontdir.place(x=xd_entry_L, y=D_Yloc, width=font_entry_width, height=23)
        self.Entry_Fontdir.configure(textvariable=self.fontdir)
        self.Fontdir = Button(gen_settings, text="Select Dir")
        self.Fontdir.place(x=xd_entry_L + font_entry_width + 10, y=D_Yloc, width=w_label - 80, height=23)

        D_Yloc = D_Yloc + D_dY
        self.Label_Hcalc = Label(gen_settings, text="Height Calculation")
        self.Label_Hcalc.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Radio_Hcalc_USE = Radiobutton(gen_settings, text="Max Used", \
                                           value="max_use", width="110", anchor=W)
        self.Radio_Hcalc_USE.place(x=w_label + x_radio_offset, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_USE.configure(variable=self.H_CALC)

        self.Radio_Hcalc_ALL = Radiobutton(gen_settings, text="Max All", \
                                           value="max_all", width="110", anchor=W)
        self.Radio_Hcalc_ALL.place(x=w_label + x_radio_offset + 90, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_ALL.configure(variable=self.H_CALC)

        if self.input_type.get() != "text":
            self.Entry_Fontdir.configure(state="disabled")
            self.Fontdir.configure(state="disabled")
            self.Radio_Hcalc_ALL.configure(state="disabled")
            self.Radio_Hcalc_USE.configure(state="disabled")
        else:
            self.Fontdir.bind("<ButtonRelease-1>", self.Fontdir_Click)

        D_Yloc = D_Yloc + 24
        self.Label_Box = Label(gen_settings, text="Add Box/Circle")
        self.Label_Box.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Checkbutton_plotbox = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_plotbox.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_plotbox.configure(variable=self.plotbox)
        self.plotbox.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(gen_settings, text="Box/Circle Gap:", anchor=E)
        self.Label_BoxGap.place(x=w_label + x_radio_offset + 25, y=D_Yloc, width=125, height=21)
        self.Entry_BoxGap = Entry(gen_settings)
        self.Entry_BoxGap.place(x=w_label + x_radio_offset + 165, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(gen_settings, textvariable=self.units, anchor=W)
        self.Label_BoxGap_u.place(x=w_label + x_radio_offset + 230, y=D_Yloc, width=100, height=21)
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_v_pplot = Label(gen_settings, text="Plot During V-Carve Calculation")
        self.Label_v_pplot.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_pplot = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_v_pplot.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)
        self.v_pplot.trace_variable("w", self.Entry_v_pplot_Callback)

        D_Yloc = D_Yloc + D_dY + 10
        self.Label_SaveConfig = Label(gen_settings, text="Configuration File")
        self.Label_SaveConfig.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.GEN_SaveConfig = Button(gen_settings, text="Save")
        self.GEN_SaveConfig.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=21, anchor="nw")
        self.GEN_SaveConfig.bind("<ButtonRelease-1>", self.write_config_file)

        ## Buttons ##
        gen_settings.update_idletasks()
        Ybut = int(gen_settings.winfo_height()) - 30
        Xbut = int(gen_settings.winfo_width() / 2)

        self.GEN_Reload = Button(gen_settings, text="Recalculate")
        self.GEN_Reload.place(x=Xbut - 65, y=Ybut, width=130, height=30, anchor="e")
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        self.GEN_Recalculate = Button(gen_settings, text="Re-Load Image")
        self.GEN_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="c")
        self.GEN_Recalculate.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.GEN_Close = Button(gen_settings, text="Close", command=self.Close_Current_Window_Click)
        self.GEN_Close.place(x=Xbut + 65, y=Ybut, width=130, height=30, anchor="w")

    ################################################################################
    #                         V-Carve Settings window                              #
    ################################################################################
    def VCARVE_Settings_Window(self):
        vcarve_settings = Toplevel(width=580, height=690)
        vcarve_settings.grab_set()  # Use grab_set to prevent user input in the main window during calculations
        vcarve_settings.resizable(0, 0)
        vcarve_settings.title('V-Carve Settings')
        vcarve_settings.iconname("V-Carve Settings")

        try:
            vcarve_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                vcarve_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        D_Yloc = 12
        D_dY = 24
        xd_label_L = 12

        w_label = 250
        w_entry = 60
        w_units = 35
        xd_entry_L = xd_label_L + w_label + 10
        xd_units_L = xd_entry_L + w_entry + 5

        # ----------------------
        self.Label_cutter_type = Label(vcarve_settings, text="Cutter Type")
        self.Label_cutter_type.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Radio_Type_VBIT = Radiobutton(vcarve_settings, text="V-Bit", value="VBIT", width="100", anchor=W)
        self.Radio_Type_VBIT.place(x=xd_entry_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_Type_VBIT.configure(variable=self.bit_shape)

        D_Yloc = D_Yloc + 24
        self.Radio_Type_BALL = Radiobutton(vcarve_settings, text="Ball Nose", value="BALL", width="100", anchor=W)
        self.Radio_Type_BALL.place(x=xd_entry_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_Type_BALL.configure(variable=self.bit_shape)

        D_Yloc = D_Yloc + 24
        self.Radio_Type_STRAIGHT = Radiobutton(vcarve_settings, text="Straight", value="FLAT", width="100", anchor=W)
        self.Radio_Type_STRAIGHT.place(x=xd_entry_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_Type_STRAIGHT.configure(variable=self.bit_shape)

        self.bit_shape.trace_variable("w", self.Entry_Bit_Shape_var_Callback)
        # ----------------------

        D_Yloc = D_Yloc + D_dY
        self.Label_Vbitangle = Label(vcarve_settings, text="V-Bit Angle")
        self.Label_Vbitangle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Vbitangle_u = Label(vcarve_settings, text="deg", anchor=W)
        self.Label_Vbitangle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Vbitangle = Entry(vcarve_settings, width="15")
        self.Entry_Vbitangle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Vbitangle.configure(textvariable=self.v_bit_angle)
        self.v_bit_angle.trace_variable("w", self.Entry_Vbitangle_Callback)
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Vbitdia = Label(vcarve_settings, text="V-Bit Diameter")
        self.Label_Vbitdia.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Vbitdia_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_Vbitdia_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Vbitdia = Entry(vcarve_settings, width="15")
        self.Entry_Vbitdia.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Vbitdia.configure(textvariable=self.v_bit_dia)
        self.v_bit_dia.trace_variable("w", self.Entry_Vbitdia_Callback)
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_VDepthLimit = Label(vcarve_settings, text="Cut Depth Limit")
        self.Label_VDepthLimit.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_VDepthLimit_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_VDepthLimit_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_VDepthLimit = Entry(vcarve_settings, width="15")
        self.Entry_VDepthLimit.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_VDepthLimit.configure(textvariable=self.v_depth_lim)
        self.v_depth_lim.trace_variable("w", self.Entry_VDepthLimit_Callback)
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_maxcut = Label(vcarve_settings, text="Max Cut Depth")
        self.Label_maxcut.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_maxcut_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_maxcut_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Label_maxcut_i = Label(vcarve_settings, textvariable=self.maxcut, anchor=W)
        self.Label_maxcut_i.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=21)

        D_Yloc = D_Yloc + D_dY + 5
        self.Label_StepSize = Label(vcarve_settings, text="Sub-Step Length")
        self.Label_StepSize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_StepSize_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_StepSize_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_StepSize = Entry(vcarve_settings, width="15")
        self.Entry_StepSize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_StepSize.configure(textvariable=self.v_step_len)
        self.v_step_len.trace_variable("w", self.Entry_StepSize_Callback)
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(), 2)

        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator00 = Frame(vcarve_settings, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator00.place(x=0, y=D_Yloc, width=580, height=2)

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_v_flop = Label(vcarve_settings, text="Flip Normals (Cut Outside)")
        self.Label_v_flop.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_flop = Checkbutton(vcarve_settings, text="", anchor=W)
        self.Checkbutton_v_flop.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_flop.configure(variable=self.v_flop)
        self.v_flop.trace_variable("w", self.Entry_recalc_var_Callback)

        x_radio_offset = 62 - 40
        D_Yloc = D_Yloc + 24
        self.Label_vBox = Label(vcarve_settings, text="Add Box (Flip Normals)")
        self.Label_vBox.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Checkbutton_plotbox = Checkbutton(vcarve_settings, text="", anchor=W)
        self.Checkbutton_plotbox.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_plotbox.configure(variable=self.plotbox)
        self.plotbox.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(vcarve_settings, text="Box Gap:", anchor=E)
        self.Label_BoxGap.place(x=w_label + x_radio_offset + 25, y=D_Yloc, width=75, height=21)
        self.Entry_BoxGap = Entry(vcarve_settings)
        self.Entry_BoxGap.place(x=w_label + x_radio_offset + 110, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_BoxGap_u.place(x=w_label + x_radio_offset + 305, y=D_Yloc, width=100, height=21)
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)

        self.Label_BoxGap_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_BoxGap_u.place(x=w_label + x_radio_offset + 175, y=D_Yloc, width=100, height=21)

        self.GEN_Reload = Button(vcarve_settings, text="Recalculate")
        self.GEN_Reload.place(x=580 - 10, y=D_Yloc, width=90, height=25, anchor="ne")
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator0 = Frame(vcarve_settings, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator0.place(x=0, y=D_Yloc, width=580, height=2)

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_inlay = Label(vcarve_settings, text="Prismatic (For inlay also select Add Box)")
        self.Label_inlay.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_inlay = Checkbutton(vcarve_settings, text="", anchor=W)
        self.Checkbutton_inlay.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_inlay.configure(variable=self.inlay)
        self.inlay.trace_variable("w", self.Entry_Prismatic_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_Allowance = Label(vcarve_settings, text="Prismatic Overcut")
        self.Label_Allowance.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Allowance_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_Allowance_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Allowance = Entry(vcarve_settings, width="15")
        self.Entry_Allowance.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Allowance.configure(textvariable=self.allowance)
        self.allowance.trace_variable("w", self.Entry_Allowance_Callback)
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(), 2)

        ### Update Idle tasks before requesting anything from winfo
        vcarve_settings.update_idletasks()
        center_loc = int(float(vcarve_settings.winfo_width()) / 2)

        ## Multipass Settings ##
        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator1 = Frame(vcarve_settings, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.place(x=0, y=D_Yloc, width=580, height=2)

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_multipass = Label(vcarve_settings, text="Multipass Cutting")
        self.Label_multipass.place(x=center_loc, y=D_Yloc, width=w_label, height=21, anchor=CENTER)

        D_Yloc = D_Yloc + D_dY
        self.Label_v_rough_stk = Label(vcarve_settings, text="V-Carve Finish Pass Stock")
        self.Label_v_rough_stk.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_v_rough_stk_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_v_rough_stk_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)

        self.Label_right_v_rough_stk = Label(vcarve_settings, text="(Zero disables multipass cutting)", anchor=W)
        self.Label_right_v_rough_stk.place(x=xd_units_L + 20, y=D_Yloc, width=w_label, height=21)

        self.Entry_v_rough_stk = Entry(vcarve_settings, width="15")
        self.Entry_v_rough_stk.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_v_rough_stk.configure(textvariable=self.v_rough_stk)
        self.v_rough_stk.trace_variable("w", self.Entry_v_rough_stk_Callback)
        self.entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_v_max_cut = Label(vcarve_settings, text="V-Carve Max Depth per Pass")
        self.Label_v_max_cut.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_v_max_cut_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_v_max_cut_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_v_max_cut = Entry(vcarve_settings, width="15")
        self.Entry_v_max_cut.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_v_max_cut.configure(textvariable=self.v_max_cut)
        self.v_max_cut.trace_variable("w", self.Entry_v_max_cut_Callback)
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), 2)

        if float(self.v_rough_stk.get()) == 0.0:
            self.Label_v_max_cut.configure(state="disabled")
            self.Label_v_max_cut_u.configure(state="disabled")
            self.Entry_v_max_cut.configure(state="disabled")
        else:
            self.Label_v_max_cut.configure(state="normal")
            self.Label_v_max_cut_u.configure(state="normal")
            self.Entry_v_max_cut.configure(state="normal")

        if not bool(self.inlay.get()):
            self.Label_Allowance.configure(state="disabled")
            self.Entry_Allowance.configure(state="disabled")
            self.Label_Allowance_u.configure(state="disabled")
        else:
            self.Label_Allowance.configure(state="normal")
            self.Entry_Allowance.configure(state="normal")
            self.Label_Allowance_u.configure(state="normal")

        if not bool(self.plotbox.get()):
            self.Label_BoxGap.configure(state="disabled")
            self.Entry_BoxGap.configure(state="disabled")
            self.Label_BoxGap_u.configure(state="disabled")
        else:
            self.Label_BoxGap.configure(state="normal")
            self.Entry_BoxGap.configure(state="normal")
            self.Label_BoxGap_u.configure(state="normal")

        ## Cleanup Settings ##
        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator1 = Frame(vcarve_settings, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.place(x=0, y=D_Yloc, width=580, height=2)

        right_but_loc = int(vcarve_settings.winfo_width()) - 10
        width_cb = 100
        height_cb = 35

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_clean = Label(vcarve_settings, text="Cleanup Operations")
        self.Label_clean.place(x=center_loc, y=D_Yloc, width=w_label, height=21, anchor=CENTER)

        self.CLEAN_Recalculate = Button(vcarve_settings, text="Calculate\nCleanup", command=self.CLEAN_Recalculate_Click)
        self.CLEAN_Recalculate.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb * 1.5, anchor="ne")

        D_Yloc = D_Yloc + D_dY
        self.Label_CLEAN_DIA = Label(vcarve_settings, text="Cleanup Cut Diameter")
        self.Label_CLEAN_DIA.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_CLEAN_DIA_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_CLEAN_DIA_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_CLEAN_DIA = Entry(vcarve_settings, width="15")
        self.Entry_CLEAN_DIA.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_CLEAN_DIA.configure(textvariable=self.clean_dia)
        self.clean_dia.trace_variable("w", self.Entry_CLEAN_DIA_Callback)
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_STEP_OVER = Label(vcarve_settings, text="Cleanup Cut Step Over")
        self.Label_STEP_OVER.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_STEP_OVER_u = Label(vcarve_settings, text="%", anchor=W)
        self.Label_STEP_OVER_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_STEP_OVER = Entry(vcarve_settings, width="15")
        self.Entry_STEP_OVER.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_STEP_OVER.configure(textvariable=self.clean_step)
        self.clean_step.trace_variable("w", self.Entry_STEP_OVER_Callback)
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), 2)

        D_Yloc = D_Yloc + 24
        check_delta = 40
        self.Label_clean_P = Label(vcarve_settings, text="Cleanup Cut Directions")
        self.Label_clean_P.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Write_Clean = Button(vcarve_settings, text="Save Cleanup\nG-Code", command=self.Write_Clean_Click)
        self.Write_Clean.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb, anchor="e")

        self.Checkbutton_clean_P = Checkbutton(vcarve_settings, text="P", anchor=W)
        self.Checkbutton_clean_P.configure(variable=self.clean_P)
        self.Checkbutton_clean_P.place(x=xd_entry_L, y=D_Yloc, width=w_entry + 40, height=23)
        self.Checkbutton_clean_X = Checkbutton(vcarve_settings, text="X", anchor=W)
        self.Checkbutton_clean_X.configure(variable=self.clean_X)
        self.Checkbutton_clean_X.place(x=xd_entry_L + check_delta, y=D_Yloc, width=w_entry + 40, height=23)
        self.Checkbutton_clean_Y = Checkbutton(vcarve_settings, text="Y", anchor=W)
        self.Checkbutton_clean_Y.configure(variable=self.clean_Y)
        self.Checkbutton_clean_Y.place(x=xd_entry_L + check_delta * 2, y=D_Yloc, width=w_entry + 40, height=23)

        D_Yloc = D_Yloc + 12

        D_Yloc = D_Yloc + D_dY
        self.Label_V_CLEAN = Label(vcarve_settings, text="V-Bit Cleanup Step")
        self.Label_V_CLEAN.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_V_CLEAN_u = Label(vcarve_settings, textvariable=self.units, anchor=W)
        self.Label_V_CLEAN_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_V_CLEAN = Entry(vcarve_settings, width="15")
        self.Entry_V_CLEAN.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_V_CLEAN.configure(textvariable=self.clean_v)
        self.clean_v.trace_variable("w", self.Entry_V_CLEAN_Callback)
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), 2)

        D_Yloc = D_Yloc + 24
        self.Label_v_clean_P = Label(vcarve_settings, text="V-Bit Cut Directions")
        self.Label_v_clean_P.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Write_V_Clean = Button(vcarve_settings, text="Save V Cleanup\nG-Code", command=self.Write_V_Clean_Click)
        self.Write_V_Clean.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb, anchor="e")

        self.Checkbutton_v_clean_P = Checkbutton(vcarve_settings, text="P", anchor=W)
        self.Checkbutton_v_clean_P.configure(variable=self.v_clean_P)
        self.Checkbutton_v_clean_P.place(x=xd_entry_L, y=D_Yloc, width=w_entry + 40, height=23)
        self.Checkbutton_v_clean_X = Checkbutton(vcarve_settings, text="X", anchor=W)
        self.Checkbutton_v_clean_X.configure(variable=self.v_clean_X)
        self.Checkbutton_v_clean_X.place(x=xd_entry_L + check_delta, y=D_Yloc, width=w_entry + 40, height=23)
        self.Checkbutton_v_clean_Y = Checkbutton(vcarve_settings, text="Y", anchor=W)
        self.Checkbutton_v_clean_Y.configure(variable=self.v_clean_Y)
        self.Checkbutton_v_clean_Y.place(x=xd_entry_L + check_delta * 2, y=D_Yloc, width=w_entry + 40, height=23)

        ## V-Bit Picture ##
        self.PHOTO = PhotoImage(format='gif', data=
        'R0lGODlhoABQAIABAAAAAP///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEK'
        + 'AAEALAAAAACgAFAAAAL+jI+pBu2/opy02ouzvg+G7m3iSJam1XHpybbuezhk'
        + 'CFNyjZ9AS+ff6gtqdq5eMUQUKlG4GwsYW0ptPiMGmkhOtwhtzioBd7nkqBTk'
        + 'BV3LZe8Z7Vyzue75zL6t4zf6fa3vxxGoBDhIZViFKFKoeNeYwfjIJylHyWPJ'
        + 'hPmkechZEmkJ6hk2GiFaqnD6qIpq1ur6WhnL+kqLaIuKO6g7yuvnywmMJ4xJ'
        + 'PGdMidxmkpaFxDClTMar1ZA1hr0kTcecDUu0Exe0nacDy/D8ER17vgidugK+'
        + 'zq7OHB5jXf1Onkpf311HXz1+1+gBs7ZAzcB57Aj+IPUFoUNC6CbCgKMGYa3+'
        + 'cBjhBOtisUkzf2FCXjT5C+UTlSl7sQykMRQxhf8+RSxmrFrOKi9VXCwI7gbH'
        + 'h/iCGgX56SAae3+AEg36FN0+qQt10BIHj1XMIk6xJZH3D+zXd1Yhab2ybaRR'
        + 'sFXjVZR4JJOjCVtf6IQ2NuzUrt7KlrwUkB/NoXD35hM7tOZKvjy21v0D6NRI'
        + 'xZBBKovzmCTPojeJao6WeFzmz6InjiYtmtBp1Jtb9/y8eoZA1nmkxaYt5LbZ'
        + 'frhrx+29R7eNPq9JCzcVGTgdXLGLG7/qXHlCVcel+/Y5vGBRjWyR7n6OAtTs'
        + 'b9otfwdPV9R4sgux3sN7NzHWjX8htQPSfW/UgYRL888KPAllP3jgX14GRpFP'
        + 'O/85405YCZpRIIEQIsjRfAtStYgeAuUX34TwCajZYUkhJ6FizRgIgYggNlTd'
        + 'EMR1Ux5q0Q2BoXUbTVQAADs=')

        self.Label_photo = Label(vcarve_settings, image=self.PHOTO)
        self.Label_photo.place(x=w_label + 150, y=40)
        self.Entry_Bit_Shape_Check()

        ## Buttons ##
        Ybut = int(vcarve_settings.winfo_height()) - 30
        Xbut = int(vcarve_settings.winfo_width() / 2)

        self.VCARVE_Recalculate = Button(vcarve_settings, text="Calculate V-Carve", command=self.VCARVE_Recalculate_Click)
        self.VCARVE_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")

        if self.cut_type.get() == "v-carve":
            self.VCARVE_Recalculate.configure(state="normal", command=None)
        else:
            self.VCARVE_Recalculate.configure(state="disabled", command=None)

        self.VCARVE_Close = Button(vcarve_settings, text="Close", command=vcarve_settings.destroy)
        self.VCARVE_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")
