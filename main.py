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

# Bazaar settings
bazaar_auto_update = True
# If true, bazaar automatically updates before performing calculation
bazaar_cooldown = 60  # seconds
# Time limit in seconds between each automatic update
compact_tolerance = 10000  # coins
# Minimum coin loss per compacting action for the calculator to make a note of coin loss

# Output settings
output_to_clipboard = True
# If true, Short Output and Share Output also get saved in your clipboard

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
        print("BOOTING: Hero UI Manager loaded")
        self.huim.createControls()
        self.huim.createFrames(self, frame_keys=[["inputs_minion", "inputs_player", "outputs_setup", "outputs_profit"]], grid_frames=True, grid_size=0.96, border=0.003)
        self.frames["addons_main"] = tk.Frame(self, background=self.colors["background"])
        self.huim.createFrames(self.frames["addons_main"], frame_keys=[["addons_buttons", "addons_output"]], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0)
        print("BOOTING: Framework set up")
        self.version = self.huim.defVar(dtype=float, initial=1.2)
        print(f"BOOTING: Calculator version {self.version.get()}")

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
        self.wisdomB = tk.Button(self.frames["inputs_player_grid"], text='Edit', command=lambda: self.huim.edit_vars(self.update_GUI_wisdom, ["combatWisdom", "miningWisdom", "farmingWisdom", "fishingWisdom", "foragingWisdom", "alchemyWisdom"]))
        self.wisdomB.place(in_=self.variables["wisdom"]["widget"][-1], relx=1, x=3, rely=0.5, anchor='w')

        self.rising_celsius_override = False

        self.emptytimeamount, self.emptytimeamountI = self.huim.defVarI(dtype=float, frame=self.frames["inputs_player_grid"], L_text="Empty Time span:", initial=1.0)
        self.emptytimelength, self.emptytimelengthI = self.huim.defVarI(dtype=str, frame=self.frames["inputs_player_grid"], L_text="Empty Time Length:", initial="Days", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.emptytimelengthI[-1].place(in_=self.emptytimeamountI[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.totaltimeamount, self.totaltimeamountI = self.huim.defVarI(dtype=float, frame=self.frames["inputs_player_grid"], L_text="Total Time span:", initial=1.0)
        self.totaltimelength, self.totaltimelengthI = self.huim.defVarI(dtype=str, frame=self.frames["inputs_player_grid"], L_text="Total Time Length:", initial="Days", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.totaltimelengthI[-1].place(in_=self.totaltimeamountI[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.notesAnchor = self.huim.genLabel(frm=self.frames["outputs_setup_grid"], txt="")

        print("BOOTING: self.variables initialized")

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
        self.fancyoutputB = tk.Button(self.frames["controls"], text='Share Output', command=self.fancyOutput)
        self.calcB = tk.Button(self.frames["controls"], text='Calculate', command=lambda: self.calculate(True))
        self.statusC = tk.Canvas(self.frames["controls"], bg="green", width=10, height=10, borderwidth=0)
        self.addonsB = tk.Button(self.frames["controls"], text="Add-ons Menu", command=lambda: self.huim.toggleSwitch("addons"))
        self.bazaarB = tk.Button(self.frames["controls"], text="Update Bazaar", command=self.update_bazaar)
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

        print("BOOTING: Widgets placed")

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
        
        print("BOOTING: Switches activated")

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
        print("BOOTING: Output orders defined")

        # Load bazaar prices
        print("BOOTING: Connecting to bazaar")
        self.bazaar_timer = 0
        self.update_bazaar(cooldown_warning=False)
        print("BOOTING: Ready")
        return

#%% functions

    def time_number(self, time_length, time_amount, secondsPaction=0.0, actionsPerHarvest=1.0):
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
            return str(np.round(number, decimal - 1 + int(np.abs(np.floor(np.log10(np.abs(number)))))))
        highest_reduction = min(int(np.floor(np.log10(np.abs(number))) / 3), len(reduced_amounts) - 1)
        reduced = np.round((number / (10 ** (3 * highest_reduction))), decimal)
        output_string = f'{reduced}{reduced_amounts[highest_reduction]}'
        return output_string

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
        if templateName == "Choose Template":
            return
        self.template.set("Choose Template")
        if templateName == "ID":
            template = self.decodeID(self.loadID.get())
        elif templateName == "Clean":
            template = {var_key: self.variables[var_key]["initial"] for var_key in self.variables if self.variables[var_key]["vtype"] == "input" and var_key not in ["minion", "miniontier"]}
        else:
            template = templateList[templateName]
        for setting, variable in template.items():
            self.variables[setting]["var"].set(variable)
            if "command" in self.variables[setting] and self.variables[setting]["command"] is not None:
                if type(variable) == bool:
                    self.variables[setting]["command"]()
                else:
                    self.variables[setting]["command"](variable)
            if "Wisdom" in setting:
                self.update_GUI_wisdom()
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
        if output_to_clipboard:
            self.clipboard_clear()
            self.clipboard_append(crafted_string)
        if toTerminal:
            print(crafted_string, "\n")
            return
        else:
            return crafted_string

    def get_inputs(self):
        template = {}
        for key in self.ID_order:
            var_data = self.variables[key]
            if var_data["vtype"] != "input":
                self.catch_warning("self.ID_order contains non-input variable")
                continue
            template[key] = var_data["var"].get()
        return template

    def constructID(self, template):
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
        setup_id = str(self.version.get()) + "!"
        for key, val in template.items():
            var_options = self.variables[key]["options"]
            if len(var_options) == 0:
                if int(val) == val:
                    val = int(val)
                setup_id += "!" + str(val) + "!"
            else:
                index = var_options.index(val)
                setup_id += chr(48 + index)
        return setup_id

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
            print("WARNING: Invalid ID, Incompatible version")
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
                print("WARNING:", ID, "no forced cost found")
                return 0
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

    def getPetXPBoosts(self, pet, xp_type, exp_share=False):
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

    def catch_warning(self, warning_message):
        """
        Warning catching system used during calculations.

        Parameters
        ----------
        warning_message : string
            Warning text.

        Returns
        -------
        None.

        """
        if "WARNING" not in self.variables["notes"]["list"]:
            self.variables["notes"]["list"]["WARNING"] = "Check terminal for warning"
        print("WARNING: " + warning_message)
        return

    def calculate(self, inGUI=False):
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
        if bazaar_auto_update:
            self.update_bazaar(cooldown_warning=False)

        # clear list outputs from previous calculation
        for var_key, var_data in self.variables.items():
            if var_data["vtype"] == "list":
                if var_key == "wisdom":
                    continue
                var_data["list"].clear()

        # Get inputs
        setup_template = self.get_inputs()

        # extracting often used minion constants
        minion_type = self.variables["minion"]["var"].get()
        minion_tier = self.variables["miniontier"]["var"].get()
        minion_amount = self.variables["amount"]["var"].get()
        minion_fuel = md.fuel_options[self.variables["fuel"]["var"].get()]
        minion_beacon = self.variables["beacon"]["var"].get()
        mayor = self.variables["mayor"]["var"].get()

        # Enchanted Clock uses offline calculations, but you can be on the island when using it to apply boosts that require a loaded island.
        # This clock_override replaces afk_toggle for these boosts
        afk_toggle = self.variables["afk"]["var"].get()
        clock_toggle = self.variables["enchanted_clock"]["var"].get()
        clock_override = False
        if clock_toggle and afk_toggle:
            afk_toggle = False
            clock_override = True

        # list upgrades types
        upgrades = [md.upgrade_options[self.variables["upgrade1"]["var"].get()], md.upgrade_options[self.variables["upgrade2"]["var"].get()]]
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
        speedBonus += 10 * self.variables["free_will"]["var"].get() + 5 * self.variables["postcard"]["var"].get()
        speedBonus += 5 * self.variables["potatoTalisman"]["var"].get() * (afk_toggle or clock_override) * (minion_type == "Potato")
        if self.variables["crystal"]["var"].get() != "None":
            if minion_type in list(md.floating_crystals[self.variables["crystal"]["var"].get()].values())[0]:
                speedBonus += list(md.floating_crystals[self.variables["crystal"]["var"].get()].keys())[0]
        if minion_beacon != 0:
            speedBonus += 1 * self.variables["scorched"]["var"].get()
        if minion_type == "Inferno":
            if self.rising_celsius_override:
                speedBonus += 180
            else:
                speedBonus += 18 * min(10, minion_amount)
        if mayor == "Cole" and (afk_toggle or clock_override) and minion_type in md.affected_by_cole:
            speedBonus += 25
        afkpet = self.variables["afkpet"]["var"].get()
        afkpet_rarity = self.variables["afkpetrarity"]["var"].get()
        afkpet_lvl = self.variables["afkpetlvl"]["var"].get()
        if (afk_toggle or clock_override) and minion_type in md.boost_pets[afkpet]["affects"] and afkpet_rarity in md.boost_pets[afkpet]:
            speedBonus += md.boost_pets[afkpet][afkpet_rarity][0] + afkpet_lvl * md.boost_pets[afkpet][afkpet_rarity][1]

        # multiply up minion drop bonus
        dropMultiplier = 1
        dropMultiplier *= md.itemList[minion_fuel]["upgrade"]["drop"]
        dropMultiplier *= md.itemList[upgrades[0]]["upgrade"]["drop"]
        if afk_toggle and dropMultiplier > 1:
            # drop multiplier greater than 1 is rounded down while online
            dropMultiplier = int(dropMultiplier)
        dropMultiplier *= md.itemList[upgrades[1]]["upgrade"]["drop"]
        if afk_toggle and dropMultiplier > 1:
            dropMultiplier = int(dropMultiplier)
        if mayor == "Derpy":
            dropMultiplier *= 2

        # AFKing, Special Layouts and Player Harvests influences
        actionsPerHarvest = 2
        if minion_type == "Fishing":
            # only has harvests actions
            actionsPerHarvest = 1
        if afk_toggle:
            if minion_type in ["Pumpkin", "Melon"]:
                # pumpkins and melons are forced to regrow for minion to harvest
                actionsPerHarvest = 1
            if self.variables["playerHarvests"]["var"].get():
                if minion_type in ["Fishing", "Pumpkin", "Melon"]:
                    self.variables["notes"]["list"]["Player Harvests"] = "Player Harvesting does not work with this minion"
                else:
                    actionsPerHarvest = 1
                    dropMultiplier = 1
                    if minion_type in ["Gravel"]:
                        upgrades.append("FLINT_SHOVEL")
                        self.variables["notes"]["list"]["Player Tools"] = "Assuming Player is using Flint Shovel"
                    if minion_type in ["Ice"]:
                        self.variables["notes"]["list"]["Player Tools"] = "Assuming Player is using Silk Touch"
                    if minion_type in ["Zombie", "Revenant", "Voidling", "Inferno", "Vampire", "Skeleton", "Creeper", "Spider", "Tarantula", "Cave Spider", "Blaze", "Magma Cube", "Enderman", "Ghast", "Slime", "Cow", "Pig", "Chicken", "Sheep", "Rabbit"]:
                        dropMultiplier *= 1 + 15 * self.variables["playerLooting"]["var"].get() / 100
            elif self.variables["specialLayout"]["var"].get():
                if minion_type in ["Cobblestone", "Mycelium", "Ice"]:
                    # cobblestone generator, regrowing mycelium, freezing water
                    actionsPerHarvest = 1
                if minion_type in ["Flower", "Sand", "Red Sand", "Gravel"]:
                    # harvests through natural means: water flushing, gravity
                    actionsPerHarvest = 1
                    # speedBonus -= 10  # only spawning has 10% action speed reduction, not confirmed yet.

        # AFK loot table changes
        if minion_type in ['Oak', 'Spruce', 'Birch', 'Dark Oak', 'Acacia', 'Jungle']:
            if afk_toggle:
                # chopped trees have 4 blocks of wood, unknown why offline gives 3
                md.minionList[minion_type]["drops"][md.getID[f"{minion_type} Log"]] = 4
            else:
                md.minionList[minion_type]["drops"][md.getID[f"{minion_type} Log"]] = 3
        if minion_type == "Gravel":
            if afk_toggle:
                # vanilla minecraft chance for gravel to become flint
                md.minionList[minion_type]["drops"]["GRAVEL"] = 0.9
                md.minionList[minion_type]["drops"]["FLINT"] = 0.1
            else:
                md.minionList[minion_type]["drops"]["GRAVEL"] = 1
                md.minionList[minion_type]["drops"]["FLINT"] = 0
        if minion_type == "Pumpkin":
            if afk_toggle:
                # it just does this, idk, ask Hypixel
                md.minionList[minion_type]["drops"]["PUMPKIN"] = 1
            else:
                md.minionList[minion_type]["drops"]["PUMPKIN"] = 3
        if minion_type == "Flower":
            if afk_toggle and self.variables["specialLayout"]["var"].get():
                # tall flowers blocked by low ceiling
                md.minionList[minion_type]["drops"] = { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "SMALL_FLOWER": 0.5 }
            else:
                md.minionList[minion_type]["drops"] = { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "SMALL_FLOWER": 1 / 3, "LARGE_FLOWER": 1 / 6 }

        # calculate final minion speed
        base_speed = md.minionList[minion_type]["speed"][minion_tier]
        secondsPaction = base_speed / (1 + speedBonus / 100)
        if minion_fuel == "INFERNO_FUEL":
            secondsPaction /= 1 + md.infernofuel_data["grades"][md.getID[self.variables["infernoGrade"]["var"].get()]]

        # time calculations
        if self.variables["often_empty"]["var"].get():
            emptytimeNumber = self.time_number(self.emptytimelength.get(), self.emptytimeamount.get(), secondsPaction, actionsPerHarvest)
            timeNumber = self.time_number(self.totaltimelength.get(), self.totaltimeamount.get(), secondsPaction, actionsPerHarvest)
            timeratio = timeNumber / emptytimeNumber
            self.variables["emptytime"]["var"].set(f"{self.emptytimeamount.get()} {self.emptytimelength.get()}")
        else:
            emptytimeNumber = self.time_number(self.totaltimelength.get(), self.totaltimeamount.get(), secondsPaction, actionsPerHarvest)
            timeratio = 1
        self.variables["time"]["var"].set(f"{self.totaltimeamount.get()} {self.totaltimelength.get()}")
        if self.emptytimelength.get() == "Harvests":
            harvestsPerTime = self.emptytimeamount.get()
        else:
            harvestsPerTime = emptytimeNumber / (actionsPerHarvest * secondsPaction)
        self.variables["actiontime"]["var"].set(secondsPaction)
        self.variables["harvests"]["var"].set(minion_amount * harvestsPerTime * timeratio)

        # drop multiplier online/offline mode
        if not afk_toggle:
            harvestsPerTime *= dropMultiplier
            dropMultiplier = 1

        # base drops
        for item, amount in md.minionList[minion_type]["drops"].items():
            self.variables["items"]["list"][item] = harvestsPerTime * amount * dropMultiplier

        # upgrade drops
        # create seperate dict to keep it separate from the main drops
        # because some upgrades use main drops to generate something
        upgrade_drops = {}
        spreading_drops = {}
        cooldown_drops = {}
        for upgrade in upgrades:
            upgrade_type = md.itemList[upgrade]["upgrade"]["special"]["type"]
            if "replace" in upgrade_type:
                # replacing upgrades are like Auto Smelters
                items = list(self.variables["items"]["list"].keys())
                for item in items:
                    if item in md.itemList[upgrade]["upgrade"]["special"]["list"]:
                        replacement_item = md.itemList[upgrade]["upgrade"]["special"]["list"][item]
                        if replacement_item not in self.variables["items"]["list"]:
                            self.variables["items"]["list"][replacement_item] = 0
                        self.variables["items"]["list"][replacement_item] += self.variables["items"]["list"].pop(item)
            if upgrade_type == "generate":
                # generating upgrades are like Diamond Spreadings
                finalAmount = 0
                spreading_chance = md.itemList[upgrade]["upgrade"]["special"]["chance"]
                for amount in self.variables["items"]["list"].values():
                    finalAmount += spreading_chance * amount
                if minion_fuel == "INFERNO_FUEL" and afk_toggle:
                    finalAmount /= 5
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    if item not in spreading_drops:
                        spreading_drops[item] = 0
                    spreading_drops[item] += finalAmount * amount
            elif upgrade_type == "add":
                # adding upgrades are like Corrupt Soils
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    if item not in upgrade_drops:
                        upgrade_drops[item] = 0
                    upgrade_drops[item] += harvestsPerTime * amount
            elif upgrade_type == "timer":
                # timer upgrades are like Soulflow Engines
                # formula for effective_cooldown still in research
                # if afk_toggle:
                #     effective_cooldown = 2 * secondsPaction * (1 + np.floor(np.ceil(md.itemList[upgrade]["upgrade"]["special"]["cooldown"] / secondsPaction) / 2))
                # else:
                #     effective_cooldown = ???
                if afk_toggle and upgrade == "LESSER_SOULFLOW_ENGINE" and "SOULFLOW_ENGINE" in upgrades:
                    continue  # Soulflow Engine overrides Lesser Soulflow Engine while online
                effective_cooldown = md.itemList[upgrade]["upgrade"]["special"]["cooldown"]
                for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                    if item not in cooldown_drops:
                        cooldown_drops[item] = 0
                    cooldown_drops[item] += amount * emptytimeNumber / effective_cooldown

        # other upgrades behaviours
        if afk_toggle:
            if "CORRUPT_SOIL" in upgrades:
                if "afkcorrupt" in md.minionList[minion_type]:
                    # Certain mob minions get more corrupt drops when afking
                    # It is not a constant multiplier, it is equivalent in chance to the main drops of the minion
                    upgrade_drops["SULPHUR_ORE"] *= md.minionList[minion_type]["afkcorrupt"]
                    upgrade_drops["CORRUPTED_FRAGMENT"] *= md.minionList[minion_type]["afkcorrupt"]
                if minion_type == "Chicken" and "ENCHANTED_EGG" not in upgrades:
                    # Online Chicken minion without Enchanted Egg does not make corrupt drops
                    upgrade_drops["SULPHUR_ORE"] = 0
                    upgrade_drops["CORRUPTED_FRAGMENT"] = 0
            if "ENCHANTED_EGG" in upgrades:
                # Enchanted Eggs make one laid egg and one egg on kill while AFKing
                # the egg on spawn is affected by drop multipliers
                upgrade_drops["EGG"] *= 1 + dropMultiplier
        else:
            if "ENCHANTED_SHEARS" in upgrades:
                # No wool gets added from Enchanted Shears when offline
                upgrade_drops["WOOL"] = 0
        if "SOULFLOW_ENGINE" in upgrades and minion_type == "Voidling":
            cooldown_drops["RAW_SOULFLOW"] *= 1 + 0.03 * minion_tier  # correct most likely, needs testing

        # spreading upgrades triggering from some upgrade drops
        for upgrade in upgrades:
            upgrade_type = md.itemList[upgrade]["upgrade"]["special"]["type"]
            if upgrade_type != "generate":
                continue
            else:
                spreading_chance = md.itemList[upgrade]["upgrade"]["special"]["chance"]
                if afk_toggle:
                    if "ENCHANTED_EGG" in upgrades:
                        # the egg on spawn triggers spreadings
                        for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                            if item not in spreading_drops:
                                spreading_drops[item] = 0
                            spreading_drops[item] += harvestsPerTime * dropMultiplier * spreading_chance * amount
                else:
                    finalAmount = 0
                    for amount in upgrade_drops.values():
                        finalAmount += spreading_chance * amount
                    for item, amount in md.itemList[upgrade]["upgrade"]["special"]["item"].items():
                        if item not in spreading_drops:
                            spreading_drops[item] = 0
                        spreading_drops[item] += finalAmount * amount

        # Inferno minion fuel drops
        # https://wiki.hypixel.net/Inferno_Minion_Fuel
        if minion_fuel == "INFERNO_FUEL":
            # distilate drops
            distilate = md.getID[self.variables["infernoDistillate"]["var"].get()]
            distilate_item = md.infernofuel_data["distilates"][distilate][0]
            amount_per = md.infernofuel_data["distilates"][distilate][1]
            distillate_harvests = (harvestsPerTime * 4) / 5
            upgrade_drops[distilate_item] = distillate_harvests * amount_per
            static_items = list(self.variables["items"]["list"].keys())  # create copy to edit list while looping it
            for item in static_items:  # replacing main drops with distilate drops
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
                upgrade_drops["HYPERGOLIC_IONIZED_CERAMICS"] = emptytimeNumber / md.itemList[minion_fuel]["upgrade"]["duration"]

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


        # add upgrade drops to main item list
        upgrade_drops.update(spreading_drops)
        upgrade_drops.update(cooldown_drops)
        for item, amount in upgrade_drops.items():
            if item not in self.variables["items"]["list"]:
                self.variables["items"]["list"][item] = 0
            self.variables["items"]["list"][item] += amount

        # (Super) Compactor logic at the end because it applies to all drops
        # for both compactor types it floors the ratio between items and needed items for one compacted
        # multiplies the floored ratio if the action creates multiple compacted item
        # uses modulo to find the left over amount
        # keeps track of which items have been compacted to check for loss of profit
        # saves per item the following dict
        # {"from": item, "makes": compact item, "amount": amount of compacted, "per": amount of item needed}
        compacted_items = []
        # Compactors
        # loops once through item list because there are no double normal compacted items
        if "compact" in upgrades_types:
            static_items = list(self.variables["items"]["list"].items())
            for item, amount in static_items:
                if item in md.compactorList:
                    compact_name = md.compactorList[item]["makes"]
                    percompact = md.compactorList[item]["per"]
                    compact_amount = int(amount / percompact)
                    if compact_amount == 0:
                        continue
                    if "amount" in md.compactorList[item]:
                        compact_amount *= md.compactorList[item]["amount"]
                    left_over = amount % percompact
                    if left_over == 0.0:  # floating point error may cause extremely small numbers that should have been 0 too not trigger this
                        del self.variables["items"]["list"][item]
                    else:
                        self.variables["items"]["list"][item] = left_over
                    self.variables["items"]["list"][compact_name] = compact_amount
                    compacted_items.append({"from": item, **md.compactorList[item]})
            pass

        # Super compactor
        # loops continously through the item list until is cannot find something to compact
        if "enchant" in upgrades_types:
            found_enchantable = True
            safety_lock = 0
            while found_enchantable is True:
                safety_lock += 1
                if safety_lock >= 10:  # safety to prevent an infinite while loop
                    self.catch_warning("While-loop overflow, super compactor 3000")
                    break
                found_enchantable = False
                static_items = list(self.variables["items"]["list"].items())
                for item, amount in static_items:
                    if item in md.enchanterList:
                        enchanted_name = md.enchanterList[item]["makes"]
                        perenchanted = md.enchanterList[item]["per"]
                        enchanted_amount = int(amount / perenchanted)
                        if enchanted_amount == 0:
                            continue
                        if "amount" in md.enchanterList[item]:
                            enchanted_amount *= md.enchanterList[item]["amount"]
                        left_over = amount % perenchanted
                        if left_over == 0.0:
                            del self.variables["items"]["list"][item]
                        else:
                            self.variables["items"]["list"][item] = left_over
                        self.variables["items"]["list"][enchanted_name] = enchanted_amount
                        compacted_items.append({"from": item, **md.enchanterList[item]})
                        if enchanted_name in md.enchanterList:
                            found_enchantable = True

        # storage calculations
        # amount of storage measured in slots
        available_storage = md.minion_chests[self.variables["chest"]["var"].get()]
        if "storage" in md.minionList[minion_type] and minion_tier in md.minionList[minion_type]["storage"]:
            available_storage += md.minionList[minion_type]["storage"][minion_tier]
        else:
            available_storage += md.standard_storage[minion_tier]

        # WARNING: calculation for fill_time does not work with compactors and is not accurate for setup with multiple drops
        # used_storage_slots calculations work fine.
        used_storage = 0
        used_storage_slots = 0
        for itemtype, amount in self.variables["items"]["list"].items():
            used_storage += amount / 64  # hypixel does not care about smaller max stack sizes
            used_storage_slots += np.ceil(amount / 64)
        fill_time = (emptytimeNumber * available_storage) / used_storage
        self.variables["filltime"]["var"].set(fill_time)
        self.variables["used_storage"]["var"].set(used_storage_slots)
        self.variables["available_storage"]["var"].set(available_storage)

        # multiply drops by minion amount
        # all processes as calculated above should be linear with minion amount
        for itemtype in self.variables["items"]["list"].keys():
            self.variables["items"]["list"][itemtype] *= minion_amount

        # convert items into coins and xp
        # while keeping track where items get sold
        # it makes a list of all prices and takes the one that matches the choice of sellLoc
        minion_hopper = self.variables["hopper"]["var"].get()
        minion_sellLoc = self.variables["sellLoc"]["var"].get()
        coinsPerTime = 0.0
        sellto = "NPC"
        hopper_multiplier = 1
        if minion_sellLoc == "Bazaar":
            sellto = "bazaar"
        elif minion_sellLoc == "Best (NPC/Bazaar)":
            sellto = "best"
        elif minion_sellLoc == "Hopper":
            hopper_multiplier = md.hopper_data[minion_hopper]
        prices = {}
        # Coins
        if minion_sellLoc != "None":
            for itemtype, amount in self.variables["items"]["list"].items():
                prices.clear()
                prices["NPC"] = self.getPrice(itemtype, "sell", "npc")
                prices["bazaar"] = self.getPrice(itemtype, "sell", "bazaar")
                # prices["custom"] = self.getPrice(itemtype, "sell", "custom", force=True)  # might use later
                if sellto in prices:
                    self.variables["itemSellLoc"]["list"][itemtype] = sellto
                    final_price = prices[sellto]
                else:
                    self.variables["itemSellLoc"]["list"][itemtype] = max(prices, key=prices.get)
                    final_price = prices[self.variables["itemSellLoc"]["list"][itemtype]]
                self.variables["itemtypeProfit"]["list"][itemtype] = amount * final_price * hopper_multiplier
                coinsPerTime += amount * final_price
        # XP
        for itemtype, amount in self.variables["items"]["list"].items():
            xptype, value = list(*md.itemList[itemtype]["xp"].items())
            if value == 0:
                continue
            if xptype not in self.variables["xp"]["list"]:
                self.variables["xp"]["list"][xptype] = 0
            self.variables["xp"]["list"][xptype] += amount * value * (1 + self.variables["wisdom"]["list"][xptype].get() / 100)
        if mayor == "Derpy":
            for xptype in self.variables["xp"]["list"].keys():
                self.variables["xp"]["list"][xptype] *= 1.5
        coinsPerTime *= hopper_multiplier
        self.variables["itemProfit"]["var"].set(coinsPerTime * timeratio)
        if afk_toggle and self.variables["playerHarvests"]["var"].get() and "combat" in self.variables["xp"]["list"]:
            del self.variables["xp"]["list"]["combat"]

        # Check for over-compacting
        if sellto in ["best", "bazaar"]:
            overcompacting = []
            for data in compacted_items:
                item = data["from"]
                compact_item = data["makes"]
                per_compact = data["per"]
                compact_amount = 1
                if "amount" in data:
                    compact_amount = data["amount"]
                cost = self.getPrice(item, "sell", "bazaar") * per_compact
                compact_cost = self.getPrice(compact_item, "sell", "bazaar") * compact_amount
                if cost - compact_cost > compact_tolerance:
                    overcompacting.append(md.itemList[item]['display'])
            if len(overcompacting) != 0:
                self.variables["notes"]["list"]["Over-compacting"] = ', '.join(overcompacting)

        # Pet leveling calculations
        # https://wiki.hypixel.net/Pets#Leveling
        # for Golden Dragon: special algorithm taking into account that pet items cannot be applied to Golden Dragon Eggs
        # the pet costs are manually added in pet_data
        petProfitPerTime = 0.0
        all_pets = {
            "levelingpet": {"pet": self.variables["levelingpet"]["var"].get(), "pet_xp": {}, "levelled_pets": 0.0},
            "expsharepet": {"pet": self.variables["expsharepet"]["var"].get(), "pet_xp": {"exp_share": 0.0}, "levelled_pets": 0.0},
            "expsharepetslot2": {"pet": self.variables["expsharepetslot2"]["var"].get(), "pet_xp": {"exp_share": 0.0}, "levelled_pets": 0.0},
            "expsharepetslot3": {"pet": self.variables["expsharepetslot3"]["var"].get(), "pet_xp": {"exp_share": 0.0}, "levelled_pets": 0.0}
        }
        main_pet = self.variables["levelingpet"]["var"].get()
        main_pet_xp = all_pets["levelingpet"]["pet_xp"]
        if main_pet != "None":
            if main_pet in ["Golden Dragon", "Jade Dragon"]:
                left_over_pet_xp = 0.0
                for skill, amount in self.variables["xp"]["list"].items():
                    pet_xp_boost, xp_boost_pet_item = self.getPetXPBoosts(main_pet, skill)
                    main_pet_xp[skill], left_over_pet_xp = self.dragon_xp(amount, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item)
            else:
                for skill, amount in self.variables["xp"]["list"].items():
                    pet_xp_boost, xp_boost_pet_item = self.getPetXPBoosts(main_pet, skill)
                    main_pet_xp[skill] = amount * pet_xp_boost * xp_boost_pet_item
            exp_share_boost = 0.2 * self.variables["taming"]["var"].get() + 10 * (self.variables["mayor"]["var"].get() == "Diana") + self.variables["toucan_attribute"]["var"].get()
            exp_share_item = 15 * self.variables["expshareitem"]["var"].get()
            for pet_slot, pet_info in all_pets.items():
                if pet_slot == "levelingpet":
                    continue
                exp_share_pet = pet_info["pet"]
                if exp_share_pet != "None": 
                    if exp_share_pet in ["Golden Dragon", "Jade Dragon"]:
                        if exp_share_boost == 0:
                            continue
                        left_over_pet_xp = 0.0
                        for skill, amount in main_pet_xp.items():
                            non_matching = self.getPetXPBoosts(exp_share_pet, skill, True)
                            equiv_pet_xp_boost = non_matching * (exp_share_boost / 100)
                            equiv_xp_boost_pet_item = 1 + exp_share_item / exp_share_boost
                            gained_pet_xp, left_over_pet_xp = self.dragon_xp(amount, left_over_pet_xp, equiv_pet_xp_boost, equiv_xp_boost_pet_item)
                            pet_info["pet_xp"]["exp_share"] += gained_pet_xp
                    else:
                        for skill, amount in main_pet_xp.items():
                            non_matching = self.getPetXPBoosts(exp_share_pet, skill, True)
                            pet_info["pet_xp"]["exp_share"] += amount * ((exp_share_boost + exp_share_item * (exp_share_pet != "Golden Dragon (lvl 1-100)")) / 100) * non_matching
                if mayor != "Diana":
                    break
            exp_share_price = self.getPrice("PET_ITEM_EXP_SHARE", "buy", "custom", True)
            if exp_share_price == 0:
                exp_share_price = self.getPrice("PET_ITEM_EXP_SHARE_DROP", "buy", "bazaar") + 72 * self.getPrice("ENCHANTED_GOLD", "buy", "bazaar")
            for pet_slot, pet_info in all_pets.items():
                self.variables["pets_levelled"]["list"][pet_slot] = sum(pet_info["pet_xp"].values()) / md.max_lvl_pet_xp_amounts[md.all_pets[pet_info["pet"]]["rarity"]]
                if pet_info["pet"] not in pet_costs:
                    self.variables["notes"]["list"]["Pet Costs"] = f"{pet_info['pet']} is not in pet_costs."
                else:
                    petProfitPerTime += self.variables["pets_levelled"]["list"][pet_slot] * (pet_costs[pet_info["pet"]]["max"] - pet_costs[pet_info["pet"]]["min"])
                if pet_slot == "levelingpet" and (main_pet_item := self.variables["petxpboost"]["var"].get()) != "None":
                    petProfitPerTime -= self.variables["pets_levelled"]["list"][pet_slot] * self.getPrice(md.getID[main_pet_item], "buy", "custom", True)
                elif self.variables["expshareitem"]["var"].get():
                    petProfitPerTime -= self.variables["pets_levelled"]["list"][pet_slot] * exp_share_price
                self.variables["pets_levelled"]["list"][pet_slot] *= timeratio

        self.variables["petProfit"]["var"].set(petProfitPerTime * timeratio)

        # calculating beacon and limited fuel cost
        fuelCostPerTime = 0.0
        neededFuelPerTime = 0.0
        if minion_beacon != 0:
            if self.variables["scorched"]["var"].get():
                beacon_fuel_ID = "SCORCHED_POWER_CRYSTAL"
            else:
                beacon_fuel_ID = "POWER_CRYSTAL"
            costPerCrystal = self.getPrice(beacon_fuel_ID, "buy", "bazaar")
            fuelCostPerTime += emptytimeNumber * costPerCrystal / md.itemList[beacon_fuel_ID]["duration"] * int(not (self.variables["B_constant"]["var"].get()))
        if md.itemList[minion_fuel]["upgrade"]["duration"] != 0:
            costPerFuel = self.getPrice(minion_fuel, "buy", "bazaar")
            neededFuelPerTime = minion_amount * emptytimeNumber / md.itemList[minion_fuel]["upgrade"]["duration"]
            fuelCostPerTime += neededFuelPerTime * costPerFuel
        self.variables["fuelcost"]["var"].set(fuelCostPerTime * timeratio)
        self.variables["fuelamount"]["var"].set(np.max([neededFuelPerTime * timeratio, minion_amount]))

        # Setup cost
        total_cost = 0.0
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
                    cost_cache[item] = self.getPrice(item, "buy", "bazaar")
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
            self.variables["notes"]["list"]["Extra cost"] = ", ".join([f"{amount} {material}" for material, amount in tiered_extra_cost[minion_tier].items()]) + " per minion"
            self.variables["extracost"]["var"].set(", ".join([f"{amount * minion_amount} {material}" for material, amount in tiered_extra_cost[minion_tier].items()]))
        else:
            self.variables["extracost"]["var"].set("")
        total_cost += tiered_coin_cost[minion_tier]

        # Infinite fuel cost
        if minion_fuel != "NONE" and md.itemList[minion_fuel]["upgrade"]["duration"] == 0:
            if minion_fuel == "EVERBURNING_FLAME" and self.getPrice("EVERBURNING_FLAME", "buy", "custom", True) == 0:
                for item_ID, amount in md.upgrades_material_cost["EVERBURNING_FLAME"].items():
                    total_cost += amount * self.getPrice(item_ID, "buy", "bazaar")
            else:
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
        free_will_price = self.getPrice("FREE_WILL", "buy", "bazaar")
        postcard_price = self.getPrice("POSTCARD", "buy", "custom", True)
        if postcard_price == 0:
            # If no price found, use the free will price
            final_postcard_cost = free_will_price
        else:
            final_postcard_cost = postcard_price
        if self.variables["free_will"]["var"].get() is True:
            tiered_free_will = {}
            for tier in tier_loop:
                free_wills_needed = 1 / (0.5 + 0.04 * (tier - 1))
                # for each failed Free Will we need another minion and we get a postcard
                # the last Free Will will not give a post card
                free_wills_failed = free_wills_needed - 1
                tiered_free_will[tier] = free_wills_failed * (tiered_coin_cost[tier] - final_postcard_cost) + free_wills_needed * free_will_price
            optimal = min(tiered_free_will, key=tiered_free_will.get)
            self.variables["optimal_tier_free_will"]["var"].set(optimal)
            self.variables["notes"]["list"]["Free Will"] = f"per minion, apply {1 / (0.5 + 0.04 * (optimal - 1)):.2} Free Wills on Tier {optimal}"
            self.variables["freewillcost"]["var"].set(tiered_free_will[optimal] * minion_amount)

        # Storage Chest cost
        if self.variables["chest"]["var"].get() != "None":
            chest_ID = md.getID[self.variables["chest"]["var"].get()]
            total_cost += self.getPrice(chest_ID, "buy", "bazaar")
        
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

        # Postcard cost
        if self.variables["postcard"]["var"].get():
            total_cost += final_postcard_cost

        # Potato Talisman cost
        if self.variables["potatoTalisman"]["var"].get():
            total_cost += self.getPrice("POTATO_TALISMAN", "buy", "custom", True)

        # Attribute costs
        if self.variables["toucan_attribute"]["var"].get() != 0:
            total_cost += md.attribute_shards["Epic"][self.variables["toucan_attribute"]["var"].get()] * self.getPrice("SHARD_TOUCAN", "buy", "bazaar")
        if self.variables["falcon_attribute"]["var"].get() != 0:
            total_cost += md.attribute_shards["Rare"][self.variables["falcon_attribute"]["var"].get()] * self.getPrice("SHARD_FALCON", "buy", "bazaar")


        # Sending results to self.variables
        self.variables["setupcost"]["var"].set(total_cost)
        self.variables["totalProfit"]["var"].set(self.variables["itemProfit"]["var"].get() + self.variables["petProfit"]["var"].get() - self.variables["fuelcost"]["var"].get())

        # multiply final lists by timeratio
        for loop_key in ["items", "itemtypeProfit", "xp"]:
            for item in self.variables[loop_key]["list"]:
                self.variables[loop_key]["list"][item] *= timeratio

        # Construct ID
        setup_ID = self.constructID(setup_template)
        self.variables["ID"]["var"].set(setup_ID)
        self.variables["ID_container"]["list"].clear()
        self.variables["ID_container"]["list"].append(setup_ID)

        # Get minion notes
        if "notes" in md.minionList[self.variables["minion"]["var"].get()]:
            self.variables["notes"]["list"].update(md.minionList[self.variables["minion"]["var"].get()]["notes"].copy())



        # Update listboxes
        if inGUI is True:
            if self.addons_auto_run["Rising Celsius Override"].get():
                self.addons_list["Rising Celsius Override"](self)
            for addon_name, auto_run_bool in self.addons_auto_run.items():
                if addon_name == "Rising Celsius Override":
                    continue
                if auto_run_bool.get():
                    self.addons_list[addon_name](self)
            self.update_GUI()
            self.statusC.configure(bg="green")
            self.statusC.update()
        return        

    def update_bazaar(self, cooldown_warning=True):
        """
        Checks if a bazaar_cooldown amount of seconds has passed,
        calls to Hypixel API for most recent bazaar data,
        handles that data to calculate accurate buy and sell prices.
        To get accurate prices, it takes a top percentage (top 10% default) of the orders and takes the average of them.

        Parameters
        ----------
        cooldown_warning : bool
            Toggle if a terminal message should be printed if the bazaar update cooldown has not passed yet.

        Returns
        -------
        None

        """
        if time.time() - self.bazaar_timer < bazaar_cooldown and self.bazaar_timer != 0:
            if cooldown_warning:
                print("BAZAAR: Bazaar is on cooldown")
            return
        print("BAZAAR: Calling Bazaar")
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
        print("BAZAAR: Bazaar call successful")
        self.bazaar_timer = raw_data["lastUpdated"] / 1000
        self.variables["bazaar_update_txt"]["var"].set(time.strftime("%Y-%m-%d %H:%M:%S UTC%z", time.localtime(self.bazaar_timer)))
        top_percent = 0.1
        print("BAZAAR: Processing data")
        for itemtype, item_data in md.itemList.items():
            if itemtype not in raw_data["products"]:
                continue
            for action in ["buy", "sell"]:
                top_amount = top_percent * sum([order["amount"] for order in raw_data["products"][itemtype][f"{action}_summary"]])
                if top_amount == 0:
                    item_data["prices"][f"{action}Price"] = 0
                    if "npc" not in item_data["prices"]:
                        print(f"BAZAAR: no {action} supply for {itemtype}")
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
                    print(f"BAZAAR: bottom heavy {action} supply for {itemtype}, taking top order price")
                else:
                    item_data["prices"][f"{action}Price"] = top_percent_avg_price
        print("BAZAAR: Processing complete")
        print("AH: Updating Postcard price")
        self.update_AH()
        return

    def update_AH(self):
        """
        Currently: Updates price of Postcard.
        In the future: Updates Auction House prices.

        AH data from https://sky.coflnet.com/data

        Returns
        -------
        None.

        """

        try:
            postcard_url = r"https://sky.coflnet.com/api/item/price/POSTCARD/bin"
            req = urllib.request.Request(postcard_url, headers={'User-Agent': f"Minion Calculator v{self.version.get()} (Python)", })
            f = urllib.request.urlopen(req)
            call_data = f.read().decode('utf-8')
        except Exception as error:
            print(f"ERROR: Could not finish API call to Coflnet\n{error}")
            return
        raw_data = json.loads(call_data)
        md.itemList["POSTCARD"]["prices"]["custom"] = (raw_data["lowest"] + raw_data["secondLowest"]) / 2
        return

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
