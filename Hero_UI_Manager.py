# -*- coding: utf-8 -*-
"""
@author: Herodirk

Hero UI Manager
A module containing functions to assit in the creation and management of Tkinter windows and Tkinter variables
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import urllib.request
import logging
import json
import time
from copy import deepcopy
import math

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#%% Hero UI Manager

class H_UI_M():
    def __init__(self, main, windowTitle, windowWidth, windowHeight, palette="dark", debug_mode=False):
        """
        H_UI_M: Hero UI Manager, main class for Hero UI Manager functions
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
        self.logger = logging.getLogger("HUIM_logger")
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
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
        self.reduced_amounts = {0: "", 1: "k", 2: "M", 3: "B", 4: "T", 5: "Qd"}
        self.active_edit_vars = None
        self.edit_vars_requests = {}

        self.style = ttk.Style()
        self.style.theme_create(
            "calculator", parent="clam",
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
        self.style.theme_use('calculator')
        # self.logger.info("Hero UI Manager version ")  # will use later when HUIM because separate from the minion calculator
        return

    ### Frame creation

    def create_controls(self, relControlsHeight=0.07):
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
        self.logger.debug("Created controls")
        return

    def create_frames(self, parent, frame_keys=[], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0.07):
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

    ### Variable and Widget creation

    def create_label(self, frm, txt, txtvar=False):
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

    def def_var(self, dtype, initial=None):
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
        elif dtype == list:
            var = tk.StringVar(self.main)
        elif dtype == dict:
            var = tk.StringVar(self.main)
        if initial is not None:
            var.set(initial)
        return var

    def def_input_var(self, dtype, frame, L_text, initial=None, options=None, cmd=None, checkbox_text=None, w=None, h=None, existing_var=None):
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
            List of options for an option menu. List must contain items of type dtype. The default is None.
        cmd : function, optional
            Function that runs when an option in the option menu is. The default is None.
        checkbox_text : str, optional
            Text that will be displayed next to the checkbox if dtype is bool
        w : int, optional
            Width of the widget. None for default size. The default is None.
        h : int, optional
            Height of the widget. None for default size. The default is None.

        Returns
        -------
        var : tk.BooleanVar, tk.IntVar, tk.StringVar or tk.DoubleVar
            Fully constructed Tkinter variable ready for use.
        list
            List containing the label and the input widget.

        """
        if existing_var is None:
            var = self.def_var(dtype, initial=initial)
        else:
            var = existing_var
        if dtype != bool:
            if options is not None:
                input_widget = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=1 + len(str(max(options, key=lambda x: len(str(x))))), height=20)
                if cmd is not None:
                    input_widget.bind('<<ComboboxSelected>>', lambda void_event: cmd(var.get()))
            else:
                input_widget = tk.Entry(frame, textvariable=var)
        else:
            input_widget = tk.Checkbutton(frame, variable=var, background=self.main.colors["frame_background"], command=cmd)
            if checkbox_text is not None:
                input_widget.configure(text=checkbox_text)
        label = self.create_label(frm=frame, txt=L_text)
        if w is not None:
            input_widget.configure(width=w)
        if h is not None:
            input_widget.configure(height=h)
        return var, [label, input_widget]

    def def_output_var(self, frame, dtype, L_text, initial=None, w=None, h=None):
        """
        def_output_var: define output variable
        Generates a Tkinter variable, a label and an variable label.
        The variable label is connected to the Tkinter variable.

        Parameters
        ----------
        frame : tk.Frame
            Frame where the label and output widget will be generated in.
        dtype : type
            Data type for the Tkinter variable. Accepted options are bool, int, str, float, list or dict.
        L_text : str
            String used for the label.
        initial : something of type dtype, optional
            Inital value for the Tkinter variable. Set to None for default initial value. The default is None.
        w : int, optional
            Width of the widget. None for default size. The default is None.
        h : int, optional
            Height of the widget. None for default size. The default is None.

        Returns
        -------
        var : tk.BooleanVar, tk.IntVar, tk.StringVar or tk.DoubleVar
            Fully constructed Tkinter variable ready for use.
        list
            List containing the label and the variable label.

        """
        var = self.def_var(dtype, initial=initial)
        text_label = self.create_label(frm=frame, txt=L_text)
        if dtype in [list, dict]:
            output_widget = tk.Listbox(frame, listvariable=var)
        else:
            output_widget = self.create_label(frm=frame, txt=var, txtvar=True)
        if w is not None:
            output_widget.configure(width=w)
        if h is not None:
            output_widget.configure(height=h)
        return var, [text_label, output_widget]

    ### Widget placement

    def create_grid(self, grid_dict):
        """
        Creates a 2 dimensional array of widgets out of a dict consisting of
        values: None or list filled with widgets and/or None
        keys: if value is None, key should be a variable key
        
        :param grid_dict: dict definition for the grid
        :return: 2 dimensional grid array of widgets
        :rtype: list
        """
        grid_arr = []
        for key, val in grid_dict.items():
            if val is None:
                grid_arr.append(self.main.var_dict[key].widget)
            else:
                grid_arr.append(val)
        return grid_arr

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
                    self.create_label(frm=grid_frame, txt="").grid(row=rowindex, column=colindex)
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

    ### Switch management

    def def_switch(self, switch_id, widget_references, locations, control=None, negate=False, initial=True):
        """
        def_switch: define switch
        Creates an entry in the switches dict used for turning widgets on and off.
        The entry is saved under an ID and has the following items:
            the current visibility state as a boolean\n
            a reference to the widget itself\n
            the location of the widget\n
            a control variable to determine if the widget should show or disappear\n
            a boolean to reverse the relation with the control

        Parameters
        ----------
        switch_id : str
            ID for the switch to call it with toggleSwitch.
        widget_references : any Tkinter widget or list of widgets and/or variable keys
            The objects that will be part of the switch, can be one singular widget or a list of widgets and/or variables keys.
        locations : "grid", dict or list of dicts and/or "grid"
            Location of the widget,
            "grid" if the widget is part of a grid, a dictionary with arguments for .place() or
            a list of dictionaries for multiple objects.
            widget_references and locations should reference the same amount of objects
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
        widget_list = []
        location_list = []

        # process given widgets
        if type(widget_references) is not list:
            widget_references = [widget_references]
        for widget in widget_references:
            if type(widget) is str:
                if widget not in self.main.var_dict:
                    self.logger.warning(f"var key \"{widget}\" in switch \"{switch_id}\" not in var_dict")
                    continue
                widget_list.extend(self.main.var_dict[widget].widget)
            else:
                widget_list.append(widget)
        
        # process given locations
        if type(locations) is dict:
            location_list = [locations]
        elif locations == "grid":
            location_list = ["grid" for _ in widget_list]
        else:
            location_list = locations

        # check amount equality
        if len(widget_list) != len(location_list):
            self.logger.warning(f"{switch_id} switch did not activate, given widgets does not equal given locations ({len(widget_list)} != {len(location_list)})")

        # save switch
        self.main.switches[switch_id] = {"state": initial, "widgets": widget_list, "locations": location_list, "control": control, "negate": negate}

        # apply initial state
        for widget, loc in zip(widget_list, location_list):
            if loc != "grid" and initial is True:
                widget.place(**loc)
            if loc == "grid" and initial is False:
                widget.grid_remove()
        return

    def toggle_switch(self, switch_id, control=None):
        """
        Toggles a switch by ID and check if control conditions are met

        Parameters
        ----------
        switch_id : str
            Identifier of the switch.
        control : str, int, float, optional
            Control variable to determine if the widget should be visible or not. None to force a switch. The default is None.

        Returns
        -------
        None.

        """
        if switch_id not in self.main.switches:
            self.logger.error(f"ID {switch_id} does not exist in switch storage")
            return
        state = self.main.switches[switch_id]["state"]
        if control is not None:
            if self.main.switches[switch_id]["negate"]:
                if state is not (control == self.main.switches[switch_id]["control"]):
                    return
            else:
                if state is (control == self.main.switches[switch_id]["control"]):
                    return
        if state is True:
            next_grid_state = lambda obj: obj.grid_remove()
            next_place_state = lambda obj, args: obj.place_forget()
        else:
            next_grid_state = lambda obj: obj.grid()
            next_place_state = lambda obj, args: obj.place(**args)
        for widget, loc in zip(self.main.switches[switch_id]["widgets"], self.main.switches[switch_id]["locations"]):
            if loc == "grid":
                next_grid_state(widget)
            else:
                next_place_state(widget, loc)
        self.main.switches[switch_id]["state"] = bool(1 - int(state))
        return

    def create_switch_call(self, switch_id, controlvar=None):
        """
        Creates a command for a GUI widget that calls a switch.

        Parameters
        ----------
        switch_id : str
            Identifier of the switch.
        controlvar : str or None
            Variable key for the switch control. "self" to make the command send the value in the widget as control. None to force a switch. The default is None.

        Returns
        -------
        lambda function
            Command for a GUI widget that calls a switch

        """
        if controlvar == "self":
            return lambda x: self.toggle_switch(switch_id, x)
        elif controlvar is None:
            return lambda: self.toggle_switch(switch_id, None)
        else:
            return lambda: self.toggle_switch(switch_id, self.main.var_dict[controlvar].get())

    def create_show_hide_toggle(self, anchor_widget, switch_id, place_args={"relx": 1, "x": 3, "rely": 0.5, "anchor": 'w'}, button_text="Toggle extra options"):
        """
        Creates and places a button that forces a switch, or runs any inputted function.

        Parameters
        ----------
        parent_var_key : str
            Variable key of the widget where the button should anchor to.
        switch_id : str or function
            As string it's the identifier of the switch. As function it is any function.
        place_args : dict
            Dictionary containing the arguments for the .place function of Tkinter.
            Default is {"relx": 1, "x": 3, "rely": 0.5, "anchor": 'w'}

        Returns
        -------
        None.
        """
        button_frame = anchor_widget.master
        if type(switch_id) is str:
            button = tk.Button(button_frame, text=button_text, border=0, borderwidth=0, command=self.create_switch_call(switch_id))
        elif str(type(switch_id)) == "<class 'function'>":
            button = tk.Button(button_frame, text=button_text, border=0, borderwidth=0, command=switch_id)
        if place_args is None:
            return button
        button.place(in_=anchor_widget, **place_args)
        return

    ### Data logistics

    def call_API(self, api_url, api_name="API", data=None, headers={}, retried=False):
        self.logger.debug(f"Calling {api_name}")
        failed = False
        try:
            req = urllib.request.Request(api_url, data=data, headers=headers)
            call_data = urllib.request.urlopen(req).read().decode('utf-8')
        except urllib.error.HTTPError as error:
            self.logger.error(f"Could not finish {api_name} call: \n{error.code}: {error.reason}")
            failed = True
        except urllib.error.URLError as error:
            self.logger.error(f"Could not finish {api_name} call: \n{error.reason}")
            failed = True
        if failed:
            if retried:
                return {}
            else:
                self.logger.warning(f"Retrying {api_name} call in 10 seconds")
                time.sleep(10)
                return self.call_API(api_url, api_name=api_name, data=data, headers=headers, retried=True)
        else:
            return json.loads(call_data)

    def get_from_GUI(self, var_keys, translate=True):
        """
        Gets the requested variables of the GUI and returns them as a dict.

        Returns
        -------
        dict
            values of the requested variables.

        """
        var_values = {}
        for var_key in var_keys:
            if var_key not in self.main.var_dict:
                self.logger.warning(f"{var_key} key not in self.var_dict")
                continue
            if self.main.var_dict[var_key].dtype in [dict, list]:
                var_values[var_key] = deepcopy(self.main.var_dict[var_key].list)
            else:
                var_values[var_key] = self.main.var_dict[var_key].get(translate)
        return var_values

    def send_to_GUI(self, outputs):
        """
        sends outputs to the GUI.

        Parameters
        ----------
        outputs : dict
            dict containing variable keys as keys with the wanted value.

        Returns
        -------
        None.

        """
        for var_key in outputs:
            if var_key not in self.main.var_dict:
                self.logger.warning(f"Output {var_key} not found in self.var_dict")
                continue
            if (var_dtype := self.main.var_dict[var_key].dtype) in [dict, list]:
                self.main.var_dict[var_key].list.clear()
                if var_dtype is dict:
                    self.main.var_dict[var_key].list.update(outputs[var_key])
                else:
                    self.main.var_dict[var_key].list.extend(outputs[var_key])
            else:
                self.main.var_dict[var_key].set(outputs[var_key])
        return

    def check_json(self, file, default):
        if not file.is_file():
            self.write_json(file, default)
        return

    def write_json(self, file, json_object):
        try:
            file.write_text(json.dumps(json_object, indent=4, sort_keys=True), encoding="utf-8")
        except Exception:
            self.logger.error(f"Failed to write to {file.name}")
        return

    def read_json(self, file):
        try:
            data = json.loads(file.read_text())
        except Exception:
            data = {}
        return data

    ### Data editing

    def reduced_number(self, number, decimal=2):
        """
        Rounds a number to the inputted amount of decimal places and adds a letter to large numbers like M for million.

        Parameters
        ----------
        number : float
            The number to round.
        decimal : int, optional
            Amount of decial places to round to. The default is 2.

        Returns
        -------
        str
            Rounded number with a size indicator letter if needed.

        """
        if number == math.inf:
            return "Infinite"
        if number == 0.0:
            return str(0)
        elif np.abs(number) < 1:
            return str(np.round(number, decimal - 1 + int(np.abs(np.floor(np.log10(np.abs(number)))))))
        highest_reduction = min(int(np.floor(np.log10(np.abs(number))) / 3), len(self.reduced_amounts) - 1)
        reduced = np.round((number / (10 ** (3 * highest_reduction))), decimal)
        if int(reduced) == reduced:
            reduced = int(reduced)
        output_string = f'{reduced}{self.reduced_amounts[highest_reduction]}'
        return output_string

    def deepmultiply(self, obj, multiplier):
        """
        Multiplies all number values in an object.

        Parameters
        ----------
        obj : dict or list
            The object.
        multiplier : float or int
            The multiplication amount.

        Returns
        -------
        None.

        """
        if type(obj) is dict:
            keys = obj.keys()
        else:
            keys = range(len(obj))
        for key in keys:
            if type(obj[key]) in [dict, list]:
                self.deepmultiply(obj[key], multiplier)
            elif type(obj[key]) is str:
                continue
            else:
                obj[key] *= multiplier
        return

    def time_number(self, time_unit, time_amount, custom_time_unit_seconds=1.0):
        """
        Translates time amount and length into seconds.

        Parameters
        ----------
        time_unit : str
            A time unit, "Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", or a custom unit, defined by custom_time_unit_seconds.
        time_amount : float
            Amount of time units.
        custom_time_unit_seconds : float, optional
            Amount of seconds per custom time length. Used when time_length does not match any normal units of time. The default is 1.0.

        Returns
        -------
        float
            The inputted time amount and length as seconds.

        """
        if time_unit == "Years":
            return 31536000 * time_amount
        elif time_unit == "Weeks":
            return 604800 * time_amount
        elif time_unit == "Days":
            return 86400 * time_amount
        elif time_unit == "Hours":
            return 3600 * time_amount
        elif time_unit == "Minutes":
            return 60 * time_amount
        elif time_unit == "Seconds":
            return 1 * time_amount
        else:
            return custom_time_unit_seconds * time_amount

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
                self.logger.error("Inputted wrong data type, please try again")
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
                self.logger.error("Inputted wrong data type, please try again")
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

    def new_edit_vars(self, request_id, variables, exit_function, relwidth=0.2, relheight=0.5):
        # variables : {
        #   var_key : {
        #       dtype : data type,
        #       display : str,
        #       initial : value of dtype,
        #       options : list
        #   },
        #   dict_key : {
        #       dtype := dict,
        #       display : str,
        #       initial : dict
        #   },
        # }
        self.edit_vars_requests[request_id] = {}
        self.edit_vars_requests[request_id]["variables"] = {}
        # frame : main frame
        # exit_func : exit function
        # variables : {
        #   edit_vars_key : tkvar 
        #   edit_dict_key : {listbox : tkvar, edit_key : tkvar, edit_val : tkvar, dict: dict }
        # }
        self.edit_vars_requests[request_id]["exit_func"] = exit_function
        new_edit_vars_frame = tk.Frame(self.main, background=self.main.colors["background"])
        new_edit_vars_grid = tk.Frame(new_edit_vars_frame, background=self.main.colors["frame_background"])
        new_edit_vars_grid.place(rely=0.5 * 0.02, relx=0.5 * 0.02, relwidth=1 - 0.02, relheight=1 - 0.02)
        self.def_switch(f"edit_vars_{request_id}", widget_references=new_edit_vars_frame,
                        locations={"anchor": "c", "relx": 0.5, "rely": 0.5, "relwidth": relwidth, "relheight": relheight}, initial=False)
        
        widgets_dict = {}
        for var_key, var_data in variables.items():
            if var_data is None:
                self.edit_vars_requests[request_id]["variables"][var_key], widgets_dict[var_key] = self.def_input_var(self.main.var_dict[var_key].dtype, new_edit_vars_grid, f"{self.main.var_dict[var_key].get_display()}:", None, self.main.var_dict[var_key].options, None, existing_var=self.main.var_dict[var_key].tkvar)
            elif var_data["dtype"] == dict:
                self.edit_vars_requests[request_id]["variables"][var_key] = {}
                self.edit_vars_requests[request_id]["variables"][var_key]["listbox"], widgets_dict[var_key + "_listbox"] = self.def_output_var(new_edit_vars_grid, dict, f"{var_data['display']}:", var_data["initial"], 35, 10)
                self.edit_vars_requests[request_id]["variables"][var_key]["listbox"].set([f'{init_key}: {init_val}' for init_key, init_val in var_data["initial"].items()])
                self.edit_vars_requests[request_id]["variables"][var_key]["edit_key"], widgets_dict[var_key + "_edit_key"] = self.def_input_var(str, new_edit_vars_grid, "Key:")
                self.edit_vars_requests[request_id]["variables"][var_key]["edit_val"], widgets_dict[var_key + "_edit_val"] = self.def_input_var(str, new_edit_vars_grid, "Value:")
                widgets_dict[var_key + "_submit"] = [None, tk.Button(new_edit_vars_grid, text="Submit", command=lambda: self.edit_dict_submit(request_id, var_key))]
                self.edit_vars_requests[request_id]["variables"][var_key]["dict"] = var_data["initial"]
            else:
                self.edit_vars_requests[request_id]["variables"][var_key], widgets_dict[var_key] = self.def_input_var(var_data["dtype"], new_edit_vars_grid, f"{var_data['display']}:", var_data["initial"], var_data["options"], None)

        self.fill_grid(widgets_dict.values(), new_edit_vars_grid)

        closeB = tk.Button(new_edit_vars_grid, text="Close", command=lambda: self.edit_vars_confirm(request_id))
        closeB.place(relx=0.5, rely=1, anchor="s", y=-10)
        self.edit_vars_requests[request_id]["frame"] = new_edit_vars_frame
        return

    def edit_dict_submit(self, request_id, edit_dict_key):
        dict_to_edit = self.edit_vars_requests[request_id]["variables"][edit_dict_key]["dict"]
        edit_key = self.edit_vars_requests[request_id]["variables"][edit_dict_key]["edit_key"].get()
        edit_val = self.edit_vars_requests[request_id]["variables"][edit_dict_key]["edit_val"].get()
        if edit_key == "":
            return
        if edit_val == "":
            del dict_to_edit[edit_key]
        else:
            try:
                edit_val = float(edit_val)
            except ValueError:
                pass
            dict_to_edit[edit_key] = edit_val
        self.edit_vars_requests[request_id]["variables"][edit_dict_key]["listbox"].set([f'{key}: {val}' for key, val in dict_to_edit.items()])
        return

    def edit_vars(self, request_id):
        """
        Activates the inputted edit vars request.

        Parameters
        ----------
        request_id : string
            ID of edit vars request as defined with new_edit_vars

        Returns
        -------
        None

        """
        if self.active_edit_vars is not None:
            self.logger.warning("Already editing variables")
            return
        if request_id not in self.edit_vars_requests:
            self.logger.warning("Edit vars request does not exist")
            return
        self.active_edit_vars = request_id        
        self.toggle_switch(f"edit_vars_{request_id}")
        return

    def edit_vars_confirm(self, request_id):
        results = {}
        try:
            for var_key, tkvar in self.edit_vars_requests[request_id]["variables"].items():
                if type(tkvar) != dict:
                    results[var_key] = tkvar.get()
                else:
                    results[var_key] = tkvar["dict"]
        except tk._tkinter.TclError:
            self.logger.error("Inputted wrong data type, please try again")
        else:
            self.active_edit_vars = None
            self.toggle_switch(f"edit_vars_{request_id}")
            if self.edit_vars_requests[request_id]["exit_func"] is not None:
                self.edit_vars_requests[request_id]["exit_func"](results)
        return


#%% Hero Variable Manager

class Hvar():
    def __init__(self, huim: H_UI_M, key: str, vtype: str, dtype: type, display: str, initial, frame: str=None, fancy_display: str=None , widget_width:int=None, widget_height: int=None, options: list | dict=None, command=None, switch_initial: None | bool=None, checkbox_text: None | str=None, tags: list| None=None):
        if key in huim.main.var_dict:
            self.logger.warning(f"{key} already exists in variable dictionary, overwriting it")
        huim.main.var_dict[key] = self  # define in variable dictionary
        # Mandatory data:
        self.key = key  # unique identifier 
        self.vtype = vtype  # str, variable type ("input", "output", "storage")
        self.dtype = dtype  # type, data type
        self.name_display = display  # str, human-readable display name of variable
        self.initial = initial  # {self.dtype}, initial value of the variable

        # Optional data:
        self.frame = frame  # str, ID of Tk Frame in huim.main.frames where the widgets get made
        self.fancy_name_display = fancy_display  # str, fancy display name of variable, if None, self.name_display is used
        if self.dtype == bool:
            self.options = [False, True]
        else:
            self.options = options  # list containing allowed values, None if no restrictions. If given as dict: allowed values as keys, automatic translation for .get() as values. Dict saved in self.translation, list of keys saved in self.options
        self.command = command  # callable, function to run when input changed 
        self.switch_initial = switch_initial  # bool or None, initial state of the output switch, None if no output switch
        self.widget_width = widget_width  # int, width of widget in characters
        self.widget_height = widget_height  # int, height of widget in amount of lines
        self.checkbox_text = checkbox_text  # str, text added next to the checkbox
        self.tags = tags  # list, tags of the variable

        # Generated data:
        self.tkvar = None
        self.list = None
        if self.dtype in [list, dict]:
            self.list = self.initial
        self.widget = None
        self.translation = None  # Translation: untranslated (display) -> translated (internal)
        self.reverse_translation = None  # Reverse Translation: translated (internal) -> untranslated (display)
        if type(self.options) is dict:
            self.translation = self.options
            self.options = list(self.options.keys())
            self.reverse_translation = {translated: untranslated for untranslated, translated in self.translation.items()}
        self.tk_output_switch = None

        if self.vtype == "input":
            self.tkvar, self.widget = huim.def_input_var(dtype=self.dtype, frame=huim.main.frames[self.frame],
                                                 L_text=f"{self.name_display}:", initial=self.initial,
                                                 options=self.options, cmd=self.command, checkbox_text=self.checkbox_text)
        elif self.vtype == "output":
            self.tkvar, self.widget = huim.def_output_var(dtype=self.dtype, frame=huim.main.frames[self.frame],
                                                 L_text=f"{self.name_display}:", initial=self.initial,
                                                 h=self.widget_height, w=self.widget_width)
        elif self.vtype == "storage":
            self.tkvar = huim.def_var(dtype=self.dtype, initial=self.initial)
        if self.switch_initial is not None:
            self.tk_output_switch, widget = huim.def_input_var(dtype=bool, frame=huim.main.frames[self.frame], L_text="", initial=self.switch_initial)
            self.widget.append(widget[-1])

    def get(self, translate=True):
        if (self.translation is None) or (translate is False):
            return self.tkvar.get()
        elif translate:
            return self.translation[self.tkvar.get()]

    def get_display(self, fancy: bool=False) -> str:
        if fancy and self.fancy_name_display is not None:
            return self.fancy_name_display
        return self.name_display

    def get_output_switch(self):
        if self.tk_output_switch is None:
            return None
        else:
            return self.tk_output_switch.get()

    def has_tag(self, tag):
        if self.tags is None:
            return False
        else:
            return tag in self.tags

    def set(self, value, translated=False) -> None:
        if (self.translation is None) or (translated is False):
            self.tkvar.set(value)
            return
        else:
            self.tkvar.set(self.reverse_translation[value])
            return

    def update_listbox(self, key_format_function=lambda x: x, value_format_function=lambda x: x, filter=lambda key, val: True) -> None:
        if self.dtype not in [dict, list]:
            return
        listbox_list = []
        if self.dtype is dict:
            for key, val in self.list.items():
                if not filter(key, val):
                    continue
                listbox_list.append(f'{key_format_function(key)}: {value_format_function(val)}')
        elif self.dtype is list:
            for val in self.list:
                if not filter(None, val):
                    continue
                listbox_list.append(key_format_function(val))
        self.set(listbox_list)
        return

    def update_option_list(self, new_list, translated=False):
        if self.dtype == bool:
            return
        if self.options == None:
            return
        if translated:
            new_list = [self.reverse_translation[list_item] for list_item in new_list]
        if not (set(new_list) <= set(self.options)):
            return
        self.widget[1].config(values=new_list)
        if self.get(False) not in new_list:
            self.set(new_list[-1])
        return
