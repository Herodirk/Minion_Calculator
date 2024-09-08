# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 16:21:07 2024

@author: Herodirk

A module containing functions to assit in the creation and handling of Tkinter windows
"""

import tkinter as tk
import numpy as np

color_palettes = {"dark": {"background": "black",
                           "frame_background": "#313338",
                           "controls_frame": "dim gray",
                           "widget_background": "#383A40",
                           "widget_border": "#2E3035",
                           "active_background": "#2E3035",
                           "text": "white",
                           "selected_text": "black",
                           "selection": "light gray"}}


class Hk():
    def __init__(self, main, windowTitle, windowWidth, windowHeight, palette="dark"):
        """
        Initializes Hkinter. Sets the chosen color palette. Configures the main window. Creates dict variables for storage of switches and frames.

        Parameters
        ----------
        main : root
            Root of the Tkinter application that Hkinter is being used for.
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
        return

    def createFrames(self, frame_keys=[], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0.07):
        """
        Saves and places controls frame and additional frames according to inputted matrix.
        Maxtric can be any size. Fill empty spaces with None.

        Parameters
        ----------
        frame_keys : list
            2 dimensional array of frame keys as strings. The default is [].
            [
                [column 1 row 1, column 2 row 1],
                [column 1 row 2, column 2 row 2],
            ]
        grid_frames : bool, optional
            DESCRIPTION. The default is True.
        grid_size : float, optional
            Relative size of grid frame in the parent frame. Float between 0 and 1. The default is 0.96.
        border : float, optional
            Relative size of the border thickness in the main window. Float between 0 and 1. The default is 0.01.
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

        self.main.frame_amount = np.size(frame_keys)
        rel_w = 1 / max([len(frame_keys[i]) for i in range(len(frame_keys))])
        rel_h = (1 - relControlsHeight) / len(frame_keys)
        for row_loc, row_keys in enumerate(frame_keys):
            for col_loc, key in enumerate(row_keys):
                if key is not None:
                    self.main.frames[key] = tk.Frame(self.main, background=self.main.colors["frame_background"])
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
        tl.Label
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

    def defVarI(self, dtype, frame, L_text, initial=None, options=[], cmd=None):
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
                entry = tk.OptionMenu(frame, var, *options, command=cmd)
            else:
                entry = tk.Entry(frame, textvariable=var)
        else:
            entry = tk.Checkbutton(frame, variable=var, background=self.main.colors["frame_background"], command=cmd)
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

    def fill_grid(self, grid_arr, frame):
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

        Returns
        -------
        None.

        """
        for rowindex, row in enumerate(grid_arr):
            for colindex, col in enumerate(row):
                if col is None:
                    self.genLabel(frm=frame, txt="").grid(row=rowindex, column=colindex)
                    continue
                col.grid(row=rowindex, column=colindex, sticky='w')
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
        obj : any Tkinter widget
            DESCRIPTION.
        loc : "grid" or a function
            Location of the widget, grid if the widget is part of a grid or a function that places the widget.
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
            loc(obj)
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
            Control variable to determine if the widget should be visible or not. None to force a switch. The default is None. The default is None.

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
                    loc(obj)

            self.main.switches[ID]["state"] = True
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


#%% test enviroment
if __name__ == "__main__":
    class test_calc(tk.Tk):
        def __init__(self):
            super().__init__()
            self.hk = Hk(self, "Test", 500, 500)

            self.hk.createFrames([["inputs", "outputs"]])

            test_text = tk.Label(self.frames["controls"], text="test")
            test_text.pack()

            self.var, self.varI = self.hk.defVarI(frame=self.frames["inputs"], dtype=float, L_text="Variable:", initial=0.0)
            self.negative, self.negativeI = self.hk.defVarI(frame=self.frames["inputs"], dtype=bool, L_text="Negative:", initial=False)
            self.out, self.outO = self.hk.defVarO(frame=self.frames["outputs"], dtype=float, L_text="Squared:", initial=0.0)
            self.previous, self.previousO = self.hk.defListO(frame=self.frames["outputs"], L_text="History:")
            self.history = []
            self.show_A, self.show_AI = self.hk.defVarI(bool, self.frames["inputs"], L_text="A", initial=False)
            self.hk.defSwitch("A", self.show_AI, loc="grid")
            self.show_B, self.show_BI = self.hk.defVarI(bool, self.frames["inputs"], L_text="BBBBBBBBB", initial=False)
            self.hk.defSwitch("B", self.show_BI[0], loc=lambda x: x.place(in_=self.button, rely=2, anchor="nw"), initial=False)
            self.show_zero = tk.Label(self.frames["inputs"], text="Is zero")
            self.hk.defSwitch("zero", self.show_zero, "grid", control=0.0, initial=True)

            self.button = tk.Button(self.frames["inputs"], text='Test', command=self.testfunc)
            # self.button.place(relx=0, rely=0.5, anchor="w")

            self.testbutton = tk.Button(self.frames["outputs"], text='Add', command=lambda x=self.some_func: self.hk.input_args(func=x, execute=True))

            self.testbutton2 = tk.Button(self.frames["outputs"], text='Multiply', command=self.another_func)

            grid_arr = [self.varI,
                        self.negativeI,
                        self.show_AI,
                        [self.button],
                        [self.show_zero]]
            self.hk.fill_grid(grid_arr, self.frames["inputs"])

            grid_arr = [self.outO,
                        self.previousO,
                        [self.testbutton, self.testbutton2]]
            self.hk.fill_grid(grid_arr, self.frames["outputs"])

        def testfunc(self):
            number = self.var.get()
            squared = number**2
            if self.negative.get():
                squared *= -1
            self.out.set(squared)
            self.history.append(squared)
            self.previous.set(self.history)
            if self.show_A.get() is True:
                self.show_BI[0].configure(text="AAAAA")
            else:
                self.show_BI[0].configure(text="BBBBBBBBB")
            self.hk.toggleSwitch("A", None)
            self.hk.toggleSwitch("B", None)
            self.hk.toggleSwitch("zero", squared)
            return

        def some_func(self, x=0.0, y=0.0, name="Name"):
            print(x + y)
            print(name)
            return

        def another_func(self):
            inputs = self.hk.input_vars({"Number 1": [1, -1], "Number 2": float})
            print(inputs)
            return

    def start_test():
        test = test_calc()
        test.mainloop()
        # del test.hk
        test.destroy()
        return
