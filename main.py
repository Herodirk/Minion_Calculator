# -*- coding: utf-8 -*-
"""
@author: Herodirk

Main file for the minion calculator.
To start the calculator: run this file with a local python interpreter

Bazaar and NPC price data from https://api.hypixel.net
AH data from https://sky.coflnet.com/data
"""


#%% imports

try:
    import tkinter as tk
    import math
    import time
    import webbrowser
    import HSB_minion_data as md
    import Hero_UI_Manager as HPM
    import official_calculator_add_ons as Hero_addons
except ModuleNotFoundError as import_error:
    missing_package = import_error.name
    if missing_package in ["HSB_minion_data", "Hero_UI_Manager", "official_calculator_add_ons"]:
        print(f"ERROR - import - Could not find calculator file {missing_package}.py,\nplease make sure all the calculator files are in the same folder.")
    else:
        print(f"ERROR - import - Could not find {missing_package} module,\nplease install this module using PIP")
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
API_cooldown = 120  # seconds
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
        "sell_loc": "Hopper",
    },
    "Compact": {
        "sell_loc": "Best (NPC/Bazaar)",
        "upgrade1": "Super Compactor 3000",
    },
    "Compact Corrupt": {
        "sell_loc": "Best (NPC/Bazaar)",
        "hopper": "Enchanted Hopper",
        "upgrade1": "Super Compactor 3000",
        "upgrade2": "Corrupt Soil",
    },
    "Cheap speed": {
        "fuel": "Enchanted Lava Bucket",
        "upgrade2": "Diamond Spreading",
        "beacon": "None",
        "infusion": False,
        "free_will": False,
        "postcard": True
    },
    "No permanent speed": {
        "fuel": "Plasma Bucket",
        "upgrade2": "Flycatcher",
        "beacon": "Beacon V",
        "infusion": False,
        "free_will": False,
        "postcard": True
    },
    "Max speed": {
        "fuel": "Plasma Bucket",
        "upgrade2": "Flycatcher",
        "beacon": "Beacon V",
        "infusion": True,
        "free_will": True,
        "postcard": True
    },
    "Hyper speed": {
        "fuel": "Hyper Catalyst",
        "upgrade2": "Flycatcher",
        "beacon": "Beacon V",
        "infusion": True,
        "free_will": True,
        "postcard": True
    },
    "AFK with pet": {
        "afkpet_lvl": 100,
        "afk": True
    },
    "Solo Wisdom": {
        "mining_wisdom": 83.5,  # max Seasoned Mineman (15), cookie (25), god pot (20), Cavern Wisdom (6.5), Refined Divine drill with Compact X (7 + 10)
        "combat_wisdom": 109,  # max Slayer unique tier kills (6 + 6 + 6 + 12 + 6), Rift Necklace (1), Hunter Ring (5), Bubba Blister (2), Veteran (10), cookie (25), god pot (30)
        "farming_wisdom": 72.5,  # Fruit Bowl (1), Pelt Belt (1), Zorro's Cape (1), Rift Necklace (1), Agarimoo Artifact (1), Garden Wisdom (6.5) cookie (25), god pot (20), Blessed Mythic farming tool with Cultivating X (6 + 10)
        "fishing_wisdom": 55.5,  # Moby-Duck (1), Future Calories Talisman (1), Agarimoo Artifact (1), Chumming Talisman (1), Sea Wisdom (6.5), cookie (25), god pot (20)
        "foraging_wisdom": 93.82,  # Efficient Forager (15), Foraging Wisdom (6.5), David's Cloak (5), Foraging Wisdom Boosters armor and equipment (4 + 2), cookie (25), god pot (20), Moonglade Legendary Axe with Absorb X, Foraging Wisdom Boosters and essence shop perk Axed I ((5 + 10 + 1) * 1.02)
    },
    "Full Coop Wisdom": {  # cookie (25), god pot (20), 8 * (1 + 45 / 100) = 8 + (8 * 45) / 100 =  1 + (700 + 8 * 45) / 100 = 1 + 1060 / 100
        "mining_wisdom": 1060,  
        "combat_wisdom": 1060,
        "farming_wisdom": 1060,
        "fishing_wisdom": 1060,
        "foraging_wisdom": 1060,
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
        "amount": 32,
        "fuel": "Inferno Minion Fuel",
        "inferno_grade": "Hypergolic Gabagool",
        "inferno_distillate": "Gabagool Distillate",
        "inferno_eyedrops": False,
        "sell_loc": "Best (NPC/Bazaar)",
        "upgrade1": "Super Compactor 3000",
        "upgrade2": "Flycatcher",
        "chest": "XX-Large Storage",
        "beacon": "Beacon V",
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
# make sure that any pets you add have the ID spelt the same as in md.calculator_data
# The date of the price and possible notes is behind each pet.
pet_costs = {
    "NONE": {"min": 1, "max": 1},
    "PET_CUSTOM_PET": {"min": 0, "max": 20000000},
    "PET_GOLDEN_DRAGON": {"min": 610000000, "max": 800000000},  # 2025-8-31
    "PET_JADE_DRAGON": {"min": 580000000, "max": 720000000},  # 2025-8-31
    "PET_ROSE_DRAGON": {"min": 650000000, "max": 1150000000},  # 2026-1-31
    "PET_ROSE_DRAGON_EGG": {"min": 650000000, "max": 740000000},  # 2026-1-31
    "PET_BLACK_CAT": {"min": 40000000, "max": 62000000},  # 2025-8-31 (both buy and sell as legendary)
    "PET_ELEPHANT": {"min": 23000000, "max": 30000000},  # 2025-8-31
    "PET_MOOSHROOM_COW": {"min": 8000000, "max": 20000000},  # 2025-8-31
    "PET_SLUG": {"min": 5000000, "max": 32000000},  # 2025-8-31
    "PET_HEDGEHOG": {"min": 8000000, "max": 30000000},  # 2025-8-31
    "PET_ENDERMAN": {"min": 44000000, "max": 69000000},  # 2025-8-31 (buy as legendary lvl 1, sell as mythic lvl 100)
}

# and the custom prices in calculator data (see HSB_minion_data.py)


#%% Main Class

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        # Use Hero UI Manager to initialize the window and the frames with grids
        self.huim = HPM.H_UI_M(main=self, windowTitle="Minion Calculator", windowWidth=1450, windowHeight=750, palette=color_palette, debug_mode=debug_mode)
        self.huim.create_controls()
        self.huim.create_frames(self, frame_keys=[["inputs_minion", "inputs_player", "outputs_setup", "outputs_profit"]], grid_frames=True, grid_size=0.96, border=0.003)
        self.frames["addons_main"] = tk.Frame(self, background=self.colors["background"])
        self.huim.create_frames(self.frames["addons_main"], frame_keys=[["addons_buttons", "addons_output"]], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0)
        self.huim.logger.debug("Framework set up")
        self.version = self.huim.def_var(dtype=float, initial=1.2)
        self.huim.logger.info(f"Calculator version {self.version.get()}")

        # Define variables
        self.template = HPM.Hvar(self.huim, key="template", vtype="input", display="Templates", initial="Choose Template", dtype=str, frame="inputs_minion_grid", options=list(templateList.keys()), command=self.load_template)
        self.load_ID = HPM.Hvar(self.huim, key="load_id", vtype="input", dtype=str, frame="inputs_minion_grid", display="Load ID", initial="")
        self.minion = HPM.Hvar(self.huim, key="minion", vtype="input", dtype=str, display="Minion", frame="inputs_minion_grid", initial="Custom", options=md.minion_options, command=lambda x: self.multiswitch('minion', x))
        self.miniontier = HPM.Hvar(self.huim, key="miniontier", vtype="input", dtype=int, display="Tier", frame="inputs_minion_grid", initial=12, options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], command=lambda x: self.multiswitch('minion', x))
        self.amount = HPM.Hvar(self.huim, key="amount", vtype="input", dtype=int, display="Amount", frame="inputs_minion_grid", initial=1, options=None)
        self.fuel = HPM.Hvar(self.huim, key="fuel", vtype="input", dtype=str, display="Fuel", frame="inputs_minion_grid", initial="None", options=md.fuel_options, command=lambda x: self.multiswitch('fuel', x))
        self.inferno_grade = HPM.Hvar(self.huim, key="inferno_grade", vtype="input", dtype=str, display="Grade", frame="inputs_minion_grid", initial="Hypergolic Gabagool", options=md.inferno_fuel_grade_options)
        self.inferno_distillate = HPM.Hvar(self.huim, key="inferno_distillate", vtype="input", dtype=str, display="Distillate", frame="inputs_minion_grid", initial="Gabagool Distillate", options=md.inferno_fuel_distillate_options)
        self.inferno_eyedrops = HPM.Hvar(self.huim, key="inferno_eyedrops", vtype="input", dtype=bool, display="Eyedrops", frame="inputs_minion_grid", initial=False)
        self.hopper = HPM.Hvar(self.huim, key="hopper", vtype="input", dtype=str, display="Hopper", frame="inputs_minion_grid", initial="None", options=md.hopper_options)
        self.upgrade1 = HPM.Hvar(self.huim, key="upgrade1", vtype="input", dtype=str, display="Upgrade 1", frame="inputs_minion_grid", initial="None", options=md.upgrade_options)
        self.upgrade2 = HPM.Hvar(self.huim, key="upgrade2", vtype="input", dtype=str, display="Upgrade 2", frame="inputs_minion_grid", initial="None", options=md.upgrade_options)
        self.chest = HPM.Hvar(self.huim, key="chest", vtype="input", dtype=str, display="Chest", frame="inputs_minion_grid", initial="None", options=md.chest_options)
        self.beacon = HPM.Hvar(self.huim, key="beacon", vtype="input", dtype=str, display="Beacon", frame="inputs_minion_grid", initial="None", options=md.beacon_options, command=self.huim.create_switch_call("beacon", controlvar="self"))
        self.scorched = HPM.Hvar(self.huim, key="scorched", vtype="input", dtype=bool, display="Scorched", frame="inputs_minion_grid", initial=False)
        self.B_constant = HPM.Hvar(self.huim, key="B_constant", vtype="input", dtype=bool, display="Free Fuel Beacon", frame="inputs_minion_grid", initial=False)
        self.B_acquired = HPM.Hvar(self.huim, key="B_acquired", vtype="input", dtype=bool, display="Acquired Beacon", frame="inputs_minion_grid", initial=False)
        self.infusion = HPM.Hvar(self.huim, key="infusion", vtype="input", dtype=bool, display="Infusion", frame="inputs_minion_grid", initial=False)
        self.crystal = HPM.Hvar(self.huim, key="crystal", vtype="input", dtype=str, display="Crystal", frame="inputs_minion_grid", initial="None", options=md.floating_crystal_options)
        self.free_will = HPM.Hvar(self.huim, key="free_will", vtype="input", dtype=bool, display="Free Will", frame="inputs_minion_grid", initial=False, command=self.huim.create_switch_call("free_will", controlvar="free_will"))
        self.postcard = HPM.Hvar(self.huim, key="postcard", vtype="input", dtype=bool, display="Postcard", frame="inputs_minion_grid", initial=False)
        self.afk = HPM.Hvar(self.huim, key="afk", vtype="input", dtype=bool, display="AFK", frame="inputs_player_grid", initial=False, command=lambda: self.multiswitch("afk", None))
        self.afkpet = HPM.Hvar(self.huim, key="afkpet", vtype="input", dtype=str, display="AFK Pet", frame="inputs_player_grid", initial="None", options=md.boosting_pet_options)
        self.afkpet_rarity = HPM.Hvar(self.huim, key="afkpet_rarity", vtype="input", dtype=str, display="AFK Pet Rarity", frame="inputs_player_grid", initial="Legendary", options=['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Mythic'])
        self.afkpet_lvl = HPM.Hvar(self.huim, key="afkpet_lvl", vtype="input", dtype=float, display="AFK Pet level", frame="inputs_player_grid", initial=0.0)
        self.enchanted_clock = HPM.Hvar(self.huim, key="enchanted_clock", vtype="input", dtype=bool, display="Enchanted Clock", frame="inputs_player_grid", initial=False)
        self.special_layout = HPM.Hvar(self.huim, key="special_layout", vtype="input", dtype=bool, display="Special Layout", frame="inputs_player_grid", initial=False)
        self.player_harvests = HPM.Hvar(self.huim, key="player_harvests", vtype="input", dtype=bool, display="Player Harvests", frame="inputs_player_grid", initial=False)
        self.player_looting = HPM.Hvar(self.huim, key="player_looting", vtype="input", dtype=int, display="Looting", frame="inputs_player_grid", initial=0, options=[0, 1, 2, 3, 4, 5])
        self.potato_accessory = HPM.Hvar(self.huim, key="potato_accessory", vtype="input", dtype=str, display="Potato Accessory", frame="inputs_player_grid", initial="None", options=md.potato_accessory_options)
        self.combat_wisdom = HPM.Hvar(self.huim, key="combat_wisdom", vtype="storage", dtype=float, display="Combat", initial=0.0)
        self.mining_wisdom = HPM.Hvar(self.huim, key="mining_wisdom", vtype="storage", dtype=float, display="Mining", initial=0.0)
        self.farming_wisdom = HPM.Hvar(self.huim, key="farming_wisdom", vtype="storage", dtype=float, display="Farming", initial=0.0)
        self.fishing_wisdom = HPM.Hvar(self.huim, key="fishing_wisdom", vtype="storage", dtype=float, display="Fishing", initial=0.0)
        self.foraging_wisdom = HPM.Hvar(self.huim, key="foraging_wisdom", vtype="storage", dtype=float, display="Foraging", initial=0.0)
        self.alchemy_wisdom = HPM.Hvar(self.huim, key="alchemy_wisdom", vtype="storage", dtype=float, display="Alchemy", initial=0.0)
        self.wisdom = HPM.Hvar(self.huim, key="wisdom", vtype="output", dtype=dict, display="Wisdom", frame="inputs_player_grid", widget_width=None, widget_height=6, initial={'combat': self.combat_wisdom, 'mining': self.mining_wisdom, 'farming': self.farming_wisdom, 'fishing': self.fishing_wisdom, 'foraging': self.foraging_wisdom, 'alchemy': self.alchemy_wisdom})
        self.mayor = HPM.Hvar(self.huim, key="mayor", vtype="input", dtype=str, display="Mayor", frame="inputs_player_grid", initial="None", options=md.mayor_options, command=lambda x: self.multiswitch("mayors", x))
        self.levelingpet = HPM.Hvar(self.huim, key="levelingpet", vtype="input", dtype=str, display="Leveling pet", frame="inputs_player_grid", initial="None", options=md.pet_options, command=lambda x: self.multiswitch("pet_leveling", x))
        self.taming = HPM.Hvar(self.huim, key="taming", vtype="input", dtype=float, display="Taming", frame="inputs_player_grid", initial=0.0)
        self.falcon_attribute = HPM.Hvar(self.huim, key="falcon_attribute", vtype="input", dtype=int, display="Battle Experience", frame="inputs_player_grid", initial=0, options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.toucan_attribute = HPM.Hvar(self.huim, key="toucan_attribute", vtype="input", dtype=int, display="Why Not More", frame="inputs_player_grid", initial=0, options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.petxpboost = HPM.Hvar(self.huim, key="petxpboost", vtype="input", dtype=str, display="Pet XP boost", frame="inputs_player_grid", initial="None", options=md.pet_exp_boost_options)
        self.beastmaster = HPM.Hvar(self.huim, key="beastmaster", vtype="input", dtype=float, display="Beastmaster", frame="inputs_player_grid", initial=0.0)
        self.expsharepet = HPM.Hvar(self.huim, key="expsharepet", vtype="input", dtype=str, display="Exp Share pet", frame="inputs_player_grid", initial="None", options=md.pet_options)
        self.expsharepetslot2 = HPM.Hvar(self.huim, key="expsharepetslot2", vtype="input", dtype=str, display="Exp Share pet 2", frame="inputs_player_grid", initial="None", options=md.pet_options)
        self.expsharepetslot3 = HPM.Hvar(self.huim, key="expsharepetslot3", vtype="input", dtype=str, display="Exp Share pet 3", frame="inputs_player_grid", initial="None", options=md.pet_options)
        self.expshareitem = HPM.Hvar(self.huim, key="expshareitem", vtype="input", dtype=bool, display="Exp Share pet item", frame="inputs_player_grid", initial=False)
        self.scale_time = HPM.Hvar(self.huim, key="scale_time", vtype="input", dtype=bool, display="Scale Time", frame="inputs_player_grid", initial=False, command=self.huim.create_switch_call("scaled_time_switch", controlvar="scale_time"))
        self.sell_loc = HPM.Hvar(self.huim, key="sell_loc", vtype="input", dtype=str, display="Sell Location", frame="inputs_player_grid", initial="Best (NPC/Bazaar)", options=['Best (NPC/Bazaar)', 'Bazaar', 'Hopper', 'NPC'], command=self.huim.create_switch_call("NPC_Bazaar", controlvar="self"))
        self.bazaar_sell_type = HPM.Hvar(self.huim, key="bazaar_sell_type", vtype="input", dtype=str, display="Bazaar sell type", frame="inputs_player_grid", initial="Sell Offer", options=list(md.bazaar_sell_types.keys()))
        self.bazaar_buy_type = HPM.Hvar(self.huim, key="bazaar_buy_type", vtype="input", dtype=str, display="Bazaar buy type", frame="inputs_player_grid", initial="Buy Order", options=list(md.bazaar_buy_types.keys()))
        self.bazaar_taxes = HPM.Hvar(self.huim, key="bazaar_taxes", vtype="input", dtype=bool, display="Bazaar taxes", frame="inputs_player_grid", initial=True, command=self.huim.create_switch_call("bazaar_tax", controlvar="bazaar_taxes"))
        self.bazaar_flipper = HPM.Hvar(self.huim, key="bazaar_flipper", vtype="input", dtype=int, display="Bazaar Flipper", frame="inputs_player_grid", initial=1, options=[0, 1, 2])
        self.ID = HPM.Hvar(self.huim, key="ID", vtype="output", dtype=str, display="Setup ID", frame="outputs_setup_grid", initial="", switch_initial=True)
        self.ID_container = HPM.Hvar(self.huim, key="ID_container", vtype="output", dtype=list, display="ID", frame="outputs_setup_grid", widget_width=35, widget_height=1, initial=[], switch_initial=False)
        self.scaled_time = HPM.Hvar(self.huim, key="scaled_time", vtype="output", dtype=str, display="Scaled Time", frame="outputs_setup_grid", initial="1.0 Days", switch_initial=True)
        self.time_seconds = HPM.Hvar(self.huim, key="time_seconds", vtype="storage", dtype=float, display="Time (s)", initial=86400.0)
        self.empty_time = HPM.Hvar(self.huim, key="empty_time", vtype="output", dtype=str, display="Empty Time", fancy_display="Empty every", frame="outputs_setup_grid", initial="1.0 Days", switch_initial=True)
        self.actiontime = HPM.Hvar(self.huim, key="actiontime", vtype="output", dtype=float, display="Action time (s)", frame="outputs_setup_grid", initial=0.0, switch_initial=False)
        self.harvests = HPM.Hvar(self.huim, key="harvests", vtype="output", dtype=float, display="Harvests", frame="outputs_setup_grid", initial=0.0, switch_initial=False)
        self.items = HPM.Hvar(self.huim, key="items", vtype="output", dtype=dict, display="Item amounts", frame="outputs_setup_grid", widget_width=35, widget_height=None, initial={}, switch_initial=False, tags=["item_ID_to_display"])
        self.item_sell_loc = HPM.Hvar(self.huim, key="item_sell_loc", vtype="output", dtype=dict, display="Sell locations", frame="outputs_profit_grid", widget_width=35, widget_height=None, initial={}, switch_initial=False, tags=["item_ID_to_display"])
        self.filltime = HPM.Hvar(self.huim, key="filltime", vtype="output", dtype=float, display="Fill time", frame="outputs_setup_grid", initial=0.0, switch_initial=False)
        self.used_storage = HPM.Hvar(self.huim, key="used_storage", vtype="output", dtype=int, display="Used Storage", frame="outputs_setup_grid", initial=0, switch_initial=False)
        self.itemtype_profit = HPM.Hvar(self.huim, key="itemtype_profit", vtype="output", dtype=dict, display="Itemtype profits", fancy_display="Profits per item type", frame="outputs_profit_grid", widget_width=35, widget_height=None, initial={}, switch_initial=False, tags=["item_ID_to_display"])
        self.item_profit = HPM.Hvar(self.huim, key="item_profit", vtype="output", dtype=float, display="Total item profit", frame="outputs_profit_grid", initial=0.0, switch_initial=False)
        self.xp = HPM.Hvar(self.huim, key="xp", vtype="output", dtype=dict, display="XP amounts", frame="outputs_setup_grid", widget_width=35, widget_height=4, initial={}, switch_initial=False)
        self.pets_levelled = HPM.Hvar(self.huim, key="pets_levelled", vtype="output", dtype=dict, display="Pets Levelled", frame="outputs_setup_grid", widget_width=35, widget_height=4, initial={}, switch_initial=False)
        self.pet_profit = HPM.Hvar(self.huim, key="pet_profit", vtype="output", dtype=float, display="Pet profit", frame="outputs_profit_grid", initial=0.0, switch_initial=False)
        self.fuelcost = HPM.Hvar(self.huim, key="fuelcost", vtype="output", dtype=float, display="Fuel cost", frame="outputs_profit_grid", initial=0.0, switch_initial=False)
        self.fuelamount = HPM.Hvar(self.huim, key="fuelamount", vtype="output", dtype=float, display="Fuel amount", frame="outputs_setup_grid", initial=0.0, switch_initial=False)
        self.total_profit = HPM.Hvar(self.huim, key="total_profit", vtype="output", dtype=float, display="Total profit", frame="outputs_profit_grid", initial=0.0, switch_initial=True)
        self.notes = HPM.Hvar(self.huim, key="notes", vtype="output", dtype=dict, display="Notes", frame="outputs_setup_grid", widget_width=50, widget_height=4, initial={}, switch_initial=False)
        self.bazaar_update_txt = HPM.Hvar(self.huim, key="bazaar_update_txt", vtype="output", dtype=str, display="Bazaar data", frame="outputs_profit_grid", initial="Not Loaded", switch_initial=True)
        self.setupcost = HPM.Hvar(self.huim, key="setupcost", vtype="output", dtype=float, display="Setup cost", frame="outputs_profit_grid", initial=0.0, switch_initial=True)
        self.freewillcost = HPM.Hvar(self.huim, key="freewillcost", vtype="output", dtype=float, display="Free Will cost", fancy_display="+ Average Free Will cost", frame="outputs_profit_grid", initial=0.0, switch_initial=True)
        self.extracost = HPM.Hvar(self.huim, key="extracost", vtype="storage", dtype=str, display="Extra cost", fancy_display="+ Extra cost", initial="")
        self.optimal_tier_free_will = HPM.Hvar(self.huim, key="optimal_tier_free_will", vtype="storage", dtype=int, display="Optimal Tier Free Will", initial=1)
        self.available_storage = HPM.Hvar(self.huim, key="available_storage", vtype="storage", dtype=int, display="Available Storage", initial=0)
        self.addons_output_container = HPM.Hvar(self.huim, key="addons_output_container", vtype="output", dtype=dict, display="Add-on Outputs", frame="addons_output_grid", widget_width=65, widget_height=20, initial={}, switch_initial=False)
        self.empty_time_amount = HPM.Hvar(self.huim, key="empty_time_amount", vtype="input", dtype=float, display="Empty Time span", initial=1.0, frame="inputs_player_grid")
        self.empty_time_unit = HPM.Hvar(self.huim, key="empty_time_unit", vtype="input", dtype=str, display="Empty Time unit", initial="Days", frame="inputs_player_grid", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.scaled_time_amount = HPM.Hvar(self.huim, key="scaled_time_amount", vtype="input", dtype=float, display="Scaled Time span", initial=1.0, frame="inputs_player_grid")
        self.scaled_time_unit = HPM.Hvar(self.huim, key="scaled_time_unit", vtype="input", dtype=str, display="Scaled Time unit", initial="Days", frame="inputs_player_grid", options=["Years", "Weeks", "Days", "Hours", "Minutes", "Seconds", "Harvests"])
        self.rising_celsius_override = HPM.Hvar(self.huim, key="rising_celsius_override", vtype="input", dtype=bool, display="Force Rising Celsius", initial=False, frame="inputs_minion_grid")
        self.used_pet_prices = HPM.Hvar(self.huim, key="used_pet_prices", vtype="output", dtype=dict, display="Used Pet Prices", initial={}, frame="outputs_profit_grid", widget_width=35, widget_height=4, switch_initial=True, tags=["item_ID_to_display"])

        self.empty_time_unit.widget[-1].place(in_=self.empty_time_amount.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.scaled_time_unit.widget[-1].place(in_=self.scaled_time_amount.widget[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.wisdom.update_listbox(value_format_function=lambda var: var.get(), filter=lambda key, val: val.get() != 0.0)
        self.wisdomB = tk.Button(self.frames["inputs_player_grid"], text='Edit', command=lambda: self.huim.edit_vars(lambda: self.wisdom.update_listbox(value_format_function=lambda var: var.get(), filter=lambda key, val: val.get() != 0.0), ["combat_wisdom", "mining_wisdom", "farming_wisdom", "fishing_wisdom", "foraging_wisdom", "alchemy_wisdom"]))
        self.wisdomB.place(in_=self.wisdom.widget[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.notesAnchor = self.huim.create_label(frm=self.frames["outputs_setup_grid"], txt="")

        self.huim.logger.debug("Variables initialized")

        # Create widgets for controls menu and placing them
        self.creditLB = self.huim.create_label(frm=self.frames["controls"], txt=f"Minion Calculator V{self.version.get()}\nMade by Herodirk")
        self.creditLB.place(in_=self.stopB, x=-10, rely=0.5, y=-1, anchor="e")
        self.manualLB = self.huim.create_label(frm=self.frames["controls"], txt="Online Manual:\nCalculator Manual")
        self.manualLB.place(in_=self.creditLB, x=-10, rely=0.5, anchor="e")
        self.manualLB.bind("<Button-1>", lambda void_event: webbrowser.open(r"https://herodirk.github.io/"))
        self.API_creditLB = self.huim.create_label(frm=self.frames["controls"], txt="Bazaar data from Hypixel API,\nAH data from SkyCofl API")
        self.API_creditLB.place(in_=self.manualLB, x=-10, rely=0.5, anchor="e")
        self.API_creditLB.bind("<Button-1>", lambda click_event: webbrowser.open(r"https://api.hypixel.net/") if click_event.y < 18 else webbrowser.open(r"https://sky.coflnet.com/data"))

        self.outputB = tk.Button(self.frames["controls"], text='Short Output', command=self.output_data)
        self.fancyoutputB = tk.Button(self.frames["controls"], text='Share Output', command=self.fancy_output)
        self.calcB = tk.Button(self.frames["controls"], text='Calculate', command=lambda: self.calculate(True))
        self.statusC = tk.Canvas(self.frames["controls"], bg="green", width=10, height=10, borderwidth=0)
        self.addonsB = tk.Button(self.frames["controls"], text="Add-ons Menu", command=lambda: self.huim.toggle_switch("addons"))
        self.pricesB = tk.Button(self.frames["controls"], text="Update Prices", command=self.update_prices)
        # self.status, self.statusO = self.huim.def_output_var(frame=self.frames["controls"], dtype=str, L_text="Status:", initial="Ready")  # might use later

        controlsGrid = [self.calcB, self.statusC, self.outputB, self.fancyoutputB, self.pricesB, self.addonsB]
        self.huim.fill_arr(controlsGrid, self.frames["controls"])

        # Create miscellaneous labels
        miniontitleLB = self.huim.create_label(frm=self.frames["inputs_minion_grid"], txt="\nMinion options")
        islandtitleLB = self.huim.create_label(frm=self.frames["inputs_minion_grid"], txt="\nIsland options")
        playertitleLB = self.huim.create_label(frm=self.frames["inputs_player_grid"], txt="Player options")
        timingtitleLB = self.huim.create_label(frm=self.frames["inputs_player_grid"], txt="\nTime options")
        markettitleLB = self.huim.create_label(frm=self.frames["inputs_player_grid"], txt="\nMarket options")
        setupoutputsLB = self.huim.create_label(frm=self.frames["outputs_setup_grid"], txt="Setup Information")
        setupprintLB = self.huim.create_label(frm=self.frames["outputs_setup_grid"], txt="Share")
        minionoutputsLB = self.huim.create_label(frm=self.frames["outputs_setup_grid"], txt="Minion Outputs")
        minionprintLB = self.huim.create_label(frm=self.frames["outputs_setup_grid"], txt="Share")
        profitoutputsLB = self.huim.create_label(frm=self.frames["outputs_profit_grid"], txt="Profit Outputs")
        profitprintLB = self.huim.create_label(frm=self.frames["outputs_profit_grid"], txt="Share")
        addonsprintLB = self.huim.create_label(frm=self.frames["addons_output_grid"], txt="Share")
        addonsoutputsLB = self.huim.create_label(frm=self.frames["addons_output_grid"], txt="Add-on Outputs")

        # Defining the order of widgets and placing them for all the grids
        self.grids = {
            "inputs_minion_grid": {
                "template": None,
                "load_id": None,
                "minion_label": [None, miniontitleLB],
                "minion": None,
                "miniontier": None,
                "amount": None,
                "fuel": None,
                "inferno_grade": None,
                "inferno_distillate": None,
                "inferno_eyedrops": None,
                "rising_celsius_override": None,
                "hopper": None,
                "upgrade1": None,
                "upgrade2": None,
                "chest": None,
                "infusion": None,
                "free_will": None,
                "island_label": [None, islandtitleLB],
                "beacon": None,
                "scorched": None,
                "B_constant": None,
                "B_acquired": None,
                "crystal": None,
                "postcard": None,
            },
            "inputs_player_grid": {
                "player_label": [None, playertitleLB],
                "afk": None,
                "afkpet": None,
                "afkpet_rarity": None,
                "afkpet_lvl": None,
                "enchanted_clock": None,
                "special_layout": None,
                "player_harvests": None,
                "player_looting": None,
                "potato_accessory": None,
                "wisdom": None,
                "mayor": None,
                "levelingpet": None,
                "toggle_levelingpet_options": [None, self.huim.create_show_hide_toggle("levelingpet", lambda: self.multiswitch("pet_leveling", None), None)],
                "taming": None,
                "falcon_attribute": None,
                "petxpboost": None,
                "beastmaster": None,
                "expsharepet": None,
                "expsharepetslot2": None,
                "expsharepetslot3": None,
                "toucan_attribute": None,
                "expshareitem": None,
                "timing_label": [None, timingtitleLB],
                "empty_time_amount": None,
                "scale_time": None,
                "scaled_time_amount": None,
                "market_label": [None, markettitleLB],
                "sell_loc": None,
                "bazaar_sell_type": None,
                "bazaar_buy_type": None,
                "bazaar_taxes": None,
                "bazaar_flipper": None
            },
            "outputs_setup_grid": {
                "labels": [None, setupoutputsLB, setupprintLB],
                "ID": [self.ID.widget[0], self.ID_container.widget[1], self.ID.widget[2]],
                "empty_time": None,
                "scaled_time": None,
                "actiontime": None,
                "fuelamount": None,
                "notes": [self.notes.widget[0], None, self.notes.widget[2]],
                "notes_anchor": [self.notesAnchor],
                "notes_space_1": [None],
                "notes_space_2": [None],
                "notes_space_3": [None],
                "minions_labels": [None, minionoutputsLB, minionprintLB],
                "harvests": None,
                "items": None,
                "used_storage": None,
                "xp": None,
                "pets_levelled": None,
            },
            "outputs_profit_grid": {
                "labels": [None, profitoutputsLB, profitprintLB],
                "bazaar_update_txt": None,
                "setupcost": None,
                "freewillcost": None,
                "item_sell_loc": None,
                "itemtype_profit": None,
                "item_profit": None,
                "used_pet_prices": None,
                "pet_profit": None,
                "fuelcost": None,
                "total_profit": None
            },
            "addons_output_grid": {
                "labels": [None, addonsoutputsLB, addonsprintLB],
                "addons_output_container": [None, self.addons_output_container.widget[1], self.addons_output_container.widget[2]]
            },
        }
        for grid_key in self.grids.keys():
            self.huim.fill_grid(self.huim.create_grid(self.grids[grid_key]), self.frames[grid_key])

        self.notes.widget[1].place(in_=self.notesAnchor, relx=1, x=5, rely=0, anchor='nw')
        self.notes.widget[1].tkraise()

        # Add-ons buttons
        self.addons_list = {**external_add_ons}
        self.addons_buttons = {}
        self.addons_auto_run = {}
        for number, addon_info in enumerate(self.addons_list.items()):
            addon_name, addon_function = addon_info
            button_function = lambda func=addon_function: func(self)
            self.addons_buttons[addon_name] = tk.Button(self.frames["addons_buttons_grid"], text=addon_name, command=button_function)
            self.addons_auto_run[addon_name], widget = self.huim.def_input_var(dtype=bool, frame=self.frames["addons_buttons_grid"], L_text="", initial=False)
            widget[-1].place(in_=self.addons_buttons[addon_name], anchor="w", relx=1, rely=0.5, x=10)
            self.addons_buttons[addon_name].grid(row=number % 8, column=(int(number / 8)) * 2)

        self.huim.logger.debug("Widgets placed")

        # Create switches with Hero UI Manager for the extended minion options
        self.huim.def_switch("pet_leveling", widget_references=["taming", "petxpboost", "beastmaster", "expsharepet", "expshareitem", "pets_levelled", "pet_profit", "falcon_attribute", "toucan_attribute", "used_pet_prices"],
                            locations="grid", control="None", negate=True, initial=False)
        self.huim.def_switch("exp_share_diana", widget_references=["expsharepetslot2", "expsharepetslot3"],
                            locations="grid", control="DianaTrue", negate=False, initial=False)
        self.huim.def_switch("NPC_Bazaar", widget_references="item_sell_loc",
                            locations="grid", control="Best (NPC/Bazaar)", negate=False, initial=True)
        self.huim.def_switch("infernofuel", widget_references=["inferno_grade", "inferno_distillate", "inferno_eyedrops"],
                            locations="grid", control="Inferno Minion Fuel", negate=False, initial=False)
        self.huim.def_switch("rising_celsius", widget_references="rising_celsius_override",
                            locations="grid", control="Inferno", negate=False, initial=False)
        self.huim.def_switch("beacon", widget_references=["scorched", "B_constant", "B_acquired"],
                            locations="grid", control="None", negate=True, initial=False)
        self.huim.def_switch("potato_accessory_switch", widget_references="potato_accessory",
                            locations="grid", control="PotatoTrue", negate=False, initial=False)
        self.huim.def_switch("bazaar_tax", widget_references="bazaar_flipper",
                            locations="grid", control=1, negate=False, initial=True)
        self.huim.def_switch("afking", widget_references=["afkpet", "afkpet_rarity", "afkpet_lvl", "enchanted_clock", "special_layout", "player_harvests", "player_looting"],
                            locations="grid", control=True, negate=False, initial=False)
        self.huim.def_switch("fuel_amount", widget_references="fuelamount",
                            locations="grid", control=-1, negate=True, initial=False)
        self.huim.def_switch("scaled_time_switch", widget_references=["scaled_time_amount", "scaled_time"],
                            locations="grid", control=True, negate=False, initial=False)
        self.huim.def_switch("free_will", widget_references="freewillcost",
                            locations="grid", control=True, negate=False, initial=False)
        self.huim.def_switch(ID="addons", widget_references=self.frames["addons_main"],
                            locations={"anchor": "c", "relx": 0.5, "rely": 0.5, "relwidth": 0.7, "relheight": 0.8}, initial=False)
        
        # Show/Hide toggle buttons for large amount of extended options
        self.huim.create_show_hide_toggle("afk", "afking")
        self.huim.create_show_hide_toggle("beacon", "beacon")
        
        self.huim.logger.debug("Switches activated")

        self.dependent_variables = {"afkpet_rarity": "afkpet", "afkpet_lvl": "afkpet", "player_harvests": "afk", "empty_time": "scale_time", "freewillcost": "free_will", "expshareitem": "expsharepet", "used_pet_prices": "levelingpet", "pet_profit": "levelingpet"}
        # dependent variables are only active when another specified variable is not equivalent to 0,
        # this overrides forced outputs as inactive variables might not be equivalent to 0
        self.key_replace_bool = ["infusion", "free_will", "postcard"]  # variables that are booleans that need their display name outputted instead of the boolean value

        # Define output orders for Short Output (self.outputOrder) and Share Output (self.fancyOrder)
        self.outputOrder = ['fuel', "inferno_grade", "inferno_distillate", "inferno_eyedrops", "rising_celsius_override",
                            'hopper', 'upgrade1', 'upgrade2', 'chest',
                            'beacon', 'scorched', 'B_constant', 'B_acquired',
                            'crystal', 'postcard', 'infusion', 'free_will', 'afk', 'afkpet', 'afkpet_rarity', 'afkpet_lvl', 'enchanted_clock', 'special_layout', 'potato_accessory', 'player_harvests', "player_looting",
                            'wisdom', 'mayor', 'levelingpet', 'taming', 'falcon_attribute', 'petxpboost', 'beastmaster', 'toucan_attribute', 'expshareitem', 'expsharepet', 'expsharepetslot2', 'expsharepetslot3',
                            'ID', 'setupcost', 'freewillcost', 'extracost', 'actiontime', 'fuelamount', 'sell_loc', 'bazaar_update_txt', 'bazaar_taxes', 'bazaar_flipper', 'notes',
                            'empty_time', 'scaled_time', 'harvests', 'used_storage', 'items', 'item_sell_loc',
                            'item_profit', 'itemtype_profit', 'xp', 'pet_profit', 'pets_levelled', 'used_pet_prices',
                            'fuelcost', 'total_profit', 'addons_output_container']

        # The Share Output order is stored per line.
        # First dimension of dict exists of keys which are placed first on a line
        # These keys can serve as headers, or if the key is a variable key, the variable is outputted as {"display"}: {"value"}
        # the values are the second dimension of dict, the keys of which are sub-headers used for formatting, like adding line breaks
        # the values of the second dimension are array-like objects consisting of variable keys,
        # the variables are displayed differently depending on which array type it is:
        # set {}: only the values of the variables will be outputted (without any order)
        # list []: both the displays and the values of the variables will be outputted
        # tuple (): both displays and values are shown, the sub-header will be outputted in front of every variable
        self.fancyOrder = {
            "**Minion Upgrades**": {
                "\n> Internal: ": {"fuel", "hopper", "upgrade1", "upgrade2"},
                "\n> External: ": {"chest", "beacon", "crystal", "postcard"},
                "\n> Permanent: ": {"infusion", "free_will"}
            },
            "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
            "Inferno Info": {"\n> ": ["inferno_grade", "inferno_distillate", "inferno_eyedrops", "rising_celsius_override"]},
            "afk": {"\n> ": ["afkpet", "afkpet_rarity", "afkpet_lvl", "enchanted_clock", "special_layout", "potato_accessory"]},
            "player_harvests": {"\n> ": ["player_looting"]},
            "wisdom": None,
            "mayor": None,
            "levelingpet": {
                "\n> ": ["taming", "falcon_attribute", "petxpboost", "beastmaster", "toucan_attribute", "expshareitem"],
                "\n> Exp Share Pets: ": {"expsharepet", "expsharepetslot2", "expsharepetslot3"}
            },
            "used_pet_prices": None,
            "**Setup Information**": {"\n> ": ("ID", "setupcost", "freewillcost", "extracost", "actiontime", "fuelamount")},
            "Bazaar Info": {"\n> ": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper"]},
            "notes": None,
            "empty_time": None,
            "**Outputs** for ": {"": {"scaled_time"}},
            "harvests": None,
            "used_storage": None,
            "items": None,
            "item_sell_loc": None,
            "item_profit": None,
            "itemtype_profit": None,
            "xp": None,
            "pet_profit": None,
            "pets_levelled": None,
            "fuelcost": None,
            "total_profit": None,
            "addons_output_container": None
        }

        self.ID_order = [
            "minion", "miniontier", "amount", "fuel",
            "hopper", "upgrade1", "upgrade2", "chest", "beacon", "scorched", "B_constant", "B_acquired",
            "infusion", "crystal", "free_will", "postcard",
            "inferno_grade", "inferno_distillate", "inferno_eyedrops", "rising_celsius_override",
            "afk", "afkpet", "afkpet_rarity", "afkpet_lvl", "enchanted_clock", "special_layout",
            "player_harvests", "player_looting", "potato_accessory",
            "combat_wisdom", "mining_wisdom", "farming_wisdom", "fishing_wisdom", "foraging_wisdom", "alchemy_wisdom",
            "mayor",
            "levelingpet", "taming", "falcon_attribute", "toucan_attribute", "petxpboost", "beastmaster",
            "expsharepet", "expsharepetslot2", "expsharepetslot3", "expshareitem",
            "sell_loc", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper",
            "empty_time_amount", "empty_time_unit", "scale_time", "scaled_time_amount", "scaled_time_unit",
        ]
        self.huim.logger.debug("Output orders defined")

        # Load prices
        self.API_timer = 0
        self.bazaar_items = []
        self.AH_items = []
        self.recipe_items = []
        self.init_prices()
        self.huim.logger.debug("Updated NPC prices")
        self.update_prices(cooldown_warning=False, in_gui=True)
        self.huim.logger.info("Ready")
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
            if type(control) == str or self.miniontier.get() not in md.calculator_data[self.minion.get()]["speed"].keys():
                self.miniontier.set(list(md.calculator_data[self.minion.get()]["speed"].keys())[-1])
            if type(control) == str:
                self.huim.toggle_switch("potato_accessory_switch", control + str(self.afk.get()))
                self.huim.toggle_switch("rising_celsius", control)
        elif multi_ID == "fuel":
            self.huim.toggle_switch("infernofuel", control)
            self.huim.toggle_switch("fuel_amount", md.calculator_data[md.fuel_options[control]]["fuel_duration"])
        elif multi_ID == "afk":
            afkState = self.afk.get()
            self.huim.toggle_switch("afking", afkState)
            self.huim.toggle_switch("potato_accessory_switch", self.minion.get(False) + str(afkState))
        elif multi_ID == "pet_leveling":
            self.huim.toggle_switch("pet_leveling", control)
            mayor = self.mayor.get(False)
            pet_leveling_state = self.switches["pet_leveling"]["state"]
            self.huim.toggle_switch("exp_share_diana", mayor + str(pet_leveling_state))
        elif multi_ID == "mayors":
            pet_leveling_state = self.switches["pet_leveling"]["state"]
            self.huim.toggle_switch("exp_share_diana", control + str(pet_leveling_state))
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
            template = self.decode_id(self.load_ID.get())
        elif template_name == "Clean":
            template = {var_key: self.var_dict[var_key].initial for var_key in self.ID_order if var_key not in ["minion", "miniontier"]}
        else:
            template = templateList[template_name]
        for setting, variable in template.items():
            self.var_dict[setting].set(variable)
            if self.var_dict[setting].command is not None:
                if type(variable) == bool:
                    self.var_dict[setting].command()
                else:
                    self.var_dict[setting].command(variable)
            if "_wisdom" in setting:
                self.wisdom.update_listbox(value_format_function=lambda var: var.get(), filter=lambda key, val: val.get() != 0.0)
        return

    def output_data(self, toTerminal=True):
        """
        Generates a short output string with all relavent inputs and chosen ouputs.
        The order of these inputs and output in the output string is defined in self.outputOrder in __init__().
        If toTerminal is True it also logs the string to terminal.

        Parameters
        ----------
        toTerminal : bool, optional
            Toggle for logging to terminal. The default is True.

        Returns
        -------
        crafted_string : str
            Output string. If toTerminal is True, this function returns None.

        """
        crafted_string = f'{self.amount.get()}x {self.minion.get(False)} t{self.miniontier.get()}; '
        string_parts = {}
        for var_key in self.outputOrder:
            if var_key in self.dependent_variables:
                if self.var_dict[self.dependent_variables[var_key]].get(False) in ["None", "0", "0.0", "", False]:
                    continue
            elif var_key in ["expsharepetslot2", "expsharepetslot3"]:
                if self.mayor.get(False) != "Diana":
                    continue
            elif var_key in ["inferno_grade", "inferno_distillate", "inferno_eyedrops"]:
                if self.fuel.get(False) != "Inferno Minion Fuel":
                    continue
            elif var_key in ["rising_celsius_override"]:
                if self.minion.get(False) != "Inferno":
                    continue
            if var_key == "scaled_time" and self.scale_time.get() is False and self.empty_time.get_output_switch() is False:
                continue
            elif self.var_dict[var_key].get_output_switch() is False:
                if (var_key == "notes" and self.special_layout.get() is True and "Special Layout" in self.notes.list):
                    string_parts["notes"] = "Notes: Special Layout: " + self.notes.list['Special Layout']
                else:
                    continue
            if var_key == "wisdom":
                wisdoms = {list_key: var.get() for list_key, var in self.wisdom.list.items() if (var.get() not in ["None", 0, 0.0] and list_key in self.xp.list)}
                if len(wisdoms) != 0:
                    string_parts["widsom"] = self.wisdom.get_display() + ": " + ", ".join(f"{wisdom_type}: {wisdom_val}" for wisdom_type, wisdom_val in wisdoms.items())
                continue
            if var_key == "bazaar_update_txt":
                string_parts["bazaar_update_txt"] = f'Bazaar info: {self.bazaar_sell_type.get()}, {self.bazaar_buy_type.get()}, Last updated at {self.bazaar_update_txt.get()}'
                continue
            if var_key == "extracost":
                if self.setupcost.get_output_switch() is False:
                    continue

            vtype = self.var_dict[var_key].vtype
            display = self.var_dict[var_key].get_display()
            dtype = self.var_dict[var_key].dtype
            if dtype in [list, dict]:
                if len(self.var_dict[var_key].list) == 0:
                    continue
                formatting_function = lambda x: x
                if self.var_dict[var_key].has_tag("item_ID_to_display"):
                    formatting_function = lambda x: md.calculator_data[x]['display']
                elif var_key == "pets_levelled":
                    formatting_function = lambda x: self.var_dict[x].get(False)
                formatted_list = []
                for list_key, list_val in self.var_dict[var_key].list.items():
                    if type(list_val) in [float, int]:
                        formatted_list.append(f"{formatting_function(list_key)}: {self.huim.reduced_number(list_val)}")
                    else:
                        formatted_list.append(f"{formatting_function(list_key)}: {list_val}")
                string_parts[var_key] = display + ": " + ", ".join(formatted_list)
                continue

            val = self.var_dict[var_key].get(False)
            if vtype == "input":
                if val in ["None", 0, 0.0, False, ""]:
                    continue
                if dtype in [int, float, bool]:
                    string_parts[var_key] = f"{display}: {val}"
                else:
                    string_parts[var_key] = f"{val}"
            else:
                if dtype in [int, float]:
                    string_parts[var_key] = f"{display}: {self.huim.reduced_number(val)}"
                else:
                    string_parts[var_key] = f"{display}: {val}"

        crafted_string += "; ".join(string_parts.values())
        if output_to_clipboard:
            self.clipboard_clear()
            self.clipboard_append(crafted_string)
        if toTerminal is True:
            self.huim.logger.info("\n" + crafted_string)
            return
        else:
            return crafted_string

    def prep_fancy_data(self, var_key, display=True, newline=False):
        """
        Subfunction for fancyOutput().
        This function generate the part of the Share Output for the inputted variable key
        with toggles if the self.variable "display" should be shown and if a new line should be put at the end.
        Returns None if the self.variable has "output_switch" set to False.
        Returns None if the value of the self.variable is equivalent to 0, except if "output_switch" is True.

        Parameters
        ----------
        var_key : str
            A variable key.
        display : bool, optional
            Toggle for if the self.variable "display" should be shown. The default is True.
        newline : bool, optional
            Toggle for if a new line should be put at the end. The default is False.

        Returns
        -------
        str
            The part of the Share Output for the inputted variable key.

        """
        # Special cases that can stop variables from outputting
        if var_key in self.dependent_variables:  # special case: dependent variables
            if self.var_dict[self.dependent_variables[var_key]].get(False) in ["None", "0", "0.0", "", False]:
                return None
        elif var_key in ["expsharepetslot2", "expsharepetslot3"]:  # special case: slots only active during Diana
            if self.mayor.get(False) != "Diana":
                return None
        elif var_key in ["inferno_grade", "inferno_distillate", "inferno_eyedrops"]:  # special case: fuel attributes only relevant for Inferno Minion Fuel
            if self.fuel.get(False) != "Inferno Minion Fuel":
                return None
        elif var_key in ["rising_celsius_override"]:  # special case: Rising Celsius only applies to Inferno minions
            if self.minion.get(False) != "Inferno":
                return None
        elif var_key == "extracost":  # special case: setup cost is turned off
            if self.setupcost.get_output_switch() is False:
                return None
        elif var_key == "scaled_time" and self.scale_time.get() is False and self.empty_time.get_output_switch() is False:  # special case: scale time is off and empty time is off
            return None

        # Output switch
        force = False  # force is a toggle for output variables that can be equivalent to 0 but still have to be outputted due to output switch
        output_switch_val = self.var_dict[var_key].get_output_switch()
        if output_switch_val is False:
            # special cases: output switch set to false, but forced output anyway
            if var_key == "notes" and self.special_layout.get() is True and "Special Layout" in self.notes.list:
                return f"Notes:\n> Special Layout: `{self.notes.list['Special Layout']}`"
            else:
                return None
        elif output_switch_val is True:
            force = True

        # Special cases that can override the formatting
        if var_key == "wisdom":  # special case: wisdom being separate variables
            wisdoms = {list_key: var.get() for list_key, var in self.wisdom.list.items() if (var.get() not in ["None", 0, 0.0] and list_key in self.xp.list)}
            if len(wisdoms) != 0:
                return self.wisdom.get_display(True) + ":\n> " + ", ".join(f"{wisdom_type}: `{wisdom_val}`" for wisdom_type, wisdom_val in wisdoms.items())
            return None
        elif var_key == "used_storage":  # special case: add available storage to output
            val = f"`{self.var_dict[var_key].get()}` (out of `{self.available_storage.get()}`)"
        elif var_key in self.key_replace_bool:  # special case: output key instead of the boolean
            if self.var_dict[var_key].get() is True:
                val = f"`{self.var_dict[var_key].get_display(True)}`"
            else:
                return None
        elif var_key == "ID":  # special case: spoiler lines around setup ID
            val = f"||{self.var_dict[var_key].get()}||".replace("\\", r"\\")
        elif self.var_dict[var_key].dtype in [dict, list]:
            if len(self.var_dict[var_key].list) == 0:
                return None
            formatting_function = lambda x: x
            if self.var_dict[var_key].has_tag("item_ID_to_display"):
                formatting_function = lambda x: md.calculator_data[x]['display']
            elif var_key == "pets_levelled":
                formatting_function = lambda x: self.var_dict[x].get(False)
            formatted_list = []
            for list_key, list_val in self.var_dict[var_key].list.items():
                if type(list_val) in [float, int]:
                    formatted_list.append(f"{formatting_function(list_key)}: `{self.huim.reduced_number(list_val)}`")
                else:
                    formatted_list.append(f"{formatting_function(list_key)}: `{list_val}`")
            val = "\n> " + ", ".join(formatted_list)
        elif self.var_dict[var_key].dtype in [int, float]:
            val = f"`{self.huim.reduced_number(self.var_dict[var_key].get())}`"
        else:
            val = f"`{self.var_dict[var_key].get(False)}`"
        if val in ["`None`", "`0`", "`0.0`", "", "``", "`False`"] and force is False:
            return None
        if var_key == "freewillcost":
            val += f" (optimal: apply on t{self.optimal_tier_free_will.get()})"
        return_str = ""
        if display:
            return_str += f"{self.var_dict[var_key].get_display(True)}: "
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
            Toggle for logging to terminal. The default is True.

        Returns
        -------
        crafted_string : str
            Output string. If toTerminal is True, this function returns None.

        """
        crafted_string = f'{self.amount.get()}x **{self.minion.get(False)} t{self.miniontier.get()}**'
        for key in self.fancyOrder:
            line_str = ""
            header = ""
            force_line = False
            if key in self.var_dict:
                header = self.prep_fancy_data(key)
                force_line = True
            else:
                header = key
            if header is None:
                continue
            if header == "Beacon Info" and self.beacon.get() == 0:
                continue
            if header == "Inferno Info" and self.minion.get(False) != "Inferno" and self.fuel.get(False) != "Inferno Minion Fuel":
                continue
            if header == "Bazaar Info" and self.bazaar_update_txt.get_output_switch() is False:
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
            self.huim.logger.info("\n" + crafted_string)
            return
        else:
            return crafted_string

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
        for var_key in self.ID_order:
            if var_key not in setup_data:
                self.huim.logger.warning(f"{var_key} key not in setup_data, assuming default value")
                val = self.var_dict[var_key].initial
            elif self.var_dict[var_key].translation is not None:
                val = md.calculator_data[setup_data[var_key]]["display"]
            else:
                val = setup_data[var_key]
            var_options = self.var_dict[var_key].options
            if var_options is None:
                if int(val) == val:
                    val = int(val)
                setup_id += "!" + str(val) + "!"
            elif len(var_options) > 79:
                index = var_options.index(val)
                setup_id += "!" + str(index) + "!"
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
            self.huim.logger.error("Invalid ID, could not find version number")
            return setup_data
        try:
            version = float(ID[0:end_ver])
        except Exception:
            self.huim.logger.error("Invalid ID, could not find version number")
            return setup_data
        ID_index = end_ver + 1
        if version != self.version.get():
            self.huim.logger.error("Invalid ID, Incompatible version")
            return setup_data
        try:
            for var_key in self.ID_order:
                var_options = self.var_dict[var_key].options
                if var_options is None:
                    if ID[ID_index] != "!":
                        self.huim.logger.error(f"did not find {var_key}")
                        return {}
                    end_val = ID.find("!", ID_index + 1)
                    setup_data[var_key] = self.var_dict[var_key].dtype(ID[ID_index + 1:end_val])
                    ID_index = end_val + 1
                elif len(var_options) > 79:
                    if ID[ID_index] != "!":
                        self.huim.logger.error(f"did not find {var_key}")
                        return {}
                    end_val = ID.find("!", ID_index + 1)
                    setup_data[var_key] = var_options[int(ID[ID_index + 1:end_val])]
                    ID_index = end_val + 1
                else:
                    setup_data[var_key] = var_options[ord(ID[ID_index]) - 48]
                    ID_index += 1
        except IndexError as error:
            self.huim.logger.error("Invalid ID, ID incomplete")
            return {}
        return setup_data

    def get_price(self, ID, setup_data, action="buy", location="bazaar", force=False):
        """
        Returns the price of an item from ID, transaction type and location of transaction.

        Parameters
        ----------
        ID : str
            Skyblock Item ID of which the price is needed.
        setup_data : dict
            needed setup data: bazaar_buy_type, bazaar_sell_type, bazaar_taxes, bazaar_flipper, mayor.
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
                location = md.bazaar_buy_types[setup_data["bazaar_buy_type"]]
            elif action == "sell":
                location = md.bazaar_sell_types[setup_data["bazaar_sell_type"]]
                if setup_data["bazaar_taxes"]:
                    bazaar_tax = 0.0125 - 0.00125 * setup_data["bazaar_flipper"]
                    bazaar_tax *= md.calculator_data[setup_data["mayor"]]["tax_multiplier"]
                    multiplier = 1 - bazaar_tax
        elif location == "npc" and action == "buy":
            multiplier = 2
        if ID in md.calculator_data:
            if location in md.calculator_data[ID]["prices"]:
                return multiplier * md.calculator_data[ID]["prices"][location]
            elif force:
                self.huim.logger.warning("no forced cost found for " + ID)
                return 0
            elif "custom" in md.calculator_data[ID]["prices"]:
                return md.calculator_data[ID]["prices"]["custom"]
            elif "npc" in md.calculator_data[ID]["prices"]:
                return multiplier * md.calculator_data[ID]["prices"]["npc"]
            else:
                self.huim.logger.warning("no cost found for " + ID)
                return 0
        else:
            self.huim.logger.error(ID + " not in calculator data")
            return 0

    def get_speed_boosts(self, minion, minion_fuel_id, upgrade_ids, afk_toggle, clock_override, setup_data):
        """
        Adds up speed boosts, uses the fact that booleans can be seen as 0 and 1 for false and true resp.

        Parameters
        ----------
        minion : str
            Minion type ID.
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
            potato_accessory, afkpet, afkpet_rarity, afkpet_lvl, rising_celsius_override

        Returns
        -------
        float
            Total additive speed boost.
        """
        speed_boost = 0
        speed_boost += md.calculator_data[minion_fuel_id]["speed_boost"]
        speed_boost += md.calculator_data[upgrade_ids[0]]["speed_boost"] + md.calculator_data[upgrade_ids[1]]["speed_boost"]
        speed_boost += md.calculator_data[setup_data["beacon"]]["speed_boost"] + md.calculator_data["MITHRIL_INFUSION"]["speed_boost"] * setup_data["infusion"]
        speed_boost += md.calculator_data["FREE_WILL"]["speed_boost"] * setup_data["free_will"] + md.calculator_data["POSTCARD"]["speed_boost"] * setup_data["postcard"]
        if setup_data["crystal"] != "NONE":
            if md.has_data_tag(minion, md.calculator_data[setup_data["crystal"]]["affected_minions"]):
                speed_boost += md.calculator_data[setup_data["crystal"]]["speed_boost"]
        if setup_data["beacon"] != "NONE" and setup_data["scorched"]:
            speed_boost += md.calculator_data["SCORCHED_POWER_CRYSTAL"]["speed_boost"]
        if minion == "INFERNO_MINION":
            if setup_data["rising_celsius_override"]:
                speed_boost += 180
            else:
                speed_boost += 18 * min(10, setup_data["amount"])
        if minion_fuel_id == "EVERBURNING_FLAME" and md.has_data_tag(minion, md.calculator_data[minion_fuel_id]["upgrade_special"]["affected_minions"]):
            speed_boost += md.calculator_data[minion_fuel_id]["upgrade_special"]["amount"]
        if not (afk_toggle or clock_override):
            return speed_boost
        if md.has_data_tag(minion, md.calculator_data[setup_data["mayor"]]["affected_minions"]):
            speed_boost += md.calculator_data[setup_data["mayor"]]["speed_boost"]
        if md.has_data_tag(minion, md.calculator_data[setup_data["potato_accessory"]]["affected_minions"]):
            speed_boost += md.calculator_data[setup_data["potato_accessory"]]["speed_boost"]
        afkpet = setup_data["afkpet"]
        afkpet_rarity = setup_data["afkpet_rarity"]
        if md.has_data_tag(minion, md.calculator_data[afkpet]["affected_minions"]) and afkpet_rarity in md.calculator_data[afkpet]["boosting_pet"]:
            speed_boost += md.calculator_data[afkpet]["boosting_pet"][afkpet_rarity][0] + setup_data["afkpet_lvl"] * md.calculator_data[afkpet]["boosting_pet"][afkpet_rarity][1]
        return speed_boost

    def get_drop_multiplier(self, minion, minion_fuel_id, upgrade_ids, afk_toggle, setup_data):
        """
        Multiplies together drop multipliers.

        Parameters
        ----------
        minion : str
            Minion type ID.
        minion_fuel_id : str
            Minion fuel ID.
        upgrade_ids : list
            List of upgrade IDs
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: player_harvests, player_looting, mayor

        Returns
        -------
        float
            Total multiplicative drop multiplier.
        """
        drop_multiplier = 1
        if afk_toggle and setup_data["player_harvests"] and (minion not in ["FISHING_MINION", "PUMPKIN_MINION", "MELON_MINION"]):
            if md.has_data_tag(minion, "mob_minion"):
                drop_multiplier *= 1 + 15 * setup_data["player_looting"] / 100
            return drop_multiplier
        drop_multiplier *= md.calculator_data[minion_fuel_id]["drop_multiplier"]
        drop_multiplier *= md.calculator_data[upgrade_ids[0]]["drop_multiplier"]
        if afk_toggle and drop_multiplier > 1:
            # drop multiplier greater than 1 is rounded down while online
            drop_multiplier = int(drop_multiplier)
        drop_multiplier *= md.calculator_data[upgrade_ids[1]]["drop_multiplier"]
        if afk_toggle and drop_multiplier > 1:
            drop_multiplier = int(drop_multiplier)
        if md.has_data_tag(minion, md.calculator_data[setup_data["mayor"]]["affected_minions"]):
            drop_multiplier *= md.calculator_data[setup_data["mayor"]]["drop_multiplier"]
        return drop_multiplier
    
    def get_actions_per_harvest(self, minion, upgrade_ids, afk_toggle, setup_data, setup_notes):
        """
        Multiplies together drop multipliers.

        Parameters
        ----------
        minion : str
            Minion type ID.
        upgrade_ids : list
            List of upgrade IDs
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: player_harvests, special_layout
        setup_notes : dict
            setup notes

        Returns
        -------
        int
            Actions per harvest.
        """
        actions_per_harvest = 2
        if minion == "FISHING_MINION":
            # only has harvests actions
            actions_per_harvest = 1
        if afk_toggle:
            if minion in ["PUMPKIN_MINION", "MELON_MINION"]:
                # pumpkins and melons are forced to regrow for minion to harvest
                actions_per_harvest = 1
            if setup_data["player_harvests"]:
                if minion in ["FISHING_MINION", "PUMPKIN_MINION", "MELON_MINION"]:
                    setup_notes["Player Harvests"] = "Player Harvesting does not work with this minion"
                else:
                    actions_per_harvest = 1
                    if minion in ["GRAVEL_MINION"]:
                        upgrade_ids.append("FLINT_SHOVEL")
                        setup_notes["Player Tools"] = "Assuming Player is using Flint Shovel"
                    if minion in ["ICE_MINION"]:
                        setup_notes["Player Tools"] = "Assuming Player is using Silk Touch"
            elif setup_data["special_layout"]:
                if minion in ["COBBLESTONE_MINION", "MYCELIUM_MINION", "ICE_MINION"]:
                    # cobblestone generator, regrowing mycelium, freezing water
                    actions_per_harvest = 1
                if minion in ["FLOWER_MINION", "SAND_MINION", "RED_SAND_MINION", "GRAVEL_MINION"]:
                    # harvests through natural means: water flushing, gravity
                    actions_per_harvest = 1
                    # speedBonus -= 10  # only spawning has 10% action speed reduction, not confirmed yet.
        return actions_per_harvest

    def update_loot_table(self, minion, minion_fuel_id, upgrades, afk_toggle, setup_data):
        """
        Applies changes to the loot tables of the minions depending on things like AFKing or special layouts.

        Parameters
        ----------
        minion : str
            Minion type ID.
        minion_fuel_id : str
            Minion fuel ID
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: special_layout

        Returns
        -------
        None.
        """
        if md.has_data_tag(minion, "wood_minion"):
            if afk_toggle:
                # chopped trees have 4 blocks of wood, unknown why offline gives 3
                md.calculator_data[minion]["drops"][list(md.calculator_data[minion]["drops"].keys())[0]] = 4
            else:
                md.calculator_data[minion]["drops"][list(md.calculator_data[minion]["drops"].keys())[0]] = 3
        elif minion == "GRAVEL_MINION":
            if afk_toggle:
                # vanilla minecraft chance for gravel to become flint
                md.calculator_data[minion]["drops"]["GRAVEL"] = 0.9
                md.calculator_data[minion]["drops"]["FLINT"] = 0.1
            else:
                md.calculator_data[minion]["drops"]["GRAVEL"] = 1
                md.calculator_data[minion]["drops"]["FLINT"] = 0
        elif minion == "PUMPKIN_MINION":
            if afk_toggle:
                # it just does this, idk, ask Hypixel
                md.calculator_data[minion]["drops"]["PUMPKIN"] = 1
            else:
                md.calculator_data[minion]["drops"]["PUMPKIN"] = 3
        elif minion == "SHEEP_MINION":
            if "ENCHANTED_SHEARS" in upgrades:
                md.calculator_data[minion]["drops"]["WOOL"] = 0
            else:
                md.calculator_data[minion]["drops"]["WOOL"] = 1
        elif minion == "FLOWER_MINION":
            if minion_fuel_id == "THORNY_VINES":
                md.calculator_data[minion]["drops"] = { "WILD_ROSE": 2 }
            elif afk_toggle and setup_data["special_layout"]:
                # tall flowers blocked by low ceiling
                md.calculator_data[minion]["drops"] = { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "RED_ROSE:1": 0.5 / 8, "RED_ROSE:2": 0.5 / 8, "RED_ROSE:3": 0.5 / 8, "RED_ROSE:4": 0.5 / 8, "RED_ROSE:5": 0.5 / 8, "RED_ROSE:6": 0.5 / 8, "RED_ROSE:7": 0.5 / 8, "RED_ROSE:8": 0.5 / 8 }
            else:
                md.calculator_data[minion]["drops"] = { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "RED_ROSE:1": 0.5 / 11, "RED_ROSE:2": 0.5 / 11, "RED_ROSE:3": 0.5 / 11, "RED_ROSE:4": 0.5 / 11, "RED_ROSE:5": 0.5 / 11, "RED_ROSE:6": 0.5 / 11, "RED_ROSE:7": 0.5 / 11, "RED_ROSE:8": 0.5 / 11, "DOUBLE_PLANT:1": 0.5 / 11, "DOUBLE_PLANT:4": 0.5 / 11, "DOUBLE_PLANT:5": 0.5 / 11 }
        elif minion == "SUNFLOWER_MINION":
            if minion_fuel_id == "DAYSWITCH":
                md.calculator_data[minion]["drops"] = { "DOUBLE_PLANT": 2 }
            elif minion_fuel_id == "NIGHTSWITCH":
                md.calculator_data[minion]["drops"] = { "MOONFLOWER": 2 }
            else:
                md.calculator_data[minion]["drops"] = { "DOUBLE_PLANT": 1, "MOONFLOWER": 1 }
        return

    def get_seconds_per_action(self, minion, minion_tier, minion_fuel_id, speed_boost, setup_data):
        """
        Calculates total minion speed.

        Parameters
        ----------
        minion : str
            Minion type ID.
        minion_tier : int
            Minion tier, 1 to 12.
        minion_fuel_id : 
            Minion fuel ID
        speed_boost : float
            Total additive speed boost
        setup_data : dict
            Needed setup data: inferno_grade

        Returns
        -------
        float
            seconds per action.
        """
        base_speed = md.calculator_data[minion]["speed"][minion_tier]
        secondsPaction = base_speed / (1 + speed_boost / 100)
        if minion_fuel_id == "INFERNO_FUEL":
            secondsPaction /= 1 + md.inferno_fuel_data["grades"][setup_data["inferno_grade"]]
        return secondsPaction

    def get_time_constants(self, seconds_per_action, actions_per_harvest, setup_data):
        """
        Calculates empty_time in seconds and the ratio between scaled time and empty time.

        Parameters
        ----------
        seconds_per_action : float
            Final seconds per action.
        actions_per_harvest : int
            Final actions per harvest.
        setup_data : dict
            Needed setup data: empty_time_unit, empty_time_amount, scale_time, scaled_time_unit, scaled_time_amount

        Returns
        -------
        float, float
            Time between empties in seconds, ratio between empty_time and scaled time.
        """
        empty_time_seconds = self.huim.time_number(setup_data["empty_time_unit"], setup_data["empty_time_amount"], seconds_per_action * actions_per_harvest)
        empty_time_str = scaled_time_str = f"{setup_data["empty_time_amount"]} {setup_data["empty_time_unit"]}"
        timeratio = 1
        if setup_data["scale_time"]:
            scaled_time_seconds = self.huim.time_number(setup_data["scaled_time_unit"], setup_data["scaled_time_amount"], seconds_per_action * actions_per_harvest)
            scaled_time_str = f"{setup_data["scaled_time_amount"]} {setup_data["scaled_time_unit"]}"
            timeratio = scaled_time_seconds / empty_time_seconds
        return empty_time_seconds, timeratio, empty_time_str, scaled_time_str

    def get_harvests_per_time(self, empty_time_seconds, actions_per_harvest, seconds_per_action, afk_toggle, drop_multiplier, setup_data):
        """
        Calculates the amount of harvests in the inputted empty_time.

        Parameters
        ----------
        empty_time_seconds : float
            Time between empties in seconds.
        actions_per_harvest : int
            Final actions per harvest.
        seconds_per_action : float
            Final seconds per action
        afk_toggle : boolean
            True if AFKing, False if offline
        drop_multiplier : float
            Total drop multiplier
        setup_data : dict
            needed setup data: empty_time_unit, empty_time_amount

        Returns
        -------
        float, float
            amount of harvests between empties, updated drop_multiplier if offline.
        """
        if setup_data["empty_time_unit"] == "Harvests":
            harvests_per_time = setup_data["empty_time_amount"]
        else:
            harvests_per_time = empty_time_seconds / (actions_per_harvest * seconds_per_action)
        
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
            upgrade_type = md.calculator_data[upgrade]["upgrade_special"]["type"]
            if "spreading" in upgrade_type:
                for item, amount in md.calculator_data[upgrade]["upgrade_special"]["items"].items():
                    spreading_info[item] = amount
                    drops_list[item] = 0
            if "replace" in upgrade_type:
                replace_info.update(md.calculator_data[upgrade]["upgrade_special"]["replacement_list"])
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
        :param minion: str, minion type ID
        :param harvests_per_time: float, amount of harvests between empties
        :param drop_multiplier: float, total drop multiplier
        """
        for item, amount in md.calculator_data[minion]["drops"].items():
            self.add_drops(item, harvests_per_time * amount * drop_multiplier, drops_list, spreading_info, replace_info)
        return

    def get_upgrade_drops(self, drops_list, spreading_info, minion, minion_tier, drop_multiplier, upgrade_ids, harvests_per_time, afk_toggle, empty_time_seconds, seconds_per_action):
        """
        Gets generated drops from upgrades of the setup and adds them to the drops_list
        
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param minion: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param drop_multiplier: float, total drop multiplier
        :param upgrade_ids: list, upgrade IDs
        :param harvests_per_time: float, amount of harvests between empties
        :param afk_toggle: boolean, True if AFKing, False if offline
        :param empty_time_seconds: float, seconds between empties
        :param seconds_per_action: float, seconds per minion action
        """
        for upgrade in upgrade_ids:
            upgrade_type = md.calculator_data[upgrade]["upgrade_special"]["type"]
            specific_multiplier = 1
            if upgrade_type == "add":
                # adding upgrades are like Corrupt Soils
                if afk_toggle:
                    if "CORRUPT_SOIL" == upgrade:
                        if "afkcorrupt" in md.calculator_data[minion]:
                            # Certain mob minions get more corrupt drops when afking
                            # It is not a constant multiplier, it is equivalent in chance to the main drops of the minion
                            specific_multiplier = md.calculator_data[minion]["afkcorrupt"]
                        if minion == "CHICKEN_MINION" and "ENCHANTED_EGG" not in upgrade_ids:
                            # Online Chicken minion without Enchanted Egg does not make corrupt drops
                            specific_multiplier = 0
                    if "ENCHANTED_EGG" == upgrade:
                        # Enchanted Eggs make one laid egg and one egg on kill while AFKing
                        # the egg on spawn is affected by drop multipliers and spreadings
                        self.add_drops("EGG", harvests_per_time * drop_multiplier, drops_list, spreading_info)
                    for item, amount in md.calculator_data[upgrade]["upgrade_special"]["items"].items():
                        self.add_drops(item, harvests_per_time * amount * specific_multiplier, drops_list)
                else:
                    for item, amount in md.calculator_data[upgrade]["upgrade_special"]["items"].items():
                        self.add_drops(item, harvests_per_time * amount * specific_multiplier, drops_list, spreading_info)
            elif upgrade_type == "cooldown":
                # cooldown upgrades are like Soulflow Engines
                # formula for effective_cooldown still in research
                if afk_toggle and upgrade == "LESSER_SOULFLOW_ENGINE" and "SOULFLOW_ENGINE" in upgrade_ids:
                    continue  # Soulflow Engine overrides Lesser Soulflow Engine while online
                if afk_toggle:
                    effective_cooldown = 2 * seconds_per_action * (1 + math.floor(math.ceil(md.calculator_data[upgrade]["upgrade_special"]["cooldown"] / seconds_per_action) / 2))
                else:
                    effective_cooldown = md.calculator_data[upgrade]["upgrade_special"]["offline_cooldown"]
                if "SOULFLOW_ENGINE" == upgrade and minion == "VOIDLING_MINION":
                    specific_multiplier = 1 + 0.03 * minion_tier  # correct most likely, needs testing
                for cooldown_item, cooldown_amount in md.calculator_data[upgrade]["upgrade_special"]["items"].items():
                    self.add_drops(cooldown_item, specific_multiplier * cooldown_amount * empty_time_seconds / effective_cooldown, drops_list)
        return

    def get_inferno_drops(self, drops_list, spreading_info, replace_info, minion, minion_tier, minion_fuel, drop_multiplier, harvests_per_time, empty_time_seconds, afk_toggle, setup_data):
        """
        Gets generated inferno fuel drops and adds them to drops_list.
        https://wiki.hypixel.net/Inferno_Minion_Fuel
        
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param replace_info: dict, the replacements of original item ID as key and final item ID as value
        :param minion: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param minion_fuel: str, ID of minion fuel
        :param drop_multiplier: float, total drop multiplier
        :param harvests_per_time: float, amount of harvests between empties
        :param empty_time_seconds: float, time between empties
        :param afk_toggle: boolean, True if AFKing, False if offline
        :param setup_data: needed setup data: inferno_distillate, inferno_grade, inferno_eyedrops, setup data for self.get_price
        """
        if minion_fuel != "INFERNO_FUEL":
            return
        # distilate drops
        distilate = setup_data["inferno_distillate"]
        distilate_item = md.inferno_fuel_data["distilates"][distilate][0]
        amount_per = md.inferno_fuel_data["distilates"][distilate][1]
        distillate_harvests = (harvests_per_time * 4) / 5
        if afk_toggle:
            self.get_base_drops(drops_list, spreading_info, replace_info, minion, - distillate_harvests, drop_multiplier)
        else:
            self.get_base_drops(drops_list, None, replace_info, minion, - distillate_harvests, drop_multiplier)
        self.add_drops(distilate_item, distillate_harvests * amount_per, drops_list)

        # Hypergolic drops
        if setup_data["inferno_grade"] == "HYPERGOLIC_GABAGOOL":  # hypergolic fuel stuff
            multiplier = 1
            if setup_data["inferno_eyedrops"] is True:  # Capsaicin Eyedrops
                multiplier = 1.3
            for item, chance in md.inferno_fuel_data["drops"].items():
                if item == "INFERNO_APEX" and minion_tier >= 10:  # Apex Minion perk
                    chance *= 2
                self.add_drops(item, multiplier * chance * harvests_per_time, drops_list)
            self.add_drops("HYPERGOLIC_IONIZED_CERAMICS", empty_time_seconds / md.calculator_data[minion_fuel]["fuel_duration"], drops_list)

        # calculate fuel cost
        infernofuel_components = {
            "INFERNO_FUEL_BLOCK": 2,  # 2 inferno fuel blocks
            distilate: 6,  # 6 times distilate item
            setup_data["inferno_grade"]: 1,  # 1 gabagool core
            "CAPSAICIN_EYEDROPS_NO_CHARGES": int(setup_data["inferno_eyedrops"])  # capsaicin eyedrops
        }
        costPerInfernofuel = 0
        for component_ID, amount in infernofuel_components.items():
            costPerInfernofuel += amount * self.get_price(component_ID, setup_data, action="buy", location="bazaar")
        md.calculator_data["INFERNO_FUEL"]["prices"]["custom"] = costPerInfernofuel
        # the fuel cost is put into the item data to be used later in the general fuel cost calculator
        return

    def apply_compactor(self, drops_list, compacting_list):
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
            if item not in compacting_list:
                continue
            amount = drops_list[item]
            per_compacted = compacting_list[item]["per"]
            if amount < per_compacted:
                continue
            compacted_name = compacting_list[item]["makes"]
            compacted_amount = int(amount / per_compacted)
            if "amount" in compacting_list[item]:
                compacted_amount *= compacting_list[item]["amount"]
            left_over = amount % per_compacted
            drops_list[item] = left_over
            drops_list[compacted_name] = compacted_amount
            compacted_items.append({"from": item, **compacting_list[item]})
            if compacted_name in compacting_list:
                compactables.append(compacted_name)
        return compacted_items

    def get_compacted_drops(self, drops_list, upgrades):
        """
        Gets compacted drops, returns a list of all compacted items
        
        :param drops_list: dict, all drops of the setup
        :param upgrades: list, list of upgrades IDs
        :return compacted_items: list, IDs of items that got compacted
        """
        compacted_items = []
        for upgrade in upgrades:
            if "compact" in md.calculator_data[upgrade]["upgrade_special"]["type"]:
                compacted_items.extend(self.apply_compactor(drops_list, md.calculator_data[upgrade]["upgrade_special"]["compacting_list"]))
        return compacted_items

    def get_available_storage(self, minion, minion_tier, setup_data):
        """
        Gets amount of available storage measured in slots
        
        :param minion: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param setup_data: needed setup data: chest
        :return available_storage: available storage measured in slots
        """
        available_storage = md.calculator_data[setup_data["chest"]]["storage_slots"]
        if "storage" in md.calculator_data[minion] and minion_tier in md.calculator_data[minion]["storage"]:
            available_storage += md.calculator_data[minion]["storage"][minion_tier]
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
            used_storage_slots += math.ceil(amount / 64)  # hypixel does not care about smaller max stack sizes
        return used_storage_slots
    
    def get_fill_time(self, minion, available_storage):
        # WARNING: calculation for fill_time does not work with compactors and is not accurate for setup with multiple drops
        # used_storage_slots calculations work fine.
        # fill_time = (empty_time_seconds * available_storage) / used_storage

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
        
        :param setup_data: needed setup data: sell_loc
        :return sellto: str, general sell location
        :return hopper_multiplier: float, hopper profit multiplier
        """
        sellto = "NPC"
        hopper_multiplier = 1
        minion_sell_loc = setup_data["sell_loc"]
        if minion_sell_loc == "Bazaar":
            sellto = "bazaar"
        elif minion_sell_loc == "Best (NPC/Bazaar)":
            sellto = "best"
        elif minion_sell_loc == "Hopper":
            hopper_multiplier = md.calculator_data[setup_data["hopper"]]["hopper_selling_rate"]
        return sellto, hopper_multiplier
    
    def get_item_profit(self, sell_location, hopper_multiplier, drops_list, setup_data):
        """
        Makes a list of all prices and takes the one that matches the choice of sell_location or takes the maximum, while keeping track where items get sold
        
        :param sell_location: str, general sell location
        :param hopper_multiplier: hopper profit multiplier
        :param drops_list: dict, all drops of the setup
        :param setup_data: dict, needed setup data: setup data for self.get_price
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
            item_prices["NPC"] = self.get_price(itemtype, setup_data, "sell", "npc")
            item_prices["bazaar"] = self.get_price(itemtype, setup_data, "sell", "bazaar")
            # item_prices["custom"] = self.get_price(itemtype, setup_data, "sell", "custom", force=True)  # might use later
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
        :param setup_data: needed setup data: player_harvests, combat_wisdom, mining_wisdom, farming_wisdom, fishing_wisdom, foraging_wisdom, alchemy_wisdom
        :return skill_xp: dict, gained skill xp per type
        """
        skill_xp = {}
        for itemtype, amount in drops_list.items():
            xptype, value = list(*md.calculator_data[itemtype]["xp"].items())
            if value == 0:
                continue
            if xptype not in skill_xp:
                skill_xp[xptype] = 0
            skill_xp[xptype] += amount * value * (1 + setup_data[xptype + "_wisdom"] / 100)
        self.huim.deepmultiply(skill_xp, md.calculator_data[mayor]["xp_multiplier"])
        if afk_toggle and setup_data["player_harvests"] and "combat" in skill_xp:
            del skill_xp["combat"]
        return skill_xp

    def get_over_compacting(self, sell_location, compacted_items, per_item_sell_location, setup_notes, setup_data):
        """
        Checks for all compacted items if compacting them loses value
        
        :param sell_location: str, general sell location
        :param compacted_items: list, IDs of items that got compacted
        :param per_item_sell_location: dict, final sell location per item ID
        :param setup_notes: dict, setup notes
        :param setup_data: needed setup data: setup data for self.get_price
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
            cost = self.get_price(item, setup_data, "sell", per_item_sell_location[item]) * per_compact
            compact_cost = self.get_price(compact_item, setup_data, "sell", per_item_sell_location[compact_item]) * compact_amount
            if cost - compact_cost > compact_tolerance:
                over_compacting.append(md.calculator_data[item]['display'])
        if len(over_compacting) != 0:
            setup_notes["Over-compacting"] = ', '.join(over_compacting)
        return

    def get_pet_xp_boosts(self, pet, xp_type, setup_data, exp_share=False):
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
        setup_data : dict
            needed setup data: taming, beastmaster, petxpboost, mayor, falcon_attribute
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
        if md.calculator_data[pet]["pet_type"] != "all" and md.calculator_data[pet]["pet_type"] != xp_type:
            if xp_type in ["alchemy", "enchanting"]:
                non_matching = 1 / 12
            else:
                non_matching = 1 / 3
        if exp_share:
            return non_matching
        petxpbonus = (1 + setup_data["taming"] / 100) * (1 + setup_data["beastmaster"] / 100) * non_matching
        if md.calculator_data[setup_data["petxpboost"]]["exp_boost_type"] in [xp_type, "all"]:
            pet_item = 1 + md.calculator_data[setup_data["petxpboost"]]["exp_boost_amount"] / 100
        else:
            pet_item = 1
        if setup_data["mayor"] == "MAYOR_DIANA":
            petxpbonus *= 1.35
        if xp_type in ["mining", "fishing"]:
            petxpbonus *= 1.5
        if pet == "PET_REINDEER":
            petxpbonus *= 2
        if xp_type in ["combat"] and setup_data["falcon_attribute"] != 0:
            petxpbonus *= (1 + setup_data["falcon_attribute"] / 100)
        return petxpbonus, pet_item

    def dragon_xp(self, gained_xp, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item):
        """
        Calculates the pet xp gain on the dragon pets.

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

    def get_pet_profit(self, skill_xp, mayor, setup_data):
        """
        Get total profit from pet levelling\n
        Pet levelling calculations: https://wiki.hypixel.net/Pets#Leveling,\n
        for Golden Dragon: special algorithm taking into account that pet items cannot be applied to Golden Dragon Eggs,\n
        the pet costs are manually added in pet_data
        
        :param skill_xp: dict, gained skill xp per type
        :param mayor: str, mayor
        :param setup_data: needed setup data: levelingpet, expsharepet, expsharepetslot2, expsharepetslot3, taming, toucan_attribute, expshareitem, petxpboost, setup data for self.get_price and for self.get_pet_xp_boosts
        :return pet_profit: float, total profit from pets
        :return setup_pets: dict, pet slot var key as key, dict as value with pet name, pet xp and amount of levelled pets
        :return pet_prices: dict, pet name as key, string as value with lvl 1 price and max lvl price 
        """
        pet_profit = 0.0
        main_pet = setup_data["levelingpet"]
        if main_pet == "NONE":
            return 0, {}, {}
        setup_pets = { "levelingpet": { "pet": main_pet, "pet_xp": {}, "levelled_pets": 0.0 } }
        for var_key in ["expsharepet", "expsharepetslot2", "expsharepetslot3"]:
            if setup_data[var_key] == "NONE" or (mayor != "MAYOR_DIANA" and var_key in ["expsharepetslot2", "expsharepetslot3"]):
                continue
            setup_pets[var_key] = { "pet": setup_data[var_key], "pet_xp": { "exp_share": 0.0 }, "levelled_pets": 0.0 }
        pet_prices = {}
        main_pet_xp = setup_pets["levelingpet"]["pet_xp"]
        if "Dragon" in md.calculator_data[main_pet]["rarity"]:
            left_over_pet_xp = 0.0
            for skill, amount in skill_xp.items():
                pet_xp_boost, xp_boost_pet_item = self.get_pet_xp_boosts(main_pet, skill, setup_data)
                main_pet_xp[skill], left_over_pet_xp = self.dragon_xp(amount, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item)
        else:
            for skill, amount in skill_xp.items():
                pet_xp_boost, xp_boost_pet_item = self.get_pet_xp_boosts(main_pet, skill, setup_data)
                main_pet_xp[skill] = amount * pet_xp_boost * xp_boost_pet_item
        exp_share_boost = 0.2 * setup_data["taming"] + 10 * (mayor == "MAYOR_DIANA") + setup_data["toucan_attribute"]
        exp_share_item = 15 * setup_data["expshareitem"]
        for pet_slot, pet_info in setup_pets.items():
            if pet_slot == "levelingpet":
                continue
            exp_share_pet = pet_info["pet"]
            if "Dragon" in md.calculator_data[exp_share_pet]["rarity"]:
                if exp_share_boost == 0:
                    continue
                left_over_pet_xp = 0.0
                for skill, amount in main_pet_xp.items():
                    non_matching = self.get_pet_xp_boosts(exp_share_pet, skill, setup_data, True)
                    equiv_pet_xp_boost = non_matching * (exp_share_boost / 100)
                    equiv_xp_boost_pet_item = 1 + exp_share_item / exp_share_boost
                    gained_pet_xp, left_over_pet_xp = self.dragon_xp(amount, left_over_pet_xp, equiv_pet_xp_boost, equiv_xp_boost_pet_item)
                    pet_info["pet_xp"]["exp_share"] += gained_pet_xp
            else:
                for skill, amount in main_pet_xp.items():
                    non_matching = self.get_pet_xp_boosts(exp_share_pet, skill, setup_data, True)
                    pet_info["pet_xp"]["exp_share"] += amount * ((exp_share_boost + exp_share_item) / 100) * non_matching
        super_scrubber_price = self.get_price("SUPER_SCRUBBER", setup_data, "buy", "custom", True)
        for pet_slot, pet_info in setup_pets.items():
            pets_levelled = sum(pet_info["pet_xp"].values()) / md.max_lvl_pet_xp_amounts[md.calculator_data[pet_info["pet"]]["rarity"]]
            setup_pets[pet_slot]["levelled_pets"] = pets_levelled
            if pet_info["pet"] not in pet_costs:
                if pet_info["pet"] not in pet_prices:
                    pet_prices[pet_info["pet"]] = f"Price for {md.calculator_data[pet_info['pet']]["display"]} not found"
            else:
                pet_profit += pets_levelled * (pet_costs[pet_info["pet"]]["max"] - pet_costs[pet_info["pet"]]["min"])
                if pet_info["pet"] not in pet_prices:
                    pet_prices[pet_info["pet"]] = f"{self.huim.reduced_number(pet_costs[pet_info["pet"]]["min"])} - {self.huim.reduced_number(pet_costs[pet_info["pet"]]["max"])}"
            if pet_slot == "levelingpet" and (main_pet_item := setup_data["petxpboost"]) != "NONE":
                pet_profit -= pets_levelled * (md.pet_item_scrub_cost[md.calculator_data[main_pet_item]["rarity"]] + super_scrubber_price)
            if pet_slot != "levelingpet" and setup_data["expshareitem"]:
                pet_profit -= pets_levelled * (md.pet_item_scrub_cost[md.calculator_data["PET_ITEM_EXP_SHARE"]["rarity"]] + super_scrubber_price)
        return pet_profit, setup_pets, pet_prices

    def get_finite_fuel_cost(self, minion_amount, minion_fuel, empty_time_seconds, setup_data):
        """
        get cost per empty_time for the finite fuel and beacon fuel
        
        :param minion_amount: int, minion amount
        :param minion_fuel: str, ID of minion fuel
        :param empty_time_seconds: float, time between empties in seconds
        :param setup_data: needed setup data: beacon, scorched, B_constant, setup data for self.get_price
        """
        fuel_cost = 0.0
        needed_fuel = 0.0
        if setup_data["beacon"] != "NONE":
            if setup_data["scorched"]:
                beacon_fuel_ID = "SCORCHED_POWER_CRYSTAL"
            else:
                beacon_fuel_ID = "POWER_CRYSTAL"
            cost_per_crystal = self.get_price(beacon_fuel_ID, setup_data, "buy", "bazaar")
            fuel_cost += empty_time_seconds * cost_per_crystal / md.calculator_data[beacon_fuel_ID]["fuel_duration"] * int(not (setup_data["B_constant"]))
        if md.calculator_data[minion_fuel]["fuel_duration"] != -1:
            cost_per_fuel = self.get_price(minion_fuel, setup_data, "buy", "bazaar")
            needed_fuel = minion_amount * empty_time_seconds / md.calculator_data[minion_fuel]["fuel_duration"]
            fuel_cost += needed_fuel * cost_per_fuel
        return fuel_cost, needed_fuel

    def get_setup_cost(self, minion_type, minion_tier, minion_amount, minion_fuel, upgrades, setup_pets, setup_notes, setup_data):
        """
        Gets cost of all parts of the setup
        
        :param minion_type: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param minion_amount: int, minion amount
        :param minion_fuel: str, ID of minion fuel
        :param upgrades: list, IDs of upgrades
        :param setup_notes: dict, setup notes
        :param setup_data: needed setup data: hopper, infusion, free_will, chest, beacon, B_acquired, crystal, postcard, potato_accessory, petxpboost, expshareitem, toucan_attribute, falcon_attribute, setup data for self.get_price
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
        tier_loop = range(1, minion_tier + 1)
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
                    cost_cache[item] = self.get_price(item, setup_data, "buy", "bazaar")
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
        if minion_fuel != "NONE" and md.calculator_data[minion_fuel]["fuel_duration"] == -1:
            cost_per_part["fuel"] = self.get_price(minion_fuel, setup_data, "buy", "bazaar")

        # Hopper cost
        if setup_data["hopper"] != "NONE":
            cost_per_part["hopper"] = self.get_price(setup_data["hopper"], setup_data, "buy", "bazaar")

        # Internal minion upgrades cost
        for i, upgrade in enumerate(upgrades):
            if upgrade != "NONE":
                cost_per_part[f"upgrade{i + 1}"] = self.get_price(upgrade, setup_data, "buy", "bazaar")

        # Infusion cost
        if setup_data["infusion"]:
            cost_per_part["infusion"] = self.get_price("MITHRIL_INFUSION", setup_data, "buy", "bazaar")

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
        free_will_price = self.get_price("FREE_WILL", setup_data, "buy", "bazaar")
        postcard_price = self.get_price("POSTCARD", setup_data, "buy", "custom", True)
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
            self.huim.logger.debug(f"Found Average Free Will cost per tier:\n{tiered_free_will}",)
            optimal = min(tiered_free_will, key=tiered_free_will.get)
            self.optimal_tier_free_will.set(optimal)
            setup_notes["Free Will"] = f"per minion, apply {1 / (0.5 + 0.04 * (optimal - 1)):.2} Free Wills on Tier {optimal}"
            cost_per_part["free_will"] = tiered_free_will[optimal]
            self.freewillcost.set(cost_per_part["free_will"])

        # Storage Chest cost
        if setup_data["chest"] != "NONE":
            cost_per_part["chest"] = self.get_price(setup_data["chest"], setup_data, "buy", "bazaar")
        
        # multiply by minion amount
        self.huim.deepmultiply(cost_per_part, minion_amount)

        # Beacon cost
        if setup_data["beacon"] != "NONE" and not setup_data["B_acquired"]:
            cost_per_part["beacon"] = self.get_price(setup_data["beacon"], setup_data, "buy", "bazaar")

        # Floating Crystal cost
        if setup_data["crystal"] != "NONE":
            cost_per_part["crystal"] = self.get_price(setup_data["crystal"], setup_data, "buy", "bazaar")

        # Postcard cost
        if setup_data["postcard"]:
            cost_per_part["postcard"] = final_postcard_cost

        # Potato Talisman cost
        if setup_data["potato_accessory"] != "NONE":
            cost_per_part["potato_accessory"] = self.get_price(setup_data["potato_accessory"], setup_data, "buy", "custom", True)

        # Pet Item costs
        for pet_slot in setup_pets.keys():
            if pet_slot == "levelingpet":
                cost_per_part["petxpboost"] = self.get_price(setup_data["petxpboost"], setup_data, "buy", "custom", True)
            elif setup_data["expshareitem"]:
                if "expshareitem" not in cost_per_part:
                    cost_per_part["expshareitem"] = 0
                cost_per_part["expshareitem"] += self.get_price("PET_ITEM_EXP_SHARE", setup_data, "buy", "bazaar")

        # Attribute costs
        if setup_data["toucan_attribute"] != 0:
            cost_per_part["toucan_attribute"] = md.attribute_shards["Epic"][setup_data["toucan_attribute"]] * self.get_price("SHARD_TOUCAN", setup_data, "buy", "bazaar")
        if setup_data["falcon_attribute"] != 0:
            cost_per_part["falcon_attribute"] = md.attribute_shards["Rare"][setup_data["falcon_attribute"]] * self.get_price("SHARD_FALCON", setup_data, "buy", "bazaar")


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
            self.update_prices(cooldown_warning=False, in_gui=inGUI)

        # Get inputs if none are given
        if setup_data is None:
            setup_data = self.huim.get_from_GUI(self.ID_order)

        # extracting often used minion constants
        minion_type = setup_data["minion"]
        minion_tier = setup_data["miniontier"]
        minion_amount = setup_data["amount"]
        minion_fuel = setup_data["fuel"]
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
        upgrades = [setup_data["upgrade1"], setup_data["upgrade2"]]

        # adding up minion speed bonus
        speed_boost = self.get_speed_boosts(minion_type, minion_fuel, upgrades, afk_toggle, clock_override, setup_data)

        # multiply up minion drop bonus
        drop_multiplier = self.get_drop_multiplier(minion_type, minion_fuel, upgrades, afk_toggle, setup_data)

        # AFKing, Special Layouts and Player Harvests influences
        actions_per_harvest = self.get_actions_per_harvest(minion_type, upgrades, afk_toggle, setup_data, setup_notes)

        # AFK loot table changes
        self.update_loot_table(minion_type, minion_fuel, upgrades, afk_toggle, setup_data)

        # calculate final minion speed
        seconds_per_action = self.get_seconds_per_action(minion_type, minion_tier, minion_fuel, speed_boost, setup_data)

        # time calculations
        empty_time_seconds, timeratio, empty_time_str, scaled_time_str = self.get_time_constants(seconds_per_action, actions_per_harvest, setup_data)
        
        # harvests per time
        harvests_per_time, drop_multiplier = self.get_harvests_per_time(empty_time_seconds, actions_per_harvest, seconds_per_action, afk_toggle, drop_multiplier, setup_data)

        # initialise drops list and get upgrade info
        spreading_info, replace_info = self.get_upgrade_info(upgrades, drops_list)
        
        # base drops
        self.get_base_drops(drops_list, spreading_info, replace_info, minion_type, harvests_per_time, drop_multiplier)

        # upgrade drops
        self.get_upgrade_drops(drops_list, spreading_info, minion_type, minion_tier, drop_multiplier, upgrades, harvests_per_time, afk_toggle, empty_time_seconds, seconds_per_action)
        
        # Inferno minion fuel drops
        self.get_inferno_drops(drops_list, spreading_info, replace_info, minion_type, minion_tier, minion_fuel, drop_multiplier, harvests_per_time, empty_time_seconds, afk_toggle, setup_data)

        # Apply compactors
        compacted_items = self.get_compacted_drops(drops_list, upgrades)

        # storage calculations
        available_storage = self.get_available_storage(minion_type, minion_tier, setup_data)
        used_storage = self.get_used_storage(drops_list)
        fill_time = self.get_fill_time(minion_type, available_storage)

        # multiply drops by minion amount
        # all processes as calculated above should be linear with minion amount
        self.huim.deepmultiply(drops_list, minion_amount)

        sell_location, hopper_multiplier = self.get_sell_location(setup_data)
        # Coins
        item_profit, per_item_profit, per_item_sell_location = self.get_item_profit(sell_location, hopper_multiplier, drops_list, setup_data)
        # XP
        skill_xp = self.get_skill_xp(afk_toggle, mayor, drops_list, setup_data)

        # Check for over-compacting
        self.get_over_compacting(sell_location, compacted_items, per_item_sell_location, setup_notes, setup_data)
        
        # Pet leveling
        pet_profit, setup_pets, pet_prices = self.get_pet_profit(skill_xp, mayor, setup_data)

        # calculating beacon and limited fuel cost
        fuel_cost, needed_fuel = self.get_finite_fuel_cost(minion_amount, minion_fuel, empty_time_seconds, setup_data)

        # total profit
        total_profit = item_profit + pet_profit - fuel_cost

        # Setup cost
        total_cost, extra_cost, cost_per_part = self.get_setup_cost(minion_type, minion_tier, minion_amount, minion_fuel, upgrades, setup_pets, setup_notes, setup_data)

        # Construct ID
        setup_ID = self.construct_id(setup_data)

        # Get minion notes
        if "notes" in md.calculator_data[minion_type]:
            setup_notes.update(md.calculator_data[minion_type]["notes"])

        # collect outputs
        outputs = {
            "pet_profit": pet_profit,
            "harvests": minion_amount * harvests_per_time,
            "itemtype_profit": per_item_profit,
            "items": drops_list,
            "item_profit": item_profit,
            "xp": skill_xp,
            "fuelcost": fuel_cost,
            "total_profit": total_profit,
            "fuelamount": needed_fuel,
            "pets_levelled": {pet_slot: setup_pets[pet_slot]["levelled_pets"] for pet_slot in setup_pets.keys()}
        }

        self.huim.deepmultiply(outputs, timeratio)
        outputs["fuelamount"] = math.ceil(outputs["fuelamount"] / minion_amount) * minion_amount
        outputs.update({
            "available_storage": available_storage,
            "item_sell_loc": per_item_sell_location,
            "ID_container": [setup_ID],
            "ID": setup_ID,
            "extracost": extra_cost,
            "setupcost": total_cost,
            "filltime": fill_time,
            "used_storage": used_storage,
            "empty_time": empty_time_str,
            "scaled_time": scaled_time_str,
            "actiontime": seconds_per_action,
            "notes": setup_notes,
            "used_pet_prices": pet_prices,
        })

        # Update GUI
        if inGUI:
            self.huim.send_to_GUI(outputs)
            self.addons_output_container.list.clear()
            for addon_name, auto_run_bool in self.addons_auto_run.items():
                if auto_run_bool.get():
                    self.addons_list[addon_name](self)
            self.update_listboxes()
            self.statusC.configure(bg="green")
            self.statusC.update()

        if return_outputs:
            return outputs
        return        

    def init_prices(self):
        """
        calls to Hypixel's Item and Bazaar API,
        handles that data to get NPC prices and check which items are on Bazaar.
        Also checks calculator data for all recipe and AH items

        Returns
        -------
        None

        """
        raw_bazaar_data = self.huim.call_API(r"https://api.hypixel.net/v2/skyblock/bazaar", "Hypixel Bazaar API")
        if "success" not in raw_bazaar_data or raw_bazaar_data["success"] is False:
            self.huim.logger.error("Hypixel Bazaar API call was unsuccessful")
            return

        raw_item_data = self.huim.call_API(r"https://api.hypixel.net/resources/skyblock/items", "Hypixel Item API")
        if "success" not in raw_item_data or raw_item_data["success"] is False:
            self.huim.logger.error("Hypixel Item API call was unsuccessful")
            return
        dict_item_data = {}
        for item_data in raw_item_data["items"]:
            dict_item_data[item_data["id"]] = item_data
        
        for item_id in md.calculator_data.keys():
            if "prices" not in md.calculator_data[item_id]:
                continue
            if item_id in dict_item_data and "npc_sell_price" in dict_item_data[item_id]:
                md.calculator_data[item_id]["prices"]["npc"] = dict_item_data[item_id]["npc_sell_price"]
            elif "npc" not in md.calculator_data[item_id]["prices"]:
                md.calculator_data[item_id]["prices"]["npc"] = 0
            if item_id in raw_bazaar_data["products"]:
                self.bazaar_items.append(item_id)
            elif "recipe" in md.calculator_data[item_id]:
                self.recipe_items.append(item_id)
            elif "AH" in md.calculator_data[item_id] and md.calculator_data[item_id]["AH"]:
                self.AH_items.append(item_id)
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
        self.bazaar_update_txt.set("Loading...")
        raw_bazaar_data = self.huim.call_API(r"https://api.hypixel.net/v2/skyblock/bazaar", "Hypixel Bazaar API")
        if "success" not in raw_bazaar_data or raw_bazaar_data["success"] is False:
            self.huim.logger.error("Hypixel Bazaar API call was unsuccessful")
            return
        self.API_timer = raw_bazaar_data["lastUpdated"] / 1000
        top_percent = 0.1
        for item_id in self.bazaar_items:
            if item_id not in raw_bazaar_data["products"]:
                continue
            for action in ["buy", "sell"]:
                top_amount = top_percent * sum([order["amount"] for order in raw_bazaar_data["products"][item_id][f"{action}_summary"]])
                if top_amount == 0:
                    md.calculator_data[item_id]["prices"][f"{action}Price"] = 0
                    if "npc" not in md.calculator_data[item_id]["prices"]:
                        self.huim.logger.warning(f"no {action} supply for {item_id}")
                    continue
                counter = top_amount
                top_sum = 0
                for order in raw_bazaar_data["products"][item_id][f"{action}_summary"]:
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
                top_price = raw_bazaar_data["products"][item_id][f"{action}_summary"][0]["pricePerUnit"]
                if top_price / top_percent_avg_price >= 2.5:
                    md.calculator_data[item_id]["prices"][f"{action}Price"] = top_price
                    self.huim.logger.info(f"bottom heavy {action} supply for {item_id}, taking top order price")
                else:
                    md.calculator_data[item_id]["prices"][f"{action}Price"] = top_percent_avg_price
        self.bazaar_update_txt.set(time.strftime("%Y-%m-%d %H:%M:%S UTC%z", time.localtime(self.API_timer)))
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
        raw_auction_data = self.huim.call_API(r"https://sky.coflnet.com/api/item/price/" + item_id + r"/bin", "SkyCofl AH API", headers={'User-Agent': f"Minion Calculator v{self.version.get()} (Python)"})
        return (raw_auction_data["lowest"] + raw_auction_data["secondLowest"]) / 2

    def update_recipe_price(self, item_id):
        """
        Calculates equivalent bazaar price for recipe items
        
        :param item_id: str, item ID that has a recipe
        
        Returns
        -------
        None.
        """
        if item_id not in md.calculator_data:
            self.huim.logger.error(f"{item_id} not in calculator data")
            return
        if "recipe" not in md.calculator_data[item_id]:
            self.huim.logger.error(f"{item_id} is not a recipe item")
            return
        md.calculator_data[item_id]["prices"]["buyPrice"] = 0
        md.calculator_data[item_id]["prices"]["sellPrice"] = 0
        for material_id, amount in md.calculator_data[item_id]["recipe"].items():
            if "AH" in md.calculator_data[material_id]:
                md.calculator_data[item_id]["prices"]["buyPrice"] += amount * md.calculator_data[material_id]["prices"]["custom"]
                md.calculator_data[item_id]["prices"]["sellPrice"] += amount * md.calculator_data[material_id]["prices"]["custom"]
                continue
            md.calculator_data[item_id]["prices"]["buyPrice"] += amount * md.calculator_data[material_id]["prices"]["buyPrice"]
            md.calculator_data[item_id]["prices"]["sellPrice"] += amount * md.calculator_data[material_id]["prices"]["sellPrice"]
        return

    def update_prices(self, cooldown_warning=True, in_gui=True):
        """
        If API_cooldown is done, update prices
        
        :param cooldown_warning: bool, toggle if a terminal message should be logged if the bazaar update cooldown has not passed yet.
        """
        if time.time() - self.API_timer < API_cooldown and self.API_timer != 0:
            if cooldown_warning:
                self.huim.logger.info("API update is on cooldown")
            return
        self.huim.logger.info("Updating Bazaar prices")
        if in_gui is True:
            background_color_storage = self.statusC["background"]
            self.statusC.configure(bg="aqua")
            self.statusC.update()
        self.call_bazaar()
        self.huim.logger.info("Updating Auction House prices")
        for item_id in self.AH_items:
            md.calculator_data[item_id]["prices"]["custom"] = self.call_auction_house(item_id)
        self.huim.logger.info("Updating Recipe prices")
        for item_id in self.recipe_items:
            self.update_recipe_price(item_id)
        if in_gui is True:
            self.statusC.configure(bg=background_color_storage)
            self.statusC.update()
        return

    def update_listboxes(self):
        """
        Calls .update_listbox() for all variables that are of dtype list or dict.
        Except wisdom

        Returns
        -------
        None.

        """
        for var_key in self.var_dict:
            if self.var_dict[var_key].dtype in [list, dict]:
                if var_key == "wisdom":
                    continue
                if var_key == "pets_levelled":
                    self.pets_levelled.update_listbox(key_format_function=lambda x: self.var_dict[x].get(False))
                    continue
                format_function = lambda x: x
                if self.var_dict[var_key].has_tag("item_ID_to_display"):
                    format_function = lambda x: md.calculator_data[x]["display"]
                self.var_dict[var_key].update_listbox(key_format_function=format_function)
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
        self.addons_output_container.list[output_name] = output_str
        self.addons_output_container.update_listbox()
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
    print("INFO - start_app - Exited mainloop")
    try:
        App.destroy()
        print("INFO - start_app - Detroyed application")
    except Exception:
        print("ERROR - start_app - Please use the stop button in the bottom right to close the application")
    print("INFO - start_app - Closed")
    return

if __name__ == "__main__":
    start_app()
else:
    print("Run `main.py` directly to start the calculator")
