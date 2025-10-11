# -*- coding: utf-8 -*-
"""
@author: Herodirk

Hero UI Manager
A module containing functions to assit in the creation and management of Tkinter windows and Tkinter variables
"""

import tkinter as tk
from tkinter import ttk
import numpy as np


color_palettes = {
    "dark": {
        "background": "black",
        "frame_background": "#313338",
        "controls_frame": "dim gray",
        "widget_background": "#383A40",
        "widget_border": "#2E3035",
        "active_background": "#2E3035",
        "text": "white",
        "selected_text": "black",
        "selection": "light gray"
    },
    "dark_red": {
        "background": "black",
        "frame_background": "#100808",
        "controls_frame": "#662626",
        "widget_background": "#441313",
        "widget_border": "#2C0C0C",
        "active_background": "#2C0C0C",
        "text": "white",
        "selected_text": "black",
        "selection": "light gray"
    },
    "light": {
        "background": "black",
        "frame_background": "#FFFFFF",
        "controls_frame": "#FFCF4B",
        "widget_background": "#FFCA8E",
        "widget_border": "#FF9E4F",
        "active_background": "#FF9E4F",
        "text": "black",
        "selected_text": "black",
        "selection": "light gray"
    },
    "gray_text": {
        "background": "black",
        "frame_background": "#200808",
        "controls_frame": "#662626",
        "widget_background": "#541313",
        "widget_border": "#3C0C0C",
        "active_background": "#3C0C0C",
        "text": "gray",
        "selected_text": "black",
        "selection": "light gray"
    }
}


#%% Hero UI Manager

class H_UI_M():
    def __init__(self, main, version, windowTitle, windowWidth, windowHeight, palette="dark"):
        """
        Hk: Hero UI Manager, main class for Hero UI Manager functions
        Initializes Hero UI Manager. Sets the chosen color palette. Configures the main window. Creates dict variables for storage of switches and frames.

        Parameters
        ----------
        main : root
            Root of the Tkinter application that Hero UI Manager is being used for.
        windowTitle : str
            Title of the main window.
        windowWidth : int
            Width of the main window.
        windowHeight : int
            Height of the main window.
        palette : str, optional
            Key for the color palette for the application. Choose from the dict color_palettes. The default is "dark".

        Returns
        -------
        None.

        """
        self.main = main
        self.version = version
        self.main.title(windowTitle)
        self.main.colors = color_palettes[palette]
        self.main.configure(width=windowWidth, height=windowHeight, background=self.main.colors["background"])
        self.main.tk_setPalette(activeBackground=self.main.colors["active_background"],
                                foreground=self.main.colors["text"],
                                selectColor=self.main.colors["widget_background"],
                                activeForeground=self.main.colors["text"],
                                highlightBackground=self.main.colors["widget_border"],
                                background=self.main.colors["widget_background"],
                                selectBackground=self.main.colors["selection"],
                                selectForeground=self.main.colors["selected_text"],
                                )

        self.main.switches = {}
        self.main.frames = {}
        self.main.var_dict = {}
        self.edit_vars_active = False

        self.style = ttk.Style()
        self.style.theme_create(
            "minion_calculator", parent="clam",
            settings={
                "TCombobox": {
                    "configure": {
                        "background": self.main.colors["frame_background"],
                        "fieldbackground": self.main.colors["widget_background"],
                        "foreground": self.main.colors["text"],
                        "selectbackground": self.main.colors["widget_background"],
                        "selectforeground": self.main.colors["text"],
                        "arrowcolor": self.main.colors["text"],
                        "lightcolor": self.main.colors["widget_border"],
                        "darkcolor": self.main.colors["frame_background"],
                        "bordercolor": self.main.colors["widget_border"],
                        "padding": 5
                    }
                },
                "Vertical.TScrollbar" : {
                    "configure": {
                        "arrowcolor": self.main.colors["text"],
                        "background": self.main.colors["widget_border"],
                        "bordercolor": self.main.colors["widget_background"],
                        "troughcolor": self.main.colors["frame_background"],
                    }
                }
            }
        )
        self.style.theme_use('minion_calculator')
        return

    def createControls(self, relControlsHeight=0.07):
        """
        Saves and places controls frame with Stop button.

        Parameters
        ----------
        relControlsHeight : float, optional
            Relative height of the control frame in the main window. Float between 0 and 1. The default is 0.07.

        Returns
        -------
        None.

        """
        self.main.frames["controls"] = tk.Frame(self.main, background=self.main.colors["controls_frame"])
        self.main.frames["controls"].place(rely=1 - relControlsHeight, relwidth=1, relheight=relControlsHeight)

        self.main.stopB = tk.Button(self.main.frames["controls"], text='Stop', command=self.main.quit)
        self.main.stopB.place(relx=0.99, rely=0.5, anchor="e")
        return

    def createFrames(self, parent, frame_keys=[], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0.07):
        """
        Saves and places frames according to inputted matrix.
        Maxtric can be any size. Fill empty spaces with None.

        Parameters
        ----------
        parent : Tk object
            parent object of the frames
        frame_keys : list
            2 dimensional array of frame keys as strings. The default is [].
            [
                [column 1 row 1, column 2 row 1],
                [column 1 row 2, column 2 row 2],
            ]
        grid_frames : bool, optional
            Toggle to add a frame in each frame named {frame name}_grid acting as a default translation for widgets. The default is True.
        grid_size : float, optional
            Relative size of grid frame in the parent frame. Float between 0 and 1. The default is 0.96.
        border : float, optional
            Relative size of the border thickness in the main window. Float between 0 and 1. The default is 0.01.
        controls : bool, optional
            Toggle for giving the parent frame a controls frame
        relControlsHeight : float, optional
            Relative height of the control frame in the main window. Float between 0 and 1. The default is 0.07.
            Can be set to 0 if Control frame was not used

        Returns
        -------
        None.

        """
        self.main.frame_amount = np.size(frame_keys)
        rel_w = 1 / max([len(frame_keys[i]) for i in range(len(frame_keys))])
        rel_h = (1 - relControlsHeight) / len(frame_keys)
        for row_loc, row_keys in enumerate(frame_keys):
            for col_loc, key in enumerate(row_keys):
                if key is not None:
                    self.main.frames[key] = tk.Frame(parent, background=self.main.colors["frame_background"])
                    self.main.frames[key].place(rely=row_loc * rel_h + 0.5 * border, relx=rel_w * col_loc + 0.5 * border, relwidth=rel_w - border, relheight=rel_h - border)
                    if grid_frames:
                        self.main.frames[key + "_grid"] = tk.Frame(self.main.frames[key], background=self.main.colors["frame_background"])
                        self.main.frames[key + "_grid"].place(rely=1 - grid_size, relx=1 - grid_size, relwidth=grid_size, relheight=grid_size)
        return

    def genLabel(self, frm, txt, txtvar=False):
        """
        genLabel: generate label
        Generates a label object in the specified frame with the specified text
        Background color is set to the same color used for frames in the palette.
        If txtvar is set to True, it will make a variable label with txt as the variable.

        Parameters
        ----------
        frm : tk.Frame
            Frame where the label will be generated in.
        txt : str or something parsable as string
            Text or variable that will be used in the label.
        txtvar : bool, optional
            Toggle for if the inputted txt is a variable or not. The default is False.

        Returns
        -------
        tk.Label
            Fully constructed label ready to be placed.

        """
        if txtvar:
            return tk.Label(frm, textvariable=txt, background=self.main.colors["frame_background"])
        else:
            return tk.Label(frm, text=txt, background=self.main.colors["frame_background"])

    def defVar(self, dtype, initial=None):
        """
        defVar: define variable
        Generate Tkinter variable for booleans, integers, strings or floats with an optional initial value.

        Parameters
        ----------
        dtype : type
            Data type for the Tkinter variable. Accepted options are bool, int, str or float.
        initial : something of type dtype, optional
            Inital value for the Tkinter variable. Set to None for default initial value. The default is None.

        Returns
        -------
        var : tk.BooleanVar, tk.IntVar, tk.StringVar or tk.DoubleVar
            Fully constructed Tkinter variable ready for use.

        """
        if dtype == bool:
            var = tk.BooleanVar(self.main)
        elif dtype == int:
            var = tk.IntVar(self.main)
        elif dtype == str:
            var = tk.StringVar(self.main)
        elif dtype == float:
            var = tk.DoubleVar(self.main)
        if initial is not None:
            var.set(initial)
        return var

    def defVarI(self, dtype, frame, L_text, initial=None, options=[], cmd=None, checkbox_text=None):
        """
        defVarI: define variable input
        Generates a Tkinter variable, a label and an input widget.
        The type of input widget can be influenced by the function arguments:
            if no options are provided, it will be a text input box
            if dtype is bool, it will be a checkbox

        Parameters
        ----------
        dtype : type
            Data type for the Tkinter variable. Accepted options are bool, int, str or float.
        frame : tk.Frame
            Frame where the label and input widget will be generated in.
        L_text : str
            String used for the label.
        initial : something of type dtype, optional
            Inital value for the Tkinter variable. Set to None for default initial value. The default is None.
        options : list, optional
            List of options for an option menu. List must contain items of type dtype. The default is [].
        cmd : function, optional
            Function that runs when an option in the option menu is. The default is None.
        checkbox_text : str, optional
            Text that will be displayed next to the checkbox if dtype is bool

        Returns
        -------
        var : tk.BooleanVar, tk.IntVar, tk.StringVar or tk.DoubleVar
            Fully constructed Tkinter variable ready for use.
        list
            List containing the label and the input widget.

        """
        var = self.defVar(dtype, initial=initial)
        if dtype != bool:
            if len(options) != 0:
                entry = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=1 + len(str(max(options, key=lambda x: len(str(x))))), height=20)
                if cmd is not None:
                    entry.bind('<<ComboboxSelected>>', lambda void_event: cmd(var.get()))
            else:
                entry = tk.Entry(frame, textvariable=var)
        else:
            entry = tk.Checkbutton(frame, variable=var, background=self.main.colors["frame_background"], command=cmd)
            if checkbox_text is not None:
                entry.configure(text=checkbox_text)
        label = self.genLabel(frm=frame, txt=L_text)
        return var, [label, entry]

    def defVarO(self, frame, dtype, L_text, initial=None):
        """
        defVarO: define variable output
        Generates a Tkinter variable, a label and an variable label.
        The variable label is connected to the Tkinter variable.

        Parameters
        ----------
        frame : tk.Frame
            Frame where the label and output widget will be generated in.
        dtype : type
            Data type for the Tkinter variable. Accepted options are bool, int, str or float.
        L_text : str
            String used for the label.
        initial : something of type dtype, optional
            Inital value for the Tkinter variable. Set to None for default initial value. The default is None.

        Returns
        -------
        var : tk.BooleanVar, tk.IntVar, tk.StringVar or tk.DoubleVar
            Fully constructed Tkinter variable ready for use.
        list
            List containing the label and the variable label.

        """
        var = self.defVar(dtype, initial=initial)
        text_label = self.genLabel(frm=frame, txt=L_text)
        var_label = self.genLabel(frm=frame, txt=var, txtvar=True)
        return var, [text_label, var_label]

    def defListO(self, frame, L_text, w=None, h=None):
        """
        defListO: define list output
        Generates a Tkinter variable, a label and a list box.
        The list box is connected to the Tkinter variable.

        Parameters
        ----------
        frame : tk.Frame
            Frame where the label and output widget will be generated in.
        L_text : str
            String used for the label.
        w : int, optional
            Width of the list box. None for default size. The default is None.
        h : int, optional
            Height of the list box. None for default size. The default is None.

        Returns
        -------
        var : tk.BooleanVar, tk.IntVar, tk.StringVar or tk.DoubleVar
            Fully constructed Tkinter variable ready for use.
        list
            List containing the label and the list box.

        """
        var = self.defVar(str, initial=[])
        text_label = self.genLabel(frm=frame, txt=L_text)
        output_list = tk.Listbox(frame, listvariable=var)
        if w is not None:
            output_list.configure(width=w)
        if h is not None:
            output_list.configure(height=h)
        return var, [text_label, output_list]

    def fill_grid(self, grid_arr, grid_frame, stick='w'):
        """
        Places widgets in a grid according to the inputted matrix.

        Parameters
        ----------
        grid_arr : list
            2 dimensional array of widgets.\n
            [\n
                [column 1 row 1, column 2 row 1],\n
                [column 1 row 2, column 2 row 2],
            ]
        frame : tk.Frame
            Frame where the label and output widget will be generated in.
        stick : str
            First letter letter of a cardinal direction for which side to align the widgets to. 'n', 'e', 's', 'w'.

        Returns
        -------
        None.

        """
        for rowindex, row in enumerate(grid_arr):
            for colindex, col in enumerate(row):
                if col is None:
                    self.genLabel(frm=grid_frame, txt="").grid(row=rowindex, column=colindex)
                    continue
                col.grid(row=rowindex, column=colindex, sticky=stick)
        return

    def fill_arr(self, arr, frame, anc="w", rel_start=[0.01, 0.5], rel_next=[1, 0.5], abs_next=[10, 0]):
        """
        fill_arr: fill array
        Places widget in a row according to the inputted array.

        Parameters
        ----------
        arr : list
            1 dimensional array of widgets.
        frame : tk.Frame
           Frame where the label and output widget will be generated in.
        anc : str, optional
            Anchor for the attachment point of the next widget on the previous widget.
            Accepted options are the cardinal directions as one letter n, e, s, w.
            This is the opposite direction of where to the array will be placed.
            The default is "w".
        rel_start : list, optional
            List of relative x,y coordinates indicating the starting position relative in the frame.
            The default is [0.01, 0.5].
        rel_next : list, optional
            List of relative x,y coordinates indicating the position of the next widget anchor relative to the previous widget anchor.
            The default is [1, 0.5].
        abs_next : list, optional
            List of absolute x,y coordinates indicating an extra translation of the new widget anchor.
            The default is [10, 0].

        Returns
        -------
        None.

        """
        prev_widget = arr[0]
        for widget in arr:
            if widget == prev_widget:
                widget.place(relx=rel_start[0], rely=rel_start[1], anchor=anc)
            else:
                widget.place(in_=prev_widget, relx=rel_next[0], x=abs_next[0], rely=rel_next[1], y=abs_next[1], anchor=anc)
            prev_widget = widget

    def defSwitch(self, ID, obj, loc, control=None, negate=False, initial=True):
        """
        defSwitch: define switch
        Creates an entry in the switches dict used for turning widgets on and off.
        The entry is saved under an ID and has the following items:
            the current visibility state as a boolean\n
            a reference to the widget itself\n
            the location of the widget\n
            a control variable to determine if the widget should show or disappear\n
            a boolean to reverse the relation with the control

        Parameters
        ----------
        ID : str
            ID for the switch to call it with toggleSwitch.
        obj : any Tkinter widget or list of widgets
            The objects that will be part of the switch, can be one singular widget or a list of widgets.
        loc : "grid", dict or list
            Location of the widget, "grid" if the widget is part of a grid, a dictionary with arguments for .place() or
            a list of dictionaries for multiple objects.
            If obj and loc are lists, they should be the same length
        control : str, int, float, optional
            Control variable to determine if the widget should be visible or not. None if there is not control. The default is None.
        negate : bool, optional
            Boolean to reverse the relation with the control. The default is False.
        initial : bool, optional
            Initial state of the visibility of the widget.
            For widgets in a grid, it assumes that they are already placed, so initial==True would not do anything extra.
            For widgets outside a grid, it assumes that they are not placed yet, so initial==False would not do anything extra.
            The default is True.

        Returns
        -------
        None.

        """
        self.main.switches[ID] = {"state": initial, "obj": obj, "loc": loc, "control": control, "negate": negate}
        if loc != "grid" and initial is True:
            obj.place(**loc)
        if loc == "grid" and initial is False:
            for widget in obj:
                widget.grid_remove()
        return

    def toggleSwitch(self, ID, control=None):
        """
        Toggles a switch by ID and check if control conditions are met

        Parameters
        ----------
        ID : str
            Identifier of the switch.
        control : str, int, float, optional
            Control variable to determine if the widget should be visible or not. None to force a switch. The default is None.

        Returns
        -------
        None.

        """
        try:
            state = self.main.switches[ID]["state"]
        except Exception as error:
            print("Error: toggleSwitch, ID does not exist")
            print(error)
            return
        if control is not None:
            if self.main.switches[ID]["negate"]:
                if state is not (control == self.main.switches[ID]["control"]):
                    return
            else:
                if state is (control == self.main.switches[ID]["control"]):
                    return
        if type(self.main.switches[ID]["obj"]) == list:
            objs = self.main.switches[ID]["obj"]
        else:
            objs = [self.main.switches[ID]["obj"]]
        if type(self.main.switches[ID]["loc"]) == list:
            locs = self.main.switches[ID]["loc"]
        else:
            locs = [self.main.switches[ID]["loc"]]
        if state is True:
            if self.main.switches[ID]["loc"] == "grid":
                for obj in objs:
                    obj.grid_remove()
            else:
                for obj in objs:
                    obj.place_forget()
            self.main.switches[ID]["state"] = False
        else:
            if self.main.switches[ID]["loc"] == "grid":
                for obj in objs:
                    obj.grid()
            else:
                for obj, loc in zip(objs, locs):
                    obj.place(**loc)
            self.main.switches[ID]["state"] = True
        return

    def createSwitchCall(self, ID, controlvar=None):
        """
        Creates a command for a GUI widget that calls a switch.

        Parameters
        ----------
        ID : str
            Identifier of the switch.
        controlvar : str or None
            Variable key for the switch control. "self" to make the command send the value in the widget as control. None to force a switch. The default is None.

        Returns
        -------
        lambda function
            Command for a GUI widget that calls a switch

        """
        if controlvar == "self":
            return lambda x: self.toggleSwitch(ID, x)
        elif controlvar is None:
            return lambda: self.toggleSwitch(ID, None)
        elif self.version == "MINION":
            return lambda: self.toggleSwitch(ID, self.main.variables[controlvar]["var"].get())
        else:
            return lambda: self.toggleSwitch(ID, self.main.var_dict[controlvar].get())

    def createShowHideToggle(self, parent_var_key, ID, place_args={"relx": 1, "x": 3, "rely": 0.5, "anchor": 'w'}):
        """
        Creates and places a button that forces a switch, or runs any inputted function.

        Parameters
        ----------
        parent_var_key : str
            Variable key of the widget where the button should anchor to.
        ID : str or function
            As string it's the identifier of the switch. As function it is any function.
        place_args : dict
            Dictionary containing the arguments for the .place function of Tkinter.
            Default is {"relx": 1, "x": 3, "rely": 0.5, "anchor": 'w'}

        Returns
        -------
        None.
        """
        if self.version == "MINION":
            button_frame = self.main.variables[parent_var_key]["frame"]
        else:
            button_frame = self.main.var_dict[parent_var_key].frame
        if type(ID) is str:
            button = tk.Button(self.main.frames[button_frame], text="Toggle extra options", border=0, borderwidth=0, command=self.createSwitchCall(ID))
        elif str(type(ID)) == "<class 'function'>":
            button = tk.Button(self.main.frames[button_frame], text="Toggle extra options", border=0, borderwidth=0, command=ID)
        if place_args is None:
            return button
        if self.version == "MINION":
            button_anchor = self.main.variables[parent_var_key]["widget"][-1]
        else:
            button_anchor = self.main.var_dict[parent_var_key].widget[-1]
        button.place(in_=button_anchor, **place_args)
        return

    def input_args(self, func, execute=False):
        """
        Creates a new Tkinter window that asks for inputs for a chosen function.
        That function can be executed.

        Parameters
        ----------
        func : function
            Function with arguments.
        execute : bool, optional
            Toggle for executing the function after arguments are given. The default is False.

        Returns
        -------
        list
            List of inputted arguments. Returns None if function got executed.

        """
        self.arguments = []
        inputsW = tk.Toplevel(self.main)
        inputsW.title("Input function arguments")

        inputsW.optionsF = tk.Frame(inputsW)
        inputsW.optionsF.place(relx=0.5, rely=0.9, relheight=0.1, relwidth=1, anchor="n")

        inputsW.inputsF = tk.Frame(inputsW)
        inputsW.inputsF.place(relx=0, rely=0, relheight=0.89, relwidth=1, anchor="nw")

        amount_args = func.__code__.co_argcount
        args = func.__code__.co_varnames[:amount_args]
        defaults = func.__defaults__

        widgets_dict = {}
        taken_intputs = {}
        for index, argument in enumerate(args):
            if argument == "self":
                continue
            if type(defaults[index - 1]) == int:
                taken_intputs[argument] = tk.IntVar(inputsW, value=defaults[index - 1])
            elif type(defaults[index - 1]) == float:
                taken_intputs[argument] = tk.DoubleVar(inputsW, value=defaults[index - 1])
            elif type(defaults[index - 1]) == str:
                taken_intputs[argument] = tk.StringVar(inputsW, value=defaults[index - 1])

            widgets_dict[argument] = [tk.Label(inputsW.inputsF, text=f'{argument}:'), tk.Entry(inputsW.inputsF, textvariable=taken_intputs[argument])]

        self.fill_grid(widgets_dict.values(), inputsW.inputsF)

        def confirm():
            try:
                self.arguments = [input_value.get() for input_value in taken_intputs.values()]
            except tk._tkinter.TclError:
                print("Inputted wrong data type, please try again")
            else:
                if execute:
                    func(*self.arguments)
                inputsW.quit()

        cancelB = tk.Button(inputsW.optionsF, text="Cancel", command=inputsW.quit)
        cancelB.place(relx=0.99, rely=0.99, anchor="se")
        cancelB = tk.Button(inputsW.optionsF, text="Confirm", command=confirm)
        cancelB.place(relx=0.01, rely=0.99, anchor="sw")
        inputsW.mainloop()
        inputsW.destroy()
        if not execute:
            return self.arguments
        else:
            return

    def input_vars(self, variables={}):
        """
        Creates a new Tkinter window that asks for values for the inputted variables.

        Parameters
        ----------
        variables : dict, optional
            Dict containing variable names as strings for the keys and the data type of the variable as the value. The default is {}.

        Returns
        -------
        list
            A list containing the inputted values for the variables.
            Returns an equal dimension list containing only None if the action was canceled

        """
        self.vars_out = None
        inputsW = tk.Toplevel(self.main)
        inputsW.title("Inputs")

        inputsW.optionsF = tk.Frame(inputsW)
        inputsW.optionsF.place(relx=0.5, rely=0.9, relheight=0.1, relwidth=1, anchor="n")

        inputsW.inputsF = tk.Frame(inputsW)
        inputsW.inputsF.place(relx=0, rely=0, relheight=0.89, relwidth=1, anchor="nw")

        widgets_dict = {}
        taken_inputs = {}
        for L_text, dtype in variables.items():
            initial = None
            options = []

            if type(dtype) == list:  # check for option lists and initial values
                options = dtype.copy()
                initial = options[0]
                dtype = type(initial)
            elif type(dtype) != type:
                initial = dtype
                dtype = type(dtype)

            if dtype == int:  # make tk variable
                taken_inputs[L_text] = tk.IntVar(inputsW)
            elif dtype == float:
                taken_inputs[L_text] = tk.DoubleVar(inputsW)
            elif dtype == str:
                taken_inputs[L_text] = tk.StringVar(inputsW)

            if initial is not None:  # set initial state
                taken_inputs[L_text].set(initial)

            if len(options) == 0:  # make tk input widget
                input_widget = tk.Entry(inputsW.inputsF, textvariable=taken_inputs[L_text])
            else:
                input_widget = tk.OptionMenu(inputsW.inputsF, taken_inputs[L_text], *options)
            widgets_dict[L_text] = [tk.Label(inputsW.inputsF, text=L_text), input_widget]

        self.fill_grid(widgets_dict.values(), inputsW.inputsF)

        def confirm():
            try:
                self.vars_out = [input_value.get() for input_value in taken_inputs.values()]
            except tk._tkinter.TclError:
                print("Inputted wrong data type, please try again")
            else:
                inputsW.quit()

        def cancel():
            self.vars_out = [None for _ in variables]
            inputsW.quit()

        cancelB = tk.Button(inputsW.optionsF, text="Cancel", command=cancel)
        cancelB.place(relx=0.99, rely=0.99, anchor="se")
        cancelB = tk.Button(inputsW.optionsF, text="Confirm", command=confirm)
        cancelB.place(relx=0.01, rely=0.99, anchor="sw")
        inputsW.mainloop()
        inputsW.destroy()
        return self.vars_out

    def edit_vars(self, exit_function, variables=[]):
        """
        Creates a pop-up that asks for values for the inputted variable keys.

        Parameters
        ----------
        exit_function : function
            Function run after clicking close.
        variables : list
            List containing variable keys as strings.

        Returns
        -------
        list
            A list containing the inputted values for the variables.
            Returns an equal dimension list containing only None if the action was canceled

        """
        if self.edit_vars_active is True:
            print("WARNING: Already editing variables")
            return
        else:
            self.edit_vars_active = True

        self.edit_vars_mainframe = tk.Frame(self.main, background=self.main.colors["background"])
        self.edit_vars_mainframe.place(anchor="c", relx=0.5, rely=0.5, relwidth=0.2, relheight=0.5)
        
        self.createFrames(self.edit_vars_mainframe, frame_keys=[["edit_vars"]], grid_frames=True, grid_size=0.96, border=0.04, relControlsHeight=0.1)
        self.edit_vars_options = tk.Frame(self.edit_vars_mainframe, background=self.main.colors["controls_frame"])
        self.edit_vars_options.place(rely=0.9, relheight=0.1, relwidth=1)

        self.edit_vars_inputs = self.main.frames["edit_vars_grid"]
        del self.main.frames["edit_vars_grid"]
        del self.main.frames["edit_vars"]

        widgets_dict = {}
        for var_key in variables:
            if self.version == "MINION":
                options = self.main.variables[var_key]["options"]
            else:
                options = self.main.var_dict[var_key].options

            if self.version == "MINION":
                L_text = self.main.variables[var_key]["display"]
            else:
                L_text = self.main.var_dict[var_key].display

            if self.version == "MINION":
                var = self.main.variables[var_key]["var"]
            else:
                var = self.main.var_dict[var_key].tkvar

            if len(options) == 0:
                input_widget = tk.Entry(self.edit_vars_inputs, textvariable=var)
            else:
                input_widget = tk.OptionMenu(self.edit_vars_inputs, var, *options)
            widgets_dict[var_key] = [self.genLabel(frm=self.edit_vars_inputs, txt=L_text + ":"), input_widget]

        self.fill_grid(widgets_dict.values(), self.edit_vars_inputs)

        closeB = tk.Button(self.edit_vars_options, text="Close", command=lambda: self.edit_confirm(exit_func=exit_function, vars=variables))
        closeB.place(relx=0.5, rely=0.5, anchor="c")
        return

    def edit_confirm(self, exit_func, vars=[]):
        try:
            if self.version == "MINION":
                for var_key in vars: 
                    self.main.variables[var_key]["var"].get()
            else:
                for var_key in vars:
                    self.main.var_dict[var_key].get()
        except tk._tkinter.TclError:
            print("WARNING: Inputted wrong data type, please try again")
        else:
            if exit_func is not None:
                exit_func()
            self.edit_vars_mainframe.destroy()
            self.edit_vars_active = False
        return


#%% Hero Variable Manager

class Hvar():
    def __init__(self, hk, key, vtype, dtype, display, frame, initial, width=0, height=0, options=[], command=None, noWidget=False, switch_initial=None, checkbox_text=None):
        hk.main.var_dict[key] = self
        self.vtype = vtype
        self.dtype = dtype
        self.display = display
        self.frame = frame
        self.initial = initial
        if self.dtype == bool:
            self.options = [False, True]
        else:
            self.options = options
        self.command = command
        self.noWidget = noWidget
        self.switch_initial = switch_initial
        self.list_width = width
        self.list_height = height
        self.checkbox_text = checkbox_text
        self.tkvar = None
        self.widget = None
        self.switch_output = None

        if self.vtype == "input" and self.noWidget is False:
            self.tkvar, self.widget = hk.defVarI(dtype=self.dtype, frame=hk.main.frames[self.frame],
                                                 L_text=f"{self.display}:", initial=self.initial,
                                                 options=self.options, cmd=self.command, checkbox_text=self.checkbox_text)
        elif self.vtype == "output":
            self.tkvar, self.widget = hk.defVarO(dtype=self.dtype, frame=hk.main.frames[self.frame],
                                                 L_text=f"{self.display}:", initial=self.initial,)
        elif self.vtype == "input" and self.noWidget is True:
            self.tkvar = hk.defVar(dtype=self.dtype, initial=self.initial)
        elif self.vtype == "list":
            self.tkvar, self.widget = hk.defListO(frame=hk.main.frames[self.frame], L_text=f"{self.display}:", h=self.list_height, w=self.list_width)
        if self.switch_initial is not None and self.noWidget is False:
            self.switch_output, widget = hk.defVarI(dtype=bool, frame=hk.main.frames[self.frame], L_text="", initial=self.switch_initial)
            self.widget.append(widget[-1])

    def get(self):
        return self.tkvar.get()

    def set(self, value):
        self.tkvar.set(value)
        return
