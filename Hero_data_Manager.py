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
Other data points:
- Inferno fuel data
- Standard storage amounts
- Shards per attribute level
- Pet item replacement costs
- Pet exp amounts for max level

Bazaar and NPC price data from https://api.hypixel.net
AH data from https://sky.coflnet.com/data

Notes about inaccuracies and tests at the bottom of this file
"""

import pathlib

class H_data_M():
    def __init__(self, huim):
        self.calculator_data = huim.read_json(pathlib.Path("calculator_data.json"))

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

        self.attribute_shards = {
            "COMMON": { 1: 1, 2: 4, 3: 9, 4: 15, 5: 22, 6: 30, 7: 40, 8: 54, 9: 72, 10: 96 },
            "UNCOMMON": { 1: 1, 2: 3, 3: 6, 4: 10, 5: 15, 6: 21, 7: 28, 8: 36, 9: 48, 10: 64 },
            "RARE": { 1: 1, 2: 3, 3: 6, 4: 9, 5: 13, 6: 17, 7: 22, 8: 28, 9: 36, 10: 48 },
            "EPIC": { 1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 16, 8: 20, 9: 25, 10: 32 },
            "LEGENDARY": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 9, 7: 12, 8: 15, 9: 19, 10: 24 }
        }

        self.pet_item_scrub_cost = { "COMMON": 25000, "UNCOMMON": 50000, "RARE": 100000, "EPIC": 250000, "LEGENDARY": 500000, "MYTHIC": 1000000, "DIVINE": 2500000 }

        self.max_lvl_pet_xp_amounts = { "COMMON": 5624785, "UNCOMMON": 8644220, "RARE": 12626665, "EPIC": 18608500, "LEGENDARY": 25353230, "MYTHIC": 25353230, "DRAGON": 210255385 }
        pass

    def has_data_tag(self, data_ID, tag):
        if data_ID not in self.calculator_data:
            print(f"ERROR - has_data_tag - data ID {data_ID} not in calculator data")
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

"""
Calculator Data Notes

If information has been checked, there is "# correct" behind it with the date of the test.
If information has been checked but still isn't a logical value, then there is "# correct inaccuracy" behind it with the date of the test.
These are inaccuracies from Hypixel and they can correct them at any point in time, so they should be checked regularly
If that date is missing, it was confirmed by an old test and might need to be checked again.


LAPIS_MINION: drops  # correct
HARD_STONE_MINION: drops  # correct
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
EVERBURNING_FLAME: affected_minions  # TODO: check affected minions
AUTO_SMELTER, DWARVEN_COMPACTOR: replacement_list: {CLAY_BALL: BRICKS}  # correct (2026-1-29)
COMPACTOR: compacting_list  # does not make Hay Bales anymore
SUPER_COMPACTOR_3000, DWARVEN_COMPACTOR: compacting_list  # correct that they do not compact the following items
- WHEAT -> ENCHANTED_BREAD
- CHILI_PEPPER -> STUFFED_CHILI_PEPPER
- HEMOGLASS -> HEMOBOMB
- ENCHANTED_GHAST_TEAR -> SILVER_FANG

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

JACOBS_PARTICIPATION_MEDAL: upgrade_special  # rough estimate of drop rate
ENCHANTED_SHEARS: upgrade_special  # Base drop wool gets set to 0. For online, its possible that the sheep regrow their wool, making it up to 3 wool per spawn and harvest, needs testing

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
POISONOUS_POTATO  # TODO: check if compacting is even possible

XP notes:
- ENCHANTED_GLOWSTONE  # correct inaccuracy
- ENCHANTED_WHEAT  # correct
- ENCHANTED_HAY_BALE  # correct
- ENCHANTED_GOLDEN_CARROT  # correct (2026-3-7)
- HUGE_MUSHROOM_2  # correct inaccuracy
- HUGE_MUSHROOM_1  # correct inaccuracy
- ENCHANTED_HUGE_MUSHROOM_2  # correct inaccuracy (2026-3-17)
- ENCHANTED_HUGE_MUSHROOM_1  # correct inaccuracy (2026-3-17)
- ENCHANTED_CACTUS_GREEN  # correct inaccuracy
- ENCHANTED_CACTUS  # correct inaccuracy
- ENCHANTED_COOKIE  # correct (2026-3-9)
- ENCHANTED_SUGAR  # correct type
- ENCHANTED_SUGAR_CANE  # correct type
- WILD_ROSE  # correct (2025-12-17)
- ENCHANTED_WILD_ROSE  # correct (2025-12-17)
- COMPACTED_WILD_ROSE  # correct (2025-12-21)
- DOUBLE_PLANT  # correct (2025-12-17)
- ENCHANTED_SUNFLOWER  # correct (2025-12-17)
- COMPACTED_SUNFLOWER  # correct (2025-12-21)
- MOONFLOWER  # correct (2025-12-17)
- ENCHANTED_MOONFLOWER  # correct (2025-12-17)
- COMPACTED_MOONFLOWER  # correct (2025-12-21)
- POISONOUS_POTATO  # TODO: check xp amount
- ENCHANTED_POISONOUS_POTATO  # TODO: check xp amount
- ENCHANTED_ENDER_PEARL  # correct inaccuracy
- ABSOLUTE_ENDER_PEARL  # correct inaccuracy
- HEMOGLASS  # correct
- ENCHANTED_STRING  # correct inaccuracy
- ENCHANTED_GHAST_TEAR  # correct inaccuracy
- ENCHANTED_LEATHER  # correct inaccuracy
- ENCHANTED_EGG  # correct inaccuracy
- SUPER_EGG  # TODO: check xp amount
- OMEGA_EGG  # TODO: check xp amount
- ENCHANTED_RABBIT  # correct
- ENCHANTED_COOKED_RABBIT  # correct
- ENCHANTED_RABBIT_FOOT  # correct
- ENCHANTED_RABBIT_HIDE  # correct inaccuracy

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

"""