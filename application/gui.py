import os
import sys
import re
import getopt
from time import time

from math import *


import readers.cxf as parse_cxf
import readers.dxf as parse_dxf

import writers

from util import *

from util.mathutil import Zero, Get_Angle, Transform

from settings import Settings

version = '1.5'

################################################################################
class Gui(Frame):

    self.settings = None

    def __init__(self, master, settings):
        Frame.__init__(self, master)
        self.w = 780
        self.h = 490
        frame = Frame(master, width=self.w, height=self.h)
        self.master = master
        self.x = -1
        self.y = -1
        self.delay_calc = 0

        self.settings = settings

        # TODO checkExternalBinaries() from util.externals

        self.createWidgets()

    def setting(self, name):
        '''shorthand for self.settings.get(name)'''
        return self.settings.get(name)


    def bindKeys(self):
        self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind('<Enter>', self.bindConfigure)
        self.master.bind('<Escape>', self.KEY_ESC)
        self.master.bind('<F1>', self.KEY_F1)
        self.master.bind('<F2>', self.KEY_F2)
        self.master.bind('<F3>', self.KEY_F3)
        self.master.bind('<F4>', self.KEY_F4)
        self.master.bind('<F5>', self.KEY_F5) #self.Recalculate_Click)
        self.master.bind('<Control-Up>'  , self.Listbox_Key_Up)
        self.master.bind('<Control-Down>', self.Listbox_Key_Down)
        self.master.bind('<Prior>', self.KEY_ZOOM_IN) # Page Up
        self.master.bind('<Next>', self.KEY_ZOOM_OUT) # Page Down
        self.master.bind('<Control-g>', self.KEY_CTRL_G)

    def createWidgets(self):
        self.initComplete = 0
        self.bindKeys()

        self.batch      = BooleanVar()
        self.show_axis  = BooleanVar()
        self.show_box   = BooleanVar()
        self.show_thick = BooleanVar()
        self.flip       = BooleanVar()
        self.mirror     = BooleanVar()
        self.outer      = BooleanVar()
        self.upper      = BooleanVar()
        self.fontdex    = BooleanVar()
        self.b_carve    = BooleanVar()
        self.v_flop     = BooleanVar()
        self.v_pplot    = BooleanVar()
        self.arc_fit    = BooleanVar()
        self.ext_char   = BooleanVar()
        self.var_dis    = BooleanVar()
        self.useIMGsize = BooleanVar()

        self.clean_P    = BooleanVar()
        self.clean_X    = BooleanVar()
        self.clean_Y    = BooleanVar()
        self.v_clean_P  = BooleanVar()
        self.v_clean_X  = BooleanVar()
        self.v_clean_Y  = BooleanVar()

        self.YSCALE     = StringVar()
        self.XSCALE     = StringVar()
        self.LSPACE     = StringVar()
        self.CSPACE     = StringVar()
        self.WSPACE     = StringVar()
        self.TANGLE     = StringVar()
        self.TRADIUS    = StringVar()
        self.ZSAFE      = StringVar()
        self.ZCUT       = StringVar()
        self.STHICK     = StringVar()
        self.origin     = StringVar()
        self.justify    = StringVar()
        self.units      = StringVar()

        self.xorigin    = StringVar()
        self.yorigin    = StringVar()
        self.segarc     = StringVar()
        self.accuracy   = StringVar()

        self.funits     = StringVar()
        self.FEED       = StringVar()
        self.fontfile   = StringVar()
        self.H_CALC     = StringVar()
        self.plotbox    = StringVar()
        self.boxgap     = StringVar()
        self.fontdir    = StringVar()
        self.cut_type   = StringVar()
        self.input_type = StringVar()

        self.v_bit_angle= StringVar()
        self.v_bit_dia  = StringVar()
        self.v_depth_lim= StringVar()
        self.v_drv_crner= StringVar()
        self.v_stp_crner= StringVar()
        self.v_step_len = StringVar()
        self.v_acc      = StringVar()
        self.v_check_all= StringVar()

        self.clean_dia  = StringVar()
        self.clean_step = StringVar()
        self.clean_v    = StringVar()
        self.clean_w    = StringVar()
        self.clean_name = StringVar()

        self.gpre        = StringVar()
        self.gpost       = StringVar()

        self.bmp_turnpol      = StringVar()
        self.bmp_turdsize     = StringVar()
        self.bmp_alphamax     = StringVar()
        self.bmp_opttolerance = StringVar()
        self.bmp_longcurve    = BooleanVar()

        self.maxcut             = StringVar()
        self.current_input_file = StringVar()
        self.bounding_box       = StringVar()


        self.segID   = []
        self.gcode   = []
        self.svgcode = []
        self.coords  = []
        self.vcoords = []
        self.clean_coords=[]
        self.clean_segment=[]
        self.clean_coords_sort=[]
        self.v_clean_coords_sort=[]

        self.font    = {}
        self.RADIUS_PLOT = 0
        self.MAXX    = 0
        self.MINX    = 0
        self.MAXY    = 0
        self.MINY    = 0
        self.Xzero = float(0.0)
        self.Yzero = float(0.0)
        self.default_text = "F-Engrave"
        self.DXF_source = " "
        self.HOME_DIR     =  os.path.expanduser("~")
        self.NGC_FILE     = (self.HOME_DIR + "/None")
        self.IMAGE_FILE   = (self.HOME_DIR + "/None")
        self.current_input_file.set(" ")
        self.bounding_box.set(" ")

        self.pscale = 0
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
            self.units.set('mm')
            self.funits.set('mm/min')

        ##########################################################################
        #                         G-Code Default Preamble                        #
        ##########################################################################
        # G17        ; sets XY plane                                             #
        # G64 P0.003 ; G64 P- (motion blending tolerance set to 0.003) This is   #
        #              the default in engrave.py                                 #
        # G64        ; G64 without P option keeps the best speed possible, no    #
        #              matter how far away from the programmed point you end up. #
        # M3 S3000   ; Spindle start at 3000                                     #
        # M7         ; Turn mist coolant on                                      #
        ##########################################################################
        self.gpre.set("G17 G64 P0.003 M3 S3000 M7")

        ##########################################################################
        #                        G-Code Default Postamble                        #
        ##########################################################################
        # M5 ; Stop Spindle                                                      #
        # M9 ; Turn all coolant off                                              #
        # M2 ; End Program                                                       #
        ##########################################################################
        self.gpost.set("M5 M9 M2")

        ##########################################################################
        ###                     END INITILIZING VARIABLES                      ###
        ##########################################################################
        config_file = "config.ngc"
        home_config1 = self.HOME_DIR + "/" + config_file
        config_file2 = ".fengraverc"
        home_config2 = self.HOME_DIR + "/" + config_file2
        if ( os.path.isfile(config_file) ):
            self.Open_G_Code_File(config_file)
        elif ( os.path.isfile(home_config1) ):
            self.Open_G_Code_File(home_config1)
        elif ( os.path.isfile(home_config2) ):
            self.Open_G_Code_File(home_config2)

        opts, args = None, None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hbg:f:d:t:", [
                "help","batch","gcode_file","fontdir=","defdir=","text="
            ])
        except getopt.GetOptError:
            fmessage('Unable interpret command line options')
            print e
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

        if self.setting('batch'):
            fmessage('(F-Engrave Batch Mode)')

            if self.input_type.get() == "text":
                self.Read_font_file()
            else:
                self.Read_image_file()

            self.DoIt()
            if self.cut_type.get() == "v-carve":
                self.V_Carve_It()
            # self.WriteGCode()
            self.WriteSVG()

            for line in self.svgcode:
                print line

            # for line in self.gcode:
            #     try:
            #         sys.stdout.write(line+'\n')
            #     except:
            #         sys.stdout.write('(skipping line)\n')
            sys.exit()

        ##########################################################################

        # make a Status Bar
        self.statusMessage = StringVar()
        self.statusMessage.set("")
        self.statusbar = Label(self.master, textvariable=self.statusMessage, \
                                   bd=1, relief=SUNKEN , height=1)
        self.statusbar.pack(anchor=SW, fill=X, side=BOTTOM)
        self.statusMessage.set("Welcome to F-Engrave")

        # Buttons
        self.Recalculate = Button(self.master,text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

        # Canvas
        lbframe = Frame( self.master )
        self.PreviewCanvas_frame = lbframe
        self.PreviewCanvas = Canvas(lbframe, width=self.w-525, \
                                        height=self.h-200, background="grey")
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
        self.Label_font_prop = Label(self.master,text="Text Font Properties:", anchor=W)

        self.Label_Yscale = Label(self.master,text="Text Height", anchor=CENTER)
        self.Label_Yscale_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Yscale = Entry(self.master,width="15")
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)
        self.NormalColor =  self.Entry_Yscale.cget('bg')

        self.Label_Sthick = Label(self.master,text="Line Thickness")
        self.Label_Sthick_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self.master,width="15")
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)

        self.Label_Xscale = Label(self.master,text="Text Width", anchor=CENTER )
        self.Label_Xscale_u = Label(self.master,text="%", anchor=W)
        self.Entry_Xscale = Entry(self.master,width="15")
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)

        self.Label_useIMGsize = Label(self.master,text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command = self.useIMGsize_var_Callback)
        #self.useIMGsize.trace_variable("w", self.useIMGsize_var_Callback)

        self.Label_Cspace = Label(self.master,text="Char Spacing", anchor=CENTER )
        self.Label_Cspace_u = Label(self.master,text="%", anchor=W)
        self.Entry_Cspace = Entry(self.master,width="15")
        self.Entry_Cspace.configure(textvariable=self.CSPACE)
        self.Entry_Cspace.bind('<Return>', self.Recalculate_Click)
        self.CSPACE.trace_variable("w", self.Entry_Cspace_Callback)

        self.Label_Wspace = Label(self.master,text="Word Spacing", anchor=CENTER )
        self.Label_Wspace_u = Label(self.master,text="%", anchor=W)
        self.Entry_Wspace = Entry(self.master,width="15")
        self.Entry_Wspace.configure(textvariable=self.WSPACE)
        self.Entry_Wspace.bind('<Return>', self.Recalculate_Click)
        self.WSPACE.trace_variable("w", self.Entry_Wspace_Callback)

        self.Label_Lspace = Label(self.master,text="Line Spacing", anchor=CENTER )
        self.Entry_Lspace = Entry(self.master,width="15")
        self.Entry_Lspace.configure(textvariable=self.LSPACE)
        self.Entry_Lspace.bind('<Return>', self.Recalculate_Click)
        self.LSPACE.trace_variable("w", self.Entry_Lspace_Callback)

        self.Label_pos_orient = Label(self.master,text="Text Position and Orientation:",\
                                          anchor=W)

        self.Label_Tangle = Label(self.master,text="Text Angle", anchor=CENTER )
        self.Label_Tangle_u = Label(self.master,text="deg", anchor=W)
        self.Entry_Tangle = Entry(self.master,width="15")
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)

        self.Label_Justify      = Label(self.master,text="Justify", anchor=CENTER )
        self.Justify_OptionMenu = OptionMenu(self.master, self.justify, "Left","Center",\
                                                 "Right", command=self.Recalculate_RQD_Click)

        self.Label_Origin      = Label(self.master,text="Origin", anchor=CENTER )
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

        self.Label_flip = Label(self.master,text="Flip Text")
        self.Checkbutton_flip = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_recalc_var_Callback)

        self.Label_mirror = Label(self.master,text="Mirror Text")
        self.Checkbutton_mirror = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_recalc_var_Callback)

        self.Label_text_on_arc = Label(self.master,text="Text on Circle Properties:",\
                                           anchor=W)

        self.Label_Tradius = Label(self.master,text="Circle Radius", anchor=CENTER )
        self.Label_Tradius_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Tradius = Entry(self.master,width="15")
        self.Entry_Tradius.configure(textvariable=self.TRADIUS)
        self.Entry_Tradius.bind('<Return>', self.Recalculate_Click)
        self.TRADIUS.trace_variable("w", self.Entry_Tradius_Callback)

        self.Label_outer = Label(self.master,text="Outside circle")
        self.Checkbutton_outer = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=self.outer)
        self.outer.trace_variable("w", self.Entry_recalc_var_Callback)

        self.Label_upper = Label(self.master,text="Top of Circle")
        self.Checkbutton_upper = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=self.upper)
        self.upper.trace_variable("w", self.Entry_recalc_var_Callback)

        self.separator1 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(height=2, bd=1, relief=SUNKEN)

        # End Left Column #

        # Right Column #
        self.Label_gcode_opt = Label(self.master,text="Gcode Properties:", anchor=W)

        self.Label_Feed = Label(self.master,text="Feed Rate")
        self.Label_Feed_u = Label(self.master,textvariable=self.funits, anchor=W)
        self.Entry_Feed = Entry(self.master,width="15")
        self.Entry_Feed.configure(textvariable=self.FEED)
        self.Entry_Feed.bind('<Return>', self.Recalculate_Click)
        self.FEED.trace_variable("w", self.Entry_Feed_Callback)

        self.Label_Zsafe = Label(self.master,text="Z Safe")
        self.Label_Zsafe_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self.master,width="15")
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)

        self.Label_Zcut = Label(self.master,text="Cut Depth")
        self.Label_Zcut_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self.master,width="15")
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)


        self.Checkbutton_fontdex = Checkbutton(self.master,text="Show All Font Characters",\
                                                   anchor=W)
        self.fontdex.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Checkbutton_fontdex.configure(variable=self.fontdex)
        self.Label_fontfile = Label(self.master,textvariable=self.current_input_file, anchor=W,\
                                        foreground='grey50')
        self.Label_List_Box = Label(self.master,text="Font Files:", foreground="#101010",\
                                        anchor=W)
        lbframe = Frame( self.master )
        self.Listbox_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Listbox_1 = Listbox(lbframe, selectmode="single", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Listbox_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Listbox_1.pack(side=LEFT, fill=BOTH, expand=1)

        self.Listbox_1.bind("<ButtonRelease-1>", self.Listbox_1_Click)
        self.Listbox_1.bind("<Up>",   self.Listbox_Key_Up)
        self.Listbox_1.bind("<Down>", self.Listbox_Key_Down)

        try:
            font_files = os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files = " "
        for name in font_files:
            if str.find(name.upper(),'.CXF') != -1 \
            or (str.find(name.upper(),'.TTF') != -1 and self.TTF_AVAIL ):
                self.Listbox_1.insert(END, name)
        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")

        self.fontdir.trace_variable("w", self.Entry_fontdir_Callback)

        self.V_Carve_Calc = Button(self.master,text="Calc V-Carve", command=self.V_Carve_Calc_Click)

        self.Radio_Cut_E = Radiobutton(self.master,text="Engrave", value="engrave", anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type )
        self.Radio_Cut_V = Radiobutton(self.master,text="V-Carve", value="v-carve", anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type )
        self.cut_type.trace_variable("w", self.menu_View_Refresh_Callback)
        # End Right Column #

        # Text Box
        self.Input_Label = Label(self.master,text="Input Text:",anchor=W)

        lbframe = Frame( self.master)
        self.Input_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Input = Text(lbframe, width="40", height="12", yscrollcommand=scrollbar.set,\
                              bg='white')
        self.Input.insert(END, self.default_text)
        scrollbar.config(command=self.Input.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Input.pack(side=LEFT, fill=BOTH, expand=1)
        self.Input.bind("<Key>", self.Recalculate_RQD_Nocalc)
        ## self.master.unbind("<Alt>")

        #GEN Setting Window Entry initialization
        self.Entry_Xoffset=Entry()
        self.Entry_Yoffset=Entry()
        self.Entry_BoxGap = Entry()
        self.Entry_ArcAngle = Entry()
        self.Entry_Accuracy = Entry()
        #Bitmap Setting Window Entry initialization
        self.Entry_BMPturdsize = Entry()
        self.Entry_BMPalphamax = Entry()
        self.Entry_BMPoptTolerance = Entry()
        #V-Carve Setting Window Entry initialization
        self.Entry_Vbitangle = Entry()
        self.Entry_Vbitdia = Entry()
        self.Entry_VDepthLimit = Entry()
        self.Entry_InsideAngle = Entry()
        self.Entry_OutsideAngle = Entry()
        self.Entry_StepSize = Entry()
        self.Entry_LoopAcc = Entry()
        self.Entry_W_CLEAN = Entry()
        self.Entry_CLEAN_DIA = Entry()
        self.Entry_STEP_OVER = Entry()
        self.Entry_V_CLEAN = Entry()

        # Make Menu Bar
        self.menuBar = Menu(self.master, relief = "raised", bd=2)

        top_File = Menu(self.menuBar, tearoff=0)
        top_File.add("command", label = "Open F-engrave G-Code File", \
                         command = self.menu_File_Open_G_Code_File)
        if self.POTRACE_AVAIL == True:
            top_File.add("command", label = "Open DXF/Bitmap File", \
                             command = self.menu_File_Open_DXF_File)
        else:
            top_File.add("command", label = "Open DXF File", \
                             command = self.menu_File_Open_DXF_File)

        top_File.add("command", label = "Save G-Code File", \
                         command = self.menu_File_Save_G_Code_File)
        top_File.add("command", label = "Save SVG File",    \
                         command = self.menu_File_Save_SVG_File)
        if IN_AXIS:
            top_File.add("command", label = "Write To Axis and Exit", \
                             command = self.WriteToAxis)
        else:
            top_File.add("command", label = "Exit", command = self.menu_File_Quit)
        self.menuBar.add("cascade", label="File", menu=top_File)

        top_Edit = Menu(self.menuBar, tearoff=0)
        top_Edit.add("command", label = "Copy G-Code Data to Clipboard", \
                         command = self.CopyClipboard_GCode)
        top_Edit.add("command", label = "Copy SVG Data to Clipboard", \
                         command = self.CopyClipboard_SVG  )
        self.menuBar.add("cascade", label="Edit", menu=top_Edit)

        top_View = Menu(self.menuBar, tearoff=0)
        top_View.add("command", label = "Recalculate", command = self.menu_View_Recalculate)
        top_View.add_separator()

        top_View.add("command", label = "Zoom In <Page Up>", command = self.menu_View_Zoom_in)
        top_View.add("command", label = "Zoom Out <Page Down>", command = self.menu_View_Zoom_out)
        top_View.add("command", label = "Zoom Fit <F5>", command = self.menu_View_Refresh)

        top_View.add_separator()

        top_View.add_checkbutton(label = "Show Thickness" ,   variable=self.show_thick, \
                                     command= self.menu_View_Refresh)
        top_View.add_checkbutton(label = "Show Origin Axis",  variable=self.show_axis , \
                                     command= self.menu_View_Refresh)
        top_View.add_checkbutton(label = "Show Bounding Box", variable=self.show_box  , \
                                     command= self.menu_View_Refresh)
        self.menuBar.add("cascade", label="View", menu=top_View)

        top_Settings = Menu(self.menuBar, tearoff=0)
        top_Settings.add("command", label = "General Settings", \
                             command = self.GEN_Settings_Window)
        top_Settings.add("command", label = "V-Carve Settings", \
                             command = self.VCARVE_Settings_Window)
        if self.POTRACE_AVAIL == True:
            top_Settings.add("command", label = "Bitmap Import Settings", \
                                 command = self.PBM_Settings_Window)

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label = "Engrave Mode" ,   variable=self.cut_type, value="engrave")
        top_Settings.add_radiobutton(label = "V-Carve Mode" ,   variable=self.cut_type, value="v-carve")

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label = "Text Mode (CXF/TTF)" ,   variable=self.input_type, value="text", \
                                         command= self.menu_Mode_Change)
        top_Settings.add_radiobutton(label = "Image Mode (DXF/Bitmap)" ,   variable=self.input_type, value="image", \
                                         command= self.menu_Mode_Change)

        self.menuBar.add("cascade", label="Settings", menu=top_Settings)

        top_Help = Menu(self.menuBar, tearoff=0)
        top_Help.add("command", label = "About", command = self.menu_Help_About)
        self.menuBar.add("cascade", label="Help", menu=top_Help)

        self.master.config(menu=self.menuBar)

################################################################################
    def entry_set(self, val2, calc_flag=0, new=0):
        if calc_flag == 0 and new==0:
            try:
                self.statusbar.configure( bg = 'yellow' )
                val2.configure( bg = 'yellow' )
                self.statusMessage.set(" Recalculation required.")
            except:
                pass
        elif calc_flag == 3:
            try:
                val2.configure( bg = 'red' )
                self.statusbar.configure( bg = 'red' )
                self.statusMessage.set(" Value should be a number. ")
            except:
                pass
        elif calc_flag == 2:
            try:
                self.statusbar.configure( bg = 'red' )
                val2.configure( bg = 'red' )
                #self.statusMessage.set(message)
            except:
                pass
        elif (calc_flag == 0 or calc_flag == 1) and new==1 :
            try:
                self.statusbar.configure( bg = 'white' )
                self.statusMessage.set(self.bounding_box.get())
                val2.configure( bg = 'white' )
            except:
                pass
        elif (calc_flag == 1) and new==0 :
            try:
                self.statusbar.configure( bg = 'white' )
                self.statusMessage.set(self.bounding_box.get())
                val2.configure( bg = 'white' )
            except:
                pass

        elif (calc_flag == 0 or calc_flag == 1) and new==2:
            return 0
        return 1

################################################################################
    def Sort_Paths(self, ecoords, i_loop=2):
        ##########################
        ###   find loop ends   ###
        ##########################
        Lbeg = []
        Lend = []
        if len(ecoords) > 0:
            Lbeg.append(0)
            loop_old = ecoords[0][i_loop]
            for i in range(1,len(ecoords)):
                loop = ecoords[i][i_loop]
                if loop != loop_old:
                    Lbeg.append(i)
                    Lend.append(i-1)
                loop_old = loop
            Lend.append(i)

        #######################################################
        # Find new order based on distance to next beg or end #
        #######################################################
        order_out = []
        use_beg=0
        if len(ecoords)>0:
            order_out.append([Lbeg[0],Lend[0]])
        inext = 0
        total = len(Lbeg)
        for i in range(total-1):
            if use_beg==1:
                ii=Lbeg.pop(inext)
                Lend.pop(inext)
            else:
                ii=Lend.pop(inext)
                Lbeg.pop(inext)

            Xcur = ecoords[ii][0]
            Ycur = ecoords[ii][1]

            dx = Xcur - ecoords[ Lbeg[0] ][0]
            dy = Ycur - ecoords[ Lbeg[0] ][1]
            min_dist = dx*dx + dy*dy

            dxe = Xcur - ecoords[ Lend[0] ][0]
            dye = Ycur - ecoords[ Lend[0] ][1]
            min_diste = dxe*dxe + dye*dye

            inext=0
            inexte=0
            for j in range(1,len(Lbeg)):
                dx = Xcur - ecoords[ Lbeg[j] ][0]
                dy = Ycur - ecoords[ Lbeg[j] ][1]
                dist = dx*dx + dy*dy
                if dist < min_dist:
                    min_dist=dist
                    inext=j
                ###
                dxe = Xcur - ecoords[ Lend[j] ][0]
                dye = Ycur - ecoords[ Lend[j] ][1]
                diste = dxe*dxe + dye*dye
                if diste < min_diste:
                    min_diste=diste
                    inexte=j
                ###
            if min_diste < min_dist:
                inext=inexte
                order_out.append([Lend[inexte],Lbeg[inexte]])
                use_beg=1
            else:
                order_out.append([Lbeg[inext],Lend[inext]])
                use_beg=0
        ###########################################################
        return order_out

    def Line_Arc_Fit(self, lastx, lasty, lastz, x1, y1, z1, nextx, nexty, nextz, FLAG_arc, code,
                     R_last, x_center_last, y_center_last, FLAG_line):
        global Zero
        Acc    =   float(self.accuracy.get())
        ########################################
        ### Line fit and arc fit (curve fit) ###
        ########################################
        dx_a = x1-lastx
        dy_a = y1-lasty
        dz_a = z1-lastz

        dx_c = nextx-lastx
        dy_c = nexty-lasty
        dz_c = nextz-lastz

        if   (abs(dx_a) > Zero):
            line_t = dx_c / dx_a
        elif (abs(dy_a) > Zero):
            line_t = dy_c / dy_a
        elif (abs(dz_a) > Zero):
            line_t = dz_c / dz_a
        else:
            line_t = 0

        ex = dx_c - dx_a * line_t
        ey = dy_c - dy_a * line_t
        ez = dz_c - dz_a * line_t
        et = sqrt(ex*ex + ey*ey + ez*ez)

        L_a = dx_a*dx_a + dy_a*dy_a + dz_a*dz_a
        L_c = dx_c*dx_c + dy_c*dy_c + dz_c*dz_c

        FLAG_arc_last  = FLAG_arc
        FLAG_arc = 0

        FLAG_line_last = FLAG_line
        if  et > Acc or (L_a >= L_c) or FLAG_arc_last == 1:
            FLAG_line = 0
        else:
            FLAG_line = 1
            code="G1"

        ###############
        # Arc Fitting #
        ###############


        if (FLAG_line != 1 and FLAG_line_last !=1 and line_t != 0 and bool(self.arc_fit.get())==1 ):
            dx_b = nextx-x1
            dy_b = nexty-y1
            dz_b = nextz-z1
            L_b  = dx_b*dx_b + dy_b*dy_b + dz_b*dz_b

            if abs(dx_a) > Zero and abs(dx_b) > Zero:
                ma = dy_a/dx_a
                mb = dy_b/dx_b

                if abs(mb-ma) > Zero and  (abs(ma) > Zero or abs(mb) > Zero) :
                    x_center = (ma*mb*(lasty-nexty)+mb*(lastx+x1)-ma*(x1+nextx))/(2*(mb-ma))
                    if abs(ma) > Zero:
                        y_center = -1/ma*(x_center-(lastx+x1)/2) + (lasty+y1)/2
                    elif abs(mb) > Zero:
                        y_center= -1/mb*(x_center-(x1+nextx)/2) + (y1+nexty)/2

                    R_arc = sqrt((x1-x_center)**2 + (y1-y_center)**2)
                    cord_a = sqrt(dx_a**2 + dy_a**2)
                    cord_b = sqrt(dx_b**2 + dy_b**2)
                    cord_limit = 2*R_arc*sin(radians(float(self.segarc.get())))

                    try:
                        sagitta_a = R_arc - sqrt(R_arc**2 - cord_a**2)
                        sagitta_b = R_arc - sqrt(R_arc**2 - cord_b**2)
                        sagitta_min = min(sagitta_a , sagitta_b)
                    except:
                        sagitta_min = 0.0

                    SKIP=0
                    if FLAG_arc_last == 1:
                        if abs(R_last-R_arc)   > Zero or \
                           abs(x_center_last-x_center) > Zero or \
                           abs(y_center_last-y_center) > Zero:
                            SKIP=1

                    if max(cord_a,cord_b) <= cord_limit and \
                                       abs(ez) <= Zero and \
                                       L_a**2 + L_b**2 < L_c**2 and \
                                       cord_a/cord_b >= 1.0/1.5 and \
                                       cord_a/cord_b <= 1.5 and \
                                       sagitta_min > Zero and \
                                       SKIP == 0:

                        seg_sin_test  =   (y1 - lasty)/ cord_a
                        seg_cos_test  =  -(x1 - lastx)/ cord_a
                        phi_test      = Get_Angle(seg_sin_test,seg_cos_test)
                        X_test,Y_test = Transform(x_center-lastx,y_center-lasty,radians(phi_test))
                        code = 'G2' if Y_test > 0.0 else 'G3'
                        x_center_last = x_center
                        y_center_last = y_center
                        R_last = R_arc
                        FLAG_arc = 1
        WRITE=0

        if FLAG_line == 0 and FLAG_arc == 0:
            WRITE=1

        return code,FLAG_arc,R_last,x_center_last,y_center_last,WRITE,FLAG_line
        #####################
        # End Arc Fitting   #
        #####################

    ################################################################################
    def WriteGCode(self):
        global Zero
        self.gcode = []
        SafeZ  =   float(self.ZSAFE.get())
        Depth  =   float(self.ZCUT.get())

        if self.batch.get():
            String = self.default_text
        else:
            String = self.Input.get(1.0,END)

        String_short = String
        max_len = 40
        if len(String)  >  max_len:
            String_short = String[0:max_len] + '___'

        Acc    =   float(self.accuracy.get())

        self.gcode.append('( Code generated by f-engrave-'+version+'.py widget )')
        self.gcode.append('( by Scorch - 2014 )')
        self.gcode.append('(Settings used in f-engrave when this file was created)')
        if self.input_type.get() == "text":
            self.gcode.append("(Engrave Text:" + re.sub(r'\W+', ' ', String_short) + " )" )
        self.gcode.append("(=========================================================)")

        # BOOL
        self.gcode.append('(fengrave_set show_axis  %s )' %( int(self.show_axis.get())     ))
        self.gcode.append('(fengrave_set show_box   %s )' %( int(self.show_box.get())      ))
        self.gcode.append('(fengrave_set show_thick %s )' %( int(self.show_thick.get())    ))
        self.gcode.append('(fengrave_set flip       %s )' %( int(self.flip.get())          ))
        self.gcode.append('(fengrave_set mirror     %s )' %( int(self.mirror.get())        ))
        self.gcode.append('(fengrave_set outer      %s )' %( int(self.outer.get())         ))
        self.gcode.append('(fengrave_set upper      %s )' %( int(self.upper.get())         ))
        self.gcode.append('(fengrave_set v_flop     %s )' %( int(self.v_flop.get())        ))
        self.gcode.append('(fengrave_set v_pplot    %s )' %( int(self.v_pplot.get())       ))
        self.gcode.append('(fengrave_set bmp_long   %s )' %( int(self.bmp_longcurve.get()) ))
        self.gcode.append('(fengrave_set b_carve    %s )' %( int(self.b_carve.get())       ))
        self.gcode.append('(fengrave_set var_dis    %s )' %( int(self.var_dis.get())       ))
        self.gcode.append('(fengrave_set arc_fit    %s )' %( int(self.arc_fit.get())       ))
        self.gcode.append('(fengrave_set ext_char   %s )' %( int(self.ext_char.get())      ))
        self.gcode.append('(fengrave_set useIMGsize %s )' %( int(self.useIMGsize.get())    ))

        # STRING.get()
        self.gcode.append('(fengrave_set YSCALE     %s )' %( self.YSCALE.get()     ))
        self.gcode.append('(fengrave_set XSCALE     %s )' %( self.XSCALE.get()     ))
        self.gcode.append('(fengrave_set LSPACE     %s )' %( self.LSPACE.get()     ))
        self.gcode.append('(fengrave_set CSPACE     %s )' %( self.CSPACE.get()     ))
        self.gcode.append('(fengrave_set WSPACE     %s )' %( self.WSPACE.get()     ))
        self.gcode.append('(fengrave_set TANGLE     %s )' %( self.TANGLE.get()     ))
        self.gcode.append('(fengrave_set TRADIUS    %s )' %( self.TRADIUS.get()    ))
        self.gcode.append('(fengrave_set ZSAFE      %s )' %( self.ZSAFE.get()      ))
        self.gcode.append('(fengrave_set ZCUT       %s )' %( self.ZCUT.get()       ))
        self.gcode.append('(fengrave_set STHICK     %s )' %( self.STHICK.get()     ))
        self.gcode.append('(fengrave_set origin     %s )' %( self.origin.get()     ))
        self.gcode.append('(fengrave_set justify    %s )' %( self.justify.get()    ))
        self.gcode.append('(fengrave_set units      %s )' %( self.units.get()      ))

        self.gcode.append('(fengrave_set xorigin    %s )' %( self.xorigin.get()    ))
        self.gcode.append('(fengrave_set yorigin    %s )' %( self.yorigin.get()    ))
        self.gcode.append('(fengrave_set segarc     %s )' %( self.segarc.get()     ))
        self.gcode.append('(fengrave_set accuracy   %s )' %( self.accuracy.get()   ))

        self.gcode.append('(fengrave_set FEED       %s )' %( self.FEED.get()       ))
        self.gcode.append('(fengrave_set fontfile   \042%s\042 )' %( self.fontfile.get() ))
        self.gcode.append('(fengrave_set H_CALC     %s )' %( self.H_CALC.get()     ))
        self.gcode.append('(fengrave_set plotbox    %s )' %( self.plotbox.get()    ))
        self.gcode.append('(fengrave_set boxgap     %s )' %( self.boxgap.get()    ))
        self.gcode.append('(fengrave_set cut_type    %s )' %( self.cut_type.get()    ))
        self.gcode.append('(fengrave_set v_bit_angle %s )' %( self.v_bit_angle.get() ))
        self.gcode.append('(fengrave_set v_bit_dia   %s )' %( self.v_bit_dia.get()   ))
        self.gcode.append('(fengrave_set v_drv_crner %s )' %( self.v_drv_crner.get() ))
        self.gcode.append('(fengrave_set v_stp_crner %s )' %( self.v_stp_crner.get() ))
        self.gcode.append('(fengrave_set v_step_len  %s )' %( self.v_step_len.get()  ))
        self.gcode.append('(fengrave_set v_acc       %s )' %( self.v_acc.get()       ))
        self.gcode.append('(fengrave_set v_depth_lim  %s )' %( self.v_depth_lim.get() ))

        self.gcode.append('(fengrave_set v_check_all %s )' %( self.v_check_all.get() ))
        self.gcode.append('(fengrave_set bmp_turnp   %s )' %( self.bmp_turnpol.get()      ))
        self.gcode.append('(fengrave_set bmp_turds   %s )' %( self.bmp_turdsize.get()     ))
        self.gcode.append('(fengrave_set bmp_alpha   %s )' %( self.bmp_alphamax.get()     ))
        self.gcode.append('(fengrave_set bmp_optto   %s )' %( self.bmp_opttolerance.get() ))

        self.gcode.append('(fengrave_set fontdir    \042%s\042 )' %( self.fontdir.get()  ))
        self.gcode.append('(fengrave_set gpre        %s )' %( self.gpre.get()         ))
        self.gcode.append('(fengrave_set gpost       %s )' %( self.gpost.get()        ))

        self.gcode.append('(fengrave_set imagefile   \042%s\042 )' %( self.IMAGE_FILE ))
        self.gcode.append('(fengrave_set input_type  %s )' %( self.input_type.get() ))

        self.gcode.append('(fengrave_set clean_dia   %s )' %( self.clean_dia.get()  ))
        self.gcode.append('(fengrave_set clean_step  %s )' %( self.clean_step.get() ))
        self.gcode.append('(fengrave_set clean_w     %s )' %( self.clean_w.get()    ))
        self.gcode.append('(fengrave_set clean_v     %s )' %( self.clean_v.get()    ))
        clean_out = ("%d,%d,%d,%d,%d,%d" %(self.clean_P.get(),self.clean_X.get(),self.clean_Y.get(),\
            self.v_clean_P.get(),self.v_clean_Y.get(),self.v_clean_X.get()) )
        self.gcode.append('(fengrave_set clean_paths  %s )' %( clean_out ))

        str_data=''
        cnt = 0
        for char in String:
           if cnt > 10:
               str_data = str_data + ')'
               self.gcode.append('(fengrave_set TCODE   %s' %(str_data))
               str_data=''
               cnt=0
           str_data = str_data + ' %03d ' %( ord(char) )
           cnt = cnt + 1
        str_data = str_data + ')'
        self.gcode.append('(fengrave_set TCODE   %s' %(str_data))

        self.gcode.append('( Fontfile: %s )' %(self.fontfile.get()))


        if self.units.get() == "in":
            dp=4
            dpfeed=2
        else:
            dp=3
            dpfeed=1
        #FORMAT = '#1 = %%.%df  ( Safe Z )' %(dp)

        if not self.var_dis.get():
            FORMAT = '#1 = %%.%df  ( Safe Z )' %(dp)
            self.gcode.append(FORMAT %(SafeZ))
            FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' %(dp)
            self.gcode.append(FORMAT %(Depth))
            safe_val  = '#1'
            depth_val = '#2'
        else:
            FORMAT = '%%.%df' %(dp)
            safe_val  = FORMAT %(SafeZ)
            depth_val = FORMAT %(Depth)

        self.gcode.append("(#########################################################)")
        # G90        ; Sets absolute distance mode
        self.gcode.append('G90')
        # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
        if bool(self.arc_fit.get()):
            self.gcode.append('G91.1')
        if self.units.get() == "in":
            # G20 ; sets units to inches
            self.gcode.append('G20')
        else:
            # G21 ; sets units to mm
            self.gcode.append('G21')

        for line in self.gpre.get().split('|'):
            self.gcode.append(line)

        FORMAT = 'F%%.%df  ( Set Feed Rate )' %(dpfeed)
        self.gcode.append(FORMAT %(float(self.FEED.get())))
        self.gcode.append( 'G0 Z%s' %(safe_val))

        oldx = oldy = -99990.0
        first_stroke = True

        if self.cut_type.get() == "engrave":
            ##########################
            ###   Create ECOORDS   ###
            ##########################
            loop=0
            ecoords = []
            for line in self.coords:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                x2 = XY[2]
                y2 = XY[3]
                dx = oldx - x1
                dy = oldy - y1
                dist = sqrt(dx*dx + dy*dy)
                # check and see if we need to move to a new discontinuous start point
                if (dist > Acc) or first_stroke:
                    loop = loop+1
                    first_stroke = False
                    ecoords.append([x1,y1,loop])
                ecoords.append([x2,y2,loop])
                oldx, oldy = x2, y2

            order_out=self.Sort_Paths(ecoords)

            ###########################
            dist = 999
            lastx=-999
            lasty=-999
            lastz= 0
            z1   = 0
            nextz= 0

            self.gcode.append("G0 Z%s" %(safe_val))
            for line in order_out:
                temp=line
                if temp[0] > temp[1]:
                    step = -1
                else:
                    step = 1

                R_last         = 999
                x_center_last  = 999
                y_center_last  = 999
                FLAG_arc = 0
                FLAG_line = 0
                code=" "

                loop_old = -1
                for i in range(temp[0],temp[1]+step,step):
                    x1   = ecoords[i][0]
                    y1   = ecoords[i][1]
                    loop = ecoords[i][2]

                    if ( i+1 < temp[1]+step ):
                        nextx    = ecoords[i+1][0]
                        nexty    = ecoords[i+1][1]
                        nextloop = ecoords[i+1][2]
                    else:
                        nextx    =  0
                        nexty    =  0
                        nextloop =  -99 #don't change this dummy number it is used below

                    # check and see if we need to move to a new discontinuous start point
                    if (loop != loop_old):
                        dx = x1-lastx
                        dy = y1-lasty
                        dist = sqrt(dx*dx + dy*dy)
                        if dist > Acc:
                            # lift engraver
                            self.gcode.append("G0 Z%s" %(safe_val))
                            # rapid to current position

                            FORMAT = 'G0 X%%.%df Y%%.%df'%(dp,dp)
                            self.gcode.append(FORMAT %(x1,y1))
                            # drop cutter
                            self.gcode.append('G1 Z%s' %(depth_val))

                            x_center_last = 0
                            y_center_last = 0
                            R_last = 0
                            FLAG_arc = 0
                            FLAG_line = 0
                            code=" "
                            lastx = x1
                            lasty = y1
                    else:
                        ########################################
                        ### Line fit and arc fit (curve fit) ###
                        ########################################
                        [code,FLAG_arc,R_last,x_center_last,y_center_last,WRITE,FLAG_line] = \
                            self.Line_Arc_Fit(lastx,lasty,lastz,x1,y1,z1,\
                                              nextx,nexty,nextz,\
                                              FLAG_arc,code,\
                                              R_last,x_center_last,y_center_last,FLAG_line)

                        if ( WRITE == 1 or nextloop == -99):
                            if (code == "G2" or code == "G3"):
                                R_check_1 = abs((x1-x_center_last   )**2+(y1-y_center_last   )**2 - R_last**2)
                                R_check_2 = abs((lastx-x_center_last)**2+(lasty-y_center_last)**2 - R_last**2)
                                if  R_check_1 > Zero or  R_check_2 > Zero:
                                    fmessage("-- G-Code Curve Fitting Anomaly - Check Output --")
                                    self.gcode.append('(---Curve Fitting Anomaly - Check Output. Error = %.6f ---)' %(max(R_check_1,R_check_2)))

                                    FORMAT = 'G1 X%%.%df Y%%.%df' %(dp,dp)
                                    self.gcode.append(FORMAT %(lastx,lasty))
                                    self.gcode.append(FORMAT %(x1,y1))
                                    self.gcode.append('(------------------ End Anomoly Resolution -------------------)')
                                else:
                                    Ival = x_center_last - lastx
                                    Jval = y_center_last - lasty
                                    FORMAT = '%%s X%%.%df Y%%.%df I%%.%df J%%.%df' %(dp,dp,dp,dp)
                                    self.gcode.append(FORMAT %(code,x1,y1,Ival,Jval))
                                    ######################################################################
                                    # This is the code for the old format for arcs
                                    #FORMAT = '%%s X%%.%df Y%%.%df R%%.%df' %(dp,dp,dp)
                                    #self.gcode.append(FORMAT %(code,x1,y1,R_last))
                                    ######################################################################
                            else:
                                FORMAT = 'G1 X%%.%df Y%%.%df' %(dp,dp)
                                self.gcode.append(FORMAT %(x1,y1))
                            x_center_last = 0
                            y_center_last = 0
                            R_last = 0
                            FLAG_arc = 0
                            FLAG_line = 0
                            code=" "
                            lastx=x1
                            lasty=y1
                        ##############################
                        # End Line and Arc Fitting   #
                        ##############################
                    loop_old = loop
        else:
            # V-carve stuff
            ##########################
            ###   find loop ends   ###
            ##########################
            Lbeg=[]
            Lend=[]
            Lbeg.append(0)
            if len(self.vcoords) > 0:
                loop_old=self.vcoords[0][3]
                for i in range(1,len(self.vcoords)):
                    loop = self.vcoords[i][3]
                    if loop != loop_old:
                        Lbeg.append(i)
                        Lend.append(i-1)
                    loop_old=loop
                Lend.append(i)
                #####################################################
                # Find new order based on distance to next begining #
                #####################################################
                order_out = []
                order_out.append([Lbeg[0],Lend[0]])
                inext = 0
                total=len(Lbeg)
                for i in range(total-1):
                    ii=Lend.pop(inext)
                    Lbeg.pop(inext)
                    Xcur = self.vcoords[ii][0]
                    Ycur = self.vcoords[ii][1]

                    dx = Xcur - self.vcoords[ Lbeg[0] ][0]
                    dy = Ycur - self.vcoords[ Lbeg[0] ][1]
                    min_dist = dx*dx + dy*dy

                    inext=0
                    for j in range(1,len(Lbeg)):
                        dx = Xcur - self.vcoords[ Lbeg[j] ][0]
                        dy = Ycur - self.vcoords[ Lbeg[j] ][1]
                        dist = dx*dx + dy*dy
                        if dist < min_dist:
                            min_dist=dist
                            inext=j
                    order_out.append([Lbeg[inext],Lend[inext]])
                #####################################################
                new_coords=[]
                for line in order_out:
                    temp=line
                    for i in range(temp[0],temp[1]+1):
                        new_coords.append(self.vcoords[i])

                loop_old = -1
                half_angle = radians( float(self.v_bit_angle.get())/2.0 )
                bit_radius = float(self.v_bit_dia.get())/2.0

                R_last         = 999
                x_center_last  = 999
                y_center_last  = 999
                FLAG_arc = 0
                FLAG_line = 0
                code=" "

                v_index=-1
                #for line in xrange(len(new_coords)):
                while v_index < len(new_coords)-1:
                    v_index = v_index + 1
                    x1   = new_coords[v_index][0]
                    y1   = new_coords[v_index][1]
                    r1   = new_coords[v_index][2]
                    loop = new_coords[v_index][3]

                    if ( v_index+1 < len(new_coords) ):
                        nextx    = new_coords[v_index+1][0]
                        nexty    = new_coords[v_index+1][1]
                        nextr    = new_coords[v_index+1][2]
                        nextloop = new_coords[v_index+1][3]
                    else:
                        nextx    =  0
                        nexty    =  0
                        nextr    =  0
                        nextloop =  -99 #don't change this dummy number it is used below

                    #if float(self.v_bit_angle.get()) == 180.0:
                    if self.b_carve.get():
                        theta =  acos(r1 / bit_radius)
                        z1    = -bit_radius*(1- sin(theta))

                        next_theta =  acos(nextr / bit_radius)
                        nextz      = -bit_radius*(1- sin(next_theta))
                    else:
                        z1    = -r1   /tan(half_angle)
                        nextz = -nextr/tan(half_angle)


                    # check and see if we need to move to a new discontinuous start point
                    if (loop != loop_old):
                        # lift engraver
                        self.gcode.append("G0 Z%s" %(safe_val))
                        # rapid to current position
                        FORMAT = 'G0 X%%.%df Y%%.%df' %(dp,dp)
                        self.gcode.append(FORMAT %(x1,y1))
                        # drop cutter to z depth
                        FORMAT = 'G1 Z%%.%df'  %(dp)
                        self.gcode.append(FORMAT %(z1))
                        lastx=x1
                        lasty=y1
                        lastz=z1
                        x_center_last = 0
                        y_center_last = 0
                        R_last = 0
                        FLAG_arc = 0
                        FLAG_line = 0
                        code=" "

                    else:
                        ########################################
                        ### Line fit and arc fit (curve fit) ###
                        ########################################
                        [code,FLAG_arc,R_last,x_center_last,y_center_last,WRITE,FLAG_line] = \
                            self.Line_Arc_Fit(lastx,lasty,lastz,x1,y1,z1,\
                                              nextx,nexty,nextz,\
                                              FLAG_arc,code,\
                                              R_last,x_center_last,y_center_last,FLAG_line)

                        if ( WRITE == 1 or nextloop == -99):
                            if (code == "G2" or code == "G3"):
                                R_check_1 = abs((x1-x_center_last   )**2+(y1-y_center_last   )**2 - R_last**2)
                                R_check_2 = abs((lastx-x_center_last)**2+(lasty-y_center_last)**2 - R_last**2)
                                if  R_check_1 > Zero or  R_check_1 > Zero:
                                    fmessage("-- G-Code Curve Fitting Anomaly - Check Output --")
                                    self.gcode.append('(---Curve Fitting Anomaly - Check Output. Error = %.6f ---)' %(max(R_check_1,R_check_2)))

                                    FORMAT = 'G1 X%%.%df Y%%.%df Z%%.%df' %(dp,dp,dp)
                                    self.gcode.append(FORMAT %(lastx,lasty,lastz))
                                    self.gcode.append(FORMAT %(x1,y1,z1))
                                    self.gcode.append('(------------------ End Anomoly Resolution -------------------)')
                                else:
                                    Ival = x_center_last - lastx
                                    Jval = y_center_last - lasty
                                    FORMAT = '%%s X%%.%df Y%%.%df I%%.%df J%%.%df Z%%.%df' %(dp,dp,dp,dp,dp)
                                    self.gcode.append(FORMAT %(code,x1,y1,Ival,Jval,z1))
                                    ######################################################################
                                    # This is the code for the old format for arcs
                                    #FORMAT = '%%s X%%.%df Y%%.%df R%%.%df' %(dp,dp,dp)
                                    #self.gcode.append(FORMAT %(code,x1,y1,R_last))
                                    ######################################################################
                            else:
                                FORMAT = 'G1 X%%.%df Y%%.%df Z%%.%df' %(dp,dp,dp)
                                self.gcode.append(FORMAT %(x1,y1,z1))
                            lastx=x1
                            lasty=y1
                            lastz=z1
                            x_center_last = 0
                            y_center_last = 0
                            R_last = 0
                            FLAG_arc = 0
                            FLAG_line = 0
                            code=" "
                        ##############################
                        # End Line and Arc Fitting   #
                        ##############################
                    loop_old = loop
            # V-carve stuff

        # Make Circle
        XOrigin    =  float(self.xorigin.get())
        YOrigin    =  float(self.yorigin.get())
        Radius_plot=  float(self.RADIUS_PLOT)
        if Radius_plot != 0 and self.cut_type.get() == "engrave":
            self.gcode.append('G0 Z%s' %(safe_val))

            FORMAT = 'G0 X%%.%df Y%%.%df' %(dp,dp)
            self.gcode.append(FORMAT  %(-Radius_plot - self.Xzero + XOrigin, YOrigin - self.Yzero))
            self.gcode.append('G1 Z%s' %(depth_val))
            FORMAT = 'G2 I%%.%df J%%.%df' %(dp,dp)
            self.gcode.append(FORMAT %( Radius_plot, 0.0))
        # End Circle

        self.gcode.append( 'G0 Z%s' %(safe_val))  # final engraver up

        for line in self.gpost.get().split('|'):
            self.gcode.append(line)

    ################################################################################

    #############################
    # Write Cleanup G-code File #
    #############################
    def WRITE_CLEAN_UP(self,bit_type="straight"):
        global Zero
        self.gcode = []
        SafeZ  =   float(self.ZSAFE.get())
        BitDia =   float(self.clean_dia.get())

        self.calc_depth_limit()
        Depth = float(self.maxcut.get())

        Acc    =   float(self.accuracy.get())
        Units  =   self.units.get()

        self.gcode.append('( Code generated by f-engrave-'+version+'.py widget )')
        self.gcode.append('( by Scorch - 2014 )')
        self.gcode.append('( This file is a secondary operation for cleaning up a V-carve )')

        if bit_type == "straight":
            coords_out = self.clean_coords_sort
            self.gcode.append('( The tool paths were calculated based on using a bit with a)')
            self.gcode.append('( Diameter of %.4f %s)' %(BitDia, Units))
        else:
            coords_out = self.v_clean_coords_sort
            self.gcode.append('( The tool paths were calculated based on using a v-bit with a)')
            self.gcode.append('( angle of %.4f Degrees)' %(float(self.v_bit_angle.get())) )

        self.gcode.append("(=========================================================)")


        if self.units.get() == "in":
            dp=4
            dpfeed=2
        else:
            dp=3
            dpfeed=1
        #FORMAT = '%%.%df' %(dp)

        if not self.var_dis.get():
            FORMAT = '#1 = %%.%df  ( Safe Z )' %(dp)
            self.gcode.append(FORMAT %(SafeZ))
            FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' %(dp)
            self.gcode.append(FORMAT %(Depth))
            safe_val  = '#1'
            depth_val = '#2'
        else:
            FORMAT = '%%.%df' %(dp)
            safe_val  = FORMAT %(SafeZ)
            depth_val = FORMAT %(Depth)

        self.gcode.append("(#########################################################)")
        # G90        ; Sets absolute distance mode
        self.gcode.append('G90')
        # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
        if bool(self.arc_fit.get()):
            self.gcode.append('G91.1')
        if self.units.get() == "in":
            # G20 ; sets units to inches
            self.gcode.append('G20')
        else:
            # G21 ; sets units to mm
            self.gcode.append('G21')

        for line in self.gpre.get().split('|'):
            self.gcode.append(line)

        FORMAT = 'F%%.%df  ( Set Feed Rate )' %(dpfeed)
        self.gcode.append(FORMAT %(float(self.FEED.get())))
        self.gcode.append( 'G0 Z%s' %(safe_val))

        oldx = oldy = -99990.0
        first_stroke = True
        ########################################################################
        # The clean coords have already been sorted so we can just write them  #
        ########################################################################

        order_out=self.Sort_Paths(coords_out,3)
        new_coords=[]
        for line in order_out:
            temp=line
            if (temp[0] < temp[1]):
                step=1
            else:
                step=-1
            for i in range(temp[0],temp[1]+step,step):
                new_coords.append(coords_out[i])
        coords_out=new_coords

        if len(coords_out) > 0:
            loop_old = -1
            FLAG_arc = 0
            FLAG_line = 0
            code=" "
            v_index=-1
            while v_index < len(coords_out)-1:
                v_index = v_index + 1
                x1   = coords_out[v_index][0]
                y1   = coords_out[v_index][1]
                r1   = coords_out[v_index][2]
                loop = coords_out[v_index][3]

                if ( v_index+1 < len(coords_out) ):
                    nextx    = coords_out[v_index+1][0]
                    nexty    = coords_out[v_index+1][1]
                    nextr    = coords_out[v_index+1][2]
                    nextloop = coords_out[v_index+1][3]
                else:
                    nextx    =  0
                    nexty    =  0
                    nextr    =  0
                    nextloop =  -99

                # check and see if we need to move to a new discontinuous start point
                if (loop != loop_old):
                    # lift engraver
                    self.gcode.append("G0 Z%s" %(safe_val))
                    # rapid to current position
                    FORMAT = 'G0 X%%.%df Y%%.%df' %(dp,dp)
                    self.gcode.append(FORMAT %(x1,y1))
                    # drop cutter to z depth
                    self.gcode.append("G1 Z%s" %(depth_val))
                    lastx=x1
                    lasty=y1
                else:
                    dx_a = x1-lastx
                    dy_a = y1-lasty

                    dx_c = nextx-lastx
                    dy_c = nexty-lasty

                    if   (abs(dx_a) > Zero):
                        line_t = dx_c / dx_a
                    elif (abs(dy_a) > Zero):
                        line_t = dy_c / dy_a
                    else:
                        line_t   =  0
                        nextloop = -99

                    ex = dx_c - dx_a * line_t
                    ey = dy_c - dy_a * line_t
                    et = sqrt(ex*ex + ey*ey)

                    L_a = dx_a*dx_a + dy_a*dy_a
                    L_c = dx_c*dx_c + dy_c*dy_c

                    if ( (et > Zero) or (nextloop != loop) or (L_a >= L_c)):
                        FORMAT = 'G1 X%%.%df Y%%.%df' %(dp,dp)
                        self.gcode.append(FORMAT %(x1,y1))
                        lastx=x1
                        lasty=y1
                loop_old = loop
        self.gcode.append( 'G0 Z%s' %(safe_val))  # final engraver up

        for line in self.gpost.get().split('|'):
            self.gcode.append(line)
        ###################################

    def WriteSVG(self):
        self.svgcode = writers.svg(self)

    def CopyClipboard_GCode(self):
        self.clipboard_clear()
        if (self.Check_All_Variables() > 0):
            return
        self.WriteGCode()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def CopyClipboard_SVG(self):
        self.clipboard_clear()
        self.WriteSVG()
        for line in self.svgcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        if (self.Check_All_Variables() > 0):
            return
        self.WriteGCode()
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
        self.zoomy  = event.y
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

    def mousePan(self,event):
        all = self.PreviewCanvas.find_all()
        dx = event.x-self.panx
        dy = event.y-self.pany
        for i in all:
            self.PreviewCanvas.move(i, dx, dy)
        self.lastx = self.lastx + dx
        self.lasty = self.lasty + dy
        self.panx = event.x
        self.pany = event.y

    def Recalculate_Click(self, event):
        self.DoIt()

    def Settings_ReLoad_Click(self, event, arg1="", arg2=""):
        win_id=self.grab_current()
        if self.input_type.get() == "text":
            self.Read_font_file()
        else:
            self.Read_image_file()
        self.DoIt()
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def VCARVE_Recalculate_Click(self):
        win_id=self.grab_current()
        self.V_Carve_Calc_Click()
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def CLEAN_Recalculate_Click(self):
        win_id=self.grab_current()
        if self.clean_segment == []:
            mess = "Calculate V-Carve must be executed\n"
            mess = mess + "prior to Calculating Cleanup"
            message_box("Cleanup Info",mess)
        else:
            stop = self.Clean_Calc_Click("straight")
            if stop != 1:
                self.Clean_Calc_Click("v-bit")
            self.Plot_Data()

        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_Clean_Click(self):
        win_id=self.grab_current()
        if (self.clean_P.get() + \
            self.clean_X.get() + \
            self.clean_Y.get() + \
            self.v_clean_P.get() + \
            self.v_clean_Y.get() + \
            self.v_clean_X.get()) != 0:
            if self.clean_coords_sort == []:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message_box("Cleanup Info",mess)
            else:
                self.menu_File_Save_clean_G_Code_File("straight")
        else:
            mess =        "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no V Cleanup paths were found)"
            message_box("Cleanup Info",mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_V_Clean_Click(self):
        win_id=self.grab_current()
        if (self.clean_P.get() + \
            self.clean_X.get() + \
            self.clean_Y.get() + \
            self.v_clean_P.get() + \
            self.v_clean_Y.get() + \
            self.v_clean_X.get()) != 0:
            if self.v_clean_coords_sort == []:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving V Cleanup G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message_box("Cleanup Info",mess)
            else:
                self.menu_File_Save_clean_G_Code_File("v-bit")
        else:
            mess =        "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no Cleanup paths were found)"
            message_box("Cleanup Info",mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    ######################

    def Close_Current_Window_Click(self):
        win_id=self.grab_current()
        win_id.destroy()

    def Stop_Click(self, event):
        global STOP_CALC
        STOP_CALC=1

    def calc_vbit_dia(self):
        bit_dia   = float(self.v_bit_dia.get())
        depth_lim = float(self.v_depth_lim.get())
        if depth_lim < 0.0:
            if self.b_carve.get():
                R = bit_dia / 2.0
                bit_dia = 2*sqrt( R**2 - (R+depth_lim)**2)
            else:
                half_angle = radians( float(self.v_bit_angle.get())/2.0 )
                bit_dia = -2*depth_lim*tan(half_angle)

        return bit_dia

    def calc_depth_limit(self):
        try:
            if self.b_carve.get():
                bit_depth = -float( self.v_bit_dia.get()) / 2.0
            else:
                half_angle = radians( float(self.v_bit_angle.get())/2.0 )
                bit_depth = -float(self.v_bit_dia.get())/2.0 /tan(half_angle)
            depth_lim = float(self.v_depth_lim.get())
            if depth_lim < 0.0:
                self.maxcut.set("%.3f" %(max(bit_depth, depth_lim)))
            else:
                self.maxcut.set("%.3f" %(bit_depth))
        except:
            self.maxcut.set("error")

    # Left Column #
    #############################
    def Entry_Yscale_Check(self):
        try:
            value = float(self.YSCALE.get())
            if  value <= 0.0:
                self.statusMessage.set(" Height should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Yscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check() )
    #############################
    def Entry_Xscale_Check(self):
        try:
            value = float(self.XSCALE.get())
            if  value <= 0.0:
                self.statusMessage.set(" Width should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Xscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check() )
    #############################
    def Entry_Sthick_Check(self):
        try:
            value = float(self.STHICK.get())
            if  value < 0.0:
                self.statusMessage.set(" Thickness should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Sthick_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check() )
    #############################
    def Entry_Lspace_Check(self):
        try:
            value = float(self.LSPACE.get())
            if  value < 0.0:
                self.statusMessage.set(" Line space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Lspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check() )
    #############################
    def Entry_Cspace_Check(self):
        try:
            value = float(self.CSPACE.get())
            if  value < 0.0:
                self.statusMessage.set(" Character space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Cspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check() )
    #############################
    def Entry_Wspace_Check(self):
        try:
            value = float(self.WSPACE.get())
            if  value < 0.0:
                self.statusMessage.set(" Word space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Wspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check() )
    #############################
    def Entry_Tangle_Check(self):
        try:
            value = float(self.TANGLE.get())
            if  value <= -360.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between -360 and 360 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Tangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check() )
    #############################
    def Entry_Tradius_Check(self):
        try:
            value = float(self.TRADIUS.get())
            if  value < 0.0:
                self.statusMessage.set(" Radius should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Tradius_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() )
    # End Left Column #

    # Right Column #
    #############################
    def Entry_Feed_Check(self):
        try:
            value = float(self.FEED.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Feed_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Feed,self.Entry_Feed_Check())
    #############################
    def Entry_Zsafe_Check(self):
        try:
            value = float(self.ZSAFE.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Zsafe_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zsafe,self.Entry_Zsafe_Check())
    #############################
    def Entry_Zcut_Check(self):
        try:
            value = float(self.ZCUT.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Zcut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zcut,self.Entry_Zcut_Check())
    #############################
    # End Right Column #


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
    #############################
    def Entry_Yoffset_Check(self):
        try:
            value = float(self.yorigin.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Yoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yoffset,self.Entry_Yoffset_Check())
    #############################
    def Entry_ArcAngle_Check(self):
        try:
            value = float(self.segarc.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_ArcAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check())
    #############################
    def Entry_Accuracy_Check(self):
        try:
            value = float(self.accuracy.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Accuracy_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check())
    #############################
    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_BoxGap_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BoxGap,self.Entry_BoxGap_Check())
    #############################
    def Fontdir_Click(self, event):
        win_id=self.grab_current()
        newfontdir = askdirectory(mustexist=1,initialdir=self.fontdir.get() )
        if newfontdir != "" and newfontdir != ():
            self.fontdir.set(newfontdir.encode("utf-8"))
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
            if  value < 0.0 or value > 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Vbitangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check() )
        self.calc_depth_limit()

    #############################
    def Entry_Vbitdia_Check(self):
        try:
            value = float(self.v_bit_dia.get())
            if  value <= 0.0:
                self.statusMessage.set(" Diameter should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Vbitdia_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check() )
        self.calc_depth_limit()
    #############################
    def Entry_VDepthLimit_Check(self):
        try:
            value = float(self.v_depth_lim.get())
            if  value > 0.0:
                self.statusMessage.set(" Depth should be less than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_VDepthLimit_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() )
        self.calc_depth_limit()
    #############################
    def Entry_InsideAngle_Check(self):
        try:
            value = float(self.v_drv_crner.get())
            if  value <= 0.0 or value >= 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_InsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() )
    #############################
    def Entry_OutsideAngle_Check(self):
        try:
            value = float(self.v_stp_crner.get())
            if  value <= 180.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between 180 and 360 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_OutsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check() )
    #############################
    def Entry_StepSize_Check(self):
        try:
            value = float(self.v_step_len.get())
            if  value <= 0.0:
                self.statusMessage.set(" Step size should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_StepSize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check() )
    #############################
    def Entry_LoopAcc_Check(self):
        try:
            value = float(self.v_acc.get())
            if  value < 0.0:
                self.statusMessage.set(" Loop Accuracy should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_LoopAcc_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_LoopAcc, self.Entry_LoopAcc_Check() )
    #############################
    def Entry_W_CLEAN_Check(self):
        try:
            value = float(self.clean_w.get())
            if  value <= 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_W_CLEAN_Callback(self, varName, index, mode):
        self.clean_coords = []
        self.entry_set(self.Entry_W_CLEAN, self.Entry_W_CLEAN_Check() )
            #############################
    def Entry_V_CLEAN_Check(self):
        try:
            value = float(self.clean_v.get())
            if  value < 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_V_CLEAN_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check() )
    #############################
    def Entry_CLEAN_DIA_Check(self):
        try:
            value = float(self.clean_dia.get())
            if  value <= 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_CLEAN_DIA_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check() )
    #############################
    def Entry_STEP_OVER_Check(self):
        try:
            value = float(self.clean_step.get())
            if  value <= 0.0:
                self.statusMessage.set(" Step Over should be between 0% and 100% ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_STEP_OVER_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check() )
    #############################

    def Entry_B_Carve_Check(self):
        self.calc_depth_limit()
        try:
            if self.b_carve.get():
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_InsideAngle.configure(state="disabled")
                self.Label_InsideAngle_u.configure(state="disabled")
                self.Entry_InsideAngle.configure(state="disabled")
            else:
                self.Label_Vbitangle.configure(state="normal")
                self.Label_Vbitangle_u.configure(state="normal")
                self.Entry_Vbitangle.configure(state="normal")
                self.Label_photo.configure(state="normal")
                self.Label_InsideAngle.configure(state="normal")
                self.Label_InsideAngle_u.configure(state="normal")
                self.Entry_InsideAngle.configure(state="normal")
        except:
            pass
    def Entry_B_Carve_var_Callback(self, varName, index, mode):
        self.Entry_B_Carve_Check()

    ######################################
    # Bitmap Settings Window Call Backs  #
    ######################################
    def Entry_BMPturdsize_Check(self):
        try:
            value = float(self.bmp_turdsize.get())
            if  value < 1.0:
                self.statusMessage.set(" Step size should be greater or equal to 1.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_BMPturdsize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check() )
    #############################
    def Entry_BMPalphamax_Check(self):
        try:
            value = float(self.bmp_alphamax.get())
            if  value < 0.0 or value > 4.0/3.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_BMPalphamax_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check() )
    #############################
    def Entry_BMPoptTolerance_Check(self):
        try:
            value = float(self.bmp_opttolerance.get())
            if  value < 0.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_BMPoptTolerance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check() )
    #############################

    ##########################################################################
    ##########################################################################
    def Check_All_Variables(self):
        if self.batch.get():
            return 0
        MAIN_error_cnt= \
        self.entry_set(self.Entry_Yscale,  self.Entry_Yscale_Check()  ,2) +\
        self.entry_set(self.Entry_Xscale,  self.Entry_Xscale_Check()  ,2) +\
        self.entry_set(self.Entry_Sthick,  self.Entry_Sthick_Check()  ,2) +\
        self.entry_set(self.Entry_Lspace,  self.Entry_Lspace_Check()  ,2) +\
        self.entry_set(self.Entry_Cspace,  self.Entry_Cspace_Check()  ,2) +\
        self.entry_set(self.Entry_Wspace,  self.Entry_Wspace_Check()  ,2) +\
        self.entry_set(self.Entry_Tangle,  self.Entry_Tangle_Check()  ,2) +\
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() ,2) +\
        self.entry_set(self.Entry_Feed,    self.Entry_Feed_Check()    ,2) +\
        self.entry_set(self.Entry_Zsafe,   self.Entry_Zsafe_Check()   ,2) +\
        self.entry_set(self.Entry_Zcut,    self.Entry_Zcut_Check()    ,2)

        GEN_error_cnt= \
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check() ,2) +\
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check() ,2) +\
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),2) +\
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),2) +\
        self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,2) +\
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check() ,2) +\
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check() ,2) +\
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),2) +\
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),2) +\
        self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,2)

        VCARVE_error_cnt= \
        self.entry_set(self.Entry_Vbitangle,   self.Entry_Vbitangle_Check()   ,2) +\
        self.entry_set(self.Entry_Vbitdia,     self.Entry_Vbitdia_Check()     ,2) +\
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() ,2) +\
        self.entry_set(self.Entry_OutsideAngle,self.Entry_OutsideAngle_Check(),2) +\
        self.entry_set(self.Entry_StepSize,    self.Entry_StepSize_Check()    ,2) +\
        self.entry_set(self.Entry_LoopAcc,     self.Entry_StepSize_Check()    ,2) +\
        self.entry_set(self.Entry_W_CLEAN,     self.Entry_W_CLEAN_Check()     ,2) +\
        self.entry_set(self.Entry_CLEAN_DIA,   self.Entry_CLEAN_DIA_Check()   ,2) +\
        self.entry_set(self.Entry_STEP_OVER,   self.Entry_STEP_OVER_Check()   ,2) +\
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), 2)

        PBM_error_cnt= \
        self.entry_set(self.Entry_BMPoptTolerance,self.Entry_BMPoptTolerance_Check(),2) +\
        self.entry_set(self.Entry_BMPturdsize,    self.Entry_BMPturdsize_Check()    ,2) +\
        self.entry_set(self.Entry_BMPalphamax,    self.Entry_BMPalphamax_Check()    ,2)

        ERROR_cnt = MAIN_error_cnt + GEN_error_cnt + VCARVE_error_cnt +PBM_error_cnt

        if (ERROR_cnt > 0):
            self.statusbar.configure( bg = 'red' )
        if (PBM_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in PBM Settings Window ")
        if (VCARVE_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in V-Carve Settings Window ")
        if (GEN_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in General Settings Window ")
        if (MAIN_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in Main Window ")

        return ERROR_cnt

    ##########################################################################
    ##########################################################################
    def V_Carve_Calc_Click(self):
        if (self.Check_All_Variables() > 0):
            return

        vcalc_status = Toplevel(width=525, height=60)
        # Use grab_set to prevent user input in the main window during calculations
        vcalc_status.grab_set()

        self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT , height=1, anchor=W)
        self.statusbar2.place(x=130+12+12, y=6, width=350, height=30)
        self.statusMessage.set("Starting Calculation")
        self.statusbar.configure( bg = 'yellow' )

        self.stop_button = Button(vcalc_status,text="Stop Calculation")
        self.stop_button.place(x=12, y=17, width=130, height=30)
        self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

        self.Checkbutton_v_pplot = Checkbutton(vcalc_status,text="Plot During V-Carve Calculation", anchor=W)
        self.Checkbutton_v_pplot.place(x=130+12+12, y=34, width=300, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)

        vcalc_status.resizable(0,0)
        vcalc_status.title('Executing V-Carve')
        vcalc_status.iconname("F-Engrave")

        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            vcalc_status.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            fmessage("Unable to create temporary icon file.")

        self.V_Carve_It()
        self.menu_View_Refresh()
        vcalc_status.grab_release()
        try:
            vcalc_status.destroy()
        except:
            pass

    ##########################################################################
    ##########################################################################
    def Clean_Calc_Click(self,bit_type="straight"):
        if (self.Check_All_Variables() > 0):
            return 1

        if self.clean_coords == []:
            vcalc_status = Toplevel(width=525, height=50)
            # Use grab_set to prevent user input in the main window during calculations
            vcalc_status.grab_set()

            self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT , height=1)
            self.statusbar2.place(x=130+12+12, y=12, width=350, height=30)
            self.statusMessage.set("Starting Clean Calculation")
            self.statusbar.configure( bg = 'yellow' )

            self.stop_button = Button(vcalc_status,text="Stop Calculation")
            self.stop_button.place(x=12, y=12, width=130, height=30)
            self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

            vcalc_status.resizable(0,0)
            vcalc_status.title('Executing Clean Area Calculation')
            vcalc_status.iconname("F-Engrave")

            try: #Attempt to create temporary icon bitmap file
                f = open("f_engrave_icon",'w')
                f.write("#define f_engrave_icon_width 16\n")
                f.write("#define f_engrave_icon_height 16\n")
                f.write("static unsigned char f_engrave_icon_bits[] = {\n")
                f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
                f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
                f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
                f.close()
                vcalc_status.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                fmessage("Unable to create temporary icon file.")

            clean_cut = 1
            self.V_Carve_It(clean_cut)
            vcalc_status.grab_release()
            try:
                vcalc_status.destroy()
            except:
                pass
            self.entry_set(self.Entry_W_CLEAN, self.Entry_W_CLEAN_Check() ,1)

        self.Clean_Path_Calc(bit_type)

        if self.clean_coords == []:
            return 1
        else:
            return 0

    def Entry_recalc_var_Callback(self, varName, index, mode):
        self.Recalc_RQD()

    def Entry_units_var_Callback(self):
        if (self.units.get() == 'in') and (self.funits.get()=='mm/min'):
            self.Scale_Linear_Inputs(1/25.4)
            self.funits.set('in/min')
            #self.v_step_len.set("0.01")
            #self.accuracy.set("0.001")
        elif (self.units.get() == 'mm') and (self.funits.get()=='in/min'):
            self.Scale_Linear_Inputs(25.4)
            self.funits.set('mm/min')
            #self.v_step_len.set("0.25")
            #self.accuracy.set("0.025")
        self.Recalc_RQD()

    def Scale_Linear_Inputs(self, factor=1.0):
        try:
            self.YSCALE.set(     '%.3g' %(float(self.YSCALE.get()     )*factor) )
            self.TRADIUS.set(    '%.3g' %(float(self.TRADIUS.get()    )*factor) )
            self.ZSAFE.set(      '%.3g' %(float(self.ZSAFE.get()      )*factor) )
            self.ZCUT.set(       '%.3g' %(float(self.ZCUT.get()       )*factor) )
            self.STHICK.set(     '%.3g' %(float(self.STHICK.get()     )*factor) )
            self.FEED.set(       '%.3g' %(float(self.FEED.get()       )*factor) )
            self.boxgap.set(     '%.3g' %(float(self.boxgap.get()     )*factor) )
            self.v_bit_dia.set(  '%.3g' %(float(self.v_bit_dia.get()  )*factor) )
            self.v_depth_lim.set('%.3g' %(float(self.v_depth_lim.get())*factor) )
            self.v_step_len.set( '%.3g' %(float(self.v_step_len.get() )*factor) )
            self.v_acc.set(      '%.3g' %(float(self.v_acc.get()      )*factor) )
            self.xorigin.set(    '%.3g' %(float(self.xorigin.get()    )*factor) )
            self.yorigin.set(    '%.3g' %(float(self.yorigin.get()    )*factor) )
            self.accuracy.set(   '%.3g' %(float(self.accuracy.get()   )*factor) )
            self.clean_w.set(    '%.3g' %(float(self.clean_w.get()    )*factor) )
            self.clean_v.set(    '%.3g' %(float(self.clean_v.get()    )*factor) )
            self.clean_dia.set(  '%.3g' %(float(self.clean_dia.get()  )*factor) )
        except:
            pass

    def useIMGsize_var_Callback(self): #, varName, index, mode):
        if self.input_type.get() != "text":
            self.Read_image_file()
        try:
            ymx = max(self.font[key].get_ymax() for key in self.font)
            ymn = min(self.font[key].get_ymin() for key in self.font)
            image_height = ymx-ymn
        except:
            if self.units.get() == 'in':
                image_height = 2
            else:
                image_height = 50
        if (self.useIMGsize.get()):
            self.YSCALE.set('%.3g' %(100 * float(self.YSCALE.get()) / image_height ))
        else:
            self.YSCALE.set('%.3g' %(float(self.YSCALE.get()) / 100 * image_height ))

        self.menu_View_Refresh()
        self.Recalc_RQD()
    '''
    def Entry_units_var_Callback(self, varName, index, mode):
        if self.units.get() == 'in':
            self.funits.set('in/min')
            self.v_step_len.set("0.01")
            self.accuracy.set("0.001")
            # Unit conversion code needs to detect if the units are already set to
            # the value new unit system.  Otherwise the factor gets multiplied
            # everytime the radio button is touched
            # Not all values with linear units a included here yet
            # Working List of missing variables:
            # Radius, Line Thickness,

            # change all unit measurements to inches from mm
            #self.FEED.set("{0:.3f}".format(float(self.FEED.get()) / 25.4))
            #self.v_bit_dia.set(("{0:.3f}".format(float(self.v_bit_dia.get()) / 25.4)))
            #self.v_depth_lim.set(("{0:.3f}".format(float(self.v_depth_lim.get()) / 25.4)))
            #self.clean_w.set(("{0:.3f}".format(float(self.clean_w.get()) / 25.4)))
            #self.clean_dia.set(("{0:.3f}".format(float(self.clean_dia.get()) / 25.4)))
            #self.ZSAFE.set(("{0:.3f}".format(float(self.ZSAFE.get()) / 25.4)))
            #self.ZCUT.set(("{0:.3f}".format(float(self.ZCUT.get()) / 25.4)))
            #self.YSCALE.set(("{0:.3f}".format(float(self.YSCALE.get()) / 25.4)))
        else:
            self.funits.set('mm/min')
            self.v_step_len.set("0.25")
            self.accuracy.set("0.025")
            # change all unit measurements to mm from inches
            #self.FEED.set("{0:.3f}".format(float(self.FEED.get()) * 25.4))
            #self.v_bit_dia.set(("{0:.3f}".format(float(self.v_bit_dia.get()) * 25.4)))
            #self.v_depth_lim.set(("{0:.3f}".format(float(self.v_depth_lim.get()) * 25.4)))
            #self.clean_w.set(("{0:.3f}".format(float(self.clean_w.get()) * 25.4)))
            #self.clean_dia.set(("{0:.3f}".format(float(self.clean_dia.get()) * 25.4)))
            #self.ZSAFE.set(("{0:.3f}".format(float(self.ZSAFE.get()) * 25.4)))
            #self.ZCUT.set(("{0:.3f}".format(float(self.ZCUT.get()) * 25.4)))
            #self.YSCALE.set(("{0:.3f}".format(float(self.YSCALE.get()) * 25.4)))
        self.Recalc_RQD()
    '''

    def Listbox_1_Click(self, event):
        labelL = []
        for i in self.Listbox_1.curselection():
            labelL.append( self.Listbox_1.get(i))
        try:
            self.fontfile.set(labelL[0])
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Listbox_Key_Up(self, event):
        try:
            select_new = int(self.Listbox_1.curselection()[0])-1
        except:
            select_new = self.Listbox_1.size()-2
        self.Listbox_1.selection_clear(0,END)
        self.Listbox_1.select_set(select_new)
        try:
            self.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Listbox_Key_Down(self, event):
        try:
            select_new = int(self.Listbox_1.curselection()[0])+1
        except:
            select_new = 1
        self.Listbox_1.selection_clear(0,END)
        self.Listbox_1.select_set(select_new)
        try:
            self.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Entry_fontdir_Callback(self, varName, index, mode):
        self.Listbox_1.delete(0, END)
        self.Listbox_1.configure( bg = self.NormalColor )
        try:
            font_files=os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files=" "
        for name in font_files:
            if str.find(name.upper(),'.CXF') != -1 \
            or (str.find(name.upper(),'.TTF') != -1 and self.TTF_AVAIL ):
                self.Listbox_1.insert(END, name)
        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")
        self.Read_font_file()
        self.Recalc_RQD()
    # End General Settings Callbacks

    def menu_File_Open_G_Code_File(self):
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR
        fileselect = askopenfilename(filetypes=[("F-Engrave G-code Files","*.ngc"),\
                                                ("All Files","*")],\
                                                 initialdir=init_dir)

        if fileselect != '' and fileselect != ():
            self.Open_G_Code_File(fileselect)

    def menu_File_Open_DXF_File(self):
        init_dir = os.path.dirname(self.IMAGE_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        if self.POTRACE_AVAIL == True:

            fileselect = askopenfilename(filetypes=[("DXF/Bitmap Files", ("*.dxf","*.bmp","*.pbm","*.ppm","*.pgm","*.pnm")),
                                                    ("DXF Files","*.dxf"),\
                                                    ("Bitmap Files",("*.bmp","*.pbm","*.ppm","*.pgm","*.pnm")),\
                                                    ("All Files","*")],\
                                                     initialdir=init_dir)
        else:
            fileselect = askopenfilename(filetypes=[("DXF Files","*.dxf"),
                                                    ("All Files","*")],
                                                    initialdir=init_dir)

        if fileselect != '' and fileselect != ():
            self.IMAGE_FILE = fileselect
            self.Read_image_file()
            self.DoIt()

    def Open_G_Code_File(self,filename):
        self.delay_calc = 1
        boxsize = "0"
        try:
            fin = open(filename, 'r')
        except Exception, e:
            print e
            fmessage("Unable to open file: %s" % (filename))
            return
        text_codes=[]
        ident = "fengrave_set"
        for line in fin:
            if ident in line:
                if "TCODE" in line:
                    for chr in line[line.find("TCODE"):].split():
                        try:
                            text_codes.append(int(unicode(chr)) )
                        except:
                            pass
                # BOOL
                elif "show_axis"  in line:
                    self.show_axis.set(line[line.find("show_axis"):].split()[1])
                elif "show_box"   in line:
                    self.show_box.set(line[line.find("show_box"):].split()[1])
                elif "show_thick" in line:
                    self.show_thick.set(line[line.find("show_thick"):].split()[1])
                elif "flip"       in line:
                    self.flip.set(line[line.find("flip"):].split()[1])
                elif "mirror"     in line:
                    self.mirror.set(line[line.find("mirror"):].split()[1])
                elif "outer"  in line:
                    self.outer.set(line[line.find("outer"):].split()[1])
                elif "upper"      in line:
                   self.upper.set(line[line.find("upper"):].split()[1])
                elif "v_flop"      in line:
                   self.v_flop.set(line[line.find("v_flop"):].split()[1])
                elif "v_pplot"      in line:
                   self.v_pplot.set(line[line.find("v_pplot"):].split()[1])
                elif "bmp_long"      in line:
                   self.bmp_longcurve.set(line[line.find("bmp_long"):].split()[1])
                elif "arc_fit"   in line:
                   self.arc_fit.set(line[line.find("arc_fit"):].split()[1])
                elif "ext_char"   in line:
                   self.ext_char.set(line[line.find("ext_char"):].split()[1])
                elif "useIMGsize"   in line:
                   self.useIMGsize.set(line[line.find("useIMGsize"):].split()[1])

                # STRING
                elif "fontdir"    in line:
                    self.fontdir.set(line[line.find("fontdir"):].split("\042")[1])
                elif "gpre"       in line:
                    gpre_tmp = ""
                    for word in line[line.find("gpre"):].split():
                        if word != ")" and word != "gpre":
                            gpre_tmp = gpre_tmp + word + " "
                    self.gpre.set(gpre_tmp)
                elif "gpost"      in line:
                    gpost_tmp = ""
                    for word in line[line.find("gpost"):].split():
                        if word != ")" and word != "gpost":
                            gpost_tmp = gpost_tmp + word + " "
                    self.gpost.set(gpost_tmp)

                # STRING.set()
                elif "YSCALE"     in line:
                    self.YSCALE.set(line[line.find("YSCALE"):].split()[1])
                elif "XSCALE"     in line:
                    self.XSCALE.set(line[line.find("XSCALE"):].split()[1])
                elif "LSPACE"     in line:
                    self.LSPACE.set(line[line.find("LSPACE"):].split()[1])
                elif "CSPACE"     in line:
                    self.CSPACE.set(line[line.find("CSPACE"):].split()[1])
                elif "WSPACE"     in line:
                    self.WSPACE.set(line[line.find("WSPACE"):].split()[1])
                elif "TANGLE"     in line:
                    self.TANGLE.set(line[line.find("TANGLE"):].split()[1])
                elif "TRADIUS"    in line:
                    self.TRADIUS.set(line[line.find("TRADIUS"):].split()[1])
                elif "ZSAFE"      in line:
                    self.ZSAFE.set(line[line.find("ZSAFE"):].split()[1])
                elif "ZCUT"       in line:
                    self.ZCUT.set(line[line.find("ZCUT"):].split()[1])
                elif "STHICK"     in line:
                    self.STHICK.set(line[line.find("STHICK"):].split()[1])

                elif "xorigin"    in line:
                    self.xorigin.set(line[line.find("xorigin"):].split()[1])
                elif "yorigin"    in line:
                    self.yorigin.set(line[line.find("yorigin"):].split()[1])
                elif "segarc"     in line:
                    self.segarc.set(line[line.find("segarc"):].split()[1])
                elif "accuracy"   in line:
                    self.accuracy.set(line[line.find("accuracy"):].split()[1])

                elif "origin"     in line:
                    self.origin.set(line[line.find("origin"):].split()[1])
                elif "justify"    in line:
                    self.justify.set(line[line.find("justify"):].split()[1])
                elif "units"      in line:
                    self.units.set(line[line.find("units"):].split()[1])
                elif "FEED"       in line:
                    self.FEED.set(line[line.find("FEED"):].split()[1])
                elif "fontfile"   in line:
                    self.fontfile.set(line[line.find("fontfile"):].split("\042")[1])
                elif "H_CALC"     in line:
                    self.H_CALC.set(line[line.find("H_CALC"):].split()[1])
                elif "plotbox"    in line:
                    self.plotbox.set(line[line.find("plotbox"):].split()[1])
                elif "boxgap"    in line:
                    self.boxgap.set(line[line.find("boxgap"):].split()[1])
                elif "boxsize"    in line:
                    boxsize = line[line.find("boxsize"):].split()[1]
                elif "cut_type"    in line:
                    self.cut_type.set(line[line.find("cut_type"):].split()[1])
                elif "v_bit_angle"    in line:
                    self.v_bit_angle.set(line[line.find("v_bit_angle"):].split()[1])
                elif "v_bit_dia"    in line:
                    self.v_bit_dia.set(line[line.find("v_bit_dia"):].split()[1])
                elif "v_drv_crner"    in line:
                    self.v_drv_crner.set(line[line.find("v_drv_crner"):].split()[1])
                elif "v_stp_crner"    in line:
                    self.v_stp_crner.set(line[line.find("v_stp_crner"):].split()[1])
                elif "v_step_len"    in line:
                    self.v_step_len.set(line[line.find("v_step_len"):].split()[1])
                elif "v_acc"    in line:
                    self.v_acc.set(line[line.find("v_acc"):].split()[1])
                elif "b_carve"    in line:
                    self.b_carve.set(line[line.find("b_carve"):].split()[1])
                elif "var_dis"    in line:
                    self.var_dis.set(line[line.find("var_dis"):].split()[1])
                elif "v_depth_lim"    in line:
                    self.v_depth_lim.set(line[line.find("v_depth_lim"):].split()[1])
                elif "v_check_all"    in line:
                    self.v_check_all.set(line[line.find("v_check_all"):].split()[1])
                elif "bmp_turnp"    in line:
                    self.bmp_turnpol.set(line[line.find("bmp_turnp"):].split()[1])
                elif "bmp_turds"    in line:
                    self.bmp_turdsize.set(line[line.find("bmp_turds"):].split()[1])
                elif "bmp_alpha"    in line:
                    self.bmp_alphamax.set(line[line.find("bmp_alpha"):].split()[1])
                elif "bmp_optto"    in line:
                    self.bmp_opttolerance.set(line[line.find("bmp_optto"):].split()[1])
                elif "imagefile"    in line:
                    self.IMAGE_FILE = (line[line.find("imagefile"):].split("\042")[1])
                elif "input_type"    in line:
                    self.input_type.set(line[line.find("input_type"):].split()[1])
                elif "clean_dia"     in line:
                    self.clean_dia.set(line[line.find("clean_dia"):].split()[1])
                elif "clean_step"    in line:
                    self.clean_step.set(line[line.find("clean_step"):].split()[1])
                elif "clean_w"       in line:
                    self.clean_w.set(line[line.find("clean_w"):].split()[1])
                elif "clean_v"       in line:
                    self.clean_v.set(line[line.find("clean_v"):].split()[1])
                elif "clean_paths"    in line:
                    clean_paths=(line[line.find("clean_paths"):].split()[1])
                    clean_split = [float(n) for n in clean_paths.split(',')]
                    if len(clean_split) > 5:
                        self.clean_P.set(bool(clean_split[0]))
                        self.clean_X.set(bool(clean_split[1]))
                        self.clean_Y.set(bool(clean_split[2]))
                        self.v_clean_P.set(bool(clean_split[3]))
                        self.v_clean_Y.set(bool(clean_split[4]))
                        self.v_clean_X.set(bool(clean_split[5]))

        fin.close()

        file_full = self.fontdir.get() + "/" + self.fontfile.get()
        fileName, fileExtension = os.path.splitext(file_full)
        TYPE=fileExtension.upper()

        if TYPE != '.CXF' and TYPE!='.TTF' and TYPE!='':
            if ( os.path.isfile(file_full) ):
                self.input_type.set("image")

        if boxsize!="0":
            self.boxgap.set( float(boxsize) * float(self.STHICK.get()) )


        if text_codes != []:
            try:
                self.Input.delete(1.0, END)
                for Ch in text_codes:
                    self.Input.insert(END, "%c" %( unichr(int(Ch))))
            except:
                self.default_text = ''
                for Ch in text_codes:
                    self.default_text = self.default_text + "%c" %( unichr(int(Ch)))

        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.units.set('mm')
            self.funits.set('mm/min')

        self.calc_depth_limit()

        temp_name, fileExtension = os.path.splitext(filename)
        file_base=os.path.basename(temp_name)

        self.delay_calc = 0
        if self.initComplete == 1:
            self.menu_Mode_Change()
            self.NGC_FILE = filename


    def menu_File_Save_G_Code_File(self):
        if (self.Check_All_Variables() > 0):
            return

        if self.vcoords == [] and self.cut_type.get() == "v-carve":
            mess = "V-carve path data does not exist.  "
            mess += "Only settings will be saved.\n\n"
            mess += "To generate V-Carve path data Click on the"
            mess += "\"Calculate V-Carve\" button on the main window."
            if not message_ask_ok_cancel("Continue", mess ):
                return

        self.WriteGCode()
        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file=os.path.basename(fileName)

        if self.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file=os.path.basename(fileName)
        else:
            init_file="text"

        filename = asksaveasfilename(defaultextension='.ngc', \
                                     filetypes=[("EMC2 Files","*.ngc"),("All Files","*")],\
                                     initialdir=init_dir,\
                                     initialfile= init_file )

        if filename != '' and filename != ():
            self.NGC_FILE = filename
            try:
                fout = open(filename,'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" %(filename))
                self.statusbar.configure( bg = 'red' )
                return
            for line in self.gcode:
                try:
                    fout.write(line+'\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close
            self.statusMessage.set("File Saved: %s" %(filename))
            self.statusbar.configure( bg = 'white' )


    def menu_File_Save_clean_G_Code_File(self, bit_type="straight"):
        if (self.Check_All_Variables() > 0):
            return

        self.WRITE_CLEAN_UP(bit_type)

        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file=os.path.basename(fileName)
        if self.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file=os.path.basename(fileName)
            fileName_tmp, fileExtension = os.path.splitext(init_file)
            init_file = fileName_tmp
        else:
            init_file="text"

        if bit_type == "v-bit":
            init_file = init_file + "_v" + self.clean_name.get()
        else:
            init_file = init_file +        self.clean_name.get()


        filename = asksaveasfilename(defaultextension='.ngc', \
                                     filetypes=[("EMC2 Files","*.ngc"),("All Files","*")],\
                                     initialdir=init_dir,\
                                     initialfile= init_file )

        if filename != '' and filename != ():
            try:
                fout = open(filename,'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" %(filename))
                self.statusbar.configure( bg = 'red' )
                return
            for line in self.gcode:
                try:
                    fout.write(line+'\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close
            self.statusMessage.set("File Saved: %s" %(filename))
            self.statusbar.configure( bg = 'white' )

    def menu_File_Save_SVG_File(self):
        self.WriteSVG()

        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file=os.path.basename(fileName)
        if self.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file=os.path.basename(fileName)
        else:
            init_file="text"

        filename = asksaveasfilename(defaultextension='.svg', \
                                     filetypes=[("SVG File"  ,"*.svg"),("All Files","*")],\
                                     initialdir=init_dir,\
                                     initialfile= init_file )

        if filename != '' and filename != ():
            try:
                fout = open(filename,'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" %(filename))
                self.statusbar.configure( bg = 'red' )
                return
            for line in self.svgcode:
                try:
                    fout.write(line+'\n')
                except:
                    pass

                fout.close
            self.statusMessage.set("File Saved: %s" %(filename))
            self.statusbar.configure( bg = 'white' )
    def menu_File_Quit(self):
        if message_ask_ok_cancel("Exit", "Exiting F-Engrave...."):
            self.Quit_Click(None)

    def menu_View_Refresh_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_View_Refresh(self):
        if (not self.batch.get()):
            dummy_event = Event()
            dummy_event.widget=self.master
            self.Master_Configure(dummy_event,1)
            self.Plot_Data()

    def menu_Mode_Change_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_Mode_Change(self):
        dummy_event = Event()
        dummy_event.widget=self.master
        self.Master_Configure(dummy_event,1)

        if self.input_type.get() == "text":
            self.Read_font_file()
        else:
            self.Read_image_file()
        self.DoIt()

    def menu_View_Recalculate(self):
        self.DoIt()

    def menu_Help_About(self):
        about = "F-Engrave by Scorch.\n\n"
        about = about + "\163\143\157\162\143\150\100\163\143\157\162"
        about = about + "\143\150\167\157\162\153\163\056\143\157\155\n"
        about = about + "http://www.scorchworks.com/"
        message_box("About F-Engrave",about)

    def KEY_ESC(self, event):
        pass #A stop calculation command may go here

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

    def bindConfigure(self, event):
        if not self.initComplete:
            self.initComplete = 1
            self.menu_Mode_Change()

    def Master_Configure(self, event, update=0):
        if event.widget != self.master:
            return

        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        if (self.x, self.y) == (-1,-1):
            self.x, self.y = x,y
        if abs(self.w-w)>10 or abs(self.h-h)>10 or update==1:
            ###################################################
            #  Form changed Size (resized) adjust as required #
            ###################################################
            self.w=w
            self.h=h
            #canvas
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
                self.Label_Yscale_u = Label(self.master,textvariable=self.units, anchor=W)

                self.Label_useIMGsize.place_forget()
                self.Checkbutton_useIMGsize.place_forget()

                # Left Column #
                w_label=90
                w_entry=60
                w_units=35

                x_label_L=10
                x_entry_L=x_label_L+w_label+10
                x_units_L=x_entry_L+w_entry+5

                Yloc=6
                self.Label_font_prop.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)
                Yloc=Yloc+24
                self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Yscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Yscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Sthick.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Sthick_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Sthick.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                if self.cut_type.get() != "engrave":
                    self.Entry_Sthick.configure(state="disabled")
                    self.Label_Sthick.configure(state="disabled")
                    self.Label_Sthick_u.configure(state="disabled")
                else:
                    self.Entry_Sthick.configure(state="normal")
                    self.Label_Sthick.configure(state="normal")
                    self.Label_Sthick_u.configure(state="normal")

                Yloc=Yloc+24
                self.Label_Xscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Xscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Xscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Cspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Cspace_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Cspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Wspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Wspace_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Wspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Lspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Entry_Lspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24+12
                self.separator1.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Justify.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Justify_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24+12
                self.separator2.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_text_on_arc.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Label_Tradius.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Tradius_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Tradius.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_outer.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_outer.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_upper.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_upper.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24+12
                self.separator3.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)

                # End Left Column #

                # Start Right Column
                w_label=90
                w_entry=60
                w_units=35

                x_label_R=self.w - 220
                x_entry_R=x_label_R+w_label+10
                x_units_R=x_entry_R+w_entry+5

                Yloc=6
                self.Label_gcode_opt.place(x=x_label_R, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Entry_Feed.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Feed.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Feed_u.place(x=x_units_R, y=Yloc, width=w_units+15, height=21)

                Yloc=Yloc+24
                self.Entry_Zsafe.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Zsafe.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zsafe_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)


                Yloc=Yloc+24
                self.Label_Zcut.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zcut_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)
                self.Entry_Zcut.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)

                if self.cut_type.get() != "engrave":
                    self.Entry_Zcut.configure(state="disabled")
                    self.Label_Zcut.configure(state="disabled")
                    self.Label_Zcut_u.configure(state="disabled")
                else:
                    self.Entry_Zcut.configure(state="normal")
                    self.Label_Zcut.configure(state="normal")
                    self.Label_Zcut_u.configure(state="normal")

                Yloc=Yloc+24+6
                self.Label_List_Box.place(x=x_label_R+0, y=Yloc, width=113, height=22)

                Yloc=Yloc+24
                self.Listbox_1_frame.place(x=x_label_R+0, y=Yloc, width=160+25, height = self.h-300)
                self.Label_fontfile.place(x=x_label_R, y=self.h-165, width=w_label+75, height=21)
                self.Checkbutton_fontdex.place(x=x_label_R, y=self.h-145, width=185, height=23)

                # Buttons etc.

                Ybut=self.h-60
                self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

                Ybut=self.h-60
                self.V_Carve_Calc.place(x=x_label_R, y=Ybut, width=100, height=30)

                Ybut=self.h-105
                self.Radio_Cut_E.place(x=x_label_R, y=Ybut, width=185, height=23)
                Ybut=self.h-85
                self.Radio_Cut_V.place(x=x_label_R, y=Ybut, width=185, height=23)

                self.PreviewCanvas.configure( width = self.w-455, height = self.h-160 )
                self.PreviewCanvas_frame.place(x=220, y=10)
                self.Input_Label.place(x=222, y=self.h-130, width=112, height=21, anchor=W)
                self.Input_frame.place(x=222, y=self.h-110, width=self.w-455, height=75)

            else:
                self.Label_font_prop.configure(text="Image Properties:")
                self.Label_Yscale.configure(text="Image Height")
                self.Label_Xscale.configure(text="Image Width")
                self.Label_pos_orient.configure(text="Image Position and Orientation:")
                self.Label_Tangle.configure(text="Image Angle")
                self.Label_flip.configure(text="Flip Image")
                self.Label_mirror.configure(text="Mirror Image")
                if (self.useIMGsize.get()):
                    self.Label_Yscale_u = Label(self.master,text="%", anchor=W)
                else:
                    self.Label_Yscale_u = Label(self.master,textvariable=self.units, anchor=W)

                # Left Column #
                w_label=90
                w_entry=60
                w_units=35

                x_label_L=10
                x_entry_L=x_label_L+w_label+10
                x_units_L=x_entry_L+w_entry+5

                Yloc=6
                self.Label_font_prop.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)
                Yloc=Yloc+24
                self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Yscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Yscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_useIMGsize.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_useIMGsize.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_Sthick.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Sthick_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Sthick.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)
                if self.cut_type.get() != "engrave":
                    self.Entry_Sthick.configure(state="disabled")
                    self.Label_Sthick.configure(state="disabled")
                    self.Label_Sthick_u.configure(state="disabled")
                else:
                    self.Entry_Sthick.configure(state="normal")
                    self.Label_Sthick.configure(state="normal")
                    self.Label_Sthick_u.configure(state="normal")



                Yloc=Yloc+24
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

                Yloc=Yloc+24+12
                self.separator1.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                self.Label_Justify.place_forget()
                self.Justify_OptionMenu.place_forget()

                Yloc=Yloc+24
                self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                self.Label_text_on_arc.place_forget()
                self.Label_Tradius.place_forget()
                self.Label_Tradius_u.place_forget()
                self.Entry_Tradius.place_forget()
                self.Label_outer.place_forget()
                self.Checkbutton_outer.place_forget()
                self.Label_upper.place_forget()
                self.Checkbutton_upper.place_forget()

                # End Left Column #
                # Start Right Column Items
                x_label_R=x_label_L
                x_entry_R=x_entry_L
                x_units_R=x_units_L

                Yloc=Yloc+24+12
                self.separator2.place(x=x_label_R, y=Yloc,width=w_label+75+40, height=2)

                Yloc=Yloc+6
                self.Label_gcode_opt.place(x=x_label_R, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Entry_Feed.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Feed.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Feed_u.place(x=x_units_R, y=Yloc, width=w_units+15, height=21)

                Yloc=Yloc+24
                self.Entry_Zsafe.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Zsafe.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zsafe_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)


                Yloc=Yloc+24
                self.Label_Zcut.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zcut_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)
                self.Entry_Zcut.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)

                if self.cut_type.get() != "engrave":
                    self.Entry_Zcut.configure(state="disabled")
                    self.Label_Zcut.configure(state="disabled")
                    self.Label_Zcut_u.configure(state="disabled")
                else:
                    self.Entry_Zcut.configure(state="normal")
                    self.Label_Zcut.configure(state="normal")
                    self.Label_Zcut_u.configure(state="normal")

                self.Label_List_Box.place_forget()
                self.Listbox_1_frame.place_forget()
                self.Checkbutton_fontdex.place_forget()

                Yloc=Yloc+24+12
                self.separator3.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_fontfile.place(x=x_label_R, y=Yloc, width=w_label+75, height=21)

                # Buttons etc.
                offset_R=100
                Ybut=self.h-60
                self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

                Ybut=self.h-60
                self.V_Carve_Calc.place(x=x_label_R+offset_R, y=Ybut, width=100, height=30)

                Ybut=self.h-105
                self.Radio_Cut_E.place(x=x_label_R+offset_R, y=Ybut, width=w_label, height=23)
                Ybut=self.h-85
                self.Radio_Cut_V.place(x=x_label_R+offset_R, y=Ybut, width=w_label, height=23)

                self.PreviewCanvas.configure( width = self.w-240, height = self.h-45 )
                self.PreviewCanvas_frame.place(x=230, y=10)
                self.Input_Label.place_forget()
                self.Input_frame.place_forget()

            ###########################################################
            if self.cut_type.get() == "v-carve":
                pass
            else:
                pass
            ###########################################################
            self.Plot_Data()

    ############################################################################
    # routine takes an x and y the point is rotated by angle returns new x,y   #
    ############################################################################
    def Rotn(self,x,y,angle,radius):
        if radius > 0.0:
            alpha = x / radius
            xx = ( radius + y ) * sin(alpha)
            yy = ( radius + y ) * cos(alpha)
        elif radius < 0.0:
            alpha = x / radius
            xx = ( radius + y ) * sin(alpha)
            yy = ( radius + y ) * cos(alpha)
        else: #radius is 0
            alpha = 0
            xx = x
            yy = y

        rad = sqrt(xx * xx + yy * yy)
        theta = atan2(yy,xx)
        newx=rad * cos(theta + radians(angle) )
        newy=rad * sin(theta + radians(angle) )
        return newx,newy,alpha

    ############################################################################
    # routine takes an x and a y scales are applied and returns new x,y tuple  #
    ############################################################################
    def CoordScale(self,x,y,xscale,yscale):
        newx = x * xscale
        newy = y * yscale
        return newx,newy

    def Plot_Line(self,XX1,YY1,XX2,YY2,midx,midy,cszw,cszh,PlotScale,col,radius=0):
        x1 =  cszw/2 + (XX1-midx) / PlotScale
        x2 =  cszw/2 + (XX2-midx) / PlotScale
        y1 =  cszh/2 - (YY1-midy) / PlotScale
        y2 =  cszh/2 - (YY2-midy) / PlotScale
        if radius==0:
            thick=0
        else:
            thick  =  radius*2 / PlotScale
        self.segID.append( self.PreviewCanvas.create_line(x1,y1,x2,y2,fill = col, capstyle="round", width=thick))

    def Plot_Circ(self,XX1,YY1,midx,midy,cszw,cszh,PlotScale,color,Rad,fill):
        dd=Rad
        x1 =  cszw/2 + (XX1-dd-midx) / PlotScale
        x2 =  cszw/2 + (XX1+dd-midx) / PlotScale
        y1 =  cszh/2 - (YY1-dd-midy) / PlotScale
        y2 =  cszh/2 - (YY1+dd-midy) / PlotScale
        if fill ==0:
            self.segID.append( self.PreviewCanvas.create_oval(x1,y1,x2,y2, outline=color, fill=None, width=1 ))
        else:
            self.segID.append( self.PreviewCanvas.create_oval(x1,y1,x2,y2, outline=color, fill=color, width=0 ))

    ############################################################################
    # Routine finds the maximum radius that can be placed in the position      #
    # xpt,ypt witout interfearing with other line segments (rmin is max R LOL) #
    ############################################################################
    def find_max_circle(self,xpt,ypt,rmin,char_num,seg_sin,seg_cos,corner,Acc,CHK_STRING):
        global Zero
        rtmp = rmin

        xIndex = int((xpt-self.MINX)/self.xPartitionLength)
        yIndex = int((ypt-self.MINY)/self.yPartitionLength)

        self.coords_check=[]
        R_A = abs(rmin)
        Bcnt=-1
        ############################################################
        # Loop over active partitions for the current line segment #
        ############################################################
        for line_B in self.partitionList[xIndex][yIndex]:
            Bcnt=Bcnt+1
            X_B = line_B[len(line_B)-3]
            Y_B = line_B[len(line_B)-2]
            R_B = line_B[len(line_B)-1]
            GAP = sqrt( (X_B-xpt)*(X_B-xpt) + (Y_B-ypt)*(Y_B-ypt)  )
            if GAP < abs(R_A + R_B):
                self.coords_check.append(line_B)

        for linec in self.coords_check:
            XYc = linec
            xmaxt=max(XYc[0],XYc[2]) + rmin*2
            xmint=min(XYc[0],XYc[2]) - rmin*2
            ymaxt=max(XYc[1],XYc[3]) + rmin*2
            ymint=min(XYc[1],XYc[3]) - rmin*2
            if (xpt >= xmint and  ypt >= ymint and xpt <= xmaxt and  ypt <= ymaxt):
                logic_full = True
            else:
                logic_full = False
                continue

            if (CHK_STRING == "chr"):
                logic_full = logic_full and (char_num == int(XYc[5]))

            if corner==1:
                logic_full = logic_full and ( (fabs(xpt-XYc[0]) > Acc) or (fabs(ypt-XYc[1]) > Acc) ) and \
                    ( (fabs(xpt-XYc[2]) > Zero) or (fabs(ypt-XYc[3]) > Zero) )

            if logic_full:
                xc1 = (XYc[0]-xpt) * seg_cos - (XYc[1]-ypt) * seg_sin
                yc1 = (XYc[0]-xpt) * seg_sin + (XYc[1]-ypt) * seg_cos
                xc2 = (XYc[2]-xpt) * seg_cos - (XYc[3]-ypt) * seg_sin
                yc2 = (XYc[2]-xpt) * seg_sin + (XYc[3]-ypt) * seg_cos

                if fabs(xc2-xc1) < Zero and (yc2-yc1) != 0.0:
                    rtmp=fabs(xc1)
                    if max(yc1,yc2) >= rtmp and min(yc1,yc2) <= rtmp:
                        rmin = min(rmin,rtmp)

                elif fabs(yc2-yc1) < Zero and (xc2-xc1) != 0.0:
                    if max(xc1,xc2) >= 0 and min(xc1,xc2) <= 0 and yc1 > Acc:
                        rtmp=yc1/2
                        rmin = min(rmin,rtmp)

                if fabs(yc2-yc1) > Zero and fabs(xc2-xc1) > Zero:
                    m = (yc2-yc1)/(xc2-xc1)
                    b = yc1 - m*xc1
                    sq = m+1/m
                    A = 1 + m*m - 2*m*sq
                    B = -2*b*sq
                    C = -b*b
                    try:
                        sq_root = sqrt(B*B-4*A*C)
                        xq1 = (-B + sq_root)/(2*A)

                        if xq1 >= min(xc1,xc2) and xq1 <= max(xc1,xc2):
                            rtmp = xq1*sq + b
                            if rtmp >= 0.0:
                                rmin=min(rmin,rtmp)

                        xq2 = (-B - sq_root)/(2*A)
                        yq2 = m*xq2+b

                        if xq2 >= min(xc1,xc2) and xq2 <= max(xc1,xc2):
                            rtmp = xq2*sq + b
                            if rtmp >= 0.0:
                                rmin=min(rmin,rtmp)
                    except:
                        pass

                if yc1 > Zero:
                    rtmp = (xc1*xc1 + yc1*yc1) / (2*yc1)
                    rmin=min(rmin,rtmp)

                if yc2 > Zero:
                    rtmp = (xc2*xc2 + yc2*yc2) / (2*yc2)
                    rmin=min(rmin,rtmp)

                ###### NEW V1.20 #######
                if abs(yc1) < Zero and abs(xc1) < Zero:
                    if yc2 > Zero:
                        rmin = 0
                if abs(yc2) < Zero and abs(xc2) < Zero:
                    if yc1 > Zero:
                        rmin = 0
                ### END NEW V1.20 #####

        return rmin

    def Recalculate_RQD_Nocalc(self, event):
        self.statusbar.configure( bg = 'yellow' )
        self.Input.configure( bg = 'yellow' )
        self.statusMessage.set(" Recalculation required.")

    def Recalculate_RQD_Click(self, event):
        self.statusbar.configure( bg = 'yellow' )
        self.statusMessage.set(" Recalculation required.")
        self.DoIt()

    def Recalc_RQD(self):
        self.statusbar.configure( bg = 'yellow' )
        self.statusMessage.set(" Recalculation required.")
        self.DoIt()

    ##########################################
    #          Read Font File                #
    ##########################################
    def Read_font_file(self):
        self.font = {}
        file_full = self.fontdir.get() + "/" + self.fontfile.get()
        if not os.path.isfile(file_full):
            return
        if not self.batch.get():
            self.statusbar.configure(bg = 'yellow')
            self.statusMessage.set(" Reading File.........")
            self.master.update_idletasks()

        fileName, fileExtension = os.path.splitext(file_full)
        self.current_input_file.set( os.path.basename(file_full) )

        SegArc = float(self.segarc.get())
        TYPE=fileExtension.upper()
        if TYPE=='.CXF':
            try:
                file = open(file_full)
            except:
                self.statusMessage.set("Unable to Open CXF File: %s" %(file_full))
                self.statusbar.configure( bg = 'red' )
                return
            self.font = parse_cxf(file, SegArc)  # build stroke lists from font file
            file.close()

        elif TYPE=='.TTF':
            if self.ext_char.get():
                option = "-e"
            else:
                option = ""
            cmd = ["ttf2cxf_stream",option,file_full,"STDOUT"]
            try:
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                if VERSION == 3:
                    file=bytes.decode(stdout).split("\n")
                else:
                    file=stdout.split("\n")

                self.font = parse(file,SegArc)  # build stroke lists from font file
                self.input_type.set("text")
            except:
                fmessage("Unable To open True Type (TTF) font file: %s" %(file_full))
        else:
            pass

        if (not self.batch.get()):
            self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),1)
            self.menu_View_Refresh()

    ##########################################
    #          Read Font File                #
    ##########################################
    def Read_image_file(self):
        self.font = {}
        file_full = self.IMAGE_FILE
        if ( not os.path.isfile(file_full) ):
            return

        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set(" Reading File.........")
            self.master.update_idletasks()

        fileName, fileExtension = os.path.splitext(file_full)
        self.current_input_file.set( os.path.basename(file_full) )

        #if (self.useIMGsize.get()):
        new_origin = False
        #else:
        #    new_origin = True

        SegArc    =  float(self.segarc.get())
        TYPE = fileExtension.upper()
        if TYPE is '.DXF':
            String = self.Input.get(1.0, END).encode('ascii', 'ignore')
            #if (self.useIMGsize.get()):
            #    new_origin = False
            #else:
            #    new_origin = True
            try:
                fd = open(file_full)
                self.font,self.DXF_source = parse_dxf(fd, SegArc, new_origin)  # build stroke lists from font file
                fd.close()
                self.input_type.set("image")
            except Exception, e:
                print e
                fmessage("Unable To open Drawing Exchange File (DXF) file.")

        elif TYPE in ('.BMP', '.PBM', '.PPM', '.PGM', '.PNM'):
            try:
                #cmd = ["potrace","-b","dxf",file_full,"-o","-"]
                if self.bmp_longcurve.get() == 1:
                    cmd = ["potrace",
                       "-z", self.bmp_turnpol.get(),
                       "-t", self.bmp_turdsize.get(),
                       "-a",self.bmp_alphamax.get(),
                       "-O",self.bmp_opttolerance.get(),
                       "-b","dxf",file_full,"-o","-"]
                else:
                    cmd = ["potrace",
                       "-z", self.bmp_turnpol.get(),
                       "-t", self.bmp_turdsize.get(),
                       "-a",self.bmp_alphamax.get(),
                       "-n",
                       "-b","dxf",file_full,"-o","-"]

                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                if VERSION == 3:
                    fd=bytes.decode(stdout).split("\n")
                else:
                    fd=stdout.split("\n")
                self.font,self.DXF_source = parse_dxf(fd,SegArc,new_origin)  # build stroke lists from font file
                self.input_type.set("image")
            except:
                fmessage("Unable To create path data from bitmap File.")
        else:
            pass


        #Reset Entry Fields in Bitmap Settings
        if (not self.batch.get()):
            self.entry_set(self.Entry_BMPoptTolerance,self.Entry_BMPoptTolerance_Check(),1)
            self.entry_set(self.Entry_BMPturdsize,    self.Entry_BMPturdsize_Check()    ,1)
            self.entry_set(self.Entry_BMPalphamax,    self.Entry_BMPalphamax_Check()    ,1)
            self.entry_set(self.Entry_ArcAngle,       self.Entry_ArcAngle_Check()       ,1)
            self.menu_View_Refresh()


    ##########################################
    #        CANVAS PLOTTING STUFF           #
    ##########################################
    def Plot_Data(self):
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
        midx=(maxx+minx)/2
        midy=(maxy+miny)/2

        if self.cut_type.get() == "v-carve":
            Thick = 0.0
        else:
            Thick   = float(self.STHICK.get())

        if self.input_type.get() == "text":
            Radius_in =  float(self.TRADIUS.get())
        else:
            Radius_in = 0.0

        PlotScale = max((maxx-minx+Thick)/(cszw-buff), (maxy-miny+Thick)/(cszh-buff))
        if PlotScale <= 0:
            PlotScale=1.0
        self.pscale = PlotScale

        Radius_plot = 0
        if self.plotbox.get() != "no_box" and self.cut_type.get() == "engrave":
            if Radius_in != 0:
                Radius_plot=  float(self.RADIUS_PLOT)

        x_lft = cszw/2 + (minx-midx) / PlotScale
        x_rgt = cszw/2 + (maxx-midx) / PlotScale
        y_bot = cszh/2 + (maxy-midy) / PlotScale
        y_top = cszh/2 + (miny-midy) / PlotScale

        if self.show_box.get() == True:
            self.segID.append( self.PreviewCanvas.create_rectangle(
                    x_lft, y_bot, x_rgt, y_top, fill="gray80", outline="gray80", width = 0) )

        if Radius_in != 0:
            Rx_lft = cszw/2 + ( -Radius_in-midx)  / PlotScale
            Rx_rgt = cszw/2 + (  Radius_in-midx)  / PlotScale
            Ry_bot = cszh/2 + (  Radius_in+midy)  / PlotScale
            Ry_top = cszh/2 + ( -Radius_in+midy)  / PlotScale
            self.segID.append( self.PreviewCanvas.create_oval(Rx_lft, Ry_bot, Rx_rgt, Ry_top, outline="gray90", width = 0, dash=3) )

        if self.show_thick.get() == True:
            plot_width = Thick / PlotScale
        else:
            plot_width = 1.0

        # Plot circle radius with radius equal to Radius_plot
        if Radius_plot != 0:
            Rpx_lft = cszw/2 + ( -Radius_plot-midx)  / PlotScale
            Rpx_rgt = cszw/2 + (  Radius_plot-midx)  / PlotScale
            Rpy_bot = cszh/2 + (  Radius_plot+midy)  / PlotScale
            Rpy_top = cszh/2 + ( -Radius_plot+midy)  / PlotScale
            self.segID.append( self.PreviewCanvas.create_oval(Rpx_lft, Rpy_bot, Rpx_rgt, Rpy_top, outline="black", width = plot_width) )

        for line in self.coords:
            XY = line
            x1 =  cszw/2 + (XY[0]-midx) / PlotScale
            x2 =  cszw/2 + (XY[2]-midx) / PlotScale
            y1 =  cszh/2 - (XY[1]-midy) / PlotScale
            y2 =  cszh/2 - (XY[3]-midy) / PlotScale
            self.segID.append( self.PreviewCanvas.create_line(x1,y1,x2,y2,fill = 'black', \
                                                                  width=plot_width , \
                                                                  capstyle='round' ))
        XOrigin   =  float(self.xorigin.get())
        YOrigin   =  float(self.yorigin.get())
        axis_length=(maxx-minx)/4
        axis_x1 =  cszw/2 + (-midx             + XOrigin ) / PlotScale
        axis_x2 =  cszw/2 + ( axis_length-midx + XOrigin ) / PlotScale
        axis_y1 =  cszh/2 - (-midy             + YOrigin ) / PlotScale
        axis_y2 =  cszh/2 - ( axis_length-midy + YOrigin ) / PlotScale


        #########################################
        # V-carve Ploting Stuff
        #########################################
        if self.cut_type.get() == "v-carve":
            loop_old = -1
            for line in self.vcoords:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                color = "black"
                self.Plot_Circ(x1,y1,midx,midy,cszw,cszh,PlotScale,color,r,1)

            loop_old = -1
            for line in self.vcoords:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                loop  = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                if (loop == loop_old):
                    pass
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color)
                loop_old = loop
                xold=x1
                yold=y1

        ########################################
        # Plot cleanup data
        ########################################
        if self.cut_type.get() == "v-carve":
            loop_old = -1
            for line in self.clean_coords_sort:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                loop  = XY[3]
                #color = "gray40"
                color = "brown"
                if (loop == loop_old):
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color,r)
                loop_old = loop
                xold=x1
                yold=y1

            loop_old = -1
            for line in self.clean_coords_sort:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                loop  = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                if (loop == loop_old):
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color)
                loop_old = loop
                xold=x1
                yold=y1

            loop_old = -1
            for line in self.v_clean_coords_sort:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                loop  = XY[3]
                color = "yellow"
                if (loop == loop_old):
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color)
                loop_old = loop
                xold=x1
                yold=y1


        #########################################
        # End V-carve Plotting Stuff
        #########################################

        if self.show_axis.get() == True:
            # Plot coordinate system origin
            self.segID.append( self.PreviewCanvas.create_line(axis_x1,axis_y1,\
                                                                  axis_x2,axis_y1,\
                                                                  fill = 'red'  , width = 0))
            self.segID.append( self.PreviewCanvas.create_line(axis_x1,axis_y1,\
                                                                  axis_x1,axis_y2,\
                                                                  fill = 'green', width = 0))

    ############################################################################
    #                         Perform  Calculations                            #
    ############################################################################
    def DoIt(self):
        if (self.initComplete == 0 or self.delay_calc == 1) and (not self.batch.get):
            return

        if (not self.batch.get):
            if self.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)

        if (self.Check_All_Variables() > 0):
            return

        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set(" Calculating.........")
            self.master.update_idletasks()
            self.PreviewCanvas.delete(ALL)

        # erase old data
        self.segID = []
        self.gcode   = []
        self.svgcode = []
        self.coords  = []
        self.vcoords = []
        self.clean_coords = []
        self.clean_segment=[]
        self.clean_coords_sort=[]
        self.v_clean_coords_sort=[]

        self.RADIUS_PLOT = 0


        if len(self.font) == 0 and (not self.batch.get()):
            self.statusbar.configure( bg = 'red' )
            if self.input_type.get() == "text":
                self.statusMessage.set("No Font Characters Loaded")
            else:
                self.statusMessage.set("No Image Loaded")
            return

        if self.input_type.get() == "text":
            if (not self.batch.get()):
                String    =  self.Input.get(1.0,END)
            else:
                String    =  self.default_text

            Radius_in =  float(self.TRADIUS.get())
        else:
            String    = "F"
            Radius_in =  0.0
        try:
            SegArc    =  float(self.segarc.get())
            YScale_in =  float(self.YSCALE.get() )
            CSpaceP   =  float(self.CSPACE.get() )
            WSpaceP   =  float(self.WSPACE.get() )
            LSpace    =  float(self.LSPACE.get() )
            Angle     =  float(self.TANGLE.get() )
            Thick     =  float(self.STHICK.get() )
            XOrigin   =  float(self.xorigin.get())
            YOrigin   =  float(self.yorigin.get())
            v_flop    =  bool(self.v_flop.get())
        except:
            self.statusMessage.set(" Unable to create paths.  Check Settings Entry Values.")
            self.statusbar.configure( bg = 'red' )
            return

        if self.cut_type.get() == "v-carve":
            Thick = 0.0

        line_maxx = []
        line_maxy = []
        line_maxa = []
        line_mina = []
        line_miny = []
        line_minx = []

        maxx_tmp = -99991.0
        maxy_tmp = -99992.0
        maxa_tmp = -99993.0
        mina_tmp =  99993.0
        miny_tmp =  99994.0
        minx_tmp =  99995.0

        font_word_space  = 0
        font_line_height = -1e10
        font_char_width =  -1e10
        font_used_height = -1e10
        font_used_width  = -1e10
        font_used_depth  =  1e10

        ################################
        ##      Font Index Preview    ##
        ################################
        if self.fontdex.get() == True:
            Radius_in = 0.0
            String = ""
            for key in self.font:
                if self.ext_char:
                    String = String + unichr(key)
                elif int(key) < 256:
                    String = String + unichr(key)
                    #String = String + chr(key)

            Strings = sorted(String)
            mcnt = 0
            String = ""

            if self.ext_char.get():
                pcols = int(1.5*sqrt(float(len(self.font))))
            else:
                pcols = 15

            for char in Strings:
##                tcnt = tcnt + 1
##
##                #fmessage( "% %x: %s\t" %( hex(ord(char)),char),False)
##                fmessage( "%s " %( hex(ord(char))),False)
##                if tcnt > tcols:
##                    fmessage( "\n",False)
##                    tcnt = 0
                mcnt = mcnt+1
                String = String + char
                if mcnt > pcols:
                    String = String + '\n'
                    mcnt = 0
            #fmessage( "\n",False)

        ##################################
        ## Font Height/Width Calculation #
        ##################################
        for char in String:
            try:
                font_used_height = max( self.font[ord(char)].get_ymax(), font_used_height )
                font_used_width  = max( self.font[ord(char)].get_xmax(), font_used_width  )
                font_used_depth  = min( self.font[ord(char)].get_ymin(), font_used_depth  )
            except:
                pass

        if self.H_CALC.get() == "max_all":
            font_line_height = max(self.font[key].get_ymax() for key in self.font)
            font_line_depth  = min(self.font[key].get_ymin() for key in self.font)
        elif self.H_CALC.get() == "max_use":
            font_line_height = font_used_height
            font_line_depth  = font_used_depth

        if font_line_height > 0:
            if (self.useIMGsize.get() and self.input_type.get()=="image"):
                YScale = YScale_in/100.0
            else:
                YScale = (YScale_in-Thick)/(font_line_height-font_line_depth)
                if YScale <= Zero:
                    YScale = .1
        else:
            if (not self.batch.get()): self.statusbar.configure( bg = 'red' )
            if self.H_CALC.get() == "max_all":
                if (not self.batch.get()):
                    self.statusMessage.set("No Font Characters Found")
                else:
                    fmessage("(No Font Characters Found)")
            elif self.H_CALC.get() == "max_use":
                if (not self.batch.get()):
                    self.statusMessage.set("Input Characters Were Not Found in the Current Font")
                else:
                    fmessage("(Input Characters Were Not Found in the Current Font)")
            return

        font_char_width  = max(self.font[key].get_xmax() for key in self.font)
        font_word_space =  font_char_width * (WSpaceP/100.0)

        XScale = float(self.XSCALE.get())  * YScale / 100
        font_char_space =  font_char_width * (CSpaceP /100.0)

        if Radius_in != 0.0:
            if self.outer.get() == True:
                if self.upper.get() == True:
                    Radius =  Radius_in + Thick/2 + YScale*(-font_line_depth)
                else:
                    Radius = -Radius_in - Thick/2 - YScale*(font_line_height)
            else:
                if self.upper.get() == True:
                    Radius =  Radius_in - Thick/2 - YScale*(font_line_height)
                else:
                    Radius = -Radius_in + Thick/2 + YScale*(-font_line_depth)
        else:
            Radius =  Radius_in

        font_line_space = (font_line_height - font_line_depth + Thick/YScale) * LSpace

        max_vals=[]

        xposition  = 0.0
        yposition  = 0.0
        line_cnt = 0.0
        char_cnt = 0
        no_font_record = []
        message2 = ""
        for char in String:
            char_cnt = char_cnt + 1

            if char == ' ':
                xposition += font_word_space
                continue
            if char == '\t':
                xposition += 3*font_word_space
                continue
            if char == '\n':
                xposition = 0
                yposition += font_line_space
                line_cnt = line_cnt+1
                line_minx.append(minx_tmp)
                line_miny.append(miny_tmp)
                line_maxx.append(maxx_tmp)
                line_maxy.append(maxy_tmp)
                line_maxa.append(maxa_tmp)
                line_mina.append(mina_tmp)
                maxx_tmp = -99919.0
                maxy_tmp = -99929.0
                maxa_tmp = -99939.0
                mina_tmp =  99949.0
                miny_tmp =  99959.0
                minx_tmp =  99969.0
                continue

            first_stroke = True
            try:
                font_line_height = self.font[ord(char)].get_ymax()
            except:
                flag=0
                for norec in no_font_record:
                    if norec == char:
                        flag=1
                if flag == 0:
                    no_font_record.append(char)
                    message2 = ", CHECK OUTPUT! Some characters not found in font file."
                continue
            for stroke in self.font[ord(char)].stroke_list:
                x1 = stroke.xstart + xposition
                y1 = stroke.ystart - yposition
                x2 = stroke.xend   + xposition
                y2 = stroke.yend   - yposition

                # Perform scaling
                x1,y1 = self.CoordScale(x1,y1,XScale,YScale)
                x2,y2 = self.CoordScale(x2,y2,XScale,YScale)

                self.coords.append([x1,y1,x2,y2,line_cnt,char_cnt])

                maxx_tmp = max(maxx_tmp, x1, x2)
                minx_tmp = min(minx_tmp, x1, x2)
                miny_tmp = min(miny_tmp, y1, y2)
                maxy_tmp = max(maxy_tmp, y1, y2)

            char_width = self.font[ord(char)].get_xmax() # move over for next character
            xposition += font_char_space + char_width
        #END Char in String

        maxx = maxy = -99999.0
        miny = minx =  99999.0
        cnt=0

        for maxx_val in line_maxx:
            maxx = max( maxx, line_maxx[cnt] )
            minx = min( minx, line_minx[cnt] )
            miny = min( miny, line_miny[cnt] )
            maxy = max( maxy, line_maxy[cnt] )
            cnt=cnt+1
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
            for line in self.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    self.coords[cnt][0]=XY[0] + (maxx - line_maxx[line_num])/2
                    self.coords[cnt][2]=XY[2] + (maxx - line_maxx[line_num])/2
                except:
                    pass
                cnt=cnt+1

        ##########################################
        #        TEXT RIGHT JUSTIFY STUFF        #
        ##########################################
        if self.justify.get() == "Right":
            for line in self.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    XY[0]=XY[0] + (maxx - line_maxx[line_num])
                    XY[2]=XY[2] + (maxx - line_maxx[line_num])
                except:
                    pass
                cnt=cnt+1

        ##########################################
        #         TEXT ON RADIUS STUFF           #
        ##########################################
        mina =  99996.0
        maxa = -99993.0
        if Radius != 0.0:
            for line in self.coords:
                XY = line
                XY[0],XY[1],A1 = self.Rotn(XY[0],XY[1],0,Radius)
                XY[2],XY[3],A2 = self.Rotn(XY[2],XY[3],0,Radius)
                maxa = max(maxa, A1, A2)
                mina = min(mina, A1, A2)
            mida = (mina+maxa)/2
            ##########################################
            #         TEXT LEFT JUSTIFY STUFF        #
            ##########################################
            if self.justify.get() == "Left":
                pass
            ##########################################
            #          TEXT CENTERING STUFF          #
            ##########################################
            if self.justify.get() == "Center":
                for line in self.coords:
                    XY = line
                    XY[0],XY[1] = Transform(XY[0],XY[1],mida)
                    XY[2],XY[3] = Transform(XY[2],XY[3],mida)
            ##########################################
            #        TEXT RIGHT JUSTIFY STUFF        #
            ##########################################
            if self.justify.get() == "Right":
                for line in self.coords:
                    XY = line
                    if self.upper.get() == True:
                        XY[0],XY[1] = Transform(XY[0],XY[1],maxa)
                        XY[2],XY[3] = Transform(XY[2],XY[3],maxa)
                    else:
                        XY[0],XY[1] = Transform(XY[0],XY[1],mina)
                        XY[2],XY[3] = Transform(XY[2],XY[3],mina)

        ##########################################
        #    TEXT FLIP / MIRROR STUFF / ANGLE    #
        ##########################################
        maxx  = -99991.0
        maxy  = -99992.0
        miny  =  99994.0
        minx  =  99995.0
        maxr2 =  0.0
        for line in self.coords:
            XY = line
            if Angle != 0.0:
                XY[0],XY[1],A1 = self.Rotn(XY[0],XY[1],Angle,0)
                XY[2],XY[3],A2 = self.Rotn(XY[2],XY[3],Angle,0)

            if self.mirror.get() == True:
                XY[0] = -XY[0]
                XY[2] = -XY[2]
                v_flop  = not(v_flop)

            if self.flip.get() == True:
                XY[1] = -XY[1]
                XY[3] = -XY[3]
                v_flop = not(v_flop)

            maxx  = max(maxx,  XY[0], XY[2])
            maxy  = max(maxy,  XY[1], XY[3])

            minx  = min(minx,  XY[0], XY[2])
            miny  = min(miny,  XY[1], XY[3])

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
        if self.plotbox.get() != "no_box":
            Thick_Border  =  float(self.STHICK.get() )
            if Radius_in == 0:
                Delta = Thick/2 + float(self.boxgap.get())
                if (self.v_flop.get()!=0 and (self.DXF_source != "POTRACE" or  self.input_type.get() == "text")) or \
                   (self.v_flop.get()==0 and (self.DXF_source == "POTRACE" and self.input_type.get() != "text")):
                    self.coords.append([ minx-Delta, miny-Delta, maxx+Delta, miny-Delta, 0, 0])
                    self.coords.append([ maxx+Delta, miny-Delta, maxx+Delta, maxy+Delta, 0, 0])
                    self.coords.append([ maxx+Delta, maxy+Delta, minx-Delta, maxy+Delta, 0, 0])
                    self.coords.append([ minx-Delta, maxy+Delta, minx-Delta, miny-Delta, 0, 0])
                else:
                    self.coords.append([ minx-Delta, miny-Delta, minx-Delta, maxy+Delta, 0, 0])
                    self.coords.append([ minx-Delta, maxy+Delta, maxx+Delta, maxy+Delta, 0, 0])
                    self.coords.append([ maxx+Delta, maxy+Delta, maxx+Delta, miny-Delta, 0, 0])
                    self.coords.append([ maxx+Delta, miny-Delta, minx-Delta, miny-Delta, 0, 0])

                Delta = Delta + Thick/2
                minx = minx - Delta
                maxx = maxx + Delta
                miny = miny - Delta
                maxy = maxy + Delta
            else:
                Radius_plot = sqrt(maxr2) + Thick + float(self.boxgap.get())
                minx = -Radius_plot - Thick/2
                maxx = -minx
                miny =  minx
                maxy =  maxx
                midx =  0
                midy =  0
                self.RADIUS_PLOT = Radius_plot
                # Only do this if v-carving is enabled.
                # A g-code circle command is generated later when not v-carving
                if self.cut_type.get() == "v-carve":
                    xcirc0 = Radius_plot
                    ycirc0 = 0.0
                    beta_stp=360.0/ceil(360.0/SegArc)

                    if self.v_flop.get()==0:
                        fact = 1
                    else:
                        fact = -1

                    for k in range(int(ceil(360.0/SegArc))):
                        beta = radians( (k+1)*beta_stp * fact)
                        xcirc, ycirc = Transform(Radius_plot,0.0,beta)
                        self.coords.append([ xcirc0, ycirc0, xcirc, ycirc, 0, 0])
                        xcirc0 = xcirc
                        ycirc0 = ycirc

        ##########################################
        #         ORIGIN LOCATING STUFF          #
        ##########################################
        CASE = str(self.origin.get())
        if     CASE == "Top-Left":
            x_zero = minx
            y_zero = maxy
        elif   CASE == "Top-Center":
            x_zero = midx
            y_zero = maxy
        elif   CASE == "Top-Right":
            x_zero = maxx
            y_zero = maxy
        elif   CASE == "Mid-Left":
            x_zero = minx
            y_zero = midy
        elif   CASE == "Mid-Center":
            x_zero = midx
            y_zero = midy
        elif   CASE == "Mid-Right":
            x_zero = maxx
            y_zero = midy
        elif   CASE == "Bot-Left":
            x_zero = minx
            y_zero = miny
        elif   CASE == "Bot-Center":
            x_zero = midx
            y_zero = miny
        elif   CASE == "Bot-Right":
            x_zero = maxx
            y_zero = miny
        elif   CASE == "Arc-Center":
            x_zero = 0
            y_zero = 0
        else:          #"Default"
            x_zero = 0
            y_zero = 0

        cnt=0
        for line in self.coords:
            XY = line
            self.coords[cnt][0] = XY[0] - x_zero + XOrigin
            self.coords[cnt][1] = XY[1] - y_zero + YOrigin
            self.coords[cnt][2] = XY[2] - x_zero + XOrigin
            self.coords[cnt][3] = XY[3] - y_zero + YOrigin
            cnt=cnt+1

        self.MAXX=maxx - x_zero + XOrigin
        self.MINX=minx - x_zero + XOrigin
        self.MAXY=maxy - y_zero + YOrigin
        self.MINY=miny - y_zero + YOrigin

        self.Xzero = x_zero
        self.Yzero = y_zero

        if (not self.batch.get()):
            # Reset Status Bar and Entry Fields
            self.Input.configure(         bg = 'white' )
            self.entry_set(self.Entry_Yscale,  self.Entry_Yscale_Check()  ,1)
            self.entry_set(self.Entry_Xscale,  self.Entry_Xscale_Check()  ,1)
            self.entry_set(self.Entry_Sthick,  self.Entry_Sthick_Check()  ,1)
            self.entry_set(self.Entry_Lspace,  self.Entry_Lspace_Check()  ,1)
            self.entry_set(self.Entry_Cspace,  self.Entry_Cspace_Check()  ,1)
            self.entry_set(self.Entry_Wspace,  self.Entry_Wspace_Check()  ,1)
            self.entry_set(self.Entry_Tangle,  self.Entry_Tangle_Check()  ,1)
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() ,1)
            self.entry_set(self.Entry_Feed,    self.Entry_Feed_Check()    ,1)
            self.entry_set(self.Entry_Zsafe,   self.Entry_Zsafe_Check()   ,1)
            self.entry_set(self.Entry_Zcut,    self.Entry_Zcut_Check()    ,1)
            self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,1)
            self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),1)

            self.bounding_box.set("Bounding Box (WxH) = "    +
                                   "%.3g" % (maxx-minx)      +
                                   " %s " % self.units.get() +
                                   " x " +
                                   "%.3g" % (maxy-miny)      +
                                   " %s " % self.units.get() +
                                   " %s" % message2)
            self.statusMessage.set(self.bounding_box.get())

        if no_font_record != []:
            if (not self.batch.get()):
                self.statusbar.configure( bg = 'orange' )
            fmessage('Characters not found in font file:',False)
            fmessage("(",False)
            for entry in no_font_record:
                fmessage( "%s," %(entry),False)
            fmessage(")")

        if (not self.batch.get()):
            self.Plot_Data()
        ################
        #   End DoIt   #
        ################

    ##################################################
    def record_v_carve_data(self,x1,y1,phi,rout,loop_cnt, clean_flag):
        rbit = self.calc_vbit_dia() / 2.0

        Lx, Ly = Transform(0,rout,-phi)
        xnormv = x1+Lx
        ynormv = y1+Ly
        need_clean = 0

        if int(clean_flag) != 1:
            self.vcoords.append([xnormv, ynormv, rout, loop_cnt])

            if abs(rout - rbit) < Zero:
                need_clean = 1
        else:
            if rout > rbit:
                self.clean_coords.append([xnormv, ynormv, rout, loop_cnt])

        return xnormv,ynormv,rout,need_clean


    #####################################################
    # determine if a point is inside a given polygon or not
    # Polygon is a list of (x,y) pairs.
    # http://www.ariel.com.au/a/python-point-int-poly.html
    #####################################################
    def point_inside_polygon(self,x,y,poly):
        n = len(poly)
        inside = -1
        p1x = poly[0][0]
        p1y = poly[0][1]
        for i in range(n+1):
            p2x = poly[i%n][0]
            p2y = poly[i%n][1]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = inside * -1
            p1x,p1y = p2x,p2y

        return inside

    def V_Carve_It(self,clean_flag=0):
        global STOP_CALC
        self.master.unbind("<Configure>")
        STOP_CALC=0

        if self.units.get() == "mm":
            if float( self.v_step_len.get() ) <= .01:
                fmessage("v_step_len is very small setting to default metric value of .25 mm")
                self.v_step_len.set("0.25")

        if (self.Check_All_Variables() > 0):
            return
        if (clean_flag != 1 ):
            self.DoIt()
            self.clean_coords = []
            self.clean_coords_sort=[]
            self.v_clean_coords_sort=[]
            self.clean_segment=[]
        elif self.clean_coords_sort != [] or self.v_clean_coords_sort != []:
            # If there is existing cleanup data clear the screen before computing.
            self.clean_coords = []
            self.clean_coords_sort=[]
            self.v_clean_coords_sort=[]
            self.Plot_Data()

        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set('Preparing for V-Carve Calculations')
            self.master.update()

        #########################################
        # V-Carve Stuff
        #########################################

        if self.cut_type.get() == "v-carve" and self.fontdex.get() == False:
            v_flop    =  bool(self.v_flop.get())
            #V1.32 if self.DXF_source == "POTRACE" and self.input_type.get() != "text":
            #V1.32    v_flop  = not(v_flop)
            if self.mirror.get() == True:
                v_flop  = not(v_flop)
            if self.flip.get() == True:
                v_flop = not(v_flop)
            if self.v_pplot.get() == 1 and (not self.batch.get()):
                cszw = int(self.PreviewCanvas.cget("width"))
                cszh = int(self.PreviewCanvas.cget("height"))
                self.Plot_Data()
                PlotScale = self.pscale
                maxx = self.MAXX
                minx = self.MINX
                maxy = self.MAXY
                miny = self.MINY
                midx=(maxx+minx)/2
                midy=(maxy+miny)/2

            dline       = float(self.v_step_len.get())
            ###############################################################
            rbit        = self.calc_vbit_dia()/2.0
            if (clean_flag != 1 ):
                rmax = rbit
            else:
                rmax = max(rbit, float(self.clean_w.get())/2.0)
            ###############################################################

            v_drv_crner = float(self.v_drv_crner.get())
            v_stp_crner = float(self.v_stp_crner.get())
            #v_pplot     = bool(self.v_pplot.get())
            Acc         = float(self.accuracy.get())
            v_Acc       = float(self.v_acc.get())

            CHK_STRING  = str(self.v_check_all.get())
            b_carve     = bool(self.b_carve.get())
            if self.input_type.get() != "text":
                CHK_STRING  = "all"

            BIT_ANGLE   = float(self.v_bit_angle.get())

            dangle = degrees(dline/rbit)
            if dangle < 2.0:
                dangle = 2.0

            ## Reorder
            if self.input_type.get() == "image":
                ##########################
                ###   Create ECOORDS   ###
                ##########################
                ecoords = []
                Lbeg=[]
                Lend=[]
                for i in range(len(self.coords)):
                    [x1,y1,x2,y2,dummy1,dummy2]=self.coords[i]
                    if i == 0:
                        cnt=0
                        ecoords.append([x1,y1])
                        Lbeg.append(cnt)
                        cnt = cnt+1
                        ecoords.append([x2,y2])
                        oldx, oldy = x2, y2
                    else:
                        dist = sqrt((oldx - x1)**2 + (oldy - y1)**2)
                        # check and see if we need to move
                        # to a new discontinuous start point
                        #V1.32 if (dist > v_Acc):
                        if (dist > Zero):
                            Lend.append(cnt)
                            cnt = cnt+1
                            ecoords.append([x1,y1])
                            Lbeg.append(cnt)
                        cnt = cnt+1
                        ecoords.append([x2,y2])
                        oldx, oldy = x2, y2
                Lend.append(cnt)

                if self.DXF_source == "POTRACE" and self.input_type.get() != "text": #V1.32
                    v_flop  = not(v_flop)
                    Lflip=[]
                    Lnum=[]
                    for iloop in range(len(Lbeg)):
                        Lflip.append(False)
                        Lnum.append(0)
                else:
                    self.statusMessage.set('Checking Input Image Data')
                    self.master.update()
                    ######################################################
                    ### Fully Close Closed loops and Remove Open Loops ###
                    ######################################################
                    i = 0
                    LObeg = []
                    LOend = []
                    while i < len(Lbeg): #for each loop
                        [Xstart, Ystart] = ecoords[Lbeg[i]]
                        [Xend,   Yend  ] = ecoords[Lend[i]]

                        dist = sqrt((Xend-Xstart)**2 +(Yend-Ystart)**2)
                        if  dist <= v_Acc: #if end is the same as the beginning
                            ecoords[Lend[i]] = [Xstart, Ystart]
                            i = i+1
                        else:  #end != to beginning
                            LObeg.append(Lbeg.pop(i))
                            LOend.append(Lend.pop(i))

                    LNbeg=[]
                    LNend=[]
                    LNloop=[]
                    #######################################################
                    ###  For Each open loop connect to the next closest ###
                    ###  loop end until all of the loops are closed     ###
                    #######################################################
                    Lcnt=0
                    while len(LObeg) > 0: #for each Open Loop
                        Start = LObeg.pop(0)
                        End   = LOend.pop(0)
                        Lcnt = Lcnt+1
                        LNloop.append(Lcnt)
                        LNbeg.append(Start)
                        LNend.append(End)
                        [Xstart, Ystart] = ecoords[Start]

                        OPEN = True
                        while OPEN == True and len(LObeg) > 0:
                            [Xend,Yend] = ecoords[End]
                            dist_beg_min = sqrt((Xend-Xstart)**2 +(Yend-Ystart)**2)
                            dist_end_min = dist_beg_min
                            k_min_beg = -1
                            k_min_end = -1
                            for k in range(len(LObeg)):
                                [Xkstart, Ykstart] = ecoords[LObeg[k]]
                                [Xkend  ,   Ykend] = ecoords[LOend[k]]
                                dist_beg = sqrt((Xend-Xkstart)**2 +(Yend-Ykstart)**2)
                                dist_end = sqrt((Xend - Xkend)**2 +(Yend - Ykend)**2)

                                if dist_beg < dist_beg_min:
                                    dist_beg_min = dist_beg
                                    k_min_beg = k
                                if dist_end < dist_end_min:
                                    dist_end_min = dist_end
                                    k_min_end = k

                            if k_min_beg == -1 and k_min_end == -1:
                                kbeg = End
                                kend = Start
                                ecoords.append(ecoords[End])
                                ecoords.append(ecoords[Start])
                                LNloop.append(Lcnt)
                                LNbeg.append(len(ecoords)-2)
                                LNend.append(len(ecoords)-1)
                                OPEN = False

                            elif dist_end_min < dist_beg_min:
                                kend = LObeg.pop(k_min_end)
                                kbeg = LOend.pop(k_min_end)

                                ecoords.append(ecoords[End])
                                ecoords.append(ecoords[kbeg])

                                LNloop.append(Lcnt)
                                LNbeg.append(len(ecoords)-2)
                                LNend.append(len(ecoords)-1)
                                LNloop.append(Lcnt)
                                LNbeg.append(kbeg)
                                LNend.append(kend)
                                End  = kend
                            else:
                                kbeg = LObeg.pop(k_min_beg)
                                kend = LOend.pop(k_min_beg)

                                ecoords.append(ecoords[End])
                                ecoords.append(ecoords[kbeg])

                                LNloop.append(Lcnt)
                                LNbeg.append(len(ecoords)-2)
                                LNend.append(len(ecoords)-1)
                                LNloop.append(Lcnt)
                                LNbeg.append(kbeg)
                                LNend.append(kend)
                                End  = kend

                        if OPEN == True and len(LObeg) == 0:
                            ecoords.append(ecoords[End])
                            ecoords.append(ecoords[Start])
                            LNloop.append(Lcnt)
                            LNbeg.append(len(ecoords)-2)
                            LNend.append(len(ecoords)-1)

                    ###########################################################
                    ### Make new sequential ecoords for each new loop       ###
                    ###########################################################
                    Loop_last = -1
                    for k in range(len(LNbeg)):
                        Start = LNbeg[k]
                        End   = LNend[k]
                        Loop  = LNloop[k]
                        if Loop != Loop_last:
                            Lbeg.append(len(ecoords))

                            if Loop_last != -1:
                                Lend.append(len(ecoords)-1)
                            Loop_last = Loop

                        if Start > End:
                            step = -1
                        else:
                            step = 1
                        for i in range(Start,End+step,step):
                            [x1,y1]   = ecoords[i]
                            ecoords.append([x1,y1])
                    if len(Lbeg) > len(Lend):
                        Lend.append(len(ecoords)-1)

                    ########################################### New in V1.37
                    ### Check if loop is self intersecting  ###
                    ### If it is split into two loops       ###
                    ###########################################



                    ###########################################
                    ###   Determine loop directions CW/CCW  ###
                    ###########################################
                    self.statusMessage.set('Calculating Initial Loop Directions (CW/CCW)')
                    self.master.update()
                    Lflip = []
                    Lcw   = []

                    for k in range(len(Lbeg)):
                        Start = Lbeg[k]
                        End   = Lend[k]
                        step = 1

                        signedArea=0.0
                        #signedAreaB=0.0
                        #signedAreaC=0.0

                        [x1,y1]   = ecoords[Start]
                        for i in range(Start+1,End+step,step):
                            [x2,y2]   = ecoords[i]
                            signedArea += (x2-x1)*(y2+y1)
                            #signedAreaB += (x1 * y2 - x2 * y1)
                            #signedAreaC += (x2+x1)*(y2-y1)
                            x1=x2
                            y1=y2
                        if signedArea > 0.0:
                            Lflip.append(False)
                            Lcw.append(True)
                        else:
                            Lflip.append(True)
                            Lcw.append(False)

                    Nloops = len(Lbeg)
                    LoopTree=[]
                    Lnum=[]
                    for iloop in range(Nloops):
                        LoopTree.append([iloop,[],[]])
                        Lnum.append(iloop)

                    #####################################################
                    # For each loop determine if other loops are inside #
                    #####################################################
                    for iloop in range(Nloops):
                        CUR_PCT=float(iloop)/Nloops*100.0
                        self.statusMessage.set('Determining Which Side of Loop to Cut: %d of %d' %(iloop+1,Nloops))
                        self.master.update()
                        ipoly = ecoords[Lbeg[iloop]:Lend[iloop]]

                        ## Check points in other loops (could just check one) ##
                        if ipoly != []:
                            for jloop in range(Nloops):
                                if jloop != iloop:
                                    inside = 0
                                    #for jval in range(Lbeg[jloop],Lend[jloop]):
                                    #    inside = inside + self.point_inside_polygon(ecoords[jval][0],ecoords[jval][1],ipoly)
                                    jval = Lbeg[jloop]
                                    inside = inside + self.point_inside_polygon(ecoords[jval][0],ecoords[jval][1],ipoly)
                                    if inside > 0:
                                        Lflip[jloop] = not Lflip[jloop]
                                        LoopTree[iloop][1].append(jloop)
                                        LoopTree[jloop][2].append(iloop)

                    #####################################################
                    # Set Loop clockwise flag to the state of each loop #
                    #####################################################
                    # could flip cut side here for auto side determination
                    for iloop in range(Nloops):
                        if Lflip[iloop]:
                            Lcw[iloop]=not Lcw[iloop]

                    #########################
                    #### END NOT POTRACE ####
                    #########################

                CUR_PCT = 0.0
                #################################################
                # Find new order based on distance to next beg  #
                #################################################
                self.statusMessage.set('Re-Ordering Loops')
                self.master.update()
                order_out = []
                if len(Lflip)>0:
                    if Lflip[0]:
                        order_out.append([ Lend[0], Lbeg[0], Lnum[0] ])
                    else:
                        order_out.append([ Lbeg[0], Lend[0], Lnum[0] ])

                inext = 0
                total=len(Lbeg)
                for i in range(total-1):
                    Lbeg.pop(inext)
                    ii = Lend.pop(inext)
                    Lflip.pop(inext)
                    Lnum.pop(inext)

                    Xcur = ecoords[ii][0]
                    Ycur = ecoords[ii][1]

                    dx = Xcur - ecoords[ Lbeg[0] ][0]
                    dy = Ycur - ecoords[ Lbeg[0] ][1]
                    min_dist = dx*dx + dy*dy

                    inext=0
                    for j in range(1,len(Lbeg)):
                        dx = Xcur - ecoords[ Lbeg[j] ][0]
                        dy = Ycur - ecoords[ Lbeg[j] ][1]
                        dist = dx*dx + dy*dy
                        if dist < min_dist:
                            min_dist=dist
                            inext=j

                    if Lflip[inext]:
                        order_out.append([ Lend[inext], Lbeg[inext], Lnum[inext] ])
                    else:
                        order_out.append([ Lbeg[inext], Lend[inext], Lnum[inext] ])

                ###########################################################
                temp_coords=[]
                for k in range(len(order_out)):
                    [Start,End, LN] = order_out[k]
                    if Start > End:
                        step = -1
                    else:
                        step = 1
                    xlast = ""
                    ylast = ""
                    for i in range(Start+step,End+step,step):
                        if xlast != "" and ylast != "":
                            x1 = xlast
                            y1 = ylast
                        else:
                            [x1,y1] = ecoords[i-step]
                        [x2,y2] = ecoords[i]

                        Lseg = sqrt((x2-x1)**2 + (y2-y1)**2)
                        if Lseg >= v_Acc:
                            temp_coords.append([x1,y1,x2,y2,LN,0])
                            xlast = ""
                            ylast = ""
                        else:
                            last_segment = [x1,y1,x2,y2,LN,0]
                            xlast = x1
                            ylast = y1
                    if  xlast != "" and  ylast != "":
                        temp_coords.append(last_segment)

                self.coords = temp_coords

                for ijunk in range(len(self.coords)):
                    self.coords[ijunk][4]=0
                    self.coords[ijunk][5]=0
                ###################################################################################
                ###################################################################################
                ###for iloop in range(len(Lcw)):
                ###    print  LoopTree[iloop][0], LoopTree[iloop][1], LoopTree[iloop][2], Lcw[iloop]
                ###################################################################################
                ###################################################################################

##                Loop_map=[]
##                for iloop in range(len(Lcw)):
##                    Loop_map.append([])
##                    Loop_map[iloop].append(iloop)
##                    iloop_depth = len(LoopTree[iloop][2])
##
##                    if Lcw[iloop]:
##                        #print "T:iloop=",iloop
##                        #for jloop in range(len(Lcw)):
##                        #    if jloop in LoopTree[iloop][1]:
##                        for jloop in LoopTree[iloop][1]:
##                            ################################################
##                            # Find the loop that contains the current loop #
##                            # and include it in the list of loops to check #
##                            ################################################
##                            if ( len(LoopTree[jloop][2]) == (iloop_depth+1) ) and (jloop != iloop):
##                                #print "iloop,jloop=" ,iloop,jloop
##                                Loop_map[iloop].append(jloop)
##
##                    else: # not Lcw[iloop]:
##                        #print "F:iloop=",iloop
##                        ################################################
##                        # Find the loop that contains the current loop #
##                        # and include it in the list of loops to check #
##                        ################################################
##                        for jloop in LoopTree[iloop][2]:
##                            #print iloop_depth,len(LoopTree[jloop][2])
##                            if len(LoopTree[jloop][2]) == (iloop_depth-1):
##                                Loop_map[iloop].append(jloop)
##                        ################################################
##                        # Find the loops that are in the same loop     #
##                        # that contains the current loop and include   #
##                        # them in the list of loops to check           #
##                        ################################################
##                        for jloop in range(len(Lcw)):
##                            if LoopTree[iloop][2][:] == LoopTree[jloop][2][:] and (jloop != iloop):
##                                #print "compare",LoopTree[iloop][2][:], LoopTree[jloop][2][:]
##                                Loop_map[iloop].append(jloop)

                ###################################################################################
                ###################################################################################
                ###for iloop in range(len(Loop_map)):
                ###    print  Loop_map[iloop]
                ###################################################################################
                ###################################################################################

            #####################

            #set variable for first point in loop
            xa = 9999
            ya = 9999
            xb = 9999
            yb = 9999
            #set variable for the point previously calculated in a loop
            x0=9999
            y0=9999
            seg_sin0 = 2
            seg_cos0 = 2
            char_num0 = -1
            theta = 9999.0
            loop_cnt = 0
            if not v_flop:
                v_inc = 1
                v_index = -1
                i_x1 = 0
                i_y1 = 1
                i_x2 = 2
                i_y2 = 3
            else:
                v_inc = -1
                v_index = len(self.coords)
                i_x1 = 2
                i_y1 = 3
                i_x2 = 0
                i_y2 = 1

            coord_radius=[]
            #########################
            # Setup Grid Partitions #
            #########################
            xLength = self.MAXX-self.MINX
            yLength = self.MAXY-self.MINY

            xN=0
            yN=0

            xN_minus_1 = max(int(xLength/((2*rmax+dline)*1.1)),1)
            yN_minus_1 = max(int(yLength/((2*rmax+dline)*1.1)),1)

            xPartitionLength=xLength/xN_minus_1
            yPartitionLength=yLength/yN_minus_1

            xN = xN_minus_1+1
            yN = yN_minus_1+1

            self.xPartitionLength = xPartitionLength
            self.yPartitionLength = yPartitionLength

            self.partitionList = []

            for xCount in range(0,xN):
                self.partitionList.append([])
                for yCount in range(0,yN):
                    self.partitionList[xCount].append([])

            ###############################
            # End Setup Grid Partitions   #
            ###############################

            CUR_CNT=-1
            #for line_R in self.coords:
            while (len(self.coords) > CUR_CNT+1):
                CUR_CNT=CUR_CNT+1
                XY_R = self.coords[CUR_CNT][:]
                x1_R = XY_R[0]
                y1_R = XY_R[1]
                x2_R = XY_R[2]
                y2_R = XY_R[3]
                LENGTH = sqrt( (x2_R-x1_R)*(x2_R-x1_R) + (y2_R-y1_R)*(y2_R-y1_R) )
                # Check that segment is bigger than the set accuracy: New in V1.37
                if (LENGTH > Acc):
                    R_R = LENGTH/2 + rmax
                    X_R = (x1_R + x2_R)/2
                    Y_R = (y1_R + y2_R)/2
                    coord_radius.append([X_R, Y_R, R_R])

                    #####################################################
                    # Determine active partitions for each line segment #
                    #####################################################
                    coded_index=[]
                    ## find the local coordinates of the line segment ends
                    x1_G = XY_R[0]-self.MINX
                    y1_G = XY_R[1]-self.MINY
                    x2_G = XY_R[2]-self.MINX
                    y2_G = XY_R[3]-self.MINY

                    ## Find the grid box index for each line segment end
                    X1i = int( x1_G / xPartitionLength )
                    Y1i = int( y1_G / yPartitionLength )
                    X2i = int( x2_G / xPartitionLength )
                    Y2i = int( y2_G / yPartitionLength )

                    ## Find the max/min grid box locations
                    Xindex_min = min(X1i,X2i)
                    Xindex_max = max(X1i,X2i)
                    Yindex_min = min(Y1i,Y2i)
                    Yindex_max = max(Y1i,Y2i)

                    check_points=[]
                    if (Xindex_max > Xindex_min) and (abs(x2_G-x1_G) > Zero):
                        if (Yindex_max > Yindex_min) and (abs(y2_G-y1_G) > Zero):
                            check_points.append([X1i,Y1i])
                            check_points.append([X2i,Y2i])
                            ## Establish line equation variables: y=m*x+b
                            m_G = (y2_G-y1_G)/(x2_G-x1_G)
                            b_G = y1_G - m_G*x1_G
                            ## Add check point in each partition in the range of X values
                            x_ind_check = Xindex_min+1
                            while x_ind_check <= Xindex_max-1:
                                x_val = x_ind_check * xPartitionLength
                                y_val = m_G * x_val + b_G
                                y_ind_check = int(y_val/yPartitionLength)
                                check_points.append([x_ind_check,y_ind_check])
                                x_ind_check = x_ind_check + 1
                            ## Add check point in each partition in the range of Y values
                            y_ind_check = Yindex_min+1
                            while y_ind_check <= Yindex_max-1:
                                y_val =  y_ind_check * yPartitionLength
                                x_val = (y_val-b_G ) / m_G
                                x_ind_check = int(x_val/xPartitionLength)
                                check_points.append([x_ind_check,y_ind_check])
                                y_ind_check = y_ind_check + 1
                        else:
                            x_ind_check = Xindex_min
                            y_ind_check = Yindex_min
                            while x_ind_check <= Xindex_max:
                                check_points.append([x_ind_check,y_ind_check])
                                x_ind_check = x_ind_check + 1
                    else:
                        x_ind_check = Xindex_min
                        y_ind_check = Yindex_min
                        while y_ind_check <= Yindex_max:
                            check_points.append([x_ind_check,y_ind_check])
                            y_ind_check = y_ind_check + 1

                    ## For each grid box in check_points add the grid box and all adjacent grid boxes
                    ## to the list of boxes for this line segment
                    for xy_point in check_points:
                        xy_p = xy_point
                        xIndex = xy_p[0]
                        yIndex = xy_p[1]
                        for i in range( max(xIndex-1,0), min(xN,xIndex+2) ):
                            for j in range( max(yIndex-1,0), min(yN,yIndex+2) ):
                                coded_index.append(int(i+j*xN))

                    codedIndexSet= set(coded_index)
##                    ###################################
##                    ###  GRID TEXT PLOTTING STUFF    ##
##                    ## Plotting for grid debugging   ##
##                    ## Line end points are X's and   ##
##                    ## Active grids are 1's          ##
##                    ##################################
##                    IX1 = int((XY_R[0]-self.MINX)/xPartitionLength)
##                    IX2 = int((XY_R[2]-self.MINX)/xPartitionLength)
##                    IY1 = int((XY_R[1]-self.MINY)/yPartitionLength)
##                    IY2 = int((XY_R[3]-self.MINY)/yPartitionLength)
##                    print "x1=%.2f y1=%.2f x2=%.2f y2=%.2f" %(XY_R[0]-self.MINX, XY_R[1]-self.MINY, XY_R[2]-self.MINX, XY_R[3]-self.MINY) #, case_used)
##                    print "x1=%d y1=%d x2=%d y2=%d" %(IX1,IY1,IX2,IY2)
##                    for j in range(yN-1,-1,-1):
##                        print " "
##                        for i in range(0,xN):
##                            if int(i+j*xN) in coded_index:
##                                if (i==IX1 and j==IY1) or (i==IX2 and j==IY2):
##                                    print "X",
##                                else:
##                                    print "1",
##                            else:
##                                print "0",
##                    print "\n"
##                    ###END TEXT PLOTTING STUFF####

                    for thisCode in codedIndexSet:
                        thisIndex = thisCode
                        line_R_appended = XY_R
                        line_R_appended.append(X_R)
                        line_R_appended.append(Y_R)
                        line_R_appended.append(R_R)
                        self.partitionList[int(thisIndex%xN)][int(thisIndex/xN)].append(line_R_appended)
                    #########################################################
                    # End Determine active partitions for each line segment #
                    #########################################################


                # Remove segment if it is extremely short: New in V1.37
                else:
                    if (len(self.coords) > CUR_CNT+1):
                        DX_TEST = abs(self.coords[CUR_CNT][2]-self.coords[CUR_CNT+1][0])
                        DY_TEST = abs(self.coords[CUR_CNT][3]-self.coords[CUR_CNT+1][1])
                        if (DX_TEST < Acc and DY_TEST < Acc):
                            self.coords[CUR_CNT+1][0]=x1_R
                            self.coords[CUR_CNT+1][1]=y1_R
                    self.coords.pop(CUR_CNT)
                    CUR_CNT = CUR_CNT-1

            ## Loop through again just to determine the total length of segments
            ## For the percent complete calculation
            if (v_index >= len(self.coords)):
                v_index = len(self.coords)
            v_ind = v_index

            CUR_CNT=-1
            TOT_LENGTH = 0.0

            for line in range(len(self.coords)):
                CUR_CNT=CUR_CNT+1
                v_ind = v_ind + v_inc
                x1 = self.coords[v_ind][i_x1]
                y1 = self.coords[v_ind][i_y1]
                x2 = self.coords[v_ind][i_x2]
                y2 = self.coords[v_ind][i_y2]
                LENGTH = sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) )
                if clean_flag == 1:
                    if self.clean_segment[CUR_CNT] != 0:
                        TOT_LENGTH = TOT_LENGTH + LENGTH
                else:
                    TOT_LENGTH = TOT_LENGTH + LENGTH

            CUR_LENGTH = 0.0
            MAX_CNT = len(self.coords)
            CUR_CNT = -1
            START_TIME=time()

            ################################################################################################################
            ################################################################################################################
            ################################################################################################################
            #Update canvas with modified paths
            if (not self.batch.get()):
                self.Plot_Data()

            if TOT_LENGTH > 0.0:
                calc_flag=1
                for line in range(len(self.coords)):
                    CUR_CNT=CUR_CNT+1
                    ####################################################
                    if clean_flag == 0:
                        self.clean_segment.append(0)
                    elif len(self.clean_segment) != len(self.coords):
                        fmessage("Need to Recalculate V-Carve Path")
                        break
                    else:
                        calc_flag = self.clean_segment[CUR_CNT]
                    ####################################################
                    CUR_PCT=float(CUR_LENGTH)/TOT_LENGTH*100.0
                    if CUR_PCT > 0.0:
                        MIN_REMAIN =( time()-START_TIME )/60 * (100-CUR_PCT)/CUR_PCT
                        MIN_TOTAL = 100.0/CUR_PCT * ( time()-START_TIME )/60
                    else:
                        MIN_REMAIN = -1
                        MIN_TOTAL = -1
                    if (not self.batch.get()):
                        self.statusMessage.set('%.1f %% ( %.1f Minutes Remaining | %.1f Minutes Total )' %( CUR_PCT, MIN_REMAIN, MIN_TOTAL ) )
                        self.statusbar.configure( bg = 'yellow' )
                        self.PreviewCanvas.update()

                    if STOP_CALC != 0:
                        STOP_CALC=0

                        if (clean_flag != 1 ):
                            self.vcoords = []
                        else:
                            self.clean_coords = []
                            calc_flag = 0
                        break

                    v_index = v_index + v_inc
                    New_Loop=0
                    x1 = self.coords[v_index][i_x1]
                    y1 = self.coords[v_index][i_y1]
                    x2 = self.coords[v_index][i_x2]
                    y2 = self.coords[v_index][i_y2]
                    char_num = int(self.coords[v_index][5])
                    dx = x2-x1
                    dy = y2-y1
                    Lseg = sqrt(dx*dx + dy*dy)
                    if calc_flag != 0:
                        CUR_LENGTH = CUR_LENGTH + Lseg
                    else:
                        continue

                    if Lseg < Acc:
                        #print "Ignoring segment with length = ",Lseg
                        continue

                    #calculate the sin and cos of the coord transformation needed for
                    #the distance calculations
                    seg_sin =  dy/Lseg
                    seg_cos = -dx/Lseg
                    phi = Get_Angle(seg_sin,seg_cos)
                    if (fabs(x1-x0) > Zero or fabs(y1-y0) > Zero) or char_num != char_num0:
                        New_Loop=1
                        loop_cnt=loop_cnt+1
                        xa = float(x1)
                        ya = float(y1)
                        xb = float(x2)
                        yb = float(y2)
                        theta = 9999.0
                        seg_sin0 = 2
                        seg_cos0 = 2

                    if seg_cos0 > 1.0:
                        delta = 180
                    else:
                        xtmp1 = (x2-x1) * seg_cos0 - (y2-y1) * seg_sin0
                        ytmp1 = (x2-x1) * seg_sin0 + (y2-y1) * seg_cos0
                        Ltmp=sqrt( xtmp1*xtmp1 + ytmp1*ytmp1 )
                        d_seg_sin =   ytmp1/Ltmp
                        d_seg_cos =   xtmp1/Ltmp
                        delta = Get_Angle(d_seg_sin,d_seg_cos)
                    if delta < float(v_drv_crner) and BIT_ANGLE !=0 and not b_carve and clean_flag != 1:
                        #drive to corner
                        self.vcoords.append([x1, y1, 0.0, loop_cnt])

                    if delta > float(v_stp_crner):
                       #add sub-steps around corner
                       ###########################
                       phisteps = max(floor((delta-180)/dangle),2)
                       step_phi = (delta-180)/phisteps
                       pcnt = 0
                       while pcnt < phisteps-1:
                           pcnt=pcnt+1
                           sub_phi =  radians( -pcnt*step_phi + theta )
                           sub_seg_cos = cos(sub_phi)
                           sub_seg_sin = sin(sub_phi)

                           rout = self.find_max_circle(x1,y1,rmax,char_num,sub_seg_sin,sub_seg_cos,1,Acc,CHK_STRING)
                           xv,yv,rv,clean_seg=self.record_v_carve_data(x1,y1,sub_phi,rout,loop_cnt,clean_flag)
                           self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                           if self.v_pplot.get() == 1 and (not self.batch.get()):
                               self.Plot_Circ(xv,yv,midx,midy,cszw,cszh,PlotScale,"blue",rv,0)
                       #############################
                    ### end for linec in self.coords
                    theta = phi
                    x0=x2
                    y0=y2
                    seg_sin0=seg_sin
                    seg_cos0=seg_cos
                    char_num0=char_num

                    #Calculate the number of steps then the dx and dy for each step
                    #Don't calculate at the joints.
                    nsteps = max(floor(Lseg/dline),2)
                    dxpt = dx/nsteps
                    dypt = dy/nsteps

                    ### This makes sure the first cut start at the begining of the first segment
                    cnt = 0
                    if New_Loop == 1 and BIT_ANGLE !=0 and not b_carve:
                        cnt = -1

                    seg_sin =  dy/Lseg
                    seg_cos = -dx/Lseg
                    phi2 = radians(Get_Angle(seg_sin,seg_cos))
                    while cnt < nsteps-1:
                        cnt=cnt+1
                        #determine location of next step along outline (xpt, ypt)
                        xpt = x1 + dxpt * cnt
                        ypt = y1 + dypt * cnt

                        rout = self.find_max_circle(xpt,ypt,rmax,char_num,seg_sin,seg_cos,0,Acc,CHK_STRING)
                        # Make the first cut drive down at an angle instead of straight down plunge
                        if cnt==0 and not b_carve:
                            rout = 0.0
                        xv,yv,rv,clean_seg=self.record_v_carve_data(xpt,ypt,phi2,rout,loop_cnt,clean_flag)

                        self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                        if self.v_pplot.get() == 1 and (not self.batch.get()):
                            self.master.update_idletasks()
                            self.Plot_Circ(xv,yv,midx,midy,cszw,cszh,PlotScale,"blue",rv,0)

                        if (New_Loop==1 and cnt==1):
                            xpta  = xpt
                            ypta  = ypt
                            phi2a = phi2
                            routa = rout

                    #################################################
                    # Check to see if we need to close an open loop
                    #################################################
                    if (abs(x2-xa) < Acc and abs(y2-ya) < Acc):
                        xtmp1 = (xb-xa) * seg_cos0 - (yb-ya) * seg_sin0
                        ytmp1 = (xb-xa) * seg_sin0 + (yb-ya) * seg_cos0
                        Ltmp=sqrt( xtmp1*xtmp1 + ytmp1*ytmp1 )
                        d_seg_sin =   ytmp1/Ltmp
                        d_seg_cos =   xtmp1/Ltmp
                        delta = Get_Angle(d_seg_sin,d_seg_cos)
                        if delta < v_drv_crner and clean_flag != 1:
                            #drive to corner
                            self.vcoords.append([xa, ya, 0.0, loop_cnt])

                        elif delta > v_stp_crner:
                            #add substeps around corner
                            phisteps = max(floor((delta-180)/dangle),2)
                            step_phi = (delta-180)/phisteps
                            pcnt = 0

                            while pcnt < phisteps-1:
                                pcnt=pcnt+1
                                sub_phi =  radians( -pcnt*step_phi + theta )
                                sub_seg_cos = cos(sub_phi)
                                sub_seg_sin = sin(sub_phi)

                                rout = self.find_max_circle(xa,ya,rmax,char_num,sub_seg_sin,sub_seg_cos,1,Acc,CHK_STRING)
                                xv,yv,rv,clean_seg = self.record_v_carve_data(xa,ya,sub_phi,rout,loop_cnt,clean_flag)
                                self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                                if self.v_pplot.get() == 1 and (not self.batch.get()):
                                    self.Plot_Circ(xv,yv,midx,midy,cszw,cszh,PlotScale,"blue",rv,0)

                            xv,yv,rv,clean_seg = self.record_v_carve_data(xpta,ypta,phi2a,routa,loop_cnt,clean_flag)
                            self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                        else:
                            # Add closing segment
                            xv,yv,rv,clean_seg = self.record_v_carve_data(xpta,ypta,phi2a,routa,loop_cnt,clean_flag)
                            self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)

                #end for line in self coords


                #Reset Entry Fields in V-Carve Settings
                if (not self.batch.get()):
                    self.entry_set(self.Entry_Vbitangle,   self.Entry_Vbitangle_Check()   ,1)
                    self.entry_set(self.Entry_Vbitdia,     self.Entry_Vbitdia_Check()     ,1)
                    self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() ,1)
                    self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() ,1)
                    self.entry_set(self.Entry_OutsideAngle,self.Entry_OutsideAngle_Check(),1)
                    self.entry_set(self.Entry_StepSize,    self.Entry_StepSize_Check()    ,1)
                    self.entry_set(self.Entry_LoopAcc,     self.Entry_LoopAcc_Check()     ,1)
                    self.entry_set(self.Entry_Accuracy,    self.Entry_Accuracy_Check()    ,1)
                    self.entry_set(self.Entry_W_CLEAN,     self.Entry_W_CLEAN_Check()     ,1)
                    self.entry_set(self.Entry_CLEAN_DIA,   self.Entry_CLEAN_DIA_Check()   ,1)
                    self.entry_set(self.Entry_STEP_OVER,   self.Entry_STEP_OVER_Check()   ,1)
                    self.entry_set(self.Entry_V_CLEAN,     self.Entry_V_CLEAN_Check()     ,1)


            if CUR_CNT==MAX_CNT-1 and (not self.batch.get()):
                self.statusMessage.set('Done -- ' + self.bounding_box.get())
                self.statusbar.configure( bg = 'white' )
            ################################################################################################################
            ################################################################################################################
            ################################################################################################################

        self.master.bind("<Configure>", self.Master_Configure)
        #########################################
        # End V-Carve Stuff
        #########################################


    def Find_Paths(self,check_coords_in,clean_dia,Radjust,clean_step,skip,direction):
        check_coords=[]


        if direction == "Y":
            cnt = -1
            for line in check_coords_in:
                cnt=cnt+1
                XY=line
                check_coords.append([XY[1],XY[0],XY[2]])
        else:
            check_coords=check_coords_in

        minx_c=0
        maxx_c=0
        miny_c=0
        maxy_c=0
        if len(check_coords) > 0:
            minx_c = check_coords[0][0]-check_coords[0][2]
            maxx_c = check_coords[0][0]+check_coords[0][2]
            miny_c = check_coords[0][1]-check_coords[0][2]
            maxy_c = check_coords[0][1]+check_coords[0][2]
        for line in check_coords:
            XY    = line
            minx_c = min(minx_c, XY[0]-XY[2] )
            maxx_c = max(maxx_c, XY[0]+XY[2] )
            miny_c = min(miny_c, XY[1]-XY[2] )
            maxy_c = max(maxy_c, XY[1]+XY[2] )

        DX = clean_dia*clean_step
        DY = DX
        Xclean_coords=[]
        Xclean_coords_short=[]

        if direction != "None":
            #########################################################################
            # Find ends of horizontal lines for carving clean-up
            #########################################################################
            loop_cnt=0
            Y = miny_c
            line_cnt = skip-1
            while Y <= maxy_c:
                line_cnt = line_cnt+1
                X  = minx_c
                x1 = X
                x2 = X
                x1_old = x1
                x2_old = x2

                # Find relevant clean_coord_data
                ################################
                temp_coords=[]
                for line in check_coords:
                    XY=line
                    if Y < XY[1]+XY[2] and Y > XY[1]-XY[2]:
                        temp_coords.append(XY)
                ################################

                while X <= maxx_c:
                    for line in temp_coords:
                        XY=line
                        h = XY[0]
                        k = XY[1]
                        R = XY[2]-Radjust
                        dist=sqrt((X-h)**2 + (Y-k)**2)
                        if dist <= R:
                            Root = sqrt(R**2 - (Y-k)**2)
                            XL = h-Root
                            XR = h+Root
                            if XL < x1:
                                x1 = XL
                            if XR > x2:
                                x2 = XR
                    if x1==x2:
                        X  = X+DX
                        x1 = X
                        x2 = X
                    elif (x1 == x1_old) and (x2 == x2_old):
                        loop_cnt=loop_cnt+1
                        Xclean_coords.append([x1,Y,loop_cnt])
                        Xclean_coords.append([x2,Y,loop_cnt])
                        if line_cnt == skip:
                            Xclean_coords_short.append([x1,Y,loop_cnt])
                            Xclean_coords_short.append([x2,Y,loop_cnt])

                        X  = X+DX
                        x1 = X
                        x2 = X
                    else:
                        X = x2
                    x1_old = x1
                    x2_old = x2
                if line_cnt == skip:
                    line_cnt = 0
                Y=Y+DY
            #########################################################################


        Xclean_coords_out=[]
        Xclean_coords_short_out=[]
        if direction == "Y":

            cnt = -1
            for line in Xclean_coords:
                cnt=cnt+1
                XY=line
                Xclean_coords_out.append([XY[1],XY[0],XY[2]])

            cnt = -1
            for line in Xclean_coords_short:
                cnt=cnt+1
                XY=line
                Xclean_coords_short_out.append([XY[1],XY[0],XY[2]])
        else:
            Xclean_coords_out=Xclean_coords
            Xclean_coords_short_out=Xclean_coords_short

        return Xclean_coords_out,Xclean_coords_short_out


    def Clean_Path_Calc(self,bit_type="straight"):
        #######################################
        #reorganize clean_coords              #
        #######################################
        if bit_type=="straight":
            test_clean = self.clean_P.get()   + self.clean_X.get()   + self.clean_Y.get()
        else:
            test_clean = self.v_clean_P.get() + self.v_clean_Y.get() + self.v_clean_X.get()

        rbit      = self.calc_vbit_dia() / 2.0
        clean_w   = float(self.clean_w.get())
        check_coords=[]

        self.statusbar.configure( bg = 'yellow' )
        if bit_type=="straight":
            self.statusMessage.set('Calculating Cleanup Cut Paths')
            self.master.update()
            self.clean_coords_sort   = []

            input_step_over = float(self.clean_step.get()) #percent of cut DIA
            min_step_over = 25 #percent of cut DIA
            skip = ceil(input_step_over/min_step_over)
            step_over = input_step_over/skip

            clean_dia = float(self.clean_dia.get())          #diameter of cleanup bit
            clean_step = step_over/100.0
            Radjust   = clean_dia/2.0 + rbit
            check_coords = self.clean_coords

        elif bit_type == "v-bit":
            skip = 1
            clean_step = 1.0
            self.statusMessage.set('Calculating V-Bit Cleanup Cut Paths')
            self.master.update()
            self.v_clean_coords_sort = []

            clean_dia  = float(self.clean_v.get())*2.0  #effective diameter of clean-up v-bit
            if float(clean_dia) < Zero:
                return
            # We could add something to the readjust line to let the cutter go closer
            # to the limit but avoid contact with the previously v-carved surface.
            Radjust   =   clean_dia/4.0 + rbit
            #Radjust   =   rbit
            for line in self.clean_coords:
                XY    = line
                R = XY[2]-Radjust
                if R > 0 and R < float(self.clean_dia.get())/2.0:
                    check_coords.append(XY)


        if self.cut_type.get() == "v-carve" and len(self.clean_coords) > 1 and test_clean > 0:
            DX = clean_dia*clean_step
            DY = DX

            if bit_type=="straight":
                MAXD=clean_dia
            else:
                MAXD=sqrt(DX**2+DY**2)*1.1

            Xclean_coords=[]
            Yclean_coords=[]
            clean_coords_out=[]

            if test_clean > 0:
                #########################################################################
                # Find ends of horizontal lines for carving clean-up
                #########################################################################
                Xclean_perimeter,Xclean_coords = self.Find_Paths(check_coords,clean_dia,Radjust,clean_step,skip,"X")

                #########################################################################
                # Find ends of Vertical lines for carving clean-up
                #########################################################################
                Yclean_perimeter,Yclean_coords = self.Find_Paths(check_coords,clean_dia,Radjust,clean_step,skip,"Y")

                loop_cnt = 0
                #######################################################
                # Find new order based on distance                    #
                #######################################################
                if (self.clean_P.get() == 1 and bit_type != "v-bit") or \
                   (self.v_clean_P.get() == 1 and bit_type == "v-bit"):

                    ########################################
                    ecoords=[]
                    for line in Xclean_perimeter:
                        XY=line
                        ecoords.append([XY[0],XY[1]])

                    for line in Yclean_perimeter:
                        XY=line
                        ecoords.append([XY[0],XY[1]])

                    ################
                    ###   ends   ###
                    ################
                    Lbeg=[]
                    for i in range(1,len(ecoords)):
                        Lbeg.append(i)

                    ########################################
                    order_out = []
                    if len(ecoords)>0:
                        order_out.append(Lbeg[0])
                    inext = 0
                    total=len(Lbeg)
                    for i in range(total-1):
                        ii=Lbeg.pop(inext)
                        Xcur = ecoords[ii][0]
                        Ycur = ecoords[ii][1]
                        dx = Xcur - ecoords[ Lbeg[0] ][0]
                        dy = Ycur - ecoords[ Lbeg[0] ][1]
                        min_dist = dx*dx + dy*dy

                        inext=0
                        for j in range(1,len(Lbeg)):
                            dx = Xcur - ecoords[ Lbeg[j] ][0]
                            dy = Ycur - ecoords[ Lbeg[j] ][1]
                            dist = dx*dx + dy*dy
                            if dist < min_dist:
                                min_dist=dist
                                inext=j
                        order_out.append(Lbeg[inext])
                    ###########################################################
                    x_start_loop = -8888
                    y_start_loop = -8888
                    x_old=-999
                    y_old=-999
                    loop_cnt=1
                    for i in order_out:
                        x1   = ecoords[i][0]
                        y1   = ecoords[i][1]
                        dx = x1-x_old
                        dy = y1-y_old
                        dist = sqrt(dx*dx + dy*dy)
                        if dist > MAXD:
                            dx = x_start_loop-x_old
                            dy = y_start_loop-y_old
                            dist = sqrt(dx*dx + dy*dy)
                            if dist < MAXD:
                                clean_coords_out.append([x_start_loop,y_start_loop,clean_dia/2,loop_cnt])
                            loop_cnt=loop_cnt+1
                            x_start_loop=x1
                            y_start_loop=y1
                        clean_coords_out.append([x1,y1,clean_dia/2,loop_cnt])
                        x_old=x1
                        y_old=y1

                ###########################################################
                # Now deal with the horizontal line cuts
                ###########################################################
                if (self.clean_X.get() == 1 and bit_type != "v-bit") or \
                   (self.v_clean_X.get() == 1 and bit_type == "v-bit"):
                    x_old=-999
                    y_old=-999
                    order_out=self.Sort_Paths(Xclean_coords)
                    loop_old=-1
                    for line in order_out:
                        temp=line
                        if temp[0] > temp[1]:
                            step = -1
                        else:
                            step = 1
                        for i in range(temp[0],temp[1]+step,step):
                            x1   = Xclean_coords[i][0]
                            y1   = Xclean_coords[i][1]
                            loop = Xclean_coords[i][2]
                            dx = x1-x_old
                            dy = y1-y_old
                            dist = sqrt(dx*dx + dy*dy)
                            if dist > MAXD and loop != loop_old:
                                loop_cnt=loop_cnt+1
                            clean_coords_out.append([x1,y1,clean_dia/2,loop_cnt])
                            x_old=x1
                            y_old=y1
                            loop_old=loop


                ###########################################################
                # Now deal with the vertical line cuts
                ###########################################################
                if (self.clean_Y.get() == 1 and bit_type != "v-bit") or \
                   (self.v_clean_Y.get() == 1 and bit_type == "v-bit"):
                    x_old=-999
                    y_old=-999
                    order_out=self.Sort_Paths(Yclean_coords)
                    loop_old=-1
                    for line in order_out:
                        temp=line
                        if temp[0] > temp[1]:
                            step = -1
                        else:
                            step = 1
                        for i in range(temp[0],temp[1]+step,step):
                            x1   = Yclean_coords[i][0]
                            y1   = Yclean_coords[i][1]
                            loop = Yclean_coords[i][2]
                            dx = x1-x_old
                            dy = y1-y_old
                            dist = sqrt(dx*dx + dy*dy)
                            if dist > MAXD and loop != loop_old:
                                loop_cnt=loop_cnt+1
                            clean_coords_out.append([x1,y1,clean_dia/2,loop_cnt])
                            x_old=x1
                            y_old=y1
                            loop_old=loop


            self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check()     ,1)
            self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check()     ,1)
            self.entry_set(self.Entry_V_CLEAN,     self.Entry_V_CLEAN_Check()     ,1)

            if bit_type=="v-bit":
                self.v_clean_coords_sort = clean_coords_out
            else:
                self.clean_coords_sort = clean_coords_out
        self.statusMessage.set('Done Calculating Cleanup Cut Paths')
        self.statusbar.configure( bg = 'white' )
        self.master.update_idletasks()
        #######################################
        #End Reorganize                       #
        #######################################


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

        D_Yloc  = 12
        D_dY = 24
        xd_label_L = 12

        w_label=100
        w_entry=60
        w_units=35
        xd_entry_L=xd_label_L+w_label+10
        xd_units_L=xd_entry_L+w_entry+5

        D_Yloc=D_Yloc+D_dY
        self.Label_BMPturnpol = Label(pbm_settings,text="Turn Policy")
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

        D_Yloc=D_Yloc+D_dY
        self.Label_BMPturdsize = Label(pbm_settings,text="Turd Size")
        self.Label_BMPturdsize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPturdsize = Entry(pbm_settings,width="15")
        self.Entry_BMPturdsize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPturdsize.configure(textvariable=self.bmp_turdsize)
        self.bmp_turdsize.trace_variable("w", self.Entry_BMPturdsize_Callback)
        self.Label_BMPturdsize2 = Label(pbm_settings,text="Suppress speckles of up to this pixel size")
        self.Label_BMPturdsize2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(),2)

        D_Yloc=D_Yloc+D_dY+5
        self.Label_BMPalphamax = Label(pbm_settings,text="Alpha Max")
        self.Label_BMPalphamax.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPalphamax = Entry(pbm_settings,width="15")
        self.Entry_BMPalphamax.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPalphamax.configure(textvariable=self.bmp_alphamax)
        self.bmp_alphamax.trace_variable("w", self.Entry_BMPalphamax_Callback)
        self.Label_BMPalphamax2 = Label(pbm_settings,text="0.0 = sharp corners, 1.33 = smoothed corners")
        self.Label_BMPalphamax2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_BMP_longcurve = Label(pbm_settings,text="Long Curve")
        self.Label_BMP_longcurve.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_BMP_longcurve = Checkbutton(pbm_settings,text="", anchor=W)
        self.Checkbutton_BMP_longcurve.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_BMP_longcurve.configure(variable=self.bmp_longcurve)
        self.Label_BMP_longcurve2 = Label(pbm_settings,text="Enable Curve Optimization")
        self.Label_BMP_longcurve2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)

        D_Yloc=D_Yloc+D_dY
        self.Label_BMPoptTolerance = Label(pbm_settings,text="Opt Tolerance")
        self.Label_BMPoptTolerance.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPoptTolerance = Entry(pbm_settings,width="15")
        self.Entry_BMPoptTolerance.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPoptTolerance.configure(textvariable=self.bmp_opttolerance)
        self.bmp_opttolerance.trace_variable("w", self.Entry_BMPoptTolerance_Callback)
        self.Label_BMPoptTolerance2 = Label(pbm_settings,text="Curve Optimization Tolerance")
        self.Label_BMPoptTolerance2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(),2)


        pbm_settings.update_idletasks()
        Ybut=int(pbm_settings.winfo_height())-30
        Xbut=int(pbm_settings.winfo_width()/2)

        self.PBM_Reload = Button(pbm_settings,text="Re-Load Image")
        self.PBM_Reload.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")
        self.PBM_Reload.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.PBM_Close = Button(pbm_settings,text="Close",command=self.Close_Current_Window_Click)
        self.PBM_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")


        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            pbm_settings.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            pass

################################################################################
#                         General Settings Window                              #
################################################################################
    def GEN_Settings_Window(self):
        gen_settings = Toplevel(width=600, height=405)
        gen_settings.grab_set() # Use grab_set to prevent user input in the main window during calculations
        gen_settings.resizable(0,0)
        gen_settings.title('Settings')
        gen_settings.iconname("Settings")

        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            gen_settings.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            pass

        D_Yloc  = 6
        D_dY = 24
        xd_label_L = 12

        w_label=110+25
        w_entry=60
        w_units=35
        xd_entry_L=xd_label_L+w_label+10
        xd_units_L=xd_entry_L+w_entry+5

        #Radio Button
        D_Yloc=D_Yloc+D_dY
        self.Label_Units = Label(gen_settings,text="Units")
        self.Label_Units.place(x=xd_label_L, y=D_Yloc, width=113, height=21)
        self.Radio_Units_IN = Radiobutton(gen_settings,text="inch", value="in",
                                         width="100", anchor=W)
        self.Radio_Units_IN.place(x=w_label+22, y=D_Yloc, width=75, height=23)
        self.Radio_Units_IN.configure(variable=self.units, command=self.Entry_units_var_Callback )
        self.Radio_Units_MM = Radiobutton(gen_settings,text="mm", value="mm",
                                         width="100", anchor=W)
        self.Radio_Units_MM.place(x=w_label+110, y=D_Yloc, width=75, height=23)
        self.Radio_Units_MM.configure(variable=self.units, command=self.Entry_units_var_Callback )


        D_Yloc=D_Yloc+D_dY
        self.Label_Xoffset = Label(gen_settings,text="X Offset")
        self.Label_Xoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Xoffset_u = Label(gen_settings,textvariable=self.units, anchor=W)
        self.Label_Xoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Xoffset = Entry(gen_settings,width="15")
        self.Entry_Xoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Xoffset.configure(textvariable=self.xorigin)
        self.xorigin.trace_variable("w", self.Entry_Xoffset_Callback)
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_Yoffset = Label(gen_settings,text="Y Offset")
        self.Label_Yoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Yoffset_u = Label(gen_settings,textvariable=self.units, anchor=W)
        self.Label_Yoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Yoffset = Entry(gen_settings,width="15")
        self.Entry_Yoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Yoffset.configure(textvariable=self.yorigin)
        self.yorigin.trace_variable("w", self.Entry_Yoffset_Callback)
        self.entry_set(self.Entry_Yoffset,self.Entry_Yoffset_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_ArcAngle = Label(gen_settings,text="Arc Angle")
        self.Label_ArcAngle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_ArcAngle_u = Label(gen_settings,text="deg", anchor=W)
        self.Label_ArcAngle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_ArcAngle = Entry(gen_settings,width="15")
        self.Entry_ArcAngle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_ArcAngle.configure(textvariable=self.segarc)
        self.segarc.trace_variable("w", self.Entry_ArcAngle_Callback)
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_Accuracy = Label(gen_settings,text="Accuracy")
        self.Label_Accuracy.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Accuracy_u = Label(gen_settings,textvariable=self.units, anchor=W)
        self.Label_Accuracy_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Accuracy = Entry(gen_settings,width="15")
        self.Entry_Accuracy.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Accuracy.configure(textvariable=self.accuracy)
        self.accuracy.trace_variable("w", self.Entry_Accuracy_Callback)
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_ext_char = Label(gen_settings,text="Extended Characters")
        self.Label_ext_char.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_ext_char = Checkbutton(gen_settings,text="", anchor=W)
        self.Checkbutton_ext_char.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_ext_char.configure(variable=self.ext_char)
        self.ext_char.trace_variable("w", self.Settings_ReLoad_Click)


        D_Yloc=D_Yloc+D_dY
        self.Label_clean = Label(gen_settings,text="Enable Arc Fitting")
        self.Label_clean.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_clean = Checkbutton(gen_settings,text="", anchor=W)
        self.Checkbutton_clean.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_clean.configure(variable=self.arc_fit)

        D_Yloc=D_Yloc+D_dY
        self.Label_Gpre = Label(gen_settings,text="G Code Header")
        self.Label_Gpre.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpre = Entry(gen_settings,width="15")
        self.Entry_Gpre.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpre.configure(textvariable=self.gpre)

        D_Yloc=D_Yloc+D_dY
        self.Label_Gpost = Label(gen_settings,text="G Code Postscript")
        self.Label_Gpost.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpost = Entry(gen_settings)
        self.Entry_Gpost.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpost.configure(textvariable=self.gpost)

        D_Yloc=D_Yloc+D_dY
        self.Label_var_dis = Label(gen_settings,text="Disable Variables")
        self.Label_var_dis.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_var_dis = Checkbutton(gen_settings,text="", anchor=W)
        self.Checkbutton_var_dis.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_var_dis.configure(variable=self.var_dis)

        D_Yloc=D_Yloc+D_dY
        self.Label_Fontdir = Label(gen_settings,text="Font Directory")
        self.Label_Fontdir.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Fontdir = Entry(gen_settings,width="15")
        self.Entry_Fontdir.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Fontdir.configure(textvariable=self.fontdir)
        self.Fontdir = Button(gen_settings,text="Select Dir")
        self.Fontdir.place(x=xd_entry_L+310, y=D_Yloc, width=w_label-25, height=23)

        D_Yloc=D_Yloc+D_dY
        self.Label_Hcalc = Label(gen_settings,text="Height Calculation")
        self.Label_Hcalc.place(x=xd_label_L, y=D_Yloc, width=113, height=21)
        self.Radio_Hcalc_ALL = Radiobutton(gen_settings,text="Max All", \
                                            value="max_all", width="110", anchor=W)
        self.Radio_Hcalc_ALL.place(x=w_label+110, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_ALL.configure(variable=self.H_CALC )
        self.Radio_Hcalc_USE = Radiobutton(gen_settings,text="Max Used", \
                                            value="max_use", width="110", anchor=W)
        self.Radio_Hcalc_USE.place(x=w_label+22, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_USE.configure(variable=self.H_CALC )

        if self.input_type.get() != "text":
                self.Entry_Fontdir.configure(state="disabled")
                self.Fontdir.configure(state="disabled")
                self.Radio_Hcalc_ALL.configure(state="disabled")
                self.Radio_Hcalc_USE.configure(state="disabled")
        else:
            self.Fontdir.bind("<ButtonRelease-1>", self.Fontdir_Click)

        D_Yloc=D_Yloc+24
        self.Label_Box = Label(gen_settings,text="Add Box/Circle")
        self.Label_Box.place(x=xd_label_L, y=D_Yloc, width=113, height=21)
        self.Radio_Box_N = Radiobutton(gen_settings,text="No", value="no_box", anchor=W)
        self.Radio_Box_N.place(x=w_label+22, y=D_Yloc, width=55, height=23) #132
        self.Radio_Box_N.configure(variable=self.plotbox )
        self.Radio_Box_Y = Radiobutton(gen_settings,text="Yes", value="box", anchor=W)
        self.Radio_Box_Y.place(x=w_label+75, y=D_Yloc, width=55, height=23) #185
        self.Radio_Box_Y.configure(variable=self.plotbox )

        self.Label_BoxGap = Label(gen_settings,text="Box/Circle Gap:", anchor=E)
        self.Label_BoxGap.place(x=w_label+125, y=D_Yloc, width=w_label, height=21) #252
        self.Entry_BoxGap = Entry(gen_settings)
        self.Entry_BoxGap.place(x=w_label+262, y=D_Yloc, width=w_entry, height=23) #372
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(gen_settings,textvariable=self.units, anchor=W)

        self.Label_BoxGap_u.place(x=w_label+325, y=D_Yloc, width=100, height=21) #435
        self.entry_set(self.Entry_BoxGap,self.Entry_BoxGap_Check(),2)

        ## Buttons ##
        gen_settings.update_idletasks()
        Ybut=int(gen_settings.winfo_height())-30
        Xbut=int(gen_settings.winfo_width()/2)

        self.GEN_Reload = Button(gen_settings,text="Recalculate")
        self.GEN_Reload.place(x=Xbut-65, y=Ybut, width=130, height=30, anchor="e")
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        self.GEN_Recalculate = Button(gen_settings,text="Re-Load Image")
        self.GEN_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="c")
        self.GEN_Recalculate.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.GEN_Close = Button(gen_settings,text="Close",command=self.Close_Current_Window_Click)
        self.GEN_Close.place(x=Xbut+65, y=Ybut, width=130, height=30, anchor="w")

    ################################################################################
    #                         V-Carve Settings window                              #
    ################################################################################
    def VCARVE_Settings_Window(self):
        vcarve_settings = Toplevel(width=580, height=620)
        vcarve_settings.grab_set() # Use grab_set to prevent user input in the main window during calculations
        vcarve_settings.resizable(0,0)
        vcarve_settings.title('V-Carve Settings')
        vcarve_settings.iconname("V-Carve Settings")

        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            vcarve_settings.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            pass

        D_Yloc  = 12
        D_dY = 24
        xd_label_L = 12

        w_label=250
        w_entry=60
        w_units=35
        xd_entry_L=xd_label_L+w_label+10
        xd_units_L=xd_entry_L+w_entry+5

        D_Yloc=D_Yloc+D_dY
        self.Label_b_carve = Label(vcarve_settings,text="Ball-Carve (Use Ball Nose Cutter)")
        self.Label_b_carve.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_b_carve = Checkbutton(vcarve_settings,text="", anchor=W)
        self.Checkbutton_b_carve.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_b_carve.configure(variable=self.b_carve)
        self.b_carve.trace_variable("w", self.Entry_B_Carve_var_Callback)

        D_Yloc=D_Yloc+D_dY
        self.Label_Vbitangle = Label(vcarve_settings,text="V-Bit Angle")
        self.Label_Vbitangle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Vbitangle_u = Label(vcarve_settings,text="deg", anchor=W)
        self.Label_Vbitangle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Vbitangle = Entry(vcarve_settings,width="15")
        self.Entry_Vbitangle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Vbitangle.configure(textvariable=self.v_bit_angle)
        self.v_bit_angle.trace_variable("w", self.Entry_Vbitangle_Callback)
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_Vbitdia = Label(vcarve_settings,text="V-Bit Diameter")
        self.Label_Vbitdia.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Vbitdia_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_Vbitdia_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Vbitdia = Entry(vcarve_settings,width="15")
        self.Entry_Vbitdia.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Vbitdia.configure(textvariable=self.v_bit_dia)
        self.v_bit_dia.trace_variable("w", self.Entry_Vbitdia_Callback)
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_VDepthLimit = Label(vcarve_settings,text="Cut Depth Limit")
        self.Label_VDepthLimit.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_VDepthLimit_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_VDepthLimit_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_VDepthLimit = Entry(vcarve_settings,width="15")
        self.Entry_VDepthLimit.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_VDepthLimit.configure(textvariable=self.v_depth_lim)
        self.v_depth_lim.trace_variable("w", self.Entry_VDepthLimit_Callback)
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_maxcut = Label(vcarve_settings,text="Max Cut Depth")
        self.Label_maxcut.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_maxcut_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_maxcut_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Label_maxcut_i = Label(vcarve_settings,textvariable=self.maxcut, anchor=W)
        self.Label_maxcut_i.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=21)

        D_Yloc=D_Yloc+D_dY+5
        self.Label_InsideAngle = Label(vcarve_settings,text="Inside Corner Angle (Less Than)")
        self.Label_InsideAngle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_InsideAngle_u = Label(vcarve_settings,text="deg", anchor=W)
        self.Label_InsideAngle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_InsideAngle = Entry(vcarve_settings,width="15")
        self.Entry_InsideAngle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_InsideAngle.configure(textvariable=self.v_drv_crner)
        self.v_drv_crner.trace_variable("w", self.Entry_InsideAngle_Callback)
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_OutsideAngle = Label(vcarve_settings,text="Outside Corner Angle (Greater Than)")
        self.Label_OutsideAngle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_OutsideAngle_u = Label(vcarve_settings,text="deg", anchor=W)
        self.Label_OutsideAngle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_OutsideAngle = Entry(vcarve_settings,width="15")
        self.Entry_OutsideAngle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_OutsideAngle.configure(textvariable=self.v_stp_crner)
        self.v_stp_crner.trace_variable("w", self.Entry_OutsideAngle_Callback)
        self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check(),2)

        D_Yloc=D_Yloc+D_dY+5
        self.Label_StepSize = Label(vcarve_settings,text="Sub-Step Length")
        self.Label_StepSize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_StepSize_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_StepSize_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_StepSize = Entry(vcarve_settings,width="15")
        self.Entry_StepSize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_StepSize.configure(textvariable=self.v_step_len)
        self.v_step_len.trace_variable("w", self.Entry_StepSize_Callback)
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_LoopAcc = Label(vcarve_settings,text="V-Carve Loop Accuracy")
        self.Label_LoopAcc.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_LoopAcc_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_LoopAcc_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_LoopAcc = Entry(vcarve_settings,width="15")
        self.Entry_LoopAcc.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_LoopAcc.configure(textvariable=self.v_acc)
        self.v_acc.trace_variable("w", self.Entry_LoopAcc_Callback)
        self.entry_set(self.Entry_LoopAcc, self.Entry_LoopAcc_Check(),2)

        #Radio Button
        D_Yloc=D_Yloc+D_dY+5
        self.Label_V_check_all = Label(vcarve_settings,text="Check all or Current Char Only")
        self.Label_V_check_all.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_V_check_all_Y = Radiobutton(vcarve_settings,text="All", value="all",
                                         width="100", anchor=W)
        self.Radio_V_check_all_Y.place(x=w_label+22, y=D_Yloc, width=75, height=23)
        self.Radio_V_check_all_Y.configure(variable=self.v_check_all )

        self.Radio_V_check_all_N = Radiobutton(vcarve_settings,text="Character only", value="chr",
                                                      anchor=W)
        self.Radio_V_check_all_N.place(x=w_label+110, y=D_Yloc, width=125, height=23)
        self.Radio_V_check_all_N.configure(variable=self.v_check_all )

        if self.input_type.get() != "text":
            self.Label_V_check_all.configure(state="disabled")
            self.Radio_V_check_all_Y.configure(state="disabled")
            self.Radio_V_check_all_N.configure(state="disabled")
        else:
            self.Label_V_check_all.configure(state="normal")
            self.Radio_V_check_all_Y.configure(state="normal")
            self.Radio_V_check_all_N.configure(state="normal")

        D_Yloc=D_Yloc+D_dY
        self.Label_v_flop = Label(vcarve_settings,text="Flip Normals (V-Carve Side)")
        self.Label_v_flop.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_flop = Checkbutton(vcarve_settings,text="", anchor=W)
        self.Checkbutton_v_flop.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_flop.configure(variable=self.v_flop)

        D_Yloc=D_Yloc+D_dY
        self.Label_v_pplot = Label(vcarve_settings,text="Plot During V-Carve Calculation")
        self.Label_v_pplot.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_pplot = Checkbutton(vcarve_settings,text="", anchor=W)
        self.Checkbutton_v_pplot.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)

        ## Cleanup Settings ##
        D_Yloc=D_Yloc+D_dY+12
        self.vcarve_separator1 = Frame(vcarve_settings,height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.place(x=0, y=D_Yloc,width=580, height=2)

        ### Update Idle tasks before requesting anything from winfo
        vcarve_settings.update_idletasks()

        right_but_loc=int(vcarve_settings.winfo_width())-10
        width_cb = 100
        height_cb = 35

        D_Yloc=D_Yloc+D_dY-12
        center_loc=int(float(vcarve_settings.winfo_width())/2)

        self.Label_clean = Label(vcarve_settings,text="Cleanup Operations")
        self.Label_clean.place(x=center_loc, y=D_Yloc, width=w_label, height=21,anchor=CENTER)

        D_Yloc=D_Yloc+D_dY
        self.Label_W_CLEAN = Label(vcarve_settings,text="Cleanup Search Distance")
        self.Label_W_CLEAN.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_W_CLEAN_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_W_CLEAN_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_W_CLEAN = Entry(vcarve_settings,width="15")
        self.Entry_W_CLEAN.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_W_CLEAN.configure(textvariable=self.clean_w)
        self.clean_w.trace_variable("w", self.Entry_W_CLEAN_Callback)
        self.entry_set(self.Entry_W_CLEAN, self.Entry_W_CLEAN_Check(),2)

        self.CLEAN_Recalculate = Button(vcarve_settings,text="Calculate\nCleanup", command=self.CLEAN_Recalculate_Click)
        self.CLEAN_Recalculate.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb*1.5, anchor="ne")

        D_Yloc=D_Yloc+D_dY+12
        self.Label_CLEAN_DIA = Label(vcarve_settings,text="Cleanup Cut Diameter")
        self.Label_CLEAN_DIA.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_CLEAN_DIA_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_CLEAN_DIA_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_CLEAN_DIA = Entry(vcarve_settings,width="15")
        self.Entry_CLEAN_DIA.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_CLEAN_DIA.configure(textvariable=self.clean_dia)
        self.clean_dia.trace_variable("w", self.Entry_CLEAN_DIA_Callback)
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_STEP_OVER = Label(vcarve_settings,text="Cleanup Cut Step Over")
        self.Label_STEP_OVER.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_STEP_OVER_u = Label(vcarve_settings,text="%", anchor=W)
        self.Label_STEP_OVER_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_STEP_OVER = Entry(vcarve_settings,width="15")
        self.Entry_STEP_OVER.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_STEP_OVER.configure(textvariable=self.clean_step)
        self.clean_step.trace_variable("w", self.Entry_STEP_OVER_Callback)
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(),2)

        D_Yloc=D_Yloc+24
        check_delta=40
        self.Label_clean_P = Label(vcarve_settings,text="Cleanup Cut Directions")
        self.Label_clean_P.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Write_Clean = Button(vcarve_settings,text="Save Cleanup\nG-Code", command=self.Write_Clean_Click)
        self.Write_Clean.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb, anchor="e")

        self.Checkbutton_clean_P = Checkbutton(vcarve_settings,text="P", anchor=W)
        self.Checkbutton_clean_P.configure(variable=self.clean_P)
        self.Checkbutton_clean_P.place(x=xd_entry_L, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_clean_X = Checkbutton(vcarve_settings,text="X", anchor=W)
        self.Checkbutton_clean_X.configure(variable=self.clean_X)
        self.Checkbutton_clean_X.place(x=xd_entry_L+check_delta, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_clean_Y = Checkbutton(vcarve_settings,text="Y", anchor=W)
        self.Checkbutton_clean_Y.configure(variable=self.clean_Y)
        self.Checkbutton_clean_Y.place(x=xd_entry_L+check_delta*2, y=D_Yloc, width=w_entry+40, height=23)

        D_Yloc=D_Yloc+12

        D_Yloc=D_Yloc+D_dY
        self.Label_V_CLEAN = Label(vcarve_settings,text="V-Bit Cleanup Step")
        self.Label_V_CLEAN.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_V_CLEAN_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_V_CLEAN_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_V_CLEAN = Entry(vcarve_settings,width="15")
        self.Entry_V_CLEAN.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_V_CLEAN.configure(textvariable=self.clean_v)
        self.clean_v.trace_variable("w", self.Entry_V_CLEAN_Callback)
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(),2)

        D_Yloc=D_Yloc+24
        self.Label_v_clean_P = Label(vcarve_settings,text="V-Bit Cut Directions")
        self.Label_v_clean_P.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Write_V_Clean = Button(vcarve_settings,text="Save V Cleanup\nG-Code", command=self.Write_V_Clean_Click)
        self.Write_V_Clean.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb, anchor="e")

        self.Checkbutton_v_clean_P = Checkbutton(vcarve_settings,text="P", anchor=W)
        self.Checkbutton_v_clean_P.configure(variable=self.v_clean_P)
        self.Checkbutton_v_clean_P.place(x=xd_entry_L, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_v_clean_X = Checkbutton(vcarve_settings,text="X", anchor=W)
        self.Checkbutton_v_clean_X.configure(variable=self.v_clean_X)
        self.Checkbutton_v_clean_X.place(x=xd_entry_L+check_delta, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_v_clean_Y = Checkbutton(vcarve_settings,text="Y", anchor=W)
        self.Checkbutton_v_clean_Y.configure(variable=self.v_clean_Y)
        self.Checkbutton_v_clean_Y.place(x=xd_entry_L+check_delta*2, y=D_Yloc, width=w_entry+40, height=23)

        ## V-Bit Picture ##
        self.PHOTO = PhotoImage(format='gif',data=
             'R0lGODlhoABQAIABAAAAAP///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEK'
            +'AAEALAAAAACgAFAAAAL+jI+pBu2/opy02ouzvg+G7m3iSJam1XHpybbuezhk'
            +'CFNyjZ9AS+ff6gtqdq5eMUQUKlG4GwsYW0ptPiMGmkhOtwhtzioBd7nkqBTk'
            +'BV3LZe8Z7Vyzue75zL6t4zf6fa3vxxGoBDhIZViFKFKoeNeYwfjIJylHyWPJ'
            +'hPmkechZEmkJ6hk2GiFaqnD6qIpq1ur6WhnL+kqLaIuKO6g7yuvnywmMJ4xJ'
            +'PGdMidxmkpaFxDClTMar1ZA1hr0kTcecDUu0Exe0nacDy/D8ER17vgidugK+'
            +'zq7OHB5jXf1Onkpf311HXz1+1+gBs7ZAzcB57Aj+IPUFoUNC6CbCgKMGYa3+'
            +'cBjhBOtisUkzf2FCXjT5C+UTlSl7sQykMRQxhf8+RSxmrFrOKi9VXCwI7gbH'
            +'h/iCGgX56SAae3+AEg36FN0+qQt10BIHj1XMIk6xJZH3D+zXd1Yhab2ybaRR'
            +'sFXjVZR4JJOjCVtf6IQ2NuzUrt7KlrwUkB/NoXD35hM7tOZKvjy21v0D6NRI'
            +'xZBBKovzmCTPojeJao6WeFzmz6InjiYtmtBp1Jtb9/y8eoZA1nmkxaYt5LbZ'
            +'frhrx+29R7eNPq9JCzcVGTgdXLGLG7/qXHlCVcel+/Y5vGBRjWyR7n6OAtTs'
            +'b9otfwdPV9R4sgux3sN7NzHWjX8htQPSfW/UgYRL888KPAllP3jgX14GRpFP'
            +'O/85405YCZpRIIEQIsjRfAtStYgeAuUX34TwCajZYUkhJ6FizRgIgYggNlTd'
            +'EMR1Ux5q0Q2BoXUbTVQAADs=')

        self.Label_photo = Label(vcarve_settings,image=self.PHOTO)
        self.Label_photo.place(x=w_label+150, y=40)
        self.Entry_B_Carve_Check()

        ## Buttons ##

        Ybut=int(vcarve_settings.winfo_height())-30
        Xbut=int(vcarve_settings.winfo_width()/2)

        self.VCARVE_Recalculate = Button(vcarve_settings,text="Calculate V-Carve", command=self.VCARVE_Recalculate_Click)
        self.VCARVE_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")


        if self.cut_type.get() == "v-carve":
            self.VCARVE_Recalculate.configure(state="normal", command=None)
        else:
            self.VCARVE_Recalculate.configure(state="disabled", command=None)

        self.VCARVE_Close = Button(vcarve_settings,text="Close",command=vcarve_settings.destroy)
        self.VCARVE_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")

