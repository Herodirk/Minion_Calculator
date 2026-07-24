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
    import pathlib
    import json
    import Hero_data_Manager as HDM
    import Hero_UI_Manager as HPM
    import official_calculator_add_ons as Hero_addons
except ModuleNotFoundError as import_error:
    missing_package = import_error.name
    if missing_package in ["Hero_data_Manager", "Hero_UI_Manager", "official_calculator_add_ons"]:
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

# Setup Templates
templateList = {
    "Choose Template": {},  # would suggest to keep this one
    "Load ID": {},  # would suggest to keep this one too
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
    "Solo Wisdom": {  # consists of non-random sources of wisdom that can be achieved alone on the private island, excluding pets
        "mining_wisdom": 103.1,  # Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Refined Divine drill with Compact X (10 + 10), Dimensional Mythic armor (4 * 3), Cavern Wisdom (6.5), Blue Omelette Seasoned Mineman (15.1)
        "combat_wisdom": 113.5,  # Hunter Ring (5), Abicase (1.5), Bubba Blister (2), Rift Necklace (1), cookie (25), god pot (30), Celestial Mason Jar (3), Veteran (10), unique slayer tier kills (6 + 6 + 6 + 12 + 6)
        "farming_wisdom": 190,  # Agarimoo Artifact (1), Abicase (1.5), Lunar Legendary Pelt Belt (1 + 3), Lunar Mythic Zorro's Cape during Contest (2 * (1 + 4)), Lunar Mythic Rift Necklace (1 + 6), Lunar Mythic Gillsplash Gloves (4), Blessed Legendary Mk. III farming tool with Cultivating X (3 + 5 + 10), Mythic Sunny armor (4 * 6), cookie (25), god pot (20), Celestial Mason Jar (3), Very Moldy Bread (30 + 5), Garden Wisdom (6.5), Sowledge Chip (30), Fruit Bowl (1)
        "fishing_wisdom": 92,  # Agarimoo Artifact (1), Chumming Talisman (1), Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Moby-Duck (30 + 1), Sea Wisdom (6.5), Ship Parts (1.5), Ship Crew (0.5), Mysterious Package (1)
        "foraging_wisdom": 98.32,  # Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), David's Cloak (5), Foraging Wisdom Boosters armor and equipment (4 + 2), Moonglade Legendary Axe with Absorb X, Foraging Wisdom Boosters and essence shop perk Axed I ((5 + 10 + 1) * 1.02), Efficient Forager (15), Foraging Wisdom (6.5)
        "alchemy_wisdom": 54.5  # Witch's Artifact (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Spider Slayer VIII (5)
    },
    "Full Coop Wisdom": {  # effective wisdom of 8 players, for each player same sources as above, but no tools, armor or equipment. Calculates as `8 * (1 + W / 100) = (1 + (700 + 8 * W) / 100)`
        "mining_wisdom": 1268,  # Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Cavern Wisdom (6.5), Seasoned Mineman (15)
        "combat_wisdom": 1600,  # Hunter Ring (5), Abicase (1.5), Bubba Blister (2), cookie (25), god pot (30), Celestial Mason Jar (3), Veteran (10), unique slayer tier kills (6 + 6 + 6 + 12 + 6)
        "farming_wisdom": 1684,  # Agarimoo Artifact (1), Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Very Moldy Bread (30 + 5), Garden Wisdom (6.5), Sowledge Chip (30), Fruit Bowl (1)
        "fishing_wisdom": 1436,  # Agarimoo Artifact (1), Chumming Talisman (1), Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Moby-Duck (30 + 1), Sea Wisdom (6.5), Ship Parts (1.5), Ship Crew (0.5), Mysterious Package (1)
        "foraging_wisdom": 1268,  # Abicase (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Efficient Forager (15), Foraging Wisdom (6.5)
        "alchemy_wisdom": 1136  # Witch's Artifact (1.5), cookie (25), god pot (20), Celestial Mason Jar (3), Spider Slayer VIII (5)
    },
    "Combat Pet Leveling": {
        "expshareitem": True,
        "taming": 60,
        "falcon_attribute": 10,
        "pet_exp_boost": "Epic Combat Exp Boost",
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
        "beacon_fuel": "Scorched Power Crystal",
        "infusion": True,
        "free_will": True,
        "postcard": True,
        "bazaar_sell_type": "Sell Offer",
        "bazaar_buy_type": "Buy Order",
        "sell_form": "Compacted"
    },
    "Maxed Solo rdrag Levelling": {
        "minion": "Cactus",
        "amount": 32,
        "fuel": "Hyper Catalyst",
        "sell_loc": "Best (NPC/Bazaar)",
        "upgrade1": "Super Compactor 3000",
        "upgrade2": "Berberis Fuel Injector",
        "chest": "XX-Large Storage",
        "beacon": "Beacon V",
        "beacon_fuel": "Scorched Power Crystal",
        "infusion": True,
        "free_will": True,
        "postcard": True,
        "crystal": "Cornucopia Crystal",
        "unique_farming_minions": 1,
        "expshareitem": True,
        "taming": 60,
        "pet_exp_boost": "Epic Farming Exp Boost",
        "toucan_attribute": 10,
        "bazaar_sell_type": "Sell Offer",
        "bazaar_buy_type": "Buy Order",
        "sell_form": "Compacted",
        "farming_wisdom": 190,
        "mayor": "Diana",
        "levelingpet": "Rose Dragon",
        "expsharepet": "Rose Dragon",
        "expsharepetslot2": "Rose Dragon",
        "expsharepetslot3": "Rose Dragon",
        "beastmaster": 5
    }
}


# and the custom prices in calculator data (see HSB_minion_data.py)


#%% Main Class

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        # Get settings
        self.settings_file = pathlib.Path("calculator_settings.json")
        self.default_settings = {
            "API_auto_update": True,
            "API_cooldown": 120,
            "pet_API_cooldown": 1800,
            "compact_tolerance": 10000,
            "output_to_clipboard": True,
            "debug_mode": False,
            "color_palette": "dark_red",
            "window_width": 1450,
            "window_height": 750,
            "calculated_ID": "",
        }
        if not self.settings_file.is_file():
            self.settings_file.write_text(json.dumps(self.default_settings, indent=4, sort_keys=True), encoding="utf-8")
        try:
            found_settings = json.loads(self.settings_file.read_text())
        except Exception:
            found_settings = {}
        setting_load_errors = []  # queue errors as HUIM is not defined yet
        for setting in self.default_settings.keys():
            if setting not in found_settings:
                setting_load_errors.append(setting)
                found_settings[setting] = self.default_settings[setting]

        # Use Hero UI Manager to initialize the window and the frames with grids
        self.huim = HPM.H_UI_M(main=self, windowTitle="Minion Calculator", windowWidth=found_settings["window_width"], windowHeight=found_settings["window_height"], palette=found_settings["color_palette"], debug_mode=found_settings["debug_mode"])
        if len(setting_load_errors) != 0:
            self.huim.logger.error(f"Could not find the following settings: {", ".join(setting_load_errors)}")
        self.huim.create_controls()
        self.huim.create_frames(self, frame_keys=[["inputs_minion", "inputs_player", "outputs_setup", "outputs_profit"]], grid_frames=True, grid_size=0.96, border=0.003)
        self.frames["addons_main"] = tk.Frame(self, background=self.colors["background"])
        self.huim.create_frames(self.frames["addons_main"], frame_keys=[["addons_buttons", "addons_output"]], grid_frames=True, grid_size=0.96, border=0.01, relControlsHeight=0)
        self.huim.logger.debug("Framework set up")
        self.version = self.huim.def_var(dtype=str, initial="1.2.2")
        self.huim.logger.info(f"Calculator version {self.version.get()}")

        # Getting calculator data
        self.md = HDM.H_data_M(self.huim)
        self.ID_order = self.huim.read_json(pathlib.Path(r"calculator_version_data/id_order.json"))
        self.input_options = self.huim.read_json(pathlib.Path(r"calculator_version_data/input_options.json"))

        # Define variables
        self.API_auto_update = HPM.Hvar(self.huim, key="API_auto_update", vtype="storage", dtype=bool, display="API Auto Update", initial=found_settings["API_auto_update"])
        self.API_cooldown = HPM.Hvar(self.huim, key="API_cooldown", vtype="storage", dtype=int, display="API Cooldown (s)", initial=found_settings["API_cooldown"])
        self.pet_API_cooldown = HPM.Hvar(self.huim, key="pet_API_cooldown", vtype="storage", dtype=int, display="Pet API Cooldown (s)", initial=found_settings["pet_API_cooldown"])
        self.compact_tolerance = HPM.Hvar(self.huim, key="compact_tolerance", vtype="storage", dtype=int, display="Over-compacting (coin)", initial=found_settings["compact_tolerance"])
        self.output_to_clipboard = HPM.Hvar(self.huim, key="output_to_clipboard", vtype="storage", dtype=bool, display="Output to Clipboard", initial=found_settings["output_to_clipboard"])
        self.debug_mode = HPM.Hvar(self.huim, key="debug_mode", vtype="storage", dtype=bool, display="Debug Mode", initial=found_settings["debug_mode"])
        self.color_palette = HPM.Hvar(self.huim, key="color_palette", vtype="storage", dtype=str, display="Color Palette", initial=found_settings["color_palette"], options=list(HPM.color_palettes.keys()))
        self.template = HPM.Hvar(self.huim, key="template", vtype="input", display="Templates", initial="Choose Template", dtype=str, frame="inputs_minion_grid", options=list(templateList.keys()), command=self.load_template)
        self.load_ID = HPM.Hvar(self.huim, key="load_id", vtype="input", dtype=str, frame="inputs_minion_grid", display="Load ID", initial=found_settings["calculated_ID"])
        self.minion = HPM.Hvar(self.huim, key="minion", vtype="input", dtype=str, display="Minion", frame="inputs_minion_grid", initial="Custom", options=self.input_options["minion"], command=lambda x: self.multiswitch('minion', x))
        self.miniontier = HPM.Hvar(self.huim, key="miniontier", vtype="input", dtype=int, display="Tier", frame="inputs_minion_grid", initial=12, options=self.input_options["miniontier"], command=lambda x: self.multiswitch('minion', x))
        self.amount = HPM.Hvar(self.huim, key="amount", vtype="input", dtype=int, display="Amount", frame="inputs_minion_grid", initial=1, options=None)
        self.fuel = HPM.Hvar(self.huim, key="fuel", vtype="input", dtype=str, display="Fuel", frame="inputs_minion_grid", initial="None", options=self.input_options["fuel"], command=lambda x: self.multiswitch('fuel', x))
        self.inferno_grade = HPM.Hvar(self.huim, key="inferno_grade", vtype="input", dtype=str, display="Grade", frame="inputs_minion_grid", initial="Hypergolic Gabagool", options=self.input_options["inferno_grade"])
        self.inferno_distillate = HPM.Hvar(self.huim, key="inferno_distillate", vtype="input", dtype=str, display="Distillate", frame="inputs_minion_grid", initial="Gabagool Distillate", options=self.input_options["inferno_distillate"])
        self.inferno_eyedrops = HPM.Hvar(self.huim, key="inferno_eyedrops", vtype="input", dtype=bool, display="Eyedrops", frame="inputs_minion_grid", initial=False)
        self.hopper = HPM.Hvar(self.huim, key="hopper", vtype="input", dtype=str, display="Hopper", frame="inputs_minion_grid", initial="None", options=self.input_options["hopper"])
        self.upgrade1 = HPM.Hvar(self.huim, key="upgrade1", vtype="input", dtype=str, display="Upgrade 1", frame="inputs_minion_grid", initial="None", options=self.input_options["upgrade"])
        self.upgrade2 = HPM.Hvar(self.huim, key="upgrade2", vtype="input", dtype=str, display="Upgrade 2", frame="inputs_minion_grid", initial="None", options=self.input_options["upgrade"])
        self.chest = HPM.Hvar(self.huim, key="chest", vtype="input", dtype=str, display="Chest", frame="inputs_minion_grid", initial="None", options=self.input_options["chest"])
        self.beacon = HPM.Hvar(self.huim, key="beacon", vtype="input", dtype=str, display="Beacon", frame="inputs_minion_grid", initial="None", options=self.input_options["beacon"], command=self.huim.create_switch_call("beacon", controlvar="self"))
        self.beacon_fuel = HPM.Hvar(self.huim, key="beacon_fuel", vtype="input", dtype=str, display="Beacon Fuel", frame="inputs_minion_grid", initial="Power Crystal", options=self.input_options["beacon_fuel"])
        self.free_fuel_beacon = HPM.Hvar(self.huim, key="free_fuel_beacon", vtype="input", dtype=bool, display="Free Fuel Beacon", frame="inputs_minion_grid", initial=False)
        self.infusion = HPM.Hvar(self.huim, key="infusion", vtype="input", dtype=bool, display="Infusion", frame="inputs_minion_grid", initial=False)
        self.crystal = HPM.Hvar(self.huim, key="crystal", vtype="input", dtype=str, display="Crystal", frame="inputs_minion_grid", initial="None", options=self.input_options["crystal"], command=self.huim.create_switch_call("cornucopia_bonus", controlvar="self"))
        self.unique_farming_minions = HPM.Hvar(self.huim, key="unique_farming_minions", vtype="input", dtype=int, display="Uniques", fancy_display="Unique Farming Minions", frame="inputs_minion_grid", initial=1)
        self.free_will = HPM.Hvar(self.huim, key="free_will", vtype="input", dtype=bool, display="Free Will", frame="inputs_minion_grid", initial=False, command=self.huim.create_switch_call("optimal_free_will", controlvar="free_will"))
        self.postcard = HPM.Hvar(self.huim, key="postcard", vtype="input", dtype=bool, display="Postcard", frame="inputs_minion_grid", initial=False)
        self.afk = HPM.Hvar(self.huim, key="afk", vtype="input", dtype=bool, display="AFK", frame="inputs_player_grid", initial=False, command=lambda: self.multiswitch("afk", None))
        self.afkpet = HPM.Hvar(self.huim, key="afkpet", vtype="input", dtype=str, display="AFK Pet", frame="inputs_player_grid", initial="None", options=self.input_options["afkpet"], command=lambda x: self.afkpet_rarity.update_option_list(list(self.md.calculator_data[self.input_options["afkpet"][x]]["boosting_pet"].keys()), True))
        self.afkpet_rarity = HPM.Hvar(self.huim, key="afkpet_rarity", vtype="input", dtype=str, display="AFK Pet Rarity", frame="inputs_player_grid", initial="Legendary", options=self.input_options["pet_rarity"])
        self.afkpet_lvl = HPM.Hvar(self.huim, key="afkpet_lvl", vtype="input", dtype=float, display="AFK Pet level", frame="inputs_player_grid", initial=0.0)
        self.enchanted_clock = HPM.Hvar(self.huim, key="enchanted_clock", vtype="input", dtype=bool, display="Enchanted Clock", frame="inputs_player_grid", initial=False)
        self.special_layout = HPM.Hvar(self.huim, key="special_layout", vtype="input", dtype=bool, display="Special Layout", frame="inputs_player_grid", initial=False)
        self.player_harvests = HPM.Hvar(self.huim, key="player_harvests", vtype="input", dtype=bool, display="Player Harvests", frame="inputs_player_grid", initial=False)
        self.player_looting = HPM.Hvar(self.huim, key="player_looting", vtype="input", dtype=int, display="Looting", frame="inputs_player_grid", initial=0, options=self.input_options["player_looting"])
        self.potato_accessory = HPM.Hvar(self.huim, key="potato_accessory", vtype="input", dtype=str, display="Potato Accessory", frame="inputs_player_grid", initial="None", options=self.input_options["potato_accessory"])
        self.combat_wisdom = HPM.Hvar(self.huim, key="combat_wisdom", vtype="input", dtype=float, display="Combat wisdom", fancy_display="Combat", frame="inputs_player_grid", initial=0.0)
        self.mining_wisdom = HPM.Hvar(self.huim, key="mining_wisdom", vtype="input", dtype=float, display="Mining wisdom", fancy_display="Mining", frame="inputs_player_grid", initial=0.0)
        self.farming_wisdom = HPM.Hvar(self.huim, key="farming_wisdom", vtype="input", dtype=float, display="Farming wisdom", fancy_display="Farming", frame="inputs_player_grid", initial=0.0)
        self.fishing_wisdom = HPM.Hvar(self.huim, key="fishing_wisdom", vtype="input", dtype=float, display="Fishing wisdom", fancy_display="Fishing", frame="inputs_player_grid", initial=0.0)
        self.foraging_wisdom = HPM.Hvar(self.huim, key="foraging_wisdom", vtype="input", dtype=float, display="Foraging wisdom", fancy_display="Foraging", frame="inputs_player_grid", initial=0.0)
        self.alchemy_wisdom = HPM.Hvar(self.huim, key="alchemy_wisdom", vtype="input", dtype=float, display="Alchemy wisdom", fancy_display="Alchemy", frame="inputs_player_grid", initial=0.0)
        self.mayor = HPM.Hvar(self.huim, key="mayor", vtype="input", dtype=str, display="Mayor", frame="inputs_player_grid", initial="None", options=self.input_options["mayor"], command=lambda x: self.multiswitch("mayors", x))
        self.levelingpet = HPM.Hvar(self.huim, key="levelingpet", vtype="input", dtype=str, display="Leveling pet", frame="inputs_player_grid", initial="None", options=self.input_options["levelingpet"], command=lambda x: self.multiswitch("pet_leveling", x))
        self.levelingpet_rarity = HPM.Hvar(self.huim, key="levelingpet_rarity", vtype="input", dtype=str, display="Leveling pet Rarity", frame="inputs_player_grid", initial="Legendary", options=self.input_options["pet_rarity"])
        self.taming = HPM.Hvar(self.huim, key="taming", vtype="input", dtype=float, display="Taming", frame="inputs_player_grid", initial=0.0)
        self.falcon_attribute = HPM.Hvar(self.huim, key="falcon_attribute", vtype="input", dtype=int, display="Battle Experience", frame="inputs_player_grid", initial=0, options=self.input_options["attribute"])
        self.toucan_attribute = HPM.Hvar(self.huim, key="toucan_attribute", vtype="input", dtype=int, display="Why Not More", frame="inputs_player_grid", initial=0, options=self.input_options["attribute"])
        self.pet_exp_boost = HPM.Hvar(self.huim, key="pet_exp_boost", vtype="input", dtype=str, display="Pet XP boost", frame="inputs_player_grid", initial="None", options=self.input_options["pet_exp_boost"])
        self.beastmaster = HPM.Hvar(self.huim, key="beastmaster", vtype="input", dtype=float, display="Beastmaster", frame="inputs_player_grid", initial=0.0)
        self.expsharepet = HPM.Hvar(self.huim, key="expsharepet", vtype="input", dtype=str, display="Exp Share pet", frame="inputs_player_grid", initial="None", options=self.input_options["levelingpet"], command=lambda x: self.expsharepet_rarity.update_option_list(self.md.calculator_data[self.input_options["levelingpet"][x]]["pet_rarities"], True))
        self.expsharepet_rarity = HPM.Hvar(self.huim, key="expsharepet_rarity", vtype="input", dtype=str, display="Exp Share pet Rarity", frame="inputs_player_grid", initial="Legendary", options=self.input_options["pet_rarity"])
        self.expsharepetslot2 = HPM.Hvar(self.huim, key="expsharepetslot2", vtype="input", dtype=str, display="Exp Share pet 2", frame="inputs_player_grid", initial="None", options=self.input_options["levelingpet"], command=lambda x: self.expsharepetslot2_rarity.update_option_list(self.md.calculator_data[self.input_options["levelingpet"][x]]["pet_rarities"], True))
        self.expsharepetslot2_rarity = HPM.Hvar(self.huim, key="expsharepetslot2_rarity", vtype="input", dtype=str, display="Exp Share pet Rarity", frame="inputs_player_grid", initial="Legendary", options=self.input_options["pet_rarity"])
        self.expsharepetslot3 = HPM.Hvar(self.huim, key="expsharepetslot3", vtype="input", dtype=str, display="Exp Share pet 3", frame="inputs_player_grid", initial="None", options=self.input_options["levelingpet"], command=lambda x: self.expsharepetslot3_rarity.update_option_list(self.md.calculator_data[self.input_options["levelingpet"][x]]["pet_rarities"], True))
        self.expsharepetslot3_rarity = HPM.Hvar(self.huim, key="expsharepetslot3_rarity", vtype="input", dtype=str, display="Exp Share pet Rarity", frame="inputs_player_grid", initial="Legendary", options=self.input_options["pet_rarity"])
        self.expshareitem = HPM.Hvar(self.huim, key="expshareitem", vtype="input", dtype=bool, display="Exp Share pet item", frame="inputs_player_grid", initial=False)
        self.scale_time = HPM.Hvar(self.huim, key="scale_time", vtype="input", dtype=bool, display="Scale Time", frame="inputs_player_grid", initial=False, command=self.huim.create_switch_call("scaled_time_switch", controlvar="scale_time"))
        self.sell_loc = HPM.Hvar(self.huim, key="sell_loc", vtype="input", dtype=str, display="Sell Location", frame="inputs_player_grid", initial="Best (NPC/Bazaar)", options=self.input_options["sell_loc"], command=self.huim.create_switch_call("NPC_Bazaar", controlvar="self"))
        self.bazaar_sell_type = HPM.Hvar(self.huim, key="bazaar_sell_type", vtype="input", dtype=str, display="Bazaar sell type", frame="inputs_player_grid", initial="Sell Offer", options=self.input_options["bazaar_sell_type"])
        self.bazaar_buy_type = HPM.Hvar(self.huim, key="bazaar_buy_type", vtype="input", dtype=str, display="Bazaar buy type", frame="inputs_player_grid", initial="Buy Order", options=self.input_options["bazaar_buy_type"])
        self.bazaar_taxes = HPM.Hvar(self.huim, key="bazaar_taxes", vtype="input", dtype=bool, display="Bazaar taxes", frame="inputs_player_grid", initial=True, command=self.huim.create_switch_call("bazaar_tax", controlvar="bazaar_taxes"))
        self.bazaar_flipper = HPM.Hvar(self.huim, key="bazaar_flipper", vtype="input", dtype=int, display="Bazaar Flipper", frame="inputs_player_grid", initial=1, options=self.input_options["bazaar_flipper"])
        self.sell_form = HPM.Hvar(self.huim, key="sell_form", vtype="input", dtype=str, display="Sell Form", frame="inputs_player_grid", initial="Base", options=self.input_options["sell_form"])
        self.calculated_ID = HPM.Hvar(self.huim, key="calculated_ID", vtype="output", dtype=str, display="Setup ID", frame="outputs_setup_grid", initial="", switch_initial=True)
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
        self.setupcost_breakdown = HPM.Hvar(self.huim, key="setupcost_breakdown", vtype="output", dtype=dict, display="Setup part costs", frame="outputs_profit_grid", widget_width=35, widget_height=8, initial={}, switch_initial=False)
        self.extracost = HPM.Hvar(self.huim, key="extracost", vtype="output", dtype=str, display="Extra cost", frame="outputs_profit_grid", initial="None", switch_initial=True)
        self.optimal_tier_free_will = HPM.Hvar(self.huim, key="optimal_tier_free_will", vtype="output", dtype=int, display="Free Will Tier", fancy_display="Optimal tier Free Will", frame="outputs_profit_grid", initial=0, switch_initial=True)
        self.available_storage = HPM.Hvar(self.huim, key="available_storage", vtype="output", dtype=int, display="Available Storage", frame="outputs_setup_grid", initial=0, switch_initial=False)
        self.addons_output_container = HPM.Hvar(self.huim, key="addons_output_container", vtype="output", dtype=dict, display="Add-on Outputs", frame="addons_output_grid", widget_width=65, widget_height=20, initial={}, switch_initial=False)
        self.empty_time_amount = HPM.Hvar(self.huim, key="empty_time_amount", vtype="input", dtype=float, display="Empty Time span", initial=1.0, frame="inputs_player_grid")
        self.empty_time_unit = HPM.Hvar(self.huim, key="empty_time_unit", vtype="input", dtype=str, display="Empty Time unit", initial="Days", frame="inputs_player_grid", options=self.input_options["time_unit"])
        self.scaled_time_amount = HPM.Hvar(self.huim, key="scaled_time_amount", vtype="input", dtype=float, display="Scaled Time span", initial=1.0, frame="inputs_player_grid")
        self.scaled_time_unit = HPM.Hvar(self.huim, key="scaled_time_unit", vtype="input", dtype=str, display="Scaled Time unit", initial="Days", frame="inputs_player_grid", options=self.input_options["time_unit"])
        self.rising_celsius_override = HPM.Hvar(self.huim, key="rising_celsius_override", vtype="input", dtype=bool, display="Force Rising Celsius", initial=False, frame="inputs_minion_grid")
        self.used_pet_prices = HPM.Hvar(self.huim, key="used_pet_prices", vtype="output", dtype=dict, display="Used Pet Prices", initial={}, frame="outputs_profit_grid", widget_width=35, widget_height=4, switch_initial=True)
        self.custom_upgrade_toggle = HPM.Hvar(self.huim, key="custom_upgrade_toggle", vtype="storage", dtype=bool, display="Custom Upgrade", initial=False)

        self.empty_time_unit.widget[-1].place(in_=self.empty_time_amount.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.scaled_time_unit.widget[-1].place(in_=self.scaled_time_amount.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.afkpet_rarity.widget[-1].place(in_=self.afkpet.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.levelingpet_rarity.widget[-1].place(in_=self.levelingpet.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.expsharepet_rarity.widget[-1].place(in_=self.expsharepet.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.expsharepetslot2_rarity.widget[-1].place(in_=self.expsharepetslot2.widget[-1], relx=1, x=3, rely=0.5, anchor='w')
        self.expsharepetslot3_rarity.widget[-1].place(in_=self.expsharepetslot3.widget[-1], relx=1, x=3, rely=0.5, anchor='w')

        self.notesAnchor = self.huim.create_label(frm=self.frames["outputs_setup_grid"], txt="")

        self.huim.logger.debug("Variables initialized")

        self.huim.new_edit_vars("settings", {"API_auto_update": None, "API_cooldown": None, "pet_API_cooldown": None, "compact_tolerance": None, "output_to_clipboard": None, "debug_mode": None, "color_palette": None}, self.edit_settings, 0.2, 0.3)
        self.md.create_custom_inputs_edit_vars(self.md.custom_inputs_edit_tree, "start")

        # Create widgets for controls menu and placing them
        self.creditLB = self.huim.create_label(frm=self.frames["controls"], txt=f"Minion Calculator V{self.version.get()}\nMade by Herodirk")
        self.creditLB.place(in_=self.stopB, x=-10, rely=0.5, y=-1, anchor="e")
        self.manualLB = self.huim.create_label(frm=self.frames["controls"], txt="Online Manual:\nCalculator Manual")
        self.manualLB.place(in_=self.creditLB, x=-10, rely=0.5, anchor="e")
        self.manualLB.bind("<Button-1>", lambda void_event: webbrowser.open(r"https://herodirk.github.io/"))
        self.API_creditLB = self.huim.create_label(frm=self.frames["controls"], txt="Bazaar data from Hypixel API,\nAH data from SkyCofl API")
        self.API_creditLB.place(in_=self.manualLB, x=-10, rely=0.5, anchor="e")
        self.API_creditLB.bind("<Button-1>", lambda click_event: webbrowser.open(r"https://api.hypixel.net/") if click_event.y < 18 else webbrowser.open(r"https://sky.coflnet.com/data"))

        self.text_outputB = tk.Button(self.frames["controls"], text='Text Output', command=lambda: self.text_output(markdown=False))
        self.markdown_outputB = tk.Button(self.frames["controls"], text='Markdown Output', command=lambda: self.text_output(markdown=True))
        self.calcB = tk.Button(self.frames["controls"], text='Calculate', command=lambda: self.calculate(True))
        self.statusC = tk.Canvas(self.frames["controls"], bg="green", width=10, height=10, borderwidth=0)
        self.addonsB = tk.Button(self.frames["controls"], text="Add-ons Menu", command=lambda: self.huim.toggle_switch("addons"))
        self.pricesB = tk.Button(self.frames["controls"], text="Update Prices", command=self.update_prices)
        self.settingsB = tk.Button(self.frames["controls"], text="Edit Settings", command=lambda: self.huim.edit_vars("settings"))
        self.custom_inputsB = tk.Button(self.frames["controls"], text="Custom Inputs", command=lambda: self.huim.edit_vars("custom_input_start"))
        # self.status, self.statusO = self.huim.def_output_var(frame=self.frames["controls"], dtype=str, L_text="Status:", initial="Ready")  # might use later

        controlsGrid = [self.calcB, self.statusC, self.text_outputB, self.markdown_outputB, self.pricesB, self.addonsB, self.settingsB, self.custom_inputsB]
        self.huim.fill_arr(controlsGrid, self.frames["controls"])

        # Create miscellaneous labels
        miniontitleLB = self.huim.create_label(frm=self.frames["inputs_minion_grid"], txt="\nMinion options")
        islandtitleLB = self.huim.create_label(frm=self.frames["inputs_minion_grid"], txt="\nIsland options")
        playertitleLB = self.huim.create_label(frm=self.frames["inputs_player_grid"], txt="Player options")
        wisdomLB = self.huim.create_label(frm=self.frames["inputs_player_grid"], txt="Wisdoms:")
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
                "beacon_fuel": None,
                "free_fuel_beacon": None,
                "crystal": None,
                "unique_farming_minions": None,
                "postcard": None,
            },
            "inputs_player_grid": {
                "player_label": [None, playertitleLB],
                "afk": None,
                "afkpet": None,
                "afkpet_lvl": None,
                "enchanted_clock": None,
                "special_layout": None,
                "player_harvests": None,
                "player_looting": None,
                "potato_accessory": None,
                "wisdom_label": [wisdomLB, self.huim.create_show_hide_toggle(wisdomLB, "wisdom_inputs", None)],
                "combat_wisdom": None,
                "mining_wisdom": None,
                "farming_wisdom": None,
                "fishing_wisdom": None,
                "foraging_wisdom": None,
                "alchemy_wisdom": None,
                "mayor": None,
                "levelingpet": None,
                "toggle_levelingpet_options": [None, self.huim.create_show_hide_toggle(self.levelingpet.widget[0], lambda: self.multiswitch("pet_leveling", None), None)],
                "taming": None,
                "falcon_attribute": None,
                "pet_exp_boost": None,
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
                "bazaar_flipper": None,
                "sell_form": None
            },
            "outputs_setup_grid": {
                "labels": [None, setupoutputsLB, setupprintLB],
                "setup_ID": [self.calculated_ID.widget[0], self.ID_container.widget[1], self.calculated_ID.widget[2]],
                "empty_time": None,
                "scaled_time": None,
                "actiontime": None,
                "fuelamount": None,
                "available_storage": None,
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
                "setupcost_breakdown_toggle": [None, self.huim.create_show_hide_toggle(self.setupcost.widget[0], "setup_cost_breakdown", None, "Toggle breakdown")],
                "setupcost_breakdown": None,
                "extracost": None,
                "optimal_tier_free_will": None,
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
        self.addons_list = {}
        for addon_function_key in external_add_ons.keys():
            if "__init__" in addon_function_key:
                external_add_ons[addon_function_key](self)
            else:
                self.addons_list[addon_function_key] = external_add_ons[addon_function_key]
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
        self.huim.def_switch("wisdom_inputs", widget_references=["combat_wisdom", "mining_wisdom", "farming_wisdom", "fishing_wisdom", "foraging_wisdom", "alchemy_wisdom"],
                            locations="grid", control=None, negate=False, initial=False)
        self.huim.def_switch("pet_leveling", widget_references=["taming", "pet_exp_boost", "beastmaster", "expsharepet", "expshareitem", "pets_levelled", "pet_profit", "falcon_attribute", "toucan_attribute", "used_pet_prices"],
                            locations="grid", control="None", negate=True, initial=False)
        self.huim.def_switch("exp_share_diana", widget_references=["expsharepetslot2", "expsharepetslot3"],
                            locations="grid", control="DianaTrue", negate=False, initial=False)
        self.huim.def_switch("NPC_Bazaar", widget_references="item_sell_loc",
                            locations="grid", control="Best (NPC/Bazaar)", negate=False, initial=True)
        self.huim.def_switch("infernofuel", widget_references=["inferno_grade", "inferno_distillate", "inferno_eyedrops"],
                            locations="grid", control="Inferno Minion Fuel", negate=False, initial=False)
        self.huim.def_switch("rising_celsius", widget_references="rising_celsius_override",
                            locations="grid", control="Inferno", negate=False, initial=False)
        self.huim.def_switch("beacon", widget_references=["beacon_fuel", "free_fuel_beacon"],
                            locations="grid", control="None", negate=True, initial=False)
        self.huim.def_switch("potato_accessory_switch", widget_references="potato_accessory",
                            locations="grid", control="PotatoTrue", negate=False, initial=False)
        self.huim.def_switch("bazaar_tax", widget_references="bazaar_flipper",
                            locations="grid", control=1, negate=False, initial=True)
        self.huim.def_switch("afking", widget_references=["afkpet", "afkpet_lvl", "enchanted_clock", "special_layout", "player_harvests", "player_looting"],
                            locations="grid", control=True, negate=False, initial=False)
        self.huim.def_switch("fuel_amount", widget_references="fuelamount",
                            locations="grid", control=-1, negate=True, initial=False)
        self.huim.def_switch("scaled_time_switch", widget_references=["scaled_time_amount", "scaled_time"],
                            locations="grid", control=True, negate=False, initial=False)
        self.huim.def_switch("optimal_free_will", widget_references="optimal_tier_free_will",
                            locations="grid", control=True, negate=False, initial=False)
        self.huim.def_switch("setup_cost_breakdown", widget_references="setupcost_breakdown",
                            locations="grid", control=None, negate=False, initial=False)
        self.huim.def_switch("cornucopia_bonus", widget_references="unique_farming_minions",
                            locations="grid", control="Cornucopia Crystal", negate=False, initial=False)
        self.huim.def_switch("addons", widget_references=self.frames["addons_main"],
                            locations={"anchor": "c", "relx": 0.5, "rely": 0.5, "relwidth": 0.7, "relheight": 0.8}, initial=False)
        
        # Show/Hide toggle buttons for large amount of extended options
        self.huim.create_show_hide_toggle(self.afk.widget[-1], "afking")
        self.huim.create_show_hide_toggle(self.beacon.widget[-1], "beacon")
        
        self.huim.logger.debug("Switches activated")

        self.dependent_variables = {
            "afkpet_rarity": "afkpet",
            "afkpet_lvl": "afkpet",
            "player_harvests": "afk",
            "empty_time": "scale_time",
            "optimal_tier_free_will": "free_will",
            "expshareitem": "expsharepet",
            "pets_levelled": "levelingpet",
            "used_pet_prices": "levelingpet",
            "pet_profit": "levelingpet",
            "levelingpet_rarity": "levelingpet",
            "expsharepet_rarity": "expsharepet",
            "expsharepetslot2_rarity": "expsharepetslot2",
            "expsharepetslot3_rarity": "expsharepetslot3",
            "beacon_fuel": "beacon"
        }
        # dependent variables are only active when another specified variable is not equivalent to 0,
        # this overrides forced outputs as inactive variables might not be equivalent to 0
        self.key_replace_bool = ["infusion", "free_will", "postcard"]  # variables that are booleans that need their display name outputted instead of the boolean value

        # Define text output order
        # The text output order is stored per line.
        # First dimension of dict exists of keys which are placed first on a line
        # These keys can serve as headers, or if the key is a variable key, the variable is outputted as {"display"}: {"value"}
        # the values are the second dimension of dict, the keys of which are sub-headers used for formatting, like adding line breaks
        # the values of the second dimension are array-like objects consisting of variable keys,
        # the variables are displayed differently depending on which array type it is:
        # set {}: only the values of the variables will be outputted (without any order)
        # list []: both the displays and the values of the variables will be outputted
        # tuple (): both displays and values are shown, the sub-header will be outputted in front of every variable
        self.standard_output_order = {
            "### ": {"$": ["amount"], "$x ": ["minion"], "$ t": ["miniontier"]},
            "**Minion Upgrades**": {
                "\n> Internal: ": {"fuel", "hopper", "upgrade1", "upgrade2"},
                "\n> External: ": {"chest", "beacon", "crystal", "postcard"},
                "\n-# ": ["unique_farming_minions", "custom_upgrade_toggle"],
                "\n> Permanent: ": {"infusion", "free_will"}
            },
            "Beacon Info": {"\n> ": ["beacon_fuel", "free_fuel_beacon"]},
            "Inferno Info": {"\n> ": ["inferno_grade", "inferno_distillate", "inferno_eyedrops", "rising_celsius_override"]},
            "afk": {"%\n> ": [["afkpet_rarity", "afkpet"]],
                    " lvl ": {"afkpet_lvl"},
                    "\n> ": ["enchanted_clock", "special_layout", "potato_accessory"]},
            "player_harvests": {"\n> ": ["player_looting"]},
            "Wisdoms": {"\n> ": ["combat_wisdom", "mining_wisdom", "farming_wisdom", "fishing_wisdom", "foraging_wisdom", "alchemy_wisdom"]},
            "mayor": None,
            "Leveling pet: ": {
                "%": [["levelingpet_rarity", "levelingpet"]],
                "\n> ": ["taming", "falcon_attribute", "pet_exp_boost", "beastmaster", "toucan_attribute", "expshareitem"],
                "%\n> Exp Share Pets: ": [["expsharepet_rarity", "expsharepet"], ["expsharepetslot2_rarity", "expsharepetslot2"], ["expsharepetslot3_rarity", "expsharepetslot3"]]
            },
            "used_pet_prices": None,
            "**Setup Information**\n": {
                "> ": ["calculated_ID"],
                "\n> ": ["actiontime", "fuelamount", "available_storage", "optimal_tier_free_will", "setupcost", "extracost"]
            },
            "setupcost_breakdown": None,
            "Market Info": {"\n> ": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper", "sell_form"]},
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
            if type(control) == str or str(self.miniontier.get()) not in self.md.calculator_data[self.minion.get()]["speed"].keys():
                self.miniontier.set(list(self.md.calculator_data[self.minion.get()]["speed"].keys())[-1])
            if type(control) == str:
                self.huim.toggle_switch("potato_accessory_switch", control + str(self.afk.get()))
                self.huim.toggle_switch("rising_celsius", control)
        elif multi_ID == "fuel":
            self.huim.toggle_switch("infernofuel", control)
            self.huim.toggle_switch("fuel_amount", self.md.calculator_data[self.input_options["fuel"][control]]["fuel_duration"])
        elif multi_ID == "afk":
            afkState = self.afk.get()
            self.huim.toggle_switch("afking", afkState)
            self.huim.toggle_switch("potato_accessory_switch", self.minion.get(False) + str(afkState))
        elif multi_ID == "pet_leveling":
            self.huim.toggle_switch("pet_leveling", control)
            mayor = self.mayor.get(False)
            pet_leveling_state = self.switches["pet_leveling"]["state"]
            self.huim.toggle_switch("exp_share_diana", mayor + str(pet_leveling_state))
            if control is not None:
                self.levelingpet_rarity.update_option_list(self.md.calculator_data[self.input_options["levelingpet"][control]]["pet_rarities"], True)
        elif multi_ID == "mayors":
            pet_leveling_state = self.switches["pet_leveling"]["state"]
            self.huim.toggle_switch("exp_share_diana", control + str(pet_leveling_state))
        return

    def load_template(self, template_name):
        """
        Handles the input from the template input.
        If "Load ID" is selected it sends the inputted ID to the decoder.
        If "Clean" is selected it sets every variable with "vtype" equal to "input" to its "initial".
        Otherwise it is a key from templateList which has as value a dict with variable keys and values.
        If the variable has a load function with switches, it runs that too.

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
        if template_name == "Load ID":
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
        return

    def data_to_text(self, var_key, calculation_data, output_switches, display=True, newline=False, markdown=True):
        if var_key not in calculation_data:
            return None
        # Special cases that can stop variables from outputting
        if var_key in self.dependent_variables:  # special case: dependent variables
            if calculation_data[self.dependent_variables[var_key]] in ["None", "0", "0.0", "", False]:
                return None
        elif var_key in ["expsharepetslot2", "expsharepetslot3"]:  # special case: slots only active during Diana
            if calculation_data["mayor"] != "Diana":
                return None
        elif var_key in ["inferno_grade", "inferno_distillate", "inferno_eyedrops"]:  # special case: fuel attributes only relevant for Inferno Minion Fuel
            if calculation_data["fuel"] != "Inferno Minion Fuel":
                return None
        elif var_key in ["rising_celsius_override"]:  # special case: Rising Celsius only applies to Inferno minions
            if calculation_data["minion"] != "Inferno":
                return None
        elif var_key in ["unique_farming_minions"]:  # special case: Unique Farming Minions only matters for Cornucopia Crystal
            if calculation_data["crystal"] != "Cornucopia Crystal":
                return None
        elif var_key == "scaled_time" and calculation_data["scale_time"] is False and output_switches["empty_time"] is False:  # special case: scale time is off and empty time is off
            return None

        # Output switch
        force = False  # force is a toggle for output variables that can be equivalent to 0 but still have to be outputted due to output switch
        output_switch_val = None
        if var_key in output_switches:
            output_switch_val = output_switches[var_key]
        if output_switch_val is False:
            return None
        elif output_switch_val is True:
            force = True

        # Getting data
        if var_key in self.key_replace_bool:  # special case: output key instead of the boolean
            if calculation_data[var_key] is True:
                data = f"{self.var_dict[var_key].get_display(True)}"
            else:
                return None  # no output if zero-like
        elif var_key == "special_layout" and "Special Layout" in calculation_data["notes"]:  # special case: special layout description instead of True
            data = f"{calculation_data["notes"]["Special Layout"]}"
        elif var_key == "custom_upgrade_toggle" and calculation_data[var_key]:
            data = f"Speed boost: {self.md.calculator_data["CUSTOM_UPGRADE"]["speed_boost"]}, Drop multiplier: {self.md.calculator_data["CUSTOM_UPGRADE"]["drop_multiplier"]}"
        elif self.var_dict[var_key].dtype in [dict, list]:
            data = calculation_data[var_key]
        elif self.var_dict[var_key].dtype in [int, float]:
            data = self.huim.reduced_number(calculation_data[var_key])
        else:
            data = f"{calculation_data[var_key]}"

        # Filter for zero-like
        if (data in ["None", "0", "0.0", "", "False"] or len(data) == 0) and force is False:
            return None

        # Text formatting
        return_str = ""
        if display:
            return_str += f"{self.var_dict[var_key].get_display(True)}: "
        value_formatting_function = lambda x: f"{x}"
        if markdown:
            value_formatting_function = lambda x: f"`{x}`"
        if type(data) in [list, dict]:
            return_str += "\n> "
            key_formatting_function = lambda x: x
            if self.var_dict[var_key].has_tag("item_ID_to_display"):
                key_formatting_function = lambda x: self.md.calculator_data[x]['display']
            elif var_key == "pets_levelled":
                key_formatting_function = lambda x: calculation_data[x + "_rarity"] + " " + calculation_data[x]
            elif var_key == "setupcost_breakdown":
                key_formatting_function = lambda x: self.var_dict[x].get_display(True)
            elif var_key == "used_pet_prices":
                key_formatting_function = lambda x: " ".join([self.md.calculator_data[y]["display"] for y in x.split(".")])
            formatted_list = []
            for list_key, list_val in data.items():
                if type(list_val) in [float, int]:
                    list_val = self.huim.reduced_number(list_val)
                formatted_list.append(f"{key_formatting_function(list_key)}: {value_formatting_function(list_val)}")
            return_str += ", ".join(formatted_list)
        elif markdown and var_key == "calculated_ID":
            return_str += f"||{data}||".replace("\\", r"\\")
        else:
            return_str += value_formatting_function(data)
        if newline:
            return_str += "\n"
        return return_str

    def text_output(self, calculation_data=None, output_switches=None, output_order=None, markdown=True, to_terminal=True):
        if calculation_data is None:
            calculation_data = self.huim.get_from_GUI(self.var_dict.keys())
            calculation_data.update(self.decode_id(calculation_data["calculated_ID"]))
        if output_switches is None:
            output_switches = {var_key: self.var_dict[var_key].get_output_switch() for var_key in self.var_dict}
        if output_order is None:
            output_order = self.standard_output_order
        crafted_string = ""
        for section_key in output_order:
            # Special cases where entire sections can be skipped
            if section_key == "Beacon Info" and calculation_data["beacon"] == 0:
                continue
            if section_key == "Inferno Info" and calculation_data["minion"] != "Inferno" and calculation_data["fuel"] != "Inferno Minion Fuel":
                continue
            if section_key == "Market Info" and ("bazaar_update_txt" in output_switches and output_switches["bazaar_update_txt"] is False):
                continue

            line_str = ""
            header = ""
            force_line = False
            if section_key in self.var_dict:
                header = self.data_to_text(section_key, calculation_data, output_switches, markdown=markdown)
                force_line = True
            else:
                header = section_key
                if not markdown:
                    header = header.replace("*", "")
                    header = header.replace("### ", "")
                    header = header.replace("-# ", "- ")
            if header is None:
                continue

            if type(output_order[section_key]) is dict:
                for sub_key, key_arr in output_order[section_key].items():
                    if not markdown:
                        sub_key = sub_key.replace("*", "")
                        sub_key = sub_key.replace("### ", "")
                        sub_key = sub_key.replace("-# ", "- ")
                    line_data = ""
                    if "$" in sub_key:  # value only: no display, no markdown
                        sub_key = sub_key[1:]
                        line_data += ", ".join(s for var_key in key_arr if (s := self.data_to_text(var_key, calculation_data, output_switches, display=False, markdown=False)) is not None)
                    elif "%" in sub_key:  # combined text: no display
                        sub_key = sub_key[1:]
                        line_data += ", ".join(t for key_group in key_arr if (t := " ".join(s for var_key in key_group if (s := self.data_to_text(var_key, calculation_data, output_switches, display=False, markdown=markdown)) is not None)) != "")
                    elif type(key_arr) == list:  # standard
                        line_data += ", ".join(s for var_key in key_arr if (s := self.data_to_text(var_key, calculation_data, output_switches, markdown=markdown)) is not None)
                    elif type(key_arr) == tuple:  # repeated sub_key
                        line_data += sub_key.join(s for var_key in key_arr if (s := self.data_to_text(var_key, calculation_data, output_switches, markdown=markdown)) is not None)
                    elif type(key_arr) == set:  # no display
                        line_data += ", ".join(s for var_key in key_arr if (s := self.data_to_text(var_key, calculation_data, output_switches, display=False, markdown=markdown)) is not None)
                    if line_data == "":
                        continue
                    line_str += sub_key + line_data
            if line_str != "" or force_line is True:
                crafted_string += "\n" + header + line_str
        if self.output_to_clipboard.get():
            self.clipboard_clear()
            self.clipboard_append(crafted_string)
        if to_terminal:
            self.huim.logger.info("\n" + crafted_string)
            return
        else:
            return crafted_string

    def construct_id(self, setup_data):
        """
        Generates the setup ID of the provided setup data.
        A setup ID consists of:\n
        - the version number of the minion calculator it was generated in\n
        - the index of the set value in "options" of each variable with "vtype" equal to "input" encoded in ASCII with an offset of 48\n
        - the set value surrounded by exclamation marks if a variable has an empty "options" list

        Returns
        -------
        setup_id : str
            Setup ID.

        """
        setup_id = self.version.get() + "!"
        for var_key in self.ID_order:
            if var_key not in setup_data:
                self.huim.logger.warning(f"{var_key} key not in setup_data, assuming default value")
                val = self.var_dict[var_key].initial
            elif self.var_dict[var_key].reverse_translation is not None:
                val = self.var_dict[var_key].reverse_translation[setup_data[var_key]]
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

    def decode_id(self, setup_id):
        """
        Generates a template structure for load_template() from a given setup ID.

        Parameters
        ----------
        setup_id : str
            Setup ID.

        Returns
        -------
        dict
            Template structure for load_template().

        """
        setup_data = {}
        end_ver = setup_id.find("!")
        if end_ver == -1:
            self.huim.logger.error("Invalid setup ID, could not find version number")
            return setup_data
        try:
            version = setup_id[0:end_ver]
        except Exception:
            self.huim.logger.error("Invalid setup ID, could not find version number")
            return setup_data
        ID_index = end_ver + 1
        if version != self.version.get():
            self.huim.logger.error("Invalid setup ID, Incompatible version")
            return setup_data
        try:
            for var_key in self.ID_order:
                var_options = self.var_dict[var_key].options
                if var_options is None:
                    if setup_id[ID_index] != "!":
                        self.huim.logger.error(f"did not find {var_key}")
                        return {}
                    end_val = setup_id.find("!", ID_index + 1)
                    setup_data[var_key] = self.var_dict[var_key].dtype(setup_id[ID_index + 1:end_val])
                    ID_index = end_val + 1
                elif len(var_options) > 79:
                    if setup_id[ID_index] != "!":
                        self.huim.logger.error(f"did not find {var_key}")
                        return {}
                    end_val = setup_id.find("!", ID_index + 1)
                    setup_data[var_key] = var_options[int(setup_id[ID_index + 1:end_val])]
                    ID_index = end_val + 1
                else:
                    setup_data[var_key] = var_options[ord(setup_id[ID_index]) - 48]
                    ID_index += 1
        except IndexError as error:
            self.huim.logger.error("Invalid setup ID, ID incomplete")
            return {}
        return setup_data

    def get_price(self, item_ID, setup_data, action="buy", location="bazaar", force=False):
        """
        Returns the price of an item from ID, transaction type and location of transaction.

        Parameters
        ----------
        item_ID : str
            Skyblock Item ID of which the price is needed.
        setup_data : dict
            needed setup data: bazaar_buy_type, bazaar_sell_type, bazaar_taxes, bazaar_flipper, mayor.
        action : str, optional
            Type of transaction. "buy" or "sell". The default is "buy".
        location : str, optional
            Location of the transaction, "npc", "bazaar", "ah", "custom". The default is "bazaar".
        force : bool, optional
            Toggle to force the location and action, if price point is not found, this function returns 0

        Returns
        -------
        float
            price of the item.
        """
        if item_ID not in self.md.calculator_data:
            self.huim.logger.error(item_ID + " not in calculator data")
            return 0
        if "prices" not in self.md.calculator_data[item_ID]:
            self.huim.logger.error("No prices found for " + item_ID)
            return 0

        price_point = location
        if price_point == "bazaar":
            if action == "buy":
                price_point = setup_data["bazaar_buy_type"]
            elif action == "sell":
                price_point = setup_data["bazaar_sell_type"]

        price = 0
        if price_point in self.md.calculator_data[item_ID]["prices"]:
            price = self.md.calculator_data[item_ID]["prices"][price_point]
        elif force:
            self.huim.logger.warning("no forced cost found for " + item_ID)
        else:
            for backup_price_point in ["sellPrice", "buyPrice", "ah", "custom", "npc", "warn"]:
                if backup_price_point in self.md.calculator_data[item_ID]["prices"]:
                    price = self.md.calculator_data[item_ID]["prices"][backup_price_point]
                    break
            if backup_price_point == "warn":
                self.huim.logger.warning("no cost found for " + item_ID)

        if location == "bazaar" and action == "sell":
            price = self.apply_bazaar_tax(price, setup_data)
        elif location == "ah" and action == "sell":
            price = self.apply_ah_tax(price, setup_data)
        elif location == "npc" and action == "buy":
            price = 2 * price
        return price

    def apply_bazaar_tax(self, price, setup_data):
        if not setup_data["bazaar_taxes"]:
            return price
        bazaar_tax = 0.0125 - 0.00125 * setup_data["bazaar_flipper"]
        bazaar_tax *= self.md.calculator_data[setup_data["mayor"]]["tax_multiplier"]
        return price * (1 - bazaar_tax)

    def apply_ah_tax(self, price, setup_data):
        if not setup_data["bazaar_taxes"]:
            return price
        if price > 10000000:
            starting_fee_tax = 0.025
        elif price > 1000000:
            starting_fee_tax = 0.02
        else:
            starting_fee_tax = 0.01
        return max(1000000, price * 0.99) - price * starting_fee_tax

    def get_speed_boosts(self, minion, upgrade_ids, upgrade_effects, afk_toggle, clock_override, setup_data):
        """
        Adds up speed boosts, uses the fact that booleans can be seen as 0 and 1 for false and true resp.

        Parameters
        ----------
        minion : str
            Minion type ID.
        upgrade_ids : list
            List of upgrade IDs
        upgrade_effects : dict
            Active upgrade effects sorted by type
        afk_toggle : boolean
            True if AFKing, False if offline
        clock_override : boolean
            True if using the Enchanted Clock
        setup_data : dict
            Needed setup data: amount, mayor, beacon, beacon_fuel, infusion, free_will, postcard, crystal,\n
            potato_accessory, afkpet, afkpet_rarity, afkpet_lvl, rising_celsius_override

        Returns
        -------
        float
            Total additive speed boost.
        """
        speed_boost = 0
        for upgrade in upgrade_ids:
            speed_boost += self.md.calculator_data[upgrade]["speed_boost"]
        speed_boost += self.md.calculator_data[setup_data["beacon"]]["speed_boost"] + self.md.calculator_data["MITHRIL_INFUSION"]["speed_boost"] * setup_data["infusion"]
        speed_boost += self.md.calculator_data["FREE_WILL"]["speed_boost"] * setup_data["free_will"] + self.md.calculator_data["POSTCARD"]["speed_boost"] * setup_data["postcard"]
        if setup_data["crystal"] != "NONE":
            if self.md.has_data_tag(minion, self.md.calculator_data[setup_data["crystal"]]["affected_minions"]):
                speed_boost += self.md.calculator_data[setup_data["crystal"]]["speed_boost"]
                if setup_data["crystal"] == "CORNUCOPIA_CRYSTAL":
                    speed_boost += setup_data["unique_farming_minions"]
        if setup_data["beacon"] != "NONE":
            speed_boost += self.md.calculator_data[setup_data["beacon_fuel"]]["speed_boost"]
        if minion == "INFERNO_MINION":
            if setup_data["rising_celsius_override"]:
                speed_boost += 180
            else:
                speed_boost += 18 * min(10, setup_data["amount"])
        for item_ID, effect_data in upgrade_effects["speed_bonus"].items():
            if self.md.has_data_tag(minion, effect_data["affected_minions"]):
                speed_boost += effect_data["amount"]
        if self.md.has_data_tag(minion, self.md.calculator_data[setup_data["mayor"]]["affected_minions"]):
            speed_boost += self.md.calculator_data[setup_data["mayor"]]["speed_boost"]
        if not (afk_toggle or clock_override):
            return speed_boost
        if self.md.has_data_tag(minion, self.md.calculator_data[setup_data["potato_accessory"]]["affected_minions"]):
            speed_boost += self.md.calculator_data[setup_data["potato_accessory"]]["speed_boost"]
        afkpet = setup_data["afkpet"]
        afkpet_rarity = setup_data["afkpet_rarity"]
        if self.md.has_data_tag(minion, self.md.calculator_data[afkpet]["affected_minions"]) and afkpet_rarity in self.md.calculator_data[afkpet]["boosting_pet"]:
            speed_boost += self.md.calculator_data[afkpet]["boosting_pet"][afkpet_rarity][0] + setup_data["afkpet_lvl"] * self.md.calculator_data[afkpet]["boosting_pet"][afkpet_rarity][1]
        return speed_boost

    def get_drop_multiplier(self, minion, upgrade_ids, afk_toggle, setup_data):
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
            Needed setup data: player_harvests, player_looting, mayor

        Returns
        -------
        float
            Total multiplicative drop multiplier.
        """
        drop_multiplier = 1
        if afk_toggle and setup_data["player_harvests"] and (minion not in ["FISHING_MINION", "PUMPKIN_MINION", "MELON_MINION"]):
            if self.md.has_data_tag(minion, "mob_minion"):
                drop_multiplier *= 1 + 15 * setup_data["player_looting"] / 100
            return drop_multiplier
        for upgrade in upgrade_ids:
            drop_multiplier *= self.md.calculator_data[upgrade]["drop_multiplier"]
            if afk_toggle and drop_multiplier > 1:
                # drop multiplier greater than 1 is rounded down while online, TODO: test again
                drop_multiplier = int(drop_multiplier)
        if self.md.has_data_tag(minion, self.md.calculator_data[setup_data["mayor"]]["affected_minions"]):
            drop_multiplier *= self.md.calculator_data[setup_data["mayor"]]["drop_multiplier"]
        return drop_multiplier
    
    def get_actions_per_harvest(self, minion, upgrade_ids, upgrade_effects, afk_toggle, setup_data, setup_notes):
        """
        Multiplies together drop multipliers.

        Parameters
        ----------
        minion : str
            Minion type ID.
        upgrade_effects : dict
            Active upgrade effects sorted by type
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
                        upgrade_effects["replacing"]["GRAVEL"] = { "FLINT": 1 }
                        setup_notes["Player Tools"] = "Assuming Player is using Flint Shovel"
                    if minion in ["ICE_MINION"]:
                        setup_notes["Player Tools"] = "Assuming Player is using Silk Touch"
            elif setup_data["special_layout"]:
                if minion in ["COBBLESTONE_MINION", "MYCELIUM_MINION", "ICE_MINION"]:
                    # cobblestone generator, regrowing mycelium, freezing water
                    actions_per_harvest = 1
                if minion == "FLOWER_MINION" and "THORNY_VINES" not in upgrade_ids:
                    # harvests through natural means: water flushing
                    actions_per_harvest = 1
                    # speedBonus -= 10  # only spawning has 10% action speed reduction, not confirmed yet.
                if minion in ["SAND_MINION", "RED_SAND_MINION", "GRAVEL_MINION"]:
                    # harvests through natural means: gravity
                    actions_per_harvest = 1
                    # speedBonus -= 10  # only spawning has 10% action speed reduction, not confirmed yet.
        return actions_per_harvest

    def update_loot_table(self, minion, upgrade_ids, upgrade_effects, afk_toggle, setup_data):
        """
        Applies changes to the loot tables of the minions depending on things like AFKing or special layouts.

        Parameters
        ----------
        minion : str
            Minion type ID.
        upgrade_ids : list
            List of upgrade IDs
        upgrade_effects : dict
            Active upgrade effects sorted by type
        afk_toggle : boolean
            True if AFKing, False if offline
        setup_data : dict
            Needed setup data: special_layout

        Returns
        -------
        None.
        """
        if self.md.has_data_tag(minion, "wood_minion"):
            if afk_toggle:
                # chopped trees have 4 blocks of wood, unknown why offline gives 3
                upgrade_effects["replacing"].update({
                    "LOG": {"LOG": 4 / 3},
                    "LOG:1": {"LOG:1": 4 / 3},
                    "LOG:2": {"LOG:2": 4 / 3},
                    "LOG_2:1": {"LOG_2:1": 4 / 3},
                    "LOG_2": {"LOG_2": 4 / 3},
                    "LOG:3": {"LOG:3": 4 / 3},
                })
        elif minion == "GRAVEL_MINION":
            if afk_toggle:
                # vanilla minecraft chance for gravel to become flint
                self.md.calculator_data[minion]["drops"]["GRAVEL"] = 0.9
                self.md.calculator_data[minion]["drops"]["FLINT"] = 0.1
            else:
                self.md.calculator_data[minion]["drops"]["GRAVEL"] = 1
                self.md.calculator_data[minion]["drops"]["FLINT"] = 0
        elif minion == "PUMPKIN_MINION":
            if not afk_toggle:
                upgrade_effects["replacing"].update({"PUMPKIN": {"PUMPKIN": 3}})
                # it just does this, idk, ask Hypixel
        elif minion == "SHEEP_MINION":
            if "ENCHANTED_SHEARS" in upgrade_ids:
                upgrade_effects["replacing"].update({"WOOL": {"WOOL": 0}})
        elif minion == "FLOWER_MINION":
            if afk_toggle and setup_data["special_layout"] and "THORNY_VINES" not in upgrade_ids:
                # tall flowers blocked by low ceiling
                upgrade_effects["replacing"].update({
                    "RED_ROSE:1": {"RED_ROSE:1": 11 / 8},
                    "RED_ROSE:2": {"RED_ROSE:2": 11 / 8},
                    "RED_ROSE:3": {"RED_ROSE:3": 11 / 8},
                    "RED_ROSE:4": {"RED_ROSE:4": 11 / 8},
                    "RED_ROSE:5": {"RED_ROSE:5": 11 / 8},
                    "RED_ROSE:6": {"RED_ROSE:6": 11 / 8},
                    "RED_ROSE:7": {"RED_ROSE:7": 11 / 8},
                    "RED_ROSE:8": {"RED_ROSE:8": 11 / 8},
                    "DOUBLE_PLANT:1": {},
                    "DOUBLE_PLANT:4": {},
                    "DOUBLE_PLANT:5": {}
                })
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
        base_speed = self.md.calculator_data[minion]["speed"][str(minion_tier)]
        seconds_per_action = base_speed / (1 + speed_boost / 100)
        if minion_fuel_id == "INFERNO_FUEL":
            seconds_per_action /= 1 + self.md.inferno_fuel_data["grades"][setup_data["inferno_grade"]]
        self.huim.logger.debug(f"Base action time: {base_speed}")
        self.huim.logger.debug(f"Unrounded action time: {seconds_per_action}")
        seconds_per_action = round(seconds_per_action * 20) / 20
        if seconds_per_action < 0.05:
            seconds_per_action = 0.05
        return seconds_per_action

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
        empty_time_str = scaled_time_str = f"{self.huim.reduced_number(setup_data["empty_time_amount"])} {setup_data["empty_time_unit"]}"
        timeratio = 1
        if setup_data["scale_time"]:
            scaled_time_seconds = self.huim.time_number(setup_data["scaled_time_unit"], setup_data["scaled_time_amount"], seconds_per_action * actions_per_harvest)
            scaled_time_str = f"{self.huim.reduced_number(setup_data["scaled_time_amount"])} {setup_data["scaled_time_unit"]}"
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

    def get_upgrade_info(self, minion_fuel_id, drops_list, setup_data):
        """
        Compiles upgrades and upgrade effects
        
        Parameters
        ----------
        minion_fuel_id : str
            Minion fuel ID
        drops_list : dict
            dict containing all drops of the setup
        setup_data : dict
            needed setup data: upgrade1, upgrade2, custom_upgrade_toggle

        Returns
        -------
        list, dict
            upgrade_ids: list of IDs of the used upgrades\n
            upgrade_effects: dict of active upgrade effects sorted by type            
        """
        upgrade_effects = {
            "replacing": {},  # old item: {new item: ratio = (new item / old item)}, or {} (empty dict) to remove old item
            "spreading": {},  # item: average per drop
            "adding": {},  # "ID": {item: amount}
            "cooldown": {},  # "ID": {items: {item: amount}, online_cooldown: seconds, offline_cooldown: seconds}
            "speed_bonus": {},  # "ID": {amount: +%, affected_minions: [affected minion tags and IDs]}
            "compacting": {},  # "ID": {item: compacting recipes}
            "expanding": 0
        }
        upgrade_ids = [minion_fuel_id, setup_data["upgrade1"], setup_data["upgrade2"]]
        if setup_data["custom_upgrade_toggle"]:
            upgrade_ids.append("CUSTOM_UPGRADE")
        for upgrade in upgrade_ids:
            if "upgrade_effects" not in self.md.calculator_data[upgrade]:
                continue
            for effect_type, upgrade_effect_data in self.md.calculator_data[upgrade]["upgrade_effects"].items():
                if "replacing" == effect_type:
                    upgrade_effects["replacing"].update(upgrade_effect_data)
                elif "spreading" == effect_type:
                    for item, amount in upgrade_effect_data.items():
                        upgrade_effects["spreading"][item] = amount
                        drops_list[item] = 0
                elif "expanding" == effect_type:
                    upgrade_effects[effect_type] += upgrade_effect_data
                else:
                    upgrade_effects[effect_type][upgrade] = upgrade_effect_data
        return upgrade_ids, upgrade_effects
    
    def add_drops(self, item, amount, drops_list, spreading_info=None, replacing_info=None):
        """
        Adds drops to drops_list, automatically applies spreading_info and replace_info if given
        
        :param item: str, item ID of the drop
        :param amount: float, amount of the drop
        :param drops_list: dict, all drops of the setup
        :param spreading_info: dict, the average amount of a spreading item generated per drop
        :param replace_info: dict, the replacements of original item ID as key and final item ID as value
        """
        if replacing_info is not None and item in replacing_info:
            for new_item, ratio in replacing_info[item].items():
                self.add_drops(new_item, amount * ratio, drops_list, spreading_info, None)
            return
        if item not in drops_list:
            drops_list[item] = 0
        drops_list[item] += amount
        if spreading_info is not None:
            for spreading_item, spreading_average in spreading_info.items():
                drops_list[spreading_item] += amount * spreading_average
        return

    def get_base_drops(self, drops_list, upgrade_effects, minion, harvests_per_time, drop_multiplier):
        """
        Gets generated base drops of the setup and adds them to drops_list
        
        :param drops_list: dict, all drops of the setup
        :param upgrade_effects: dict, active upgrade effects sorted by type
        :param minion: str, minion type ID
        :param harvests_per_time: float, amount of harvests between empties
        :param drop_multiplier: float, total drop multiplier
        """
        for item, amount in self.md.calculator_data[minion]["drops"].items():
            self.add_drops(item, harvests_per_time * amount * drop_multiplier, drops_list, upgrade_effects["spreading"], upgrade_effects["replacing"])
        return

    def get_upgrade_drops(self, drops_list, upgrade_effects, minion, minion_tier, drop_multiplier, upgrade_ids, harvests_per_time, afk_toggle, empty_time_seconds, seconds_per_action, setup_data):
        """
        Gets generated drops from upgrades of the setup and adds them to the drops_list
        
        :param drops_list: dict, all drops of the setup
        :param upgrade_effects: dict, active upgrade effects sorted by type
        :param minion: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param drop_multiplier: float, total drop multiplier
        :param upgrade_ids: list, upgrade IDs
        :param harvests_per_time: float, amount of harvests between empties
        :param afk_toggle: boolean, True if AFKing, False if offline
        :param empty_time_seconds: float, seconds between empties
        :param seconds_per_action: float, seconds per minion action
        :param setup_data: dict, needed setup data: setup data for self.get_drop_multiplier
        """
        for upgrade, effect_data in upgrade_effects["adding"].items():
            # adding upgrades are like Corrupt Soils
            specific_multiplier = 1
            if afk_toggle:
                if "CORRUPT_SOIL" == upgrade:
                    if "afkcorrupt" in self.md.calculator_data[minion]:
                        # Certain mob minions get more corrupt drops when afking
                        # It is not a constant multiplier, it is equivalent in chance to the main drops of the minion
                        specific_multiplier = self.md.calculator_data[minion]["afkcorrupt"]
                    if minion == "CHICKEN_MINION" and "ENCHANTED_EGG" not in upgrade_ids:
                        # Online Chicken minion without Enchanted Egg does not make corrupt drops
                        specific_multiplier = 0
                if "ENCHANTED_EGG" == upgrade:
                    # Enchanted Eggs make one laid egg and one egg on kill while AFKing
                    # the egg on spawn is affected by drop multipliers and spreadings
                    self.add_drops("EGG", harvests_per_time * drop_multiplier, drops_list, upgrade_effects["spreading"])
                for item, amount in effect_data.items():
                    self.add_drops(item, harvests_per_time * amount * specific_multiplier, drops_list)
            else:
                for item, amount in effect_data.items():
                    self.add_drops(item, harvests_per_time * amount * specific_multiplier, drops_list, upgrade_effects["spreading"])
        for upgrade, effect_data in upgrade_effects["cooldown"].items():
            # cooldown upgrades are like Soulflow Engines
            # formula for effective_cooldown still in research
            specific_multiplier = 1
            if afk_toggle and upgrade == "LESSER_SOULFLOW_ENGINE" and "SOULFLOW_ENGINE" in upgrade_ids:
                continue  # Soulflow Engine overrides Lesser Soulflow Engine while online
            if afk_toggle:
                effective_cooldown = 2 * seconds_per_action * (1 + math.floor(math.ceil(effect_data["online_cooldown"] / seconds_per_action) / 2))
            else:
                effective_cooldown = effect_data["offline_cooldown"]
            if "SOULFLOW_ENGINE" == upgrade and minion == "VOIDLING_MINION":
                specific_multiplier = 1 + 0.03 * minion_tier  # correct most likely, needs testing
            for cooldown_item, cooldown_amount in effect_data["items"].items():
                if cooldown_item == "RAW_SOULFLOW":
                    specific_multiplier *= self.get_drop_multiplier(minion, [upgrade_id for upgrade_id in upgrade_ids if upgrade_id not in ["LESSER_SOULFLOW_ENGINE", "SOULFLOW_ENGINE"]], afk_toggle, setup_data)
                self.add_drops(cooldown_item, specific_multiplier * cooldown_amount * empty_time_seconds / effective_cooldown, drops_list)
        return

    def get_inferno_drops(self, drops_list, upgrade_effects, minion, minion_tier, minion_fuel, drop_multiplier, harvests_per_time, empty_time_seconds, afk_toggle, setup_data):
        """
        Gets generated inferno fuel drops and adds them to drops_list.
        https://wiki.hypixel.net/Inferno_Minion_Fuel
        
        :param drops_list: dict, all drops of the setup
        :param upgrade_effects: dict, active upgrade effects sorted by type
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
        distilate_item = self.md.inferno_fuel_data["distilates"][distilate][0]
        amount_per = self.md.inferno_fuel_data["distilates"][distilate][1]
        distillate_harvests = (harvests_per_time * 4) / 5
        if afk_toggle:
            self.get_base_drops(drops_list, upgrade_effects, minion, - distillate_harvests, drop_multiplier)
        else:
            self.get_base_drops(drops_list, {"spreading": None, "replacing": upgrade_effects["replacing"]}, minion, - distillate_harvests, drop_multiplier)
        self.add_drops(distilate_item, distillate_harvests * amount_per, drops_list)

        # Hypergolic drops
        if setup_data["inferno_grade"] == "HYPERGOLIC_GABAGOOL":  # hypergolic fuel stuff
            multiplier = 1
            if setup_data["inferno_eyedrops"] is True:  # Capsaicin Eyedrops
                multiplier = 1.3
            for item, chance in self.md.inferno_fuel_data["drops"].items():
                if item == "INFERNO_APEX" and minion_tier >= 10:  # Apex Minion perk
                    chance *= 2
                self.add_drops(item, multiplier * chance * harvests_per_time, drops_list)
            self.add_drops("HYPERGOLIC_IONIZED_CERAMICS", empty_time_seconds / self.md.calculator_data[minion_fuel]["fuel_duration"], drops_list)

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
        self.md.calculator_data["INFERNO_FUEL"]["prices"]["custom"] = costPerInfernofuel
        # the fuel cost is put into the item data to be used later in the general fuel cost calculator
        return

    def apply_compactor(self, drops_list, compacting_list):
        """
        Applies given compacting rules to the drops list and returns a list of all compacted items
        
        :param drops_list: dict, all drops of the setup
        :param compactor_list: dict of the form {item: `compacting recipe name`, ...}

        :return compacted_items: list, IDs of items that got compacted
        """
        compacted_items = []
        compactables = list(drops_list.keys())
        while compactables:
            item = compactables.pop(0)
            if item not in compacting_list:
                continue
            compacting_data = self.md.calculator_data[item]["compacting"][compacting_list[item]]
            amount = drops_list[item]
            per_compacted = compacting_data["per"]
            if amount < per_compacted:
                continue
            compacted_name = compacting_data["makes"]
            compacted_amount = int(amount / per_compacted)
            if "amount" in compacting_data:
                compacted_amount *= compacting_data["amount"]
            left_over = amount % per_compacted
            drops_list[item] = left_over
            drops_list[compacted_name] = compacted_amount
            compacted_items.append({"from": item, **compacting_data})
            if compacted_name in compacting_list:
                compactables.append(compacted_name)
        return compacted_items

    def get_compacted_drops(self, drops_list, upgrade_effects):
        """
        Gets compacted drops, returns a list of all compacted items
        
        :param drops_list: dict, all drops of the setup
        :param upgrade_effects: dict, active upgrade effects sorted by type
        :return compacted_items: list, IDs of items that got compacted
        """
        compacted_items = []
        for compacting_list in upgrade_effects["compacting"].values():
            compacted_items.extend(self.apply_compactor(drops_list, compacting_list))
        return compacted_items

    def get_available_storage(self, minion, minion_tier, setup_data):
        """
        Gets amount of available storage measured in slots
        
        :param minion: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param setup_data: needed setup data: chest
        :return available_storage: available storage measured in slots
        """
        available_storage = self.md.calculator_data[setup_data["chest"]]["storage_slots"]
        if "storage" in self.md.calculator_data[minion] and str(minion_tier) in self.md.calculator_data[minion]["storage"]:
            available_storage += self.md.calculator_data[minion]["storage"][str(minion_tier)]
        else:
            available_storage += self.md.standard_storage[minion_tier]
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
            hopper_multiplier = self.md.calculator_data[setup_data["hopper"]]["hopper_selling_rate"]
        return sellto, hopper_multiplier
    
    def get_item_profit(self, sell_location, hopper_multiplier, drops_list, setup_data):
        """
        Makes a list of all prices and takes the one that matches the choice of sell_location or takes the maximum, while keeping track where items get sold
        
        :param sell_location: str, general sell location
        :param hopper_multiplier: hopper profit multiplier
        :param drops_list: dict, all drops of the setup
        :param setup_data: dict, needed setup data: sell_form, setup data for self.get_price
        :return item_profit: float, total profit from drops
        :return per_item_profit: dict, profit per item ID
        :return per_item_sell_location: dict, final sell location per item ID
        """""
        item_profit = 0.0
        per_item_profit = {}
        per_item_sell_location = {}
        item_prices = {}
        for itemtype, amount in drops_list.items():
            sell_itemtype = itemtype
            price_ratio = 1
            if setup_data["sell_form"] != 0:
                for compacted_tier in range(1, setup_data["sell_form"] + 1):
                    if self.md.calculator_data[sell_itemtype]["compact_tier"] >= compacted_tier:
                        continue
                    if "compacting" in self.md.calculator_data[sell_itemtype] and "compact" in self.md.calculator_data[sell_itemtype]["compacting"]:
                        compacting_data = self.md.calculator_data[sell_itemtype]["compacting"]["compact"]
                        effective_per_compacted = compacting_data["per"]
                        if "amount" in compacting_data:
                            effective_per_compacted /= compacting_data["amount"]
                        price_ratio /= effective_per_compacted
                        sell_itemtype = compacting_data["makes"]
            item_prices.clear()
            item_prices["NPC"] = self.get_price(sell_itemtype, setup_data, "sell", "npc")
            item_prices["bazaar"] = self.get_price(sell_itemtype, setup_data, "sell", "bazaar")
            # item_prices["custom"] = self.get_price(sell_itemtype, setup_data, "sell", "custom", force=True)  # might use later
            if sell_location in item_prices:
                per_item_sell_location[itemtype] = sell_location
            else:
                per_item_sell_location[itemtype] = max(item_prices, key=item_prices.get)
            final_price = item_prices[per_item_sell_location[itemtype]] * price_ratio
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
            if "xp" not in self.md.calculator_data[itemtype]:
                continue
            for xptype, value in self.md.calculator_data[itemtype]["xp"].items():
                if value == 0:
                    continue
                if xptype not in skill_xp:
                    skill_xp[xptype] = 0
                skill_xp[xptype] += amount * value * (1 + setup_data[xptype + "_wisdom"] / 100)
        self.huim.deepmultiply(skill_xp, self.md.calculator_data[mayor]["xp_multiplier"])
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
            if cost - compact_cost > self.compact_tolerance.get():
                over_compacting.append(self.md.calculator_data[item]['display'])
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
            Pet for the calculation, must be a pet from calculator data.
        xp_type : str
            Type of skill XP.
        setup_data : dict
            needed setup data: taming, beastmaster, pet_exp_boost, mayor, falcon_attribute
        exp_share : bool
            Toggle for if the xp is given through Exp Share. Default is False.

        Returns
        -------
        float
            Combined pet xp boosts of all boosts except pet item
        float
            pet xp boost of pet item

        """
        pet_xp_boost = 1
        if self.md.calculator_data[pet]["pet_type"] != "all" and self.md.calculator_data[pet]["pet_type"] != xp_type:
            if xp_type in ["alchemy", "enchanting"]:
                pet_xp_boost = 1 / 12
            else:
                pet_xp_boost = 1 / 3
        if xp_type in ["mining", "fishing"]:
            pet_xp_boost *= 1.5
        if exp_share:
            return pet_xp_boost
        pet_xp_boost *= (1 + setup_data["taming"] / 100) * (1 + setup_data["beastmaster"] / 100)
        if self.md.calculator_data[setup_data["pet_exp_boost"]]["exp_boost_type"] in [xp_type, "all"] and not self.md.has_data_tag(pet, "dragon_egg_pet"):
            pet_item = 1 + self.md.calculator_data[setup_data["pet_exp_boost"]]["exp_boost_amount"] / 100
        else:
            pet_item = 1
        if setup_data["mayor"] == "MAYOR_DIANA":
            pet_xp_boost *= 1.35
        if pet == "PET_REINDEER":
            pet_xp_boost *= 2
        if xp_type in ["combat"] and setup_data["falcon_attribute"] != 0:
            pet_xp_boost *= (1 + setup_data["falcon_attribute"] / 100)
        return pet_xp_boost, pet_item

    def get_pets_levelled(self, skill_xp, mayor, setup_data):
        """
        Pet levelling calculations: https://wiki.hypixel.net/Pets#Leveling,\n
        for Dragon pets: an extra multiplier to take that pet items cannot be applied to Dragon Eggs into account,\n
        this gives an average amount of pets levelled, for exact amounts, use the add-on Exact Pet Levelling.\n
        Decimal amounts of levelled pets is the fraction of total pet xp for max level, not pet level.

        :param skill_xp: dict, gained skill xp per type
        :param mayor: str, mayor
        :param setup_data: needed setup data: levelingpet, levelingpet_rarity, expsharepet, expsharepet_rarity, expsharepetslot2, expsharepetslot2_rarity, expsharepetslot3, expsharepetslot3_rarity, taming, toucan_attribute, expshareitem, pet_exp_boost, beastmaster, setup data for self.get_price
        :return setup_pets: dict, pet slot var key as key, dict as value with pet name, pet xp and amount of levelled pets        
        """
        main_pet = setup_data["levelingpet"]
        if main_pet == "NONE":
            return {}

        # Creating setup_pets
        setup_pets = { "levelingpet": { "pet": main_pet, "rarity": setup_data["levelingpet_rarity"], "pet_xp": {}, "levelled_pets": 0.0 } }
        for var_key in ["expsharepet", "expsharepetslot2", "expsharepetslot3"]:
            if setup_data[var_key] == "NONE" or (mayor != "MAYOR_DIANA" and var_key in ["expsharepetslot2", "expsharepetslot3"]):
                continue
            setup_pets[var_key] = { "pet": setup_data[var_key], "rarity": setup_data[var_key + "_rarity"], "pet_xp": { "exp_share": 0.0 }, "levelled_pets": 0.0 }

        # Main pet
        main_pet_xp = setup_pets["levelingpet"]["pet_xp"]
        dragon_pet_multiplier = lambda pet_item: 1
        dragon_pet_xp_lvl_200 = self.md.calculator_data["DRAGON"]["max_lvl_pet_xp_amount"]
        dragon_pet_xp_lvl_100 = self.md.calculator_data["LEGENDARY"]["max_lvl_pet_xp_amount"]
        if self.md.has_data_tag(main_pet, "dragon_pet"):
            dragon_pet_multiplier = lambda pet_item: dragon_pet_xp_lvl_200 / ( dragon_pet_xp_lvl_200 + dragon_pet_xp_lvl_100 * (pet_item - 1))
        for skill, amount in skill_xp.items():
            pet_xp_boost, xp_boost_pet_item = self.get_pet_xp_boosts(main_pet, skill, setup_data)
            main_pet_xp[skill] = amount * pet_xp_boost * xp_boost_pet_item * dragon_pet_multiplier(xp_boost_pet_item)

        # Exp Share
        exp_share_boost = 0.2 * setup_data["taming"] + 10 * (mayor == "MAYOR_DIANA") + setup_data["toucan_attribute"]
        exp_share_item = 15 * setup_data["expshareitem"]
        for pet_slot, pet_info in setup_pets.items():
            if pet_slot == "levelingpet":
                continue
            exp_share_pet = pet_info["pet"]
            dragon_pet_multiplier = 1
            if self.md.has_data_tag(exp_share_pet, "dragon_pet"):
                if exp_share_boost == 0:
                    continue
                dragon_pet_multiplier = dragon_pet_xp_lvl_200 / ( dragon_pet_xp_lvl_200 + dragon_pet_xp_lvl_100 * (exp_share_item / exp_share_boost))
            for skill, amount in main_pet_xp.items():
                pet_xp_boost = self.get_pet_xp_boosts(exp_share_pet, skill, setup_data, True)
                pet_info["pet_xp"]["exp_share"] += amount * ((exp_share_boost + exp_share_item * (not self.md.has_data_tag(exp_share_pet, "dragon_egg_pet"))) / 100) * pet_xp_boost * dragon_pet_multiplier

        # Calculate levelled pets
        for pet_slot, pet_info in setup_pets.items():
            if self.md.has_data_tag(pet_info["pet"], "dragon_pet"):
                max_lvl_pet_xp = dragon_pet_xp_lvl_200
            elif self.md.has_data_tag(pet_info["pet"], "hatched_dragon_pet"):
                max_lvl_pet_xp = dragon_pet_xp_lvl_200 - dragon_pet_xp_lvl_100
            else:
                max_lvl_pet_xp = self.md.calculator_data[pet_info["rarity"]]["max_lvl_pet_xp_amount"]
            pet_info["levelled_pets"] = sum(pet_info["pet_xp"].values()) / max_lvl_pet_xp
        return setup_pets

    def get_pet_profit(self, setup_pets, setup_data):
        """
        Get total profit from the levelled pets
        
        :param setup_pets: dict, pet slot var key as key, dict as value with pet name, pet xp and amount of levelled pets
        :param setup_data: needed setup data: expshareitem, pet_exp_boost, setup data for self.get_price
        :return pet_profit: float, total profit from pets
        :return used_pet_prices: dict, pet name as key, string as value with lvl 1 price and max lvl price 
        """
        pet_profit = 0.0
        used_pet_prices = {}
        super_scrubber_price = self.get_price("SUPER_SCRUBBER", setup_data, "buy", "custom", True)
        for pet_slot, pet_info in setup_pets.items():
            combined_pet_id = pet_info['rarity'] + "." + pet_info["pet"]
            if pet_info['rarity'] not in self.md.calculator_data[pet_info["pet"]]["pet_prices"]:
                if combined_pet_id not in used_pet_prices:
                    used_pet_prices[combined_pet_id] = f"Price not found"
            else:
                pet_price_max = self.md.calculator_data[pet_info["pet"]]["pet_prices"][pet_info["rarity"]]["max"]
                pet_price_min = self.md.calculator_data[pet_info["pet"]]["pet_prices"][pet_info["rarity"]]["min"]
                pet_profit += pet_info["levelled_pets"] * (self.apply_ah_tax(pet_price_max, setup_data) - pet_price_min)
                if combined_pet_id not in used_pet_prices:
                    used_pet_prices[combined_pet_id] = f"{self.huim.reduced_number(pet_price_min)} - {self.huim.reduced_number(pet_price_max)} ({self.huim.reduced_number(self.apply_ah_tax(pet_price_max, setup_data))})"
            if self.md.has_data_tag(pet_info["pet"], "dragon_egg_pet"):
                continue
            if pet_slot == "levelingpet" and (main_pet_item := setup_data["pet_exp_boost"]) != "NONE":
                pet_profit -= pet_info["levelled_pets"] * (self.md.calculator_data[self.md.calculator_data[main_pet_item]["rarity"]]["pet_item_scrub_cost"] + super_scrubber_price)
            if pet_slot != "levelingpet" and setup_data["expshareitem"]:
                pet_profit -= pet_info["levelled_pets"] * (self.md.calculator_data[self.md.calculator_data["PET_ITEM_EXP_SHARE"]["rarity"]]["pet_item_scrub_cost"] + super_scrubber_price)
        return pet_profit, used_pet_prices

    def get_finite_fuel_cost(self, minion_amount, minion_fuel, empty_time_seconds, setup_data):
        """
        get cost per empty_time for the finite fuel and beacon fuel
        
        :param minion_amount: int, minion amount
        :param minion_fuel: str, ID of minion fuel
        :param empty_time_seconds: float, time between empties in seconds
        :param setup_data: needed setup data: beacon, beacon_fuel, free_fuel_beacon, setup data for self.get_price
        """
        fuel_cost = 0.0
        needed_fuel = 0.0
        if setup_data["beacon"] != "NONE":
            cost_per_crystal = self.get_price(setup_data["beacon_fuel"], setup_data, "buy", "bazaar")
            fuel_cost += empty_time_seconds * cost_per_crystal / self.md.calculator_data[setup_data["beacon_fuel"]]["fuel_duration"] * int(not (setup_data["free_fuel_beacon"]))
        if self.md.calculator_data[minion_fuel]["fuel_duration"] != -1:
            cost_per_fuel = self.get_price(minion_fuel, setup_data, "buy", "bazaar")
            needed_fuel = minion_amount * empty_time_seconds / self.md.calculator_data[minion_fuel]["fuel_duration"]
            fuel_cost += needed_fuel * cost_per_fuel
        return fuel_cost, needed_fuel

    def get_setup_cost(self, minion_type, minion_tier, minion_amount, minion_fuel, setup_pets, setup_data):
        """
        Gets cost of all parts of the setup
        
        :param minion_type: str, minion type ID
        :param minion_tier: int, minion tier, 1 to 12
        :param minion_amount: int, minion amount
        :param minion_fuel: str, ID of minion fuel
        :param setup_data: needed setup data: hopper, upgrade1, upgrade2, infusion, free_will, chest, beacon, crystal, postcard, potato_accessory, pet_exp_boost, expshareitem, toucan_attribute, falcon_attribute, setup data for self.get_price
        :return total_cost: float, total setup cost
        :return extra_cost: str, total extra cost 
        :return cost_per_part: dict, cost per setup part
        """
        cost_per_part = {}
        extra_cost = "None"

        # Single minion cost
        cost_cache = {}
        tiered_coin_cost = {}
        tiered_extra_cost = {}
        tier_loop = range(1, minion_tier + 1)
        for tier in tier_loop:
            tiered_coin_cost[tier] = 0.0
            for item, amount in self.md.calculator_data[minion_type]["minion_costs"][str(tier)].items():
                if item not in self.md.calculator_data:
                    if tier not in tiered_extra_cost:
                        tiered_extra_cost[tier] = {}
                    tiered_extra_cost[tier][item] = amount
                    continue
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
            extra_cost = ", ".join([f"{amount * minion_amount} {material.replace('_', ' ').title()}" for material, amount in tiered_extra_cost[minion_tier].items()])
        cost_per_part["minion"] = tiered_coin_cost[minion_tier]

        # Infinite fuel cost
        if minion_fuel != "NONE" and self.md.calculator_data[minion_fuel]["fuel_duration"] == -1:
            cost_per_part["fuel"] = self.get_price(minion_fuel, setup_data, "buy", "bazaar")

        # Hopper cost
        if setup_data["hopper"] != "NONE":
            cost_per_part["hopper"] = self.get_price(setup_data["hopper"], setup_data, "buy", "bazaar")

        # Internal minion upgrades cost
        if setup_data["upgrade1"] != "NONE":
            cost_per_part[f"upgrade1"] = self.get_price(setup_data["upgrade1"], setup_data, "buy", "bazaar")
        if setup_data["upgrade2"] != "NONE":
            cost_per_part[f"upgrade2"] = self.get_price(setup_data["upgrade2"], setup_data, "buy", "bazaar")

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
        postcard_price = self.get_price("POSTCARD", setup_data, "sell", "ah")
        free_will_optimal_tier = 0
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
            free_will_optimal_tier = min(tiered_free_will, key=tiered_free_will.get)
            cost_per_part["free_will"] = tiered_free_will[free_will_optimal_tier]

        # Storage Chest cost
        if setup_data["chest"] != "NONE":
            cost_per_part["chest"] = self.get_price(setup_data["chest"], setup_data, "buy", "bazaar")
        
        # multiply by minion amount
        self.huim.deepmultiply(cost_per_part, minion_amount)

        # Beacon cost
        if setup_data["beacon"] != "NONE":
            cost_per_part["beacon"] = self.get_price(setup_data["beacon"], setup_data, "buy", "bazaar")

        # Floating Crystal cost
        if setup_data["crystal"] != "NONE":
            cost_per_part["crystal"] = self.get_price(setup_data["crystal"], setup_data, "buy", "bazaar")

        # Postcard cost
        if setup_data["postcard"]:
            cost_per_part["postcard"] = final_postcard_cost

        # Potato Talisman cost
        if setup_data["potato_accessory"] != "NONE":
            cost_per_part["potato_accessory"] = self.get_price(setup_data["potato_accessory"], setup_data, "buy", "ah")

        # Pet Item costs
        for pet_slot in setup_pets.keys():
            if self.md.has_data_tag(setup_pets[pet_slot]["pet"], "dragon_egg_pet"):
                continue
            if pet_slot == "levelingpet":
                cost_per_part["pet_exp_boost"] = self.get_price(setup_data["pet_exp_boost"], setup_data, "buy", "ah")
            elif setup_data["expshareitem"]:
                if "expshareitem" not in cost_per_part:
                    cost_per_part["expshareitem"] = 0
                cost_per_part["expshareitem"] += self.get_price("PET_ITEM_EXP_SHARE", setup_data, "buy", "bazaar")

        # Attribute costs
        if setup_data["toucan_attribute"] != 0:
            cost_per_part["toucan_attribute"] = self.md.calculator_data["EPIC"]["attribute_shards"][str(setup_data["toucan_attribute"])] * self.get_price("SHARD_TOUCAN", setup_data, "buy", "bazaar")
        if setup_data["falcon_attribute"] != 0:
            cost_per_part["falcon_attribute"] = self.md.calculator_data["RARE"]["attribute_shards"][str(setup_data["falcon_attribute"])] * self.get_price("SHARD_FALCON", setup_data, "buy", "bazaar")


        total_cost = sum(cost_per_part.values())
        return total_cost, extra_cost, free_will_optimal_tier, cost_per_part

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

        # Get inputs if none are given
        if setup_data is None:
            setup_data = self.huim.get_from_GUI(self.ID_order)

        # auto update API
        if self.API_auto_update.get():
            self.update_prices(cooldown_warning=False, in_gui=inGUI)
            for pet_slot in ["levelingpet", "expsharepet", "expsharepetslot2", "expsharepetslot3"]:
                self.update_pet_price(setup_data[pet_slot], setup_data[pet_slot + "_rarity"])
            if self.md.has_data_tag(setup_data["pet_exp_boost"], "auction_price_upon_request") and (time.time() - self.md.calculator_data[setup_data["pet_exp_boost"]]["price_last_updated"] > self.API_cooldown.get()):
                self.md.calculator_data[setup_data["pet_exp_boost"]]["prices"]["ah"] = self.call_auction_house(setup_data["pet_exp_boost"])
                self.md.calculator_data[setup_data["pet_exp_boost"]]["price_last_updated"] = time.time()

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

        # get upgrade info
        upgrades, upgrade_effects = self.get_upgrade_info(minion_fuel, drops_list, setup_data)

        # adding up minion speed bonus
        speed_boost = self.get_speed_boosts(minion_type, upgrades, upgrade_effects, afk_toggle, clock_override, setup_data)
        self.huim.logger.debug(f"Speed boost: {speed_boost}")

        # multiply up minion drop bonus
        drop_multiplier = self.get_drop_multiplier(minion_type, upgrades, afk_toggle, setup_data)
        self.huim.logger.debug(f"Drop multiplier: {drop_multiplier}")

        # AFKing, Special Layouts and Player Harvests influences
        actions_per_harvest = self.get_actions_per_harvest(minion_type, upgrades, upgrade_effects, afk_toggle, setup_data, setup_notes)
        self.huim.logger.debug(f"Actions per harvest: {actions_per_harvest}")

        # AFK loot table changes
        self.update_loot_table(minion_type, upgrades, upgrade_effects, afk_toggle, setup_data)

        # calculate final minion speed
        seconds_per_action = self.get_seconds_per_action(minion_type, minion_tier, minion_fuel, speed_boost, setup_data)

        # time calculations
        empty_time_seconds, timeratio, empty_time_str, scaled_time_str = self.get_time_constants(seconds_per_action, actions_per_harvest, setup_data)
        
        # harvests per time
        harvests_per_time, drop_multiplier = self.get_harvests_per_time(empty_time_seconds, actions_per_harvest, seconds_per_action, afk_toggle, drop_multiplier, setup_data)
        
        # base drops
        self.get_base_drops(drops_list, upgrade_effects, minion_type, harvests_per_time, drop_multiplier)

        # upgrade drops
        self.get_upgrade_drops(drops_list, upgrade_effects, minion_type, minion_tier, drop_multiplier, upgrades, harvests_per_time, afk_toggle, empty_time_seconds, seconds_per_action, setup_data)
        
        # Inferno minion fuel drops
        self.get_inferno_drops(drops_list, upgrade_effects, minion_type, minion_tier, minion_fuel, drop_multiplier, harvests_per_time, empty_time_seconds, afk_toggle, setup_data)

        # Apply compactors
        compacted_items = self.get_compacted_drops(drops_list, upgrade_effects)

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
        setup_pets = self.get_pets_levelled(skill_xp, mayor, setup_data)
        pet_profit, used_pet_prices = self.get_pet_profit(setup_pets, setup_data)

        # calculating beacon and limited fuel cost
        fuel_cost, needed_fuel = self.get_finite_fuel_cost(minion_amount, minion_fuel, empty_time_seconds, setup_data)

        # total profit
        total_profit = item_profit + pet_profit - fuel_cost

        # Setup cost
        total_cost, extra_cost, free_will_optimal_tier, cost_per_part = self.get_setup_cost(minion_type, minion_tier, minion_amount, minion_fuel, setup_pets, setup_data)

        # Construct ID
        setup_ID = self.construct_id(setup_data)

        # Get minion notes
        if "notes" in self.md.calculator_data[minion_type]:
            setup_notes.update(self.md.calculator_data[minion_type]["notes"])

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
            "calculated_ID": setup_ID,
            "extracost": extra_cost,
            "setupcost": total_cost,
            "setupcost_breakdown": cost_per_part,
            "filltime": fill_time,
            "used_storage": used_storage,
            "empty_time": empty_time_str,
            "scaled_time": scaled_time_str,
            "actiontime": seconds_per_action,
            "notes": setup_notes,
            "used_pet_prices": used_pet_prices,
            "optimal_tier_free_will": free_will_optimal_tier,
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
        
        for item_id in self.md.calculator_data.keys():
            if "prices" not in self.md.calculator_data[item_id]:
                continue
            if item_id in dict_item_data and "npc_sell_price" in dict_item_data[item_id]:
                self.md.calculator_data[item_id]["prices"]["npc"] = dict_item_data[item_id]["npc_sell_price"]
            elif "npc" not in self.md.calculator_data[item_id]["prices"]:
                self.md.calculator_data[item_id]["prices"]["npc"] = 0
            if item_id in raw_bazaar_data["products"]:
                self.bazaar_items.append(item_id)
            elif "recipe" in self.md.calculator_data[item_id]:
                self.recipe_items.append(item_id)
            elif self.md.has_data_tag(item_id, "auction_price"):
                self.AH_items.append(item_id)
            elif self.md.has_data_tag(item_id, "auction_price_upon_request"):
                self.md.calculator_data[item_id]["price_last_updated"] = 0
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
                    self.md.calculator_data[item_id]["prices"][f"{action}Price"] = 0
                    if "npc" not in self.md.calculator_data[item_id]["prices"]:
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
                    self.md.calculator_data[item_id]["prices"][f"{action}Price"] = top_price
                    self.huim.logger.info(f"bottom heavy {action} supply for {item_id}, taking top order price")
                else:
                    self.md.calculator_data[item_id]["prices"][f"{action}Price"] = top_percent_avg_price
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
        raw_auction_data = self.huim.call_API(r"https://sky.coflnet.com/api/item/price/" + item_id + r"/bin", f"SkyCofl AH BIN API: {item_id}", headers={'User-Agent': f"Minion Calculator v{self.version.get()} (Python)"})
        return (raw_auction_data["lowest"] + raw_auction_data["secondLowest"]) / 2

    def update_recipe_price(self, item_id):
        """
        Calculates equivalent bazaar price for recipe items
        
        :param item_id: str, item ID that has a recipe
        
        Returns
        -------
        None.
        """
        if item_id not in self.md.calculator_data:
            self.huim.logger.error(f"{item_id} not in calculator data")
            return
        if "recipe" not in self.md.calculator_data[item_id]:
            self.huim.logger.error(f"{item_id} is not a recipe item")
            return
        self.md.calculator_data[item_id]["prices"]["buyPrice"] = 0
        self.md.calculator_data[item_id]["prices"]["sellPrice"] = 0
        for material_id, amount in self.md.calculator_data[item_id]["recipe"].items():
            if self.md.has_data_tag(material_id, "auction_price"):
                self.md.calculator_data[item_id]["prices"]["buyPrice"] += amount * self.md.calculator_data[material_id]["prices"]["ah"]
                self.md.calculator_data[item_id]["prices"]["sellPrice"] += amount * self.md.calculator_data[material_id]["prices"]["ah"]
                continue
            self.md.calculator_data[item_id]["prices"]["buyPrice"] += amount * self.md.calculator_data[material_id]["prices"]["buyPrice"]
            self.md.calculator_data[item_id]["prices"]["sellPrice"] += amount * self.md.calculator_data[material_id]["prices"]["sellPrice"]
        return

    def update_prices(self, cooldown_warning=True, in_gui=True):
        """
        If API_cooldown is done, update prices
        
        :param cooldown_warning: bool, toggle if a terminal message should be logged if the bazaar update cooldown has not passed yet.
        """
        if time.time() - self.API_timer < self.API_cooldown.get() and self.API_timer != 0:
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
            self.md.calculator_data[item_id]["prices"]["ah"] = self.call_auction_house(item_id)
        self.huim.logger.info("Updating Recipe prices")
        for item_id in self.recipe_items:
            self.update_recipe_price(item_id)
        if in_gui is True:
            self.statusC.configure(bg=background_color_storage)
            self.statusC.update()
        return

    def update_pet_price(self, pet_ID, rarity):
        """
        API call to SkyCofl to update Auction House price of the given pet.
        First calls to BIN, and takes the average of the two lowest.
        If there are less than 2 BIN auctions active it falls back to the average of the last 2 days.
        If no price is found, it will keep the old price.
        Repeated for both minimum and maximum pet level.
        Both minimum and maximum have to be found for a new pet to be added to memory.

        AH data from https://sky.coflnet.com/data
        
        :param pet_ID: str, pet ID as seen in calculator data
        """
        if self.md.has_data_tag(pet_ID, "no_ah_api"):
            return
        if rarity in self.md.calculator_data[pet_ID]["pet_prices"] and time.time() - self.md.calculator_data[pet_ID]["pet_prices"][rarity]["last_updated"] < self.pet_API_cooldown.get():
            self.huim.logger.debug(f"{pet_ID} {rarity} price update is on cooldown")
            return
        level_ranges = { "min": "1", "max": "100" }
        api_end_point = r"https://sky.coflnet.com/api/item/price/"
        if self.md.has_data_tag(pet_ID, "dragon_egg_pet"):
            api_pet_id = pet_ID.removesuffix("_EGG")
            level_ranges["max"] = "100-103"
        elif self.md.has_data_tag(pet_ID, "hatched_dragon_pet"):
            api_pet_id = pet_ID.removesuffix("_HATCHED")
            level_ranges["min"] = "100-103"
            level_ranges["max"] = "200"
        else:
            api_pet_id = pet_ID
        if self.md.has_data_tag(pet_ID, "dragon_pet"):
            level_ranges["max"] = "200"
        api_bin = r"/bin"
        api_static_filters = r"?filters[Rarity]=" + rarity + r"&filters[Candy]=0&filters[PetItem]=NOT_TIER_BOOST&filters[PetLevel]="
        results = {"min": 0, "max": 0}
        for level_type, level_range in level_ranges.items():
            raw_auction_data = self.huim.call_API(api_end_point + api_pet_id + api_bin + api_static_filters + level_range, f"SkyCofl pet AH BIN API: {api_pet_id}", headers={'User-Agent': f"Minion Calculator v{self.version.get()} (Python)"})
            lowest_price = raw_auction_data["lowest"]
            second_lowest_price = raw_auction_data["secondLowest"]
            if lowest_price == 0 or second_lowest_price == 0:
                # fall back to average of last 2 days if not enough BINs are found
                results[level_type] = self.huim.call_API(api_end_point + api_pet_id + api_static_filters + level_range, f"SkyCofl pet AH API: {api_pet_id}", headers={'User-Agent': f"Minion Calculator v{self.version.get()} (Python)"})["mean"]
            else:
                results[level_type] = (lowest_price + second_lowest_price) / 2
        if rarity not in self.md.calculator_data[pet_ID]["pet_prices"]:
            if results["min"] == 0 or results["max"] == 0:
                return
            self.md.calculator_data[pet_ID]["pet_prices"][rarity] = { "min": 0, "max": 0, "last_updated": 0 }
            self.md.instance_data[f"{pet_ID}.pet_prices.{rarity}"] = None  # will auto update when instance data is saved (just need to get the key in)
        if results["min"] != 0:
            self.md.calculator_data[pet_ID]["pet_prices"][rarity]["min"] = results["min"]
        if results["max"] != 0:
            self.md.calculator_data[pet_ID]["pet_prices"][rarity]["max"] = results["max"]
        self.md.calculator_data[pet_ID]["pet_prices"][rarity]["last_updated"] = time.time()
        return

    def update_listboxes(self):
        """
        Calls .update_listbox() for all variables that are of dtype list or dict.

        Returns
        -------
        None.

        """
        for var_key in self.var_dict:
            if self.var_dict[var_key].dtype in [list, dict]:
                if var_key == "pets_levelled":
                    self.pets_levelled.update_listbox(key_format_function=lambda x: self.var_dict[x + "_rarity"].get(False) + " " + self.var_dict[x].get(False))
                    continue
                elif var_key == "setupcost_breakdown":
                    self.setupcost_breakdown.update_listbox(key_format_function=lambda x: self.var_dict[x].get_display(False))
                    continue
                elif var_key == "used_pet_prices":
                    self.used_pet_prices.update_listbox(key_format_function=lambda x: " ".join([self.md.calculator_data[y]["display"] for y in x.split(".")]))
                    continue
                format_function = lambda x: x
                if self.var_dict[var_key].has_tag("item_ID_to_display"):
                    format_function = lambda x: self.md.calculator_data[x]["display"]
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
    
    def edit_settings(self, new_settings):
        if self.debug_mode.get():
            self.huim.logger.setLevel(10)
        else:
            self.huim.logger.setLevel(20)
        return

    def save_calculator_data(self):
        saving_settings = {}
        for setting in self.default_settings.keys():
            if setting in self.var_dict:
                saving_settings[setting] = self.var_dict[setting].get()
            elif setting == "window_height":
                saving_settings[setting] = self.winfo_height()
            elif setting == "window_width":
                saving_settings[setting] = self.winfo_width()
        self.huim.write_json(self.settings_file, saving_settings)
        self.md.save_instance_data()
        return

#%% main loop


def run_calculator():
    """
    Starts the minion calculator and destroys it when exited
    Warns user if the stop button was not used to close the calculator

    Returns
    -------
    None.

    """
    App = Calculator()
    App.mainloop()
    print("INFO - run_calculator - Exited mainloop")
    try:
        App.save_calculator_data()
        print("INFO - run_calculator - Saved calculator data")
        App.destroy()
        print("INFO - run_calculator - Detroyed application")
    except tk.TclError:
        print("ERROR - run_calculator - Please use the stop button in the bottom right to close the application")
    print("INFO - run_calculator - Closed")
    return

if __name__ == "__main__":
    run_calculator()
else:
    print("Run `main.py` directly to start the calculator")
