from util import VERSION, OK, NOR, INV, NAN
from tooltip import ToolTip

if VERSION == 3:
    from tkinter import *
else:
    from Tkinter import *


class GeneralSettings(object):

    def __init__(self, master, settings):

        self.settings = settings

        # GUI callbacks
        self.entry_set = master.entry_set
        self.statusMessage = master.statusMessage
        self.Fontdir_Click = master.Fontdir_Click
        self.Settings_ReLoad_Click = master.Settings_ReLoad_Click
        self.Recalculate_Click = master.Recalculate_Click
        self.Settings_ReLoad_Click = master.Settings_ReLoad_Click
        self.write_config_file = master.write_config_file
        self.Recalc_RQD = master.Recalc_RQD
        self.Scale_Linear_Inputs = master.Scale_Linear_Inputs

        # GUI Engraver callbacks
        self.refresh_v_pplot = master.engrave.refresh_v_pplot

        # General settings window
        self.general_settings = Toplevel(width=600, height=500)
        # Use grab_set to prevent user input in the main window during calculations
        self.general_settings.grab_set()
        self.general_settings.resizable(0, 0)
        self.general_settings.title('Settings')
        self.general_settings.iconname("Settings")

        # General Settings entries
        self.Entry_Xoffset = Entry()
        self.Entry_Yoffset = Entry()
        self.Entry_BoxGap = Entry()
        self.Entry_ArcAngle = Entry()
        self.Entry_Accuracy = Entry()

        # General Settings variables
        self.units = StringVar()
        self.funits = StringVar()   # feed units
        self.xorigin = StringVar()  # Xoffset
        self.yorigin = StringVar()  # Yoffset
        self.segarc = StringVar()   # ArcAngle
        self.accuracy = StringVar()

        self.ext_char = BooleanVar()
        self.arc_fit = StringVar()
        self.no_comments = BooleanVar()

        self.gpre = StringVar()
        self.gpost = StringVar()

        self.var_dis = BooleanVar()
        self.fontdir = StringVar()
        self.H_CALC = StringVar()  # height calculation

        self.useIMGsize = BooleanVar()
        self.plotbox = BooleanVar()
        self.boxgap = StringVar()
        self.v_pplot = BooleanVar()
        self.input_type = StringVar()

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

        self.initialise_variables()
        self.create_widgets()
        self.create_icon()

    def initialise_variables(self):
        self.units.set(self.settings.get('units'))
        self.funits.set(self.settings.get('feed_units'))
        self.xorigin.set(self.settings.get('xorigin'))
        self.yorigin.set(self.settings.get('yorigin'))
        self.segarc.set(self.settings.get('segarc'))
        self.accuracy.set(self.settings.get('accuracy'))

        self.ext_char.set(self.settings.get('ext_char'))
        self.arc_fit.set(self.settings.get('arc_fit'))
        self.no_comments.set(self.settings.get('no_comments'))

        self.gpre.set(self.settings.get('gcode_preamble'))
        self.gpost.set(self.settings.get('gcode_postamble'))

        self.var_dis.set(self.settings.get('var_dis'))
        self.fontdir.set(self.settings.get('fontdir'))
        self.H_CALC.set(self.settings.get('height_calculation'))

        self.useIMGsize.set(self.settings.get('useIMGsize'))
        self.plotbox.set(self.settings.get('plotbox'))
        self.boxgap.set(self.settings.get('boxgap'))
        self.v_pplot.set(self.settings.get('v_pplot'))
        self.input_type.set(self.settings.get('input_type'))

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

    def Close_Current_Window_Click(self):
        self.general_settings.destroy()

    def create_widgets(self):

        general_settings = self.general_settings

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
        self.Label_Units = Label(general_settings, text="Units")
        self.Label_Units.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Radio_Units_IN = Radiobutton(general_settings, text="inch", value="in", width="100", anchor=W)
        self.Radio_Units_IN.place(x=w_label + x_radio_offset, y=D_Yloc, width=75, height=23)
        self.Radio_Units_IN.configure(variable=self.units, command=self.Entry_units_var_Callback)

        self.Radio_Units_MM = Radiobutton(general_settings, text="mm", value="mm", width="100", anchor=W)
        self.Radio_Units_MM.place(x=w_label + x_radio_offset + 60, y=D_Yloc, width=75, height=23)
        self.Radio_Units_MM.configure(variable=self.units, command=self.Entry_units_var_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_Xoffset = Label(general_settings, text="X Offset")
        self.Label_Xoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Xoffset_u = Label(general_settings, textvariable=self.units, anchor=W)
        self.Label_Xoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Xoffset = Entry(general_settings, width="15")
        self.Entry_Xoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Xoffset.configure(textvariable=self.xorigin)
        self.xorigin.trace_variable("w", self.Entry_Xoffset_Callback)
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Yoffset = Label(general_settings, text="Y Offset")
        self.Label_Yoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Yoffset_u = Label(general_settings, textvariable=self.units, anchor=W)
        self.Label_Yoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Yoffset = Entry(general_settings, width="15")
        self.Entry_Yoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Yoffset.configure(textvariable=self.yorigin)
        self.yorigin.trace_variable("w", self.Entry_Yoffset_Callback)
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_ArcAngle = Label(general_settings, text="Arc Angle")
        self.Label_ArcAngle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_ArcAngle_u = Label(general_settings, text="deg", anchor=W)
        self.Label_ArcAngle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_ArcAngle = Entry(general_settings, width="15")
        self.Entry_ArcAngle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_ArcAngle.configure(textvariable=self.segarc)
        self.segarc.trace_variable("w", self.Entry_ArcAngle_Callback)
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Accuracy = Label(general_settings, text="Accuracy")
        self.Label_Accuracy.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Accuracy_u = Label(general_settings, textvariable=self.units, anchor=W)
        self.Label_Accuracy_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Accuracy = Entry(general_settings, width="15")
        self.Entry_Accuracy.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Accuracy.configure(textvariable=self.accuracy)
        self.accuracy.trace_variable("w", self.Entry_Accuracy_Callback)
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_ext_char = Label(general_settings, text="Extended Characters")
        self.Label_ext_char.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_ext_char = Checkbutton(general_settings, text="", anchor=W)
        self.Checkbutton_ext_char.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_ext_char.configure(variable=self.ext_char)
        self.ext_char.trace_variable("w", self.Settings_ReLoad_Click)

        D_Yloc = D_Yloc + D_dY
        self.Label_arcfit = Label(general_settings, text="Arc Fitting")
        self.Label_arcfit.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_arcfit_none = Radiobutton(general_settings, text="None",
                                             value="none", width="110", anchor=W)
        self.Radio_arcfit_none.place(x=w_label + x_radio_offset, y=D_Yloc, width=90, height=23)
        self.Radio_arcfit_none.configure(variable=self.arc_fit)
        self.Radio_arcfit_radius = Radiobutton(general_settings, text="Radius Format",
                                               value="radius", width="110", anchor=W)
        self.Radio_arcfit_radius.place(x=w_label + x_radio_offset + 65, y=D_Yloc, width=100, height=23)
        self.Radio_arcfit_radius.configure(variable=self.arc_fit)
        self.Radio_arcfit_center = Radiobutton(general_settings, text="Center Format",
                                               value="center", width="110", anchor=W)
        self.Radio_arcfit_center.place(x=w_label + x_radio_offset + 65 + 115, y=D_Yloc, width=100, height=23)
        self.Radio_arcfit_center.configure(variable=self.arc_fit)
        self.arc_fit.trace_variable("w", self.Entry_arcfit_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_no_com = Label(general_settings, text="Suppress Comments")
        self.Label_no_com.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_no_com = Checkbutton(general_settings, text="", anchor=W)
        self.Checkbutton_no_com.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_no_com.configure(variable=self.no_comments)

        D_Yloc = D_Yloc + D_dY
        self.Label_Gpre = Label(general_settings, text="G Code Header")
        self.Label_Gpre.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpre = Entry(general_settings, width="15")
        self.Entry_Gpre.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpre.configure(textvariable=self.gpre)
        self.gpre.trace_variable("w", self.Entry_Gpre_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_Gpost = Label(general_settings, text="G Code Postscript")
        self.Label_Gpost.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpost = Entry(general_settings)
        self.Entry_Gpost.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpost.configure(textvariable=self.gpost)
        self.gpost.trace_variable("w", self.Entry_Gpost_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_var_dis = Label(general_settings, text="Disable Variables")
        self.Label_var_dis.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_var_dis_ToolTip = ToolTip(self.Label_var_dis,
                                             text='Disable the use of variables in the generated G-Code.')
        self.Checkbutton_var_dis = Checkbutton(general_settings, text="", anchor=W)
        self.Checkbutton_var_dis.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_var_dis.configure(variable=self.var_dis)
        self.var_dis.trace_variable("w", self.Checkbutton_var_dis_Callback)

        D_Yloc = D_Yloc + D_dY
        font_entry_width = 215
        self.Label_Fontdir = Label(general_settings, text="Font Directory")
        self.Label_Fontdir.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Fontdir = Entry(general_settings, width="15")
        self.Entry_Fontdir.place(x=xd_entry_L, y=D_Yloc, width=font_entry_width, height=23)
        self.Entry_Fontdir.configure(textvariable=self.fontdir)
        self.Fontdir = Button(general_settings, text="Select Dir")
        self.Fontdir.place(x=xd_entry_L + font_entry_width + 10, y=D_Yloc, width=w_label - 80, height=23)

        D_Yloc = D_Yloc + D_dY
        self.Label_Hcalc = Label(general_settings, text="Height Calculation")
        self.Label_Hcalc.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Radio_Hcalc_USE = Radiobutton(general_settings, text="Max Used",
                                           value="max_use", width="110", anchor=W)
        self.Radio_Hcalc_USE.place(x=w_label + x_radio_offset, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_USE.configure(variable=self.H_CALC)

        self.Radio_Hcalc_ALL = Radiobutton(general_settings, text="Max All",
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
        self.Label_Box = Label(general_settings, text="Add Box/Circle")
        self.Label_Box.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Checkbutton_plotbox = Checkbutton(general_settings, text="", anchor=W)
        self.Checkbutton_plotbox.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_plotbox.configure(variable=self.plotbox)
        self.plotbox.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(general_settings, text="Box/Circle Gap:", anchor=E)
        self.Label_BoxGap.place(x=w_label + x_radio_offset + 25, y=D_Yloc, width=125, height=21)
        self.Entry_BoxGap = Entry(general_settings)
        self.Entry_BoxGap.place(x=w_label + x_radio_offset + 165, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(general_settings, textvariable=self.units, anchor=W)
        self.Label_BoxGap_u.place(x=w_label + x_radio_offset + 230, y=D_Yloc, width=100, height=21)
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)

        # TODO Tkinter Checkbutton default values are 0/1, this seems to go with False and True, as used in settings.
        # TODO Find out whether it is better to explicitly set on/off value to True respectively False

        D_Yloc = D_Yloc + D_dY
        self.Label_v_pplot = Label(general_settings, text="Plot During V-Carve Calculation")
        self.Label_v_pplot.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_pplot = Checkbutton(general_settings, text="", anchor=W)
        self.Checkbutton_v_pplot.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)
        self.v_pplot.trace_variable("w", self.Entry_v_pplot_Callback)

        D_Yloc = D_Yloc + D_dY + 10
        self.Label_SaveConfig = Label(general_settings, text="Configuration File")
        self.Label_SaveConfig.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.GEN_SaveConfig = Button(general_settings, text="Save")
        self.GEN_SaveConfig.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=21, anchor="nw")
        self.GEN_SaveConfig.bind("<ButtonRelease-1>", self.write_config_file)

        # Buttons
        general_settings.update_idletasks()
        Ybut = int(general_settings.winfo_height()) - 30
        Xbut = int(general_settings.winfo_width() / 2)

        self.GEN_Reload = Button(general_settings, text="Recalculate")
        self.GEN_Reload.place(x=Xbut - 65, y=Ybut, width=130, height=30, anchor="e")
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        self.GEN_Recalculate = Button(general_settings, text="Re-Load Image")
        self.GEN_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="c")
        self.GEN_Recalculate.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.GEN_Close = Button(general_settings, text="Close", command=self.Close_Current_Window_Click)
        self.GEN_Close.place(x=Xbut + 65, y=Ybut, width=130, height=30, anchor="w")

    # Callbacks

    def Entry_units_var_Callback(self):
        if self.units.get() == 'in' and self.funits.get() == 'mm/min':
            self.Scale_Linear_Inputs(1 / 25.4)
            self.funits.set('in/min')
        elif self.units.get() == 'mm' and self.funits.get() == 'in/min':
            self.Scale_Linear_Inputs(25.4)
            self.funits.set('mm/min')

        self.settings.set('units', self.units.get())
        self.settings.set('feed_units', self.funits.get())

        self.Recalc_RQD()

    def Entry_Xoffset_Check(self):
        try:
            float(self.xorigin.get())
        except:
            return NAN
        return NOR

    def Entry_Xoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), setting='xorigin')

    def Entry_Yoffset_Check(self):
        try:
            float(self.yorigin.get())
        except:
            return NAN
        return NOR

    def Entry_Yoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), setting='yorigin')

    def Entry_ArcAngle_Check(self):
        try:
            float(self.segarc.get())
        except:
            return NAN
        return OK

    def Entry_ArcAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), setting='segarc')

    def Entry_Accuracy_Check(self):
        try:
            float(self.accuracy.get())
        except:
            return NAN
        return OK

    def Entry_Accuracy_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), setting='accuracy')

    def Entry_arcfit_Callback(self, varName, index, mode):
        self.settings.set('arc_fit', self.arc_fit.get())

    def Entry_Gpre_Callback(self, varName, index, mode):
        self.settings.set('gcode_preamble', self.gpre.get())

    def Entry_Gpost_Callback(self, varName, index, mode):
        self.settings.set('gcode_postamble', self.gpost.get())

    def Checkbutton_var_dis_Callback(self, varName, index, mode):
        self.settings.set('var_dis', self.var_dis.get())

    # TODO same validation is part of V-Carve settings
    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
            if value <= 0.0:
                self.statusMessage.set(" Gap should be greater than zero.")
                return INV
        except:
            return NAN
        return OK

    # TODO same validation is part of V-Carve settings
    def Entry_BoxGap_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), setting='boxgap')
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

    # TODO same validation is part of V-Carve settings
    def Entry_v_pplot_Callback(self, varName, index, mode):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.refresh_v_pplot()  # TODO only needed when plotting

    def Entry_Box_Callback(self, varName, index, mode):
        try:
            self.Entry_BoxGap_Callback(varName, index, mode)
        except:
            pass
        self.settings.set('plotbox', self.plotbox.get())
        self.Recalc_RQD()

    def create_icon(self):
        try:
            general_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                general_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass
