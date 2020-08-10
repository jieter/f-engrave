from util import VERSION, OK, NOR, INV, NAN, position_window, validate_entry_set
from settings import CUT_TYPE_VCARVE, INPUT_TYPE_IMAGE
from tooltip import ToolTip

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
else:
    from Tkinter import *
    from tkFileDialog import *
    from pubsub import pub


class GeneralSettings(object):

    def __init__(self, master, settings):

        self.settings = settings

        # General settings window
        self.width = 600
        self.height = 500
        self.general_settings = Toplevel(width=self.width, height=self.height)
        self.general_settings.withdraw()

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

        self.initialise_variables()
        self.create_widgets()
        self.configure_cut_type()
        self.configure_input_type()
        self.configure_boxgap()
        self.create_icon()

        position_window(self.general_settings, self.width, self.height)
        self.general_settings.deiconify()

    def Ctrl_units_changed(self):
        pub.sendMessage('units_changed')

    def Ctrl_scale_linear_inputs(self, factor=1.0):
        pub.sendMessage('scale_linear_inputs', factor=factor)

    def Ctrl_v_pplot_changed(self):
        pub.sendMessage('v_pplot_changed')

    def Ctrl_font_selected(self):
        pub.sendMessage('fontdir_click')

    def Ctrl_reload(self, event=None):
        pub.sendMessage('reload')

    def Ctrl_write_config_file(self, event=None):
        pub.sendMessage('write_config_file')

    def Ctrl_recalculate(self, event=None):
        pub.sendMessage('recalculate')

    def Ctrl_recalculation_required(self):
        pub.sendMessage('recalculation_required')

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

    def Close_Current_Window_Click(self):
        error_cnt = \
            validate_entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2) + \
            validate_entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2) + \
            validate_entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2) + \
            validate_entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2) + \
            validate_entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2) + \
            validate_entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2) + \
            validate_entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2) + \
            validate_entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2) + \
            validate_entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2) + \
            validate_entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)

        if error_cnt > 0:
            pub.sendMessage('status_message',
                            msg="Entry Error Detected: Check the entry values in the General Settings window.")
        else:
            self.general_settings.destroy()

    def create_widgets(self):

        general_settings = self.general_settings

        w_label = 25
        w_radio = 5
        w_entry = 5
        w_entry_long = 30

        self.units_frame = Frame(general_settings)
        self.Label_Units = Label(self.units_frame, text="Units", width=w_label)
        self.Label_Units.pack(side=LEFT)

        self.Radio_Units_IN = Radiobutton(self.units_frame, text="inch", value="in", width=w_radio, anchor=W)
        self.Radio_Units_IN.pack(side=LEFT, anchor=W)
        self.Radio_Units_IN.configure(variable=self.units, command=self.Entry_units_var_Callback)

        self.Radio_Units_MM = Radiobutton(self.units_frame, text="mm", value="mm", width=w_radio, anchor=W)
        self.Radio_Units_MM.pack(side=LEFT, anchor=W)
        self.Radio_Units_MM.configure(variable=self.units, command=self.Entry_units_var_Callback)

        self.xoffset_frame = Frame(general_settings)
        self.Label_Xoffset = Label(self.xoffset_frame, text="X Offset", width=w_label)
        self.Label_Xoffset.pack(side=LEFT)
        self.Label_Xoffset_u = Label(self.xoffset_frame, textvariable=self.units, anchor=W)
        self.Label_Xoffset_u.pack(side=RIGHT)
        self.Entry_Xoffset = Entry(self.xoffset_frame, width=w_entry)
        self.Entry_Xoffset.pack(side=LEFT)
        self.Entry_Xoffset.configure(textvariable=self.xorigin)
        self.xorigin.trace_variable("w", self.Entry_Xoffset_Callback)

        self.yoffset_frame = Frame(general_settings)
        self.Label_Yoffset = Label(self.yoffset_frame, text="Y Offset", width=w_label)
        self.Label_Yoffset.pack(side=LEFT)
        self.Label_Yoffset_u = Label(self.yoffset_frame, textvariable=self.units, anchor=W)
        self.Label_Yoffset_u.pack(side=RIGHT)
        self.Entry_Yoffset = Entry(self.yoffset_frame, width=w_entry)
        self.Entry_Yoffset.pack(side=LEFT)
        self.Entry_Yoffset.configure(textvariable=self.yorigin)
        self.yorigin.trace_variable("w", self.Entry_Yoffset_Callback)

        self.arcangle_frame = Frame(general_settings)
        self.Label_ArcAngle = Label(self.arcangle_frame, text="Arc Angle", width=w_label)
        self.Label_ArcAngle.pack(side=LEFT)
        self.Label_ArcAngle_u = Label(self.arcangle_frame, text="deg", anchor=W)
        self.Label_ArcAngle_u.pack(side=RIGHT)
        self.Entry_ArcAngle = Entry(self.arcangle_frame, width=w_entry)
        self.Entry_ArcAngle.pack(side=LEFT)
        self.Entry_ArcAngle.configure(textvariable=self.segarc)
        self.segarc.trace_variable("w", self.Entry_ArcAngle_Callback)

        self.accuracy_frame = Frame(general_settings)
        self.Label_Accuracy = Label(self.accuracy_frame, text="Accuracy", width=w_label)
        self.Label_Accuracy.pack(side=LEFT)
        self.Label_Accuracy_u = Label(self.accuracy_frame, textvariable=self.units, anchor=W)
        self.Label_Accuracy_u.pack(side=RIGHT)
        self.Entry_Accuracy = Entry(self.accuracy_frame, width=w_entry)
        self.Entry_Accuracy.pack(side=LEFT)
        self.Entry_Accuracy.configure(textvariable=self.accuracy)
        self.accuracy.trace_variable("w", self.Entry_Accuracy_Callback)

        self.ext_char_frame = Frame(general_settings)
        self.Label_ext_char = Label(self.ext_char_frame, text="Extended Characters", width=w_label)
        self.Label_ext_char.pack(side=LEFT)
        self.Checkbutton_ext_char = Checkbutton(self.ext_char_frame, text="", anchor=W)
        self.Checkbutton_ext_char.pack(side=LEFT)
        self.Checkbutton_ext_char.configure(variable=self.ext_char)
        self.ext_char.trace_variable("w", self.Entry_ext_char_Callback)

        self.arcfit_frame = Frame(general_settings)
        self.Label_arcfit = Label(self.arcfit_frame, text="Arc Fitting", width=w_label)
        self.Label_arcfit.pack(side=LEFT)
        self.Radio_arcfit_none = Radiobutton(self.arcfit_frame, text="None",
                                             value="none", width=w_radio, anchor=W)
        self.Radio_arcfit_none.pack(side=LEFT, anchor=W)
        self.Radio_arcfit_none.configure(variable=self.arc_fit)
        self.Radio_arcfit_radius = Radiobutton(self.arcfit_frame, text="Radius Format",
                                               value="radius", width=w_radio, anchor=W)
        self.Radio_arcfit_radius.pack(side=LEFT, anchor=W)
        self.Radio_arcfit_radius.configure(variable=self.arc_fit)
        self.Radio_arcfit_center = Radiobutton(self.arcfit_frame, text="Center Format",
                                               value="center", width=w_radio, anchor=W)
        self.Radio_arcfit_center.pack(side=LEFT, anchor=W)
        self.Radio_arcfit_center.configure(variable=self.arc_fit)
        self.arc_fit.trace_variable("w", self.Entry_arcfit_Callback)

        self.no_com_frame = Frame(general_settings)
        self.Label_no_com = Label(self.no_com_frame, text="Suppress Comments", width=w_label)
        self.Label_no_com.pack(side=LEFT)
        self.Checkbutton_no_com = Checkbutton(self.no_com_frame, text="", anchor=W)
        self.Checkbutton_no_com.pack(side=LEFT)
        self.Checkbutton_no_com.configure(variable=self.no_comments)
        self.no_comments.trace_variable("w", self.Entry_no_comments_Callback)

        self.gpre_frame = Frame(general_settings)
        self.Label_Gpre = Label(self.gpre_frame, text="G Code Header", width=w_label)
        self.Label_Gpre.pack(side=LEFT)
        self.Entry_Gpre = Entry(self.gpre_frame, width=w_entry_long)
        self.Entry_Gpre.pack(side=LEFT)
        self.Entry_Gpre.configure(textvariable=self.gpre)
        self.gpre.trace_variable("w", self.Entry_Gpre_Callback)

        self.gpost_frame = Frame(general_settings)
        self.Label_Gpost = Label(self.gpost_frame, text="G Code Postscript", width=w_label)
        self.Label_Gpost.pack(side=LEFT)
        self.Entry_Gpost = Entry(self.gpost_frame, width=w_entry_long)
        self.Entry_Gpost.pack(side=LEFT)
        self.Entry_Gpost.configure(textvariable=self.gpost)
        self.gpost.trace_variable("w", self.Entry_Gpost_Callback)

        self.var_dis_frame = Frame(general_settings)
        self.Label_var_dis = Label(self.var_dis_frame, text="Disable Variables", width=w_label)
        self.Label_var_dis.pack(side=LEFT)
        self.Label_var_dis_ToolTip = ToolTip(self.Label_var_dis,
                                             text='Disable the use of variables in the generated G-Code.')
        self.Checkbutton_var_dis = Checkbutton(self.var_dis_frame, text="", anchor=W)
        self.Checkbutton_var_dis.pack(side=LEFT)
        self.Checkbutton_var_dis.configure(variable=self.var_dis)
        self.var_dis.trace_variable("w", self.Checkbutton_var_dis_Callback)

        self.fontdir_frame = Frame(general_settings)
        self.Label_Fontdir = Label(self.fontdir_frame, text="Font Directory", width=w_label)
        self.Label_Fontdir.pack(side=LEFT)
        self.Entry_Fontdir = Entry(self.fontdir_frame, width=w_entry_long)
        self.Entry_Fontdir.pack(side=LEFT)
        self.Entry_Fontdir.configure(textvariable=self.fontdir)
        self.Fontdir = Button(self.fontdir_frame, text="Select Dir")
        self.Fontdir.pack(side=LEFT)

        self.hcalc_frame = Frame(general_settings)
        self.Label_Hcalc = Label(self.hcalc_frame, text="Height Calculation", width=w_label)
        self.Label_Hcalc.pack(side=LEFT)

        self.Radio_Hcalc_USE = Radiobutton(self.hcalc_frame, text="Max Used",
                                           value="max_use", width=8, anchor=W)
        self.Radio_Hcalc_USE.pack(side=LEFT, anchor=W)
        self.Radio_Hcalc_USE.configure(variable=self.H_CALC)

        self.Radio_Hcalc_ALL = Radiobutton(self.hcalc_frame, text="Max All",
                                           value="max_all", width=8, anchor=W)
        self.Radio_Hcalc_ALL.pack(side=LEFT, anchor=W)
        self.Radio_Hcalc_ALL.configure(variable=self.H_CALC)
        self.H_CALC.trace_variable("w", self.Checkbutton_H_CALC_Callback)

        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
            self.Entry_Fontdir.configure(state="disabled")
            self.Fontdir.configure(state="disabled")
            self.Radio_Hcalc_ALL.configure(state="disabled")
            self.Radio_Hcalc_USE.configure(state="disabled")
        else:
            self.Fontdir.bind("<ButtonRelease-1>", self.Fontdir_Click)

        self.box_frame = Frame(general_settings)
        self.Label_Box = Label(self.box_frame, text="Add Box/Circle", width=w_label)
        self.Label_Box.pack(side=LEFT)

        self.Checkbutton_plotbox = Checkbutton(self.box_frame, text="", anchor=W)
        self.Checkbutton_plotbox.pack(side=LEFT)
        self.Checkbutton_plotbox.configure(variable=self.plotbox)
        self.plotbox.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(self.box_frame, text="Box/Circle Gap:", width=15, anchor=E)
        self.Label_BoxGap.pack(side=LEFT)
        self.Entry_BoxGap = Entry(self.box_frame, width=w_entry)
        self.Entry_BoxGap.pack(side=LEFT)
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(self.box_frame, textvariable=self.units, anchor=W)
        self.Label_BoxGap_u.pack(side=LEFT)

        # TODO Tkinter Checkbutton default values are 0/1, this seems to go with False and True, as used in settings.
        # TODO Find out whether it is better to explicitly set on/off value to True respectively False

        self.vpplot_frame = Frame(general_settings)
        self.Label_v_pplot = Label(self.vpplot_frame, text="Plot During V-Carve Calculation", width=w_label)
        self.Label_v_pplot.pack(side=LEFT)
        self.Checkbutton_v_pplot = Checkbutton(self.vpplot_frame, text="", anchor=W)
        self.Checkbutton_v_pplot.pack(side=LEFT)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)
        self.v_pplot.trace_variable("w", self.Entry_v_pplot_Callback)

        self.save_frame = Frame(general_settings)
        self.Label_SaveConfig = Label(self.save_frame, text="Configuration File", width=w_label)
        self.Label_SaveConfig.pack(side=LEFT)
        self.GEN_SaveConfig = Button(self.save_frame, text="Save")
        self.GEN_SaveConfig.pack(side=LEFT)
        self.GEN_SaveConfig.bind("<ButtonRelease-1>", self.Ctrl_write_config_file)

        self.button_frame = Frame(general_settings)

        padx = 10
        pady = 10

        self.GEN_Recalculate = Button(self.button_frame, text="Recalculate")
        self.GEN_Recalculate.pack(side=LEFT, padx=padx, pady=pady, anchor=CENTER)
        self.GEN_Recalculate.bind("<ButtonRelease-1>", self.recalculate_click)

        self.GEN_Reload = Button(self.button_frame, text="Re-Load Image")
        self.GEN_Reload.pack(side=LEFT, padx=padx, pady=pady, anchor=CENTER)
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Ctrl_reload)

        self.GEN_Close = Button(self.button_frame, text="Close", command=self.Close_Current_Window_Click)
        self.GEN_Close.pack(side=LEFT, padx=padx, pady=pady, anchor=CENTER)

        general_settings.update_idletasks()

        self.units_frame.pack(side=TOP, padx=padx, anchor=W)
        self.xoffset_frame.pack(side=TOP, padx=padx, anchor=W)
        self.yoffset_frame.pack(side=TOP, padx=padx, anchor=W)
        self.arcangle_frame.pack(side=TOP, padx=padx, anchor=W)
        self.accuracy_frame.pack(side=TOP, padx=padx, anchor=W)

        self.ext_char_frame.pack(side=TOP, padx=padx, anchor=W)
        self.arcfit_frame.pack(side=TOP, padx=padx, anchor=W)
        self.no_com_frame.pack(side=TOP, padx=padx, anchor=W)
        self.gpre_frame.pack(side=TOP, padx=padx, anchor=W)
        self.gpost_frame.pack(side=TOP, padx=padx, anchor=W)

        self.var_dis_frame.pack(side=TOP, padx=padx, anchor=W)
        self.fontdir_frame.pack(side=TOP, padx=padx, anchor=W)
        self.hcalc_frame.pack(side=TOP, padx=padx, anchor=W)

        self.box_frame.pack(side=TOP, padx=padx, anchor=W)
        self.vpplot_frame.pack(side=TOP, padx=padx, anchor=W)

        self.save_frame.pack(side=TOP, padx=padx, anchor=W)
        self.button_frame.pack(side=TOP, padx=padx, anchor=CENTER)

    def Scale_Linear_Inputs(self, factor=1.0):
        # All settings are scaled here, the values in the individual frames are refreshed (w the settings here scaled)
        self.settings.set('xorigin', self.settings.get('xorigin') * factor)
        self.settings.set('yorigin', self.settings.get('yorigin') * factor)
        self.settings.set('accuracy', self.settings.get('accuracy') * factor)
        self.settings.set('boxgap', self.settings.get('boxgap') * factor)

        self.settings.set('yscale', self.settings.get('yscale') * factor)
        self.settings.set('line_thickness', self.settings.get('line_thickness') * factor)
        self.settings.set('text_radius', self.settings.get('text_radius') * factor)
        self.settings.set('feedrate', self.settings.get('feedrate') * factor)
        self.settings.set('plunge_rate', self.settings.get('plunge_rate') * factor)
        self.settings.set('zsafe', self.settings.get('zsafe') * factor)
        self.settings.set('zcut', self.settings.get('zcut') * factor)

        self.settings.set('v_bit_dia', self.settings.get('v_bit_dia') * factor)
        self.settings.set('v_depth_lim', self.settings.get('v_depth_lim') * factor)
        self.settings.set('v_max_cut', self.settings.get('v_max_cut') * factor)
        self.settings.set('max_cut', self.settings.get('max_cut') * factor)
        self.settings.set('v_step_len', self.settings.get('v_step_len') * factor)
        self.settings.set('allowance', self.settings.get('allowance') * factor)
        self.settings.set('v_rough_stk', self.settings.get('v_rough_stk') * factor)
        self.settings.set('clean_dia', self.settings.get('clean_dia') * factor)
        self.settings.set('clean_v', self.settings.get('clean_v') * factor)

        self.xorigin.set('%.3g' % self.settings.get('xorigin'))
        self.yorigin.set('%.3g' % self.settings.get('yorigin'))
        self.accuracy.set('%.3g' % self.settings.get('accuracy'))
        self.boxgap.set('%.3g' % self.settings.get('boxgap'))

        self.Ctrl_scale_linear_inputs(factor)

    def check_all_variables(self, new=1):
        error_cnt = \
            validate_entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), new) + \
            validate_entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), new) + \
            validate_entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), new) + \
            validate_entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), new) + \
            validate_entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), new)
        return error_cnt

    def configure_cut_type(self):
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.GEN_Recalculate.configure(state="disabled")
        else:
            self.GEN_Recalculate.configure(state="normal")

    def configure_input_type(self):
        if self.settings.get('input_type') == INPUT_TYPE_IMAGE:
            self.GEN_Reload.configure(state="normal")
        else:
            self.GEN_Reload.configure(state="disabled")

    def configure_boxgap(self):
        if not bool(self.plotbox.get()):
            self.Label_BoxGap.configure(state="disabled")
            self.Entry_BoxGap.configure(state="disabled")
            self.Label_BoxGap_u.configure(state="disabled")
        else:
            self.Label_BoxGap.configure(state="normal")
            self.Entry_BoxGap.configure(state="normal")
            self.Label_BoxGap_u.configure(state="normal")

    # Callbacks

    def recalculate_click(self, event):
        self.check_all_variables()
        self.Ctrl_recalculate(event)

    def Entry_units_var_Callback(self):

        if self.units.get() == 'in' and self.funits.get() == 'mm/min':
            self.Scale_Linear_Inputs(1 / 25.4)
            self.funits.set('in/min')

        elif self.units.get() == 'mm' and self.funits.get() == 'in/min':
            self.Scale_Linear_Inputs(25.4)
            self.funits.set('mm/min')

        self.settings.set('units', self.units.get())
        self.settings.set('feed_units', self.funits.get())

        self.Ctrl_units_changed()
        self.Ctrl_recalculation_required()

    def Entry_Xoffset_Check(self):
        try:
            float(self.xorigin.get())
        except ValueError:
            return NAN
        return NOR

    def Entry_Xoffset_Callback(self, varName, index, mode):
        validate_entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), setting='xorigin', settings=self.settings)

    def Entry_Yoffset_Check(self):
        try:
            float(self.yorigin.get())
        except ValueError:
            return NAN
        return NOR

    def Entry_Yoffset_Callback(self, varName, index, mode):
        validate_entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), setting='yorigin', settings=self.settings)

    def Entry_ArcAngle_Check(self):
        try:
            value = float(self.segarc.get())
            if value <= 0.0:
                pub.sendMessage('status_message', msg="Arc angle should be greater than zero.")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_ArcAngle_Callback(self, varName, index, mode):
        validate_entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), setting='segarc', settings=self.settings)

    def Entry_Accuracy_Check(self):
        try:
            float(self.accuracy.get())
        except ValueError:
            return NAN
        return OK

    def Entry_Accuracy_Callback(self, varName, index, mode):
        validate_entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), setting='accuracy', settings=self.settings)

    def Entry_ext_char_Callback(self, varName, index, mode):
        self.settings.set('ext_char', self.ext_char.get())
        self.Ctrl_reload()

    def Entry_no_comments_Callback(self, varName, index, mode):
        self.settings.set('no_comments', self.no_comments.get())

    def Entry_arcfit_Callback(self, varName, index, mode):
        self.settings.set('arc_fit', self.arc_fit.get())

    def Entry_Gpre_Callback(self, varName, index, mode):
        self.settings.set('gcode_preamble', self.gpre.get())

    def Entry_Gpost_Callback(self, varName, index, mode):
        self.settings.set('gcode_postamble', self.gpost.get())

    def Checkbutton_var_dis_Callback(self, varName, index, mode):
        self.settings.set('var_dis', self.var_dis.get())

    def Checkbutton_H_CALC_Callback(self, varName, index, mode):
        self.settings.set('height_calculation', self.H_CALC.get())
        self.Ctrl_recalculation_required()

    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
            if value <= 0.0:
                pub.sendMessage('status_message', msg="Gap should be greater than zero.")
                return INV
        except:
            return NAN
        return OK

    def Entry_BoxGap_Callback(self, varName, index, mode):
        validate_entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), setting='boxgap', settings=self.settings)
        self.configure_boxgap()

    def Entry_v_pplot_Callback(self, varName, index, mode):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.Ctrl_v_pplot_changed()

    def Entry_Box_Callback(self, varName, index, mode):
        self.settings.set('plotbox', self.plotbox.get())
        try:
            self.Entry_BoxGap_Callback(varName, index, mode)
        except:
            pass
        self.Ctrl_recalculation_required()

    def Fontdir_Click(self, event=None):
        newfontdir = askdirectory(mustexist=1, initialdir=self.fontdir.get())
        if newfontdir != "" and newfontdir != ():
            self.fontdir.set(newfontdir.encode("utf-8"))
            self.settings.set('fontdir', self.fontdir.get())
            self.Ctrl_font_selected()

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
