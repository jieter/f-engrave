from util import *
from tooltip import ToolTip
from settings import CUT_TYPE_VCARVE, CUT_TYPE_ENGRAVE

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
else:
    from Tkinter import *
    from tkFileDialog import *


class MainWindowWidget(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        # self.h = 100
        # Frame.__init__(self, parent, width=self.w, height=self.h)
        Frame.__init__(self, parent, width=self.w)

        # default widget widths
        self.w_label = 12
        self.w_entry = 5
        self.w_units = 5

        self.settings = settings

        self.units = StringVar()
        self.cut_type = StringVar()

        # Gui callbacks
        self.entry_set = gui.entry_set
        self.Recalculate_RQD_Click = gui.Recalculate_RQD_Click
        self.recalculate_RQD_Nocalc = gui.recalculate_RQD_Nocalc
        self.V_Carve_Calc_Click = gui.V_Carve_Calc_Click
        self.Recalc_RQD = gui.Recalc_RQD
        self.menu_View_Refresh = gui.menu_View_Refresh
        self.statusMessage = gui.statusMessage
        self.do_it = gui.do_it

        self.Recalculate_Click = gui.Recalculate_Click

        self._initialise_variables()

    def _initialise_variables(self):
        self.units.set(self.settings.get('units'))
        self.cut_type.set(self.settings.get('cut_type'))

    def set_units(self, units):
        if self.units != units:
            self.units = units
            self.configure_units()

    def set_cut_type(self, cut_type):
        if self.cut_type != cut_type:
            self.cut_type = cut_type
            self.configure_cut_type()

    # Virtual methods
    def configure_units(self):
        pass

    def configure_cut_type(self):
        pass

    def scale_linear_inputs(self, factor=1.0):
        pass


class TextFontProperties(MainWindowWidget):

    def __init__(self, parent, gui, settings):
        MainWindowWidget.__init__(self, parent, gui, settings)

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

        self.initialise_variables()
        self.create_widgets()
        self.configure()

    def create_widgets(self):
        self.Label_font_prop = Label(self, text="Text Font Properties:")

        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.yscale_frame = Frame(self)
        self.Label_Yscale = Label(self.yscale_frame, text="Text Height", width=w_label, anchor=E)
        self.Label_Yscale_u = Label(self.yscale_frame, textvariable=self.units, anchor=W)
        self.Label_Yscale_pct = Label(self.yscale_frame, text="%")
        self.Entry_Yscale = Entry(self.yscale_frame, width=w_entry)
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)
        self.Label_Yscale_ToolTip = ToolTip(self.Label_Yscale,
                                            text='Character height of a single line of text.')

        self.sthick_frame = Frame(self)
        self.Label_Sthick = Label(self.sthick_frame, text="Line Thickness", width=w_label, anchor=E)
        self.Label_Sthick_u = Label(self.sthick_frame, textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self.sthick_frame, width=w_entry)
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick,
                                            text='Thickness or width of engraved lines. \
                                            Set this to your engraving cutter diameter. \
                                            This setting only affects the displayed lines not the g-code output.')

        self.xscale_frame = Frame(self)
        self.Label_Xscale = Label(self.xscale_frame, text="Text Width", width=w_label, anchor=E)
        self.Label_Xscale_u = Label(self.xscale_frame, text="%", anchor=W)
        self.Entry_Xscale = Entry(self.xscale_frame, width=w_entry)
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale,
                                            text='Scaling factor for the width of characters.')

        self.cspace_frame = Frame(self)
        self.Label_Cspace = Label(self.cspace_frame, text="Char Spacing", width=w_label, anchor=E)
        self.Label_Cspace_u = Label(self.cspace_frame, text="%", anchor=W)
        self.Entry_Cspace = Entry(self.cspace_frame, width=w_entry)
        self.Entry_Cspace.configure(textvariable=self.CSPACE)
        self.Entry_Cspace.bind('<Return>', self.Recalculate_Click)
        self.CSPACE.trace_variable("w", self.Entry_Cspace_Callback)
        self.Label_Cspace_ToolTip = ToolTip(self.Label_Cspace,
                                            text='Character spacing as a percent of character width.')

        self.wspace_frame = Frame(self)
        self.Label_Wspace = Label(self.wspace_frame, text="Word Spacing", width=w_label, anchor=E)
        self.Label_Wspace_u = Label(self.wspace_frame, text="%", anchor=W)
        self.Entry_Wspace = Entry(self.wspace_frame, width=w_entry)
        self.Entry_Wspace.configure(textvariable=self.WSPACE)
        self.Entry_Wspace.bind('<Return>', self.Recalculate_Click)
        self.WSPACE.trace_variable("w", self.Entry_Wspace_Callback)
        self.Label_Wspace_ToolTip = ToolTip(self.Label_Wspace,
                                            text='Width of the space character. \
                                            This is determined as a percentage of the maximum width of the characters in the currently selected font.')

        self.lspace_frame = Frame(self)
        self.Label_Lspace = Label(self.lspace_frame, text="Line Spacing", width=w_label, anchor=E)
        self.Entry_Lspace = Entry(self.lspace_frame, width=w_entry)
        self.Entry_Lspace.configure(textvariable=self.LSPACE)
        self.Entry_Lspace.bind('<Return>', self.Recalculate_Click)
        self.LSPACE.trace_variable("w", self.Entry_Lspace_Callback)
        self.Label_Lspace_ToolTip = ToolTip(self.Label_Lspace,
                                            text='The vertical spacing between lines of text. This is a multiple of the text height previously input. \
                                            A vertical spacing of 1.0 could result in consecutive lines of text touching each other if the maximum  \
                                            height character is directly below a character that extends the lowest (like a "g").')

    def configure(self):

        # Text font properties

        self.Label_font_prop.pack(side=TOP, padx=10, anchor=W)

        self.Label_Yscale.pack(side=LEFT, anchor=W)
        self.Label_Yscale_pct.pack_forget()
        self.Label_Yscale_u.pack(side=RIGHT)
        self.Entry_Yscale.pack()
        self.yscale_frame.pack(anchor=W, padx=5)

        self.Label_Sthick.pack(side=LEFT, anchor=W)
        self.Label_Sthick_u.pack(side=RIGHT)
        self.Entry_Sthick.pack()
        self.sthick_frame.pack(anchor=W, padx=5)

        self.Label_Xscale.pack(side=LEFT, anchor=W)
        self.Label_Xscale_u.pack(side=RIGHT)
        self.Entry_Xscale.pack()
        self.xscale_frame.pack(anchor=W, padx=5)

        self.Label_Cspace.pack(side=LEFT, anchor=W)
        self.Label_Cspace_u.pack(side=RIGHT)
        self.Entry_Cspace.pack()
        self.cspace_frame.pack(anchor=W, padx=5)

        self.Label_Wspace.pack(side=LEFT, anchor=W)
        self.Label_Wspace_u.pack(side=RIGHT)
        self.Entry_Wspace.pack()
        self.wspace_frame.pack(anchor=W, padx=5)

        self.Label_Lspace.pack(side=LEFT, anchor=W)
        self.Entry_Lspace.pack()
        self.lspace_frame.pack(anchor=W, padx=5)

        self.configure_cut_type()
        self.configure_units()

    def configure_cut_type(self):
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.Entry_Sthick.configure(state="disabled")
            self.Label_Sthick.configure(state="disabled")
            self.Label_Sthick_u.configure(state="disabled")
        else:
            self.Entry_Sthick.configure(state="normal")
            self.Label_Sthick.configure(state="normal")
            self.Label_Sthick_u.configure(state="normal")

    def configure_units(self):
        self.units.set(self.settings.get('units'))

    def initialise_variables(self):
        self.YSCALE.set(self.settings.get('yscale'))
        self.XSCALE.set(self.settings.get('xscale'))
        self.STHICK.set(self.settings.get('line_thickness'))
        self.LSPACE.set(self.settings.get('line_space'))
        self.CSPACE.set(self.settings.get('char_space'))
        self.WSPACE.set(self.settings.get('word_space'))

    def check_all_variables(self, new):

        error_cnt = \
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), new) + \
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), new) + \
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), new) + \
            self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), new) + \
            self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), new) + \
            self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), new)

        return error_cnt

    def scale_linear_inputs(self):
        self.YSCALE.set('%.3g' % self.settings.get('yscale'))
        self.STHICK.set('%.3g' % self.settings.get('line_thickness'))
        self.TRADIUS.set('%.3g' % self.settings.get('text_radius'))

    # Text Font Properties callbacks

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


class TextPosition(MainWindowWidget):

    def __init__(self, parent, gui, settings):
        MainWindowWidget.__init__(self, parent, gui, settings)

        self.TANGLE = StringVar()
        self.justify = StringVar()
        self.origin = StringVar()
        self.flip = BooleanVar()
        self.mirror = BooleanVar()

        self.initialise_variables()
        self.create_widgets()
        self.configure()

    def create_widgets(self):

        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.Label_pos_orient = Label(self, text="Text Position and Orientation:")

        self.tangle_frame = Frame(self)
        self.Label_Tangle = Label(self.tangle_frame, text="Text Angle", width=w_label, anchor=E)
        self.Label_Tangle_u = Label(self.tangle_frame, text="deg")
        self.Entry_Tangle = Entry(self.tangle_frame, width=w_entry)
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle, text='Rotation of the text from horizontal.')

        self.justify_frame = Frame(self)
        self.Label_Justify = Label(self.justify_frame, text="Justify", width=w_label, anchor=E)
        self.Justify_OptionMenu = OptionMenu(self.justify_frame, self.justify, "Left", "Center",
                                             "Right", command=self.Recalculate_RQD_Click)
        self.Label_Justify_ToolTip = ToolTip(self.Label_Justify,
                                             text='Justify determins how to align multiple lines of text. Left side, Right side or Centered.')
        self.justify.trace_variable("w", self.Entry_justify_Callback)

        self.origin_frame = Frame(self)
        self.Label_Origin = Label(self.origin_frame, text="Origin", width=w_label, anchor=E)
        self.Origin_OptionMenu = OptionMenu(self.origin_frame, self.origin, "Top-Left", "Top-Center", "Top-Right", "Mid-Left",
                                            "Mid-Center", "Mid-Right", "Bot-Left", "Bot-Center", "Bot-Right", "Default",
                                            command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin,
                                            text='Origin determins where the X and Y zero position is located relative to the engraving.')
        self.origin.trace_variable("w", self.Entry_origin_Callback)

        self.flip_frame = Frame(self)
        self.Label_flip = Label(self.flip_frame, text="Flip Text", width=w_label, anchor=E)
        self.Checkbutton_flip = Checkbutton(self.flip_frame, text=" ")
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_flip_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip,
                                          text='Selecting Flip Text mirrors the text about a horizontal line.')

        self.mirror_frame = Frame(self)
        self.Label_mirror = Label(self.mirror_frame, text="Mirror Text", width=w_label, anchor=E)
        self.Checkbutton_mirror = Checkbutton(self.mirror_frame, text=" ")
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_mirror_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror,
                                            text='Selecting Mirror Text mirrors the text about a vertical line.')

    def configure(self):
        self.Label_pos_orient.pack(side=TOP, anchor=W)

        self.Label_Tangle.pack(side=LEFT)
        self.Label_Tangle_u.pack(side=RIGHT)
        self.Entry_Tangle.pack()
        self.tangle_frame.pack(anchor=W, padx=5)

        self.Label_Justify.pack(side=LEFT)
        self.Justify_OptionMenu.pack()
        self.justify_frame.pack(anchor=W, padx=5)

        self.Label_Origin.pack(side=LEFT)
        self.Origin_OptionMenu.pack()
        self.origin_frame.pack(anchor=W, padx=5)

        self.Label_flip.pack(side=LEFT)
        self.Checkbutton_flip.pack()
        self.flip_frame.pack(anchor=W, padx=5)

        self.Label_mirror.pack(side=LEFT, anchor=W)
        self.Checkbutton_mirror.pack()
        self.mirror_frame.pack(anchor=W, padx=5)

    def initialise_variables(self):
        self.TANGLE.set(self.settings.get('text_angle'))
        self.origin.set(self.settings.get('origin'))
        self.justify.set(self.settings.get('justify'))
        self.flip.set(self.settings.get('flip'))
        self.mirror.set(self.settings.get('mirror'))

    def check_all_variables(self, new):
        error_cnt = \
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), new)
        return error_cnt

    # Text Position and Orientation callbacks

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


class TextOnCircle(MainWindowWidget):

    def __init__(self, parent, gui, settings):
        MainWindowWidget.__init__(self, parent, gui, settings)

        self.TRADIUS = StringVar()
        self.outer = BooleanVar()
        self.upper = BooleanVar()

        self.initialise_variables()
        self.create_widgets()
        self.configure()

    def create_widgets(self):
        self.Label_text_on_arc = Label(self, text="Text on Circle Properties:", anchor=W)

        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.tradius_frame = Frame(self)
        self.Label_Tradius = Label(self.tradius_frame, text="Circle Radius", width=w_label, anchor=E)
        self.Label_Tradius_u = Label(self.tradius_frame, textvariable=self.units, anchor=W)
        self.Entry_Tradius = Entry(self.tradius_frame, width=w_entry)
        self.Entry_Tradius.configure(textvariable=self.TRADIUS)
        self.Entry_Tradius.bind('<Return>', self.Recalculate_Click)
        self.TRADIUS.trace_variable("w", self.Entry_Tradius_Callback)
        self.Label_Tradius_ToolTip = ToolTip(self.Label_Tradius,
                                             text='Circle radius is the radius of the circle that the text in the input box is placed on. \
                                             If the circle radius is set to 0.0 the text is not placed on a circle.')

        self.outer_frame = Frame(self)
        self.Label_outer = Label(self.outer_frame, text="Outside circle", width=w_label, anchor=E)
        self.Checkbutton_outer = Checkbutton(self.outer_frame, text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=self.outer)
        self.outer.trace_variable("w", self.Entry_outer_Callback)
        self.Label_outer_ToolTip = ToolTip(self.Label_outer,
                                           text='Select whether the text is placed so that is falls on the inside of \
                                           the circle radius or the outside of the circle radius.')

        self.upper_frame = Frame(self)
        self.Label_upper = Label(self.upper_frame, text="Top of Circle", width=w_label, anchor=E)
        self.Checkbutton_upper = Checkbutton(self.upper_frame, text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=self.upper)
        self.upper.trace_variable("w", self.Entry_upper_Callback)
        self.Label_upper_ToolTip = ToolTip(self.Label_upper,
                                           text='Select whether the text is placed on the top of the circle of on the bottom of the circle  \
                                           (i.e. concave down or concave up).')

    def configure(self):

        # Text on circle properties

        self.Label_text_on_arc.pack(side=TOP, anchor=W, padx=5)

        self.Label_Tradius.pack(side=LEFT)
        self.Label_Tradius_u.pack(side=RIGHT)
        self.Entry_Tradius.pack()
        self.tradius_frame.pack(anchor=W, padx=5)

        self.Label_outer.pack(side=LEFT)
        self.Checkbutton_outer.pack(side=RIGHT)
        self.outer_frame.pack(anchor=W, padx=5)

        self.Label_upper.pack(side=LEFT)
        self.Checkbutton_upper.pack(side=RIGHT)
        self.upper_frame.pack(anchor=W, padx=5)

        self.configure_units()

    def configure_units(self):
        self.units.set(self.settings.get('units'))

    def initialise_variables(self):
        self.TRADIUS.set(self.settings.get('text_radius'))
        self.outer.set(self.settings.get('outer'))
        self.upper.set(self.settings.get('upper'))

    def check_all_variables(self, new):
        error_cnt = \
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), new)
        return error_cnt

    def scale_linear_inputs(self, factor=1.0):
        self.TRADIUS.set('%.3g' % self.settings.get('text_radius'))

    # Text on Circle callbacks

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

    def Entry_outer_Callback(self, varName, index, mode):
        self.settings.set('outer', self.outer.get())
        self.Recalc_RQD()

    def Entry_upper_Callback(self, varName, index, mode):
        self.settings.set('upper', self.upper.get())
        self.Recalc_RQD()


class GCodeProperties(MainWindowWidget):

    def __init__(self, parent, gui, settings):
        MainWindowWidget.__init__(self, parent, gui, settings)

        self.funits = StringVar()
        self.FEED = StringVar()
        self.PLUNGE = StringVar()
        self.ZSAFE = StringVar()
        self.ZCUT = StringVar()

        self.initialise_variables()
        self.create_widgets()
        self.configure()

    def create_widgets(self):
        self.Label_gcode_opt = Label(self, text="Gcode Properties:", anchor=W)

        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.feed_frame = Frame(self)
        self.Label_Feed = Label(self.feed_frame, text="Feed Rate", width=w_label, anchor=E)
        self.Label_Feed_u = Label(self.feed_frame, textvariable=self.funits, anchor=W)
        self.Entry_Feed = Entry(self.feed_frame, width=w_entry)
        self.Entry_Feed.configure(textvariable=self.FEED)
        self.Entry_Feed.bind('<Return>', self.Recalculate_Click)
        self.FEED.trace_variable("w", self.Entry_Feed_Callback)
        self.Label_Feed_ToolTip = ToolTip(self.Label_Feed,
                                          text='Specify the tool feed rate that is output in the g-code output file.')

        self.plunge_frame = Frame(self)
        self.Label_Plunge = Label(self.plunge_frame, text="Plunge Rate", width=w_label, anchor=E)
        self.Label_Plunge_u = Label(self.plunge_frame, textvariable=self.funits, anchor=W)
        self.Entry_Plunge = Entry(self.plunge_frame, width=w_entry)
        self.Entry_Plunge.configure(textvariable=self.PLUNGE)
        self.Entry_Plunge.bind('<Return>', self.Recalculate_Click)
        self.PLUNGE.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(self.Label_Plunge,
                                            text='Plunge Rate sets the feed rate for vertical moves into the material being cut.\n \
                                            When Plunge Rate is set to zero plunge feeds are equal to Feed Rate.')

        self.zsafe_frame = Frame(self)
        self.Label_Zsafe = Label(self.zsafe_frame, text="Z Safe", width=w_label, anchor=E)
        self.Label_Zsafe_u = Label(self.zsafe_frame, textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self.zsafe_frame, width=w_entry)
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(self.Label_Zsafe,
                                           text='Z location that the tool will be sent to prior to any rapid moves.')

        self.zcut_frame = Frame(self)
        self.Label_Zcut = Label(self.zcut_frame, text="Engrave Depth", width=w_label, anchor=E)
        self.Label_Zcut_u = Label(self.zcut_frame, textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self.zcut_frame, width=w_entry)
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(self.Label_Zcut,
                                          text='Depth of the engraving cut. This setting has no effect when the v-carve option is selected.')

    def configure(self):
        self.Label_gcode_opt.pack(side=TOP, padx=10, anchor=W)

        self.Label_Feed.pack(side=LEFT)
        self.Label_Feed_u.pack(side=RIGHT)
        self.Entry_Feed.pack()
        self.feed_frame.pack(anchor=W, padx=5)

        self.Label_Plunge.pack(side=LEFT)
        self.Label_Plunge_u.pack(side=RIGHT)
        self.Entry_Plunge.pack()
        self.plunge_frame.pack(anchor=W, padx=5)

        self.Label_Zsafe.pack(side=LEFT)
        self.Label_Zsafe_u.pack(side=RIGHT)
        self.Entry_Zsafe.pack()
        self.zsafe_frame.pack(anchor=W, padx=5)

        self.Label_Zcut.pack(side=LEFT)
        self.Label_Zcut_u.pack(side=RIGHT)
        self.Entry_Zcut.pack()
        self.zcut_frame.pack(anchor=W, padx=5)

        self.configure_cut_type()
        self.configure_units()

    def configure_units(self):
        self.units.set(self.settings.get('units'))
        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.funits.set('mm/min')

    def configure_cut_type(self):
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.Entry_Zcut.configure(state="disabled")
            self.Label_Zcut.configure(state="disabled")
            self.Label_Zcut_u.configure(state="disabled")
        else:
            self.Entry_Zcut.configure(state="normal")
            self.Label_Zcut.configure(state="normal")
            self.Label_Zcut_u.configure(state="normal")

    def initialise_variables(self):
        self.funits.set(self.settings.get('feed_units'))
        self.FEED.set(self.settings.get('feedrate'))
        self.PLUNGE.set(self.settings.get('plunge_rate'))
        self.ZSAFE.set(self.settings.get('zsafe'))
        self.ZCUT.set(self.settings.get('zcut'))

    def check_all_variables(self, new):
        error_cnt = self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), new) + \
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), new) + \
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), new) + \
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), new)
        return error_cnt

    def scale_linear_inputs(self, factor=1.0):
        self.FEED.set('%.3g' % self.settings.get('feedrate'))
        self.PLUNGE.set('%.3g' % self.settings.get('plunge_rate'))
        self.ZSAFE.set('%.3g' % self.settings.get('zsafe'))
        self.ZCUT.set('%.3g' % self.settings.get('zcut'))

    # G-Code Properties callbacks

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


class FontFiles(MainWindowWidget):

    def __init__(self, parent, gui, settings):
        MainWindowWidget.__init__(self, parent, gui, settings)

        self.fontdex = BooleanVar()
        self.fontdir = StringVar()
        self.fontfile = StringVar()
        self.current_input_file = StringVar()

        # Gui callback
        self.readFontFile = gui.readFontFile

        self.initialise_variables()
        self.create_widgets()
        self.configure()
        # self.bind_keys()

    def create_widgets(self):
        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.Checkbutton_fontdex = Checkbutton(self, text="Show All Font Characters", width=20, anchor=W)
        self.fontdex.trace_variable("w", self.Entry_fontdex_Callback)
        self.Checkbutton_fontdex.configure(variable=self.fontdex)
        self.Label_fontfile = Label(self, textvariable=self.current_input_file, anchor=W, foreground='grey50')

        self.Label_List_Box = Label(self, text="Font Files:", foreground="#101010", anchor=W)

        self.Listbox_1_frame = Frame(self)
        scrollbar = Scrollbar(self.Listbox_1_frame, orient=VERTICAL)

        self.Listbox_1 = Listbox(self.Listbox_1_frame, selectmode="single", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Listbox_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Listbox_1.pack(side=LEFT, fill=BOTH, expand=1, anchor=W)

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

    # TODO how to bind the keys to the frame only (so the previewcanvas is not affected)
    def bind_keys(self):
        self.bind('<Control-Up>', self.Listbox_Key_Up)
        self.bind('<Control-Down>', self.Listbox_Key_Down)
        # self.Listbox_1.bind('<Control-Up>', self.Listbox_Key_Up)
        # self.Listbox_1.bind('<Control-Down>', self.Listbox_Key_Down)

    def configure(self):
        self.Label_List_Box.pack(anchor=W, padx=10)
        self.Listbox_1_frame.pack(fill=Y, expand=1)
        self.Label_fontfile.pack()
        self.Checkbutton_fontdex.pack(side=LEFT)

    def initialise_variables(self):
        self.fontfile.set(self.settings.get('fontfile'))
        self.fontdir.set(self.settings.get('fontdir'))

    # Font Properties callbacks

    def Entry_fontdex_Callback(self, varName, index, mode):
        self.settings.set('fontdex', self.fontdex.get())
        self.Recalc_RQD()

    def Entry_fontdir_Callback(self, varName, index, mode):
        self.Listbox_1.delete(0, END)
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
        self.readFontFile()
        self.do_it()


class ImageProperties(MainWindowWidget):

    def __init__(self, parent, gui, settings):
        MainWindowWidget.__init__(self, parent, gui, settings)

        self.useIMGsize = BooleanVar()
        self.YSCALE = StringVar()
        self.XSCALE = StringVar()
        self.LSPACE = StringVar()
        self.CSPACE = StringVar()
        self.WSPACE = StringVar()
        self.STHICK = StringVar()

        self.initialise_variables()
        self.create_widgets()
        self.configure()

    def create_widgets(self):
        self.Label_image_prop = Label(self, text="Image Properties:", anchor=W)

        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.useIMGsize_frame = Frame(self)
        self.Label_useIMGsize = Label(self.useIMGsize_frame, text="Set Height as %", width=w_label, anchor=E)
        self.Checkbutton_useIMGsize = Checkbutton(self.useIMGsize_frame, text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command=self.useIMGsize_var_Callback)

        self.yscale_frame = Frame(self)
        self.Label_Yscale = Label(self.yscale_frame, text="Image Height", width=w_label, anchor=E)
        self.Label_Yscale_u = Label(self.yscale_frame, textvariable=self.units, anchor=W)
        self.Label_Yscale_pct = Label(self.yscale_frame, text="%", anchor=W)
        self.Entry_Yscale = Entry(self.yscale_frame, width=w_entry)
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)

        self.sthick_frame = Frame(self)
        self.Label_Sthick = Label(self.sthick_frame, text="Line Thickness", width=w_label, anchor=E)
        self.Label_Sthick_u = Label(self.sthick_frame, textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self.sthick_frame, width=w_entry)
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick,
                                            text='Thickness or width of engraved lines. \
                                            Set this to your engraving cutter diameter. \
                                            This setting only affects the displayed lines not the g-code output.')

        self.xscale_frame = Frame(self)
        self.Label_Xscale = Label(self.xscale_frame, text="Image Width", width=w_label, anchor=E)
        self.Label_Xscale_u = Label(self.xscale_frame, text="%", anchor=W)
        self.Entry_Xscale = Entry(self.xscale_frame, width=w_entry)
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale,
                                            text='Scaling factor for the image width.')

    def configure(self):
        self.Label_image_prop.pack(side=TOP, padx=10, anchor=W)

        self.Label_Yscale.pack(side=LEFT, anchor=W)
        if self.settings.get('useIMGsize'):
            self.Label_Yscale_u.pack_forget()
            self.Label_Yscale_pct.pack(side=RIGHT)
        else:
            self.Label_Yscale_pct.pack_forget()
            self.Label_Yscale_u.pack(side=RIGHT)
        self.Entry_Yscale.pack()
        self.yscale_frame.pack(anchor=W, padx=5)

        self.Label_useIMGsize.pack(side=LEFT, anchor=W)
        self.Checkbutton_useIMGsize.pack()
        self.useIMGsize_frame.pack(anchor=W, padx=5)

        self.Label_Sthick.pack(side=LEFT, anchor=W)
        self.Label_Sthick_u.pack(side=RIGHT)
        self.Entry_Sthick.pack()
        self.sthick_frame.pack(anchor=W, padx=5)

        self.Label_Xscale.pack(side=LEFT, anchor=W)
        self.Label_Xscale_u.pack(side=RIGHT)
        self.Entry_Xscale.pack()
        self.xscale_frame.pack(anchor=W, padx=5)

        self.configure_units()
        self.configure_cut_type()

    def configure_units(self):
        self.units.set(self.settings.get('units'))

    def configure_cut_type(self):
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            # self.V_Carve_Calc.configure(state="normal", command=None)
            self.Entry_Sthick.configure(state="disabled")
            self.Label_Sthick.configure(state="disabled")
            self.Label_Sthick_u.configure(state="disabled")
        else:
            # self.V_Carve_Calc.configure(state="disabled", command=None)
            self.Entry_Sthick.configure(state="normal")
            self.Label_Sthick.configure(state="normal")
            self.Label_Sthick_u.configure(state="normal")

    def initialise_variables(self):
        self.useIMGsize.set(self.settings.get('useIMGsize'))
        self.YSCALE.set(self.settings.get('yscale'))
        self.XSCALE.set(self.settings.get('xscale'))
        self.STHICK.set(self.settings.get('line_thickness'))

    def check_all_variables(self, new):
        error_cnt = \
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), new) + \
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), new) + \
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), new)
        return error_cnt

    def scale_linear_inputs(self):
        self.YSCALE.set('%.3g' % self.settings.get('yscale'))
        self.STHICK.set('%.3g' % self.settings.get('line_thickness'))

    # Image Properties callbacks

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


class ImagePosition(TextPosition):

    def __init__(self, parent, gui, settings):
        TextPosition.__init__(self, parent, gui, settings)

        # self.initialise_variables()
        self.create_widgets()
        self.configure()

    # TODO aanpassen van de Text widgets
    def create_widgets(self):
        self.Label_pos_orient = Label(self, text="Image Position and Orientation:", anchor=W)

        w_label = self.w_label
        w_entry = self.w_entry
        w_units = self.w_units

        self.tangle_frame = Frame(self)
        self.Label_Tangle = Label(self.tangle_frame, text="Image Angle", width=w_label, anchor=E)
        self.Label_Tangle_u = Label(self.tangle_frame, text="deg", anchor=W)
        self.Entry_Tangle = Entry(self.tangle_frame, width=w_entry)
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle,
                                            text='Rotation of the image from horizontal.')

        self.origin_frame = Frame(self)
        self.Label_Origin = Label(self.origin_frame, text="Origin", width=w_label, anchor=E)
        self.Origin_OptionMenu = OptionMenu(self.origin_frame, self.origin, "Top-Left", "Top-Center", "Top-Right", "Mid-Left",
                                            "Mid-Center", "Mid-Right", "Bot-Left", "Bot-Center", "Bot-Right", "Default",
                                            command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin,
                                            text='Origin determines where the X and Y zero position is located relative to the engraving.')
        self.origin.trace_variable("w", self.Entry_origin_Callback)

        self.flip_frame = Frame(self)
        self.Label_flip = Label(self.flip_frame, text="Flip Image", width=w_label, anchor=E)
        self.Checkbutton_flip = Checkbutton(self.flip_frame, text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_flip_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip,
                                          text='Selecting Flip Image mirrors the design about a horizontal line.')

        self.mirror_frame = Frame(self)
        self.Label_mirror = Label(self.mirror_frame, text="Mirror Image", width=w_label, anchor=E)
        self.Checkbutton_mirror = Checkbutton(self.mirror_frame, text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_mirror_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror,
                                            text='Selecting Mirror Image mirrors the design about a vertical line.')

    def configure(self):
        self.Label_pos_orient.pack(side=TOP, padx=10, anchor=W)

        self.Label_Tangle.pack(side=LEFT)
        self.Label_Tangle_u.pack(side=RIGHT)
        self.Entry_Tangle.pack()
        self.tangle_frame.pack(anchor=W, padx=5)

        self.Label_Origin.pack(side=LEFT)
        self.Origin_OptionMenu.pack()
        self.origin_frame.pack(anchor=W, padx=5)

        self.Label_flip.pack(side=LEFT)
        self.Checkbutton_flip.pack()
        self.flip_frame.pack(anchor=W, padx=5)

        self.Label_mirror.pack(side=LEFT, anchor=W)
        self.Checkbutton_mirror.pack()
        self.mirror_frame.pack(anchor=W, padx=5)

        self.configure_units()


class MainWindowTextLeft(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        self.h = 490
        Frame.__init__(self, parent, width=self.w, height=self.h)

        self.settings = settings

        self.cut_type = StringVar()
        self.units = StringVar()

        # Gui callback
        self.Recalculate_Click = gui.Recalculate_Click
        self.set_menu_cut_type = gui.Ctrl_set_menu_cut_type
        self.Recalc_RQD = gui.Recalc_RQD

        self.set_cut_type()
        self.cut_type.trace_variable("w", self.entry_cut_type_callback)

        self.create_widgets(gui, settings)
        self.configure()

    def create_widgets(self, gui, settings):
        self.text_font_properties = TextFontProperties(self, gui, settings)
        self.text_position = TextPosition(self, gui, settings)
        self.text_on_circle = TextOnCircle(self, gui, settings)

        self.separator1 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(master=self, height=2, bd=1, relief=SUNKEN)

        # Buttons
        self.Recalculate = Button(self, text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

    def configure(self):
        self.text_font_properties.configure()
        self.text_position.configure()
        self.text_on_circle.configure()

        self.text_font_properties.pack(side=TOP, anchor=W)

        self.separator1.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.text_position.pack(side=TOP, fill=BOTH, anchor=W)

        self.separator2.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.text_on_circle.pack(side=TOP, fill=BOTH, anchor=W)

        # Button
        self.separator3.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.Recalculate.pack(side=BOTTOM, anchor=W)

    def set_cut_type(self):
        if self.cut_type.get() != self.settings.get('cut_type'):
            self.cut_type.set(self.settings.get('cut_type'))

    def entry_cut_type_callback(self, varName, index, mode):
        self.settings.set('cut_type', self.cut_type.get())

        self.text_font_properties.configure_cut_type()
        self.text_position.configure_cut_type()
        self.text_on_circle.configure_cut_type()

        self.set_menu_cut_type()
        self.Recalc_RQD()

    def check_all_variables(self, new):
        error_cnt = \
            self.text_font_properties.check_all_variables(new) + \
            self.text_position.check_all_variables(new) + \
            self.text_on_circle.check_all_variables(new)
        return error_cnt

    def scale_linear_inputs(self, factor=1.0):
        self.text_font_properties.scale_linear_inputs()
        self.text_position.scale_linear_inputs()
        self.text_on_circle.scale_linear_inputs()

    def entry_units_var_callback(self):
        self.text_font_properties.configure_units()
        self.text_position.configure_units()
        self.text_on_circle.configure_units()


class MainWindowTextRight(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        self.h = 490
        Frame.__init__(self, parent, width=self.w)

        self.settings = settings

        self.cut_type = StringVar()
        self.units = StringVar()

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

        self.set_menu_cut_type = gui.Ctrl_set_menu_cut_type

        self.set_cut_type()
        self.cut_type.trace_variable("w", self.entry_cut_type_callback)

        self.create_widgets(gui, settings)
        self.configure()

    def create_widgets(self, gui, settings):
        self.gcode_properties = GCodeProperties(self, gui, settings)
        self.font_files = FontFiles(self, gui, settings)

        self.separator1 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(master=self, height=2, bd=1, relief=SUNKEN)

        self.V_Carve_Calc = Button(self, text="Calc V-Carve", command=self.V_Carve_Calc_Click)

        self.Radio_Cut_E = Radiobutton(self, text="Engrave", value="engrave", anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type)
        self.Radio_Cut_V = Radiobutton(self, text="V-Carve", value="v-carve", anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type)

    def set_cut_type(self):
        # only when changed (to avoid recursion due to trace_variable callback)
        if self.cut_type.get() != self.settings.get('cut_type'):
            self.cut_type.set(self.settings.get('cut_type'))

    def configure(self):
        self.gcode_properties.pack(side=TOP, anchor=W)
        self.font_files.configure()

        self.separator1.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.font_files.pack(side=TOP, fill=BOTH, anchor=W, expand=1)

        # Buttons
        self.separator3.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.Radio_Cut_E.pack(side=BOTTOM, anchor=W)
        self.Radio_Cut_V.pack(side=BOTTOM, anchor=W)
        self.V_Carve_Calc.pack(side=BOTTOM, anchor=W)

        self.configure_cut_type()

    def configure_cut_type(self):
        if self.cut_type.get() == CUT_TYPE_VCARVE:
            self.V_Carve_Calc.configure(state="normal", command=None)
        else:
            self.V_Carve_Calc.configure(state="disabled", command=None)

    def check_all_variables(self, new):
        error_cnt = \
            self.gcode_properties.check_all_variables(new)
        # self.font_files.check_all_variables(new)

        return error_cnt

    def scale_linear_inputs(self, factor=1.0):
        self.gcode_properties.scale_linear_inputs()
        self.font_files.scale_linear_inputs()

    def entry_units_var_callback(self):
        self.gcode_properties.configure_units()

    def entry_cut_type_callback(self, varName, index, mode):
        self.settings.set('cut_type', self.cut_type.get())

        self.gcode_properties.configure_cut_type()
        self.set_menu_cut_type()
        self.Recalc_RQD()


class MainWindowImageLeft(Frame):

    def __init__(self, parent, gui, settings):

        self.w = 250
        self.h = 540
        Frame.__init__(self, parent, width=self.w, height=self.h)

        self.settings = settings

        self.cut_type = StringVar()
        self.units = StringVar()

        # GUI callbacks
        self.entry_set = gui.entry_set
        self.Recalculate_Click = gui.Recalculate_Click
        self.Recalculate_RQD_Click = gui.Recalculate_RQD_Click
        self.V_Carve_Calc_Click = gui.V_Carve_Calc_Click
        self.Recalc_RQD = gui.Recalc_RQD
        self.menu_View_Refresh = gui.menu_View_Refresh
        self.set_menu_cut_type = gui.Ctrl_set_menu_cut_type

        self.set_cut_type()
        self.cut_type.trace_variable("w", self.entry_cut_type_callback)

        self.create_widgets(gui, settings)
        self.configure()

    def create_widgets(self, gui, settings):
        self.image_properties = ImageProperties(self, gui, settings)
        self.image_position = ImagePosition(self, gui, settings)
        self.gcode_properties = GCodeProperties(self, gui, settings)

        self.separator1 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(master=self, height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(master=self, height=2, bd=1, relief=SUNKEN)

        self.Radio_Cut_E = Radiobutton(self, text="Engrave", value="engrave", width=10, anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type)
        self.Radio_Cut_V = Radiobutton(self, text="V-Carve", value="v-carve", width=10, anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type)

        self.button_frame = Frame(self)
        self.Recalculate = Button(self.button_frame, text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)
        self.V_Carve_Calc = Button(self.button_frame, text="Calc V-Carve", command=self.V_Carve_Calc_Click)

        self.cut_type.trace_variable("w", self.entry_cut_type_callback)

    def set_cut_type(self):
        # only when changed (to avoid recursion due to trace_variable callback)
        if self.cut_type.get() != self.settings.get('cut_type'):
            self.cut_type.set(self.settings.get('cut_type'))

    def configure(self):
        self.image_properties.pack(side=TOP, padx=10, anchor=W)

        self.separator1.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.image_position.pack(side=TOP, anchor=W)

        self.separator2.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.gcode_properties.pack(side=TOP, anchor=W)

        # Buttons
        self.separator3.pack(side=TOP, fill=X, padx=10, pady=5, anchor=W)
        self.Radio_Cut_E.pack(side=TOP, anchor=E)
        self.Radio_Cut_V.pack(side=TOP, anchor=E)

        self.Recalculate.pack(side=LEFT)
        self.V_Carve_Calc.pack(side=RIGHT)
        self.button_frame.pack(side=TOP)

        self.configure_cut_type()

    def configure_cut_type(self):
        if self.cut_type.get() == CUT_TYPE_VCARVE:
            self.V_Carve_Calc.configure(state="normal", command=None)
        else:
            self.V_Carve_Calc.configure(state="disabled", command=None)

    def check_all_variables(self, new):
        error_cnt = \
            self.image_properties.check_all_variables(new) + \
            self.image_position.check_all_variables(new) + \
            self.gcode_properties.check_all_variables(new)
        return error_cnt

    def scale_linear_inputs(self, factor=1.0):
        self.image_properties.scale_linear_inputs()
        self.image_position.scale_linear_inputs()
        self.gcode_properties.scale_linear_inputs()

    def entry_units_var_callback(self):
        self.image_properties.configure_units()
        self.image_position.configure_units()
        self.gcode_properties.configure_units()

    def entry_cut_type_callback(self, varName, index, mode):
        self.settings.set('cut_type', self.cut_type.get())

        self.image_properties.configure_cut_type()
        self.image_position.configure_cut_type()
        self.gcode_properties.configure_cut_type()

        self.set_menu_cut_type()
        self.Recalc_RQD()
