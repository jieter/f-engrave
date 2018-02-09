# from util import VERSION, OK, NOR, INV, NAN
from util import VERSION, OK, INV, NAN
# from tooltip import ToolTip

if VERSION == 3:
    from tkinter import *
else:
    from Tkinter import *


class BitmapSettings(object):
    """
    Algorithm options:
    -z, --turnpolicy policy    - how to resolve ambiguities in path decomposition
    -t, --turdsize n           - suppress speckles of up to this size (default 2)
    -a, --alphama n           - corner threshold parameter (default 1)
    -n, --longcurve            - turn off curve optimization
    -O, --opttolerance n       - curve optimization tolerance (default 0.2)
    """
    def __init__(self, master, settings):

        self.settings = settings

        # GUI callbacks
        self.entry_set = master.entry_set
        self.statusMessage = master.statusMessage
        self.Settings_ReLoad_Click = master.Settings_ReLoad_Click

        # Bitmap settings window
        self.bmp_settings = Toplevel(width=525, height=250)
        # Use grab_set to prevent user input in the main window during calculations
        self.bmp_settings.grab_set()
        self.bmp_settings.resizable(0, 0)
        self.bmp_settings.title('Bitmap Settings')
        self.bmp_settings.iconname("Bitmap Settings")

        # Bitmap entries
        self.Entry_BMPturdsize = Entry()
        self.Entry_BMPalphamax = Entry()
        self.Entry_BMPoptTolerance = Entry()

        # Bitmap variables
        self.bmp_turnpol = StringVar()
        self.bmp_turdsize = StringVar()
        self.bmp_alphamax = StringVar()
        self.bmp_longcurve = BooleanVar()
        self.bmp_opttolerance = StringVar()

        self.initialise_variables()
        self.create_widgets()
        self.create_icon()

    def initialise_variables(self):
        self.bmp_turnpol.set(self.settings.get('bmp_turnpol'))
        self.bmp_turdsize.set(self.settings.get('bmp_turdsize'))
        self.bmp_alphamax.set(self.settings.get('bmp_alphamax'))
        self.bmp_opttolerance.set(self.settings.get('bmp_opttolerance'))
        self.bmp_longcurve.set(self.settings.get('bmp_longcurve'))

    def Close_Current_Window_Click(self):
        self.bmp_settings.destroy()

    def create_widgets(self):

        bmp_settings = self.bmp_settings

        D_Yloc = 12
        D_dY = 24

        xd_label_L = 12
        w_label = 100
        w_entry = 60
        # w_units = 35
        xd_entry_L = xd_label_L + w_label + 10
        # xd_units_L = xd_entry_L+w_entry+5

        D_Yloc = D_Yloc + D_dY
        self.Label_BMPturnpol = Label(bmp_settings, text="Turn Policy")
        self.Label_BMPturnpol.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.BMPturnpol_OptionMenu = OptionMenu(bmp_settings, self.bmp_turnpol,
                                                "black", "white", "right", "left",
                                                "minority", "majority", "random")
        self.BMPturnpol_OptionMenu.place(x=xd_entry_L, y=D_Yloc, width=w_entry + 40, height=23)
        self.bmp_turnpol.trace_variable("w", self.Entry_BMPTurnpol_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_BMPturdsize = Label(bmp_settings, text="Turd Size")
        self.Label_BMPturdsize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPturdsize = Entry(bmp_settings, width="15")
        self.Entry_BMPturdsize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPturdsize.configure(textvariable=self.bmp_turdsize)
        self.bmp_turdsize.trace_variable("w", self.Entry_BMPturdsize_Callback)
        self.Label_BMPturdsize2 = Label(bmp_settings, text="Suppress speckles of up to this pixel size")
        self.Label_BMPturdsize2.place(x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 2)

        D_Yloc = D_Yloc + D_dY + 5
        self.Label_BMPalphamax = Label(bmp_settings, text="Alpha Max")
        self.Label_BMPalphamax.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPalphamax = Entry(bmp_settings, width="15")
        self.Entry_BMPalphamax.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPalphamax.configure(textvariable=self.bmp_alphamax)
        self.bmp_alphamax.trace_variable("w", self.Entry_BMPalphamax_Callback)
        self.Label_BMPalphamax2 = Label(bmp_settings, text="0.0 = sharp corners, 1.33 = smoothed corners")
        self.Label_BMPalphamax2.place(x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_BMP_longcurve = Label(bmp_settings, text="Long Curve")
        self.Label_BMP_longcurve.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_BMP_longcurve = Checkbutton(bmp_settings, text="", anchor=W)
        self.Checkbutton_BMP_longcurve.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_BMP_longcurve.configure(variable=self.bmp_longcurve)
        self.Label_BMP_longcurve2 = Label(bmp_settings, text="Enable Curve Optimization")
        self.Label_BMP_longcurve2.place(x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21)
        self.bmp_longcurve.trace_variable("w", self.Entry_BMPLongcurve_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_BMPoptTolerance = Label(bmp_settings, text="Opt Tolerance")
        self.Label_BMPoptTolerance.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPoptTolerance = Entry(bmp_settings, width="15")
        self.Entry_BMPoptTolerance.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPoptTolerance.configure(textvariable=self.bmp_opttolerance)
        self.bmp_opttolerance.trace_variable("w", self.Entry_BMPoptTolerance_Callback)
        self.Label_BMPoptTolerance2 = Label(bmp_settings, text="Curve Optimization Tolerance")
        self.Label_BMPoptTolerance2.place(x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2)

        bmp_settings.update_idletasks()
        Ybut = int(bmp_settings.winfo_height()) - 30
        Xbut = int(bmp_settings.winfo_width() / 2)

        self.PBM_Reload = Button(bmp_settings, text="Re-Load Image")
        self.PBM_Reload.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")
        self.PBM_Reload.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.PBM_Close = Button(bmp_settings, text="Close", command=self.Close_Current_Window_Click)
        self.PBM_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")

    # Bitmap check and callback methods

    def Entry_BMPturdsize_Check(self):
        try:
            value = float(self.bmp_turdsize.get())
            if value < 1.0:
                self.statusMessage.set(" Step size should be greater or equal to 1.0 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_BMPturdsize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), setting='bmp_turdsize')

    def Entry_BMPalphamax_Check(self):
        try:
            value = float(self.bmp_alphamax.get())
            if value < 0.0 or value > 4.0 / 3.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_BMPalphamax_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), setting='bmp_alphamax')

    def Entry_BMPTurnpol_Callback(self, varName, index, mode):
        self.settings.set('bmp_turnpol', self.bmp_turnpol.get())

    def Entry_BMPLongcurve_Callback(self, varName, index, mode):
        self.settings.set('bmp_longcurve', self.bmp_longcurve.get())

    def Entry_BMPoptTolerance_Check(self):
        try:
            value = float(self.bmp_opttolerance.get())
            if value < 0.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return INV
        except:
            return NAN
        return OK

    def Entry_BMPoptTolerance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), setting='bmp_opttolerance')

    def create_icon(self):
        try:
            bmp_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                bmp_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass
