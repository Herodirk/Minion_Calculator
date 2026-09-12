# -*- coding: utf-8 -*-
"""
@author: Herodirk

Hero data Manager.
Calculator Data includes:
- Minion drops with xp amounts
- Other minion related materials
- Internal and external minion upgrades
- Pets and related items
- Minions with speed, storage and upgrade costs
- Mayors
- Shards per attribute level
- Pet item replacement costs
- Pet exp amounts for max level
Other data points:
- Inferno fuel data
- Standard storage amounts

Custom Data:
- Custom inputs:
    - Minion: base speeds, drops, storage
    - Drops: xp, compacting, npc price
    - Upgrade: speed bonus, drop multiplier, upgrade special (spreading, adding, cooldown)
    - Levelling pet: type, max pet xp

Bazaar and NPC price data from https://api.hypixel.net
AH data from https://sky.coflnet.com/data

Notes about inaccuracies and tests at the bottom of this file
"""

import pathlib

class H_data_M():
    def __init__(self, huim):
        self.huim = huim

        self.inferno_fuel_data = {
            'grades': { 'HYPERGOLIC_GABAGOOL': 20, 'HEAVY_GABAGOOL': 15, 'FUEL_GABAGOOL': 10 },
            'distilates': {
                'MAGMA_CREAM_DISTILLATE': ["MAGMA_CREAM", 2],
                'BLAZE_ROD_DISTILLATE': ["BLAZE_ROD", 1],
                'NETHER_STALK_DISTILLATE': ["NETHER_STALK", 5],
                'GLOWSTONE_DUST_DISTILLATE': ["GLOWSTONE_DUST", 2.5],
                'CRUDE_GABAGOOL_DISTILLATE': ["CRUDE_GABAGOOL", 1]
            },
            'drops': {
                'CHILI_PEPPER': 1 / 136,
                'INFERNO_VERTEX': 1 / 5950,
                'INFERNO_APEX': 1 / 1309091,
                'REAPER_PEPPER': 1 / 458182,
                'GABAGOOL_THE_FISH': 1 / 3927273
            }
        }

        self.standard_storage = { 1: 1, 2: 3, 3: 3, 4: 6, 5: 6, 6: 9, 7: 9, 8: 12, 9: 12, 10: 15, 11: 15, 12: 15 }

        self.instance_data_file = pathlib.Path("calculator_instance_data.json")

        self.instance_data = {
            "NONE.pet_prices.LEGENDARY": { "min": 1, "max": 1, "last_updated": 0 },
            "CUSTOM.prices.npc": 1,
            "CUSTOM.xp.alchemy": 0,
            "CUSTOM.xp.combat": 1,
            "CUSTOM.xp.farming": 0,
            "CUSTOM.xp.fishing": 0,
            "CUSTOM.xp.foraging": 0,
            "CUSTOM.xp.mining": 0,
            "CUSTOM.compacting.block.amount": 2,
            "CUSTOM.compacting.block.per": 8,
            "CUSTOM.compacting.compact.amount": 1,
            "CUSTOM.compacting.compact.per": 160,
            "CUSTOM_BLOCK.prices.npc": 4,
            "CUSTOM_BLOCK.xp.alchemy": 0,
            "CUSTOM_BLOCK.xp.combat": 4,
            "CUSTOM_BLOCK.xp.farming": 0,
            "CUSTOM_BLOCK.xp.fishing": 0,
            "CUSTOM_BLOCK.xp.foraging": 0,
            "CUSTOM_BLOCK.xp.mining": 0,
            "CUSTOM_BLOCK.compacting.compact.amount": 4,
            "CUSTOM_BLOCK.compacting.compact.per": 160,
            "ENCHANTED_CUSTOM.prices.npc": 160,
            "ENCHANTED_CUSTOM.xp.alchemy": 0,
            "ENCHANTED_CUSTOM.xp.combat": 160,
            "ENCHANTED_CUSTOM.xp.farming": 0,
            "ENCHANTED_CUSTOM.xp.fishing": 0,
            "ENCHANTED_CUSTOM.xp.foraging": 0,
            "ENCHANTED_CUSTOM.xp.mining": 0,
            "ENCHANTED_CUSTOM.compacting.compact.amount": 1,
            "ENCHANTED_CUSTOM.compacting.compact.per": 160,
            "ENCHANTED_CUSTOM_BLOCK.prices.npc": 25600,
            "ENCHANTED_CUSTOM_BLOCK.xp.alchemy": 0,
            "ENCHANTED_CUSTOM_BLOCK.xp.combat": 25600,
            "ENCHANTED_CUSTOM_BLOCK.xp.farming": 0,
            "ENCHANTED_CUSTOM_BLOCK.xp.fishing": 0,
            "ENCHANTED_CUSTOM_BLOCK.xp.foraging": 0,
            "ENCHANTED_CUSTOM_BLOCK.xp.mining": 0,
            "CUSTOM_MINION.drops": { "CUSTOM": 1 },
            "CUSTOM_MINION.speed.1": 1,
            "CUSTOM_MINION.speed.2": 2,
            "CUSTOM_MINION.speed.3": 3,
            "CUSTOM_MINION.speed.4": 4,
            "CUSTOM_MINION.speed.5": 5,
            "CUSTOM_MINION.speed.6": 6,
            "CUSTOM_MINION.speed.7": 7,
            "CUSTOM_MINION.speed.8": 8,
            "CUSTOM_MINION.speed.9": 9,
            "CUSTOM_MINION.speed.10": 10,
            "CUSTOM_MINION.speed.11": 11,
            "CUSTOM_MINION.speed.12": 12,
            "CUSTOM_MINION.storage.1": 15,
            "CUSTOM_MINION.storage.2": 15,
            "CUSTOM_MINION.storage.3": 15,
            "CUSTOM_MINION.storage.4": 15,
            "CUSTOM_MINION.storage.5": 15,
            "CUSTOM_MINION.storage.6": 15,
            "CUSTOM_MINION.storage.7": 15,
            "CUSTOM_MINION.storage.8": 15,
            "CUSTOM_MINION.storage.9": 15,
            "CUSTOM_MINION.storage.10": 15,
            "CUSTOM_MINION.storage.11": 15,
            "CUSTOM_MINION.storage.12": 15,
            "CUSTOM_MINION.afkcorrupt": 2,
            "PET_CUSTOM_PET.pet_type": "farming",
            "CUSTOM_RARITY.max_lvl_pet_xp_amount": 25353230,
            "PET_CUSTOM_PET.pet_prices.CUSTOM_RARITY.max": 20000000,
            "CUSTOM_UPGRADE.speed_boost": 0,
            "CUSTOM_UPGRADE.drop_multiplier": 1,
            "CUSTOM_UPGRADE.xp_multiplier": 1,
            "CUSTOM_UPGRADE.upgrade_effects.spreading": {},
            "CUSTOM_UPGRADE.upgrade_effects.adding": {},
            "CUSTOM_UPGRADE.upgrade_effects.cooldown.items": {},
            "CUSTOM_UPGRADE.upgrade_effects.cooldown.online_cooldown": 60,
            "CUSTOM_UPGRADE.upgrade_effects.cooldown.offline_cooldown": 60,
        }

        self.custom_inputs_edit_tree = {
            "Cancel": "Object to edit",
            "Materials": {
                "Cancel": "Material to edit",
                "Base Custom": {
                    "CUSTOM.prices.npc": {"dtype": float, "display": "Base Custom NPC price", "options": None},
                    "CUSTOM.xp.alchemy": {"dtype": float, "display": "Base Custom Alchemy XP", "options": None},
                    "CUSTOM.xp.combat": {"dtype": float, "display": "Base Custom Combat XP", "options": None},
                    "CUSTOM.xp.farming": {"dtype": float, "display": "Base Custom Farming XP", "options": None},
                    "CUSTOM.xp.fishing": {"dtype": float, "display": "Base Custom Fishing XP", "options": None},
                    "CUSTOM.xp.foraging": {"dtype": float, "display": "Base Custom Foraging XP", "options": None},
                    "CUSTOM.xp.mining": {"dtype": float, "display": "Base Custom Mining XP", "options": None},
                    "CUSTOM.compacting.block.per": {"dtype": float, "display": "Base Custom per Custom Block craft", "options": None},
                    "CUSTOM.compacting.block.amount": {"dtype": float, "display": "Custom Block amount from craft", "options": None},
                    "CUSTOM.compacting.compact.per": {"dtype": float, "display": "Base Custom per Enchanted Custom craft", "options": None},
                    "CUSTOM.compacting.compact.amount": {"dtype": float, "display": "Enchanted Custom amount from craft", "options": None},
                },
                "Custom Block": {
                    "CUSTOM_BLOCK.prices.npc": {"dtype": float, "display": "Custom Block NPC price", "options": None},
                    "CUSTOM_BLOCK.xp.alchemy": {"dtype": float, "display": "Custom Block Alchemy XP", "options": None},
                    "CUSTOM_BLOCK.xp.combat": {"dtype": float, "display": "Custom Block Combat XP", "options": None},
                    "CUSTOM_BLOCK.xp.farming": {"dtype": float, "display": "Custom Block Farming XP", "options": None},
                    "CUSTOM_BLOCK.xp.fishing": {"dtype": float, "display": "Custom Block Fishing XP", "options": None},
                    "CUSTOM_BLOCK.xp.foraging": {"dtype": float, "display": "Custom Block Foraging XP", "options": None},
                    "CUSTOM_BLOCK.xp.mining": {"dtype": float, "display": "Custom Block Mining XP", "options": None},
                    "CUSTOM_BLOCK.compacting.compact.per": {"dtype": float, "display": "Custom Block per Enchanted Custom craft", "options": None},
                    "CUSTOM_BLOCK.compacting.compact.amount": {"dtype": float, "display": "Enchanted Custom amount from craft", "options": None},
                },
                "Enchanted Custom": {
                    "ENCHANTED_CUSTOM.prices.npc": {"dtype": float, "display": "Enchanted Custom NPC price", "options": None},
                    "ENCHANTED_CUSTOM.xp.alchemy": {"dtype": float, "display": "Enchanted Custom Alchemy XP", "options": None},
                    "ENCHANTED_CUSTOM.xp.combat": {"dtype": float, "display": "Enchanted Custom Combat XP", "options": None},
                    "ENCHANTED_CUSTOM.xp.farming": {"dtype": float, "display": "Enchanted Custom Farming XP", "options": None},
                    "ENCHANTED_CUSTOM.xp.fishing": {"dtype": float, "display": "Enchanted Custom Fishing XP", "options": None},
                    "ENCHANTED_CUSTOM.xp.foraging": {"dtype": float, "display": "Enchanted Custom Foraging XP", "options": None},
                    "ENCHANTED_CUSTOM.xp.mining": {"dtype": float, "display": "Enchanted Custom Mining XP", "options": None},
                    "ENCHANTED_CUSTOM.compacting.compact.per": {"dtype": float, "display": "Enchanted Custom per Enchanted Custom Block craft", "options": None},
                    "ENCHANTED_CUSTOM.compacting.compact.amount": {"dtype": float, "display": "Enchanted Custom Block amount from craft", "options": None},
                },
                "Enchanted Custom Block": {
                    "ENCHANTED_CUSTOM_BLOCK.prices.npc": {"dtype": float, "display": "Enchanted Custom Block NPC price", "options": None},
                    "ENCHANTED_CUSTOM_BLOCK.xp.alchemy": {"dtype": float, "display": "Enchanted Custom Block Alchemy XP", "options": None},
                    "ENCHANTED_CUSTOM_BLOCK.xp.combat": {"dtype": float, "display": "Enchanted Custom Block Combat XP", "options": None},
                    "ENCHANTED_CUSTOM_BLOCK.xp.farming": {"dtype": float, "display": "Enchanted Custom Block Farming XP", "options": None},
                    "ENCHANTED_CUSTOM_BLOCK.xp.fishing": {"dtype": float, "display": "Enchanted Custom Block Fishing XP", "options": None},
                    "ENCHANTED_CUSTOM_BLOCK.xp.foraging": {"dtype": float, "display": "Enchanted Custom Block Foraging XP", "options": None},
                    "ENCHANTED_CUSTOM_BLOCK.xp.mining": {"dtype": float, "display": "Enchanted Custom Block Mining XP", "options": None},
                }
            },
            "Custom Minion": {
                "Cancel": "Attribute to edit",
                "Drops": {
                    "CUSTOM_MINION.drops": {"dtype": dict, "display": "Minion drops"}
                },
                "Action Time": {
                    "CUSTOM_MINION.speed.1": {"dtype": float, "display": "Action time (s) t1", "options": None},
                    "CUSTOM_MINION.speed.2": {"dtype": float, "display": "Action time (s) t2", "options": None},
                    "CUSTOM_MINION.speed.3": {"dtype": float, "display": "Action time (s) t3", "options": None},
                    "CUSTOM_MINION.speed.4": {"dtype": float, "display": "Action time (s) t4", "options": None},
                    "CUSTOM_MINION.speed.5": {"dtype": float, "display": "Action time (s) t5", "options": None},
                    "CUSTOM_MINION.speed.6": {"dtype": float, "display": "Action time (s) t6", "options": None},
                    "CUSTOM_MINION.speed.7": {"dtype": float, "display": "Action time (s) t7", "options": None},
                    "CUSTOM_MINION.speed.8": {"dtype": float, "display": "Action time (s) t8", "options": None},
                    "CUSTOM_MINION.speed.9": {"dtype": float, "display": "Action time (s) t9", "options": None},
                    "CUSTOM_MINION.speed.10": {"dtype": float, "display": "Action time (s) t10", "options": None},
                    "CUSTOM_MINION.speed.11": {"dtype": float, "display": "Action time (s) t11", "options": None},
                    "CUSTOM_MINION.speed.12": {"dtype": float, "display": "Action time (s) t12", "options": None},
                },
                "Storage": {
                    "CUSTOM_MINION.storage.1": {"dtype": float, "display": "Storage (slots) t1", "options": None},
                    "CUSTOM_MINION.storage.2": {"dtype": float, "display": "Storage (slots) t2", "options": None},
                    "CUSTOM_MINION.storage.3": {"dtype": float, "display": "Storage (slots) t3", "options": None},
                    "CUSTOM_MINION.storage.4": {"dtype": float, "display": "Storage (slots) t4", "options": None},
                    "CUSTOM_MINION.storage.5": {"dtype": float, "display": "Storage (slots) t5", "options": None},
                    "CUSTOM_MINION.storage.6": {"dtype": float, "display": "Storage (slots) t6", "options": None},
                    "CUSTOM_MINION.storage.7": {"dtype": float, "display": "Storage (slots) t7", "options": None},
                    "CUSTOM_MINION.storage.8": {"dtype": float, "display": "Storage (slots) t8", "options": None},
                    "CUSTOM_MINION.storage.9": {"dtype": float, "display": "Storage (slots) t9", "options": None},
                    "CUSTOM_MINION.storage.10": {"dtype": float, "display": "Storage (slots) t10", "options": None},
                    "CUSTOM_MINION.storage.11": {"dtype": float, "display": "Storage (slots) t11", "options": None},
                    "CUSTOM_MINION.storage.12": {"dtype": float, "display": "Storage (slots) t12", "options": None},
                },
                "AFK corrupt multiplier": {
                    "CUSTOM_MINION.afkcorrupt": {"dtype": float, "display": "AFK corrupt multiplier", "options": None}
                }
            },
            "Custom Upgrade": {
                "Cancel": "Attribute to edit",
                "General": {
                    "custom_upgrade_toggle": None,
                    "CUSTOM_UPGRADE.speed_boost": {"dtype": float, "display": "Custom Upgrade Speed boost", "options": None},
                    "CUSTOM_UPGRADE.drop_multiplier": {"dtype": float, "display": "Custom Upgrade Drop multiplier", "options": None},
                    "CUSTOM_UPGRADE.xp_multiplier": {"dtype": float, "display": "Custom Upgrade XP multiplier", "options": None},
                    "CUSTOM_UPGRADE.upgrade_effects.cooldown.online_cooldown": {"dtype": float, "display": "Custom Upgrade Online Cooldown", "options": None},
                    "CUSTOM_UPGRADE.upgrade_effects.cooldown.offline_cooldown": {"dtype": float, "display": "Custom Upgrade Offline Cooldown", "options": None},
                },
                "Spreading effect": {
                    "CUSTOM_UPGRADE.upgrade_effects.spreading": {"dtype": dict, "display": "Spreading drops"}
                },
                "Adding effect": {
                    "CUSTOM_UPGRADE.upgrade_effects.adding": {"dtype": dict, "display": "Adding drops"}
                },
                "Cooldown effect": {
                    "CUSTOM_UPGRADE.upgrade_effects.cooldown.items": {"dtype": dict, "display": "Cooldown drops"}
                }
            },
            "Custom Pet": {
                "PET_CUSTOM_PET.pet_type": {"dtype": str, "display": "Pet Type", "options": ["all", "alchemy", "combat", "enchanting", "farming", "fishing", "foraging", "mining"]},
                "CUSTOM_RARITY.max_lvl_pet_xp_amount": {"dtype": float, "display": "Custom Rarity max Pet XP", "options": None},
                "PET_CUSTOM_PET.pet_prices.CUSTOM_RARITY.max": {"dtype": float, "display": "Custom Pet profit per pet", "options": None}
            }
        }

        self.huim.check_json(self.instance_data_file, self.instance_data)
        self.instance_data.update(self.huim.read_json(self.instance_data_file))
        self.init_calculator_data()
        self.huim.logger.debug("Calculator Data loaded")
        return

    def init_calculator_data(self):
        """
        calls to Hypixel's Item,
        uses that data to get NPC prices and XP amounts

        Returns
        -------
        None

        """
        self.calculator_data = self.huim.read_json(pathlib.Path("calculator_data.json"))
        self.huim.logger.debug("Static Calculator Data loaded")

        raw_item_data = self.huim.call_API(r"https://api.hypixel.net/resources/skyblock/items", "Hypixel Item API")
        if "success" not in raw_item_data or raw_item_data["success"] is False:
            self.huim.logger.error("Hypixel Item API call was unsuccessful")
            return
        dict_item_data = {}
        for item_data in raw_item_data["items"]:
            dict_item_data[item_data["id"]] = item_data
        for item_id in self.calculator_data.keys():
            if item_id not in dict_item_data:
                continue
            if "npc_sell_price" in dict_item_data[item_id]:
                self.set_data(item_id + ".prices.npc", dict_item_data[item_id]["npc_sell_price"])
            else:
                self.set_data(item_id + ".prices.npc", 0)
            if "experience" not in dict_item_data[item_id]:
                continue
            for skill, xp_data in dict_item_data[item_id]["experience"].items():
                if "MINION_STORAGE" in xp_data:
                    self.set_data(item_id + ".xp." + skill, xp_data["MINION_STORAGE"])
        for data_loc, data_val in self.instance_data.items():
            self.set_data(data_loc, data_val)
        return

    def has_data_tag(self, data_ID, tag):
        if data_ID not in self.calculator_data:
            self.huim.logger.warning(f"Data ID {data_ID} not in calculator data")
            return False
        if tag is None:
            return False
        if len(tag) == 0:
            return True
        if data_ID == tag or data_ID in tag:
            return True
        if "tags" not in self.calculator_data[data_ID]:
            return False
        if type(tag) == str and tag in self.calculator_data[data_ID]["tags"]:
            return True
        if type(tag) != list:
            return False
        for search_tag in tag:
            if search_tag in self.calculator_data[data_ID]["tags"]:
                return True
        return False

    def minion_cost_sum(self, minion_type, final_tier):
        final_cost = {}
        tier_loop = range(1, final_tier + 1)
        for tier in tier_loop:
            for item, amount in self.calculator_data[minion_type]["minion_costs"][str(tier)].items():
                if item not in final_cost:
                    final_cost[item] = 0
                final_cost[item] += amount
        return final_cost

    def get_data(self, data_location, fallback=None):
        data_pointer = self.calculator_data
        data_location_keys = data_location.split(".")
        for key in data_location_keys:
            if key not in data_pointer:
                if fallback is None:
                    self.huim.logger.warning(f"Could not find {key} in calculator data for {data_location}")
                return fallback
            data_pointer = data_pointer[key]
        return data_pointer

    def check_data(self, data_location):
        data_pointer = self.calculator_data
        data_location_keys = data_location.split(".")
        for key in data_location_keys:
            if key not in data_pointer:
                return False
            data_pointer = data_pointer[key]
        return True

    def set_data(self, data_location, data_value):
        data_pointer = self.calculator_data
        data_location_keys = data_location.split(".")
        set_location = data_location_keys[-1]
        for key in data_location_keys:
            if key == set_location:
                data_pointer[key] = data_value
            else:
                if key not in data_pointer:
                    data_pointer[key] = {}
                data_pointer = data_pointer[key]
        return

    def save_instance_data(self):
        for data_loc in self.instance_data.keys():
            self.instance_data[data_loc] = self.get_data(data_loc)
        self.huim.write_json(self.instance_data_file, self.instance_data)
        return

    def create_custom_inputs_edit_vars(self, option_tree, choice_layer):
        if "Cancel" in option_tree:
            self.huim.new_edit_vars("custom_input_" + choice_layer, {"custom_input_edit_choice": {"dtype": str, "display": option_tree["Cancel"], "initial": "Cancel", "options": list(option_tree.keys())}}, lambda results: self.huim.edit_vars("custom_input_" + results["custom_input_edit_choice"]))
            for next_layer in option_tree.keys():
                if next_layer == "Cancel":
                    continue
                self.create_custom_inputs_edit_vars(option_tree[next_layer], next_layer)
            return
        input_variables = {}
        for data_loc, custom_input_options in option_tree.items():
            input_variables[data_loc] = custom_input_options
            if custom_input_options is None:
                continue
            input_variables[data_loc]["initial"] = self.get_data(data_loc)
        self.huim.new_edit_vars("custom_input_" + choice_layer, input_variables, lambda results: self.set_custom_inputs(results, "custom_input_" + choice_layer))
        return

    def set_custom_inputs(self, edited_data_locs, request_id):
        for data_loc, data_value in edited_data_locs.items():
            if type(data_value) == dict:
                for item_id, value in list(data_value.items()):
                    if type(value) not in [int, float] or item_id not in self.calculator_data:
                        self.huim.logger.warning("Skipped bad input: " + item_id)
                        del data_value[item_id]
                        self.huim.edit_vars_requests[request_id]["variables"][data_loc]["listbox"].set([f'{key}: {val}' for key, val in data_value.items()])
            self.set_data(data_loc, data_value)
        return



"""
Calculator Data Notes

If information has been checked, there is "# correct" behind it with the date of the test.
If information has been checked but still isn't a logical value, then there is "# correct inaccuracy" behind it with the date of the test.
These are inaccuracies from Hypixel and they can correct them at any point in time, so they should be checked regularly
If that date is missing, it was confirmed by an old test and might need to be checked again.


LAPIS_MINION: drops  # correct
HARD_STONE_MINION: drops  # correct (2026-7-27)
WHEAT_MINION: drops  # correct
NETHER_WART_MINION: drops  # correct (2025-10-18)
FLOWER_MINION: drops  # TODO: check
FLOWER_MINION: tags  # correct
FISHING_MINION: drops  # good average (2025-10-24)
ZOMBIE_MINION: drops  # correct
SKELETON_MINION: drops  # correct
RABBIT_MINION: drops  # correct
COW_MINION: minion_costs: 12  # correct

INFERNO_FUEL  # exact item ID does not exist
MITHRIL_WINTER_CRYSTAL  # exact item ID does not exist
EVERBURNING_FLAME: affected_minions  # correct that spider minion does not have "combat_minion" tag (2026-6-23)
AUTO_SMELTER, DWARVEN_COMPACTOR: replacement_list: {CLAY_BALL: BRICK}  # correct (2026-1-29)
COMPACTOR: compacting_list  # does not make Hay Bales anymore
SUPER_COMPACTOR_3000, DWARVEN_COMPACTOR: compacting_list  # correct that they do not compact the following items
- WHEAT -> ENCHANTED_BREAD
- CHILI_PEPPER -> STUFFED_CHILI_PEPPER
- HEMOGLASS -> HEMOBOMB
- ENCHANTED_GHAST_TEAR -> SILVER_FANG  # correct (2026-7-27)

WOOD_PICKAXE: prices  # Lumber Merchant
WOOD_SPADE: prices  # Lumber Merchant
WOOD_HOE: prices  # Lumber Merchant
WOOD_SWORD: prices  # Lumber Merchant
WOOD_AXE: prices  # Lumber Merchant
FISHING_ROD: recipe  # +/- 3 sticks
INFERNO_FUEL: prices  # this custom price will be automatically updated by the calculator based on grade and distilate
FLINT_SHOVEL: recipe  # +/- 2 sticks
HUNTER_KNIFE: prices  # Rusty
PET_ITEM_MINING_SKILL_BOOST_COMMON: prices  # Zog
PET_ITEM_MINING_SKILL_BOOST_UNCOMMON: prices  # Zog
PET_ITEM_FARMING_SKILL_BOOST_COMMON: prices  # Zog
PET_ITEM_FARMING_SKILL_BOOST_RARE: prices  # Zog
PET_ITEM_FARMING_SKILL_BOOST_EPIC: prices  # Duncan
PET_ITEM_FISHING_SKILL_BOOST_COMMON: prices  # Zog
PET_ITEM_COMBAT_SKILL_BOOST_COMMON: prices  # Zog
PET_ITEM_FORAGING_SKILL_BOOST_COMMON: prices  # Zog
PET_ITEM_ALL_SKILLS_BOOST_COMMON: prices  # Zog
SUPER_SCRUBBER: prices  # Plumber Joe

MITHRIL_WINTER_CRYSTAL: speed_boost  # correct

Offline cooldown of the following upgrades are not confirmed:
- LESSER_SOULFLOW_ENGINE
- SOULFLOW_ENGINE
- BERBERIS_FUEL_INJECTOR

ENCHANTED_SHEARS: upgrade_effects  # Base drop wool gets set to 0. For online, its possible that the sheep regrow their wool, making it up to 3 wool per spawn and harvest, needs testing

Compacting recipes notes:
GLOWSTONE  # TODO: check if its not per 160 with amount 4
SNOW_BALL  # TODO: check per and amount
SNOW_BLOCK  # TODO: check per and amount
ENCHANTED_RED_MUSHROOM  # correct (2025-12-22)
ENCHANTED_BROWN_MUSHROOM  # correct (2025-12-22)
CACTUS  # correct (2025-12-17)
ENCHANTED_COCOA  # correct (2025-12-19)
CRUDE_GABAGOOL  # correct
SUPER_EGG  # correct
POISONOUS_POTATO  # correct (2026-7-29)


The following items are not produced by minions anymore:
- HAY_BLOCK
- ENCHANTED_BREAD


The following materials are not in bazaar:
- STONE
- GLOWSTONE
- GLASS
- CLAY
- CLAY_BRICK
- BRICK
- COAL_BLOCK
- IRON_ORE
- IRON_BLOCK
- GOLD_ORE
- GOLD_BLOCK
- DIAMOND_BLOCK
- LAPIS_BLOCK
- REDSTONE_BLOCK
- EMERALD_BLOCK
- QUARTZ_BLOCK
- INK_SACK:2
- RED_ROSE:1
- RED_ROSE:2
- RED_ROSE:3
- RED_ROSE:4
- RED_ROSE:5
- RED_ROSE:6
- RED_ROSE:7
- RED_ROSE:8
- DOUBLE_PLANT:1
- DOUBLE_PLANT:4
- DOUBLE_PLANT:5
- DYE_BYZANTIUM
- DYE_FLAME
- SLIME_BLOCK

The following items are not in Hypixel's Item API:
- FRENCH_FRIES
- ENCHANTED_SHEARS
- SLEEPY_HOLLOW

"""