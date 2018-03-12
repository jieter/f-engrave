from util import VERSION, OK, NOR, INV, NAN, position_window
from tooltip import ToolTip
from settings import CUT_TYPE_VCARVE

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
else:
    from Tkinter import *
    from tkFileDialog import *


class VCarveSettings(object):

    def __init__(self, master, settings):

        self.settings = settings

        # GUI callbacks
        self.Ctrl_entry_set = master.entry_set
        self.Ctrl_status_message = master.statusMessage
        self.Ctrl_calc_depth_limit = master.calc_depth_limit
        self.Ctrl_calculate_cleanup = master.Calculate_CLEAN_Click
        self.Ctrl_write_clean_file = master.Write_Clean_Click
        self.Ctrl_write_v_clean_file = master.Write_V_Clean_Click
        self.Ctrl_recalculation_required = master.Recalc_RQD
        self.Ctrl_calculate_v_carve = master.V_Carve_Calc_Click
        self.Ctrl_recalculate = master.Recalculate_Click

        # GUI Engraver callback
        self.Ctrl_init_clean_coords = master.engrave.init_clean_coords
        self.Ctrl_v_pplot_changed = master.engrave.refresh_v_pplot

        # V-Carve settings window
        self.width = 600
        self.height = 700
        self.vcarve_settings = Toplevel(width=self.width, height=self.height)
        self.vcarve_settings.withdraw()

        # Use grab_set to prevent user input in the main window during calculations
        self.vcarve_settings.grab_set()
        self.vcarve_settings.resizable(0, 0)
        self.vcarve_settings.title('V-Carve Settings')
        self.vcarve_settings.iconname("V-Carve Settings")

        self.units = StringVar()
        self.max_cut = StringVar()

        # V-Carve entries
        self.Entry_Vbitangle = Entry()
        self.Entry_Vbitdia = Entry()
        self.Entry_VDepthLimit = Entry()
        self.Entry_StepSize = Entry()
        self.Entry_Allowance = Entry()
        self.Entry_W_CLEAN = Entry()
        self.Entry_CLEAN_DIA = Entry()
        self.Entry_STEP_OVER = Entry()
        self.Entry_V_CLEAN = Entry()

        # V-Carve variables
        self.bit_shape = StringVar()
        self.v_bit_angle = StringVar()
        self.v_bit_dia = StringVar()
        self.v_depth_lim = StringVar()
        self.v_drv_corner = StringVar()
        self.v_step_corner = StringVar()
        self.v_step_len = StringVar()
        self.allowance = StringVar()
        self.v_max_cut = StringVar()
        self.v_rough_stk = StringVar()

        self.v_flop = BooleanVar()
        self.v_pplot = BooleanVar()
        self.inlay = BooleanVar()

        self.plotbox = BooleanVar()
        self.boxgap = StringVar()

        # clean vars
        self.clean_dia = StringVar()
        self.clean_step = StringVar()
        self.clean_v = StringVar()
        self.clean_name = StringVar()

        self.clean_P = BooleanVar()
        self.clean_X = BooleanVar()
        self.clean_Y = BooleanVar()
        self.v_clean_P = BooleanVar()
        self.v_clean_X = BooleanVar()
        self.v_clean_Y = BooleanVar()

        self.initialise_variables()
        self.create_widgets()
        self.create_icon()

        position_window(self.vcarve_settings, self.width, self.height)
        self.vcarve_settings.deiconify()

    def initialise_variables(self):
        self.units.set(self.settings.get('units'))
        self.max_cut.set('%.3g' % self.settings.get('max_cut'))

        self.bit_shape.set(self.settings.get('bit_shape'))
        self.v_bit_angle.set(self.settings.get('v_bit_angle'))
        self.v_bit_dia.set('%.3g' % self.settings.get('v_bit_dia'))
        self.v_depth_lim.set('%.3g' % self.settings.get('v_depth_lim'))
        self.v_drv_corner.set(self.settings.get('v_drv_corner'))
        self.v_step_corner.set(self.settings.get('v_step_corner'))
        self.v_step_len.set('%.3g' % self.settings.get('v_step_len'))
        self.allowance.set('%.3g' % self.settings.get('allowance'))
        self.v_rough_stk.set('%.3g' % self.settings.get('v_rough_stk'))
        self.v_max_cut.set('%.3g' % self.settings.get('v_max_cut'))

        self.v_flop.set(self.settings.get('v_flop'))
        self.v_pplot.set(self.settings.get('v_pplot'))
        self.inlay.set(self.settings.get('inlay'))
        self.plotbox.set(self.settings.get('plotbox'))
        self.boxgap.set('%.3g' % self.settings.get('boxgap'))

        self.clean_v.set('%.3g' % self.settings.get('clean_v'))
        self.clean_dia.set('%.3g' % self.settings.get('clean_dia'))
        self.clean_step.set('%.3g' % self.settings.get('clean_step'))
        self.clean_name.set(self.settings.get('clean_name'))

        self.clean_P.set(self.settings.get('clean_P'))
        self.clean_X.set(self.settings.get('clean_X'))
        self.clean_Y.set(self.settings.get('clean_Y'))
        self.v_clean_P.set(self.settings.get('v_clean_P'))
        self.v_clean_Y.set(self.settings.get('v_clean_Y'))
        self.v_clean_X.set(self.settings.get('v_clean_X'))

    def Close_Current_Window_Click(self):

        error_cnt = \
            self.Ctrl_entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(), 2) + \
            self.Ctrl_entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), 2)

        if error_cnt > 0:
            self.Ctrl_status_message.set(
                "Entry Error Detected: Check the entry values in the V-Carve Settings window")
        else:
            self.vcarve_settings.destroy()

    def create_widgets(self):

        vcarve_settings = self.vcarve_settings
        vcarve_settings.grid()

        self.vcarve_settings_upper = Frame(self.vcarve_settings)
        vcarve_settings_upper = self.vcarve_settings_upper

        self.vcarve_settings_lower = Frame(self.vcarve_settings)
        vcarve_settings_lower = self.vcarve_settings_lower

        w_label = 30
        w_entry = 5
        # w_units = 5
        w_radio = 10

        # V-Bit drawing
        self.vbit_picture()
        self.Label_photo = Label(vcarve_settings, image=self.PHOTO)

        # V-Bit shape
        self.cutter_type_frame = Frame(vcarve_settings_upper)
        self.Label_cutter_type = Label(self.cutter_type_frame, text="Cutter Type", width=w_label)
        self.Label_cutter_type.pack(side=LEFT, anchor=N)

        self.Radio_Type_VBIT = Radiobutton(self.cutter_type_frame, text="V-Bit", value="VBIT", width=w_radio, anchor=W)
        self.Radio_Type_VBIT.pack(side=TOP, anchor=E)
        self.Radio_Type_VBIT.configure(variable=self.bit_shape)

        self.Radio_Type_BALL = Radiobutton(self.cutter_type_frame, text="Ball Nose", value="BALL", width=w_radio,
                                           anchor=W)
        self.Radio_Type_BALL.pack(side=TOP, anchor=E)
        self.Radio_Type_BALL.configure(variable=self.bit_shape)

        self.Radio_Type_STRAIGHT = Radiobutton(self.cutter_type_frame, text="Straight", value="FLAT", width=w_radio,
                                               anchor=W)
        self.Radio_Type_STRAIGHT.pack(side=TOP, anchor=E)
        self.Radio_Type_STRAIGHT.configure(variable=self.bit_shape)

        self.bit_shape.trace_variable("w", self.Entry_Bit_Shape_var_Callback)

        # ...
        self.vbitangle_frame = Frame(vcarve_settings_upper)
        self.Label_Vbitangle = Label(self.vbitangle_frame, text="V-Bit Angle", width=w_label)
        self.Label_Vbitangle.pack(side=LEFT, anchor=W)
        self.Label_Vbitangle_u = Label(self.vbitangle_frame, text="deg", anchor=W)
        self.Label_Vbitangle_u.pack(side=RIGHT, anchor=W)
        self.Entry_Vbitangle = Entry(self.vbitangle_frame, width=w_entry)
        self.Entry_Vbitangle.pack(side=LEFT, anchor=W)
        self.Entry_Vbitangle.configure(textvariable=self.v_bit_angle)
        self.v_bit_angle.trace_variable("w", self.Entry_Vbitangle_Callback)

        self.vbitdia_frame = Frame(vcarve_settings_upper)
        self.Label_Vbitdia = Label(self.vbitdia_frame, text="V-Bit Diameter", width=w_label)
        self.Label_Vbitdia.pack(side=LEFT, anchor=W)
        self.Label_Vbitdia_u = Label(self.vbitdia_frame, textvariable=self.units, anchor=W)
        self.Label_Vbitdia_u.pack(side=RIGHT, anchor=W)
        self.Entry_Vbitdia = Entry(self.vbitdia_frame, width=w_entry)
        self.Entry_Vbitdia.pack(side=LEFT, anchor=W)
        self.Entry_Vbitdia.configure(textvariable=self.v_bit_dia)
        self.v_bit_dia.trace_variable("w", self.Entry_Vbitdia_Callback)

        self.vdepth_frame = Frame(vcarve_settings_upper)
        self.Label_VDepthLimit = Label(self.vdepth_frame, text="Cut Depth Limit", width=w_label)
        self.Label_VDepthLimit.pack(side=LEFT, anchor=W)
        self.Label_VDepthLimit_u = Label(self.vdepth_frame, textvariable=self.units, anchor=W)
        self.Label_VDepthLimit_u.pack(side=RIGHT, anchor=W)
        self.Entry_VDepthLimit = Entry(self.vdepth_frame, width=w_entry)
        self.Entry_VDepthLimit.pack(side=LEFT, anchor=W)
        self.Entry_VDepthLimit.configure(textvariable=self.v_depth_lim)
        self.v_depth_lim.trace_variable("w", self.Entry_VDepthLimit_Callback)

        self.maxcut_frame = Frame(vcarve_settings_upper)
        self.Label_maxcut = Label(self.maxcut_frame, text="Max Cut Depth", width=w_label)
        self.Label_maxcut.pack(side=LEFT, anchor=W)
        self.Label_maxcut_u = Label(self.maxcut_frame, textvariable=self.units, anchor=W)
        self.Label_maxcut_u.pack(side=RIGHT, anchor=W)
        self.Label_maxcut_i = Label(self.maxcut_frame, textvariable=self.max_cut, width=w_entry, anchor=W)
        self.Label_maxcut_i.pack(side=LEFT, anchor=W)

        self.stepsize_frame = Frame(vcarve_settings_upper)
        self.Label_StepSize = Label(self.stepsize_frame, text="Sub-Step Length", width=w_label)
        self.Label_StepSize.pack(side=LEFT, anchor=W)
        self.Label_StepSize_u = Label(self.stepsize_frame, textvariable=self.units, anchor=W)
        self.Label_StepSize_u.pack(side=RIGHT, anchor=W)
        self.Entry_StepSize = Entry(self.stepsize_frame, width=w_entry)
        self.Entry_StepSize.pack(side=LEFT, anchor=W)
        self.Entry_StepSize.configure(textvariable=self.v_step_len)
        self.v_step_len.trace_variable("w", self.Entry_StepSize_Callback)

        # Flip normals
        self.vflop_frame = Frame(vcarve_settings_lower)
        self.Label_v_flop = Label(self.vflop_frame, text="Flip Normals (Cut Outside)", width=w_label)
        self.Label_v_flop.pack(side=LEFT, anchor=W)
        self.Checkbutton_v_flop = Checkbutton(self.vflop_frame, text="", anchor=W)
        self.Checkbutton_v_flop.pack(side=LEFT, anchor=W)
        self.Checkbutton_v_flop.configure(variable=self.v_flop)
        self.v_flop.trace_variable("w", self.Entry_v_flop_Callback)

        self.vbox_frame = Frame(vcarve_settings_lower)
        self.Label_vBox = Label(self.vbox_frame, text="Add Box (Flip Normals)", width=w_label)
        self.Label_vBox.pack(side=LEFT, anchor=W)

        self.Checkbutton_plotbox = Checkbutton(self.vbox_frame, text="", anchor=W)
        self.Checkbutton_plotbox.pack(side=LEFT, anchor=W)
        self.Checkbutton_plotbox.configure(variable=self.plotbox)
        self.plotbox.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(self.vbox_frame, text="Box Gap", anchor=E)
        self.Label_BoxGap.pack(side=LEFT, padx=10, anchor=W)
        self.Entry_BoxGap = Entry(self.vbox_frame, width=w_entry)
        self.Entry_BoxGap.pack(side=LEFT, anchor=W)
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(self.vbox_frame, textvariable=self.units, anchor=W)
        self.Label_BoxGap_u.pack(side=LEFT, anchor=W)

        self.GEN_Reload = Button(self.vbox_frame, text="Recalculate")
        self.GEN_Reload.pack(side=RIGHT, padx=10, anchor=E)
        self.GEN_Reload.bind("<ButtonRelease-1>", self.recalculate_click)

        self.inlay_frame = Frame(vcarve_settings_lower)
        self.Label_inlay = Label(self.inlay_frame, text="Prismatic", width=w_label)
        self.Label_inlay.pack(side=LEFT, anchor=W)
        self.Checkbutton_inlay = Checkbutton(self.inlay_frame, text="", anchor=W)
        self.Checkbutton_inlay.pack(side=LEFT, anchor=W)
        self.Checkbutton_inlay.configure(variable=self.inlay)
        self.inlay.trace_variable("w", self.Entry_Prismatic_Callback)

        self.Label_inlay_right = Label(self.inlay_frame, text="(For inlay also select Add Box)", width=w_label)
        self.Label_inlay_right.pack(side=LEFT, anchor=W)

        self.allowance_frame = Frame(vcarve_settings_lower)
        self.Label_Allowance = Label(self.allowance_frame, text="Prismatic Overcut", width=w_label)
        self.Label_Allowance.pack(side=LEFT, anchor=W)
        self.Label_Allowance_u = Label(self.allowance_frame, textvariable=self.units, anchor=W)
        self.Label_Allowance_u.pack(side=RIGHT, anchor=W)
        self.Entry_Allowance = Entry(self.allowance_frame, width=w_entry)
        self.Entry_Allowance.pack(side=LEFT, anchor=W)
        self.Entry_Allowance.configure(textvariable=self.allowance)
        self.allowance.trace_variable("w", self.Entry_Allowance_Callback)

        # Update Idle tasks before requesting anything from winfo
        # vcarve_settings_lower.update_idletasks()

        # Multipass Settings

        self.Label_multipass = Label(vcarve_settings_lower, text="Multipass Cutting")

        # V-Carve finish pass stock
        self.v_rough_stk_frame = Frame(vcarve_settings_lower)
        self.Label_v_rough_stk = Label(self.v_rough_stk_frame, text="V-Carve Finish Pass Stock", width=w_label)
        self.Label_v_rough_stk.pack(side=LEFT, anchor=W)

        self.Entry_v_rough_stk = Entry(self.v_rough_stk_frame, width=w_entry)
        self.Entry_v_rough_stk.pack(side=LEFT, anchor=W)
        self.Entry_v_rough_stk.configure(textvariable=self.v_rough_stk)
        self.v_rough_stk.trace_variable("w", self.Entry_v_rough_stk_Callback)

        self.Label_v_rough_stk_u = Label(self.v_rough_stk_frame, textvariable=self.units, anchor=W)
        self.Label_v_rough_stk_u.pack(side=LEFT, anchor=W)

        self.Label_right_v_rough_stk = Label(self.v_rough_stk_frame, text="(Zero disables multipass cutting)", anchor=W)
        self.Label_right_v_rough_stk.pack(side=RIGHT, padx=10, anchor=W)

        # ...
        self.v_max_cut_frame = Frame(vcarve_settings_lower)
        self.Label_v_max_cut = Label(self.v_max_cut_frame, text="V-Carve Max Depth per Pass", width=w_label)
        self.Label_v_max_cut.pack(side=LEFT, anchor=W)
        self.Label_v_max_cut_u = Label(self.v_max_cut_frame, textvariable=self.units, anchor=W)
        self.Label_v_max_cut_u.pack(side=RIGHT, anchor=W)
        self.Entry_v_max_cut = Entry(self.v_max_cut_frame, width=w_entry)
        self.Entry_v_max_cut.pack(side=LEFT, anchor=W)
        self.Entry_v_max_cut.configure(textvariable=self.v_max_cut)
        self.v_max_cut.trace_variable("w", self.Entry_v_max_cut_Callback)

        # Cleanup Settings

        self.Label_clean = Label(vcarve_settings_lower, text="Cleanup Operations", width=w_label)

        self.clean_dia_frame = Frame(vcarve_settings_lower)
        self.CLEAN_Recalculate = Button(self.clean_dia_frame, text="Calculate\nCleanup",
                                        command=self.Ctrl_calculate_cleanup)
        self.CLEAN_Recalculate.pack(side=RIGHT, padx=10, anchor=E)

        self.Label_CLEAN_DIA = Label(self.clean_dia_frame, text="Cleanup Cut Diameter", width=w_label)
        self.Label_CLEAN_DIA.pack(side=LEFT, anchor=W)
        self.Label_CLEAN_DIA_u = Label(self.clean_dia_frame, textvariable=self.units, anchor=W)
        self.Label_CLEAN_DIA_u.pack(side=RIGHT, anchor=W)
        self.Entry_CLEAN_DIA = Entry(self.clean_dia_frame, width=w_entry)
        self.Entry_CLEAN_DIA.pack(side=LEFT, anchor=W)
        self.Entry_CLEAN_DIA.configure(textvariable=self.clean_dia)
        self.clean_dia.trace_variable("w", self.Entry_CLEAN_DIA_Callback)

        self.clean_step_over_frame = Frame(vcarve_settings_lower)
        self.Label_STEP_OVER = Label(self.clean_step_over_frame, text="Cleanup Cut Step Over", width=w_label)
        self.Label_STEP_OVER.pack(side=LEFT, anchor=W)
        self.Label_STEP_OVER_u = Label(self.clean_step_over_frame, text="%", anchor=W)
        self.Label_STEP_OVER_u.pack(side=RIGHT, anchor=W)
        self.Entry_STEP_OVER = Entry(self.clean_step_over_frame, width=w_entry)
        self.Entry_STEP_OVER.pack(side=LEFT, anchor=W)
        self.Entry_STEP_OVER.configure(textvariable=self.clean_step)
        self.clean_step.trace_variable("w", self.Entry_STEP_OVER_Callback)

        # Cleanup cut directions
        self.clean_directions_frame = Frame(vcarve_settings_lower)

        self.Label_clean_P = Label(self.clean_directions_frame, text="Cleanup Cut Directions", width=w_label)
        self.Label_clean_P.pack(side=LEFT, anchor=W)
        self.Write_Clean = Button(self.clean_directions_frame, text="Save Cleanup\nG-Code",
                                  command=self.Ctrl_write_clean_file)
        self.Write_Clean.pack(side=RIGHT, padx=10, anchor=E)

        self.Checkbutton_clean_P = Checkbutton(self.clean_directions_frame, text="P", anchor=W)
        self.Checkbutton_clean_P.configure(variable=self.clean_P)
        self.Checkbutton_clean_P.pack(side=LEFT, anchor=W)
        self.Checkbutton_clean_P_ToolTip = ToolTip(self.Checkbutton_clean_P,
                                                   text='Cut the perimeter of the uncut area.')
        self.clean_P.trace_variable("w", self.Checkbutton_clean_P_Callback)

        self.Checkbutton_clean_X = Checkbutton(self.clean_directions_frame, text="X", anchor=W)
        self.Checkbutton_clean_X.configure(variable=self.clean_X)
        self.Checkbutton_clean_X.pack(side=LEFT, anchor=W)
        self.clean_X.trace_variable("w", self.Checkbutton_clean_X_Callback)

        self.Checkbutton_clean_Y = Checkbutton(self.clean_directions_frame, text="Y", anchor=W)
        self.Checkbutton_clean_Y.configure(variable=self.clean_Y)
        self.Checkbutton_clean_Y.pack(side=LEFT, anchor=W)
        self.clean_Y.trace_variable("w", self.Checkbutton_clean_Y_Callback)

        # V-Bit Cleanup step
        self.v_cleanup_step_frame = Frame(vcarve_settings_lower)
        self.Label_V_CLEAN = Label(self.v_cleanup_step_frame, text="V-Bit Cleanup Step", width=w_label)
        self.Label_V_CLEAN.pack(side=LEFT, anchor=W)
        self.Label_V_CLEAN_u = Label(self.v_cleanup_step_frame, textvariable=self.units, anchor=W)
        self.Label_V_CLEAN_u.pack(side=RIGHT, anchor=W)
        self.Entry_V_CLEAN = Entry(self.v_cleanup_step_frame, width=w_entry)
        self.Entry_V_CLEAN.pack(side=LEFT, anchor=W)
        self.Entry_V_CLEAN.configure(textvariable=self.clean_v)
        self.clean_v.trace_variable("w", self.Entry_V_CLEAN_Callback)

        # V-Bit Cleanup directions
        self.v_clean_directions_frame = Frame(vcarve_settings_lower)
        self.Label_v_clean_P = Label(self.v_clean_directions_frame, text="V-Bit Cut Directions", width=w_label)
        self.Label_v_clean_P.pack(side=LEFT, anchor=W)

        self.Write_V_Clean = Button(self.v_clean_directions_frame, text="Save V Cleanup\nG-Code",
                                    command=self.Ctrl_write_v_clean_file)
        self.Write_V_Clean.pack(side=RIGHT, padx=10, anchor=E)

        self.Checkbutton_v_clean_P = Checkbutton(self.v_clean_directions_frame, text="P", anchor=W)
        self.Checkbutton_v_clean_P.configure(variable=self.v_clean_P)
        self.Checkbutton_v_clean_P.pack(side=LEFT, anchor=W)
        self.v_clean_P.trace_variable("w", self.Checkbutton_v_clean_P_Callback)

        self.Checkbutton_v_clean_X = Checkbutton(self.v_clean_directions_frame, text="X", anchor=W)
        self.Checkbutton_v_clean_X.configure(variable=self.v_clean_X)
        self.Checkbutton_v_clean_X.pack(side=LEFT, anchor=W)
        self.v_clean_X.trace_variable("w", self.Checkbutton_v_clean_X_Callback)

        self.Checkbutton_v_clean_Y = Checkbutton(self.v_clean_directions_frame, text="Y", anchor=W)
        self.Checkbutton_v_clean_Y.configure(variable=self.v_clean_Y)
        self.Checkbutton_v_clean_Y.pack(side=LEFT, anchor=W)
        self.v_clean_Y.trace_variable("w", self.Checkbutton_v_clean_Y_Callback)

        # Buttons
        self.button_frame = Frame(vcarve_settings_lower)
        self.VCARVE_Recalculate = Button(self.button_frame, text="Calculate V-Carve",
                                         command=self.vcarve_recalculate_click)
        self.VCARVE_Recalculate.pack(side=LEFT, padx=10, anchor=W)

        self.VCARVE_Close = Button(self.button_frame, text="Close", command=self.Close_Current_Window_Click)
        self.VCARVE_Close.pack(side=LEFT, padx=10, anchor=W)

        self.configure()

    def configure(self):

        vcarve_settings = self.vcarve_settings
        vcarve_settings.grid()

        vcarve_settings_upper = self.vcarve_settings_upper
        vcarve_settings_lower = self.vcarve_settings_lower

        padx = 10
        pady = 10

        self.cutter_type_frame.pack(side=TOP, anchor=W)
        self.vbitangle_frame.pack(side=TOP, anchor=W)
        self.vbitdia_frame.pack(side=TOP, anchor=W)
        self.vdepth_frame.pack(side=TOP, anchor=W)
        self.maxcut_frame.pack(side=TOP, anchor=W)
        self.stepsize_frame.pack(side=TOP, anchor=W)

        self.vcarve_separator1 = Frame(vcarve_settings_lower, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=W)

        self.vflop_frame.pack(side=TOP, anchor=W)
        self.vbox_frame.pack(side=TOP, anchor=W)

        self.vcarve_separator2 = Frame(vcarve_settings_lower, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator2.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=W)

        self.inlay_frame.pack(side=TOP, anchor=W)
        self.allowance_frame.pack(side=TOP, anchor=W)

        self.vcarve_separator3 = Frame(vcarve_settings_lower, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator3.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=W)
        self.Label_multipass.pack(side=TOP, anchor=CENTER)

        self.v_rough_stk_frame.pack(side=TOP, anchor=W)
        self.v_max_cut_frame.pack(side=TOP, anchor=W)

        self.vcarve_separator4 = Frame(vcarve_settings_lower, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator4.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=W)
        self.Label_clean.pack(side=TOP, anchor=CENTER)

        self.clean_dia_frame.pack(side=TOP, anchor=W)
        self.clean_step_over_frame.pack(side=TOP, anchor=W)
        self.clean_directions_frame.pack(side=TOP, anchor=W)
        self.v_cleanup_step_frame.pack(side=TOP, anchor=W)
        self.v_clean_directions_frame.pack(side=TOP, anchor=W)
        self.button_frame.pack(side=TOP, padx=padx, pady=pady, anchor=W)

        self.configure_Bit_Shape()
        self.configure_inlay()
        self.configure_plotbox()
        self.configure_rough_stk()
        self.configure_cut_type()

        vcarve_settings_upper.grid(row=0, column=0)
        self.Label_photo.grid(row=0, column=1)
        vcarve_settings_lower.grid(row=1, column=0, columnspan=2)

    def configure_cut_type(self):
        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.VCARVE_Recalculate.configure(state="normal", command=None)
        else:
            self.VCARVE_Recalculate.configure(state="disabled", command=None)

    def configure_rough_stk(self):
        if float(self.v_rough_stk.get()) == 0.0:
            self.Label_v_max_cut.configure(state="disabled")
            self.Label_v_max_cut_u.configure(state="disabled")
            self.Entry_v_max_cut.configure(state="disabled")
        else:
            self.Label_v_max_cut.configure(state="normal")
            self.Label_v_max_cut_u.configure(state="normal")
            self.Entry_v_max_cut.configure(state="normal")

    def configure_inlay(self):
        if bool(self.inlay.get()) is True:
            self.Label_Allowance.configure(state="normal")
            self.Entry_Allowance.configure(state="normal")
            self.Label_Allowance_u.configure(state="normal")
        else:
            self.Label_Allowance.configure(state="disabled")
            self.Entry_Allowance.configure(state="disabled")
            self.Label_Allowance_u.configure(state="disabled")

    def configure_plotbox(self):
        if bool(self.plotbox.get()) is True:
            self.Label_BoxGap.configure(state="normal")
            self.Entry_BoxGap.configure(state="normal")
            self.Label_BoxGap_u.configure(state="normal")
        else:
            self.Label_BoxGap.configure(state="disabled")
            self.Entry_BoxGap.configure(state="disabled")
            self.Label_BoxGap_u.configure(state="disabled")

    def configure_Bit_Shape(self):
        if self.bit_shape.get() == "VBIT":
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

    def check_all_variables(self, new=1):
        error_cnt = self.Ctrl_entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), new) + \
                    self.Ctrl_entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), new)
        return error_cnt

    # V-Carve Settings check and call-back methods

    def Entry_Vbitangle_Check(self):
        try:
            value = float(self.v_bit_angle.get())
            if value < 0.0 or value > 180.0:
                self.Ctrl_status_message.set(" Angle should be between 0 and 180 ")
                return INV
        except ValueError:
            return NAN
        return NOR

    def Entry_Vbitangle_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), setting='v_bit_angle')
        if self.Ctrl_calc_depth_limit():
            self.max_cut.set(self.settings.get('max_cut'))
        else:
            self.max_cut.set("error")

    def Entry_Vbitdia_Check(self):
        try:
            value = float(self.v_bit_dia.get())
            if value <= 0.0:
                self.Ctrl_status_message.set(" Diameter should be greater than 0 ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_Vbitdia_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), setting='v_bit_dia')
        if self.Ctrl_calc_depth_limit():
            self.max_cut.set(self.settings.get('max_cut'))
        else:
            self.max_cut.set("error")

    def Entry_VDepthLimit_Check(self):
        try:
            value = float(self.v_depth_lim.get())
            if value > 0.0:
                self.Ctrl_status_message.set(" Depth should be less than 0 ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_VDepthLimit_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), setting='v_depth_lim')
        if self.Ctrl_calc_depth_limit():
            self.max_cut.set(self.settings.get('max_cut'))
        else:
            self.max_cut.set("error")

    def Entry_StepSize_Check(self):
        try:
            value = float(self.v_step_len.get())
            if value <= 0.0:
                self.Ctrl_status_message.set(" Step size should be greater than 0 ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_StepSize_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(), setting='v_step_len')

    def Entry_v_flop_Callback(self, varName, index, mode):
        self.settings.set('v_flop', self.v_flop.get())
        self.Ctrl_recalculation_required()

    def Entry_Allowance_Check(self):
        try:
            value = float(self.allowance.get())
            if value > 0.0:
                self.Ctrl_status_message.set(" Allowance should be less than or equal to 0 ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_Allowance_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(), setting='allowance')

    def Entry_Prismatic_Callback(self, varName, index, mode):
        self.configure_inlay()
        self.settings.set('inlay', self.inlay.get())
        self.Ctrl_recalculation_required()

    def Entry_v_max_cut_Check(self):
        try:
            value = float(self.v_max_cut.get())
            # max depth is only relevant for multipass
            if float(self.v_rough_stk.get()) != 0 and value >= 0.0:
                self.Ctrl_status_message.set(" Max Depth per Pass should be less than 0.0 ")
                return INV
        except ValueError:
            return NAN
        return NOR

    def Entry_v_max_cut_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), setting='v_max_cut')

    def Entry_v_rough_stk_Check(self):
        try:
            value = float(self.v_rough_stk.get())
            if value < 0.0:
                self.Ctrl_status_message.set(" Finish Pass Stock should be positive or zero (Zero disables multi-pass)")
                return INV
        except ValueError:
            return NAN
        self.configure_rough_stk()
        return NOR

    def Entry_v_rough_stk_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(), setting='v_rough_stk')
        self.Ctrl_entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), setting='v_max_cut')

    def Entry_V_CLEAN_Check(self):
        try:
            value = float(self.clean_v.get())
            if value < 0.0:
                self.Ctrl_status_message.set(" Angle should be greater than 0.0 ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_V_CLEAN_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), setting='clean_v')

    def Entry_CLEAN_DIA_Check(self):
        try:
            value = float(self.clean_dia.get())
            if value <= 0.0:
                self.Ctrl_status_message.set(" Angle should be greater than 0.0 ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_CLEAN_DIA_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), setting='clean_dia')
        self.Ctrl_init_clean_coords()

    def Entry_STEP_OVER_Check(self):
        try:
            value = float(self.clean_step.get())
            if value <= 0.0:
                self.Ctrl_status_message.set(" Step Over should be between 0% and 100% ")
                return INV
        except ValueError:
            return NAN
        return OK

    def Entry_STEP_OVER_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), setting='clean_step')

    def Checkbutton_clean_P_Callback(self, varName, index, mode):
        self.settings.set('clean_P', self.clean_P.get())

    def Checkbutton_clean_X_Callback(self, varName, index, mode):
        self.settings.set('clean_X', self.clean_X.get())

    def Checkbutton_clean_Y_Callback(self, varName, index, mode):
        self.settings.set('clean_Y', self.clean_Y.get())

    def Checkbutton_v_clean_P_Callback(self, varName, index, mode):
        self.settings.set('v_clean_P', self.v_clean_P.get())

    def Checkbutton_v_clean_X_Callback(self, varName, index, mode):
        self.settings.set('v_clean_X', self.v_clean_X.get())

    def Checkbutton_v_clean_Y_Callback(self, varName, index, mode):
        self.settings.set('v_clean_Y', self.v_clean_Y.get())

    def Entry_v_pplot_Callback(self, varName, index, mode):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.Ctrl_v_pplot_changed()  # TODO only needed when plotting

    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
            if value <= 0.0:
                self.Ctrl_status_message.set(" Gap should be greater than zero.")
                return INV
        except:
            return NAN
        return OK

    def Entry_BoxGap_Callback(self, varName, index, mode):
        self.Ctrl_entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), setting='boxgap')
        self.configure_plotbox()

    def Entry_Box_Callback(self, varName, index, mode):
        self.Entry_BoxGap_Callback(varName, index, mode)
        self.settings.set('plotbox', self.plotbox.get())
        self.Ctrl_recalculation_required()

    def recalculate_click(self, event):
        self.check_all_variables()
        self.Ctrl_recalculate(event)

    def vcarve_recalculate_click(self):
        self.Ctrl_calculate_v_carve()
        self.vcarve_settings.withdraw()
        self.vcarve_settings.deiconify()
        self.vcarve_settings.grab_set()

    def Entry_Bit_Shape_var_Callback(self, varName, index, mode):
        self.configure_Bit_Shape()
        self.settings.set('bit_shape', self.bit_shape.get())
        if self.Ctrl_calc_depth_limit():
            self.max_cut.set('%.3g' % self.settings.get('max_cut'))
        else:
            self.max_cut.set("error")

    def vbit_picture(self):
        self.PHOTO = PhotoImage(format='gif',
                                data='R0lGODlhoABQAIABAAAAAP///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEK' +
                                     'AAEALAAAAACgAFAAAAL+jI+pBu2/opy02ouzvg+G7m3iSJam1XHpybbuezhk' +
                                     'CFNyjZ9AS+ff6gtqdq5eMUQUKlG4GwsYW0ptPiMGmkhOtwhtzioBd7nkqBTk' +
                                     'BV3LZe8Z7Vyzue75zL6t4zf6fa3vxxGoBDhIZViFKFKoeNeYwfjIJylHyWPJ' +
                                     'hPmkechZEmkJ6hk2GiFaqnD6qIpq1ur6WhnL+kqLaIuKO6g7yuvnywmMJ4xJ' +
                                     'PGdMidxmkpaFxDClTMar1ZA1hr0kTcecDUu0Exe0nacDy/D8ER17vgidugK+' +
                                     'zq7OHB5jXf1Onkpf311HXz1+1+gBs7ZAzcB57Aj+IPUFoUNC6CbCgKMGYa3+' +
                                     'cBjhBOtisUkzf2FCXjT5C+UTlSl7sQykMRQxhf8+RSxmrFrOKi9VXCwI7gbH' +
                                     'h/iCGgX56SAae3+AEg36FN0+qQt10BIHj1XMIk6xJZH3D+zXd1Yhab2ybaRR' +
                                     'sFXjVZR4JJOjCVtf6IQ2NuzUrt7KlrwUkB/NoXD35hM7tOZKvjy21v0D6NRI' +
                                     'xZBBKovzmCTPojeJao6WeFzmz6InjiYtmtBp1Jtb9/y8eoZA1nmkxaYt5LbZ' +
                                     'frhrx+29R7eNPq9JCzcVGTgdXLGLG7/qXHlCVcel+/Y5vGBRjWyR7n6OAtTs' +
                                     'b9otfwdPV9R4sgux3sN7NzHWjX8htQPSfW/UgYRL888KPAllP3jgX14GRpFP' +
                                     'O/85405YCZpRIIEQIsjRfAtStYgeAuUX34TwCajZYUkhJ6FizRgIgYggNlTd' +
                                     'EMR1Ux5q0Q2BoXUbTVQAADs=')

    def create_icon(self):
        try:
            vcarve_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                vcarve_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass
