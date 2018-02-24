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

        error_cnt = \
            self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2) + \
            self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 2) + \
            self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 2)

        if error_cnt > 0:
            self.statusMessage.set(
                "Entry Error Detected: Check the entry values in the Bitmap Settings window")
        else:
            self.bmp_settings.destroy()

    def create_widgets(self):

        bmp_settings = self.bmp_settings

        w_label = 15
        w_tip = 40
        w_entry = 5

        self.turnpol_frame = Frame(bmp_settings)
        self.Label_BMPturnpol = Label(self.turnpol_frame, text="Turn Policy", width=w_label)
        self.Label_BMPturnpol.pack(side=LEFT, anchor=W)
        self.BMPturnpol_OptionMenu = OptionMenu(self.turnpol_frame, self.bmp_turnpol,
                                                "black", "white", "right", "left",
                                                "minority", "majority", "random")
        self.BMPturnpol_OptionMenu.pack(side=RIGHT)
        self.bmp_turnpol.trace_variable("w", self.Entry_BMPTurnpol_Callback)

        self.turdsize_frame = Frame(bmp_settings)
        self.Label_BMPturdsize = Label(self.turdsize_frame, text="Turd Size", width=w_label)
        self.Label_BMPturdsize.pack(side=LEFT, anchor=W)
        self.Entry_BMPturdsize = Entry(self.turdsize_frame, width=w_entry)
        self.Entry_BMPturdsize.pack(side=LEFT, anchor=W)
        self.Entry_BMPturdsize.configure(textvariable=self.bmp_turdsize)
        self.bmp_turdsize.trace_variable("w", self.Entry_BMPturdsize_Callback)
        self.Label_BMPturdsize2 = Label(self.turdsize_frame, text="Suppress speckles of up to this pixel size", width=w_tip)
        self.Label_BMPturdsize2.pack(side=RIGHT)
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 2)

        self.alphamax_frame = Frame(bmp_settings)
        self.Label_BMPalphamax = Label(self.alphamax_frame, text="Alpha Max", width=w_label)
        self.Label_BMPalphamax.pack(side=LEFT, anchor=W)
        self.Entry_BMPalphamax = Entry(self.alphamax_frame, width=w_entry)
        self.Entry_BMPalphamax.pack(side=LEFT, anchor=W)
        self.Entry_BMPalphamax.configure(textvariable=self.bmp_alphamax)
        self.bmp_alphamax.trace_variable("w", self.Entry_BMPalphamax_Callback)
        self.Label_BMPalphamax2 = Label(self.alphamax_frame, text="0.0 = sharp corners, 1.33 = smoothed corners", width=w_tip)
        self.Label_BMPalphamax2.pack(side=RIGHT)
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 2)

        self.longcurve_frame = Frame(bmp_settings)
        self.Label_BMP_longcurve = Label(self.longcurve_frame, text="Long Curve", width=w_label)
        self.Label_BMP_longcurve.pack(side=LEFT, anchor=W)
        self.Checkbutton_BMP_longcurve = Checkbutton(self.longcurve_frame, text="", anchor=W)
        self.Checkbutton_BMP_longcurve.pack(side=LEFT, anchor=W)
        self.Checkbutton_BMP_longcurve.configure(variable=self.bmp_longcurve)
        self.Label_BMP_longcurve2 = Label(self.longcurve_frame, text="Enable Curve Optimization", width=w_tip)
        self.Label_BMP_longcurve2.pack(side=RIGHT)
        self.bmp_longcurve.trace_variable("w", self.Entry_BMPLongcurve_Callback)

        self.tolerance_frame = Frame(bmp_settings)
        self.Label_BMPoptTolerance = Label(self.tolerance_frame, text="Opt Tolerance", width=w_label)
        self.Label_BMPoptTolerance.pack(side=LEFT, anchor=W)
        self.Entry_BMPoptTolerance = Entry(self.tolerance_frame, width=w_entry)
        self.Entry_BMPoptTolerance.pack(side=LEFT, anchor=W)
        self.Entry_BMPoptTolerance.configure(textvariable=self.bmp_opttolerance)
        self.bmp_opttolerance.trace_variable("w", self.Entry_BMPoptTolerance_Callback)
        self.Label_BMPoptTolerance2 = Label(self.tolerance_frame, text="Curve Optimization Tolerance", width=w_tip)
        self.Label_BMPoptTolerance2.pack(side=RIGHT)
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2)

        self.button_frame = Frame(bmp_settings)
        self.PBM_Reload = Button(self.button_frame, text="Re-Load Image")
        self.PBM_Reload.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)
        self.PBM_Reload.pack(side=LEFT)

        self.PBM_Close = Button(self.button_frame, text="Close", command=self.Close_Current_Window_Click)
        self.PBM_Close.pack(side=RIGHT)

        pady = 5

        self.turnpol_frame.pack(side=TOP, anchor=W, pady=pady)
        self.turdsize_frame.pack(side=TOP, anchor=W, pady=pady)
        self.alphamax_frame.pack(side=TOP, anchor=W, pady=pady)
        self.longcurve_frame.pack(side=TOP, anchor=W, pady=pady)
        self.tolerance_frame.pack(side=TOP, anchor=W, pady=pady)
        self.button_frame.pack(side=BOTTOM, anchor=CENTER, pady=pady * 2)

        bmp_settings.update_idletasks()

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
