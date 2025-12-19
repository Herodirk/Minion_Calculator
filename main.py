# -*- coding: utf-8 -*-
"""
@author: Herodirk

Main file for the minion calculator.
To start the calculator: run this file with a local python interpreter

Bazaar data from https://api.hypixel.net
AH data from https://sky.coflnet.com/data (currently only Postcard)
"""


#%% imports

try:
    import tkinter as tk
    import numpy as np
    import time
    import json
    import urllib.request
    from copy import deepcopy
    import webbrowser
    import HSB_minion_data as md
    import Hero_UI_Manager
    import official_calculator_add_ons as Hero_addons
except ModuleNotFoundError as import_error:
    missing_package = import_error.name
    if missing_package in ["HSB_minion_data", "Hero_UI_Manager", "official_calculator_add_ons"]:
        print(f"Could not find calculator file {missing_package}.py,\nplease make sure all the calculator files are in the same folder.")
    else:
        print(f"Could not find {missing_package} module,\nplease install this module using PIP")
    exit()

#%% Settings

external_add_ons = {**Hero_addons.add_ons_package}
# add-ons are function that use the results of the main calculation
# add-ons can have no output or send output to the calculator through collect_addon_output
# add-ons are stored as {display name: function reference}
# the name will show up on the button, the funtion will only get the argument calculator=self sent to it.
# the support for this is limited and will be improved later

# API settings
API_auto_update = True
# If true, bazaar automatically updates before performing calculation
API_cooldown = 300  # seconds
# Time limit in seconds between each automatic update

# Output settings
compact_tolerance = 10000  # coins
# Minimum coin loss per compacting action for the calculator to make a note of coin loss
output_to_clipboard = True
# If true, Short Output and Share Output also get saved in your clipboard
debug_mode = False
# Toggle for debug mode

# Visual settings
color_palette = "dark_red"
# Color palette of the calculator, current options: "dark", "dark_red", "light", "gray_text"
# For Apple IOS users, use "gray_text"

# Setup Templates
templateList = {
    "Choose Template": {},  # would suggest to keep this one
    "ID": {},  # would suggest to keep this one too
    "Clean": {},  # would suggest to also keep this one
    "Corrupt": {
        "hopper": "Enchanted Hopper",
        "upgrade1": "Corrupt Soil",
        "upgrade2": "Diamond Spreading",
        "sellLoc": "Hopper",
    },
    "Compact": {
        "sellLoc": "Best (NPC/Bazaar)",
        "upgrade1": "Super Compactor 3000",
    },
    "Compact Corrupt": {
        "sellLoc": "Best (NPC/Bazaar)",
        "hopper": "Enchanted Hopper",
        "upgrade1": "Super Compactor 3000",
        "upgrade2": "Corrupt Soil",
    },
    "Cheap speed": {
        "fuel": "Enchanted Lava Bucket",
        "upgrade2": "Diamond Spreading",
        "beacon": 0,
        "infusion": False,
        "free_will": False,
        "postcard": True
    },
    "No permanent speed": {
        "fuel": "Plasma Bucket",
        "upgrade2": "Flycatcher",
        "beacon": 5,
        "infusion": False,
        "free_will": False,
        "postcard": True
    },
    "Max speed": {
        "fuel": "Plasma Bucket",
        "upgrade2": "Flycatcher",
        "beacon": 5,
        "infusion": True,
        "free_will": True,
        "postcard": True
    },
    "Hyper speed": {
        "fuel": "Hyper Catalyst",
        "upgrade2": "Flycatcher",
        "beacon": 5,
        "infusion": True,
        "free_will": True,
        "postcard": True
    },
    "AFK with pet": {
        "afkpetlvl": 100,
        "afk": True
    },
    "Solo Wisdom": {
        "miningWisdom": 83.5,  # max Seasoned Mineman (15), cookie (25), god pot (20), Cavern Wisdom (6.5), Refined Divine drill with Compact X (7 + 10)
        "combatWisdom": 109,  # max Slayer unique tier kills (6 + 6 + 6 + 12 + 6), Rift Necklace (1), Hunter Ring (5), Bubba Blister (2), Veteran (10), cookie (25), god pot (30)
        "farmingWisdom": 72.5,  # Fruit Bowl (1), Pelt Belt (1), Zorro's Cape (1), Rift Necklace (1), Agarimoo Artifact (1), Garden Wisdom (6.5) cookie (25), god pot (20), Blessed Mythic farming tool with Cultivating X (6 + 10)
        "fishingWisdom": 55.5,  # Moby-Duck (1), Future Calories Talisman (1), Agarimoo Artifact (1), Chumming Talisman (1), Sea Wisdom (6.5), cookie (25), god pot (20)
        "foragingWisdom": 93.82,  # Efficient Forager (15), Foraging Wisdom (6.5), David's Cloak (5), Foraging Wisdom Boosters armor and equipment (4 + 2), cookie (25), god pot (20), Moonglade Legendary Axe with Absorb X, Foraging Wisdom Boosters and essence shop perk Axed I ((5 + 10 + 1) * 1.02)
    },
    "Full Coop Wisdom": {  # cookie (25), god pot (20), 8 * (1 + 45 / 100) = 8 + (8 * 45) / 100 =  1 + (700 + 8 * 45) / 100 = 1 + 1060 / 100
        "miningWisdom": 1060,  
        "combatWisdom": 1060,
        "farmingWisdom": 1060,
        "fishingWisdom": 1060,
        "foragingWisdom": 1060,
    },
    "Combat Pet Leveling": {
        "expshareitem": True,
        "taming": 60,
        "falcon_attribute": 10,
        "petxpboost": "Epic Combat Exp Boost",
        "toucan_attribute": 10,
    },
    "Maxed Inferno Minion": {
        "minion": "Inferno",
        "amount": 31,
        "fuel": "Inferno Minion Fuel",
        "infernoGrade": "Hypergolic Gabagool",
        "infernoDistillate": "Gabagool Distillate",
        "infernoEyedrops": True,
        "sellLoc": "Best (NPC/Bazaar)",
        "upgrade1": "Super Compactor 3000",
        "upgrade2": "Flycatcher",
        "chest": "XX-Large",
        "beacon": 5,
        "scorched": True,
        "infusion": True,
        "free_will": True,
        "postcard": True,
        "bazaar_sell_type": "Sell Offer",
        "bazaar_buy_type": "Buy Order"
    }
}

# All pets are assumed to be Legendary or Mythic, except Rift Ferret, which is stuck at Epic.
# min is for the price of a level 1, max is for the price of a max lvl (either 100 or 200).
# make sure that any pets you add have the name spelt the same as in md.all_pets
# The date of the price and possible notes is behind each pet.
pet_costs = {
    "None": {"min": 1, "max": 1},
    "Custom Pet": {"min": 0, "max": 20000000},
    "Golden Dragon": {"min": 610000000, "max": 800000000},  # 2025-8-31
    "Jade Dragon": {"min": 580000000, "max": 720000000},  # 2025-8-31
    "Black Cat": {"min": 40000000, "max": 62000000},  # 2025-8-31 (both buy and sell as legendary)
    "Elephant": {"min": 23000000, "max": 30000000},  # 2025-8-31
    "Mooshroom Cow": {"min": 8000000, "max": 20000000},  # 2025-8-31
    "Slug": {"min": 5000000, "max": 32000000},  # 2025-8-31
    "Hedgehog": {"min": 8000000, "max": 30000000},  # 2025-8-31
    "Enderman": {"min": 44000000, "max": 69000000},  # 2025-8-31 (buy as legendary lvl 1, sell as mythic lvl 100)
}

# and the custom prices in md.itemList (see HSB_minion_data.py)


#%% Lists you should not touch

reduced_amounts = {0: "", 1: "k", 2: "M", 3: "B", 4: "T", 5: "Qd"}


#%% Main Class


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        # Use Hero UI Manager to initialize the window and the frames with grids
        self.huim = Hero_UI_Manager.H_UI_M(main=self, version="MINION", windowTitle="Minion Calculator", windowWidth=1450, windowHeight=750, palette=color_palette)
        self.booting_msg("Hero UI Manager loaded")
        self.huim.createControls()
        self.huim.createFrames(self, frame_keys=[["inputs_minion", "inputs_player", "outputs_setup", "outputs_profit"]], grid_frames=True, grid_size=0.96, border=0.003)
        self.frames["addons_main"] = tk.Frame(self, background=self.colors["background"])
        self.huim.createFrames(self.frames["addons_main"], frame_keys=[["addons_buttons", "addons_output"]], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0)
        self.booting_msg("Framework set up")
        self.version = self.huim.defVar(dtype=float, initial=1.2)
        self.booting_msg("Calculator version {self.version.get()}")

        # The calculator stores all important variables into this dict
        # the keys "vtype", "dtype", "frame", "noWidget" and "switch_initial"
        #     change how and where the calculator makes the inputs and outputs for each variable
        # "display" is used whenever a human-readable form of the variable is needed
        # "fancy_display" is used for markdown output, if it doesn't exist for a variable, "display" is used
        # "initial" is the initial value of the variable
        # "options" is a list of options for the variable, also used for encoding and decoding setup IDs
        # for "vtype" equal to list are extra keys: "w", "h" and "list".
        #     "w" and "h" are the width and height of the listbox widget.
        #     "list" is a normal list-like variable, most of the time a dict. This is the actual storage of the list.
        #     "var" is connected to the listbox, "list" can be shaped and put into "var" in the function self.update_GUI()
        self.variables = {
            "minion": {"vtype": "input", "dtype": str, "display": "Minion", "frame": "inputs_minion_grid", "initial": "Custom", "options": list(md.minionList.keys()), "command": lambda x: self.multiswitch("minion", x)},
            "miniontier": {"vtype": "input", "dtype": int, "display": "Tier", "frame": "inputs_minion_grid", "initial": 12, "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "command": lambda x: self.multiswitch("minion", x)},
            "amount": {"vtype": "input", "dtype": int, "display": "Amount", "frame": "inputs_minion_grid", "initial": 1, "options": [], "command": None},
            "fuel": {"vtype": "input", "dtype": str, "display": "Fuel", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.fuel_options.keys()), "command": lambda x: self.multiswitch("fuel", x)},
            "infernoGrade": {"vtype": "input", "dtype": str, "display": "Grade", "frame": "inputs_minion_grid", "initial": "Hypergolic Gabagool", "options": [md.itemList[grade]["display"] for grade in md.infernofuel_data["grades"].keys()], "command": None},
            "infernoDistillate": {"vtype": "input", "dtype": str, "display": "Distillate", "frame": "inputs_minion_grid", "initial": "Gabagool Distillate", "options": [md.itemList[dist]["display"] for dist in md.infernofuel_data["distilates"].keys()], "command": None},
            "infernoEyedrops": {"vtype": "input", "dtype": bool, "display": "Eyedrops", "frame": "inputs_minion_grid", "initial": True, "options": [False, True], "command": None},
            "hopper": {"vtype": "input", "dtype": str, "display": "Hopper", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.hopper_data.keys()), "command": None},
            "upgrade1": {"vtype": "input", "dtype": str, "display": "Upgrade 1", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.upgrade_options.keys()), "command": None},
            "upgrade2": {"vtype": "input", "dtype": str, "display": "Upgrade 2", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.upgrade_options.keys()), "command": None},
            "chest": {"vtype": "input", "dtype": str, "display": "Chest", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.minion_chests.keys()), "command": None},
            "beacon": {"vtype": "input", "dtype": int, "display": "Beacon", "frame": "inputs_minion_grid", "initial": 0, "options": [0, 1, 2, 3, 4, 5], "command": self.huim.createSwitchCall("beacon", controlvar="self")},
            "scorched": {"vtype": "input", "dtype": bool, "display": "Scorched", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
            "B_constant": {"vtype": "input", "dtype": bool, "display": "Free Fuel Beacon", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
            "B_acquired": {"vtype": "input", "dtype": bool, "display": "Acquired Beacon", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
            "infusion": {"vtype": "input", "dtype": bool, "display": "Infusion", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
            "crystal": {"vtype": "input", "dtype": str, "display": "Crystal", "frame": "inputs_minion_grid", "initial": "None", "options": list(md.floating_crystals.keys()), "command": None},
            "free_will": {"vtype": "input", "dtype": bool, "display": "Free Will", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": self.huim.createSwitchCall("free_will", controlvar="free_will")},
            "postcard": {"vtype": "input", "dtype": bool, "display": "Postcard", "frame": "inputs_minion_grid", "initial": False, "options": [False, True], "command": None},
            "afk": {"vtype": "input", "dtype": bool, "display": "AFK", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": lambda: self.multiswitch("afk", None)},
            "afkpet": {"vtype": "input", "dtype": str, "display": "AFK Pet", "frame": "inputs_player_grid", "initial": "None", "options": list(md.boost_pets.keys()), "command": None},
            "afkpetrarity": {"vtype": "input", "dtype": str, "display": "AFK Pet Rarity", "frame": "inputs_player_grid", "initial": "Legendary", "options": ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"], "command": None},
            "afkpetlvl": {"vtype": "input", "dtype": float, "display": "AFK Pet level", "frame": "inputs_player_grid", "initial": 0.0, "options": [], "command": None},
            "enchanted_clock": {"vtype": "input", "dtype": bool, "display": "Enchanted Clock", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
            "specialLayout": {"vtype": "input", "dtype": bool, "display": "Special Layout", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
            "playerHarvests": {"vtype": "input", "dtype": bool, "display": "Player Harvests", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
            "playerLooting": {"vtype": "input", "dtype": int, "display": "Looting", "frame": "inputs_player_grid", "initial": 0, "options": [0, 1, 2, 3, 4 ,5], "command": None},
            "potatoTalisman": {"vtype": "input", "dtype": bool, "display": "Potato talisman", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
            "combatWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "display": "Combat", "initial": 0.0, "options": []},
            "miningWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "display": "Mining", "initial": 0.0, "options": []},
            "farmingWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "display": "Farming", "initial": 0.0, "options": []},
            "fishingWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "display": "Fishing", "initial": 0.0, "options": []},
            "foragingWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "display": "Foraging", "initial": 0.0, "options": []},
            "alchemyWisdom": {"vtype": "input", "noWidget": True, "dtype": float, "display": "Alchemy", "initial": 0.0, "options": []},
            "wisdom": {"vtype": "list", "display": "Wisdom", "frame": "inputs_player_grid", "w": None, "h": 6, "list": {}},
            "mayor": {"vtype": "input", "dtype": str, "display": "Mayor", "frame": "inputs_player_grid", "initial": "None", "options": ["None", "Aatrox", "Cole", "Diana", "Diaz", "Finnegan", "Foxy", "Marina", "Paul", "Jerry", "Derpy", "Scorpius"], "command": lambda x: self.multiswitch("mayors", x)},
            "levelingpet": {"vtype": "input", "dtype": str, "display": "Leveling pet", "frame": "inputs_player_grid", "initial": "None", "options": list(md.all_pets.keys()), "command": lambda x: self.multiswitch("pet_leveling", x)},
            "taming": {"vtype": "input", "dtype": float, "display": "Taming", "frame": "inputs_player_grid", "initial": 0.0, "options": [], "command": None},
            "falcon_attribute": {"vtype": "input", "dtype": int, "display": "Battle Experience", "frame": "inputs_player_grid", "initial": 0, "options": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "command": None},
            "toucan_attribute": {"vtype": "input", "dtype": int, "display": "Why Not More", "frame": "inputs_player_grid", "initial": 0, "options": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "command": None},
            "petxpboost": {"vtype": "input", "dtype": str, "display": "Pet XP boost", "frame": "inputs_player_grid", "initial": "None", "options": list(md.pet_xp_boosts.keys()), "command": None},
            "beastmaster": {"vtype": "input", "dtype": float, "display": "Beastmaster", "frame": "inputs_player_grid", "initial": 0.0, "options": [], "command": None},
            "expsharepet": {"vtype": "input", "dtype": str, "display": "Exp Share pet", "frame": "inputs_player_grid", "initial": "None", "options": list(md.all_pets.keys()), "command": None},
            "expsharepetslot2": {"vtype": "input", "dtype": str, "display": "Exp Share pet 2", "frame": "inputs_player_grid", "initial": "None", "options": list(md.all_pets.keys()), "command": None},
            "expsharepetslot3": {"vtype": "input", "dtype": str, "display": "Exp Share pet 3", "frame": "inputs_player_grid", "initial": "None", "options": list(md.all_pets.keys()), "command": None},
            "expshareitem": {"vtype": "input", "dtype": bool, "display": "Exp Share pet item", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": None},
            "often_empty": {"vtype": "input", "dtype": bool, "display": "Empty Often", "frame": "inputs_player_grid", "initial": False, "options": [False, True], "command": self.huim.createSwitchCall("emptytime", controlvar="often_empty")},
            "sellLoc": {"vtype": "input", "dtype": str, "display": "Sell Location", "frame": "inputs_player_grid", "initial": "Best (NPC/Bazaar)", "options": ["Best (NPC/Bazaar)", "Bazaar", "Hopper", "NPC"], "command": self.huim.createSwitchCall("NPC_Bazaar", controlvar="self")},
            "bazaar_sell_type": {"vtype": "input", "dtype": str, "display": "Bazaar sell type", "frame": "inputs_player_grid", "initial": "Sell Offer", "options": list(md.bazaar_sell_types.keys()), "command": None},
            "bazaar_buy_type": {"vtype": "input", "dtype": str, "display": "Bazaar buy type", "frame": "inputs_player_grid", "initial": "Buy Order", "options": list(md.bazaar_buy_types.keys()), "command": None},
            "bazaar_taxes": {"vtype": "input", "dtype": bool, "display": "Bazaar taxes", "frame": "inputs_player_grid", "initial": True, "options": [False, True], "command": self.huim.createSwitchCall("bazaar_tax", controlvar="bazaar_taxes")},
            "bazaar_flipper": {"vtype": "input", "dtype": int, "display": "Bazaar Flipper", "frame": "inputs_player_grid", "initial": 1, "options": [0, 1, 2], "command": None},
            "ID": {"vtype": "output", "dtype": str, "display": "Setup ID", "frame": "outputs_setup_grid", "initial": "", "switch_initial": True},
            "ID_container": {"vtype": "list", "display": "ID", "frame": "outputs_setup_grid", "w": 35, "h": 1, "list": [], "switch_initial": False, "IDtoDisplay": False},
            "time": {"vtype": "output", "dtype": str, "display": "Time", "frame": "outputs_setup_grid", "initial": "1.0 Days", "switch_initial": True},
            "time_seconds": {"vtype": "storage", "dtype": float, "initial": 86400.0},
            "emptytime": {"vtype": "output", "dtype": str, "display": "Empty Time", "fancy_display": "Empty every", "frame": "outputs_setup_grid", "initial": "1.0 Days", "switch_initial": True},
            "actiontime": {"vtype": "output", "dtype": float, "display": "Action time (s)", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
            "harvests": {"vtype": "output", "dtype": float, "display": "Harvests", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
            "items": {"vtype": "list", "display": "Item amounts", "frame": "outputs_setup_grid", "w": 35, "h": None, "list": {}, "switch_initial": False, "IDtoDisplay": True},
            "itemSellLoc": {"vtype": "list", "display": "Sell locations", "frame": "outputs_profit_grid", "w": 35, "h": None, "list": {}, "switch_initial": False, "IDtoDisplay": True},
            "filltime": {"vtype": "output", "dtype": float, "display": "Fill time", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
            "used_storage": {"vtype": "output", "dtype": int, "display": "Used Storage", "frame": "outputs_setup_grid", "initial": 0, "switch_initial": False},
            "itemtypeProfit": {"vtype": "list", "display": "Itemtype profits", "fancy_display": "Profits per item type", "frame": "outputs_profit_grid", "w": 35, "h": None, "list": {}, "switch_initial": False, "IDtoDisplay": True},
            "itemProfit": {"vtype": "output", "dtype": float, "display": "Total item profit", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": False},
            "xp": {"vtype": "list", "display": "XP amounts", "frame": "outputs_setup_grid", "w": 35, "h": 4, "list": {}, "switch_initial": False},
            "pets_levelled": {"vtype": "list", "display": "Pets Levelled", "frame": "outputs_setup_grid",  "w": 35, "h": 4, "list": {}, "switch_initial": False},
            "petProfit": {"vtype": "output", "dtype": float, "display": "Pet profit", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": False},
            "fuelcost": {"vtype": "output", "dtype": float, "display": "Fuel cost", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": False},
            "fuelamount": {"vtype": "output", "dtype": float, "display": "Fuel amount", "frame": "outputs_setup_grid", "initial": 0.0, "switch_initial": False},
            "totalProfit": {"vtype": "output", "dtype": float, "display": "Total profit", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": True},
            "notes": {"vtype": "list", "display": "Notes", "frame": "outputs_setup_grid", "w": 50, "h": 4, "list": {}, "switch_initial": False},
            "bazaar_update_txt": {"vtype": "output", "dtype": str, "display": "Bazaar data", "frame": "outputs_profit_grid", "initial": "Not Loaded", "switch_initial": True},
            "setupcost": {"vtype": "output", "dtype": float, "display": "Setup cost", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": True},
            "freewillcost": {"vtype": "output", "dtype": float, "display": "Free Will cost", "fancy_display": "+ Average Free Will cost", "frame": "outputs_profit_grid", "initial": 0.0, "switch_initial": True},
            "extracost": {"vtype": "storage", "dtype": str, "display": "Extra cost", "fancy_display": "+ Extra cost", "initial": ""},
            "optimal_tier_free_will": {"vtype": "storage", "dtype": int, "initial": 1},
            "available_storage": {"vtype": "storage", "dtype": int, "initial": 0},
            "addons_output_container": {"vtype": "list", "display": "Add-on Outputs", "frame": "addons_output_grid", "w": 65, "h": 20, "list": {}, "switch_initial": False, "IDtoDisplay": False},
        }

        # determining input/output types according to "vtype", "noWidget" and "switch_initial"
        # the other values are send to Hero UI Manager. Hero UI Manager creates the Tkinter variable and widgets (stored in "var" and "widget" respectively)
        for var_key, var_data in self.variables.items():
            if var_data["vtype"] == "input" and "noWidget" not in var_data:
                var_data["var"], var_data["widget"] = self.huim.defVarI(dtype=var_data["dtype"], frame=self.frames[var_data["frame"]],
                                                                      L_text=f"{var_data['display']}:", initial=var_data["initial"],
                                                                      options=var_data["options"], cmd=var_data["command"])
            elif var_data["vtype"] == "output":
                var_data["var"], var_data["widget"] = self.huim.defVarO(dtype=var_data["dtype"], frame=self.frames[var_data["frame"]],
                                                                      L_text=f"{var_data['display']}:", initial=var_data["initial"])
            elif var_data["vtype"] == "input" and "noWidget" in var_data:
                var_data["var"] = self.huim.defVar(dtype=var_data["dtype"], initial=var_data["initial"])
            elif var_data["vtype"] == "list":
                var_data["var"], var_data["widget"] = self.huim.defListO(frame=self.frames[var_data["frame"]], L_text=f"{var_data['display']}:", h=var_data["h"], w=var_data["w"])
            elif var_data["vtype"] == "storage":
                var_data["var"] = self.huim.defVar(dtype=var_data["dtype"], initial=var_data["initial"])
            if "switch_initial" in var_data:
                self.variables[var_key]["output_switch"], widget = self.huim.defVarI(dtype=bool, frame=self.frames[self.variables[var_key]["frame"]], L_text="", initial=self.variables[var_key]["switch_initial"])
                var_data["widget"].append(widget[-1])

        # define left over Tkinter variables and widgets that didnt fit in self.variables
        self.template, self.templateI = self.huim.defVarI(dtype=str, frame=self.frames["inputs_minion_grid"], L_text="Templates:", initial="Choose Template", options=list(templateList.keys()), cmd=self.load_template)
        self.loadID, self.loadIDI = self.huim.defVarI(dtype=str, frame=self.frames["inputs_minion_grid"], L_text="Load ID:")

        for skill in ['combat', 'mining', 'farming', 'fishing', 'foraging', 'alchemy']:
            self.variables["wisdom"]["list"][skill] = self.variables[f"{skill}Wisdom"]["var"]
        self.wisdomB = tk.Button(self.frames["inputs_player_grid"], text='Edit', command=lambda: self.huim.edit_vars(self.update_gui_wisdom, ["combatWisdom", "miningWisdom", "farmingWisdom", "fishingWisdom", "foragingWisdom", "alchemyWisdom"]))
        self.wisdomB.place(in_=self.variables["wisdom"]["widget"][-1], relx=1, x=3, rely=0.5, anchor='w')

        self.rising_celsius_override = False

        self.emptytimeamount, self.emptytimeamountI = self.huim.defVarI(dtype=float, frame=self.frames["inputs_player_grid"], L_text="Empty Time span:", initial=1.0)
        self.emptytimelength, self.emptytimelengthI = self.huim.defVarI(dtype=str, frame=self.frames["inputs_player_grid"], L_text="Empty Time Length:", initial="Days", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.emptytimelengthI[-1].place(in_=self.emptytimeamountI[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.totaltimeamount, self.totaltimeamountI = self.huim.defVarI(dtype=float, frame=self.frames["inputs_player_grid"], L_text="Total Time span:", initial=1.0)
        self.totaltimelength, self.totaltimelengthI = self.huim.defVarI(dtype=str, frame=self.frames["inputs_player_grid"], L_text="Total Time Length:", initial="Days", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.totaltimelengthI[-1].place(in_=self.totaltimeamountI[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.notesAnchor = self.huim.genLabel(frm=self.frames["outputs_setup_grid"], txt="")

        self.booting_msg("self.variables initialized")

        # Create widgets for controls menu and placing them
        self.creditLB = self.huim.genLabel(frm=self.frames["controls"], txt=f"Minion Calculator V{self.version.get()}\nMade by Herodirk")
        self.creditLB.place(in_=self.stopB, x=-10, rely=0.5, y=-1, anchor="e")
        self.manualLB = self.huim.genLabel(frm=self.frames["controls"], txt="Online Manual:\nCalculator Manual")
        self.manualLB.place(in_=self.creditLB, x=-10, rely=0.5, anchor="e")
        self.manualLB.bind("<Button-1>", lambda void_event: webbrowser.open(r"https://herodirk.github.io/"))
        self.API_creditLB = self.huim.genLabel(frm=self.frames["controls"], txt="Bazaar data from Hypixel API,\nAH data from SkyCofl API")
        self.API_creditLB.place(in_=self.manualLB, x=-10, rely=0.5, anchor="e")
        self.API_creditLB.bind("<Button-1>", lambda click_event: webbrowser.open(r"https://api.hypixel.net/") if click_event.y < 18 else webbrowser.open(r"https://sky.coflnet.com/data"))

        self.outputB = tk.Button(self.frames["controls"], text='Short Output', command=self.output_data)
        self.fancyoutputB = tk.Button(self.frames["controls"], text='Share Output', command=self.fancy_output)
        self.calcB = tk.Button(self.frames["controls"], text='Calculate', command=lambda: self.calculate(True))
        self.statusC = tk.Canvas(self.frames["controls"], bg="green", width=10, height=10, borderwidth=0)
        self.addonsB = tk.Button(self.frames["controls"], text="Add-ons Menu", command=lambda: self.huim.toggleSwitch("addons"))
        self.bazaarB = tk.Button(self.frames["controls"], text="Update Bazaar", command=self.update_prices)
        # self.status, self.statusO = self.huim.defVarO(frame=self.frames["controls"], dtype=str, L_text="Status:", initial="Ready")  # might use later

        controlsGrid = [self.calcB, self.statusC, self.outputB, self.fancyoutputB, self.bazaarB, self.addonsB]
        self.huim.fill_arr(controlsGrid, self.frames["controls"])

        # Create miscellaneous labels
        miniontitleLB = self.huim.genLabel(frm=self.frames["inputs_minion_grid"], txt="\nMinion options")
        islandtitleLB = self.huim.genLabel(frm=self.frames["inputs_minion_grid"], txt="\nIsland options")
        playertitleLB = self.huim.genLabel(frm=self.frames["inputs_player_grid"], txt="Player options")
        timingtitleLB = self.huim.genLabel(frm=self.frames["inputs_player_grid"], txt="\nTime options")
        markettitleLB = self.huim.genLabel(frm=self.frames["inputs_player_grid"], txt="\nMarket options")
        setupoutputsLB = self.huim.genLabel(frm=self.frames["outputs_setup_grid"], txt="Setup Information")
        setupprintLB = self.huim.genLabel(frm=self.frames["outputs_setup_grid"], txt="Share")
        minionoutputsLB = self.huim.genLabel(frm=self.frames["outputs_setup_grid"], txt="Minion Outputs")
        minionprintLB = self.huim.genLabel(frm=self.frames["outputs_setup_grid"], txt="Share")
        profitoutputsLB = self.huim.genLabel(frm=self.frames["outputs_profit_grid"], txt="Profit Outputs")
        profitprintLB = self.huim.genLabel(frm=self.frames["outputs_profit_grid"], txt="Share")
        addonsprintLB = self.huim.genLabel(frm=self.frames["addons_output_grid"], txt="Share")
        addonsoutputsLB = self.huim.genLabel(frm=self.frames["addons_output_grid"], txt="Add-on Outputs")

        # Defining the order of widgets and placing them for all the grids
        self.grids = {
            "inputs_minion_grid": {
                "template": self.templateI,
                "ID": self.loadIDI,
                "minion_label": [None, miniontitleLB],
                "minion": self.variables["minion"]["widget"],
                "miniontier": self.variables["miniontier"]["widget"],
                "amount": self.variables["amount"]["widget"],
                "fuel": self.variables["fuel"]["widget"],
                "infernoGrade": self.variables["infernoGrade"]["widget"],
                "infernoDistillate": self.variables["infernoDistillate"]["widget"],
                "infernoEyedrops": self.variables["infernoEyedrops"]["widget"],
                "hopper": self.variables["hopper"]["widget"],
                "upgrade1": self.variables["upgrade1"]["widget"],
                "upgrade2": self.variables["upgrade2"]["widget"],
                "chest": self.variables["chest"]["widget"],
                "infusion": self.variables["infusion"]["widget"],
                "free_will": self.variables["free_will"]["widget"],
                "island_label": [None, islandtitleLB],
                "beacon": self.variables["beacon"]["widget"],
                "scorched": self.variables["scorched"]["widget"],
                "B_constant": self.variables["B_constant"]["widget"],
                "B_acquired": self.variables["B_acquired"]["widget"],
                "crystal": self.variables["crystal"]["widget"],
                "postcard": self.variables["postcard"]["widget"],
            },
            "inputs_player_grid": {
                "player_label": [None, playertitleLB],
                "afk": self.variables["afk"]["widget"],
                "afkpet": self.variables["afkpet"]["widget"],
                "afkpetrarity": self.variables["afkpetrarity"]["widget"],
                "afkpetlvl": self.variables["afkpetlvl"]["widget"],
                "enchanted_clock": self.variables["enchanted_clock"]["widget"],
                "specialLayout": self.variables["specialLayout"]["widget"],
                "playerHarvests": self.variables["playerHarvests"]["widget"],
                "playerLooting": self.variables["playerLooting"]["widget"],
                "potatoTalisman": self.variables["potatoTalisman"]["widget"],
                "wisdom": self.variables["wisdom"]["widget"],
                "mayor": self.variables["mayor"]["widget"],
                "levelingpet": self.variables["levelingpet"]["widget"],
                "toggle_levelingpet_options": [None, self.huim.createShowHideToggle("levelingpet", lambda: self.multiswitch("pet_leveling", None), None)],
                "taming": self.variables["taming"]["widget"],
                "falcon_attribute": self.variables["falcon_attribute"]["widget"],
                "petxpboost": self.variables["petxpboost"]["widget"],
                "beastmaster": self.variables["beastmaster"]["widget"],
                "expsharepet": self.variables["expsharepet"]["widget"],
                "expsharepetslot2": self.variables["expsharepetslot2"]["widget"],
                "expsharepetslot3": self.variables["expsharepetslot3"]["widget"],
                "toucan_attribute": self.variables["toucan_attribute"]["widget"],
                "expshareitem": self.variables["expshareitem"]["widget"],
                "timing_label": [None, timingtitleLB],
                "totaltime": self.totaltimeamountI,
                "often_empty": self.variables["often_empty"]["widget"],
                "emptytime": self.emptytimeamountI,
                "market_label": [None, markettitleLB],
                "sellLoc": self.variables["sellLoc"]["widget"],
                "bazaar_sell_type": self.variables["bazaar_sell_type"]["widget"],
                "bazaar_buy_type": self.variables["bazaar_buy_type"]["widget"],
                "bazaar_taxes": self.variables["bazaar_taxes"]["widget"],
                "bazaar_flipper": self.variables["bazaar_flipper"]["widget"]
            },
            "outputs_setup_grid": {
                "labels": [None, setupoutputsLB, setupprintLB],
                "ID": [self.variables["ID"]["widget"][0], self.variables["ID_container"]["widget"][1], self.variables["ID"]["widget"][2]],
                "time": self.variables["time"]["widget"],
                "emptytime": self.variables["emptytime"]["widget"],
                "actiontime": self.variables["actiontime"]["widget"],
                "fuelamount": self.variables["fuelamount"]["widget"],
                "notes": [self.variables["notes"]["widget"][0], None, self.variables["notes"]["widget"][2]],
                "notes_anchor": [self.notesAnchor],
                "notes_space_1": [None],
                "notes_space_2": [None],
                "notes_space_3": [None],
                "minions_labels": [None, minionoutputsLB, minionprintLB],
                "harvests": self.variables["harvests"]["widget"],
                "items": self.variables["items"]["widget"],
                "used_storage": self.variables["used_storage"]["widget"],
                "xp": self.variables["xp"]["widget"],
                "pets_levelled": self.variables["pets_levelled"]["widget"],
            },
            "outputs_profit_grid": {
                "labels": [None, profitoutputsLB, profitprintLB],
                "bazaar_update_txt": self.variables["bazaar_update_txt"]["widget"],
                "setupcost": self.variables["setupcost"]["widget"],
                "freewillcost": self.variables["freewillcost"]["widget"],
                "itemSellLoc": self.variables["itemSellLoc"]["widget"],
                "itemtypeProfit": self.variables["itemtypeProfit"]["widget"],
                "itemProfit": self.variables["itemProfit"]["widget"],
                "petProfit": self.variables["petProfit"]["widget"],
                "fuelcost": self.variables["fuelcost"]["widget"],
                "totalProfit": self.variables["totalProfit"]["widget"]
            },
            "addons_output_grid": {
                "labels": [None, addonsoutputsLB, addonsprintLB],
                "addons_output_container": [None, self.variables["addons_output_container"]["widget"][1], self.variables["addons_output_container"]["widget"][2]]
            },
        }
        for grid_key in self.grids.keys():
            self.huim.fill_grid(self.grids[grid_key].values(), self.frames[grid_key])

        self.variables["notes"]["widget"][1].place(in_=self.notesAnchor, relx=1, x=5, rely=0, anchor='nw')
        self.variables["notes"]["widget"][1].tkraise()

        # Add-ons buttons
        self.addons_list = {**external_add_ons}
        self.addons_buttons = {}
        self.addons_auto_run = {}
        for number, addon_info in enumerate(self.addons_list.items()):
            addon_name, addon_function = addon_info
            button_function = lambda func=addon_function: func(self)
            self.addons_buttons[addon_name] = tk.Button(self.frames["addons_buttons_grid"], text=addon_name, command=button_function)
            self.addons_auto_run[addon_name], widget = self.huim.defVarI(dtype=bool, frame=self.frames["addons_buttons_grid"], L_text="", initial=False)
            widget[-1].place(in_=self.addons_buttons[addon_name], anchor="w", relx=1, rely=0.5, x=10)
            self.addons_buttons[addon_name].grid(row=number % 8, column=(int(number / 8)) * 2)

        self.booting_msg("Widgets placed")

        # Create switches with Hero UI Manager for the extended minion options
        self.huim.defSwitch("pet_leveling", [*self.variables["taming"]["widget"], *self.variables["petxpboost"]["widget"], *self.variables["beastmaster"]["widget"],
                                           *self.variables["expsharepet"]["widget"], *self.variables["expshareitem"]["widget"],
                                           *self.variables["pets_levelled"]["widget"], *self.variables["petProfit"]["widget"],
                                           *self.variables["falcon_attribute"]["widget"], *self.variables["toucan_attribute"]["widget"]],
                          loc="grid", control="None", negate=True, initial=False)
        self.huim.defSwitch("exp_share_diana", [*self.variables["expsharepetslot2"]["widget"], *self.variables["expsharepetslot3"]["widget"]],
                          loc="grid", control="DianaTrue", negate=False, initial=False)
        self.huim.defSwitch("NPC_Bazaar", [*self.variables["itemSellLoc"]["widget"]],
                          loc="grid", control="Best (NPC/Bazaar)", negate=False, initial=True)
        self.huim.defSwitch("infernofuel", [*self.variables["infernoGrade"]["widget"], *self.variables["infernoDistillate"]["widget"], *self.variables["infernoEyedrops"]["widget"]],
                          loc="grid", control="Inferno Minion Fuel", negate=False, initial=False)
        self.huim.defSwitch("beacon", [*self.variables["scorched"]["widget"], *self.variables["B_constant"]["widget"], *self.variables["B_acquired"]["widget"]],
                          loc="grid", control=0, negate=True, initial=False)
        self.huim.defSwitch("potato", [*self.variables["potatoTalisman"]["widget"]],
                          loc="grid", control="PotatoTrue", negate=False, initial=False)
        self.huim.defSwitch("bazaar_tax", [*self.variables["bazaar_flipper"]["widget"]],
                          loc="grid", control=1, negate=False, initial=True)
        self.huim.defSwitch("afking", [*self.variables["afkpet"]["widget"], *self.variables["afkpetrarity"]["widget"], *self.variables["afkpetlvl"]["widget"],
                                     *self.variables["enchanted_clock"]["widget"], *self.variables["specialLayout"]["widget"],
                                     *self.variables["playerHarvests"]["widget"], *self.variables["playerLooting"]["widget"]],
                          loc="grid", control=True, negate=False, initial=False)
        self.huim.defSwitch("fuel_amount", [*self.variables["fuelamount"]["widget"]],
                          loc="grid", control=0, negate=True, initial=False)
        self.huim.defSwitch("emptytime", [*self.emptytimeamountI, *self.variables["emptytime"]["widget"]],
                          loc="grid", control=True, negate=False, initial=False)
        self.huim.defSwitch("free_will", [*self.variables["freewillcost"]["widget"]],
                          loc="grid", control=True, negate=False, initial=False)
        self.huim.defSwitch(ID="addons", obj=self.frames["addons_main"],
                          loc={"anchor": "c", "relx": 0.5, "rely": 0.5, "relwidth": 0.7, "relheight": 0.8}, initial=False)
        
        # Show/Hide toggle buttons for large amount of extended options
        self.huim.createShowHideToggle("afk", "afking")
        self.huim.createShowHideToggle("beacon", "beacon")
        
        self.booting_msg("Switches activated")

        self.dependent_variables = {"afkpetrarity": "afkpet", "afkpetlvl": "afkpet", "playerHarvests": "afk", "emptytime": "often_empty", "freewillcost": "free_will", "expshareitem": "expsharepet"}
        # dependent variables are only active when another specified variable is not equivalent to 0,
        # this overrides forced outputs as inactive variables might not be equivalent to 0
        self.key_replace_bool = ["infusion", "free_will", "postcard"]  # variables that are booleans that need their display name outputted instead of the boolean value

        # Define output orders for Short Output (self.outputOrder) and Share Output (self.fancyOrder)
        self.outputOrder = ['fuel', 'hopper', 'upgrade1', 'upgrade2', 'chest',
                            'beacon', 'scorched', 'B_constant', 'B_acquired',
                            'crystal', 'postcard', 'infusion', 'free_will', 'afk', 'afkpet', 'afkpetrarity', 'afkpetlvl', 'enchanted_clock', 'specialLayout', 'potatoTalisman', 'playerHarvests', "playerLooting",
                            'wisdom', 'mayor', 'levelingpet', 'taming', 'falcon_attribute', 'petxpboost', 'beastmaster', 'toucan_attribute', 'expshareitem', 'expsharepet', 'expsharepetslot2', 'expsharepetslot3',
                            'ID', 'setupcost', 'freewillcost', 'extracost', 'actiontime', 'fuelamount', 'sellLoc', 'bazaar_update_txt', 'bazaar_taxes', 'bazaar_flipper', 'notes',
                            'time', 'often_empty', 'emptytime', 'harvests', 'used_storage', 'items', 'itemSellLoc',
                            'itemProfit', 'itemtypeProfit', 'xp', 'petProfit', 'pets_levelled',
                            'fuelcost', 'totalProfit', 'addons_output_container']

        # The Share Output order is stored per line.
        # First dimension of dict exists of keys which are placed first on a line
        # These keys can serve as headers, or if the key is a variable key, the variable is outputted as {"display"}: {"value"}
        # the values are the second dimension of dict, the keys of which are sub-headers used for formatting, like adding line breaks
        # the values of the second dimension are array-like objects consisting of variable keys,
        # the variables are displayed differently depending on which array type it is:
        # set {}: only the values of the variables will be outputted
        # list []: both the displays and the values of the variables will be outputted
        # tuple (): both displays and values are shown, the sub-header will be outputted in front of every variable
        self.fancyOrder = {
            "**Minion Upgrades**": {
                "\n> Internal: ": {"fuel", "hopper", "upgrade1", "upgrade2"},
                "\n> External: ": {"chest", "beacon", "crystal", "postcard"},
                "\n> Permanent: ": {"infusion", "free_will"}
            },
            "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
            "Fuel Info": {"\n> ": ["infernoGrade", "infernoDistillate", "infernoEyedrops"]},
            "afk": {"\n> ": ["afkpet", "afkpetrarity", "afkpetlvl", "enchanted_clock", "specialLayout", "potatoTalisman"]},
            "playerHarvests": {"\n> ": ["playerLooting"]},
            "often_empty": None,
            "wisdom": None,
            "mayor": None,
            "levelingpet": {
                "\n> ": ["taming", "falcon_attribute", "petxpboost", "beastmaster", "toucan_attribute", "expshareitem"],
                "\n> Exp Share Pets: ": {"expsharepet", "expsharepetslot2", "expsharepetslot3"}
            },
            "**Setup Information**": {"\n> ": ("ID", "setupcost", "freewillcost", "extracost", "actiontime", "fuelamount")},
            "Bazaar Info": {"\n> ": ["sellLoc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper"]},
            "notes": None,
            "**Outputs** for ": {"": {"time"}},
            "emptytime": None,
            "harvests": None,
            "used_storage": None,
            "items": None,
            "itemSellLoc": None,
            "itemProfit": None,
            "itemtypeProfit": None,
            "xp": None,
            "petProfit": None,
            "pets_levelled": None,
            "fuelcost": None,
            "totalProfit": None,
            "addons_output_container": None
        }

        self.ID_order = [
            "minion", "miniontier", "amount", "fuel", "infernoGrade", "infernoDistillate", "infernoEyedrops",
            "hopper", "upgrade1", "upgrade2", "chest", "beacon", "scorched", "B_constant", "B_acquired",
            "infusion", "crystal", "free_will", "postcard",
            "afk", "afkpet", "afkpetrarity", "afkpetlvl", "enchanted_clock", "specialLayout",
            "playerHarvests", "playerLooting", "potatoTalisman",
            "combatWisdom", "miningWisdom", "farmingWisdom", "fishingWisdom", "foragingWisdom", "alchemyWisdom",
            "mayor",
            "levelingpet", "taming", "falcon_attribute", "toucan_attribute", "petxpboost", "beastmaster",
            "expsharepet", "expsharepetslot2", "expsharepetslot3", "expshareitem",
            "often_empty",
            "sellLoc",
            "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper",
        ]
        self.booting_msg("Output orders defined")

        # Load bazaar prices
        self.API_timer = 0
        self.update_prices(cooldown_warning=False)
        self.booting_msg("Ready")
        return

    def system_msg(self, msg_type, message):
        print(msg_type.upper() + ": " + message)
        return
    
    def booting_msg(self, message):
        self.system_msg("BOOTING", message)
        return

    def info_msg(self, message):
        self.system_msg("INFO", message)
        return
    
    def warning_msg(self, message):
        self.system_msg("WARNING", message)
        return
    
    def error_msg(self, message):
        self.system_msg("ERROR", message)
        return

    def output_msg(self, message):
        self.system_msg("OUTPUT", "\n" + message + "\n\n")
        return

    def debug_msg(self, message):
        if not debug_mode:
            self.system_msg("DEBUG", message)
        return

    def time_number(self, time_length, time_amount, seconds_per_action=0.0, actions_per_harvest=1.0):
        """
        Translates time amount and length into seconds.

        Parameters
        ----------
        time_length : str
            A time unit, "Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests".
        time_amount : float
            Amount of time units.
        secondsPaction : float, optional
            Seconds per action. Used to calculate the amount of seconds in one harvest. The default is 0.0.
        actionsPerHarvest : float, optional
            Actions per harvest. Used to calculate the amount of seconds in one harvest. The default is 1.0.

        Returns
        -------
        float
            The inputted time amount and length as seconds.

        """
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
            return seconds_per_action * actions_per_harvest * time_amount
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
            return str(np.round(number, decimal - 1 + int(np.abs(np.floor(np.log10(np.abs(number)))))))
        highest_reduction = min(int(np.floor(np.log10(np.abs(number))) / 3), len(reduced_amounts) - 1)
        reduced = np.round((number / (10 ** (3 * highest_reduction))), decimal)
        output_string = f'{reduced}{reduced_amounts[highest_reduction]}'
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

    def update_gui_wisdom(self):
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

    def multiswitch(self, multi_ID, control):
        """
        Function for switches that were too complicated for Hero UI Manager to handle.

        Parameters
        ----------
        multi_ID : str
            Identifier for the multi-switch.
        control : float, str
            Any value to use for switch control

        Returns
        -------
        None.

        """
        if multi_ID == "minion":
            if type(control) == str or self.variables["miniontier"]["var"].get() not in md.minionList[self.variables["minion"]["var"].get()]["speed"].keys():
                self.variables["miniontier"]["var"].set(list(md.minionList[self.variables["minion"]["var"].get()]["speed"].keys())[-1])
            if type(control) == str:
                self.huim.toggleSwitch("potato", control + str(self.variables["afk"]["var"].get()))
        elif multi_ID == "fuel":
            self.huim.toggleSwitch("infernofuel", control)
            self.huim.toggleSwitch("fuel_amount", md.itemList[md.fuel_options[control]]["upgrade"]["duration"])
        elif multi_ID == "afk":
            afkState = self.variables["afk"]["var"].get()
            self.huim.toggleSwitch("afking", afkState)
            self.huim.toggleSwitch("potato", self.variables["minion"]["var"].get() + str(afkState))
        elif multi_ID == "pet_leveling":
            self.huim.toggleSwitch("pet_leveling", control)
            mayor = self.variables["mayor"]["var"].get()
            pet_leveling_state = self.switches["pet_leveling"]["state"]
            self.huim.toggleSwitch("exp_share_diana", mayor + str(pet_leveling_state))
        elif multi_ID == "mayors":
            pet_leveling_state = self.switches["pet_leveling"]["state"]
            self.huim.toggleSwitch("exp_share_diana", control + str(pet_leveling_state))
        return

    def load_template(self, template_name):
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
        if template_name == "Choose Template":
            return
        self.template.set("Choose Template")
        if template_name == "ID":
            template = self.decode_id(self.loadID.get())
        elif template_name == "Clean":
            template = {var_key: self.variables[var_key]["initial"] for var_key in self.variables if self.variables[var_key]["vtype"] == "input" and var_key not in ["minion", "miniontier"]}
        else:
            template = templateList[template_name]
        for setting, variable in template.items():
            self.variables[setting]["var"].set(variable)
            if "command" in self.variables[setting] and self.variables[setting]["command"] is not None:
                if type(variable) == bool:
                    self.variables[setting]["command"]()
                else:
                    self.variables[setting]["command"](variable)
            if "Wisdom" in setting:
                self.update_gui_wisdom()
        return

    def output_data(self, toTerminal=True):
        """
        WARNING: OUTDATED, PLEASE USE FANCY OUTPUT
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
        crafted_string = f'{self.variables["amount"]["var"].get()}x {self.variables["minion"]["var"].get()} t{self.variables["miniontier"]["var"].get()}; '
        string_parts = {}
        for var_key in self.outputOrder:
            if var_key in self.dependent_variables:
                if self.variables[self.dependent_variables[var_key]]["var"].get() in ["None", "0", "0.0", "", False]:
                    continue
            elif var_key in ["expsharepetslot2", "expsharepetslot3"]:
                if self.variables["mayor"]["var"].get() != "Diana":
                    continue
            if "output_switch" in self.variables[var_key]:
                if self.variables[var_key]["output_switch"].get() is False:
                    if (var_key == "notes" and self.variables["specialLayout"]["var"].get() is True and "Special Layout" in self.variables["notes"]["list"]):
                        string_parts["notes"] = "Notes: Special Layout: " + self.variables['notes']['list']['Special Layout']
                    else:
                        continue
            if var_key == "wisdom":
                wisdoms = {list_key: var.get() for list_key, var in self.variables["wisdom"]["list"].items() if (var.get() not in ["None", 0, 0.0] and list_key in self.variables["xp"]["list"])}
                if len(wisdoms) != 0:
                    string_parts["widsom"] = self.variables["wisdom"]["display"] + ": " + ", ".join(f"{wisdom_type}: {wisdom_val}" for wisdom_type, wisdom_val in wisdoms.items())
                continue
            if var_key == "bazaar_update_txt":
                string_parts["bazaar_update_txt"] = f'Bazaar info: {self.variables["bazaar_sell_type"]["var"].get()}, {self.variables["bazaar_buy_type"]["var"].get()}, Last updated at {self.variables["bazaar_update_txt"]["var"].get()}'
                continue
            if var_key == "extracost":
                if self.variables["setupcost"]["output_switch"].get() is False:
                    continue

            vtype = self.variables[var_key]["vtype"]
            display = self.variables[var_key]["display"]
            if vtype == "list":
                if len(self.variables[var_key]["list"]) == 0:
                    continue
                formatting_function = lambda x: x
                if "IDtoDisplay" in self.variables[var_key] and self.variables[var_key]["IDtoDisplay"] is True:
                    formatting_function = lambda x: md.itemList[x]['display']
                elif var_key == "pets_levelled":
                    formatting_function = lambda x: self.variables[x]["var"].get()
                formatted_list = []
                for list_key, list_val in self.variables[var_key]["list"].items():
                    if var_key == "pets_levelled" and formatting_function(list_key) == "None":
                        continue
                    if type(list_val) in [float, int]:
                        formatted_list.append(f"{formatting_function(list_key)}: {self.reduced_number(list_val)}")
                    else:
                        formatted_list.append(f"{formatting_function(list_key)}: {list_val}")
                string_parts[var_key] = display + ": " + ", ".join(formatted_list)
                continue

            dtype = self.variables[var_key]["dtype"]
            val = self.variables[var_key]["var"].get()
            if vtype == "input":
                if val in ["None", 0, 0.0]:
                    continue
                if dtype in [int, float, bool]:
                    string_parts[var_key] = f"{display}: {val}"
                elif val == "Inferno Minion Fuel":
                    string_parts[var_key] = f'Inferno Minion Fuel ({self.variables["infernoGrade"]["var"].get()}, {self.variables["infernoDistillate"]["var"].get()}, Capcaisin: {self.variables["infernoEyedrops"]["var"].get()})'
                else:
                    string_parts[var_key] = f"{val}"
            else:
                if dtype in [int, float]:
                    string_parts[var_key] = f"{display}: {self.reduced_number(val)}"
                else:
                    string_parts[var_key] = f"{display}: {val}"

        crafted_string += "; ".join(string_parts.values())
        if output_to_clipboard:
            self.clipboard_clear()
            self.clipboard_append(crafted_string)
        if toTerminal is True:
            self.output_msg(crafted_string)
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
        force = False  # force is a toggle for output variables that can be equivalent to 0 but still have to be outputted
        if var_key in self.dependent_variables:  # special case: dependent variables
            if self.variables[self.dependent_variables[var_key]]["var"].get() in ["None", "0", "0.0", "", False]:
                return None
        elif var_key in ["expsharepetslot2", "expsharepetslot3"]:  # special case: slots only active during Diana
            if self.variables["mayor"]["var"].get() != "Diana":
                return None
        if "output_switch" in self.variables[var_key]:
            if self.variables[var_key]["output_switch"].get() is False:
                # special cases: output switch set to false, but forced output anyway
                if var_key == "notes" and self.variables["specialLayout"]["var"].get() is True and "Special Layout" in self.variables["notes"]["list"]:
                    return f"Notes:\n> Special Layout: `{self.variables['notes']['list']['Special Layout']}`"
                else:
                    return None
            else:
                force = True
        if var_key == "wisdom":  # special case: wisdom being separate variables
            wisdoms = {list_key: var.get() for list_key, var in self.variables["wisdom"]["list"].items() if (var.get() not in ["None", 0, 0.0] and list_key in self.variables["xp"]["list"])}
            if len(wisdoms) != 0:
                return self.variables["wisdom"]["display"] + ":\n> " + ", ".join(f"{wisdom_type}: `{wisdom_val}`" for wisdom_type, wisdom_val in wisdoms.items())
            return None
        elif var_key == "beacon":  # special case: add "Beacon" and put the tier in roman numerals
            val = {0: "", 1: "`Beacon I`", 2: "`Beacon II`", 3: "`Beacon III`", 4: "`Beacon IV`", 5: "`Beacon V`"}[self.variables[var_key]["var"].get()]
        elif var_key == "used_storage":  # special case: add available storage to output
            val = f"`{self.variables[var_key]['var'].get()}` (out of `{self.variables['available_storage']['var'].get()}`)"
        elif var_key == "chest":  # special case: add " Storage" after the size
            if self.variables[var_key]["var"].get() == "None":
                val = ""
            else:
                val = f"`{self.variables[var_key]['var'].get()} Storage`"
        elif var_key in self.key_replace_bool:  # special case: output key instead of the boolean
            if self.variables[var_key]["var"].get() is True:
                val = f"`{self.variables[var_key]['display']}`"
            else:
                return None
        elif var_key == "extracost":  # special case: setup cost is turned off
            if self.variables["setupcost"]["output_switch"].get() is False:
                return None
            else:
                val = f"`{self.variables[var_key]['var'].get()}`"
        elif var_key == "ID":  # special case: spoiler lines around setup ID
            val = f"||{self.variables[var_key]['var'].get()}||".replace("\\", r"\\")
        elif self.variables[var_key]["vtype"] == "list":
            if len(self.variables[var_key]["list"]) == 0:
                return None
            formatting_function = lambda x: x
            if "IDtoDisplay" in self.variables[var_key] and self.variables[var_key]["IDtoDisplay"] is True:
                formatting_function = lambda x: md.itemList[x]['display']
            elif var_key == "pets_levelled":
                formatting_function = lambda x: self.variables[x]["var"].get()
            formatted_list = []
            for list_key, list_val in self.variables[var_key]["list"].items():
                if var_key == "pets_levelled" and formatting_function(list_key) == "None":
                    continue
                if type(list_val) in [float, int]:
                    formatted_list.append(f"{formatting_function(list_key)}: `{self.reduced_number(list_val)}`")
                else:
                    formatted_list.append(f"{formatting_function(list_key)}: `{list_val}`")
            val = "\n> " + ", ".join(formatted_list)
        elif self.variables[var_key]["dtype"] in [int, float]:
            val = f"`{self.reduced_number(self.variables[var_key]['var'].get())}`"
        else:
            val = f"`{self.variables[var_key]['var'].get()}`"
        if val in ["`None`", "`0`", "`0.0`", "", "``", "`False`"] and force is False:
            return None
        if var_key == "freewillcost":
            val += f" (optimal: apply on t{self.variables['optimal_tier_free_will']['var'].get()})"
        return_str = ""
        if display:
            if "fancy_display" in self.variables[var_key]:
                return_str += f"{self.variables[var_key]['fancy_display']}: "
            else:
                return_str += f"{self.variables[var_key]['display']}: "
        return_str += f"{val}"
        if newline:
            return_str += "\n"
        return return_str

    def fancy_output(self, toTerminal=True):
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
        if output_to_clipboard:
            self.clipboard_clear()
            self.clipboard_append(crafted_string)
        if toTerminal:
            self.output_msg(crafted_string)
            return
        else:
            return crafted_string

    def get_inputs(self):
        """
        Gets the inputs of the GUI and returns them as setup data.

        Returns
        -------
        dict
            Setup data of the inputted setup.

        """
        setup_data = {}
        for key in self.ID_order:
            var_data = self.variables[key]
            if var_data["vtype"] != "input":
                self.warning_msg("self.ID_order contains non-input variable")
                continue
            setup_data[key] = var_data["var"].get()
        return setup_data

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
            if var_key not in self.variables:
                self.warning_msg(f"Output {var_key} not found in self.variables")
                continue
            if self.variables[var_key]["vtype"] == "list":
                self.variables[var_key]["list"].clear()
                if type(self.variables[var_key]["list"]) is dict:
                    self.variables[var_key]["list"].update(outputs[var_key])
                else:
                    self.variables[var_key]["list"].extend(outputs[var_key])
            else:
                self.variables[var_key]["var"].set(outputs[var_key])
        return

    def construct_id(self, setup_data):
        """
        Generates the setup ID of the provided setup data.
        A setup ID consists of:\n
        - the version number of the minion calculator it was generated in\n
        - the index of the set value in "options" of each self.variable with "vtype" equal to "input" encoded in ASCII with an offset of 48\n
        - the set value surrounded by exclamation marks if a self.variable has an empty "options" list

        Returns
        -------
        ID : str
            Setup ID.

        """
        setup_id = str(self.version.get()) + "!"
        for key, val in setup_data.items():
            var_options = self.variables[key]["options"]
            if len(var_options) == 0:
                if int(val) == val:
                    val = int(val)
                setup_id += "!" + str(val) + "!"
            else:
                index = var_options.index(val)
                setup_id += chr(48 + index)
        return setup_id

    def decode_id(self, ID):
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
        setup_data = {}
        end_ver = ID.find("!")
        if end_ver == -1:
            self.warning_msg("Invalid ID, could not find version number")
            return setup_data
        try:
            version = float(ID[0:end_ver])
        except Exception:
            self.warning_msg("Invalid ID, could not find version number")
            return setup_data
        ID_index = end_ver + 1
        if version != self.version.get():
            self.warning_msg("Invalid ID, Incompatible version")
            return setup_data
        try:
            for key, var_data in self.variables.items():
                if var_data["vtype"] != "input":
                    continue
                if len(var_data["options"]) == 0:
                    if ID[ID_index] != "!":
                        self.warning_msg(f"did not find {key}")
                        return
                    end_val = ID.find("!", ID_index + 1)
                    setup_data[key] = var_data["dtype"](ID[ID_index + 1:end_val])
                    ID_index = end_val + 1
                else:
                    setup_data[key] = var_data["options"][ord(ID[ID_index]) - 48]
                    ID_index += 1
        except Exception as error:
            if type(error) == IndexError:
                self.warning_msg("Invalid ID, ID incomplete")
                return {}
            else:
                self.error_msg("unknown error\ndumping error logs\n" + error)
                return {}
        return setup_data

    def get_price(self, ID, action="buy", location="bazaar", force=False):
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
            Toggle to force the location and action, if location is not found, this function returns 0

        Returns
        -------
        float
            price of the item.
        """
        multiplier = 1
        if location == "bazaar":
            if action == "buy":
                location = md.bazaar_buy_types[self.variables["bazaar_buy_type"]["var"].get()]
            elif action == "sell":
                location = md.bazaar_sell_types[self.variables["bazaar_sell_type"]["var"].get()]
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
                self.warning_msg("no forced cost found for " + ID)
                return 0
            elif "npc" in md.itemList[ID]["prices"]:
                return multiplier * md.itemList[ID]["prices"]["npc"]
            elif "custom" in md.itemList[ID]["prices"]:
                return md.itemList[ID]["prices"]["custom"]
            else:
                self.warning_msg("no cost found for " + ID)
                return 0
        else:
            self.warning_msg(ID + " not in itemList")
            return 0

    def get_upgrade_types(self, upgrades):
        """
        Gets the upgrade types of the given upgrades.

        Parameters
        ----------
        upgrades : list
            List of upgrade IDs.

        Returns
        -------
        list
            List of upgrade types.

        """
        upgrade_types = []
        for upgrade in upgrades:
            for temp_type in md.itemList[upgrade]["upgrade"]["special"]["type"].split(", "):
                upgrade_types.append(temp_type)
        return upgrade_types

    def get_speed_boosts(self, minion, minion_fuel_id, upgrade_ids, afk_toggle, clock_override, setup_data):
        """
        Adds up speed boosts, uses the fact that booleans can be seen as 0 and 1 for false and true resp.

        Parameters
        ----------
        minion : str
            Minion type.
        minion_fuel_id : str
            Minion fuel ID.
        upgrade_ids : list
            List of upgrade IDs
        afk_toggle : boolean
            True if AFKing, False if offline
        clock_override : boolean
            True if using the Enchanted Clock
        setup_data : dict
            Needed setup data: amount, mayor, beacon, scorched, infusion, free_will, postcard, crystal,\n
            potatoTalisman, afkpet, afkpetrarity, afkpetlvl

        Returns
        -------
        float
            Total additive speed boost.
        """
        speed_boost = 0
        speed_boost += md.itemList[minion_fuel_id]["upgrade"]["speed"]
        speed_boost += md.itemList[upgrade_ids[0]]["upgrade"]["speed"] + md.itemList[upgrade_ids[1]]["upgrade"]["speed"]
        speed_boost += 2 * setup_data["beacon"] + 10 * setup_data["infusion"]
        speed_boost += 10 * setup_data["free_will"] + 5 * setup_data["postcard"]
        speed_boost += 5 * setup_data["potatoTalisman"] * (afk_toggle or clock_override) * (minion == "Potato")
        if setup_data["crystal"] != "None":
            if minion in list(md.floating_crystals[setup_data["crystal"]].values())[0]:
                speed_boost += list(md.floating_crystals[setup_data["crystal"]].keys())[0]
        if setup_data["beacon"] != 0:
            speed_boost += 1 * setup_data["scorched"]
        if minion == "Inferno":
            if self.rising_celsius_override:
                speed_boost += 180
            else:
                speed_boost += 18 * min(10, setup_data["amount"])
        if setup_data["mayor"] == "Cole" and (afk_toggle or clock_override) and minion in md.affected_by_cole:
            speed_boost += 25
        afkpet = setup_data["afkpet"]
        afkpet_rarity = setup_data["afkpetrarity"]
        afkpet_lvl = setup_data["afkpetlvl"]
        if (afk_toggle or clock_override) and minion in md.boost_pets[afkpet]["affects"] and afkpet_rarity in md.boost_pets[afkpet]:
            speed_boost += md.boost_pets[afkpet][afkpet_rarity][0] + afkpet_lvl * md.boost_pets[afkpet][afkpet_rarity][1]
        return speed_boost

    def get_drop_multiplier(self, minion, minion_fuel_id, upgrade_ids, afk_toggle, setup_data):
        """
        Multiplies together drop multipliers.

        Parameters
        ----------
        minion : str
            Minion type.
        minion_fuel_id : str
            Minion fuel ID.
        upgrade_ids : list
            List of upgrade IDs
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: playerHarvests, playerLooting, mayor

        Returns
        -------
        float
            Total multiplicative drop multiplier.
        """
        drop_multiplier = 1
        if afk_toggle and setup_data["playerHarvests"] and (minion not in ["Fishing", "Pumpkin", "Melon"]):
            if minion in ["Zombie", "Revenant", "Voidling", "Inferno", "Vampire", "Skeleton", "Creeper", "Spider", "Tarantula", "Cave Spider", "Blaze", "Magma Cube", "Enderman", "Ghast", "Slime", "Cow", "Pig", "Chicken", "Sheep", "Rabbit"]:
                drop_multiplier *= 1 + 15 * setup_data["playerLooting"] / 100
            return drop_multiplier
        drop_multiplier *= md.itemList[minion_fuel_id]["upgrade"]["drop"]
        drop_multiplier *= md.itemList[upgrade_ids[0]]["upgrade"]["drop"]
        if afk_toggle and drop_multiplier > 1:
            # drop multiplier greater than 1 is rounded down while online
            drop_multiplier = int(drop_multiplier)
        drop_multiplier *= md.itemList[upgrade_ids[1]]["upgrade"]["drop"]
        if afk_toggle and drop_multiplier > 1:
            drop_multiplier = int(drop_multiplier)
        if setup_data["mayor"] == "Derpy":
            drop_multiplier *= 2
        return drop_multiplier
    
    def get_actions_per_harvest(self, minion, upgrade_ids, afk_toggle, setup_data, setup_notes):
        """
        Multiplies together drop multipliers.

        Parameters
        ----------
        minion : str
            Minion type.
        upgrade_ids : list
            List of upgrade IDs
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: playerHarvests, specialLayout
        setup_notes : dict
            setup notes

        Returns
        -------
        int
            Actions per harvest.
        """
        actions_per_harvest = 2
        if minion == "Fishing":
            # only has harvests actions
            actions_per_harvest = 1
        if afk_toggle:
            if minion in ["Pumpkin", "Melon"]:
                # pumpkins and melons are forced to regrow for minion to harvest
                actions_per_harvest = 1
            if setup_data["playerHarvests"]:
                if minion in ["Fishing", "Pumpkin", "Melon"]:
                    setup_notes["Player Harvests"] = "Player Harvesting does not work with this minion"
                else:
                    actions_per_harvest = 1
                    if minion in ["Gravel"]:
                        upgrade_ids.append("FLINT_SHOVEL")
                        setup_notes["Player Tools"] = "Assuming Player is using Flint Shovel"
                    if minion in ["Ice"]:
                        setup_notes["Player Tools"] = "Assuming Player is using Silk Touch"
            elif setup_data["specialLayout"]:
                if minion in ["Cobblestone", "Mycelium", "Ice"]:
                    # cobblestone generator, regrowing mycelium, freezing water
                    actions_per_harvest = 1
                if minion in ["Flower", "Sand", "Red Sand", "Gravel"]:
                    # harvests through natural means: water flushing, gravity
                    actions_per_harvest = 1
                    # speedBonus -= 10  # only spawning has 10% action speed reduction, not confirmed yet.
        return actions_per_harvest

    def update_loot_table(self, minion, minion_fuel_id, afk_toggle, setup_data):
        """
        Applies changes to the loot tables of the minions depending on things like AFKing or special layouts.

        Parameters
        ----------
        minion : str
            Minion type.
        minion_fuel_id : str
            Minion fuel ID
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: specialLayout

        Returns
        -------
        None.
        """
        if minion in ['Oak', 'Spruce', 'Birch', 'Dark Oak', 'Acacia', 'Jungle']:
            if afk_toggle:
                # chopped trees have 4 blocks of wood, unknown why offline gives 3
                md.minionList[minion]["drops"][md.getID[f"{minion} Log"]] = 4
            else:
                md.minionList[minion]["drops"][md.getID[f"{minion} Log"]] = 3
        elif minion == "Gravel":
            if afk_toggle:
                # vanilla minecraft chance for gravel to become flint
                md.minionList[minion]["drops"]["GRAVEL"] = 0.9
                md.minionList[minion]["drops"]["FLINT"] = 0.1
            else:
                md.minionList[minion]["drops"]["GRAVEL"] = 1
                md.minionList[minion]["drops"]["FLINT"] = 0
        elif minion == "Pumpkin":
            if afk_toggle:
                # it just does this, idk, ask Hypixel
                md.minionList[minion]["drops"]["PUMPKIN"] = 1
            else:
                md.minionList[minion]["drops"]["PUMPKIN"] = 3
        elif minion == "Flower":
            if minion_fuel_id == "THORNY_VINES":
                md.minionList[minion]["drops"] = { "WILD_ROSE": 2 }
            elif afk_toggle and setup_data["specialLayout"]:
                # tall flowers blocked by low ceiling
                md.minionList[minion]["drops"] = { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "SMALL_FLOWER": 0.5 }
            else:
                md.minionList[minion]["drops"] = { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "SMALL_FLOWER": 1 / 3, "LARGE_FLOWER": 1 / 6 }
        elif minion == "Sunflower":
            if minion_fuel_id == "DAYSWITCH":
                md.minionList[minion]["drops"] = { "DOUBLE_PLANT": 2 }
            elif minion_fuel_id == "NIGHTSWITCH":
                md.minionList[minion]["drops"] = { "MOONFLOWER": 2 }
            else:
                md.minionList[minion]["drops"] = { "DOUBLE_PLANT": 1, "MOONFLOWER": 1 }
        return

    def get_seconds_per_action(self, minion, minion_tier, minion_fuel_id, speed_boost, setup_data):
        """
        Calculates total minion speed.

        Parameters
        ----------
        minion : str
            Minion type.
        minion_tier : int
            Minion tier, 1 to 12.
        minion_fuel_id : 
            Minion fuel ID
        speed_boost : float
            Total additive speed boost
        setup_data : dict
            Needed setup data: infernoGrade

        Returns
        -------
        float
            seconds per action.
        """
        base_speed = md.minionList[minion]["speed"][minion_tier]
        secondsPaction = base_speed / (1 + speed_boost / 100)
        if minion_fuel_id == "INFERNO_FUEL":
            secondsPaction /= 1 + md.infernofuel_data["grades"][md.getID[setup_data["infernoGrade"]]]
        return secondsPaction

    def get_emptytime_and_ratio(self, seconds_per_action, actions_per_harvest, setup_data):
        """
        Calculates emptytime in seconds and the ratio between scaled time and empty time.

        Parameters
        ----------
        seconds_per_action : float
            Final seconds per action.
        actions_per_harvest : int
            Final actions per harvest.
        setup_data : dict
            Needed setup data: often_empty

        Returns
        -------
        float, float
            Time between empties in seconds, ratio between emptytime and scaled time.
        """
        if setup_data["often_empty"]:
            emptytime_seconds = self.time_number(self.emptytimelength.get(), self.emptytimeamount.get(), seconds_per_action, actions_per_harvest)
            scaled_time_seconds = self.time_number(self.totaltimelength.get(), self.totaltimeamount.get(), seconds_per_action, actions_per_harvest)
            timeratio = scaled_time_seconds / emptytime_seconds
        else:
            emptytime_seconds = self.time_number(self.totaltimelength.get(), self.totaltimeamount.get(), seconds_per_action, actions_per_harvest)
            timeratio = 1
        return emptytime_seconds, timeratio
    
    def get_harvests_per_time(self, emptytime_seconds, actions_per_harvest, seconds_per_action, afk_toggle, drop_multiplier):
        """
        Calculates the amount of harvests in the inputted emptytime.

        Parameters
        ----------
        emptytime_seconds : float
            Time between empties in seconds.
        actions_per_harvest : int
            Final actions per harvest.
        seconds_per_action : float
            Final seconds per action
        afk_toggle : boolean
            True if AFKing, False if offline
        drop_multiplier : float
            Total drop multiplier

        Returns
        -------
        float, float
            amount of harvests between empties, updated drop_multiplier if offline.
        """
        if self.emptytimelength.get() == "Harvests":
            harvests_per_time = self.emptytimeamount.get()
        else:
            harvests_per_time = emptytime_seconds / (actions_per_harvest * seconds_per_action)
        
        # drop multiplier online/offline mode
        if not afk_toggle:
            harvests_per_time *= drop_multiplier
            drop_multiplier = 1
        return harvests_per_time, drop_multiplier

    def get_upgrade_info(self, upgrade_ids, drops_list):
        """
        Generates
        
        Parameters
        ----------
        upgrade_ids : list
            list of upgrade IDs
        drops_list : dict
            dict containing all drops of the setup

        Returns
        -------
        dict, dict
            spreading_info contains the average amount of a spreading item generated per drop\n
            replace_info contains the replacements of original item ID as key and final item ID as value
        """
        spreading_info = {}
        replace_info = {}
        for upgrade in upgrade_ids:
            upgrade_type = md.itemList[upgrade]["upgrade"]["special"]["type"]
            if "generate" in upgrade_type:
                spreading_chance = md.itemList[upgrade]["upgrade"]["special"]["chance"]
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    spreading_info[item] = spreading_chance * amount
                    drops_list[item] = 0
            if "replace" in upgrade_type:
                replace_info.update(md.itemList[upgrade]["upgrade"]["special"]["list"])
        return spreading_info, replace_info
    
    def add_drops(self, item, amount, drops_list, spreading_info=None, replace_info=None):
        """
        Adds drops to drops_list, automatically applies spreading_info and replace_info if given
        
        :param item: str, item ID of the drop
        :param amount: float, amount of the drop
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param replace_info: dict, the replacements of original item ID as key and final item ID as value
        """
        if replace_info is not None and item in replace_info:
            item = replace_info[item]
        if item not in drops_list:
            drops_list[item] = 0
        drops_list[item] += amount
        if spreading_info is not None:
            for spreading_item, spreading_average in spreading_info.items():
                drops_list[spreading_item] += amount * spreading_average
        return

    def get_base_drops(self, drops_list, spreading_info, replace_info, minion, harvests_per_time, drop_multiplier):
        """
        Gets generated base drops of the setup and adds them to drops_list
        
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param replace_info: dict, the replacements of original item ID as key and final item ID as value
        :param minion: str, minion type
        :param harvests_per_time: float, amount of harvests between empties
        :param drop_multiplier: float, total drop multiplier
        """
        for item, amount in md.minionList[minion]["drops"].items():
            self.add_drops(item, harvests_per_time * amount * drop_multiplier, drops_list, spreading_info, replace_info)
        return

    def get_upgrade_drops(self, drops_list, spreading_info, minion, minion_tier, drop_multiplier, upgrade_ids, harvests_per_time, afk_toggle, emptytime_seconds):
        """
        Gets generated drops from upgrades of the setup and adds them to the drops_list
        
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param minion: str, minion type
        :param minion_tier: int, minion tier, 1 to 12
        :param drop_multiplier: float, total drop multiplier
        :param upgrade_ids: list, upgrade IDs
        :param harvests_per_time: float, amount of harvests between empties
        :param afk_toggle: boolean, True if AFKing, False if offline
        :param emptytime_seconds: float, seconds between empties
        """
        for upgrade in upgrade_ids:
            upgrade_type = md.itemList[upgrade]["upgrade"]["special"]["type"]
            specific_multiplier = 1
            if upgrade_type == "add":
                # adding upgrades are like Corrupt Soils
                if afk_toggle:
                    if "CORRUPT_SOIL" == upgrade:
                        if "afkcorrupt" in md.minionList[minion]:
                            # Certain mob minions get more corrupt drops when afking
                            # It is not a constant multiplier, it is equivalent in chance to the main drops of the minion
                            specific_multiplier = md.minionList[minion]["afkcorrupt"]
                        if minion == "Chicken" and "ENCHANTED_EGG" not in upgrade_ids:
                            # Online Chicken minion without Enchanted Egg does not make corrupt drops
                            specific_multiplier = 0
                    if "ENCHANTED_EGG" == upgrade:
                        # Enchanted Eggs make one laid egg and one egg on kill while AFKing
                        # the egg on spawn is affected by drop multipliers and spreadings
                        self.add_drops("EGG", harvests_per_time * drop_multiplier, drops_list, spreading_info)
                    for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                        self.add_drops(item, harvests_per_time * amount * specific_multiplier, drops_list)
                else:
                    if "ENCHANTED_SHEARS" == upgrade:
                        # No wool gets added from Enchanted Shears when offline
                        specific_multiplier = 0
                    for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                        self.add_drops(item, harvests_per_time * amount * specific_multiplier, drops_list, spreading_info)
            elif upgrade_type == "timer":
                # timer upgrades are like Soulflow Engines
                # formula for effective_cooldown still in research
                # if afk_toggle:
                #     effective_cooldown = 2 * secondsPaction * (1 + np.floor(np.ceil(md.itemList[upgrade]["upgrade"]["special"]["cooldown"] / secondsPaction) / 2))
                # else:
                #     effective_cooldown = ???
                if afk_toggle and upgrade == "LESSER_SOULFLOW_ENGINE" and "SOULFLOW_ENGINE" in upgrade_ids:
                    continue  # Soulflow Engine overrides Lesser Soulflow Engine while online
                if "SOULFLOW_ENGINE" == upgrade and minion == "Voidling":
                    specific_multiplier = 1 + 0.03 * minion_tier  # correct most likely, needs testing
                effective_cooldown = md.itemList[upgrade]["upgrade"]["special"]["cooldown"]
                for cooldown_item, cooldown_amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    self.add_drops(cooldown_item, specific_multiplier * cooldown_amount * emptytime_seconds / effective_cooldown, drops_list)
        return

    def get_inferno_drops(self, drops_list, spreading_info, replace_info, minion, minion_tier, minion_fuel, drop_multiplier, harvests_per_time, emptytime_seconds, afk_toggle, setup_data):
        """
        Gets generated inferno fuel drops and adds them to drops_list.
        https://wiki.hypixel.net/Inferno_Minion_Fuel
        
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param replace_info: dict, the replacements of original item ID as key and final item ID as value
        :param minion: str, minion type
        :param minion_tier: int, minion tier, 1 to 12
        :param minion_fuel: str, ID of minion fuel
        :param drop_multiplier: float, total drop multiplier
        :param harvests_per_time: float, amount of harvests between empties
        :param emptytime_seconds: float, time between empties
        :param afk_toggle: boolean, True if AFKing, False if offline
        :param setup_data: needed setup data: infernoDistillate, infernoGrade, infernoEyedrops
        """
        if minion_fuel != "INFERNO_FUEL":
            return
        # distilate drops
        distilate = md.getID[setup_data["infernoDistillate"]]
        distilate_item = md.infernofuel_data["distilates"][distilate][0]
        amount_per = md.infernofuel_data["distilates"][distilate][1]
        distillate_harvests = (harvests_per_time * 4) / 5
        if afk_toggle:
            self.get_base_drops(drops_list, spreading_info, replace_info, minion, - distillate_harvests, drop_multiplier)
        else:
            self.get_base_drops(drops_list, None, replace_info, minion, - distillate_harvests, drop_multiplier)
        self.add_drops(distilate_item, distillate_harvests * amount_per, drops_list)

        # Hypergolic drops
        if setup_data["infernoGrade"] == "Hypergolic Gabagool":  # hypergolic fuel stuff
            multiplier = 1
            if setup_data["infernoEyedrops"] is True:  # Capsaicin Eyedrops
                multiplier = 1.3
            for item, chance in md.infernofuel_data["drops"].items():
                if item == "INFERNO_APEX" and minion_tier >= 10:  # Apex Minion perk
                    chance *= 2
                self.add_drops(item, multiplier * chance * harvests_per_time, drops_list)
            self.add_drops("HYPERGOLIC_IONIZED_CERAMICS", emptytime_seconds / md.itemList[minion_fuel]["upgrade"]["duration"], drops_list)

        # calculate fuel cost
        infernofuel_components = {
            "INFERNO_FUEL_BLOCK": 2,  # 2 inferno fuel blocks
            distilate: 6,  # 6 times distilate item
            md.getID[setup_data["infernoGrade"]]: 1,  # 1 gabagool core
            "CAPSAICIN_EYEDROPS_NO_CHARGES": int(setup_data["infernoEyedrops"])  # capsaicin eyedrops
        }
        costPerInfernofuel = 0
        for component_ID, amount in infernofuel_components.items():
            costPerInfernofuel += amount * self.get_price(component_ID, action="buy", location="bazaar")
        md.itemList["INFERNO_FUEL"]["prices"]["custom"] = costPerInfernofuel
        # the fuel cost is put into the item data to be used later in the general fuel cost calculator
        return

    def apply_compactor(self, drops_list, compactor_list):
        """
        Applies given compacting rules to the drops list and returns a list of all compacted items
        
        :param drops_list: dict, all drops of the setup
        :param compactor_list: dict of the form {item: {"makes": compacted item, "amount": amount of compacted, "per": amount of item needed}, ...}

        :return compacted_items: list, IDs of items that got compacted
        """
        compacted_items = []
        compactables = list(drops_list.keys())
        while compactables:
            item = compactables.pop(0)
            if item not in compactor_list:
                continue
            amount = drops_list[item]
            per_compacted = compactor_list[item]["per"]
            if amount < per_compacted:
                continue
            compacted_name = compactor_list[item]["makes"]
            compacted_amount = int(amount / per_compacted)
            if "amount" in compactor_list[item]:
                compacted_amount *= compactor_list[item]["amount"]
            left_over = amount % per_compacted
            drops_list[item] = left_over
            drops_list[compacted_name] = compacted_amount
            compacted_items.append({"from": item, **compactor_list[item]})
            if compacted_name in compactor_list:
                compactables.append(compacted_name)
        return compacted_items

    def get_compacted_drops(self, drops_list, upgrade_types):
        """
        Gets compacted drops, returns a list of all compacted items
        
        :param drops_list: dict, all drops of the setup
        :param upgrade_types: list, types of upgrades
        :return compacted_items: list, IDs of items that got compacted
        """
        compacted_items = []
        # Compactors
        if "compact" in upgrade_types:
            compacted_items.extend(self.apply_compactor(drops_list, md.compactorList))

        # Super compactor
        if "enchant" in upgrade_types:
            compacted_items.extend(self.apply_compactor(drops_list, md.enchanterList))
        return compacted_items

    def get_available_storage(self, minion, minion_tier, setup_data):
        """
        Gets amount of available storage measured in slots
        
        :param minion: str, minion type
        :param minion_tier: int, minion tier, 1 to 12
        :param setup_data: needed setup data: chest
        :return available_storage: available storage measured in slots
        """
        available_storage = md.minion_chests[setup_data["chest"]]
        if "storage" in md.minionList[minion] and minion_tier in md.minionList[minion]["storage"]:
            available_storage += md.minionList[minion]["storage"][minion_tier]
        else:
            available_storage += md.standard_storage[minion_tier]
        return available_storage
    
    def get_used_storage(self, drops_list):
        """
        Gets amount of used storage measured in slots
        
        :param drops_list: dict, all drops of the setup
        :return used_storage_slots: used storage measured in slots
        """
        used_storage_slots = 0
        for amount in drops_list.values():
            used_storage_slots += np.ceil(amount / 64)  # hypixel does not care about smaller max stack sizes
        return used_storage_slots
    
    def get_fill_time(self, minion, available_storage):
        # WARNING: calculation for fill_time does not work with compactors and is not accurate for setup with multiple drops
        # used_storage_slots calculations work fine.
        # fill_time = (emptytime_seconds * available_storage) / used_storage

        """ 
        Rework idea:
        It's always the highest enchanted form available of the item that fills most of the storage, but it's the lack of compacting space that actually fills the storage.
        The amount of slots taken by a lack of compacting space is fixed, if there are 2 slots left for a base material the compacting will stop
        So take away those slots and you are left with slots that need to be filled with the highest enchanted form
        And the making of the highest enchanted forms is linear in time
        And in case of multiple item types
        The lack of compacting space just stacks
        And the left over space for the highest enchanted forms can be filled with a ratio of the different items
        Also add a few checks to see if final enchanted form can even be reached, in case of very low storage space
        """
        return 0

    def get_sell_location(self, setup_data):
        """
        Gets sell location and hopper multiplier
        
        :param setup_data: needed setup data: sellLoc
        :return sellto: str, general sell location
        :return hopper_multiplier: float, hopper profit multiplier
        """
        sellto = "NPC"
        hopper_multiplier = 1
        minion_sellLoc = setup_data["sellLoc"]
        if minion_sellLoc == "Bazaar":
            sellto = "bazaar"
        elif minion_sellLoc == "Best (NPC/Bazaar)":
            sellto = "best"
        elif minion_sellLoc == "Hopper":
            hopper_multiplier = md.hopper_data[setup_data["hopper"]]
        return sellto, hopper_multiplier
    
    def get_item_profit(self, sell_location, hopper_multiplier, drops_list):
        """
        Makes a list of all prices and takes the one that matches the choice of sell_location or takes the maximum, while keeping track where items get sold
        
        :param sell_location: str, general sell location
        :param hopper_multiplier: hopper profit multiplier
        :param drops_list: dict, all drops of the setup
        :return item_profit: float, total profit from drops
        :return per_item_profit: dict, profit per item ID
        :return per_item_sell_location: dict, final sell location per item ID
        """""
        item_profit = 0.0
        per_item_profit = {}
        per_item_sell_location = {}
        item_prices = {}
        for itemtype, amount in drops_list.items():
            item_prices.clear()
            item_prices["NPC"] = self.get_price(itemtype, "sell", "npc")
            item_prices["bazaar"] = self.get_price(itemtype, "sell", "bazaar")
            # item_prices["custom"] = self.get_price(itemtype, "sell", "custom", force=True)  # might use later
            if sell_location in item_prices:
                per_item_sell_location[itemtype] = sell_location
            else:
                per_item_sell_location[itemtype] = max(item_prices, key=item_prices.get)
            final_price = item_prices[per_item_sell_location[itemtype]]
            per_item_profit[itemtype] = amount * final_price * hopper_multiplier
            item_profit += amount * final_price
        item_profit *= hopper_multiplier
        return item_profit, per_item_profit, per_item_sell_location

    def get_skill_xp(self, afk_toggle, mayor, drops_list, setup_data):
        """
        Get amount of total skill xp, after having wisdom and mayor applied.
        Hypixel's bonus skill xp doesn't seem to apply to minions
        
        :param afk_toggle: boolean, True if AFKing, False if offline
        :param mayor: str, mayor
        :param drops_list: dict, all drops of the setup
        :param setup_data: needed setup data: playerHarvests, combatWisdom, miningWisdom, farmingWisdom, fishingWisdom, foragingWisdom, alchemyWisdom
        :return skill_xp: dict, gained skill xp per type
        """
        skill_xp = {}
        for itemtype, amount in drops_list.items():
            xptype, value = list(*md.itemList[itemtype]["xp"].items())
            if value == 0:
                continue
            if xptype not in skill_xp:
                skill_xp[xptype] = 0
            skill_xp[xptype] += amount * value * (1 + setup_data[xptype + "Wisdom"] / 100)
        if mayor == "Derpy":
            for xptype in skill_xp.keys():
                skill_xp[xptype] *= 1.5
        if afk_toggle and setup_data["playerHarvests"] and "combat" in skill_xp:
            del skill_xp["combat"]
        return skill_xp

    def get_over_compacting(self, sell_location, compacted_items, per_item_sell_location, setup_notes):
        """
        Checks for all compacted items if compacting them loses value
        
        :param sell_location: str, general sell location
        :param compacted_items: list, IDs of items that got compacted
        :param per_item_sell_location: dict, final sell location per item ID
        :param setup_notes: dict, setup notes
        """
        if sell_location not in ["best", "bazaar"]:
            return
        over_compacting = []
        for item_data in compacted_items:
            item = item_data["from"]
            compact_item = item_data["makes"]
            per_compact = item_data["per"]
            compact_amount = 1
            if "amount" in item_data:
                compact_amount = item_data["amount"]
            cost = self.get_price(item, "sell", per_item_sell_location[item]) * per_compact
            compact_cost = self.get_price(compact_item, "sell", per_item_sell_location[compact_item]) * compact_amount
            if cost - compact_cost > compact_tolerance:
                over_compacting.append(md.itemList[item]['display'])
        if len(over_compacting) != 0:
            setup_notes["Over-compacting"] = ', '.join(over_compacting)
        return

    def get_pet_xp_boosts(self, pet, xp_type, exp_share=False):
        """
        Return pet xp boosts for a given skill xp type.
        All boosts except pet item are multiplied together before returning.
        If xp_type is given as "exp_share", the additive exp share boosts are returned.

        Parameters
        ----------
        pet : str
            Pet for the calculation, must be a pet from pet_data.
        xp_type : str
            Type of skill XP.
        exp_share : bool
            Toggle for if the xp is given through Exp Share. Default is False.

        Returns
        -------
        float
            Combined pet xp boosts of all boosts except pet item
        float
            pet xp boost of pet item

        """
        non_matching = 1
        if md.all_pets[pet]["type"] != "all" and md.all_pets[pet]["type"] != xp_type:
            if xp_type in ["alchemy", "enchanting"]:
                non_matching = 1 / 12
            else:
                non_matching = 1 / 3
        if exp_share:
            return non_matching
        petxpbonus = (1 + self.variables["taming"]["var"].get() / 100) * (1 + self.variables["beastmaster"]["var"].get() / 100) * non_matching
        if md.pet_xp_boosts[self.variables["petxpboost"]["var"].get()][0] in [xp_type, "all"]:
            pet_item = 1 + md.pet_xp_boosts[self.variables["petxpboost"]["var"].get()][1] / 100
        else:
            pet_item = 1
        if self.variables["mayor"]["var"].get() == "Diana":
            petxpbonus *= 1.35
        if xp_type in ["mining", "fishing"]:
            petxpbonus *= 1.5
        if pet == "Reindeer":
            petxpbonus *= 2
        if xp_type in ["combat"] and self.variables["falcon_attribute"]["var"].get() != 0:
            petxpbonus *= (1 + self.variables["falcon_attribute"]["var"].get() / 100)
        return petxpbonus, pet_item

    def dragon_xp(self, gained_xp, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item):
        """
        Calculates the pet xp gain on dragon pets (Golden Dragon and Jade Dragon).

        Parameters
        ----------
        gained_xp : float
            Gained skill xp of a specific type.
        left_over_pet_xp : float
            Left over pet xp on the pet before applying the gained skill xp.
        pet_xp_boost : float
            Combined pet xp boost multiplier without pet item.
        xp_boost_pet_item : float
            Pet xp boost multiplier from pet item.

        Returns
        -------
        gained_pet_xp : float
            Amount of pet xp gained after applying the gained skill xp.
        left_over_pet_xp : float
            Left over pet xp on the pet after applying the gained skill xp.

        """
        drag_lvl_100 = 25353230
        drag_lvl_200 = 210255385
        gained_pet_xp = 0.0
        skill_xp_per_pet = (drag_lvl_200 + drag_lvl_100 * (xp_boost_pet_item - 1)) / (xp_boost_pet_item * pet_xp_boost)
        gained_pet_xp = - left_over_pet_xp
        if left_over_pet_xp <= drag_lvl_100:
            gained_xp += left_over_pet_xp / pet_xp_boost
        else:
            gained_xp += (left_over_pet_xp + drag_lvl_100 * (xp_boost_pet_item - 1)) / (pet_xp_boost * xp_boost_pet_item)
        gained_pet_xp += (gained_xp // skill_xp_per_pet) * drag_lvl_200
        left_over_xp = gained_xp % skill_xp_per_pet
        if left_over_xp <= drag_lvl_100 / pet_xp_boost:
            left_over_pet_xp = left_over_xp * pet_xp_boost
        else:
            left_over_pet_xp = left_over_xp * pet_xp_boost * xp_boost_pet_item + drag_lvl_100 * (1 - xp_boost_pet_item)
        gained_pet_xp += left_over_pet_xp
        return gained_pet_xp, left_over_pet_xp

    def get_pet_profit(self, skill_xp, mayor, setup_notes, setup_data):
        """
        Get total profit from pet levelling\n
        Pet levelling calculations: https://wiki.hypixel.net/Pets#Leveling,\n
        for Golden Dragon: special algorithm taking into account that pet items cannot be applied to Golden Dragon Eggs,\n
        the pet costs are manually added in pet_data
        
        :param skill_xp: dict, gained skill xp per type
        :param mayor: str, mayor
        :param setup_notes: dict, setup notes
        :param setup_data: needed setup data: levelingpet, expsharepet, expsharepetslot2, expsharepetslot3, taming, toucan_attribute, expshareitem, petxpboost
        :return pet_profit: total profit from pets
        """
        pet_profit = 0.0
        main_pet = setup_data["levelingpet"]
        if main_pet == "None":
            return 0, {}
        setup_pets = {
            "levelingpet": {"pet": main_pet, "pet_xp": {}, "levelled_pets": 0.0},
            "expsharepet": {"pet": setup_data["expsharepet"], "pet_xp": {"exp_share": 0.0}, "levelled_pets": 0.0},
            "expsharepetslot2": {"pet": setup_data["expsharepetslot2"], "pet_xp": {"exp_share": 0.0}, "levelled_pets": 0.0},
            "expsharepetslot3": {"pet": setup_data["expsharepetslot3"], "pet_xp": {"exp_share": 0.0}, "levelled_pets": 0.0}
        }
        main_pet_xp = setup_pets["levelingpet"]["pet_xp"]
        if "Dragon" in md.all_pets[main_pet]["rarity"]:
            left_over_pet_xp = 0.0
            for skill, amount in skill_xp.items():
                pet_xp_boost, xp_boost_pet_item = self.get_pet_xp_boosts(main_pet, skill)
                main_pet_xp[skill], left_over_pet_xp = self.dragon_xp(amount, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item)
        else:
            for skill, amount in skill_xp.items():
                pet_xp_boost, xp_boost_pet_item = self.get_pet_xp_boosts(main_pet, skill)
                main_pet_xp[skill] = amount * pet_xp_boost * xp_boost_pet_item
        exp_share_boost = 0.2 * setup_data["taming"] + 10 * (mayor == "Diana") + setup_data["toucan_attribute"]
        exp_share_item = 15 * setup_data["expshareitem"]
        for pet_slot, pet_info in setup_pets.items():
            if pet_slot == "levelingpet":
                continue
            exp_share_pet = pet_info["pet"]
            if exp_share_pet == "None":
                continue
            if "Dragon" in md.all_pets[exp_share_pet]["rarity"]:
                if exp_share_boost == 0:
                    continue
                left_over_pet_xp = 0.0
                for skill, amount in main_pet_xp.items():
                    non_matching = self.get_pet_xp_boosts(exp_share_pet, skill, True)
                    equiv_pet_xp_boost = non_matching * (exp_share_boost / 100)
                    equiv_xp_boost_pet_item = 1 + exp_share_item / exp_share_boost
                    gained_pet_xp, left_over_pet_xp = self.dragon_xp(amount, left_over_pet_xp, equiv_pet_xp_boost, equiv_xp_boost_pet_item)
                    pet_info["pet_xp"]["exp_share"] += gained_pet_xp
            else:
                for skill, amount in main_pet_xp.items():
                    non_matching = self.get_pet_xp_boosts(exp_share_pet, skill, True)
                    pet_info["pet_xp"]["exp_share"] += amount * ((exp_share_boost + exp_share_item) / 100) * non_matching
            if mayor != "Diana":
                break
        exp_share_price = self.get_price("PET_ITEM_EXP_SHARE", "buy", "custom", True)
        if exp_share_price == 0:
            exp_share_price = self.get_price("PET_ITEM_EXP_SHARE_DROP", "buy", "bazaar") + 72 * self.get_price("ENCHANTED_GOLD", "buy", "bazaar")
        for pet_slot, pet_info in setup_pets.items():
            pets_levelled = sum(pet_info["pet_xp"].values()) / md.max_lvl_pet_xp_amounts[md.all_pets[pet_info["pet"]]["rarity"]]
            setup_pets[pet_slot]["levelled_pets"] = pets_levelled
            if pet_info["pet"] not in pet_costs:
                setup_notes["Pet Costs"] = f"{pet_info['pet']} is not in pet_costs."
            else:
                pet_profit += pets_levelled * (pet_costs[pet_info["pet"]]["max"] - pet_costs[pet_info["pet"]]["min"])
            if pet_slot == "levelingpet" and (main_pet_item := setup_data["petxpboost"]) != "None":
                pet_profit -= pets_levelled * self.get_price(md.getID[main_pet_item], "buy", "custom", True)
            if pet_slot != "levelingpet" and setup_data["expshareitem"]:
                pet_profit -= pets_levelled * exp_share_price
        return pet_profit, setup_pets

    def get_finite_fuel_cost(self, minion_amount, minion_fuel, emptytime_seconds, setup_data):
        """
        get cost per emptytime for the finite fuel and beacon fuel
        
        :param minion_amount: int, minion amount
        :param minion_fuel: str, ID of minion fuel
        :param emptytime_seconds: float, time between empties in seconds
        :param setup_data: needed setup data: beacon, scorched, B_constant
        """
        fuel_cost = 0.0
        needed_fuel = 0.0
        if setup_data["beacon"] != 0:
            if setup_data["scorched"]:
                beacon_fuel_ID = "SCORCHED_POWER_CRYSTAL"
            else:
                beacon_fuel_ID = "POWER_CRYSTAL"
            cost_per_crystal = self.get_price(beacon_fuel_ID, "buy", "bazaar")
            fuel_cost += emptytime_seconds * cost_per_crystal / md.itemList[beacon_fuel_ID]["duration"] * int(not (setup_data["B_constant"]))
        if md.itemList[minion_fuel]["upgrade"]["duration"] != 0:
            cost_per_fuel = self.get_price(minion_fuel, "buy", "bazaar")
            needed_fuel = minion_amount * emptytime_seconds / md.itemList[minion_fuel]["upgrade"]["duration"]
            fuel_cost += needed_fuel * cost_per_fuel
        return fuel_cost, needed_fuel

    def get_setup_cost(self, minion_type, minion_tier, minion_amount, minion_fuel, upgrades, setup_notes, setup_data):
        """
        Gets cost of all parts of the setup
        
        :param minion_type: str, minion type
        :param minion_tier: int, minion tier, 1 to 12
        :param minion_amount: int, minion amount
        :param minion_fuel: str, ID of minion fuel
        :param upgrades: list, IDs of upgrades
        :param setup_notes: dict, setup notes
        :param setup_data: needed setup data: hopper, infusion, free_will, chest, beacon, B_acquired, crystal, postcard, potatoTalisman, toucan_attribute, falcon_attribute
        :return total_cost: float, total setup cost
        :return extra_cost: str, total extra cost 
        :return cost_per_part: dict, cost per setup part
        """
        cost_per_part = {}
        extra_cost = ""

        # Single minion cost
        cost_cache = {}
        tiered_coin_cost = {}
        tiered_extra_cost = {}
        tier_loop = np.arange(minion_tier) + 1
        for tier in tier_loop:
            tiered_coin_cost[tier] = 0.0
            if minion_type in md.extraMinionCosts:
                if tier in md.extraMinionCosts[minion_type]:
                    if "COINS" in md.extraMinionCosts[minion_type][tier]:
                        tiered_coin_cost[tier] += md.extraMinionCosts[minion_type][tier]["COINS"]
                    if len(md.extraMinionCosts[minion_type][tier]) > 1 or "COINS" not in md.extraMinionCosts[minion_type][tier]:
                        tiered_extra_cost[tier] = {cost_type.replace('_', ' ').title(): amount for cost_type, amount in md.extraMinionCosts[minion_type][tier].items() if cost_type != "COINS"}
            for item, amount in md.minionCosts[minion_type][tier].items():
                if item not in cost_cache:
                    cost_cache[item] = self.get_price(item, "buy", "bazaar")
                tiered_coin_cost[tier] += amount * cost_cache[item]
            if tier != 1:
                tiered_coin_cost[tier] += tiered_coin_cost[tier - 1]
            if tier - 1 in tiered_extra_cost:
                if tier not in tiered_extra_cost:
                    tiered_extra_cost[tier] = {}
                for material, amount in tiered_extra_cost[tier - 1].items():
                    if material not in tiered_extra_cost[tier]:
                        tiered_extra_cost[tier][material] = 0
                    tiered_extra_cost[tier][material] += amount
        if len(tiered_extra_cost) != 0:
            setup_notes["Extra cost"] = ", ".join([f"{amount} {material}" for material, amount in tiered_extra_cost[minion_tier].items()]) + " per minion"
            extra_cost = ", ".join([f"{amount * minion_amount} {material}" for material, amount in tiered_extra_cost[minion_tier].items()])
        cost_per_part["minion"] = tiered_coin_cost[minion_tier]

        # Infinite fuel cost
        if minion_fuel != "NONE" and md.itemList[minion_fuel]["upgrade"]["duration"] == 0:
            if minion_fuel == "EVERBURNING_FLAME" and self.get_price("EVERBURNING_FLAME", "buy", "custom", True) == 0:
                for item_ID, amount in md.upgrades_material_cost["EVERBURNING_FLAME"].items():
                    cost_per_part["fuel"] = amount * self.get_price(item_ID, "buy", "bazaar")
            else:
                cost_per_part["fuel"] = self.get_price(minion_fuel, "buy", "bazaar")

        # Hopper cost
        if setup_data["hopper"] in ["Budget Hopper", "Enchanted Hopper"]:
            hopper_ID = md.getID[setup_data["hopper"]]
            cost_per_part["hopper"] = self.get_price(hopper_ID, "buy", "bazaar")

        # Internal minion upgrades cost
        for i, upgrade in enumerate(upgrades):
            if upgrade != "NONE":
                cost_per_part[f"upgrade{i + 1}"] = self.get_price(upgrade, "buy", "bazaar")

        # Infusion cost
        if setup_data["infusion"]:
            cost_per_part["infusion"] = self.get_price("MITHRIL_INFUSION", "buy", "bazaar")

        # Free Will costs
        """
        Amount of Free Wills needed per minion:
        Let p be the chance to get a loyal minion.
        Let X be a r.v. denoting the amount of Free Wills needed.
        Using first step analysis we get
        E(X) = (1- p)(E(X) + 1) + p * 1
        E(X) = (1- p)E(X) + 1 - p + p
        E(X) = E(X)- pE(X) + 1
        E(X)= 1/p
        """
        free_will_price = self.get_price("FREE_WILL", "buy", "bazaar")
        postcard_price = self.get_price("POSTCARD", "buy", "custom", True)
        if postcard_price == 0:
            # If no price found, use the free will price
            final_postcard_cost = free_will_price
        else:
            final_postcard_cost = postcard_price
        if setup_data["free_will"]:
            tiered_free_will = {}
            for tier in tier_loop:
                free_wills_needed = 1 / (0.5 + 0.04 * (tier - 1))
                # for each failed Free Will we need another minion and we get a postcard
                # the last Free Will will not give a post card
                free_wills_failed = free_wills_needed - 1
                tiered_free_will[tier] = free_wills_failed * (tiered_coin_cost[tier] - final_postcard_cost) + free_wills_needed * free_will_price
            optimal = min(tiered_free_will, key=tiered_free_will.get)
            self.variables["optimal_tier_free_will"]["var"].set(optimal)
            setup_notes["Free Will"] = f"per minion, apply {1 / (0.5 + 0.04 * (optimal - 1)):.2} Free Wills on Tier {optimal}"
            cost_per_part["free_will"] = tiered_free_will[optimal]

        # Storage Chest cost
        if setup_data["chest"] != "None":
            chest_ID = md.getID[setup_data["chest"]]
            cost_per_part["chest"] = self.get_price(chest_ID, "buy", "bazaar")
        
        # multiply by minion amount
        self.deepmultiply(cost_per_part, minion_amount)

        # Beacon cost
        if setup_data["beacon"] != 0 and not setup_data["B_acquired"]:
            cost_per_part["beacon"] = 0
            for i in np.arange(setup_data["beacon"]) + 1:
                for item_ID, amount in md.upgrades_material_cost["beacon"][i].items():
                    cost_per_part["beacon"] += amount * self.get_price(item_ID, "buy", "bazaar")

        # Floating Crystal cost
        if setup_data["crystal"] != "None":
            cost_per_part["crystal"] = 0
            for item_ID, amount in md.upgrades_material_cost["crystal"][setup_data["crystal"]].items():
                cost_per_part["crystal"] += amount * self.get_price(item_ID, "buy", "bazaar")

        # Postcard cost
        if setup_data["postcard"]:
            cost_per_part["postcard"] = final_postcard_cost

        # Potato Talisman cost
        if setup_data["potatoTalisman"]:
            cost_per_part["potatoTalisman"] = self.get_price("POTATO_TALISMAN", "buy", "custom", True)

        # Attribute costs
        if setup_data["toucan_attribute"] != 0:
            cost_per_part["toucan_attribute"] = md.attribute_shards["Epic"][setup_data["toucan_attribute"]] * self.get_price("SHARD_TOUCAN", "buy", "bazaar")
        if setup_data["falcon_attribute"] != 0:
            cost_per_part["falcon_attribute"] = md.attribute_shards["Rare"][setup_data["falcon_attribute"]] * self.get_price("SHARD_FALCON", "buy", "bazaar")


        total_cost = sum(cost_per_part.values())
        return total_cost, extra_cost, cost_per_part

    def calculate(self, inGUI=False, setup_data=None, return_outputs=False):
        """
        Main calculation function

        Parameters
        ----------
        inGUI : bool, optional
            Indicator showing if this function was called from the GUI or not. The default is False.
            For making Add-ons, please keep this set to False, it prevents infinite loops.

        Returns
        -------
        None.

        """
        if inGUI is True:
            self.statusC.configure(bg="yellow")
            self.statusC.update()

        # auto update bazaar
        if API_auto_update:
            self.update_prices(cooldown_warning=False)

        # Get inputs if none are given
        if setup_data is None:
            setup_data = self.get_inputs()

        # extracting often used minion constants
        minion_type = setup_data["minion"]
        minion_tier = setup_data["miniontier"]
        minion_amount = setup_data["amount"]
        minion_fuel = md.fuel_options[setup_data["fuel"]] 
        mayor = setup_data["mayor"]
        afk_toggle = setup_data["afk"]
        
        # create shared lists
        setup_notes = {}
        drops_list = {}

        # Enchanted Clock uses offline calculations, but you can be on the island when using it to apply boosts that require a loaded island.
        # This clock_override replaces afk_toggle for these boosts
        clock_override = False
        if setup_data["enchanted_clock"] and afk_toggle:
            afk_toggle = False
            clock_override = True

        # list upgrades types
        upgrades = [md.upgrade_options[setup_data["upgrade1"]], md.upgrade_options[setup_data["upgrade2"]]]
        upgrade_types = self.get_upgrade_types(upgrades)

        # adding up minion speed bonus
        speed_boost = self.get_speed_boosts(minion_type, minion_fuel, upgrades, afk_toggle, clock_override, setup_data)

        # multiply up minion drop bonus
        drop_multiplier = self.get_drop_multiplier(minion_type, minion_fuel, upgrades, afk_toggle, setup_data)

        # AFKing, Special Layouts and Player Harvests influences
        actions_per_harvest = self.get_actions_per_harvest(minion_type, upgrades, afk_toggle, setup_data, setup_notes)

        # AFK loot table changes
        self.update_loot_table(minion_type, minion_fuel, afk_toggle, setup_data)

        # calculate final minion speed
        seconds_per_action = self.get_seconds_per_action(minion_type, minion_tier, minion_fuel, speed_boost, setup_data)

        # time calculations
        emptytime_seconds, timeratio = self.get_emptytime_and_ratio(seconds_per_action, actions_per_harvest, setup_data)
        
        # harvests per time
        harvests_per_time, drop_multiplier = self.get_harvests_per_time(emptytime_seconds, actions_per_harvest, seconds_per_action, afk_toggle, drop_multiplier)

        # initialise drops list and get upgrade info
        spreading_info, replace_info = self.get_upgrade_info(upgrades, drops_list)
        
        # base drops
        self.get_base_drops(drops_list, spreading_info, replace_info, minion_type, harvests_per_time, drop_multiplier)

        # upgrade drops
        self.get_upgrade_drops(drops_list, spreading_info, minion_type, minion_tier, drop_multiplier, upgrades, harvests_per_time, afk_toggle, emptytime_seconds)
        
        # Inferno minion fuel drops
        self.get_inferno_drops(drops_list, spreading_info, replace_info, minion_type, minion_tier, minion_fuel, drop_multiplier, harvests_per_time, emptytime_seconds, afk_toggle, setup_data)

        # Apply compactors
        compacted_items = self.get_compacted_drops(drops_list, upgrade_types)

        # storage calculations
        available_storage = self.get_available_storage(minion_type, minion_tier, setup_data)
        used_storage = self.get_used_storage(drops_list)
        fill_time = self.get_fill_time(minion_type, available_storage)

        # multiply drops by minion amount
        # all processes as calculated above should be linear with minion amount
        self.deepmultiply(drops_list, minion_amount)

        sell_location, hopper_multiplier = self.get_sell_location(setup_data)
        # Coins
        item_profit, per_item_profit, per_item_sell_location = self.get_item_profit(sell_location, hopper_multiplier, drops_list)
        # XP
        skill_xp = self.get_skill_xp(afk_toggle, mayor, drops_list, setup_data)

        # Check for over-compacting
        self.get_over_compacting(sell_location, compacted_items, per_item_sell_location, setup_notes)
        
        # Pet leveling
        pet_profit, setup_pets = self.get_pet_profit(skill_xp, mayor, setup_notes, setup_data)

        # calculating beacon and limited fuel cost
        fuel_cost, needed_fuel = self.get_finite_fuel_cost(minion_amount, minion_fuel, emptytime_seconds, setup_data)

        # total profit
        total_profit = item_profit + pet_profit - fuel_cost

        # Setup cost
        total_cost, extra_cost, cost_per_part = self.get_setup_cost(minion_type, minion_tier, minion_amount, minion_fuel, upgrades, setup_notes, setup_data)

        # Construct ID
        setup_ID = self.construct_id(setup_data)

        # Get minion notes
        if "notes" in md.minionList[minion_type]:
            setup_notes.update(md.minionList[minion_type]["notes"])

        # collect outputs
        outputs = {
            "petProfit": pet_profit,
            "harvests": minion_amount * harvests_per_time,
            "itemtypeProfit": per_item_profit,
            "items": drops_list,
            "itemProfit": item_profit,
            "xp": skill_xp,
            "fuelcost": fuel_cost,
            "totalProfit": total_profit,
            "fuelamount": needed_fuel,
            "pets_levelled": {pet_slot: setup_pets[pet_slot]["levelled_pets"] for pet_slot in setup_pets.keys()}
        }

        self.deepmultiply(outputs, timeratio)
        outputs["fuelamount"] = np.ceil(outputs["fuelamount"] / minion_amount) * minion_amount
        outputs.update({
            "available_storage": available_storage,
            "itemSellLoc": per_item_sell_location,
            "ID_container": [setup_ID],
            "ID": setup_ID,
            "extracost": extra_cost,
            "setupcost": total_cost,
            "filltime": fill_time,
            "used_storage": used_storage,
            "emptytime": f"{self.emptytimeamount.get()} {self.emptytimelength.get()}",
            "time": f"{self.totaltimeamount.get()} {self.totaltimelength.get()}",
            "actiontime": seconds_per_action,
            "notes": setup_notes
        })

        # Update GUI
        if inGUI:
            self.send_to_GUI(outputs)
            if self.addons_auto_run["Rising Celsius Override"].get():
                self.addons_list["Rising Celsius Override"](self)
            for addon_name, auto_run_bool in self.addons_auto_run.items():
                if addon_name == "Rising Celsius Override":
                    continue
                if auto_run_bool.get():
                    self.addons_list[addon_name](self)
            self.update_listboxes()
            self.statusC.configure(bg="green")
            self.statusC.update()

        if return_outputs:
            return outputs
        return        

    def call_bazaar(self):
        """
        calls to Hypixel API for most recent bazaar data,
        handles that data to calculate accurate buy and sell prices.
        To get accurate prices, it takes a top percentage (top 10% default) of the orders and takes the average of them.

        Returns
        -------
        None

        """
        self.info_msg("Calling Bazaar")
        try:
            f = urllib.request.urlopen(r"https://api.hypixel.net/v2/skyblock/bazaar")
            call_data = f.read().decode('utf-8')
        except Exception as error:
            self.error_msg(f"Could not finish Bazaar API call\n{error}")
            return
        raw_data = json.loads(call_data)
        if "success" not in raw_data or raw_data["success"] is False:
            self.error_msg("Bazaar API call was unsuccessful")
            return
        self.info_msg("Bazaar call successful")
        self.API_timer = raw_data["lastUpdated"] / 1000
        self.variables["bazaar_update_txt"]["var"].set(time.strftime("%Y-%m-%d %H:%M:%S UTC%z", time.localtime(self.API_timer)))
        top_percent = 0.1
        for itemtype, item_data in md.itemList.items():
            if itemtype not in raw_data["products"]:
                continue
            for action in ["buy", "sell"]:
                top_amount = top_percent * sum([order["amount"] for order in raw_data["products"][itemtype][f"{action}_summary"]])
                if top_amount == 0:
                    item_data["prices"][f"{action}Price"] = 0
                    if "npc" not in item_data["prices"]:
                        self.warning_msg(f"no {action} supply for {itemtype}")
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
                top_percent_avg_price = top_sum / top_amount
                top_price = raw_data["products"][itemtype][f"{action}_summary"][0]["pricePerUnit"]
                if top_price / top_percent_avg_price >= 2.5:
                    item_data["prices"][f"{action}Price"] = top_price
                    self.info_msg(f"bottom heavy {action} supply for {itemtype}, taking top order price")
                else:
                    item_data["prices"][f"{action}Price"] = top_percent_avg_price
        return

    def call_auction_house(self, item_id):
        """
        API call to SkyCofl to update Auction House price of the given item.

        AH data from https://sky.coflnet.com/data

        :param item_id: item ID

        Returns
        -------
        None.

        """

        try:
            postcard_url = r"https://sky.coflnet.com/api/item/price/" + item_id + r"/bin"
            req = urllib.request.Request(postcard_url, headers={'User-Agent': f"Minion Calculator v{self.version.get()} (Python)", })
            call_data = urllib.request.urlopen(req).read().decode('utf-8')
        except Exception as error:
            self.error_msg(f"Could not finish SkyCofl API call for {item_id}\n{error}")
            return
        raw_data = json.loads(call_data)
        return (raw_data["lowest"] + raw_data["secondLowest"]) / 2

    def update_prices(self, cooldown_warning=True):
        """
        Updates item prices.

        If API_cooldown is done, also update API
        
        :param cooldown_warning: bool, toggle if a terminal message should be printed if the bazaar update cooldown has not passed yet.
        """
        if time.time() - self.API_timer < API_cooldown and self.API_timer != 0:
            if cooldown_warning:
                self.info_msg("API update is on cooldown")
        else:
            self.call_bazaar()
            self.info_msg("Updating Auction House prices")
            md.itemList["POSTCARD"]["prices"]["custom"] = self.call_auction_house("POSTCARD")
        return

    def update_listboxes(self):
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
                format_function = lambda x: x
                if "IDtoDisplay" in var_data and var_data["IDtoDisplay"] is True:
                    format_function = lambda x: md.itemList[x]["display"]
                elif var_key == "pets_levelled":
                    format_function = lambda x: self.variables[x]["var"].get()

                listbox_list.clear()
                if type(var_data["list"]) is dict:
                    for key, val in var_data["list"].items():
                        if var_key == "pets_levelled" and format_function(key) == "None":
                            continue
                        listbox_list.append(f'{format_function(key)}: {val}')
                elif type(var_data["list"]) is list:
                    for val in var_data["list"]:
                        listbox_list.append(format_function(val))
                var_data["var"].set(listbox_list)
        return

    def collect_addon_output(self, output_name, output_str):
        """
        Collect outputs from add-ons, places them in addons_output_container
        and updates the GUI for addons_output_container

        Parameters
        ----------
        output_name : str
            Short description of what the output represents. Recommended description is the add-on name
        output_str : str
            The output of the calculation in the add-on.

        Returns
        -------
        None.

        """
        self.variables["addons_output_container"]["list"][output_name] = output_str
        listbox_list = []
        for key, val in self.variables["addons_output_container"]["list"].items():
            listbox_list.append(f'{key}: {val}')
        self.variables["addons_output_container"]["var"].set(listbox_list)
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
    print("CLOSING: Exited mainloop")
    try:
        App.destroy()
        print("CLOSING: Detroyed application")
    except Exception:
        print("ERROR: Please use the stop button in the bottom right to close the application")
    print("CLOSING: Closed")
    return

if __name__ == "__main__":
    start_app()
else:
    print("Run `main.py` directly to start the calculator")
