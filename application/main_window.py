from util import *
from tooltip import ToolTip
from settings import CUT_TYPE_VCARVE, CUT_TYPE_ENGRAVE

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
else:
    from Tkinter import *
    from tkFileDialog import *


class MainWindowTextLeft(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        self.h = 490
        # Frame.__init__(self, parent)
        Frame.__init__(self, parent, width=self.w, height=self.h)

        self.settings = settings

        # GUI callbacks
        self.entry_set = gui.entry_set
        self.Recalculate_Click = gui.Recalculate_Click
        self.Recalculate_RQD_Click = gui.Recalculate_RQD_Click
        self.recalculate_RQD_Nocalc = gui.recalculate_RQD_Nocalc
        self.V_Carve_Calc_Click = gui.V_Carve_Calc_Click
        self.Recalc_RQD = gui.Recalc_RQD
        self.menu_View_Refresh = gui.menu_View_Refresh
        self.do_it = gui.do_it

        # Variables
        self.flip = BooleanVar()
        self.mirror = BooleanVar()
        self.outer = BooleanVar()
        self.upper = BooleanVar()

        self.fontdex = BooleanVar()
        self.v_pplot = BooleanVar()

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
        self.cut_type = StringVar()  # not used for display

        self.initialise_variables()
        self.create_widgets()
        # self.bind_keys()
        self.master_configure()

    def width(self):
        return self.w

    def height(self):
        return self.h

    def create_widgets(self):

        self.create_widget_text_font_properties()
        self.create_widget_text_position()
        self.create_widget_text_on_circle()

        self.separator1 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(master=self, height=2, bd=1, relief=SUNKEN)

        # Buttons
        self.Recalculate = Button(self, text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

        # cut_type is traced only (to adjust widgets that depend on it)
        self.cut_type.trace_variable("w", self.Entry_cut_type_Callback)

    def create_widget_text_font_properties(self):
        self.Label_font_prop = Label(self, text="Text Font Properties:", anchor=W)

        self.Label_Yscale = Label(self, text="Text Height", anchor=CENTER)
        self.Label_Yscale_u = Label(self, textvariable=self.units, anchor=W)
        self.Label_Yscale_pct = Label(self, text="%", anchor=W)
        self.Entry_Yscale = Entry(self, width="15")
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)
        self.Label_Yscale_ToolTip = ToolTip(self.Label_Yscale,
                                            text='Character height of a single line of text.')

        self.NORmalColor = self.Entry_Yscale.cget('bg')

        self.Label_Sthick = Label(self, text="Line Thickness")
        self.Label_Sthick_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self, width="15")
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick,
                                            text='Thickness or width of engraved lines. \
                                            Set this to your engraving cutter diameter. \
                                            This setting only affects the displayed lines not the g-code output.')

        self.Label_Xscale = Label(self, text="Text Width", anchor=CENTER)
        self.Label_Xscale_u = Label(self, text="%", anchor=W)
        self.Entry_Xscale = Entry(self, width="15")
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale,
                                            text='Scaling factor for the width of characters.')

        self.Label_Cspace = Label(self, text="Char Spacing", anchor=CENTER)
        self.Label_Cspace_u = Label(self, text="%", anchor=W)
        self.Entry_Cspace = Entry(self, width="15")
        self.Entry_Cspace.configure(textvariable=self.CSPACE)
        self.Entry_Cspace.bind('<Return>', self.Recalculate_Click)
        self.CSPACE.trace_variable("w", self.Entry_Cspace_Callback)
        self.Label_Cspace_ToolTip = ToolTip(self.Label_Cspace,
                                            text='Character spacing as a percent of character width.')

        self.Label_Wspace = Label(self, text="Word Spacing", anchor=CENTER)
        self.Label_Wspace_u = Label(self, text="%", anchor=W)
        self.Entry_Wspace = Entry(self, width="15")
        self.Entry_Wspace.configure(textvariable=self.WSPACE)
        self.Entry_Wspace.bind('<Return>', self.Recalculate_Click)
        self.WSPACE.trace_variable("w", self.Entry_Wspace_Callback)
        self.Label_Wspace_ToolTip = ToolTip(self.Label_Wspace,
                                            text='Width of the space character. \
                                            This is determined as a percentage of the maximum width of the characters in the currently selected font.')

        self.Label_Lspace = Label(self, text="Line Spacing", anchor=CENTER)
        self.Entry_Lspace = Entry(self, width="15")
        self.Entry_Lspace.configure(textvariable=self.LSPACE)
        self.Entry_Lspace.bind('<Return>', self.Recalculate_Click)
        self.LSPACE.trace_variable("w", self.Entry_Lspace_Callback)
        self.Label_Lspace_ToolTip = ToolTip(self.Label_Lspace,
                                            text='The vertical spacing between lines of text. This is a multiple of the text height previously input. \
                                            A vertical spacing of 1.0 could result in consecutive lines of text touching each other if the maximum  \
                                            height character is directly below a character that extends the lowest (like a "g").')

    def create_widget_text_position(self):
        self.Label_pos_orient = Label(self, text="Text Position and Orientation:", anchor=W)

        self.Label_Tangle = Label(self, text="Text Angle", anchor=CENTER)
        self.Label_Tangle_u = Label(self, text="deg", anchor=W)
        self.Entry_Tangle = Entry(self, width="15")
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle, text='Rotation of the text from horizontal.')

        self.Label_Justify = Label(self, text="Justify", anchor=CENTER)
        self.Justify_OptionMenu = OptionMenu(self, self.justify, "Left", "Center",
                                             "Right", command=self.Recalculate_RQD_Click)
        self.Label_Justify_ToolTip = ToolTip(self.Label_Justify,
                                             text='Justify determins how to align multiple lines of text. Left side, Right side or Centered.')
        self.justify.trace_variable("w", self.Entry_justify_Callback)

        self.Label_Origin = Label(self, text="Origin", anchor=CENTER)
        self.Origin_OptionMenu = OptionMenu(self, self.origin, "Top-Left", "Top-Center", "Top-Right", "Mid-Left",
                                            "Mid-Center", "Mid-Right", "Bot-Left", "Bot-Center", "Bot-Right", "Default",
                                            command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin,
                                            text='Origin determins where the X and Y zero position is located relative to the engraving.')
        self.origin.trace_variable("w", self.Entry_origin_Callback)

        self.Label_flip = Label(self, text="Flip Text")
        self.Checkbutton_flip = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_flip_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip,
                                          text='Selecting Flip Text mirrors the text about a horizontal line.')

        self.Label_mirror = Label(self, text="Mirror Text")
        self.Checkbutton_mirror = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_mirror_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror,
                                            text='Selecting Mirror Text mirrors the text about a vertical line.')

    def create_widget_text_on_circle(self):
        self.Label_text_on_arc = Label(self, text="Text on Circle Properties:", anchor=W)

        self.Label_Tradius = Label(self, text="Circle Radius", anchor=CENTER)
        self.Label_Tradius_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Tradius = Entry(self, width="15")
        self.Entry_Tradius.configure(textvariable=self.TRADIUS)
        self.Entry_Tradius.bind('<Return>', self.Recalculate_Click)
        self.TRADIUS.trace_variable("w", self.Entry_Tradius_Callback)
        self.Label_Tradius_ToolTip = ToolTip(self.Label_Tradius,
                                             text='Circle radius is the radius of the circle that the text in the input box is placed on. \
                                             If the circle radius is set to 0.0 the text is not placed on a circle.')

        self.Label_outer = Label(self, text="Outside circle")
        self.Checkbutton_outer = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=self.outer)
        self.outer.trace_variable("w", self.Entry_outer_Callback)
        self.Label_outer_ToolTip = ToolTip(self.Label_outer,
                                           text='Select whether the text is placed so that is falls on the inside of \
                                           the circle radius or the outside of the circle radius.')

        self.Label_upper = Label(self, text="Top of Circle")
        self.Checkbutton_upper = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=self.upper)
        self.upper.trace_variable("w", self.Entry_upper_Callback)
        self.Label_upper_ToolTip = ToolTip(self.Label_upper,
                                           text='Select whether the text is placed on the top of the circle of on the bottom of the circle  \
                                           (i.e. concave down or concave up).')

    def set_cut_type(self):
        self.cut_type.set(self.settings.get('cut_type'))

    def master_configure(self):
        w_label = 90
        w_entry = 60
        w_units = 35

        x_label_L = 10
        x_entry_L = x_label_L + w_label + 10
        x_units_L = x_entry_L + w_entry + 5

        # cut_type may have been changed since the last configuration
        self.set_cut_type()

        # Text font properties

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

        # if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
        #     self.Entry_Sthick.configure(state="disabled")
        #     self.Label_Sthick.configure(state="disabled")
        #     self.Label_Sthick_u.configure(state="disabled")
        # else:
        #     self.Entry_Sthick.configure(state="normal")
        #     self.Label_Sthick.configure(state="normal")
        #     self.Label_Sthick_u.configure(state="normal")

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

        # Text position and orientation

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

        # Text on circle properties

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

        # Button
        Ybut = self.h - 20
        self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

    def configure_cut_type(self):
        if self.cut_type.get() == CUT_TYPE_VCARVE:
            self.Entry_Sthick.configure(state="disabled")
            self.Label_Sthick.configure(state="disabled")
            self.Label_Sthick_u.configure(state="disabled")
        else:
            self.Entry_Sthick.configure(state="normal")
            self.Label_Sthick.configure(state="normal")
            self.Label_Sthick_u.configure(state="normal")

    def initialise_variables(self):
        """
        Initialise the TK widgets with the values from settings
        """
        self.flip.set(self.settings.get('flip'))
        self.mirror.set(self.settings.get('mirror'))
        self.outer.set(self.settings.get('outer'))
        self.upper.set(self.settings.get('upper'))

        self.fontdex.set(self.settings.get('fontdex'))
        self.v_pplot.set(self.settings.get('v_pplot'))

        # self.useIMGsize.set(self.settings.get('useIMGsize'))
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

    def Check_All_Variables(self):

        error_cnt = \
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 2) + \
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 2) + \
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 2) + \
            self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), 2) + \
            self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), 2) + \
            self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), 2) + \
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 2) + \
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), 2)

        return error_cnt

    def Scale_Linear_Inputs(self, factor=1.0):
        # self.settings.set('yscale', self.settings.get('yscale') * factor)
        # self.settings.set('line_thickness', self.settings.get('line_thickness') * factor)
        # self.settings.set('text_radius', self.settings.get('text_radius') * factor)
        # self.settings.set('feedrate', self.settings.get('feedrate') * factor)
        # self.settings.set('plunge_rate', self.settings.get('plunge_rate') * factor)
        # self.settings.set('zsafe', self.settings.get('zsafe') * factor)
        # self.settings.set('zcut', self.settings.get('zcut') * factor)

        self.YSCALE.set('%.3g' % self.settings.get('yscale'))
        self.STHICK.set('%.3g' % self.settings.get('line_thickness'))
        self.TRADIUS.set('%.3g' % self.settings.get('text_radius'))

    # Text callbacks

    def Entry_units_var_Callback(self):
        self.units.set(self.settings.get('units'))
        self.Recalc_RQD()

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

    def Entry_justify_Callback(self, varName, index, mode):
        self.settings.set('justify', self.justify.get())
        self.Recalc_RQD()

    def Entry_origin_Callback(self, varName, index, mode):
        self.settings.set('origin', self.origin.get())
        self.Recalc_RQD()

    def Entry_flip_Callback(self, varName, index, mode):
        self.settings.set('flip', self.flip.get())
        self.Recalc_RQD()

    def Entry_mirror_Callback(self, varName, index, mode):
        self.settings.set('mirror', self.mirror.get())
        self.Recalc_RQD()

    def Entry_outer_Callback(self, varName, index, mode):
        self.settings.set('outer', self.outer.get())
        self.Recalc_RQD()

    def Entry_upper_Callback(self, varName, index, mode):
        self.settings.set('upper', self.upper.get())
        self.Recalc_RQD()

    # G-Code callback

    def Entry_cut_type_Callback(self, varName, index, mode):
        self.configure_cut_type()


class MainWindowTextRight(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        self.h = 490
        Frame.__init__(self, parent, width=self.w, height=self.h)

        self.settings = settings

        # GUI callbacks
        self.entry_set = gui.entry_set
        self.Recalculate_Click = gui.Recalculate_Click
        self.Recalculate_RQD_Click = gui.Recalculate_RQD_Click
        self.recalculate_RQD_Nocalc = gui.recalculate_RQD_Nocalc
        self.V_Carve_Calc_Click = gui.V_Carve_Calc_Click
        self.Recalc_RQD = gui.Recalc_RQD
        self.menu_View_Refresh = gui.menu_View_Refresh
        self.readFontFile = gui.readFontFile
        self.do_it = gui.do_it

        self.Ctrl_set_menu_cut_type = gui.Ctrl_set_menu_cut_type

        # Variables
        self.fontdex = BooleanVar()
        self.v_pplot = BooleanVar()

        self.useIMGsize = BooleanVar()
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

        self.funits = StringVar()
        self.FEED = StringVar()
        self.PLUNGE = StringVar()
        self.fontfile = StringVar()
        self.H_CALC = StringVar()
        self.fontdir = StringVar()
        self.cut_type = StringVar()
        self.input_type = StringVar()

        self.current_input_file = StringVar()
        self.bounding_box = StringVar()

        self.initialise_variables()
        self.create_widgets()
        self.bind_keys()
        self.master_configure()

    def width(self):
        return self.w

    def height(self):
        return self.h

    def create_widgets(self):
        self.create_widgets_gcode_properties()
        self.create_widgets_font()

    def create_widgets_gcode_properties(self):
        self.Label_gcode_opt = Label(self, text="Gcode Properties:", anchor=W)

        self.Label_Feed = Label(self, text="Feed Rate")
        self.Label_Feed_u = Label(self, textvariable=self.funits, anchor=W)
        self.Entry_Feed = Entry(self, width="15")
        self.Entry_Feed.configure(textvariable=self.FEED)
        self.Entry_Feed.bind('<Return>', self.Recalculate_Click)
        self.FEED.trace_variable("w", self.Entry_Feed_Callback)
        self.Label_Feed_ToolTip = ToolTip(self.Label_Feed,
                                          text='Specify the tool feed rate that is output in the g-code output file.')

        self.Label_Plunge = Label(self, text="Plunge Rate")
        self.Label_Plunge_u = Label(self, textvariable=self.funits, anchor=W)
        self.Entry_Plunge = Entry(self, width="15")
        self.Entry_Plunge.configure(textvariable=self.PLUNGE)
        self.Entry_Plunge.bind('<Return>', self.Recalculate_Click)
        self.PLUNGE.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(self.Label_Plunge,
                                            text='Plunge Rate sets the feed rate for vertical moves into the material being cut.\n\n \
                                            When Plunge Rate is set to zero plunge feeds are equal to Feed Rate.')

        self.Label_Zsafe = Label(self, text="Z Safe")
        self.Label_Zsafe_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self, width="15")
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(self.Label_Zsafe,
                                           text='Z location that the tool will be sent to prior to any rapid moves.')

        self.Label_Zcut = Label(self, text="Engrave Depth")
        self.Label_Zcut_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self, width="15")
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(self.Label_Zcut,
                                          text='Depth of the engraving cut. This setting has no effect when the v-carve option is selected.')

    def create_widgets_font(self):
        self.Checkbutton_fontdex = Checkbutton(self, text="Show All Font Characters", anchor=W)
        self.fontdex.trace_variable("w", self.Entry_fontdex_Callback)
        self.Checkbutton_fontdex.configure(variable=self.fontdex)
        self.Label_fontfile = Label(self, textvariable=self.current_input_file, anchor=W, foreground='grey50')

        self.Label_List_Box = Label(self, text="Font Files:", foreground="#101010", anchor=W)

        self.Listbox_1_frame = Frame(self)
        scrollbar = Scrollbar(self.Listbox_1_frame, orient=VERTICAL)

        self.Listbox_1 = Listbox(self.Listbox_1_frame, selectmode="single", yscrollcommand=scrollbar.set)
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

        # Buttons
        self.V_Carve_Calc = Button(self, text="Calc V-Carve", command=self.V_Carve_Calc_Click)

        self.Radio_Cut_E = Radiobutton(self, text="Engrave", value="engrave", anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type)
        self.Radio_Cut_V = Radiobutton(self, text="V-Carve", value="v-carve", anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type)

        self.cut_type.trace_variable("w", self.Entry_cut_type_Callback)

    def set_cut_type(self):
        # only when changed (to avoid recursion due to trace_variable callback)
        if self.cut_type.get() != self.settings.get('cut_type'):
            self.cut_type.set(self.settings.get('cut_type'))

    def master_configure(self):
        # configure right column
        w_label = 90
        w_entry = 60
        w_units = 35

        x_label_R = 10
        x_entry_R = x_label_R + w_label + 10
        x_units_R = x_entry_R + w_entry + 5

        # cut_type may have been changed since the last configuration
        self.set_cut_type()

        # G-Code properties

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

        # Font file

        Yloc = Yloc + 24 + 6
        self.Label_List_Box.place(x=x_label_R + 0, y=Yloc, width=113, height=22)

        # get the height of the grid this widget is in
        # h = self.winfo_height()
        h = self.master.winfo_height()

        Yloc = Yloc + 24
        self.Listbox_1_frame.place(x=x_label_R + 0, y=Yloc, width=160 + 25, height=h - 324)
        self.Label_fontfile.place(x=x_label_R, y=h - 165, width=w_label + 75, height=21)
        self.Checkbutton_fontdex.place(x=x_label_R, y=h - 145, width=185, height=23)

        # Buttons

        Ybut = h - 60
        self.V_Carve_Calc.place(x=x_label_R, y=Ybut, width=100, height=30)
        Ybut = h - 105
        self.Radio_Cut_E.place(x=x_label_R, y=Ybut, width=185, height=23)
        Ybut = h - 85
        self.Radio_Cut_V.place(x=x_label_R, y=Ybut, width=185, height=23)

        self.configure_cut_type()

    def configure_cut_type(self):
        if self.cut_type.get() == CUT_TYPE_VCARVE:
            self.V_Carve_Calc.configure(state="normal", command=None)

            self.Entry_Zcut.configure(state="disabled")
            self.Label_Zcut.configure(state="disabled")
            self.Label_Zcut_u.configure(state="disabled")
        else:
            self.V_Carve_Calc.configure(state="disabled", command=None)

            self.Entry_Zcut.configure(state="normal")
            self.Label_Zcut.configure(state="normal")
            self.Label_Zcut_u.configure(state="normal")

    def initialise_variables(self):
        """
        Initialise the TK widgets with the values from settings
        """
        self.fontdex.set(self.settings.get('fontdex'))
        self.v_pplot.set(self.settings.get('v_pplot'))

        self.ZSAFE.set(self.settings.get('zsafe'))
        self.ZCUT.set(self.settings.get('zcut'))
        self.STHICK.set(self.settings.get('line_thickness'))
        self.origin.set(self.settings.get('origin'))

        self.units.set(self.settings.get('units'))
        self.funits.set(self.settings.get('feed_units'))
        self.FEED.set(self.settings.get('feedrate'))
        self.PLUNGE.set(self.settings.get('plunge_rate'))

        self.fontfile.set(self.settings.get('fontfile'))
        self.H_CALC.set(self.settings.get('height_calculation'))
        self.fontdir.set(self.settings.get('fontdir'))

        self.cut_type.set(self.settings.get('cut_type'))
        self.input_type.set(self.settings.get('input_type'))

        self.HOME_DIR = (self.settings.get('HOME_DIR'))
        self.NGC_FILE = (self.settings.get('NGC_FILE'))
        self.IMAGE_FILE = (self.settings.get('IMAGE_FILE'))

    def bind_keys(self):
        self.bind('<Control-Up>', self.Listbox_Key_Up)
        self.bind('<Control-Down>', self.Listbox_Key_Down)

    def Check_All_Variables(self):

        error_cnt = self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 2) + \
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 2) + \
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 2) + \
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 2)

        return error_cnt

    def Scale_Linear_Inputs(self, factor=1.0):
        # self.settings.set('feedrate', self.settings.get('feedrate') * factor)
        # self.settings.set('plunge_rate', self.settings.get('plunge_rate') * factor)
        # self.settings.set('zsafe', self.settings.get('zsafe') * factor)
        # self.settings.set('zcut', self.settings.get('zcut') * factor)

        self.FEED.set('%.3g' % self.settings.get('feedrate'))
        self.PLUNGE.set('%.3g' % self.settings.get('plunge_rate'))
        self.ZSAFE.set('%.3g' % self.settings.get('zsafe'))
        self.ZCUT.set('%.3g' % self.settings.get('zcut'))

    # G-Code properties callbacks

    def Entry_units_var_Callback(self):
        self.units.set(self.settings.get('units'))
        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.funits.set('mm/min')
        self.settings.set('feed_units', self.funits.get())
        self.Recalc_RQD()

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

    def Entry_cut_type_Callback(self, varName, index, mode):
        self.settings.set('cut_type', self.cut_type.get())
        self.configure_cut_type()
        self.Ctrl_set_menu_cut_type()
        self.Recalc_RQD()

    # Font properties callbacks

    def Entry_fontdex_Callback(self, varName, index, mode):
        self.settings.set('fontdex', self.fontdex.get())
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

    def Entry_fontdir_Callback(self, varName, index, mode):
        self.Listbox_1.delete(0, END)
        self.Listbox_1.configure(bg=self.NORmalColor)
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
        # self.font = readFontFile(self.settings)
        self.readFontFile()
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
        # self.font = readFontFile(self.settings)
        self.readFontFile()
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
        # self.font = readFontFile(self.settings)
        self.readFontFile()
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
        # self.font = readFontFile(self.settings)
        self.readFontFile()
        self.do_it()


class MainWindowImageLeft(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        self.h = 540
        Frame.__init__(self, parent, width=self.w, height=self.h)

        self.settings = settings

        # GUI callbacks
        self.entry_set = gui.entry_set
        self.Recalculate_Click = gui.Recalculate_Click
        self.Recalculate_RQD_Click = gui.Recalculate_RQD_Click
        self.V_Carve_Calc_Click = gui.V_Carve_Calc_Click
        self.Recalc_RQD = gui.Recalc_RQD
        self.menu_View_Refresh = gui.menu_View_Refresh
        self.Ctrl_set_menu_cut_type = gui.Ctrl_set_menu_cut_type

        # Variables
        self.flip = BooleanVar()
        self.mirror = BooleanVar()
        self.outer = BooleanVar()
        self.upper = BooleanVar()

        self.fontdex = BooleanVar()
        self.v_pplot = BooleanVar()

        self.useIMGsize = BooleanVar()
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

        self.funits = StringVar()
        self.FEED = StringVar()
        self.PLUNGE = StringVar()
        self.fontfile = StringVar()
        self.H_CALC = StringVar()
        self.fontdir = StringVar()
        self.cut_type = StringVar()
        self.input_type = StringVar()

        self.initialise_variables()
        self.create_widgets()
        self.master_configure()

    def width(self):
        return self.w

    def height(self):
        return self.h

    def create_widgets(self):
        self.create_widgets_image_properties()
        self.create_widgets_image_position()
        self.create_widgets_gcode_properties()

        self.separator1 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(master=self, height=2, bd=1, relief=SUNKEN)

        # Buttons
        self.Recalculate = Button(self, text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

        self.V_Carve_Calc = Button(self.master, text="Calc V-Carve", command=self.V_Carve_Calc_Click)
        self.Radio_Cut_E = Radiobutton(self.master, text="Engrave", value="engrave", anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type)
        self.Radio_Cut_V = Radiobutton(self.master, text="V-Carve", value="v-carve", anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type)
        self.cut_type.trace_variable("w", self.Entry_cut_type_Callback)

    def create_widgets_image_properties(self):
        self.Label_image_prop = Label(self, text="Image Properties:", anchor=W)

        self.Label_useIMGsize = Label(self, text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command=self.useIMGsize_var_Callback)

        self.Label_Yscale = Label(self, text="Image Height", anchor=CENTER)
        self.Label_Yscale_u = Label(self, textvariable=self.units, anchor=W)
        self.Label_Yscale_pct = Label(self, text="%", anchor=W)
        self.Entry_Yscale = Entry(self, width="15")
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)

        self.NORmalColor = self.Entry_Yscale.cget('bg')

        self.Label_Sthick = Label(self, text="Line Thickness")
        self.Label_Sthick_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self, width="15")
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick,
                                            text='Thickness or width of engraved lines. \
                                            Set this to your engraving cutter diameter. \
                                            This setting only affects the displayed lines not the g-code output.')

        self.Label_Xscale = Label(self, text="Image Width", anchor=CENTER)
        self.Label_Xscale_u = Label(self, text="%", anchor=W)
        self.Entry_Xscale = Entry(self, width="15")
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale,
                                            text='Scaling factor for the image width.')

        self.Label_useIMGsize = Label(self, text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command=self.useIMGsize_var_Callback)

    def create_widgets_image_position(self):
        self.Label_pos_orient = Label(self, text="Image Position and Orientation:", anchor=W)

        self.Label_Tangle = Label(self, text="Image Angle", anchor=CENTER)
        self.Label_Tangle_u = Label(self, text="deg", anchor=W)
        self.Entry_Tangle = Entry(self, width="15")
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle,
                                            text='Rotation of the image from horizontal.')

        self.Label_Origin = Label(self, text="Origin", anchor=CENTER)
        self.Origin_OptionMenu = OptionMenu(self, self.origin, "Top-Left", "Top-Center", "Top-Right", "Mid-Left",
                                            "Mid-Center", "Mid-Right", "Bot-Left", "Bot-Center", "Bot-Right", "Default",
                                            command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin,
                                            text='Origin determins where the X and Y zero position is located relative to the engraving.')
        self.origin.trace_variable("w", self.Entry_origin_Callback)

        self.Label_flip = Label(self, text="Flip Image")
        self.Checkbutton_flip = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_flip_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip,
                                          text='Selecting Flip Image mirrors the design about a horizontal line.')

        self.Label_mirror = Label(self, text="Mirror Image")
        self.Checkbutton_mirror = Checkbutton(self, text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_mirror_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror,
                                            text='Selecting Mirror Image mirrors the design about a vertical line.')

    def create_widgets_gcode_properties(self):
        self.Label_gcode_opt = Label(self, text="Gcode Properties:", anchor=W)

        # TODO current file property
        # the current font file
        current_input_file = self.settings.get('fontfile')
        self.Label_fontfile = Label(self.master, textvariable=current_input_file, anchor=W,
                                    foreground='grey50')

        self.Label_Feed = Label(self, text="Feed Rate")
        self.Label_Feed_u = Label(self, textvariable=self.funits, anchor=W)
        self.Entry_Feed = Entry(self, width="15")
        self.Entry_Feed.configure(textvariable=self.FEED)
        self.Entry_Feed.bind('<Return>', self.Recalculate_Click)
        self.FEED.trace_variable("w", self.Entry_Feed_Callback)
        self.Label_Feed_ToolTip = ToolTip(self.Label_Feed,
                                          text='Specify the tool feed rate that is output in the g-code output file.')

        self.Label_Plunge = Label(self, text="Plunge Rate")
        self.Label_Plunge_u = Label(self, textvariable=self.funits, anchor=W)
        self.Entry_Plunge = Entry(self, width="15")
        self.Entry_Plunge.configure(textvariable=self.PLUNGE)
        self.Entry_Plunge.bind('<Return>', self.Recalculate_Click)
        self.PLUNGE.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(self.Label_Plunge,
                                            text='Plunge Rate sets the feed rate for vertical moves into the material being cut.\n\n \
                                            When Plunge Rate is set to zero plunge feeds are equal to Feed Rate.')

        self.Label_Zsafe = Label(self, text="Z Safe")
        self.Label_Zsafe_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self, width="15")
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(self.Label_Zsafe,
                                           text='Z location that the tool will be sent to prior to any rapid moves.')

        self.Label_Zcut = Label(self, text="Engrave Depth")
        self.Label_Zcut_u = Label(self, textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self, width="15")
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(self.Label_Zcut,
                                          text='Depth of the engraving cut. This setting has no effect when the v-carve option is selected.')

    def initialise_variables(self):
        """
        Initialise the TK widgets with the values from settings
        """
        self.flip.set(self.settings.get('flip'))
        self.mirror.set(self.settings.get('mirror'))
        self.outer.set(self.settings.get('outer'))
        self.upper.set(self.settings.get('upper'))

        self.fontdex.set(self.settings.get('fontdex'))
        self.v_pplot.set(self.settings.get('v_pplot'))

        # self.useIMGsize.set(self.settings.get('useIMGsize'))
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
        self.fontdir.set(self.settings.get('fontdir'))
        self.cut_type.set(self.settings.get('cut_type'))
        self.input_type.set(self.settings.get('input_type'))

        self.default_text = self.settings.get('default_text')

        self.HOME_DIR = (self.settings.get('HOME_DIR'))
        self.NGC_FILE = (self.settings.get('NGC_FILE'))
        self.IMAGE_FILE = (self.settings.get('IMAGE_FILE'))

    def set_cut_type(self):
        # only when changed (to avoid recursion due to trace_variable callback)
        if self.cut_type.get() != self.settings.get('cut_type'):
            self.cut_type.set(self.settings.get('cut_type'))

    def master_configure(self):
        w_label = 90
        w_entry = 60
        w_units = 35

        x_label_L = 10
        x_entry_L = x_label_L + w_label + 10
        x_units_L = x_entry_L + w_entry + 5

        # cut_type may have been changed since the last configuration
        self.set_cut_type()

        # Image properties

        Yloc = 6
        self.Label_image_prop.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        if self.settings.get('useIMGsize'):
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

        Yloc = Yloc + 24
        self.Label_Xscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Xscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Xscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24 + 12
        self.separator1.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)
        Yloc = Yloc + 6
        self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)

        # Image position and orientation

        Yloc = Yloc + 24
        self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24
        self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        Yloc = Yloc + 24
        self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry + 40, height=23)

        # G-Code properties

        Yloc = Yloc + 24 + 12
        # self.separator2.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)

        Yloc = Yloc + 6
        self.Label_gcode_opt.place(x=x_label_L, y=Yloc, width=w_label * 2, height=21)

        Yloc = Yloc + 24
        self.Entry_Feed.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)
        self.Label_Feed.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Feed_u.place(x=x_units_L, y=Yloc, width=w_units + 15, height=21)

        Yloc = Yloc + 24
        self.Entry_Plunge.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)
        self.Label_Plunge.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Plunge_u.place(x=x_units_L, y=Yloc, width=w_units + 15, height=21)

        Yloc = Yloc + 24
        self.Entry_Zsafe.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)
        self.Label_Zsafe.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Zsafe_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)

        Yloc = Yloc + 24
        self.Label_Zcut.place(x=x_label_L, y=Yloc, width=w_label, height=21)
        self.Label_Zcut_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
        self.Entry_Zcut.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

        Yloc = Yloc + 24 + 12
        self.separator3.place(x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2)
        Yloc = Yloc + 6
        self.Label_fontfile.place(x=x_label_L, y=Yloc, width=w_label + 75, height=21)

        self.configure_cut_type()

        # Buttons

        x_offset = 100

        Ybut = self.h - 60
        self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

        Ybut = self.h - 60
        self.V_Carve_Calc.place(x=x_label_L + x_offset, y=Ybut, width=100, height=30)

        Ybut = self.h - 105
        self.Radio_Cut_E.place(x=x_label_L + x_offset, y=Ybut, width=w_label, height=23)

        Ybut = self.h - 85
        self.Radio_Cut_V.place(x=x_label_L + x_offset, y=Ybut, width=w_label, height=23)

    def configure_cut_type(self):
        if self.cut_type.get() == CUT_TYPE_VCARVE:
            self.V_Carve_Calc.configure(state="normal", command=None)

            self.Entry_Sthick.configure(state="disabled")
            self.Label_Sthick.configure(state="disabled")
            self.Label_Sthick_u.configure(state="disabled")

            self.Entry_Zcut.configure(state="disabled")
            self.Label_Zcut.configure(state="disabled")
            self.Label_Zcut_u.configure(state="disabled")
        else:
            self.V_Carve_Calc.configure(state="disabled", command=None)

            self.Entry_Sthick.configure(state="normal")
            self.Label_Sthick.configure(state="normal")
            self.Label_Sthick_u.configure(state="normal")

            self.Entry_Zcut.configure(state="normal")
            self.Label_Zcut.configure(state="normal")
            self.Label_Zcut_u.configure(state="normal")

    def Check_All_Variables(self):
        error_cnt = \
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 2) + \
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 2) + \
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 2) + \
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 2) + \
            self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 2) + \
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 2) + \
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 2) + \
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 2)
        return error_cnt

    def Scale_Linear_Inputs(self, factor=1.0):
        # self.settings.set('yscale', self.settings.get('yscale') * factor)
        # self.settings.set('line_thickness', self.settings.get('line_thickness') * factor)
        # self.settings.set('feedrate', self.settings.get('feedrate') * factor)
        # self.settings.set('plunge_rate', self.settings.get('plunge_rate') * factor)
        # self.settings.set('zsafe', self.settings.get('zsafe') * factor)
        # self.settings.set('zcut', self.settings.get('zcut') * factor)

        self.YSCALE.set('%.3g' % self.settings.get('yscale'))
        self.STHICK.set('%.3g' % self.settings.get('line_thickness'))
        self.FEED.set('%.3g' % self.settings.get('feedrate'))
        self.PLUNGE.set('%.3g' % self.settings.get('plunge_rate'))
        self.ZSAFE.set('%.3g' % self.settings.get('zsafe'))
        self.ZCUT.set('%.3g' % self.settings.get('zcut'))

    # Image properties callbacks

    def Entry_units_var_Callback(self):
        self.units.set(self.settings.get('units'))
        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.funits.set('mm/min')
        self.settings.set('feed_units', self.funits.get())
        self.Recalc_RQD()

    def useIMGsize_var_Callback(self):

        if self.settings.get('input_type') == "image":
            try:
                image_height = self.image.get_height()
            except:
                if self.settings.get('units') == 'in':
                    image_height = 2
                else:
                    image_height = 50

        self.settings.set('useIMGsize', self.useIMGsize.get())
        if self.useIMGsize.get():
            self.YSCALE.set('%.3g' % (100 * float(self.YSCALE.get()) / image_height))
        else:
            self.YSCALE.set('%.3g' % ((float(self.YSCALE.get()) / 100) * image_height))

        self.settings.set('yscale', self.YSCALE.get())

        self.menu_View_Refresh()
        self.Recalc_RQD()

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

    def Entry_origin_Callback(self, varName, index, mode):
        self.settings.set('origin', self.origin.get())
        self.Recalc_RQD()

    def Entry_flip_Callback(self, varName, index, mode):
        self.settings.set('flip', self.flip.get())
        self.Recalc_RQD()

    def Entry_mirror_Callback(self, varName, index, mode):
        self.settings.set('mirror', self.mirror.get())
        self.Recalc_RQD()

    # G-Code properties callbacks

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

    def Entry_cut_type_Callback(self, varName, index, mode):
        self.settings.set('cut_type', self.cut_type.get())
        self.configure_cut_type()
        self.Ctrl_set_menu_cut_type()
        self.Recalc_RQD()
