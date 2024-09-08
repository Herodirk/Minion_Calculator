# -*- coding: utf-8 -*-
"""
Released on Sun Aug 8 22:10 UTC+0002 2024

@author: Herodirk

Main file for the minion calculator.
Notable features:
    near infinite customizable setup
    Corrupt soil calculations
    Inferno minions calculations
    Pet leveling calculations
    Setup cost calculations
Visit https://herodirk.github.io/ for an online manual.
To open the calculator: run this file, run the function start_app()

Current major limitations:
    (Lesser) Soulflow Engines might not be accurate (there seems to be some weird rounding in game)
    Inferno drop chances might be unaccurate (in game Hypixel seem to have higher chances)
    Item prices from AH (like pets and Everburning Flame) have to be updated manually
    Unknown average wool amount from Enchanted Shears
    For offline calculations of mob minions: Hypixel takes 5 actions to spawn in mobs, this calculator does not account for that
    Dyes (Byzantium and Flame) are included in the base drops of their minions, but they should only be there if the player harvests
Lesser limitations are listed on the support discord server,
the invite to that server is at the bottom of https://herodirk.github.io/

This program and related files (Hkinter.py and HSB_minion_data.py) are protected under a GNU GENERAL PUBLIC LICENSE (Version 3)
Herodirk: I dont want any legal trouble, just ask me for permission if you want to copy parts of the code for your own public projects. Copying for private projects is fine.

Herodirk is not affiliated with Hypixel Inc.
"""


#%% imports

import tkinter as tk
import numpy as np
import time
import json
import urllib.request
from copy import deepcopy
import HSB_minion_data as md
import Hkinter

#%% Settings

bazaar_auto_update = True
bazaar_cooldown = 60  # seconds

templateList = {
    "ID": {},  # would suggest to keep this one
    "Clean": {},  # would suggest to keep this one too
    "Corrupt": {
        "hopper": "Enchanted Hopper",
        "upgrade1": "Corrupt Soil",
    },
    "Compact": {
        "hopper": "Best (NPC/Bazaar)",
        "upgrade1": "Super Compactor 3000",
    },
    "Mid speed": {
        "fuel": "Enchanted Lava Bucket",
        "upgrade2": "Diamond Spreading",
        "beacon": 0,
        "infusion": False
    },
    "Max speed": {
        "fuel": "Plasma Bucket",
        "upgrade2": "Flycatcher",
        "beacon": 5,
        "infusion": True
    },
    "Hyper speed": {
        "fuel": "Hyper Catalyst",
        "upgrade2": "Flycatcher",
        "beacon": 5,
        "infusion": True
    },
    "AFK with pet": {
        "afkpet": 100,
        "afk": True
    },
    "GDrag Leveling": {
        "miningWisdom": 79,
        "combatWisdom": 79,
        "levelingpet": "Golden Dragon",
        "taming": 60,
        "petxpboost": "Epic Combat Exp Boost",
    },
    "Maxed Inferno Minion": {
        "minion": "Inferno",
        "amount": 31,
        "fuel": "Inferno Minion Fuel",
        "infernoGrade": "Hypergolic Gabagool",
        "infernoDistilate": "Crude Gabagool Distillate",
        "infernoEyedrops": True,
        "hopper": "Best (NPC/Bazaar)",
        "upgrade1": "Flycatcher",
        "upgrade2": "Flycatcher",
        "beacon": 5,
        "infusion": True,
        "bazaar_sell_type": "Sell Offer",
        "bazaar_buy_type": "Buy Order"
    }
}

# pet_data last updated on: 2024-9-8
pet_data = {"None": {"type": "combat", "xp": 1, "cost": {"min": 1, "max": 1}},
            "Golden Dragon": {"type": "combat", "xp": 210255385, "cost": {"min": 650000000, "max": 1090000000}},
            "Golden Dragon (lvl 1-100)": {"type": "combat", "xp": 25353230, "cost": {"min": 650000000, "max": 720000000}},
            "Golden Dragon (lvl 100-200)": {"type": "combat", "xp": 184902155, "cost": {"min": 720000000, "max": 1090000000}},
            "Black Cat": {"type": "combat", "xp": 25353230, "cost": {"min": 60000000, "max": 98000000}},
            "Elephant": {"type": "farming", "xp": 25353230, "cost": {"min": 18500000, "max": 25000000}}}

# and the custom prices in md.itemList

#%% Lots of Lists you should not touch

bazaar_buy_types = {"Buy Order": "sellPrice", "Insta Buy": "buyPrice", "Custom": "custom"}
bazaar_sell_types = {"Sell Offer": "buyPrice", "Insta Sell": "sellPrice", "Custom": "custom"}

hopper_data = {
    "None": 1,
    "Budget Hopper": 0.5,
    "Enchanted Hopper": 0.9,
    "NPC": 1,
    "Bazaar": 1,
    "Best (NPC/Bazaar)": 1
}

reduced_amounts = {0: "", 1: "k", 2: "M", 3: "B", 4: "T"}


#%% Main Class


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        # Use Hktiner to initialize the window and the frames with grids
        self.hk = Hkinter.Hk(main=self, windowTitle="Minion Calculator", windowWidth=1450, windowHeight=700, palette="dark")
        print("BOOTING: Hkinter loaded")
        self.hk.createFrames(frame_keys=[["inputs_minion", "inputs_player", "outputs_setup", "outputs_profit"]], grid_frames=True, grid_size=0.96, border=0.003)
        print("BOOTING: Framework set up")
        self.version = self.hk.defVar(dtype=float, initial=1)
        print(f"BOOTING: Calculator version {self.version.get()}")

        # The calculator stores all important variables into this dict
        # the keys "vtype", "dtype", "frame", "noWidget" and "switch_initial"
        #     change how and where the calculator makes the inputs and outputs for each variable
        # "display" is used whenever a human-readable form of the variable is needed
        # "initial" is the initial value of the variable
        # "options" is a list of options for the variable, also used for encoding and decoding setup IDs
        # for "vtype" equal to list are extra keys: "w", "h" and "list".
        #     "w" and "h" are the width and height of the listbox widget.
        #     "list" is a normal list-like variable, most of the time a dict. This is the actual storage of the list.
        #     "var" is connected to the listbox, "list" can be shaped and put into "var" in the function self.update_GUI()
        self.variables = {"minion": {"vtype": "input", "dtype": str, "display": "Minion", "frame": "inputs_minion_grid", "initial": "Custom", "options": list(md.minionList.keys()), "command": self.load_minion},
                          "miniontier": {"vtype": "input", "dtype": int, "display": "Tier", "frame": "inputs_minion_grid", "initial": 12, "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "command": self.load_minion},
                          "amount": {"vtype": "input", "dtype": int, "display": "Amount", "frame": "inputs_minion_grid", "initial": 1, "options": [], "command": None},
                          "fuel": {"vtype": "input", "dtype": str, "display": "Fuel", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.fuel_options.keys()), "command": self.load_fuel},
                          "infernoGrade": {"vtype": "input", "dtype": str, "display": "Grade", "frame": "inputs_minion_grid", "initial": "Hypergolic Gabagool", "options": [md.itemList[grade]["display"] for grade in md.infernofuel_data["grades"].keys()], "command": None},
                          "infernoDistilate": {"vtype": "input", "dtype": str, "display": "Distilate", "frame": "inputs_minion_grid", "initial": "Crude Gabagool Distillate", "options": [md.itemList[dist]["display"] for dist in md.infernofuel_data["distilates"].keys()], "command": None},
                          "infernoEyedrops": {"vtype": "input", "dtype": bool, "display": "Eyedrops", "frame": "inputs_minion_grid", "initial": True, "options": [False, True], "command": None},
                          "hopper": {"vtype": "input", "dtype": str, "display": "Hopper", "frame": "inputs_minion_grid", "initial": "None", "options": list(hopper_data.keys()), "command": self.load_hopper},
                          "upgrade1": {"vtype": "input", "dtype": str, "display": "Upgrade 1", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.upgrade_options.keys()), "command": None},
                          "upgrade2": {"vtype": "input", "dtype": str, "display": "Upgrade 2", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.upgrade_options.keys()), "command": None},
                          "chest": {"vtype": "input", "dtype": str, "display": "Chest", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.minion_chests.keys()), "command": None},
                          "beacon": {"vtype": "input", "dtype": int, "display": "Beacon", "frame": "inputs_minion_grid", "initial": 0, "options": [0, 1, 2, 3, 4, 5], "command": self.load_beacon},
                          "scorched": {"vtype": "input", "dtype": bool, "display": "Scorched", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
                          "B_constant": {"vtype": "input", "dtype": bool, "display": "Constant Beacon", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
                          "B_acquired": {"vtype": "input", "dtype": bool, "display": "Acquired Beacon", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
                          "infusion": {"vtype": "input", "dtype": bool, "display": "Infusion", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
                          "crystal": {"vtype": "input", "dtype": str, "display": "Crystal", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.floating_crystals.keys()), "command": None},
                          "afk": {"vtype": "input", "dtype": bool, "display": "AFK", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
                          "afkpet": {"vtype": "input", "dtype": float, "display": "AFK Pet level", "frame": "inputs_player_grid", "initial": 0.0, "options": [], "command": None},
                          "specialSetup": {"vtype": "input", "dtype": bool, "display": "Special setup", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
                          "potatoTalisman": {"vtype": "input", "dtype": bool, "display": "Potato talisman", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
                          "combatWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "initial": 0.0, "options": []},
                          "miningWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "initial": 0.0, "options": []},
                          "farmingWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "initial": 0.0, "options": []},
                          "fishingWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "initial": 0.0, "options": []},
                          "foragingWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "initial": 0.0, "options": []},
                          "alchemyWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "initial": 0.0, "options": []},
                          "wisdom": {"vtype": "list", "display": "Wisdom", "frame": "inputs_player_grid", "w": None, "h": 6, "list": {}},
                          "mayor": {"vtype": "input", "dtype": str, "display": "Mayor", "frame": "inputs_player_grid", "initial": "None", "options": ["None", "Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul", "Jerry", "Derpy", "Scorpius"], "command": None},
                          "levelingpet": {"vtype": "input", "dtype": str, "display": "Leveling pet", "frame": "inputs_player_grid", "initial": "None", "options": list(pet_data.keys()), "command": lambda x: self.hk.toggleSwitch("pet_leveling", x)},
                          "taming": {"vtype": "input", "dtype": float, "display": "Taming", "frame": "inputs_player_grid", "initial": 0.0, "options": [], "command": None},
                          "petxpboost": {"vtype": "input", "dtype": str, "display": "Pet XP boost", "frame": "inputs_player_grid", "initial": "None", "options": list(md.pet_xp_boosts.keys()), "command": None},
                          "beastmaster": {"vtype": "input", "dtype": float, "display": "Beastmaster", "frame": "inputs_player_grid", "initial": 0.0, "options": [], "command": None},
                          "bazaar_sell_type": {"vtype": "input", "dtype": str, "display": "Bazaar sell type", "frame": "inputs_player_grid", "initial": "Sell Offer", "options": list(bazaar_sell_types.keys()), "command": None},
                          "bazaar_buy_type": {"vtype": "input", "dtype": str, "display": "Bazaar buy type", "frame": "inputs_player_grid", "initial": "Buy Order", "options": list(bazaar_buy_types.keys()), "command": None},
                          "bazaar_taxes": {"vtype": "input", "dtype": bool, "display": "Bazaar taxes", "frame": "inputs_player_grid", "initial": True, "options": [False, True], "command": self.load_tax},
                          "bazaar_flipper": {"vtype": "input", "dtype": int, "display": "Bazaar Flipper", "frame": "inputs_player_grid", "initial": 1, "options": [0, 1, 2], "command": None},
                          "ID": {"vtype": "output", "dtype": str, "display": "Setup ID", "frame": "outputs_setup_grid", "initial": "", "switch_initial": True},
                          "time": {"vtype": "output", "dtype": str, "display": "Time", "frame": "outputs_setup_grid", "initial": "1.0 Days", "switch_initial": True},
                          "actiontime": {"vtype": "output", "dtype": float, "display": "Action time (s)", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
                          "harvests": {"vtype": "output", "dtype": float, "display": "Harvests", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
                          "items": {"vtype": "list", "display": "Item amounts", "frame": "outputs_setup_grid", "w": 35, "h": None, "list": {}, "switch_initial": False, "IDtoDisplay": True},
                          "sellLoc": {"vtype": "list", "display": "Sell locations", "frame": "outputs_profit_grid", "w": 35, "h": None, "list": {}, "switch_initial": False, "IDtoDisplay": True},
                          "filltime": {"vtype": "output", "dtype": float, "display": "Fill time", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
                          "itemtypeProfit": {"vtype": "list", "display": "Itemtype profits", "frame": "outputs_profit_grid", "w": 35, "h": None, "list": {}, "switch_initial": False, "IDtoDisplay": True},
                          "itemProfit": {"vtype": "output", "dtype": float, "display": "Total item profit", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": False},
                          "xp": {"vtype": "list", "display": "XP amounts", "frame": "outputs_setup_grid", "w": 35, "h": 4, "list": {}, "switch_initial": False},
                          "petxp": {"vtype": "output", "dtype": float, "display": "Pet XP", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
                          "petProfit": {"vtype": "output", "dtype": float, "display": "Pet profit", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": False},
                          "fuelcost": {"vtype": "output", "dtype": float, "display": "Fuel cost", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": False},
                          "totalProfit": {"vtype": "output", "dtype": float, "display": "Total profit", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": True},
                          "notes": {"vtype": "list", "display": "Notes", "frame": "outputs_setup_grid", "w": 35, "h": 4, "list": {}, "switch_initial": False},
                          "bazaar_update_txt": {"vtype": "output", "dtype": str, "display": "Bazaar data", "frame": "outputs_profit_grid", "initial": "Not Loaded", "switch_initial": True},
                          "setupcost": {"vtype": "output", "dtype": float, "display": "Setup cost", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": True},
                          }

        # determining input/output types according to "vtype", "noWidget" and "switch_initial"
        # the other values are send to Hkinter. Hkinter creates the Tkinter variable and widgets (stored in "var" and "widget" respectively)
        for var_key, var_data in self.variables.items():
            if var_data["vtype"] == "input" and "noWidget" not in var_data:
                var_data["var"], var_data["widget"] = self.hk.defVarI(dtype=var_data["dtype"], frame=self.frames[var_data["frame"]],
                                                                      L_text=f"{var_data['display']}:", initial=var_data["initial"],
                                                                      options=var_data["options"], cmd=var_data["command"])
            elif var_data["vtype"] == "output":
                var_data["var"], var_data["widget"] = self.hk.defVarO(dtype=var_data["dtype"], frame=self.frames[var_data["frame"]],
                                                                      L_text=f"{var_data['display']}:", initial=var_data["initial"])
            elif var_data["vtype"] == "input" and "noWidget" in var_data:
                var_data["var"] = self.hk.defVar(dtype=var_data["dtype"], initial=var_data["initial"])
            elif var_data["vtype"] == "list":
                var_data["var"], var_data["widget"] = self.hk.defListO(frame=self.frames[var_data["frame"]], L_text=f"{var_data['display']}:", h=var_data["h"], w=var_data["w"])
            if "switch_initial" in var_data:
                self.variables[var_key]["output_switch"], widget = self.hk.defVarI(dtype=bool, frame=self.frames[self.variables[var_key]["frame"]], L_text="", initial=self.variables[var_key]["switch_initial"])
                var_data["widget"].append(widget[-1])

        # define left over Tkinter variables and widgets that didnt fit in self.variables
        self.template, self.templateI = self.hk.defVarI(dtype=str, frame=self.frames["inputs_minion_grid"], L_text="Templates:", initial="Clean", options=templateList.keys(), cmd=self.load_template)
        self.loadID, self.loadIDI = self.hk.defVarI(dtype=str, frame=self.frames["inputs_minion_grid"], L_text="Load ID:")

        for skill in ['combat', 'mining', 'farming', 'fishing', 'foraging', 'alchemy']:
            self.variables["wisdom"]["list"][skill] = self.variables[f"{skill}Wisdom"]["var"]
        self.wisdomB = tk.Button(self.frames["inputs_player_grid"], text='Edit', command=self.wisdom_edit)
        self.wisdomB.place(in_=self.variables["wisdom"]["widget"][-1], relx=1, x=3, rely=0.5, anchor='w')

        self.timeamount, self.timeamountI = self.hk.defVarI(dtype=float, frame=self.frames["inputs_player_grid"], L_text="Time span:", initial=1.0)
        self.timelength, self.timelengthI = self.hk.defVarI(dtype=str, frame=self.frames["inputs_player_grid"], L_text="Time Length:", initial="Days", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.timelengthI[-1].place(in_=self.timeamountI[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.setupIDA = self.hk.genLabel(frm=self.frames["outputs_setup_grid"], txt="")
        self.variables["ID"]["widget"][1].place(in_=self.setupIDA, relx=1, x=10, rely=0.5, anchor='w')

        print("BOOTING: self.variables initialized")

        # Create widgets for controls menu and placing them
        self.creditLB = self.hk.genLabel(frm=self.frames["controls"], txt=f"Minion Calculator V{self.version.get()}\nMade by Herodirk")
        self.creditLB.place(in_=self.stopB, x=-10, rely=0.5, y=-1, anchor="e")
        self.manualLB = self.hk.genLabel(frm=self.frames["controls"], txt="Online Manual:\nhttps://herodirk.github.io/")
        self.manualLB.place(in_=self.creditLB, x=-10, rely=0.5, anchor="e")

        self.outputB = tk.Button(self.frames["controls"], text='Short Output', command=self.output_data)
        self.fancyoutputB = tk.Button(self.frames["controls"], text='Share Output', command=self.fancyOutput)
        self.calcB = tk.Button(self.frames["controls"], text='Calculate', command=self.calculate)
        self.statusC = tk.Canvas(self.frames["controls"], bg="green", width=10, height=10, borderwidth=0)
        self.loopB = tk.Button(self.frames["controls"], text="Loop all minions", command=self.loop_minions)
        self.bazaarB = tk.Button(self.frames["controls"], text="Update Bazaar", command=self.update_bazaar)
        self.saveB = tk.Button(self.frames["controls"], text="Save Calculation", command=self.save_calc)

        controlsGrid = [self.calcB, self.statusC, self.outputB, self.fancyoutputB, self.bazaarB]
        self.hk.fill_arr(controlsGrid, self.frames["controls"])

        # Create miscellaneous labels
        miniontitleLB = self.hk.genLabel(frm=self.frames["inputs_minion_grid"], txt="\nMinion options")
        playertitleLB = self.hk.genLabel(frm=self.frames["inputs_player_grid"], txt="Player options")
        othertitleLB = self.hk.genLabel(frm=self.frames["inputs_player_grid"], txt="\nOther options")
        setupoutputsLB = self.hk.genLabel(frm=self.frames["outputs_setup_grid"], txt="Setup Outputs")
        setupprintLB = self.hk.genLabel(frm=self.frames["outputs_setup_grid"], txt="Print")
        profitoutputsLB = self.hk.genLabel(frm=self.frames["outputs_profit_grid"], txt="Profit Outputs")
        profitprintLB = self.hk.genLabel(frm=self.frames["outputs_profit_grid"], txt="Print")

        # Defining the order of widgets and placing them for all the grids
        self.grids = {"inputs_minion_grid": {"template": self.templateI,
                                             "ID": self.loadIDI,
                                             "minion_label": [None, miniontitleLB],
                                             "minion": self.variables["minion"]["widget"],
                                             "miniontier": self.variables["miniontier"]["widget"],
                                             "amount": self.variables["amount"]["widget"],
                                             "fuel": self.variables["fuel"]["widget"],
                                             "infernoGrade": self.variables["infernoGrade"]["widget"],
                                             "infernoDistilate": self.variables["infernoDistilate"]["widget"],
                                             "infernoEyedrops": self.variables["infernoEyedrops"]["widget"],
                                             "hopper": self.variables["hopper"]["widget"],
                                             "upgrade1": self.variables["upgrade1"]["widget"],
                                             "upgrade2": self.variables["upgrade2"]["widget"],
                                             "chest": self.variables["chest"]["widget"],
                                             "beacon": self.variables["beacon"]["widget"],
                                             "scorched": self.variables["scorched"]["widget"],
                                             "B_constant": self.variables["B_constant"]["widget"],
                                             "B_acquired": self.variables["B_acquired"]["widget"],
                                             "infusion": self.variables["infusion"]["widget"],
                                             "crystal": self.variables["crystal"]["widget"]
                                             },
                      "inputs_player_grid": {"player_label": [None, playertitleLB],
                                             "afk": self.variables["afk"]["widget"],
                                             "afkpet": self.variables["afkpet"]["widget"],
                                             "specialSetup": self.variables["specialSetup"]["widget"],
                                             "potatoTalisman": self.variables["potatoTalisman"]["widget"],
                                             "wisdom": self.variables["wisdom"]["widget"],
                                             "mayor": self.variables["mayor"]["widget"],
                                             "levelingpet": self.variables["levelingpet"]["widget"],
                                             "taming": self.variables["taming"]["widget"],
                                             "petxpboost": self.variables["petxpboost"]["widget"],
                                             "beastmaster": self.variables["beastmaster"]["widget"],
                                             "other_label": [None, othertitleLB],
                                             "time": self.timeamountI,
                                             "bazaar_sell_type": self.variables["bazaar_sell_type"]["widget"],
                                             "bazaar_buy_type": self.variables["bazaar_buy_type"]["widget"],
                                             "bazaar_taxes": self.variables["bazaar_taxes"]["widget"],
                                             "bazaar_flipper": self.variables["bazaar_flipper"]["widget"]
                                             },
                      "outputs_setup_grid": {"labels": [None, setupoutputsLB, setupprintLB],
                                             "ID": [self.variables["ID"]["widget"][0], None, self.variables["ID"]["widget"][2]],
                                             "ID_anchor": [self.setupIDA],
                                             "time": self.variables["time"]["widget"],
                                             "actiontime": self.variables["actiontime"]["widget"],
                                             "harvests": self.variables["harvests"]["widget"],
                                             "items": self.variables["items"]["widget"],
                                             "xp": self.variables["xp"]["widget"],
                                             "petxp": self.variables["petxp"]["widget"],
                                             "notes": self.variables["notes"]["widget"],
                                             },
                      "outputs_profit_grid": {"labels": [None, profitoutputsLB, profitprintLB],
                                              "bazaar_update_txt": self.variables["bazaar_update_txt"]["widget"],
                                              "setupcost": self.variables["setupcost"]["widget"],
                                              "sellLoc": self.variables["sellLoc"]["widget"],
                                              "itemtypeProfit": self.variables["itemtypeProfit"]["widget"],
                                              "itemProfit": self.variables["itemProfit"]["widget"],
                                              "petProfit": self.variables["petProfit"]["widget"],
                                              "fuelcost": self.variables["fuelcost"]["widget"],
                                              "totalProfit": self.variables["totalProfit"]["widget"]
                                              }
                      }
        for grid_key in self.grids.keys():
            self.hk.fill_grid(self.grids[grid_key].values(), self.frames[grid_key])
        print("BOOTING: Widgets placed")

        # Create switches with Hkinter for the extended minion options
        self.hk.defSwitch("pet_leveling", [*self.variables["taming"]["widget"], *self.variables["petxpboost"]["widget"], *self.variables["beastmaster"]["widget"],
                                           *self.variables["petxp"]["widget"], *self.variables["petProfit"]["widget"]],
                          loc="grid", control="None", negate=True, initial=False)
        self.hk.defSwitch("NPC_Bazaar", [*self.variables["sellLoc"]["widget"]],
                          loc="grid", control="Best (NPC/Bazaar)", negate=False, initial=False)
        self.hk.defSwitch("infernofuel", [*self.variables["infernoGrade"]["widget"], *self.variables["infernoDistilate"]["widget"], *self.variables["infernoEyedrops"]["widget"]],
                          loc="grid", control="Inferno Minion Fuel", negate=False, initial=False)
        self.hk.defSwitch("beacon", [*self.variables["scorched"]["widget"], *self.variables["B_constant"]["widget"], *self.variables["B_acquired"]["widget"]],
                          loc="grid", control=0, negate=True, initial=False)
        self.hk.defSwitch("potato", [*self.variables["potatoTalisman"]["widget"]],
                          loc="grid", control="Potato", negate=False, initial=False)
        self.hk.defSwitch("bazaar_tax", [*self.variables["bazaar_flipper"]["widget"]],
                          loc="grid", control=1, negate=False, initial=True)
        print("BOOTING: Switches activated")

        # Define output orders for Short Output (self.outputOrder) and Share Output (self.fancyOrder)
        self.outputOrder = ['ID', 'fuel', 'hopper', 'upgrade1', 'upgrade2', 'chest',
                            'beacon', 'scorched', 'B_constant', 'B_acquired',
                            'infusion', 'crystal', 'afk', 'afkpet', 'specialSetup', 'potatoTalisman',
                            'wisdom', 'mayor', 'levelingpet', 'taming', 'petxpboost', 'beastmaster',
                            'time', 'actiontime', 'harvests', 'items', 'sellLoc',
                            'itemtypeProfit', 'itemProfit', 'xp', 'petxp', 'petProfit',
                            'fuelcost', 'totalProfit', 'notes',
                            'bazaar_update_txt', 'bazaar_taxes', 'bazaar_flipper',
                            'setupcost']

        self.fancyOrder = {"**Minion Upgrades**": {"\n> Internal: ": {"fuel", "hopper", "upgrade1", "upgrade2"},
                                                   "\n> External: ": {"chest", "beacon", "infusion", "crystal"}},
                           "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
                           "Fuel Info": {"\n> ": ["infernoGrade", "infernoDistilate", "infernoEyedrops"]},
                           "afk": {"\n> ": ["afkpet", "specialSetup", "potatoTalisman"]},
                           "wisdom": None,
                           "mayor": None,
                           "levelingpet": {"\n> ": ["taming", "petxpboost", "beastmaster"]},
                           "**Setup Information**": {"\n> ": ("ID", "actiontime", "harvests", "setupcost")},
                           "Bazaar Info": {"\n> ": ["bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper"]},
                           "notes": None,
                           "**Outputs** for ": {"": {"time"}},
                           "items": None,
                           "sellLoc": None,
                           "itemProfit": {"": {"itemtypeProfit"}},
                           "xp": None,
                           "petProfit": {"\n> ": ["petxp"]},
                           "fuelcost": None,
                           "totalProfit": None}
        print("BOOTING: Output orders defined")

        # Load bazaar prices
        print("BOOTING: Connecting to bazaar")
        self.bazaar_timer = 0
        self.update_bazaar(cooldown_warning=False)
        print("BOOTING: Complete")
        return

#%% functions

    def time_number(self, secondsPaction, actionsPerHarvest):
        """
        Translates time amount and length into seconds.

        Parameters
        ----------
        secondsPaction : float
            Seconds per action. Used to calculate the amount of seconds in one harvest.
        actionsPerHarvest : float
            Actions per harvest. Used to calculate the amount of seconds in one harvest.

        Returns
        -------
        float
            The inputted time amount and length as seconds.

        """
        time_length = self.timelength.get()
        time_amount = self.timeamount.get()
        self.variables["time"]["var"].set(f"{time_amount} {time_length}")
        if time_length == "Years":
            return 31536000 * time_amount
        if time_length == "Weeks":
            return 604800 * time_amount
        if time_length == "Days":
            return 86400 * time_amount
        if time_length == "Hours":
            return 3600 * time_amount
        if time_length == "Minutes":
            return 60 * time_amount
        if time_length == "Seconds":
            return 1 * time_amount
        if time_length == "Harvests":
            return secondsPaction * actionsPerHarvest * time_amount
        return 1 * time_amount

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
        if number == 0.0:
            return str(0)
        elif np.abs(number) < 1:
            return str(np.round(number, 1 + int(np.abs(np.floor(np.log10(np.abs(number)))))))
        highest_reduction = min(int(np.floor(np.log10(np.abs(number))) / 3), 4)
        reduced = np.round((number / (10 ** (3 * highest_reduction))), decimal)
        output_string = f'{reduced}{reduced_amounts[highest_reduction]}'
        return output_string

    def wisdom_edit(self):
        """
        Aks for wisdom values using Hkinters input_vars() function
        Puts the inputted values into the wisdom list
        Calls a GUI update for the wisdom listbox

        Returns
        -------
        None.

        """
        new_wisdoms = self.hk.input_vars({skill: var.get() for skill, var in self.variables["wisdom"]["list"].items()})
        if new_wisdoms is None or new_wisdoms[0] is None:
            return
        for var, val in zip(self.variables["wisdom"]["list"].values(), new_wisdoms):
            var.set(val)
        self.update_GUI_wisdom()
        return

    def update_GUI_wisdom(self):
        """
        Updates the wisdom listbox
        Does not display wisdom values equal to 0

        Returns
        -------
        None.

        """
        display_wisdoms = []
        for skill, var in self.variables["wisdom"]["list"].items():
            val = var.get()
            if val == 0.0:
                continue
            display_wisdoms.append(f"{skill}: {val}")
        self.variables["wisdom"]["var"].set(display_wisdoms)
        return

    def load_minion(self, minionName):
        """
        Sets minion tier to the maximum tier of that minion.
        Sets minion tier to maximum if the chosen tier is not in the system yet.
        Toggles switches related to minion name or tier.

        Parameters
        ----------
        minionName : str or int
            Minion name if the function was called from the minion type widget.
            Minion tier if it was called from the minion tier widget.

        Returns
        -------
        None.

        """
        if type(minionName) == str or self.variables["miniontier"]["var"].get() not in md.minionList[self.variables["minion"]["var"].get()]["speed"].keys():
            self.variables["miniontier"]["var"].set(list(md.minionList[self.variables["minion"]["var"].get()]["speed"].keys())[-1])
        if type(minionName) == str:
            self.hk.toggleSwitch("potato", minionName)
        return

    def load_template(self, templateName):
        """
        Handles the input from the template input.
        If "ID" is selected it sends the inputted ID to the decoder.
        If "Clean" is selected it sets every self.variable with "vtype" equal to "input" to its "initial".
        Otherwise it is a key from templateList which has as value a dict with self.variable keys and values.
        If the self.variable has a load function with switches, it runs that too.

        Parameters
        ----------
        templateName : str
            Name of the template. Must be a key in templateList.

        Returns
        -------
        None.

        """
        if templateName == "ID":
            template = self.decodeID(self.loadID.get())
        elif templateName == "Clean":
            template = {var_key: self.variables[var_key]["initial"] for var_key in self.variables if self.variables[var_key]["vtype"] == "input" and var_key not in ["minion", "miniontier"]}
        else:
            template = templateList[templateName]
        for setting, variable in template.items():
            self.variables[setting]["var"].set(variable)
            if setting == "bazaar_taxes":
                self.load_tax()
            elif "command" in self.variables[setting] and self.variables[setting]["command"] is not None:
                self.variables[setting]["command"](variable)
            if "Wisdom" in setting:
                self.update_GUI_wisdom()
        return

    def load_fuel(self, fuelName):
        """
        Toggles the switch of inferno fuel settings

        Parameters
        ----------
        fuelName : str
            Name of the selected fuel.

        Returns
        -------
        None.

        """
        self.hk.toggleSwitch("infernofuel", fuelName)
        return

    def load_hopper(self, hopperName):
        """
        Toggles the switch of sell location output listbox

        Parameters
        ----------
        hopperName : str
            Name of the selected hopper.

        Returns
        -------
        None.

        """
        self.hk.toggleSwitch("NPC_Bazaar", hopperName)
        return

    def load_beacon(self, beaconTier):
        """
        Toggles the switch of beacon settings

        Parameters
        ----------
        hopperName : int
            Tier of the selected beacon.

        Returns
        -------
        None.

        """
        self.hk.toggleSwitch("beacon", beaconTier)
        return

    def load_tax(self):
        """
        Toggles the switch of Bazaar Flipper

        Parameters
        ----------
        taxSwitch : bool
            Selected state for bazaar taxes.

        Returns
        -------
        None.

        """
        self.hk.toggleSwitch("bazaar_tax", self.variables["bazaar_taxes"]["var"].get())
        return

    def output_data(self, toTerminal=True):
        """
        Generates a short output string with all relavent inputs and chosen ouputs.
        The order of these inputs and output in the output string is defined in self.outputOrder in __init__().
        If toTerminal is True it also prints the string to terminal.

        Parameters
        ----------
        toTerminal : bool, optional
            Toggle for printing to terminal. The default is True.

        Returns
        -------
        crafted_string : str
            Output string. If toTerminal is True, this function returns None.

        """
        crafted_string = f'{self.variables["amount"]["var"].get()}x {self.variables["minion"]["var"].get()} t{self.variables["miniontier"]["var"].get()}, '
        special_string = ""
        inputs_string = ""
        outputs_string = ""
        for variable_key in self.outputOrder:
            vtype = self.variables[variable_key]["vtype"]
            if "output_switch" in self.variables[variable_key] and self.variables[variable_key]["output_switch"].get() is False:
                continue
            if variable_key == "afkpet" and self.variables["afk"]["var"].get() is False:
                continue
            if variable_key == "wisdom":
                val_list = {list_key: var.get() for list_key, var in self.variables["wisdom"]["list"].items() if var.get() not in ["None", 0, 0.0]}
                if len(val_list) != 0:
                    inputs_string += self.variables["wisdom"]["display"] + ": " + str(val_list) + ", "
                continue
            if variable_key == "bazaar_update_txt":
                special_string += f'Bazaar info: {self.variables["bazaar_sell_type"]["var"].get()}, {self.variables["bazaar_buy_type"]["var"].get()}, Last updated at {self.variables["bazaar_update_txt"]["var"].get()},\n'
                continue

            display = self.variables[variable_key]["display"]
            if vtype == "list":
                val_list = deepcopy(self.variables[variable_key]["list"])
                for val_key, val_value in val_list.items():
                    if type(val_value) in [int, float]:
                        val_list[val_key] = self.reduced_number(val_value)
                outputs_string += f"{display}: {val_list}, "
                continue

            dtype = self.variables[variable_key]["dtype"]
            val = self.variables[variable_key]["var"].get()
            if vtype == "input":
                if val in ["None", 0, 0.0]:
                    continue
                if dtype in [int, float, bool]:
                    inputs_string += f"{display}: {val}, "
                elif val == "Inferno Minion Fuel":
                    inputs_string += f'Inferno Minion Fuel ({self.variables["infernoGrade"]["var"].get()}, {self.variables["infernoDistilate"]["var"].get()}, Capcaisin: {self.variables["infernoEyedrops"]["var"].get()}), '
                else:
                    inputs_string += f"{val}, "
            elif vtype == "output":
                if dtype in [int, float]:
                    outputs_string += f"{display}: {self.reduced_number(val)}, "
                else:
                    outputs_string += f"{display}: {val}, "

        crafted_string += inputs_string + "\n" + special_string + outputs_string
        if toTerminal is True:
            print(crafted_string, "\n")
            return
        else:
            return crafted_string

    def prep_fancy_data(self, var_key, display=True, newline=False):
        """
        Subfunction for fancyOutput().
        This function generate the part of the Share Output for the inputted self.variables key
        with toggles if the self.variable "display" should be shown and if a new line should be put at the end.
        Returns None if the self.variable has "output_switch" set to False.
        Returns None if the value of the self.variable is equivalent to 0, except if "output_switch" is True.

        Parameters
        ----------
        var_key : str
            A self.variables key.
        display : bool, optional
            Toggle for if the self.variable "display" should be shown. The default is True.
        newline : bool, optional
            Toggle for if a new line should be put at the end. The default is False.

        Returns
        -------
        str
            The part of the Share Output for the inputted self.variables key.

        """
        force = False
        if "output_switch" in self.variables[var_key]:
            if self.variables[var_key]["output_switch"].get() is False:
                if var_key == "notes" and self.variables["specialSetup"]["var"].get() is True and "Special setup" in self.variables["notes"]["list"]:
                    return f"Notes:\n> Special setup: `{self.variables['notes']['list']['Special setup']}`"
                else:
                    return None
            else:
                force = True
        if var_key == "wisdom":
            val_list = {list_key: var.get() for list_key, var in self.variables["wisdom"]["list"].items() if var.get() not in ["None", 0, 0.0]}
            if len(val_list) != 0:
                return self.variables["wisdom"]["display"] + ":\n> " + ", ".join(f"{list_key}: `{list_val}`" for list_key, list_val in val_list.items())
            return None
        elif var_key == "beacon":
            val = {0: "", 1: "`Beacon I`", 2: "`Beacon II`", 3: "`Beacon III`", 4: "`Beacon IV`", 5: "`Beacon V`"}[self.variables[var_key]["var"].get()]
        elif var_key == "infusion":
            if self.variables["infusion"]["var"].get() is True:
                val = "`Infusion`"
            else:
                return None
        elif var_key == "ID":
            val = f"||{self.variables[var_key]['var'].get()}||"
        elif self.variables[var_key]["vtype"] == "list":
            if "IDtoDisplay" in self.variables[var_key] and self.variables[var_key]["IDtoDisplay"] is True:
                val = "\n> " + ", ".join(f"{md.itemList[list_key]['display']}: `{self.reduced_number(list_val)}`" if type(list_val) in [float, int] else f"{md.itemList[list_key]['display']}: `{list_val}`" for list_key, list_val in self.variables[var_key]["list"].items())
            else:
                val = "\n> " + ", ".join(f"{list_key}: `{self.reduced_number(list_val)}`" if type(list_val) in [float, int] else f"{list_key}: `{list_val}`" for list_key, list_val in self.variables[var_key]["list"].items())
        elif self.variables[var_key]["dtype"] in [int, float]:
            val = f"`{self.reduced_number(self.variables[var_key]['var'].get())}`"
        else:
            val = f"`{self.variables[var_key]['var'].get()}`"
        if val in ["`None`", "`0`", "`0.0`", "", "`False`"] and force is False:
            return None
        return_str = ""
        if display:
            return_str += f"{self.variables[var_key]['display']}: "
        return_str += f"{val}"
        if newline:
            return_str += "\n"
        return return_str

    def fancyOutput(self, toTerminal=True):
        """
        Generates the Share Output. The Share Output is meant for sharing through discord as it uses discords markdown features.
        This function combines the outputs of prep_fancy_data() in the order given by self.fancyOrder as defined in __init__().

        Parameters
        ----------
        toTerminal : bool, optional
            Toggle for printing to terminal. The default is True.

        Returns
        -------
        crafted_string : str
            Output string. If toTerminal is True, this function returns None.

        """
        crafted_string = f'{self.variables["amount"]["var"].get()}x **{self.variables["minion"]["var"].get()} t{self.variables["miniontier"]["var"].get()}**'
        for key in self.fancyOrder:
            line_str = ""
            header = ""
            force_line = False
            if key in self.variables:
                header = self.prep_fancy_data(key)
                force_line = True
            else:
                header = key
            if header is None:
                continue
            if header == "Beacon Info" and self.variables["beacon"]["var"].get() == 0:
                continue
            if header == "Fuel Info" and self.variables["fuel"]["var"].get() != "Inferno Minion Fuel":
                continue
            if header == "Bazaar Info" and self.variables["bazaar_update_txt"]["output_switch"].get() is False:
                continue
            if type(self.fancyOrder[key]) is dict:
                for sub_key, key_arr in self.fancyOrder[key].items():
                    if type(key_arr) == list:
                        if (joined_keys := ", ".join(s for var_key in self.fancyOrder[key][sub_key] if (s := self.prep_fancy_data(var_key)) is not None)) != "":
                            line_str += sub_key + joined_keys
                    elif type(key_arr) == tuple:
                        if (joined_keys := sub_key.join(s for var_key in self.fancyOrder[key][sub_key] if (s := self.prep_fancy_data(var_key)) is not None)) != "":
                            line_str += sub_key + joined_keys
                    elif type(key_arr) == set:
                        if (joined_keys := ", ".join(s for var_key in self.fancyOrder[key][sub_key] if (s := self.prep_fancy_data(var_key, display=False)) is not None)) != "":
                            line_str += sub_key + joined_keys
            if line_str != "" or force_line is True:
                crafted_string += "\n" + header + line_str
        if toTerminal is True:
            print(crafted_string, "\n")
            return
        else:
            return crafted_string

    def constructID(self):
        """
        Generates the setup ID of the current inputted setup.
        A setup ID consists of:
            the version number of the minion calculator it was generated in\n
            the index of the set value in "options" of each self.variable with "vtype" equal to "input" encoded in ASCII with an offset of 48\n
            the set value surrounded by exclamation marks if a self.variable has an empty "options" list

        Returns
        -------
        ID : str
            Setup ID.

        """
        ID = str(self.version.get()) + "!"
        for key, var_data in self.variables.items():
            if var_data["vtype"] != "input":
                continue
            val = var_data["var"].get()
            if len(var_data["options"]) == 0:
                if int(val) == val:
                    val = int(val)
                ID += "!" + str(val) + "!"
            else:
                index = var_data["options"].index(val)
                ID += chr(48 + index)
        return ID

    def decodeID(self, ID):
        """
        Generates a template structure for load_template() from a given setup ID.

        Parameters
        ----------
        ID : str
            Setup ID.

        Returns
        -------
        dict
            Template structure for load_template().

        """
        template = {}
        end_ver = ID.find("!")
        if end_ver == -1:
            print("WARNING: Invalid ID, could not find version number")
            return template
        try:
            version = float(ID[0:end_ver])
        except Exception:
            print("WARNING: Invalid ID, could not find version number")
            return template
        ID_index = end_ver + 1
        if version != self.version.get():
            print("WARNING: Invalid ID: Incompatible version")
            return template
        try:
            for key, var_data in self.variables.items():
                if var_data["vtype"] != "input":
                    continue
                if len(var_data["options"]) == 0:
                    if ID[ID_index] != "!":
                        print(f"WARNING: did not find {key}")
                        return
                    end_val = ID.find("!", ID_index + 1)
                    template[key] = var_data["dtype"](ID[ID_index + 1:end_val])
                    ID_index = end_val + 1
                else:
                    template[key] = var_data["options"][ord(ID[ID_index]) - 48]
                    ID_index += 1
        except Exception as error:
            if type(error) == IndexError:
                print("WARNING: Invalid ID, ID incomplete")
                return {}
            else:
                print("ERROR: unknown error\ndumping error logs", error)
                return {}
        return template

    def getPrice(self, ID, action="buy", location="bazaar", force=False):
        """
        Returns the price of an item from ID, transaction type and location of transaction.
        Uses self.variables "bazaar_buy_type" and "bazaar_sell_type" for bazaar specifics.

        Parameters
        ----------
        ID : str
            Skyblock Item ID of which the price is needed.
        action : str, optional
            Type of transaction. "buy" or "sell". The default is "buy".
        location : str, optional
            Location of the transaction, "npc", "bazaar", "custom", "best". The default is "bazaar".
        force : bool, optional
            Toggle to force the location and action, if location is not found, this function returns -1

        Returns
        -------
        float
            price of the item.
        """
        multiplier = 1
        if location == "bazaar":
            if action == "buy":
                location = bazaar_buy_types[self.variables["bazaar_buy_type"]["var"].get()]
            elif action == "sell":
                location = bazaar_sell_types[self.variables["bazaar_sell_type"]["var"].get()]
                if self.variables["bazaar_taxes"]["var"].get():
                    bazaar_tax = 0.0125 - 0.00125 * self.variables["bazaar_flipper"]["var"].get()
                    if self.variables["mayor"]["var"].get() == "Derpy":
                        bazaar_tax *= 4
                    multiplier = 1 - bazaar_tax
        elif location == "npc" and action == "buy":
            multiplier = 2
        if ID in md.itemList:
            if location in md.itemList[ID]["prices"]:
                return multiplier * md.itemList[ID]["prices"][location]
            elif force:
                print("WARNING:", ID, "no forced cost found")
                return -1
            elif "npc" in md.itemList[ID]["prices"]:
                return multiplier * md.itemList[ID]["prices"]["npc"]
            elif "custom" in md.itemList[ID]["prices"]:
                return md.itemList[ID]["prices"]["custom"]
            else:
                print("WARNING:", ID, "no cost found")
                return 0
        else:
            print("WARNING:", ID, "not in itemList")
            return 0

    def getPetXP(self, xp_type, xp_amount):
        """
        Calculated gained pet xp from an xp amount and type

        Parameters
        ----------
        xp_type : str
            Type of skill XP.
        xp_amount : float
            Amount of xp.

        Returns
        -------
        int
            Amount of pet xp

        """
        pet = self.variables["levelingpet"]["var"].get()
        petxpbonus = (1 + self.variables["taming"]["var"].get() / 100) * (1 + self.variables["beastmaster"]["var"].get() / 100)
        if md.pet_xp_boosts[self.variables["petxpboost"]["var"].get()][0] in [xp_type, "all"] and pet not in ["Golden Dragon", "Golden Dragon (lvl 1-100)"]:
            petxpbonus *= 1 + md.pet_xp_boosts[self.variables["petxpboost"]["var"].get()][1] / 100
        if self.variables["mayor"]["var"].get() == "Diana":
            petxpbonus *= 1.35
        if xp_type in ["mining", "fishing"]:
            petxpbonus *= 1.5
        if pet_data[pet]["type"] != xp_type:
            if xp_type in ["alchemy", "enchanting"]:
                petxpbonus *= 1 / 12
            else:
                petxpbonus *= 1 / 3
        if pet == "Reindeer":
            petxpbonus *= 2
        pet_xp = xp_amount * petxpbonus
        return pet_xp

    def calculate(self, inGUI=True):
        """
        Main calculation

        Parameters
        ----------
        inGUI : bool, optional
            Toggles if there is a self.statusC canvas to update. The default is True.

        Returns
        -------
        None.

        """
        if inGUI is True:
            self.statusC.configure(bg="yellow")
            self.statusC.update()

        # auto update bazaar
        if bazaar_auto_update:
            self.update_bazaar(cooldown_warning=False)

        # clear list outputs from previous calculation
        for var_key, var_data in self.variables.items():
            if var_data["vtype"] == "list":
                if var_key == "wisdom":
                    continue
                var_data["list"].clear()

        # extracting often used minion constants
        minion_type = self.variables["minion"]["var"].get()
        minion_tier = self.variables["miniontier"]["var"].get()
        base_speed = md.minionList[minion_type]["speed"][minion_tier]
        minion_amount = self.variables["amount"]["var"].get()
        minion_fuel = md.fuel_options[self.variables["fuel"]["var"].get()]
        minion_hopper = self.variables["hopper"]["var"].get()
        minion_beacon = self.variables["beacon"]["var"].get()
        upgrades = [md.upgrade_options[self.variables["upgrade1"]["var"].get()], md.upgrade_options[self.variables["upgrade2"]["var"].get()]]

        # list upgrades types
        upgrades_types = []
        for upgrade in upgrades:
            for temp_type in md.itemList[upgrade]["upgrade"]["special"]["type"].split(", "):
                upgrades_types.append(temp_type)

        # adding up minion speed bonus
        # uses the fact that booleans can be seen as 0 or 1 or false and true resp.
        speedBonus = 0
        speedBonus += md.itemList[minion_fuel]["upgrade"]["speed"]
        speedBonus += md.itemList[upgrades[0]]["upgrade"]["speed"] + md.itemList[upgrades[1]]["upgrade"]["speed"]
        speedBonus += 2 * minion_beacon + 10 * self.variables["infusion"]["var"].get()
        speedBonus += 0.3 * self.variables["afkpet"]["var"].get() * self.variables["afk"]["var"].get()
        speedBonus += 5 * self.variables["potatoTalisman"]["var"].get() * self.variables["afk"]["var"].get() * (minion_type == "Potato")
        if self.variables["crystal"]["var"].get() != "None":
            if minion_type in list(md.floating_crystals[self.variables["crystal"]["var"].get()].values())[0]:
                speedBonus += list(md.floating_crystals[self.variables["crystal"]["var"].get()].keys())[0]
        if minion_beacon != 0:
            speedBonus += 1 * self.variables["scorched"]["var"].get()
        if minion_type == "Inferno":
            speedBonus += 18 * min(10, minion_amount)
        if self.variables["mayor"]["var"].get() == "Cole" and self.variables["afk"]["var"].get() and minion_type in [
                'Cobblestone', 'Obsidian', 'Glowstone', 'Gravel', 'Sand', 'Ice', 'Coal', 'Iron',
                'Gold', 'Diamond', 'Lapis', 'Redstone', 'Emerald', 'Quartz', 'End Stone', 'Mithril']:
            speedBonus += 25

        # multiply up minion drop bonus
        # For offline drop multipliers, it is only assumed that Derpy and Fuel work.
        # When AFKing, Derpy only doubles base drops. In the offline calculations, Derpy doubles everything that gets made in a minion.
        dropMultiplier_base = 1
        dropMultiplier_offline = 1
        dropMultiplier_base *= md.itemList[minion_fuel]["upgrade"]["drop"]
        dropMultiplier_base *= md.itemList[upgrades[0]]["upgrade"]["drop"]
        dropMultiplier_base *= md.itemList[upgrades[1]]["upgrade"]["drop"]
        if "SOULFLOW_ENGINE" in upgrades and minion_type == "Voidling":
            dropMultiplier_base *= 2 * (0.5 + 0.03 * minion_tier)  # needs testing
        if self.variables["mayor"]["var"].get() == "Derpy" and self.variables["afk"]["var"].get():
            dropMultiplier_base *= 2
        if not self.variables["afk"]["var"].get():
            dropMultiplier_offline *= md.itemList[minion_fuel]["upgrade"]["drop"]

        # AFKing and Special Setups
        actionsPerHarvest = 2
        if minion_type == "Fishing":
            # only has harvests actions
            actionsPerHarvest = 1
        if self.variables["afk"]["var"].get():
            if minion_type in ["Pumpkin", "Melon"]:
                # pumpkins and melons are forced to regrow for minion to harvest
                actionsPerHarvest = 1
            if self.variables["specialSetup"]["var"].get():
                if minion_type in ["Cobblestone", "Mycelium", "Ice", "Oak"]:
                    # cobblestone generator, regrowing mycelium, freezing water, player harvesting
                    actionsPerHarvest = 1
                if minion_type in ["Flower", "Sand", "Red Sand", "Gravel"]:
                    # harvests through natural means: water flushing, gravity
                    actionsPerHarvest = 1
                    speedBonus -= 10  # only spawning has 10% action speed reduction, not confirmed yet.

        # AFK loot table changes
        if minion_type in ['Oak', 'Spruce', 'Birch', 'Dark Oak', 'Acacia', 'Jungle']:
            if self.variables["afk"]["var"].get():
                # chopped trees have 4 blocks of wood, unknown why offline gives 3
                md.minionList[minion_type]["drops"][md.getID[f"{minion_type} Wood"]] = 4
            else:
                md.minionList[minion_type]["drops"][md.getID[f"{minion_type} Wood"]] = 3
        if minion_type == "Flower":
            if self.variables["afk"]["var"].get() and self.variables["specialSetup"]["var"].get():
                # tall flows blocked by string
                md.minionList[minion_type]["drops"] = {"YELLOW_FLOWER": 1 / 10, "RED_ROSE": 1 / 10, "SMALL_FLOWER": 8 / 10}
            else:
                md.minionList[minion_type]["drops"] = {"YELLOW_FLOWER": 1 / 14, "RED_ROSE": 1 / 14, "SMALL_FLOWER": 8 / 14, "LARGE_FLOWER": 4 / 14}

        # calculate final minion speed
        secondsPaction = base_speed / (1 + speedBonus / 100)
        if minion_fuel == "INFERNO_FUEL":
            secondsPaction /= 1 + md.infernofuel_data["grades"][md.getID[self.variables["infernoGrade"]["var"].get()]]

        # time calculations
        timeNumber = self.time_number(secondsPaction, actionsPerHarvest)
        if self.timelength.get() == "Harvests":
            harvestsPerTime = self.timeamount.get()
        else:
            harvestsPerTime = timeNumber / (actionsPerHarvest * secondsPaction)

        self.variables["actiontime"]["var"].set(secondsPaction)

        # base drops
        for item, amount in md.minionList[minion_type]["drops"].items():
            self.variables["items"]["list"][item] = harvestsPerTime * amount * dropMultiplier_base

        # upgrade drops
        # create seperate dict to keep it separate from the main drops
        # because some upgrades use main drops to generate something
        upgrade_drops = {}
        for upgrade in upgrades:
            upgrade_type = md.itemList[upgrade]["upgrade"]["special"]["type"]
            if "replace" in upgrade_type:
                # replacing upgrades are like Auto Smelters
                items = list(self.variables["items"]["list"].keys())
                for item in items:
                    if item in md.itemList[upgrade]["upgrade"]["special"]["list"]:
                        self.variables["items"]["list"][md.itemList[upgrade]["upgrade"]["special"]["list"][item]] = self.variables["items"]["list"].pop(item)
            if upgrade_type == "generate":
                # generating upgrades are like Diamond Spreadings
                finalAmount = 0
                for amount in self.variables["items"]["list"].values():
                    finalAmount += md.itemList[upgrade]["upgrade"]["special"]["chance"] * amount
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    upgrade_drops[item] = finalAmount * amount
            elif upgrade_type == "add":
                # adding upgrades are like Corrupt Soils
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    upgrade_drops[item] = harvestsPerTime * amount * dropMultiplier_offline
            elif upgrade_type == "timer":
                # timer upgrades are like Soulflow Engines
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    upgrade_drops[item] = amount * timeNumber / md.itemList[upgrade]["upgrade"]["special"]["cooldown"]

        # upgrades behavior when afking
        if self.variables["afk"]["var"].get() is True:
            if "CORRUPT_SOIL" in upgrades:
                if "afkcorrupt" in md.minionList[minion_type]:
                    # Certain mob minions get more corrupt drops when afking
                    # It is not a constant multiplier, it is chances equivalent to the main drop of the minion
                    upgrade_drops["SULPHUR_ORE"] *= md.minionList[minion_type]["afkcorrupt"]
                    upgrade_drops["CORRUPTED_FRAGMENT"] *= md.minionList[minion_type]["afkcorrupt"]
            if "ENCHANTED_EGG" in upgrades:
                # Enchanted Eggs make one laid egg and one egg on kill while AFKing
                upgrade_drops["EGG"] *= 2
        else:
            if "ENCHANTED_SHEARS" in upgrades:
                # No wool gets added from Enchanted Shears when offline
                upgrade_drops["WOOL"] = 0

        # Inferno minion fuel drops
        # https://wiki.hypixel.net/Inferno_Minion_Fuel
        if minion_fuel == "INFERNO_FUEL":
            # distilate drops
            distilate = md.getID[self.variables["infernoDistilate"]["var"].get()]
            distilate_item = md.infernofuel_data["distilates"][distilate][0]
            amount_per = md.infernofuel_data["distilates"][distilate][1]
            upgrade_drops[distilate_item] = 0
            # base_item_amount = 1 / 5 + (amount_per * 4) / 5
            static_items = list(self.variables["items"]["list"].items())  # create copy to edit list while looping it
            for item, amount in static_items:  # replacing main drops with distilate drops
                distilate_amount = (amount * 4) / 5
                upgrade_drops[distilate_item] += distilate_amount * amount_per
                self.variables["items"]["list"][item] /= 5

            # Hypergolic drops
            if self.variables["infernoGrade"]["var"].get() == "Hypergolic Gabagool":  # hypergolic fuel stuff
                multiplier = 1
                if self.variables["infernoEyedrops"]["var"].get() is True:  # Capsaicin Eyedrops
                    multiplier = 1.3
                for item, chance in md.infernofuel_data["drops"].items():
                    upgrade_drops[item] = 0
                    if item == "INFERNO_APEX" and minion_tier >= 10:  # Apex Minion perk
                        chance *= 2
                    upgrade_drops[item] += multiplier * chance * harvestsPerTime
                upgrade_drops["HYPERGOLIC_IONIZED_CERAMICS"] = timeNumber / md.itemList[minion_fuel]["upgrade"]["duration"]

            # calculate fuel cost
            infernofuel_components = {"INFERNO_FUEL_BLOCK": 2,  # 2 inferno fuel blocks
                                      distilate: 6,  # 6 times distilate item
                                      md.getID[self.variables["infernoGrade"]["var"].get()]: 1,  # 1 gabagool core
                                      "CAPSAICIN_EYEDROPS_NO_CHARGES": int(self.variables["infernoEyedrops"]["var"].get())  # capsaicin eyedrops
                                      }
            costPerInfernofuel = 0
            for component_ID, amount in infernofuel_components.items():
                costPerInfernofuel += amount * self.getPrice(component_ID, action="buy", location="bazaar")
            md.itemList["INFERNO_FUEL"]["prices"]["custom"] = costPerInfernofuel
            # the fuel cost is put into the item data to be used later in the general fuel cost calculator
            pass

        # add extra diamonds from offline diamond spreading
        if self.variables["afk"]["var"].get() is False and "DIAMOND_SPREADING" in upgrades:
            static_upgrade_items = list(upgrade_drops.items())
            for itemtype, amount in static_upgrade_items:
                if itemtype == "DIAMOND":  # Diamond spreadings don't trigger on themselves,
                    continue  # currently Diamonds can only be in upgrade_drops through diamond spreadings so this should work
                upgrade_drops["DIAMOND"] += amount * 0.1

        # add upgrade drops to main item list
        for item, amount in upgrade_drops.items():
            if item not in self.variables["items"]["list"]:
                self.variables["items"]["list"][item] = 0
            self.variables["items"]["list"][item] += amount

        # Offline mode Derpy
        # The offline doubling has only been seen on Corrupt Soil and Diamond Spreading
        # but is assumed to work on everything
        if self.variables["mayor"]["var"].get() == "Derpy" and self.variables["afk"]["var"].get() is False:
            for itemtype in self.variables["items"]["list"].keys():
                self.variables["items"]["list"][itemtype] *= 2

        # (Super) Compactor logic at the end because it applies to both drop groups
        # for both compactor types it floors the ratio between items and needed items for one compacted
        # multiplies the floored ratio if the action creates multiple compacted item
        # uses modulo to find the left over amount
        # Compactors
        # loops once through item list because there are no double normal compacted items
        if "compact" in upgrades_types:
            static_items = list(self.variables["items"]["list"].items())
            for item, amount in static_items:
                if item in md.compactorList:
                    compact_name, percompact = list(md.compactorList[item].items())[0]
                    compact_amount = int(amount / percompact)
                    if compact_amount == 0:
                        continue
                    elif "amount" in md.compactorList[item]:
                        compact_amount *= md.compactorList[item]["amount"]
                    left_over = amount % percompact
                    if left_over == 0.0:
                        del self.variables["items"]["list"][item]
                    else:
                        self.variables["items"]["list"][item] = left_over
                    self.variables["items"]["list"][compact_name] = compact_amount
            pass

        # Super compactor
        # loops continously through the item list until is cannot find something to compact
        found_enchantable = True
        safety_lock = 0
        while found_enchantable is True:
            safety_lock += 1
            if safety_lock >= 10:  # safety to prevent an infinite while loop
                print("WARNING: While-loop overflow, super compactor 3000")
                break
            found_enchantable = False
            if "enchant" in upgrades_types:
                static_items = list(self.variables["items"]["list"].items())
                for item, amount in static_items:
                    if item in md.enchanterList:
                        enchanted_name, perenchanted = list(md.enchanterList[item].items())[0]
                        enchanted_amount = int(amount / perenchanted)
                        if enchanted_amount == 0:
                            continue
                        elif "amount" in md.enchanterList[item]:
                            enchanted_amount *= md.enchanterList[item]["amount"]
                        left_over = amount % perenchanted
                        if left_over == 0.0:
                            del self.variables["items"]["list"][item]
                        else:
                            self.variables["items"]["list"][item] = left_over
                        self.variables["items"]["list"][enchanted_name] = enchanted_amount
                        if enchanted_name in md.enchanterList:
                            found_enchantable = True

        # storage calculations
        # amount of storage measured in slots
        avaible_storage = md.minion_chests[self.variables["chest"]["var"].get()]
        if "storage" in md.minionList[minion_type] and minion_tier in md.minionList[minion_type]["storage"]:
            avaible_storage += md.minionList[minion_type]["storage"][minion_tier]
        else:
            avaible_storage += md.standard_storage[minion_tier]

        # WARNING: this calculation does not work with compactors and is not accurate for setup with multiple drops
        used_storage = 0
        for amount in self.variables["items"]["list"].values():
            used_storage += amount / 64
        fill_time = (timeNumber * avaible_storage) / used_storage
        self.variables["filltime"]["var"].set(fill_time)

        # multiply drops by minion amount
        # all processes as calculated above should be linear with minion amount
        for itemtype in self.variables["items"]["list"].keys():
            self.variables["items"]["list"][itemtype] *= minion_amount

        # convert items into coins and xp
        # while keeping track where items get sold
        # it makes a list of all prices and takes the one that matches the choice of hopper
        coinsPerTime = 0.0
        sellto = "NPC"
        if minion_hopper == "Bazaar":
            sellto = "bazaar"
        elif minion_hopper == "Best (NPC/Bazaar)":
            sellto = "best"
        prices = {}
        if minion_hopper != "None":
            for itemtype, amount in self.variables["items"]["list"].items():
                prices.clear()
                prices["NPC"] = self.getPrice(itemtype, "sell", "npc", force=False)
                prices["bazaar"] = self.getPrice(itemtype, "sell", "bazaar", force=False)
                if sellto in prices:
                    final_price = prices[sellto]
                    self.variables["sellLoc"]["list"][itemtype] = sellto
                else:
                    self.variables["sellLoc"]["list"][itemtype] = max(prices, key=prices.get)
                    final_price = prices[self.variables["sellLoc"]["list"][itemtype]]
                self.variables["itemtypeProfit"]["list"][itemtype] = amount * final_price * hopper_data[minion_hopper]
                coinsPerTime += amount * final_price
        for itemtype, amount in self.variables["items"]["list"].items():
            xptype, value = list(*md.itemList[itemtype]["xp"].items())
            if value == 0:
                continue
            if xptype not in self.variables["xp"]["list"]:
                self.variables["xp"]["list"][xptype] = 0
            self.variables["xp"]["list"][xptype] += amount * value * (1 + self.variables["wisdom"]["list"][xptype].get() / 100)
        if self.variables["mayor"]["var"].get() == "Derpy":
            for xptype in self.variables["xp"]["list"].keys():
                self.variables["xp"]["list"][xptype] *= 1.5
        coinsPerTime *= hopper_data[minion_hopper]
        self.variables["itemProfit"]["var"].set(coinsPerTime)

        # Pet leveling calculations
        # https://wiki.hypixel.net/Pets#Leveling
        # for golden dragon: the program slowly adds the xp to the pets
        # while keeping in mind that golden dragons below lvl 100 cannot hold pet items
        # the pet costs are manually added in pet_data
        petXPPerTime = 0.0
        petProfitPerTime = 0.0
        pet = self.variables["levelingpet"]["var"].get()
        exp_boost_type = md.pet_xp_boosts[self.variables["petxpboost"]["var"].get()][0]
        exp_boost_perc = md.pet_xp_boosts[self.variables["petxpboost"]["var"].get()][1]
        if pet == "Golden Dragon":
            for skill, amount in self.variables["xp"]["list"].items():
                remaining_xp = self.getPetXP(skill, amount)
                if exp_boost_type in [skill, "all"]:
                    boost = 1 + exp_boost_perc / 100
                else:
                    boost = 1
                safety_lock = 100
                while remaining_xp > 0 and safety_lock > 0:
                    safety_lock -= 1
                    current_petXP = petXPPerTime % 210255385
                    if current_petXP < 25353230:
                        using_xp = min(remaining_xp, 25353230 - current_petXP)
                        petXPPerTime += using_xp
                        remaining_xp -= using_xp
                    else:
                        using_xp = min(remaining_xp * boost, 210255385 - current_petXP)
                        petXPPerTime += using_xp
                        remaining_xp -= using_xp / boost
                if safety_lock == 0:
                    print("WARNING: While loop overflow, Golden Dragon calculations")
        elif pet != "None":
            for skill, amount in self.variables["xp"]["list"].items():
                petXPPerTime += self.getPetXP(skill, amount)
        if pet != "None":
            maxpetsPerTime = petXPPerTime / pet_data[pet]["xp"]
            petProfitPerTime = maxpetsPerTime * (pet_data[pet]["cost"]["max"] - pet_data[pet]["cost"]["min"])
        self.variables["petProfit"]["var"].set(petProfitPerTime)

        # calculating beacon and limited fuel cost
        fuelCostPerTime = 0.0
        if minion_beacon != 0:
            if self.variables["scorched"]["var"].get():
                beacon_fuel_ID = "SCORCHED_POWER_CRYSTAL"
            else:
                beacon_fuel_ID = "POWER_CRYSTAL"
            costPerCrystal = self.getPrice(beacon_fuel_ID, "buy", "bazaar")
            fuelCostPerTime += timeNumber * costPerCrystal / md.itemList[beacon_fuel_ID]["duration"] * int(not (self.variables["B_constant"]["var"].get()))
        if md.itemList[minion_fuel]["upgrade"]["duration"] != 0:
            costPerFuel = self.getPrice(minion_fuel, "buy", "bazaar")
            fuelCostPerTime += minion_amount * timeNumber * costPerFuel / md.itemList[minion_fuel]["upgrade"]["duration"]
        self.variables["fuelcost"]["var"].set(fuelCostPerTime)

        # Setup cost
        total_cost = 0.0
        # Single minion cost
        minion_item_cost = {}
        tier_loop = np.arange(minion_tier) + 1
        for tier in tier_loop:
            if minion_type in md.extraMinionCosts:
                if tier in md.extraMinionCosts[minion_type]:
                    for cost_type, amount in md.extraMinionCosts[minion_type][tier].items():
                        if cost_type == "COINS":
                            total_cost += md.extraMinionCosts[minion_type][tier]["COINS"]
                        else:
                            self.variables["notes"]["list"]["Extra cost"] = f"{amount} {cost_type.replace('_', ' ').title()} per minion"
            for item, amount in md.minionCosts[minion_type][tier].items():
                if item not in minion_item_cost:
                    minion_item_cost[item] = 0
                minion_item_cost[item] += amount
        for item_ID, amount in minion_item_cost.items():
            total_cost += amount * self.getPrice(item_ID, "buy", "bazaar")
        # Infinite fuel cost
        if minion_fuel != "NONE" and md.itemList[minion_fuel]["upgrade"]["duration"] == 0:
            total_cost += self.getPrice(minion_fuel, "buy", "bazaar")
        # Hopper cost
        if minion_hopper in ["Budget Hopper", "Enchanted Hopper"]:
            hopper_ID = md.getID[minion_hopper]
            total_cost += self.getPrice(hopper_ID, "buy", "bazaar")
        # Internal minion upgrades cost
        for upgrade in upgrades:
            if upgrade != "NONE":
                total_cost += self.getPrice(upgrade, "buy", "bazaar")
        # Infusion cost
        if self.variables["infusion"]["var"].get() is True:
            total_cost += self.getPrice("MITHRIL_INFUSION", "buy", "bazaar")

        # multiply by minion amount
        total_cost *= minion_amount

        # Beacon cost
        if minion_beacon != 0 and not self.variables["B_acquired"]["var"].get():
            for i in np.arange(minion_beacon) + 1:
                for item_ID, amount in md.upgrades_material_cost["beacon"][i].items():
                    total_cost += amount * self.getPrice(item_ID, "buy", "bazaar")

        # Floating Crystal cost
        if self.variables["crystal"]["var"].get() != "None":
            for item_ID, amount in md.upgrades_material_cost["crystal"][self.variables["crystal"]["var"].get()].items():
                total_cost += amount * self.getPrice(item_ID, "buy", "bazaar")

        # Sending results to self.variables
        self.variables["setupcost"]["var"].set(total_cost)
        self.variables["harvests"]["var"].set(minion_amount * harvestsPerTime)
        self.variables["petxp"]["var"].set(petXPPerTime)
        self.variables["totalProfit"]["var"].set(self.variables["itemProfit"]["var"].get() + self.variables["petProfit"]["var"].get() - self.variables["fuelcost"]["var"].get())

        # Construct ID
        self.variables["ID"]["var"].set(self.constructID())

        # Get minion notes
        if "notes" in md.minionList[self.variables["minion"]["var"].get()]:
            self.variables["notes"]["list"].update(md.minionList[self.variables["minion"]["var"].get()]["notes"].copy())

        # Update listboxes
        self.update_GUI()
        if inGUI is True:
            self.statusC.configure(bg="green")
            self.statusC.update()
        return

    def loop_minions(self):
        """
        WARNING: CURRENTLY BROKEN\n
        Loops through every minion for the inputted setup and prints Short Output

        Returns
        -------
        None.

        """
        outputlist = {}
        for minion in md.minionList.keys():
            self.variables["minion"]["var"].set(minion)
            self.load_minion(minion)
            self.calculate()
            time.sleep(0.1)
            self.output_data(toTerminal=True)
            crafted_dict = {}
            for info, data in self.outputsList.items():
                if data["switch"].get() is True:
                    variable_data = data["var"].get()
                    crafted_dict[info] = variable_data
            if len(crafted_dict) == 1:
                outputlist[minion] = list(deepcopy(crafted_dict).values())[0]
            else:
                outputlist[minion] = deepcopy(crafted_dict)
        time.sleep(0.1)
        print(outputlist)
        print("Highest: ", max(outputlist, key=outputlist.get))
        return

    def update_bazaar(self, cooldown_warning=True):
        """
        Checks if a bazaar_cooldown amount of seconds has passed,
        calls to Hypixel API for most recent bazaar data,
        handles that data to calculate accurate buy and sell prices.
        To get accurate prices, it takes a top percentage (top 10% default) of the orders and takes the average of them.

        Returns
        -------
        None

        """
        if time.time() - self.bazaar_timer < bazaar_cooldown and self.bazaar_timer != 0:
            if cooldown_warning:
                print("WARNING: Bazaar is on cooldown")
            return
        try:
            f = urllib.request.urlopen(r"https://api.hypixel.net/v2/skyblock/bazaar")
            call_data = f.read().decode('utf-8')
        except Exception as error:
            print(f"ERROR: Could not finish API call\n{error}")
            return
        raw_data = json.loads(call_data)
        if "success" not in raw_data or raw_data["success"] is False:
            print("ERROR: API call was unsuccessful")
            return
        self.bazaar_timer = raw_data["lastUpdated"] / 1000
        self.variables["bazaar_update_txt"]["var"].set(time.strftime("%Y-%m-%d %H:%M:%S UTC%z", time.localtime(self.bazaar_timer)))
        top_percent = 0.1
        for itemtype, item_data in md.itemList.items():
            if itemtype not in raw_data["products"]:
                continue
            for action in ["buy", "sell"]:
                top_amount = top_percent * sum([order["amount"] for order in raw_data["products"][itemtype][f"{action}_summary"]])
                if top_amount == 0:
                    item_data["prices"][f"{action}Price"] = 0
                    continue
                counter = top_amount
                top_sum = 0
                for order in raw_data["products"][itemtype][f"{action}_summary"]:
                    if counter <= 0:
                        break
                    if counter >= order["amount"]:
                        top_sum += order["amount"] * order["pricePerUnit"]
                        counter -= order["amount"]
                    else:
                        top_sum += counter * order["pricePerUnit"]
                        counter = 0
                        break
                item_data["prices"][f"{action}Price"] = top_sum / top_amount
        return

    def save_calc(self):
        """
        WARNING: CURRENTLY BROKEN\n
        Saves the inputs and outputs as a dict to a file.

        Returns
        -------
        None.

        """
        url = r"saved_calculations.txt"
        # with open(url, 'r', encoding='utf-8') as f:
        #     saved_calcs = json.load(f)
        new_entry = {}
        new_entry["minion"] = self.variables["minion"]["var"].get()
        new_entry["tier"] = self.variables["miniontier"]["var"].get()
        new_entry["amount"] = self.variables["amount"]["var"].get()
        for upgrade, value in self.upgradeList.items():
            new_entry[upgrade] = value.get()
        for info, data in self.outputsList.items():
            if info in ['Time span', 'Item amounts', 'XP amounts', 'Notes', 'Bazaar data']:
                if info == "Time span":
                    new_entry[info] = self.time_number()
                elif info == "Item amounts":
                    new_entry[info] = self.variables["items"]["list"]
                    new_entry["Sell types"] = self.variables["sellLoc"]["list"]
                elif info == "XP amounts":
                    new_entry[info] = self.variables["xp"]["list"]
                elif info == "Notes":
                    new_entry[info] = self.variables["notes"]["list"]
                elif info == "Bazaar data":
                    new_entry[info] = self.variables["bazaar_update_txt"]["var"].get()
                    new_entry["BZ sell"] = self.variables["bazaar_sell_type"]["var"].get()
                    new_entry["BZ buy"] = self.variables["bazaar_buy_type"]["var"].get()
            else:
                new_entry[info] = data["var"].get()
        with open(url, 'a', encoding='utf-8') as f:
            f.write(json.dumps(new_entry))
            f.write(",")

    def update_GUI(self):
        """
        Creates an array for the listbox out of the list storage of self.variables with "vtype" equal to "list"

        Returns
        -------
        None.

        """
        listbox_list = []
        for var_key, var_data in self.variables.items():
            if var_data["vtype"] == "list":
                if var_key == "wisdom":
                    continue
                listbox_list.clear()
                for key, val in var_data["list"].items():
                    if "IDtoDisplay" in var_data and var_data["IDtoDisplay"] is True:
                        key = md.itemList[key]["display"]
                    listbox_list.append(f'{key}: {val}')
                var_data["var"].set(listbox_list)
        return

#%% main loop


def start_app():
    """
    Starts the minion calculator and destroys it when exited
    Warns user if the stop button was not used to close the calculator

    Returns
    -------
    None.

    """
    App = Calculator()
    App.mainloop()
    try:
        App.destroy()
    except Exception:
        print("ERROR: Please use the stop button in the bottom right to close the application")
    return
