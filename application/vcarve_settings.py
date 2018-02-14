from util import VERSION, OK, NOR, INV, NAN
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
        self.entry_set = master.entry_set
        self.statusMessage = master.statusMessage
        self.calc_depth_limit = master.calc_depth_limit
        self.Calculate_CLEAN_Click = master.Calculate_CLEAN_Click
        self.Write_Clean_Click = master.Write_Clean_Click
        self.Write_V_Clean_Click = master.Write_V_Clean_Click
        self.Recalc_RQD = master.Recalc_RQD
        self.recalculate_click = master.Recalculate_Click
        self.V_Carve_Calc_Click = master.V_Carve_Calc_Click
        # self.calc_depth_limit = master.calc_depth_limit

        # GUI Engraver callback
        self.init_clean_coords = master.engrave.init_clean_coords
        self.refresh_v_pplot = master.engrave.refresh_v_pplot

        # V-Carve settings window
        self.vcarve_settings = Toplevel(width=580, height=690)
        # Use grab_set to prevent user input in the main window during calculations
        self.vcarve_settings.grab_set()
        self.vcarve_settings.resizable(0, 0)
        self.vcarve_settings.title('V-Carve Settings')
        self.vcarve_settings.iconname("V-Carve Settings")

        # V-Carve entries
        self.Entry_Vbitangle = Entry()
        self.Entry_Vbitdia = Entry()
        self.Entry_VDepthLimit = Entry()
        self.Entry_InsideAngle = Entry()
        self.Entry_StepSize = Entry()
        self.Entry_Allowance = Entry()
        self.Entry_W_CLEAN = Entry()
        self.Entry_CLEAN_DIA = Entry()
        self.Entry_STEP_OVER = Entry()
        self.Entry_V_CLEAN = Entry()

        # V-Carve variables
        self.units = self.settings.get('units')
        # self.maxcut = self.settings.get('maxcut')
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

        # Derived variables
        # self.calc_depth_limit()

    def initialise_variables(self):
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

        self.v_flop.set(self.settings.get('v_flop'))
        self.v_pplot.set(self.settings.get('v_pplot'))
        self.inlay.set(self.settings.get('inlay'))
        self.plotbox.set(self.settings.get('plotbox'))
        self.boxgap.set(self.settings.get('boxgap'))

        self.clean_v.set(self.settings.get('clean_v'))
        self.clean_dia.set(self.settings.get('clean_dia'))
        self.clean_step.set(self.settings.get('clean_step'))
        self.clean_name.set(self.settings.get('clean_name'))

        self.clean_P.set(self.settings.get('clean_P'))
        self.clean_X.set(self.settings.get('clean_X'))
        self.clean_Y.set(self.settings.get('clean_Y'))
        self.v_clean_P.set(self.settings.get('v_clean_P'))
        self.v_clean_Y.set(self.settings.get('v_clean_Y'))
        self.v_clean_X.set(self.settings.get('v_clean_X'))

    def Close_Current_Window_Click(self):
        self.vcarve_settings.destroy()

    def create_widgets(self):

        vcarve_settings = self.vcarve_settings

        D_Yloc = 12
        D_dY = 24

        xd_label_L = 12
        w_label = 250
        w_entry = 60
        w_units = 35

        xd_entry_L = xd_label_L + w_label + 10
        xd_units_L = xd_entry_L + w_entry + 5

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
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), 2, 'v_bit_dia')

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
        self.Label_maxcut_i = Label(vcarve_settings, textvariable=self.v_max_cut, anchor=W)
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
        self.v_flop.trace_variable("w", self.Entry_v_flop_Callback)

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
        self.GEN_Reload.bind("<ButtonRelease-1>", self.recalculate_click)

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

        # Update Idle tasks before requesting anything from winfo
        vcarve_settings.update_idletasks()
        center_loc = int(float(vcarve_settings.winfo_width()) / 2)

        # Multipass Settings
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

        # Cleanup Settings
        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator1 = Frame(vcarve_settings, height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.place(x=0, y=D_Yloc, width=580, height=2)

        right_but_loc = int(vcarve_settings.winfo_width()) - 10
        width_cb = 100
        height_cb = 35

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_clean = Label(vcarve_settings, text="Cleanup Operations")
        self.Label_clean.place(x=center_loc, y=D_Yloc, width=w_label, height=21, anchor=CENTER)

        self.CLEAN_Recalculate = Button(vcarve_settings, text="Calculate\nCleanup", command=self.Calculate_CLEAN_Click)
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
        self.Checkbutton_clean_P_ToolTip = ToolTip(self.Checkbutton_clean_P,
                                                   text='Cut the perimeter of the uncut area.')
        self.clean_P.trace_variable("w", self.Checkbutton_clean_P_Callback)

        self.Checkbutton_clean_X = Checkbutton(vcarve_settings, text="X", anchor=W)
        self.Checkbutton_clean_X.configure(variable=self.clean_X)
        self.Checkbutton_clean_X.place(x=xd_entry_L + check_delta, y=D_Yloc, width=w_entry + 40, height=23)
        self.clean_X.trace_variable("w", self.Checkbutton_clean_X_Callback)

        self.Checkbutton_clean_Y = Checkbutton(vcarve_settings, text="Y", anchor=W)
        self.Checkbutton_clean_Y.configure(variable=self.clean_Y)
        self.Checkbutton_clean_Y.place(x=xd_entry_L + check_delta * 2, y=D_Yloc, width=w_entry + 40, height=23)
        self.clean_Y.trace_variable("w", self.Checkbutton_clean_Y_Callback)

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

        self.vbit_picture()
        self.Label_photo = Label(vcarve_settings, image=self.PHOTO)
        self.Label_photo.place(x=w_label + 150, y=40)
        self.Entry_Bit_Shape_Check()

        # Buttons
        Ybut = int(vcarve_settings.winfo_height()) - 30
        Xbut = int(vcarve_settings.winfo_width() / 2)

        self.VCARVE_Recalculate = Button(vcarve_settings, text="Calculate V-Carve",
                                         command=self.vcarve_recalculate_click)
        self.VCARVE_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")

        if self.settings.get('cut_type') == CUT_TYPE_VCARVE:
            self.VCARVE_Recalculate.configure(state="normal", command=None)
        else:
            self.VCARVE_Recalculate.configure(state="disabled", command=None)

        self.VCARVE_Close = Button(vcarve_settings, text="Close", command=vcarve_settings.destroy)
        self.VCARVE_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")

    # V-Carve Settings check and call-back methods

    def Entry_Vbitangle_Check(self):
        try:
            value = float(self.v_bit_angle.get())
            if value < 0.0 or value > 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return INV
        except:
            return NAN
        return NOR

    def Entry_Vbitangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), setting='v_bit_angle')
        self.calc_depth_limit()

    def Entry_Vbitdia_Check(self):
        try:
            value = float(self.v_bit_dia.get())
            if value <= 0.0:
                self.statusMessage.set(" Diameter should be greater than 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Vbitdia_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), setting='v_bit_dia')
        self.calc_depth_limit()

    def Entry_VDepthLimit_Check(self):
        try:
            value = float(self.v_depth_lim.get())
            if value > 0.0:
                self.statusMessage.set(" Depth should be less than 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_VDepthLimit_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), setting='v_depth_lim')
        self.calc_depth_limit()

    def Entry_InsideAngle_Check(self):
        try:
            value = float(self.v_drv_corner.get())
            if value <= 0.0 or value >= 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_InsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check())
        # TODO setting

    def Entry_StepSize_Check(self):
        try:
            value = float(self.v_step_len.get())
            if value <= 0.0:
                self.statusMessage.set(" Step size should be greater than 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_StepSize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(), setting='v_step_len')

    def Entry_v_flop_Callback(self, varName, index, mode):
        self.settings.set('v_flop', self.v_flop.get())
        self.Recalc_RQD()

    def Entry_Allowance_Check(self):
        try:
            value = float(self.allowance.get())
            if value > 0.0:
                self.statusMessage.set(" Allowance should be less than or equal to 0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_Allowance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(), setting='allowance')

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
        self.settings.set('inlay', self.inlay.get())
        self.Recalc_RQD()

    def Entry_v_max_cut_Check(self):
        try:
            value = float(self.v_max_cut.get())
            if value >= 0.0:
                self.statusMessage.set(" Max Depth per Pass should be less than 0.0 ")
                return INV
        except:
            return NAN
        return NOR

    def Entry_v_max_cut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), setting='v_max_cut')

    def Entry_v_rough_stk_Check(self):
        try:
            value = float(self.v_rough_stk.get())
            if value < 0.0:
                self.statusMessage.set(" Finish Pass Stock should be positive or zero (Zero disables multi-pass)")
                return INV
        except:
            return NAN
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
        return NOR

    def Entry_v_rough_stk_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(), setting='v_rough_stk')

    def Entry_V_CLEAN_Check(self):
        try:
            value = float(self.clean_v.get())
            if value < 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_V_CLEAN_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), setting='clean_v')

    def Entry_CLEAN_DIA_Check(self):
        try:
            value = float(self.clean_dia.get())
            if value <= 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_CLEAN_DIA_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), setting='clean_dia')
        self.init_clean_coords()

    def Entry_STEP_OVER_Check(self):
        try:
            value = float(self.clean_step.get())
            if value <= 0.0:
                self.statusMessage.set(" Step Over should be between 0% and 100% ")
                return INV
        except:
            return NAN
        return OK

    def Entry_STEP_OVER_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), setting='clean_step')

    def Checkbutton_clean_P_Callback(self, varName, index, mode):
        self.settings.set('clean_P', self.clean_P.get())

    def Checkbutton_clean_X_Callback(self, varName, index, mode):
        self.settings.set('clean_X', self.clean_X.get())

    def Checkbutton_clean_Y_Callback(self, varName, index, mode):
        self.settings.set('clean_Y', self.clean_Y.get())

    def Entry_Bit_Shape_Check(self):
        self.calc_depth_limit()

        try:
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
        except:
            pass

    # TODO same validation is part of General settings
    def Entry_v_pplot_Callback(self, varName, index, mode):
        self.settings.set('v_pplot', self.v_pplot.get())
        self.refresh_v_pplot()  # TODO only needed when plotting

    # TODO same validation is part of General settings
    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
            if value <= 0.0:
                self.statusMessage.set(" Gap should be greater than zero.")
                return INV
        except:
            return NAN
        return OK

    # TODO same validation is part of General settings
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

    # TODO same validation is part of General settings
    def Entry_Box_Callback(self, varName, index, mode):
        try:
            self.Entry_BoxGap_Callback(varName, index, mode)
        except:
            pass
        self.settings.set('plotbox', self.plotbox.get())
        self.Recalc_RQD()

    def vcarve_recalculate_click(self):

        self.V_Carve_Calc_Click()

        try:
            self.vcarve_settings.withdraw()
            self.vcarve_settings.deiconify()
            self.vcarve_settings.grab_set()
        except:
            pass

    def Entry_Bit_Shape_var_Callback(self, varName, index, mode):
        self.Entry_Bit_Shape_Check()
        self.settings.set('bit_shape', self.bit_shape.get())

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
