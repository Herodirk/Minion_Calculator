# -*- coding: utf-8 -*-
"""
@author: Herodirk

File containing data of hypixel skyblock minions.
Data includes:
- List of minion related things with attributes
- Skyblock IDs of minion upgrades
- Lists of compactor, super compactor and auto smelter transformations, inferno minion chances
- Functions for calculating minion crafting cost
- List of minion costs

Bazaar and NPC price data from https://api.hypixel.net
AH data from https://sky.coflnet.com/data

If information has been checked, there is "# correct" behind it with the date of the test.
If information has been checked but still isn't a logical value, then there is "# correct inaccuracy" behind it with the date of the test.
These are inaccuracies from Hypixel and they can correct them at any point in time, so they should be checked regularly
If that date is missing, it was confirmed by an old test and might need to be checked again.
"""

from copy import deepcopy

#%% Bazaar Buy and Sell types:

bazaar_buy_types = {"Buy Order": "sellPrice", "Insta Buy": "buyPrice", "Custom": "custom"}
bazaar_sell_types = {"Sell Offer": "buyPrice", "Insta Sell": "sellPrice", "Custom": "custom"}

#%% Smelter List:

smelting_data = {
    'COBBLESTONE': 'STONE',
    'SAND': 'GLASS',
    'SAND:1': 'GLASS',
    'CLAY_BALL': 'BRICKS',  # correct (2026-1-29)
    'IRON_ORE': 'IRON_INGOT',
    'GOLD_ORE': 'GOLD_INGOT',
    'CACTUS': 'INK_SACK:2',
    'LOG': 'COAL',
    'LOG:1': 'COAL',
    'LOG:2': 'COAL',
    'LOG_2:1': 'COAL',
    'LOG_2': 'COAL',
    'LOG:3': 'COAL'
}


#%% Compacting Lists

compactor_list = {
    'CUSTOM': { 'makes': 'COMPACTED_CUSTOM', 'amount': 2, 'per': 8 },
    'GLOWSTONE_DUST': { 'makes': 'GLOWSTONE', 'per': 4 },
    'CLAY_BALL': { 'makes': 'CLAY', 'per': 4 },
    'CLAY_BRICK': { 'makes': 'BRICK', 'per': 4 },
    'ICE': { 'makes': 'PACKED_ICE', 'per': 9 },
    'SNOW_BALL': { 'makes': 'SNOW_BLOCK', 'per': 4 },
    'COAL': { 'makes': 'COAL_BLOCK', 'per': 9 },
    'IRON_INGOT': { 'makes': 'IRON_BLOCK', 'per': 9 },
    'GOLD_INGOT': { 'makes': 'GOLD_BLOCK', 'per': 9 },
    'DIAMOND': { 'makes': 'DIAMOND_BLOCK', 'per': 9 },
    'INK_SACK:4': { 'makes': 'LAPIS_BLOCK', 'per': 9 },
    'REDSTONE': { 'makes': 'REDSTONE_BLOCK', 'per': 9 },
    'EMERALD': { 'makes': 'EMERALD_BLOCK', 'per': 9 },
    'QUARTZ': { 'makes': 'QUARTZ_BLOCK', 'per': 4 },
    # 'WHEAT': {'makes': 'HAY_BLOCK', 'per': 9},  # does not produce it anymore
    'MELON': { 'makes': 'MELON_BLOCK', 'per': 9 },
    'RED_MUSHROOM': { 'makes': 'HUGE_MUSHROOM_2', 'per': 9 },
    'BROWN_MUSHROOM': { 'makes': 'HUGE_MUSHROOM_1', 'per': 9 },
    'SLIME_BALL': { 'makes': 'SLIME_BLOCK', 'per': 9 }
}

super_compactor_list = {
    'CUSTOM': { 'makes': 'ENCHANTED_CUSTOM', 'amount': 1, 'per': 160 },
    'COMPACTED_CUSTOM': { 'makes': 'ENCHANTED_CUSTOM', 'amount': 4, 'per': 160 },
    'LUSH_BERBERIS': { 'makes': 'ENCHANTED_LUSH_BERBERIS', 'per': 160 },
    'RAW_SOULFLOW': { 'makes': 'SOULFLOW', 'per': 160 },
    'SULPHUR_ORE': { 'makes': 'ENCHANTED_SULPHUR', 'per': 160 },
    'ENCHANTED_SULPHUR': { 'makes': 'ENCHANTED_SULPHUR_CUBE', 'per': 160 },
    'COBBLESTONE': { 'makes': 'ENCHANTED_COBBLESTONE', 'per': 160 },
    'OBSIDIAN': { 'makes': 'ENCHANTED_OBSIDIAN', 'per': 160 },
    'GLOWSTONE_DUST': { 'makes': 'ENCHANTED_GLOWSTONE_DUST', 'per': 160 },
    'GLOWSTONE': { 'makes': 'ENCHANTED_GLOWSTONE_DUST', 'per': 40 },
    'ENCHANTED_GLOWSTONE_DUST': { 'makes': 'ENCHANTED_GLOWSTONE', 'per': 160 },
    'FLINT': { 'makes': 'ENCHANTED_FLINT', 'per': 160 },
    'SAND': { 'makes': 'ENCHANTED_SAND', 'per': 160 },
    'SAND:1': { 'makes': 'ENCHANTED_RED_SAND', 'per': 160 },
    'ENCHANTED_RED_SAND': { 'makes': 'ENCHANTED_RED_SAND_CUBE', 'per': 160 },
    'MYCEL': { 'makes': 'ENCHANTED_MYCELIUM', 'per': 160 },
    'ENCHANTED_MYCELIUM': { 'makes': 'ENCHANTED_MYCELIUM_CUBE', 'per': 160 },
    'CLAY_BALL': { 'makes': 'ENCHANTED_CLAY_BALL', 'per': 160 },
    'ENCHANTED_CLAY_BALL': { 'makes': 'ENCHANTED_CLAY_BLOCK', 'per': 160 },
    'CLAY': { 'makes': 'ENCHANTED_CLAY_BALL', 'amount': 4, 'per': 160 },
    'ICE': { 'makes': 'ENCHANTED_ICE', 'per': 160 },
    'PACKED_ICE': { 'makes': 'ENCHANTED_ICE', 'amount': 9, 'per': 160 },
    'ENCHANTED_ICE': { 'makes': 'ENCHANTED_PACKED_ICE', 'per': 160 },
    'SNOW_BALL': { 'makes': 'ENCHANTED_SNOW_BLOCK', 'per': 640 },
    'SNOW_BLOCK': { 'makes': 'ENCHANTED_SNOW_BLOCK', 'per': 160 },
    'COAL': { 'makes': 'ENCHANTED_COAL', 'per': 160 },
    'COAL_BLOCK': { 'makes': 'ENCHANTED_COAL', 'amount': 9, 'per': 160 },
    'ENCHANTED_COAL': { 'makes': 'ENCHANTED_COAL_BLOCK', 'per': 160 },
    'IRON_INGOT': { 'makes': 'ENCHANTED_IRON', 'per': 160 },
    'IRON_BLOCK': { 'makes': 'ENCHANTED_IRON', 'amount': 9, 'per': 160 },
    'ENCHANTED_IRON': { 'makes': 'ENCHANTED_IRON_BLOCK', 'per': 160 },
    'GOLD_INGOT': { 'makes': 'ENCHANTED_GOLD', 'per': 160 },
    'GOLD_BLOCK': { 'makes': 'ENCHANTED_GOLD', 'amount': 9, 'per': 160 },
    'ENCHANTED_GOLD': { 'makes': 'ENCHANTED_GOLD_BLOCK', 'per': 160 },
    'DIAMOND': { 'makes': 'ENCHANTED_DIAMOND', 'per': 160 },
    'DIAMOND_BLOCK': { 'makes': 'ENCHANTED_DIAMOND', 'amount': 9, 'per': 160 },
    'ENCHANTED_DIAMOND': { 'makes': 'ENCHANTED_DIAMOND_BLOCK', 'per': 160 },
    'INK_SACK:4': { 'makes': 'ENCHANTED_LAPIS_LAZULI', 'per': 160 },
    'LAPIS_BLOCK': { 'makes': 'ENCHANTED_LAPIS_LAZULI', 'amount': 9, 'per': 160 },
    'ENCHANTED_LAPIS_LAZULI': { 'makes': 'ENCHANTED_LAPIS_LAZULI_BLOCK', 'per': 160 },
    'REDSTONE': { 'makes': 'ENCHANTED_REDSTONE', 'per': 160 },
    'REDSTONE_BLOCK': { 'makes': 'ENCHANTED_REDSTONE', 'amount': 9, 'per': 160 },
    'ENCHANTED_REDSTONE': { 'makes': 'ENCHANTED_REDSTONE_BLOCK', 'per': 160 },
    'EMERALD': { 'makes': 'ENCHANTED_EMERALD', 'per': 160 },
    'EMERALD_BLOCK': { 'makes': 'ENCHANTED_EMERALD', 'amount': 9, 'per': 160 },
    'ENCHANTED_EMERALD': { 'makes': 'ENCHANTED_EMERALD_BLOCK', 'per': 160 },
    'QUARTZ': { 'makes': 'ENCHANTED_QUARTZ', 'per': 160 },
    'QUARTZ_BLOCK': { 'makes': 'ENCHANTED_QUARTZ', 'amount': 4, 'per': 160 },
    'ENCHANTED_QUARTZ': { 'makes': 'ENCHANTED_QUARTZ_BLOCK', 'per': 160 },
    'ENDER_STONE': { 'makes': 'ENCHANTED_ENDSTONE', 'per': 160 },
    'MITHRIL_ORE': { 'makes': 'ENCHANTED_MITHRIL', 'per': 160 },
    'HARD_STONE': { 'makes': 'ENCHANTED_HARD_STONE', 'per': 576 },
    'ENCHANTED_HARD_STONE': { 'makes': 'CONCENTRATED_STONE', 'per': 576 },
    'WHEAT': { 'makes': 'ENCHANTED_WHEAT', 'per': 160 },
    # 'WHEAT': {'makes': 'ENCHANTED_BREAD', 'per': 60},  # does not produce it anymore
    'ENCHANTED_WHEAT': { 'makes': 'ENCHANTED_HAY_BALE', 'per': 160 },
    'SEEDS': { 'makes': 'ENCHANTED_SEEDS', 'per': 160 },
    'ENCHANTED_SEEDS': { 'makes': 'BOX_OF_SEEDS', 'per': 160 },
    'MELON': { 'makes': 'ENCHANTED_MELON', 'per': 160 },
    'MELON_BLOCK': { 'makes': 'ENCHANTED_MELON', 'amount': 9, 'per': 160 },
    'ENCHANTED_MELON': { 'makes': 'ENCHANTED_MELON_BLOCK', 'per': 160 },
    'PUMPKIN': { 'makes': 'ENCHANTED_PUMPKIN', 'per': 160 },
    'ENCHANTED_PUMPKIN': { 'makes': 'POLISHED_PUMPKIN', 'per': 160 },
    'CARROT_ITEM': { 'makes': 'ENCHANTED_CARROT', 'per': 160 },
    'ENCHANTED_CARROT': { 'makes': 'ENCHANTED_GOLDEN_CARROT', 'per': 160 },
    'POTATO_ITEM': { 'makes': 'ENCHANTED_POTATO', 'per': 160 },
    'ENCHANTED_POTATO': { 'makes': 'ENCHANTED_BAKED_POTATO', 'per': 160 },
    'RED_MUSHROOM': { 'makes': 'ENCHANTED_RED_MUSHROOM', 'per': 160 },
    'BROWN_MUSHROOM': { 'makes': 'ENCHANTED_BROWN_MUSHROOM', 'per': 160 },
    'HUGE_MUSHROOM_2': { 'makes': 'ENCHANTED_RED_MUSHROOM', 'amount': 9, 'per': 160 },
    'HUGE_MUSHROOM_1': { 'makes': 'ENCHANTED_BROWN_MUSHROOM', 'amount': 9, 'per': 160 },
    'ENCHANTED_RED_MUSHROOM': { 'makes': 'ENCHANTED_HUGE_MUSHROOM_2', 'per': 160 },  # correct (2025-12-22)
    'ENCHANTED_BROWN_MUSHROOM': { 'makes': 'ENCHANTED_HUGE_MUSHROOM_1', 'per': 160 },  # correct (2025-12-22)
    'INK_SACK:2': { 'makes': 'ENCHANTED_CACTUS_GREEN', 'per': 160 },
    'CACTUS': { 'makes': 'ENCHANTED_CACTUS_GREEN', 'per': 160 },  # correct (2025-12-17)
    'ENCHANTED_CACTUS_GREEN': { 'makes': 'ENCHANTED_CACTUS', 'per': 160 },
    'INK_SACK:3': { 'makes': 'ENCHANTED_COCOA', 'per': 160 },
    'ENCHANTED_COCOA': { 'makes': 'ENCHANTED_COOKIE', 'per': 160 },  # correct (2025-12-19)
    'SUGAR_CANE': { 'makes': 'ENCHANTED_SUGAR', 'per': 160 },
    'ENCHANTED_SUGAR': { 'makes': 'ENCHANTED_SUGAR_CANE', 'per': 160 },
    'NETHER_STALK': { 'makes': 'ENCHANTED_NETHER_STALK', 'per': 160 },
    'ENCHANTED_NETHER_STALK': { 'makes': 'MUTANT_NETHER_STALK', 'per': 160 },
    'YELLOW_FLOWER': { 'makes': 'ENCHANTED_DANDELION', 'per': 160 },
    'RED_ROSE': { 'makes': 'ENCHANTED_POPPY', 'per': 576 },
    'WILD_ROSE': { 'makes': 'ENCHANTED_WILD_ROSE', 'per': 160 },
    'ENCHANTED_WILD_ROSE': { 'makes': 'COMPACTED_WILD_ROSE', 'per': 160 },
    'DOUBLE_PLANT': { 'makes': 'ENCHANTED_SUNFLOWER', 'per': 160 },
    'ENCHANTED_SUNFLOWER': { 'makes': 'COMPACTED_SUNFLOWER', 'per': 160 },
    'MOONFLOWER': { 'makes': 'ENCHANTED_MOONFLOWER', 'per': 160 },
    'ENCHANTED_MOONFLOWER': { 'makes': 'COMPACTED_MOONFLOWER', 'per': 160 },
    'RAW_FISH': { 'makes': 'ENCHANTED_RAW_FISH', 'per': 160 },
    'RAW_FISH:1': { 'makes': 'ENCHANTED_RAW_SALMON', 'per': 160 },
    'RAW_FISH:3': { 'makes': 'ENCHANTED_PUFFERFISH', 'per': 160 },
    'RAW_FISH:2': { 'makes': 'ENCHANTED_CLOWNFISH', 'per': 160 },
    'PRISMARINE_CRYSTALS': { 'makes': 'ENCHANTED_PRISMARINE_CRYSTALS', 'per': 80 },
    'PRISMARINE_SHARD': { 'makes': 'ENCHANTED_PRISMARINE_SHARD', 'per': 80 },
    'SPONGE': { 'makes': 'ENCHANTED_SPONGE', 'per': 40 },
    'ENCHANTED_RAW_FISH': { 'makes': 'ENCHANTED_COOKED_FISH', 'per': 160 },
    'ENCHANTED_RAW_SALMON': { 'makes': 'ENCHANTED_COOKED_SALMON', 'per': 160 },
    'ENCHANTED_SPONGE': { 'makes': 'ENCHANTED_WET_SPONGE', 'per': 40 },
    'ROTTEN_FLESH': { 'makes': 'ENCHANTED_ROTTEN_FLESH', 'per': 160 },
    'POISONOUS_POTATO': { 'makes': 'ENCHANTED_POISONOUS_POTATO', 'per': 160 },
    'ENCHANTED_ENDER_PEARL': { 'makes': 'ABSOLUTE_ENDER_PEARL', 'per': 80 },
    'CRUDE_GABAGOOL': { 'makes': 'VERY_CRUDE_GABAGOOL', 'per': 192 },  # correct
    # 'CHILI_PEPPER': {'makes': 'STUFFED_CHILI_PEPPER', 'per': 160},  # does not compact
    'HEMOVIBE': { 'makes': 'HEMOGLASS', 'per': 160 },
    # 'HEMOGLASS': {'makes': 'HEMOBOMB', 'per': 15},  # does not compact
    'BONE': { 'makes': 'ENCHANTED_BONE', 'per': 160 },
    'SULPHUR': { 'makes': 'ENCHANTED_GUNPOWDER', 'per': 160 },
    'STRING': { 'makes': 'ENCHANTED_STRING', 'per': 160 },
    'SPIDER_EYE': { 'makes': 'ENCHANTED_SPIDER_EYE', 'per': 160 },
    'BLAZE_ROD': { 'makes': 'ENCHANTED_BLAZE_POWDER', 'per': 160 },
    'ENCHANTED_BLAZE_POWDER': { 'makes': 'ENCHANTED_BLAZE_ROD', 'per': 160 },
    'MAGMA_CREAM': { 'makes': 'ENCHANTED_MAGMA_CREAM', 'per': 160 },
    'ENCHANTED_MAGMA_CREAM': { 'makes': 'WHIPPED_MAGMA_CREAM', 'per': 160 },
    'ENDER_PEARL': { 'makes': 'ENCHANTED_ENDER_PEARL', 'per': 20 },
    'GHAST_TEAR': { 'makes': 'ENCHANTED_GHAST_TEAR', 'per': 5 },
    'SLIME_BALL': { 'makes': 'ENCHANTED_SLIME_BALL', 'per': 160 },
    'SLIME_BLOCK': { 'makes': 'ENCHANTED_SLIME_BALL', 'amount': 9, 'per': 160 },
    'ENCHANTED_SLIME_BALL': { 'makes': 'ENCHANTED_SLIME_BLOCK', 'per': 160 },
    'RAW_BEEF': { 'makes': 'ENCHANTED_RAW_BEEF', 'per': 160 },
    'LEATHER': { 'makes': 'ENCHANTED_LEATHER', 'per': 160 },
    'PORK': { 'makes': 'ENCHANTED_PORK', 'per': 160 },
    'ENCHANTED_PORK': { 'makes': 'ENCHANTED_GRILLED_PORK', 'per': 160 },
    'RAW_CHICKEN': { 'makes': 'ENCHANTED_RAW_CHICKEN', 'per': 160 },
    'FEATHER': { 'makes': 'ENCHANTED_FEATHER', 'per': 160 },
    'EGG': { 'makes': 'ENCHANTED_EGG', 'per': 144 },
    'ENCHANTED_EGG': { 'makes': 'SUPER_EGG', 'per': 144 },
    'SUPER_EGG': { 'makes': 'OMEGA_EGG', 'per': 9 },  # correct
    'WOOL': { 'makes': 'ENCHANTED_WOOL', 'per': 160 },
    'MUTTON': { 'makes': 'ENCHANTED_MUTTON', 'per': 160 },
    'ENCHANTED_MUTTON': { 'makes': 'ENCHANTED_COOKED_MUTTON', 'per': 160 },
    'RABBIT': { 'makes': 'ENCHANTED_RABBIT', 'per': 160 },
    'ENCHANTED_RABBIT': { 'makes': 'ENCHANTED_COOKED_RABBIT', 'per': 160 },
    'RABBIT_FOOT': { 'makes': 'ENCHANTED_RABBIT_FOOT', 'per': 160 },
    'RABBIT_HIDE': { 'makes': 'ENCHANTED_RABBIT_HIDE', 'per': 160 },
    'LOG': { 'makes': 'ENCHANTED_OAK_LOG', 'per': 160 },
    'LOG:1': { 'makes': 'ENCHANTED_SPRUCE_LOG', 'per': 160 },
    'LOG:2': { 'makes': 'ENCHANTED_BIRCH_LOG', 'per': 160 },
    'LOG_2:1': { 'makes': 'ENCHANTED_DARK_OAK_LOG', 'per': 160 },
    'LOG_2': { 'makes': 'ENCHANTED_ACACIA_LOG', 'per': 160 },
    'LOG:3': { 'makes': 'ENCHANTED_JUNGLE_LOG', 'per': 160 }
}


#%% item list

calculator_data = {
    # The following items do not exist
    "NONE": {
        'display': "None",
        "rarity": "Common",
        "hopper_selling_rate": 1,
        "storage_slots": 0,
        "exp_boost_type": "all",
        "exp_boost_amount": 0,
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "fuel_duration": -1,
        "affected_minions": None,
        "upgrade_special": { "type": "None" },
        "prices": { "npc": 0, "custom": 0 },
    },
    'CUSTOM': {
        'display': 'Custom',
        "prices": { 'npc': 1 },
        'xp': { 'combat': 1 }
    },
    'COMPACTED_CUSTOM': {
        'display': 'Compacted Custom',
        "prices": { 'npc': 4 },
        'xp': { 'combat': 4 }
    },
    'ENCHANTED_CUSTOM': {
        'display': 'Enchanted Custom',
        "prices": { 'npc': 160 },
        'xp': { 'combat': 160 }
    },

    # Minion Drops
    'LUSH_BERBERIS': {
        'display': 'Lush Berberis',
        "prices": {},
        'xp': { 'farming': 10 }
    },
    'ENCHANTED_LUSH_BERBERIS': {
        'display': 'Enchanted Lush Berberis',
        "prices": {},
        'xp': { 'farming': 1600 }
    },
    'RED_GIFT': {
        'display': 'Red Gift',
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'PURPLE_CANDY': {
        'display': 'Purple Candy',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'RAW_SOULFLOW': {
        'display': 'Raw Soulflow',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'SOULFLOW': {
        'display': 'Soulflow',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'SULPHUR_ORE': {
        'display': 'Sulphur',
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'ENCHANTED_SULPHUR': {
        'display': 'Enchanted Sulphur',
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'ENCHANTED_SULPHUR_CUBE': {
        'display': 'Enchanted Sulphur Cube',
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'CORRUPTED_FRAGMENT': {
        'display': 'Corrupted Fragment',
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'COBBLESTONE': {
        'display': 'Cobblestone',
        "prices": {},
        'xp': { 'mining': 0.1 }
    },
    'ENCHANTED_COBBLESTONE': {
        'display': 'Enchanted Cobblestone',
        "prices": {},
        'xp': { 'mining': 16 }
    },
    'STONE': {
        'display': 'Stone',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0.1 }
    },
    'OBSIDIAN': {
        'display': 'Obsidian',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_OBSIDIAN': {
        'display': 'Enchanted Obsidian',
        "prices": {},
        'xp': { 'mining': 64 }
    },
    'GLOWSTONE_DUST': {
        'display': 'Glowstone Dust',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'GLOWSTONE': {
        'display': 'Glowstone',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0.8 }
    },
    'ENCHANTED_GLOWSTONE_DUST': {
        'display': 'Enchanted Glowstone Dust',
        "prices": {},
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_GLOWSTONE': {
        'display': 'Enchanted Glowstone',
        "prices": {},
        'xp': { 'mining': 6144 }  # correct inaccuracy
    },
    'GRAVEL': {
        'display': 'Gravel',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'FLINT': {
        'display': 'Flint',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_FLINT': {
        'display': 'Enchanted Flint',
        "prices": {},
        'xp': { 'mining': 32 }
    },
    'SAND': {
        'display': 'Sand',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_SAND': {
        'display': 'Enchanted Sand',
        "prices": {},
        'xp': { 'mining': 32 }
    },
    'SAND:1': {
        'display': 'Red Sand',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_RED_SAND': {
        'display': 'Enchanted Red Sand',
        "prices": {},
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_RED_SAND_CUBE': {
        'display': 'Enchanted Red Sand Cube',
        "prices": {},
        'xp': { 'mining': 5120 }
    },
    'GLASS': {
        'display': 'Glass',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'MYCEL': {
        'display': 'Mycelium',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_MYCELIUM': {
        'display': 'Enchanted Mycelium',
        "prices": {},
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_MYCELIUM_CUBE': {
        'display': 'Enchanted Mycelium Cube',
        "prices": {},
        'xp': { 'mining': 5120 }
    },
    'CLAY_BALL': {
        'display': 'Clay Ball',
        "prices": {},
        'xp': { 'fishing': 0.1 }
    },
    'CLAY': {
        'display': 'Clay',  # not in bazaar
        "prices": {},
        'xp': { 'fishing': 0.4 }
    },
    'ENCHANTED_CLAY_BALL': {
        'display': 'Enchanted Clay Ball',
        "prices": {},
        'xp': { 'fishing': 16 }
    },
    'ENCHANTED_CLAY_BLOCK': {
        'display': 'Enchanted Clay Block', # all correct
        "prices": {},
        'xp': { 'fishing': 2560 }
    },
    'CLAY_BRICK': {
        'display': 'Brick',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'BRICK': {
        'display': 'Bricks',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0 }
    },
    'ICE': {
        'display': 'Ice',
        "prices": {},
        'xp': { 'mining': 0.5 }
    },
    'PACKED_ICE': {
        'display': 'Packed Ice',
        "prices": {},
        'xp': { 'mining': 4.5 }
    },
    'ENCHANTED_ICE': {
        'display': 'Enchanted Ice',
        "prices": {},
        'xp': { 'mining': 80 }
    },
    'ENCHANTED_PACKED_ICE': {
        'display': 'Enchanted Packed Ice',
        "prices": {},
        'xp': { 'mining': 12800 }
    },
    'SNOW_BALL': {
        'display': 'Snowball',
        "prices": {},
        'xp': { 'mining': 0.1 }
    },
    'SNOW_BLOCK': {
        'display': 'Snow Block',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_SNOW_BLOCK': {
        'display': 'Enchanted Snow Block',
        "prices": {},
        'xp': { 'mining': 64 }
    },
    'COAL': {
        'display': 'Coal',
        "speed_boost": 5,
        "drop_multiplier": 1,
        "fuel_duration": 1800,
        "prices": {},
        'xp': { 'mining': 0.3 },
    },
    'COAL_BLOCK': {
        'display': 'Block of Coal',  # not in bazaar
        "speed_boost": 5,
        "drop_multiplier": 1,
        "fuel_duration": 18000,
        "prices": {},
        'xp': { 'mining': 2.7 },
    },
    'ENCHANTED_COAL': {
        'display': 'Enchanted Coal',
        "speed_boost": 10,
        "drop_multiplier": 1,
        "fuel_duration": 86400,
        "prices": {},
        'xp': { 'mining': 48 },
    },
    'ENCHANTED_COAL_BLOCK': {
        'display': 'Enchanted Coal Block',
        "prices": {},
        'xp': { 'mining': 7680 }
    },
    'IRON_ORE': {
        'display': 'Iron Ore',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0.3 }
    },
    'IRON_INGOT': {
        'display': 'Iron Ingot',
        "prices": {},
        'xp': { 'mining': 0.3 }
    },
    'IRON_BLOCK': {
        'display': 'Block of Iron',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 2.7 }
    },
    'ENCHANTED_IRON': {
        'display': 'Enchanted Iron Ingot',
        "prices": {},
        'xp': { 'mining': 48 }
    },
    'ENCHANTED_IRON_BLOCK': {
        'display': 'Enchanted Iron Block',
        "prices": {},
        'xp': { 'mining': 7680 }
    },
    'GOLD_ORE': {
        'display': 'Gold Ore',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'GOLD_INGOT': {
        'display': 'Gold Ingot',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'GOLD_BLOCK': {
        'display': 'Block of Gold',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 3.6 }
    },
    'ENCHANTED_GOLD': {
        'display': 'Enchanted Gold Ingot',
        "prices": {},
        'xp': { 'mining': 64 }
    },
    'ENCHANTED_GOLD_BLOCK': {
        'display': 'Enchanted Gold Block',  # correct
        "prices": {},
        'xp': { 'mining': 10240 }
    },
    'DIAMOND': {
        'display': 'Diamond',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'DIAMOND_BLOCK': {
        'display': 'Block of Diamond',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 3.6 }
    },
    'ENCHANTED_DIAMOND': {
        'display': 'Enchanted Diamond',
        "prices": {},
        'xp': { 'mining': 64 }
    },
    'ENCHANTED_DIAMOND_BLOCK': {
        'display': 'Enchanted Diamond Block',
        "prices": {},
        'xp': { 'mining': 10240 }
    },
    'INK_SACK:4': {
        'display': 'Lapis Lazuli',
        "prices": {},
        'xp': { 'mining': 0.1 }
    },
    'LAPIS_BLOCK': {
        'display': 'Block of Lapis Lazuli',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 0.9 }
    },
    'ENCHANTED_LAPIS_LAZULI': {
        'display': 'Enchanted Lapis Lazuli',
        "prices": {},
        'xp': { 'mining': 16 }
    },
    'ENCHANTED_LAPIS_LAZULI_BLOCK': {
        'display': 'Enchanted Lapis Lazuli Block',
        "prices": {},
        'xp': { 'mining': 2560 }
    },
    'REDSTONE': {
        'display': 'Redstone Dust',
        "prices": {},
        'xp': { 'mining': 0.2 }
    },
    'REDSTONE_BLOCK': {
        'display': 'Block of Redstone',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 1.8 }
    },
    'ENCHANTED_REDSTONE': {
        'display': 'Enchanted Redstone Dust',
        "prices": {},
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_REDSTONE_BLOCK': {
        'display': 'Enchanted Redstone Block',
        "prices": {},
        'xp': { 'mining': 5120 }
    },
    'EMERALD': {
        'display': 'Emerald',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'EMERALD_BLOCK': {
        'display': 'Block of Emerald',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 3.6 }
    },
    'ENCHANTED_EMERALD': {
        'display': 'Enchanted Emerald',
        "prices": {},
        'xp': { 'mining': 64 }
    },
    'ENCHANTED_EMERALD_BLOCK': {
        'display': 'Enchanted Emerald Block',
        "prices": {},
        'xp': { 'mining': 10240 }
    },
    'QUARTZ': {
        'display': 'Nether Quartz',
        "prices": {},
        'xp': { 'mining': 0.3 }
    },
    'QUARTZ_BLOCK': {
        'display': 'Block of Quartz',  # not in bazaar
        "prices": {},
        'xp': { 'mining': 1.2 }
    },
    'ENCHANTED_QUARTZ': {
        'display': 'Enchanted Nether Quartz',
        "prices": {},
        'xp': { 'mining': 48 }
    },
    'ENCHANTED_QUARTZ_BLOCK': {
        'display': 'Enchanted Quartz Block',
        "prices": {},
        'xp': { 'mining': 7680 }
    },
    'ENDER_STONE': {
        'display': 'End Stone',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_ENDSTONE': {
        'display': 'Enchanted End Stone',
        "prices": {},
        'xp': { 'mining': 64 }  # correct
    },
    'MITHRIL_ORE': {
        'display': 'Mithril',
        "prices": {},
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_MITHRIL': {
        'display': 'Enchanted Mithril',
        "prices": {},
        'xp': { 'mining': 64 }
    },
    'HARD_STONE': {
        'display': 'Hard Stone',
        "prices": {},
        'xp': { 'mining': 0.1 }
    },
    'ENCHANTED_HARD_STONE': {
        'display': 'Enchanted Hard Stone',
        "prices": {},
        'xp': { 'mining': 57.6 }
    },
    'CONCENTRATED_STONE': {
        'display': 'Concentrated Stone',  # correct
        "prices": {},
        'xp': { 'mining': 33177.6 }
    },
    'WHEAT': {
        'display': 'Wheat',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'HAY_BLOCK': {
        'display': 'Hay Bale',  # not produced anymore by minions
        "prices": {},
        'xp': { 'farming': 1.8 }
    },
    'SEEDS': {
        'display': 'Seeds',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_BREAD': {
        'display': 'Enchanted Bread',
        "speed_boost": 5,
        "drop_multiplier": 1,
        "fuel_duration": 43200,
        "prices": {},
        'xp': { 'farming': 1.8 },  # not produced anymore by minions
    },
    'ENCHANTED_WHEAT': {
        'display': 'Enchanted Wheat',
        "prices": {},
        'xp': { 'farming': 32 }  # correct
    },
    'ENCHANTED_HAY_BALE': {
        'display': 'Enchanted Hay Bale',
        "prices": {},
        'xp': { 'farming': 5120 }  # correct
    },
    'ENCHANTED_SEEDS': {
        'display': 'Enchanted Seeds',
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'BOX_OF_SEEDS': {
        'display': 'Box of Seeds',
        "prices": {},
        'xp': { 'farming': 2560 }
    },
    'MELON': {
        'display': 'Melon Slice',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'MELON_BLOCK': {
        'display': 'Melon',
        "prices": {},
        'xp': { 'farming': 0.9 }
    },
    'ENCHANTED_MELON': {
        'display': 'Enchanted Melon Slice',
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_MELON_BLOCK': {
        'display': 'Enchanted Melon',
        "prices": {},
        'xp': { 'farming': 2560 }
    },
    'PUMPKIN': {
        'display': 'Pumpkin',
        "prices": {},
        'xp': { 'farming': 0.3 }
    },
    'ENCHANTED_PUMPKIN': {
        'display': 'Enchanted Pumpkin',
        "prices": {},
        'xp': { 'farming': 48 }
    },
    'POLISHED_PUMPKIN': {
        'display': 'Polished Pumpkin',
        "prices": {},
        'xp': { 'farming': 7680 }
    },
    'CARROT_ITEM': {
        'display': 'Carrot',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_CARROT': {
        'display': 'Enchanted Carrot',  # correct
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_GOLDEN_CARROT': {
        'display': 'Enchanted Golden Carrot',
        "prices": {},
        'xp': { 'farming': 0 }  # correct inaccuracy (2025-12-18)
    },
    'POTATO_ITEM': {
        'display': 'Potato',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_POTATO': {
        'display': 'Enchanted Potato',  # correct
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_BAKED_POTATO': {
        'display': 'Enchanted Baked Potato',
        "prices": {},
        'xp': { 'farming': 2560 }
    },
    "FRENCH_FRIES": {
        'display': "French Fries",
        'prices': { "npc": 1 },  # not in Item API
        'xp': { 'farming': 0 }
    },
    'RED_MUSHROOM': {
        'display': 'Red Mushroom',
        "prices": {},
        'xp': { 'farming': 0.3 }
    },
    'BROWN_MUSHROOM': {
        'display': 'Brown Mushroom',
        "prices": {},
        'xp': { 'farming': 0.3 }
    },
    'HUGE_MUSHROOM_2': {
        'display': 'Red Mushroom Block',
        "prices": {},
        'xp': { 'farming': 0.3 }  # correct inaccuracy
    },
    'HUGE_MUSHROOM_1': {
        'display': 'Brown Mushroom Block',
        "prices": {},
        'xp': { 'farming': 0.3 }  # correct inaccuracy
    },
    'ENCHANTED_RED_MUSHROOM': {
        'display': 'Enchanted Red Mushroom',
        "prices": {},
        'xp': { 'farming': 48 }
    },
    'ENCHANTED_BROWN_MUSHROOM': {
        'display': 'Enchanted Brown Mushroom',
        "prices": {},
        'xp': { 'farming': 48 }
    },
    'ENCHANTED_HUGE_MUSHROOM_2': {
        'display': 'Enchanted Red Mushroom Block',
        "prices": {},
        'xp': { 'farming': 1536 }  # correct inaccuracy (2025-12-22)
    },
    'ENCHANTED_HUGE_MUSHROOM_1': {
        'display': 'Enchanted Brown Mushroom Block',
        "prices": {},
        'xp': { 'farming': 1536 }  # correct inaccuracy (2025-12-22)
    },
    'CACTUS': {
        'display': 'Cactus',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'INK_SACK:2': {
        'display': 'Cactus Green',  # not in bazaar
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_CACTUS_GREEN': {
        'display': 'Enchanted Cactus Green',
        "prices": {},
        'xp': { 'farming': 80 }  # correct inaccuracy
    },
    'ENCHANTED_CACTUS': {
        'display': 'Enchanted Cactus',
        "prices": {},
        'xp': { 'farming': 12800 }  # correct inaccuracy
    },
    'INK_SACK:3': {
        'display': 'Cocoa Beans',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_COCOA': {
        'display': 'Enchanted Cocoa Beans',
        "prices": {},
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_COOKIE': {
        'display': 'Enchanted Cookie',
        "prices": {},
        'xp': { 'farming': 0 }  # correct inaccuracy (2025-12-19)
    },
    'SUGAR_CANE': {
        'display': 'Sugar Cane',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_SUGAR': {
        'display': 'Enchanted Sugar',
        "prices": {},
        'xp': { 'alchemy': 16 }  # correct type
    },
    'ENCHANTED_SUGAR_CANE': {
        'display': 'Enchanted Sugar Cane',
        "prices": {},
        'xp': { 'farming': 2560 }  # correct type
    },
    'NETHER_STALK': {
        'display': 'Nether Wart',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_NETHER_STALK': {
        'display': 'Enchanted Nether Wart',  # correct
        "prices": {},
        'xp': { 'farming': 32 }
    },
    'MUTANT_NETHER_STALK': {
        'display': 'Mutant Nether Wart',  # correct
        "prices": {},
        'xp': { 'farming': 5120 }
    },
    'YELLOW_FLOWER': {
        'display': 'Dandelion',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE': {
        'display': 'Poppy',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:1': {
        'display': 'Blue Orchid',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:2': {
        'display': 'Allium',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:3': {
        'display': 'Azure Bluet',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:4': {
        'display': 'Red Tulip',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:5': {
        'display': 'Orange Tulip',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:6': {
        'display': 'White Tulip',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:7': {
        'display': 'Pink Tulip',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE:8': {
        'display': 'Oxeye Daisy',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'DOUBLE_PLANT:1': {
        'display': 'Lilac',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.2 }
    },
    'DOUBLE_PLANT:4': {
        'display': 'Peony',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.2 }
    },
    'DOUBLE_PLANT:5': {
        'display': 'Rose Bush',  # not in bazaar
        "prices": {},
        'xp': { 'foraging': 0.2 }
    },
    'ENCHANTED_DANDELION': {
        'display': 'Enchanted Dandelion',
        "prices": {},
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_POPPY': {
        'display': 'Enchanted Poppy',
        "prices": {},
        'xp': { 'foraging': 57.6 }
    },
    "WILD_ROSE": {
        'display': 'Wild Rose',
        "prices": {},
        'xp': { 'farming': 0.3 }  # correct (2025-12-17)
    },
    "ENCHANTED_WILD_ROSE": {
        'display': 'Enchanted Wild Rose',
        "prices": {},
        'xp': { 'farming': 48 }  # correct (2025-12-17)
    },
    "COMPACTED_WILD_ROSE": {
        'display': 'Compacted Wild Rose',
        "prices": {},
        'xp': { 'farming': 7680 }  # correct (2025-12-21)
    },
    "DOUBLE_PLANT": {
        'display': 'Sunflower',
        "prices": {},
        'xp': { 'farming': 0.3 }  # correct (2025-12-17)
    },
    "ENCHANTED_SUNFLOWER": {
        'display': 'Enchanted Sunflower',
        "prices": {},
        'xp': { 'farming': 48 }  # correct (2025-12-17)
    },
    "COMPACTED_SUNFLOWER": {
        'display': 'Compacted Sunflower',
        "prices": {},
        'xp': { 'farming': 7680 }  # correct (2025-12-21)
    },
    "MOONFLOWER": {
        'display': 'Moonflower',
        "prices": {},
        'xp': { 'farming': 0.3 }  # correct (2025-12-17)
    },
    "ENCHANTED_MOONFLOWER": {
        'display': 'Enchanted Moonflower',
        "prices": {},
        'xp': { 'farming': 48 }  # correct (2025-12-17)
    },
    "COMPACTED_MOONFLOWER": {
        'display': 'Compacted Moonflower',
        "prices": {},
        'xp': { 'farming': 7680 }  # correct (2025-12-21)
    },
    'RAW_FISH': {
        'display': 'Raw Cod',
        "prices": {},
        'xp': { 'fishing': 0.5 }
    },
    'RAW_FISH:1': {
        'display': 'Raw Salmon',
        "prices": {},
        'xp': { 'fishing': 0.7 }
    },
    'RAW_FISH:3': {
        'display': 'Pufferfish',
        "prices": {},
        'xp': { 'fishing': 1 }
    },
    'RAW_FISH:2': {
        'display': 'Tropical Fish',
        "prices": {},
        'xp': { 'fishing': 2 }
    },
    'PRISMARINE_CRYSTALS': {
        'display': 'Prismarine Crystals',
        "prices": {},
        'xp': { 'fishing': 0.5 }
    },
    'PRISMARINE_SHARD': {
        'display': 'Prismarine Shard',
        "prices": {},
        'xp': { 'fishing': 0.5 }
    },
    'SPONGE': {
        'display': 'Sponge',
        "prices": {},
        'xp': { 'fishing': 0.5 }
    },
    'ENCHANTED_RAW_FISH': {
        'display': 'Enchanted Raw Cod',
        "prices": {},
        'xp': { 'fishing': 80 }
    },
    'ENCHANTED_RAW_SALMON': {
        'display': 'Enchanted Raw Salmon',
        "prices": {},
        'xp': { 'fishing': 112 }
    },
    'ENCHANTED_PUFFERFISH': {
        'display': 'Enchanted Pufferfish',
        "prices": {},
        'xp': { 'fishing': 160 }
    },
    'ENCHANTED_CLOWNFISH': {
        'display': 'Enchanted Tropical Fish',
        "prices": {},
        'xp': { 'fishing': 320 }
    },
    'ENCHANTED_PRISMARINE_CRYSTALS': {
        'display': 'Enchanted Prismarine Crystals',
        "prices": {},
        'xp': { 'fishing': 40 }
    },
    'ENCHANTED_PRISMARINE_SHARD': {
        'display': 'Enchanted Prismarine Shard',
        "prices": {},
        'xp': { 'fishing': 40 }
    },
    'ENCHANTED_SPONGE': {
        'display': 'Enchanted Sponge',
        "prices": {},
        'xp': { 'fishing': 20 }
    },
    'ENCHANTED_COOKED_FISH': {
        'display': 'Enchanted Cooked Cod',  # correct
        "prices": {},
        'xp': { 'fishing': 12800 }
    },
    'ENCHANTED_COOKED_SALMON': {
        'display': 'Enchanted Cooked Salmon',
        "prices": {},
        'xp': { 'fishing': 17920 }
    },
    'ENCHANTED_WET_SPONGE': {
        'display': 'Enchanted Wet Sponge',
        "prices": {},
        'xp': { 'fishing': 800 }
    },
    'ROTTEN_FLESH': {
        'display': 'Rotten Flesh',
        "prices": {},
        'xp': { 'combat': 0.3 }
    },
    'POISONOUS_POTATO': {
        'display': 'Poisonous Potato',
        "prices": {},
        'xp': { 'farming': 0 }  # check xp amount
    },
    'ENCHANTED_ROTTEN_FLESH': {
        'display': 'Enchanted Rotten Flesh',
        "prices": {},
        'xp': { 'combat': 48 }
    },
    'ENCHANTED_POISONOUS_POTATO': {
        'display': 'Enchanted Poisonous Potato',  # check if possible to compact
        "prices": {},
        'xp': { 'farming': 0 }  # check xp amount
    },
    'ENCHANTED_ENDER_PEARL': {
        'display': 'Enchanted Ender Pearl',
        "prices": {},
        'xp': { 'combat': 9 }  # correct inaccuracy
    },
    'DYE_BYZANTIUM': {
        'display': 'Byzantium Dye',  # not in bazaar (AH), also not used
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'ABSOLUTE_ENDER_PEARL': {
        'display': 'Absolute Ender Pearl',
        "prices": {},
        'xp': { 'combat': 720 }  # correct inaccuracy
    },
    'CRUDE_GABAGOOL': {
        'display': 'Crude Gabagool',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'VERY_CRUDE_GABAGOOL': {
        'display': 'Very Crude Gabagool',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'DYE_FLAME': {
        'display': 'Flame Dye',  # not in bazaar (AH), also not used
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'CHILI_PEPPER': {
        'display': 'Chili Pepper',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'STUFFED_CHILI_PEPPER': {
        'display': 'Stuffed Chili Pepper',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'INFERNO_VERTEX': {
        'display': 'Inferno Vertex',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'INFERNO_APEX': {
        'display': 'Inferno Apex',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'REAPER_PEPPER': {
        'display': 'Reaper Pepper',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'GABAGOOL_THE_FISH': {
        'display': 'Gabagool the Fish',
        "prices": {},
        "AH": True,
        'xp': { 'combat': 0 }  # unsure if correctly implemented
    },
    'HYPERGOLIC_IONIZED_CERAMICS': {
        'display': 'Hypergolic Ionized Ceramics',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'HEMOVIBE': {
        'display': 'Hemovibe',
        "prices": {},
        'xp': { 'combat': 5 }
    },
    'HEMOGLASS': {
        'display': 'Hemoglass',
        "prices": {},
        'xp': { 'combat': 800 }  # correct
    },
    'HEMOBOMB': {  # not used?
        'display': 'Hemobomb',
        "prices": {},
        'xp': { 'combat': 0 }
    },
    'BONE': {
        'display': 'Bone',
        "prices": {},
        'xp': { 'combat': 0.2 }
    },
    'ENCHANTED_BONE': {
        'display': 'Enchanted Bone',
        "prices": {},
        'xp': { 'combat': 32 }
    },
    'SULPHUR': {
        'display': 'Gunpowder',
        "prices": {},
        'xp': { 'combat': 0.3 }
    },
    'ENCHANTED_GUNPOWDER': {
        'display': 'Enchanted Gunpowder',
        "prices": {},
        'xp': { 'combat': 48 }
    },
    'STRING': {
        'display': 'String',
        "prices": {},
        'xp': { 'combat': 0.2 }
    },
    'SPIDER_EYE': {
        'display': 'Spider Eye',
        "prices": {},
        'xp': { 'combat': 0.3 }
    },
    'ENCHANTED_STRING': {
        'display': 'Enchanted String',
        "prices": {},
        'xp': { 'combat': 38 }  # correct inaccuracy
    },
    'ENCHANTED_SPIDER_EYE': {
        'display': 'Enchanted Spider Eye',
        "prices": {},
        'xp': { 'combat': 48 }
    },
    'BLAZE_ROD': {
        'display': 'Blaze Rod',
        "prices": {},
        'xp': { 'combat': 0.3 }
    },
    'ENCHANTED_BLAZE_POWDER': {
        'display': 'Enchanted Blaze Powder',
        "prices": {},
        'xp': { 'combat': 48 }
    },
    'ENCHANTED_BLAZE_ROD': {
        'display': 'Enchanted Blaze Rod',
        "prices": {},
        'xp': { 'combat': 7680 }
    },
    'MAGMA_CREAM': {
        'display': 'Magma Cream',
        "prices": {},
        'xp': { 'combat': 0.2 }
    },
    'ENCHANTED_MAGMA_CREAM': {
        'display': 'Enchanted Magma Cream',
        "prices": {},
        'xp': { 'combat': 32 }
    },
    'WHIPPED_MAGMA_CREAM': {
        'display': 'Whipped Magma Cream',
        "prices": {},
        'xp': { 'combat': 5120 }
    },
    'ENDER_PEARL': {
        'display': 'Ender Pearl',
        "prices": {},
        'xp': { 'combat': 0.3 }
    },
    'GHAST_TEAR': {
        'display': 'Ghast Tear',
        "prices": {},
        'xp': { 'combat': 0.5 }
    },
    'ENCHANTED_GHAST_TEAR': {
        'display': 'Enchanted Ghast Tear',
        "prices": {},
        'xp': { 'combat': 7.5 }  # correct inaccuracy
    },
    'SLIME_BALL': {
        'display': 'Slimeball',
        "prices": {},
        'xp': { 'combat': 0.2 }
    },
    'SLIME_BLOCK': {
        'display': 'Slime Block',  # not in bazaar
        "prices": {},
        'xp': { 'combat': 1.8 }
    },
    'ENCHANTED_SLIME_BALL': {
        'display': 'Enchanted Slimeball',
        "prices": {},
        'xp': { 'combat': 32 }
    },
    'ENCHANTED_SLIME_BLOCK': {
        'display': 'Enchanted Slime Block',
        "prices": {},
        'xp': { 'combat': 5120 }
    },
    'RAW_BEEF': {
        'display': 'Raw Beef',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'LEATHER': {
        'display': 'Leather',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_RAW_BEEF': {
        'display': 'Enchanted Raw Beef',
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_LEATHER': {
        'display': 'Enchanted Leather',
        "prices": {},
        'xp': { 'farming': 115 }  # correct inaccuracy
    },
    'PORK': {
        'display': 'Raw Porkchop',  # correct
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_PORK': {
        'display': 'Enchanted Raw Porkchop',  # correct
        "prices": {},
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_GRILLED_PORK': {
        'display': 'Enchanted Cooked Porkchop',  # correct
        "prices": {},
        'xp': { 'farming': 5120 }
    },
    'RAW_CHICKEN': {
        'display': 'Raw Chicken',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'FEATHER': {
        'display': 'Feather',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'EGG': {
        'display': 'Egg',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_RAW_CHICKEN': {
        'display': 'Enchanted Raw Chicken',
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_FEATHER': {
        'display': 'Enchanted Feather',
        "prices": {},
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_EGG': {
        'display': 'Enchanted Egg',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "add", "items": { "EGG": 1 } },
        "prices": {},
        'xp': { 'farming': 115 },  # correct inaccuracy
    },
    'SUPER_EGG': {
        'display': 'Super Enchanted Egg',
        "prices": {},
        'xp': { 'farming': 16560 }  # check xp amount
    },
    'OMEGA_EGG': {
        'display': 'Omega Enchanted Egg',
        "prices": {},
        'xp': { 'farming': 149040 }  # check xp amount
    },
    'WOOL': {
        'display': 'White Wool',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'MUTTON': {
        'display': 'Raw Mutton',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_WOOL': {
        'display': 'Enchanted Wool',
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_MUTTON': {
        'display': 'Enchanted Raw Mutton',
        "prices": {},
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_COOKED_MUTTON': {
        'display': 'Enchanted Cooked Mutton',
        "prices": {},
        'xp': { 'farming': 2560 }
    },
    'RABBIT': {
        'display': 'Raw Rabbit',
        "prices": {},
        'xp': { 'farming': 0.1 }
    },
    'RABBIT_FOOT': {
        'display': "Rabbit's Foot",
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'RABBIT_HIDE': {
        'display': 'Rabbit Hide',
        "prices": {},
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_RABBIT': {
        'display': 'Enchanted Raw Rabbit',
        "prices": {},
        'xp': { 'farming': 16 }  # correct
    },
    'ENCHANTED_COOKED_RABBIT': {
        'display': 'Enchanted Cooked Rabbit',
        "prices": {},
        'xp': { 'farming': 2560 }  # correct
    },
    'ENCHANTED_RABBIT_FOOT': {
        'display': 'Enchanted Rabbit Foot',
        "prices": {},
        'xp': { 'farming': 32 }  # correct
    },
    'ENCHANTED_RABBIT_HIDE': {
        'display': 'Enchanted Rabbit Hide',
        "prices": {},
        'xp': { 'farming': 115 }  # correct inaccuracy
    },
    'LOG': {
        'display': 'Oak Log',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'LOG:1': {
        'display': 'Spruce Log',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'LOG:2': {
        'display': 'Birch Log',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'LOG_2:1': {
        'display': 'Dark Oak Log',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'LOG_2': {
        'display': 'Acacia Log',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'LOG:3': {
        'display': 'Jungle Log',
        "prices": {},
        'xp': { 'foraging': 0.1 }
    },
    'ENCHANTED_OAK_LOG': {
        'display': 'Enchanted Oak Log',
        "prices": {},
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_SPRUCE_LOG': {
        'display': 'Enchanted Spruce Log',
        "prices": {},
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_BIRCH_LOG': {
        'display': 'Enchanted Birch Log',
        "prices": {},
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_DARK_OAK_LOG': {
        'display': 'Enchanted Dark Oak Log',
        "prices": {},
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_ACACIA_LOG': {
        'display': 'Enchanted Acacia Log',
        "prices": {},
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_JUNGLE_LOG': {
        'display': 'Enchanted Jungle Log',
        "prices": {},
        'xp': { 'foraging': 16 }
    },

    # Minion Crafting
    'REFINED_MITHRIL': {
        'display': 'Refined Mithril',
        "prices": {}
    },
    'ENCHANTED_EYE_OF_ENDER': {
        'display': 'Enchanted Eye of Ender',
        "prices": {},
    },
    'SILVER_FANG': {  # correct: cannot be made in ghast minion
        'display': 'Silver Fang',
        "prices": {},
    },
    "REVENANT_FLESH": {
        'display': "Revenant Flesh",
        "prices": {},
    },
    "REVENANT_VISCERA": {
        'display': "Revenant Viscera",
        "prices": {},
    },
    "TARANTULA_WEB": {
        'display': "Tarantula Web",
        "prices": {},
    },
    "TARANTULA_SILK": {
        'display': "Tarantula Silk",
        "prices": {},
    },
    "NULL_SPHERE": {
        'display': "Null Sphere",
        "prices": {}
    },
    "NULL_OVOID": {
        'display': "Null Ovoid",
        "prices": {}
    },
    "DERELICT_ASHE": {
        'display': "Derelict Ashe",
        "prices": {}
    },
    "MOLTEN_POWDER": {
        'display': "Molten Powder",
        "prices": {}
    },
    'ENCHANTED_FIREWORK_ROCKET': {
        'display': 'Enchanted Firework Rocket',
        "prices": {},
    },
    'ENCHANTED_FERMENTED_SPIDER_EYE': {
        'display': 'Enchanted Fermented Spider Eye',
        "prices": {},
    },

    # Fuels
    'ENCHANTED_CHARCOAL': {
        'display': 'Enchanted Charcoal',
        "speed_boost": 20,
        "drop_multiplier": 1,
        "fuel_duration": 129600,
        "prices": {},
    },
    'HAMSTER_WHEEL': {
        'display': 'Hamster Wheel',
        "speed_boost": 50,
        "drop_multiplier": 1,
        "fuel_duration": 86400,
        "prices": {},
    },
    'FOUL_FLESH': {
        'display': 'Foul Flesh',
        "speed_boost": 90,
        "drop_multiplier": 1,
        "fuel_duration": 18000,
        "prices": {},
    },
    'CATALYST': {
        'display': 'Catalyst',
        "speed_boost": 0,
        "drop_multiplier": 3,
        "fuel_duration": 10800,
        "prices": {},
    },
    'HYPER_CATALYST': {
        'display': 'Hyper Catalyst',
        "speed_boost": 0,
        "drop_multiplier": 4,
        "fuel_duration": 21600,
        "prices": {},
    },
    'CHEESE_FUEL': {
        'display': 'Tasty Cheese',
        "speed_boost": 0,
        "drop_multiplier": 2,
        "fuel_duration": 3600,
        "prices": {},
    },
    'SOLAR_PANEL': {
        'display': 'Solar Panel',
        "speed_boost": 25,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },
    'ENCHANTED_LAVA_BUCKET': {
        'display': 'Enchanted Lava Bucket',
        "speed_boost": 25,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },
    'MAGMA_BUCKET': {
        'display': 'Magma Bucket',
        "speed_boost": 30,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },
    'PLASMA_BUCKET': {
        'display': 'Plasma Bucket',
        "speed_boost": 35,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },
    'EVERBURNING_FLAME': {
        'display': 'Everburning Flame',
        "speed_boost": 35,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "upgrade_special": {"type": "speed_bonus", "amount": 5, "affected_minions": ["combat_minion"]},  # TODO: need to check affected minions
        "prices": {},
        "recipe": {"PLASMA_BUCKET": 1, "FLAMES": 16, "ENCHANTED_SULPHUR_CUBE": 2, "ENCHANTED_RED_SAND_CUBE": 2},
    },
    'INFERNO_FUEL': {  # exact item ID does not exist
        'display': 'Inferno Minion Fuel',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "fuel_duration": 86400,
        "prices": { "custom": 1 },  # this custom price will be automatically updated by the calculator based on grade and distilate
    },
    'THORNY_VINES': {
        'display': 'Thorny Vines',
        "speed_boost": 20,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },
    'DAYSWITCH': {
        'display': 'Dayswitch',
        "speed_boost": 20,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },
    'NIGHTSWITCH': {
        'display': 'Nightswitch',
        "speed_boost": 20,
        "drop_multiplier": 1,
        "fuel_duration": -1,
        "prices": {},
    },

    # Hoppers
    'BUDGET_HOPPER': {
        'display': 'Budget Hopper',
        "hopper_selling_rate": 0.5,
        "prices": {}
    },
    'ENCHANTED_HOPPER': {
        'display': 'Enchanted Hopper',
        "hopper_selling_rate": 0.7,
        "prices": {}
    },

    # Upgrades
    'AUTO_SMELTER': {
        'display': 'Auto Smelter',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "replace", "replacement_list": smelting_data },
        "prices": {},
    },
    'COMPACTOR': {
        'display': 'Compactor',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "compact", "compacting_list": compactor_list },
        "prices": {},
    },
    'SUPER_COMPACTOR_3000': {
        'display': 'Super Compactor 3000',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "compact", "compacting_list": super_compactor_list },
        "prices": {},
    },
    'DWARVEN_COMPACTOR': {
        'display': 'Dwarven Super Compactor',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "replace, compact", "replacement_list": smelting_data, "compacting_list": super_compactor_list },
        "prices": {},
    },
    'DIAMOND_SPREADING': {
        'display': 'Diamond Spreading',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "spreading", "items": { "DIAMOND": 0.1 }},
        "prices": {},
    },
    'POTATO_SPREADING': {
        'display': 'Potato Spreading',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "spreading", "items": { "POTATO_ITEM": 0.05 }},
        "prices": {},
    },
    'MINION_EXPANDER': {
        'display': 'Minion Expander',
        "speed_boost": 5,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "expand" },
        "prices": {},
    },
    'FLINT_SHOVEL': {
        'display': 'Flint Shovel',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "replace", "replacement_list": { "GRAVEL": "FLINT" } },
        "prices": {},
        "recipe": {"FLINT": 10},  # +/- 2 sticks
    },
    'FLYCATCHER_UPGRADE': {
        'display': 'Flycatcher',
        "speed_boost": 20,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "None" },
        "prices": {},
    },
    'KRAMPUS_HELMET': {
        'display': 'Krampus Helmet',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "spreading", "items": { "RED_GIFT": 0.000045 }},
        "prices": {},
        "AH": True,
    },
    'LESSER_SOULFLOW_ENGINE': {
        'display': 'Lesser Soulflow Engine',
        "speed_boost": 0,
        "drop_multiplier": 0.5,
        "upgrade_special": { "type": "cooldown", "items": { "RAW_SOULFLOW": 1 }, "cooldown": 180, "offline_cooldown": 185 },  # offline cooldown not confirmed
        "prices": {},
    },
    'SOULFLOW_ENGINE': {
        'display': 'Soulflow Engine',
        "speed_boost": 0,
        "drop_multiplier": 0.5,
        "upgrade_special": { "type": "cooldown", "items": { "RAW_SOULFLOW": 1 }, "cooldown": 90, "offline_cooldown": 105 },  # offline cooldown not confirmed
        "prices": {},
    },
    'CORRUPT_SOIL': {
        'display': 'Corrupt Soil',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "add", "items": { "SULPHUR_ORE": 1, "CORRUPTED_FRAGMENT": 1 } },
        "affected_minions": [],
        "prices": {},
    },
    'BERBERIS_FUEL_INJECTOR': {
        'display': 'Berberis Fuel Injector',
        "speed_boost": 15,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "cooldown", "items": { "LUSH_BERBERIS": 1 }, "cooldown": 300, "offline_cooldown": 300 },  # offline cooldown not confirmed
        "affected_minions": [],
        "prices": {},
    },
    'ENCHANTED_SHEARS': {
        'display': 'Enchanted Shears',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "add", "items": { "WOOL": 2 } },  # Base drop wool gets set to 0. For online, its possible that the sheep regrow their wool, making it up to 3 wool per spawn and harvest, needs testing
        "prices": { "npc": 0 },
        "recipe": {"ENCHANTED_IRON": 2},
    },
    'SLEEPY_HOLLOW': {
        'display': 'Sleepy Hollow',
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "spreading", "items": { "PURPLE_CANDY": 0.00015 }},
        "prices": { "npc": 0 },
    },
    "HUNTER_KNIFE": {
        'display': "Hunter Knife",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "upgrade_special": { "type": "replace", "replacement_list": { "POTATO_ITEM": "FRENCH_FRIES" } },
        "prices": { "custom": 500000 },  # 500k from Rusty
    },

    # Beacons
    "BEACON_1": {
        'display': "Beacon I",
        "speed_boost": 2,
        'prices': {},
        "recipe": { "ENCHANTED_MITHRIL": 192, "STARFALL": 64 }
    },
    "BEACON_2": {
        'display': "Beacon II",
        "speed_boost": 4,
        'prices': {},
        "recipe": { "ENCHANTED_MITHRIL": 192, "STARFALL": 64, "REFINED_MITHRIL": 5 }
    },
    "BEACON_3": {
        'display': "Beacon III",
        "speed_boost": 6,
        'prices': {},
        "recipe": { "ENCHANTED_MITHRIL": 192, "STARFALL": 64, "REFINED_MITHRIL": 15 }
    },
    "BEACON_4": {
        'display': "Beacon IV",
        "speed_boost": 8,
        'prices': {},
        "recipe": { "ENCHANTED_MITHRIL": 192, "STARFALL": 64, "REFINED_MITHRIL": 35, "PLASMA": 1 }
    },
    "BEACON_5": {
        'display': "Beacon V",
        "speed_boost": 10,
        'prices': {},
        "recipe": { "ENCHANTED_MITHRIL": 192, "STARFALL": 64, "REFINED_MITHRIL": 75, "PLASMA": 6 }
    },
    "POWER_CRYSTAL": {
        'display': 'Power Crystal',
        "prices": {},
        'fuel_duration': 172800
    },
    "SCORCHED_POWER_CRYSTAL": {
        'display': 'Scorched Power Crystal',
        "speed_boost": 1,
        "prices": {},
        'fuel_duration': 172800
    },

    # Floating Crystals
    "FARM_CRYSTAL": {
        'display': "Farm Crystal",
        "speed_boost": 10,
        "affected_minions": ["farming_crop_minion"],
        'prices': {},
        "recipe": { "ENCHANTED_PUMPKIN": 96, "ENCHANTED_QUARTZ": 1 }
    },
    "WOODCUTTING_CRYSTAL": {
        'display': "Woodcutting Crystal",
        "speed_boost": 10,
        "affected_minions": ["foraging_minion"],
        'prices': {},
        "recipe": { "ENCHANTED_SPRUCE_LOG": 96, "ENCHANTED_QUARTZ": 1 }
    },
    "MITHRIL_CRYSTAL": {
        'display': "Mithril Crystal",
        "speed_boost": 10,
        "affected_minions": ["mining_minion"],
        'prices': {},
        "recipe": { "ENCHANTED_MITHRIL": 16, "ENCHANTED_QUARTZ": 1 }
    },
    "WINTER_ISLAND_CRYSTAL": {
        'display': "Winter Crystal",
        "speed_boost": 5,
        "affected_minions": ["winter_minion"],
        'prices': {},
        "recipe": { "WINTER_ISLAND": 1 }
    },
    "MITHRIL_WINTER_CRYSTAL": {
        'display': "Mithril + Winter Crystal",  # not a real item
        "speed_boost": 15,  # correct
        "affected_minions": ["winter_minion"],
        'prices': {},
        "recipe": { "MITHRIL_CRYSTAL": 1, "WINTER_ISLAND_CRYSTAL": 1 }
    },

    # Chests
    "SMALL_ENCHANTED_CHEST": {
        'display': "Small Storage",
        "storage_slots": 3,
        'prices': {}
    },
    "MEDIUM_ENCHANTED_CHEST": {
        'display': "Medium Storage",
        "storage_slots": 9,
        'prices': {}
    },
    "LARGE_ENCHANTED_CHEST": {
        'display': "Large Storage",
        "storage_slots": 15,
        'prices': {}
    },
    "XLARGE_ENCHANTED_CHEST": {
        'display': "X-Large Storage",
        "storage_slots": 21,
        'prices': {}
    },
    "XXLARGE_ENCHANTED_CHEST": {
        'display': "XX-Large Storage",
        "storage_slots": 27,
        'prices': {}
    },

    # Other Upgrades
    "MITHRIL_INFUSION": {
        'display': "Mithril Infusion",
        "speed_boost": 10,
        "prices": {}
    },
    'CAPSAICIN_EYEDROPS_NO_CHARGES': {
        'display': 'Capsaicin Eyedrops',
        "prices": {}
    },
    "FREE_WILL": {
        'display': "Free Will",
        "speed_boost": 10,
        'prices': {}
    },
    "POSTCARD": {
        'display': "Postcard",
        "speed_boost": 5,
        'prices': {},
        "AH": True
    },
    "POTATO_TALISMAN": {
        'display': "Potato Talisman",
        "speed_boost": 5,
        "affected_minions": ["POTATO_MINION"],
        'prices': {},
        "AH": True
    },
    "POTATO_RING": {
        'display': "Potato Ring",
        "speed_boost": 10,
        "affected_minions": ["POTATO_MINION"],
        'prices': {},
        "AH": True
    },

    # Other Crafting Materials
    'INFERNO_FUEL_BLOCK': {
        'display': 'Inferno Fuel Block',
        "prices": {}
    },
    'HYPERGOLIC_GABAGOOL': {
        'display': 'Hypergolic Gabagool',
        "prices": {}
    },
    'HEAVY_GABAGOOL': {
        'display': 'Heavy Gabagool',
        "prices": {}
    },
    'FUEL_GABAGOOL': {
        'display': 'Fuel Gabagool',
        "prices": {}
    },
    'MAGMA_CREAM_DISTILLATE': {
        'display': 'Magma Cream Distillate',
        "prices": {}
    },
    'BLAZE_ROD_DISTILLATE': {
        'display': 'Blaze Rod Distillate',
        "prices": {}
    },
    'NETHER_STALK_DISTILLATE': {
        'display': 'Nether Wart Distillate',
        "prices": {}
    },
    'GLOWSTONE_DUST_DISTILLATE': {
        'display': 'Glowstone Distillate',
        "prices": {}
    },
    'CRUDE_GABAGOOL_DISTILLATE': {
        'display': 'Gabagool Distillate',
        "prices": {}
    },
    "STARFALL": {
        'display': "Starfall",
        "prices": {}
    },
    "PLASMA": {
        'display': "Plasma",
        "prices": {}
    },
    "FLAMES": {
        'display': "Flames",
        "prices": {}
    },
    "PRISMARINE:1": {  # not used?
        'display': "Prismarine Bricks",
        "prices": {},
        'xp': { 'mining': 0 }
    },
    "PET_ITEM_EXP_SHARE_DROP": {
        "display": "Exp Share Core",
        "prices": {}
    },
    "WINTER_ISLAND": {
        "display": "Winter Island",
        "prices": {},
        "AH": True
    },

    # Pet Items
    'PET_ITEM_MINING_SKILL_BOOST_COMMON': {
        'display': 'Common Mining Exp Boost',  # not in bazaar (Zog)
        "rarity": "Common",
        "exp_boost_type": "mining",
        "exp_boost_amount": 20,
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_MINING_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Mining Exp Boost',  # not in bazaar (Zog)
        "rarity": "Uncommon",
        "exp_boost_type": "mining",
        "exp_boost_amount": 30,
        'prices': { 'custom': 250000 }
    },
    'PET_ITEM_MINING_SKILL_BOOST_RARE': {
        'display': 'Rare Mining Exp Boost',
        "rarity": "Rare",
        "exp_boost_type": "mining",
        "exp_boost_amount": 40,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_FARMING_SKILL_BOOST_COMMON': {
        'display': 'Common Farming Exp Boost',  # not in bazaar (Zog)
        "rarity": "Common",
        "exp_boost_type": "farming",
        "exp_boost_amount": 20,
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_FARMING_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Farming Exp Boost',
        "rarity": "Uncommon",
        "exp_boost_type": "farming",
        "exp_boost_amount": 30,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_FARMING_SKILL_BOOST_RARE': {
        'display': 'Rare Farming Exp Boost',  # not in bazaar (Zog)
        "rarity": "Rare",
        "exp_boost_type": "farming",
        "exp_boost_amount": 40,
        'prices': { 'custom': 500000 }
    },
    'PET_ITEM_FARMING_SKILL_BOOST_EPIC': {
        'display': 'Epic Farming Exp Boost',  # not in bazaar (Duncan)
        "rarity": "Epic",
        "exp_boost_type": "farming",
        "exp_boost_amount": 50,
        'prices': { 'custom': 1500000 }
    },
    'PET_ITEM_FISHING_SKILL_BOOST_COMMON': {
        'display': 'Common Fishing Exp Boost',  # not in bazaar (Zog)
        "rarity": "Common",
        "exp_boost_type": "fishing",
        "exp_boost_amount": 20,
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_FISHING_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Fishing Exp Boost',
        "rarity": "Uncommon",
        "exp_boost_type": "fishing",
        "exp_boost_amount": 30,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_FISHING_SKILL_BOOST_RARE': {
        'display': 'Rare Fishing Exp Boost',
        "rarity": "Rare",
        "exp_boost_type": "fishing",
        "exp_boost_amount": 40,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_FISHING_SKILL_BOOST_EPIC': {
        'display': 'Epic Fishing Exp Boost',
        "rarity": "Epic",
        "exp_boost_type": "fishing",
        "exp_boost_amount": 50,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_COMMON': {
        'display': 'Common Combat Exp Boost',  # not in bazaar (Zog)
        "rarity": "Common",
        "exp_boost_type": "combat",
        "exp_boost_amount": 20,
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Combat Exp Boost',
        "rarity": "Uncommon",
        "exp_boost_type": "combat",
        "exp_boost_amount": 30,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_RARE': {
        'display': 'Rare Combat Exp Boost',
        "rarity": "Rare",
        "exp_boost_type": "combat",
        "exp_boost_amount": 40,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_EPIC': {
        'display': 'Epic Combat Exp Boost',
        "rarity": "Epic",
        "exp_boost_type": "combat",
        "exp_boost_amount": 50,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_FORAGING_SKILL_BOOST_COMMON': {
        'display': 'Common Foraging Exp Boost',  # not in bazaar (Zog)
        "rarity": "Common",
        "exp_boost_type": "foraging",
        "exp_boost_amount": 20,
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_FORAGING_SKILL_BOOST_EPIC': {
        'display': 'Epic Foraging Exp Boost',
        "rarity": "Epic",
        "exp_boost_type": "foraging",
        "exp_boost_amount": 50,
        'prices': {},
        "AH": True
    },
    'PET_ITEM_ALL_SKILLS_BOOST_COMMON': {
        'display': 'All Skills Exp Boost',  # not in bazaar (Zog)
        "rarity": "Common",
        "exp_boost_type": "all",
        "exp_boost_amount": 10,
        'prices': { 'custom': 50000 }
    },
    'ALL_SKILLS_SUPER_BOOST': {
        'display': 'All Skills Exp Super-Boost',
        "rarity": "Uncommon",
        "exp_boost_type": "all",
        "exp_boost_amount": 20,
        'prices': {},
        "AH": True
    },
    "PET_ITEM_EXP_SHARE": {
        'display': "Exp Share",
        "rarity": "Epic",
        'prices': {},
        'recipe': {"PET_ITEM_EXP_SHARE_DROP": 1, "ENCHANTED_GOLD": 72}
    },
    "SUPER_SCRUBBER": {
        "display": "Super Scrubber",
        "prices": { "custom": 25000 },  # not in bazaar (Plumber Joe)
    },

    # Attribute Shards
    "SHARD_TOUCAN": {
        "display": "Toucan",
        "prices": {}
    },
    "SHARD_FALCON": {
        "display": "Falcon",
        "prices": {}
    },

    # Minions
    # average drop amount from hypixel skyblock fandom wiki or self tested
    "CUSTOM_MINION": {
        'display': 'Custom',
        "drops": { "CUSTOM": 1 },
        "speed": { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12 },
        "afkcorrupt": 2,
        "notes": { "Custom": "Custom Minion does not exist", "AFK": "multiple corrupt drops" },
        "tags": ["custom_object"]
    },
    "COBBLESTONE_MINION": {
        'display': 'Cobblestone',
        "drops": { "COBBLESTONE": 1 },
        "speed": { 1: 14, 2: 14, 3: 12, 4: 12, 5: 10, 6: 10, 7: 9, 8: 9, 9: 8, 10: 8, 11: 7, 12: 6 },
        "notes": { "Special Layout": "only harvests (cobble generator)" },
        "tags": ["mining_minion"]
    },
    "OBSIDIAN_MINION": {
        'display': 'Obsidian',
        "drops": { "OBSIDIAN": 1 },
        "speed": { 1: 45, 2: 45, 3: 42, 4: 42, 5: 39, 6: 39, 7: 35, 8: 35, 9: 30, 10: 30, 11: 24, 12: 21 },
        "tags": ["mining_minion"]
    },
    "GLOWSTONE_MINION": {
        'display': 'Glowstone',
        "drops": { "GLOWSTONE_DUST": 3 },
        "speed": { 1: 25, 2: 25, 3: 23, 4: 23, 5: 21, 6: 21, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13, 12: 11 },
        "tags": ["mining_minion"]
    },
    "GRAVEL_MINION": {
        'display': 'Gravel',
        "drops": { "GRAVEL": 0.9, "FLINT": 0.1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "notes": { "Special Layout": "only spawn (gravity blocks)" },
        "tags": ["mining_minion"]
    },
    "SAND_MINION": {
        'display': 'Sand',
        "drops": { "SAND": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13 },
        "notes": { "Special Layout": "only spawn (gravity blocks)" },
        "tags": ["mining_minion"]
    },
    "RED_SAND_MINION": {
        'display': 'Red Sand',
        "drops": { "SAND:1": 1 },
        "speed": { 1: 26, 2: 25, 3: 24, 4: 23, 5: 22, 6: 21, 7: 20, 8: 19, 9: 18, 10: 16, 11: 13, 12: 11 },
        "storage": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15 },
        "notes": { "Special Layout": "only spawn (gravity blocks)" },
        "tags": ["mining_minion"]
    },
    "MYCELIUM_MINION": {
        'display': 'Mycelium',
        "drops": { "MYCEL": 1 },
        "speed": { 1: 26, 2: 25, 3: 24, 4: 23, 5: 22, 6: 21, 7: 20, 8: 19, 9: 18, 10: 16, 11: 13, 12: 11 },
        "storage": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15 },
        "notes": { "Special Layout": "only harvests (natural spreading)" },
        "tags": ["mining_minion"]
    },
    "CLAY_MINION": {
        'display': 'Clay',
        "drops": { "CLAY_BALL": 4 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 27.5, 6: 27.5, 7: 24, 8: 24, 9: 20, 10: 20, 11: 16, 12: 14 }
    },
    "ICE_MINION": {
        'display': 'Ice',
        "drops": { "ICE": 1 },
        "speed": { 1: 14, 2: 14, 3: 12, 4: 12, 5: 10, 6: 10, 7: 9, 8: 9, 9: 8, 10: 8, 11: 7, 12: 6 },
        "notes": { "Special Layout": "only harvests (frozen biome)" },
        "tags": ["mining_minion", "winter_minion"]
    },
    "SNOW_MINION": {
        'display': 'Snow',
        "drops": { "SNOW_BALL": 4 },
        "speed": { 1: 13, 2: 13, 3: 12, 4: 12, 5: 11, 6: 11, 7: 9.5, 8: 9.5, 9: 8, 10: 8, 11: 6.5, 12: 5.8 },
        "tags": ["mining_minion", "winter_minion"]
    },
    "COAL_MINION": {
        'display': 'Coal',
        "drops": { "COAL": 1 },
        "speed": { 1: 15, 2: 15, 3: 13, 4: 13, 5: 12, 6: 12, 7: 10, 8: 10, 9: 9, 10: 9, 11: 7, 12: 6 },
        "tags": ["mining_minion"]
    },
    "IRON_MINION": {
        'display': 'Iron',
        "drops": { "IRON_ORE": 1 },
        "speed": { 1: 17, 2: 17, 3: 15, 4: 15, 5: 14, 6: 14, 7: 12, 8: 12, 9: 10, 10: 10, 11: 8, 12: 7 },
        "tags": ["mining_minion"]
    },
    "GOLD_MINION": {
        'display': 'Gold',
        "drops": { "GOLD_ORE": 1 },
        "speed": { 1: 22, 2: 22, 3: 20, 4: 20, 5: 18, 6: 18, 7: 16, 8: 16, 9: 14, 10: 14, 11: 11, 12: 9 },
        "tags": ["mining_minion"]
    },
    "DIAMOND_MINION": {
        'display': 'Diamond',
        "drops": { "DIAMOND": 1 },
        "speed": { 1: 29, 2: 29, 3: 27, 4: 27, 5: 25, 6: 25, 7: 22, 8: 22, 9: 19, 10: 19, 11: 15, 12: 12 },
        "tags": ["mining_minion"]
    },
    "LAPIS_MINION": {
        'display': 'Lapis',
        "drops": { "INK_SACK:4": 6 },  # correct
        "speed": { 1: 29, 2: 29, 3: 27, 4: 27, 5: 25, 6: 25, 7: 23, 8: 23, 9: 21, 10: 21, 11: 18, 12: 16 },
        "tags": ["mining_minion"]
    },
    "REDSTONE_MINION": {
        'display': 'Redstone',
        "drops": { "REDSTONE": 4.5 },
        "speed": { 1: 29, 2: 29, 3: 27, 4: 27, 5: 25, 6: 25, 7: 23, 8: 23, 9: 21, 10: 21, 11: 18, 12: 16 },
        "tags": ["mining_minion"]
    },
    "EMERALD_MINION": {
        'display': 'Emerald',
        "drops": { "EMERALD": 1 },
        "speed": { 1: 28, 2: 28, 3: 26, 4: 26, 5: 24, 6: 24, 7: 21, 8: 21, 9: 18, 10: 18, 11: 14, 12: 12 },
        "tags": ["mining_minion"]
    },
    "QUARTZ_MINION": {
        'display': 'Quartz',
        "drops": { "QUARTZ": 1 },
        "speed": { 1: 22.5, 2: 22.5, 3: 21, 4: 21, 5: 19, 6: 19, 7: 17, 8: 17, 9: 14.5, 10: 14.5, 11: 11.5, 12: 10 },
        "tags": ["mining_minion"]
    },
    "END_STONE_MINION": {
        'display': 'End Stone',
        "drops": { "ENDER_STONE": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13 },
        "tags": ["mining_minion"]
    },
    "MITHRIL_MINION": {
        'display': 'Mithril',
        "drops": { "MITHRIL_ORE": 2 },
        "speed": { 1: 80, 2: 80, 3: 75, 4: 75, 5: 70, 6: 70, 7: 65, 8: 65, 9: 60, 10: 60, 11: 55, 12: 50 },
        "tags": ["mining_minion"]
    },
    "HARD_STONE_MINION": {
        'display': 'Hard Stone',
        "drops": { "HARD_STONE": 2 },  # correct
        "speed": { 1: 14, 2: 14, 3: 12, 4: 12, 5: 10, 6: 10, 7: 9, 8: 9, 9: 8, 10: 8, 11: 7, 12: 6 },
        "tags": ["mining_minion"]
    },
    "WHEAT_MINION": {
        'display': 'Wheat',
        "drops": { "WHEAT": 1, "SEEDS": 1.5 },  # correct
        "speed": { 1: 15, 2: 15, 3: 13, 4: 13, 5: 11, 6: 11, 7: 10, 8: 10, 9: 9, 10: 9, 11: 8, 12: 7 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "notes": { "AFK": "can skip planting with Wheat Crystal (not 100% of the time, depends on minion speed)" },
        "tags": ["farming_crop_minion"]
    },
    "MELON_MINION": {
        'display': 'Melon',
        "drops": { "MELON": 5 },
        "speed": { 1: 24, 2: 24, 3: 22.5, 4: 22.5, 5: 21, 6: 21, 7: 18.5, 8: 18.5, 9: 16, 10: 16, 11: 13, 12: 10 },
        "notes": { "AFK": "only harvests" },
        "tags": ["farming_crop_minion"]
    },
    "PUMPKIN_MINION": {
        'display': 'Pumpkin',
        "drops": { "PUMPKIN": 1 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 27, 6: 27, 7: 24, 8: 24, 9: 20, 10: 20, 11: 16, 12: 12 },
        "notes": { "AFK": "only harvests" },
        "tags": ["farming_crop_minion"]
    },
    "CARROT_MINION": {
        'display': 'Carrot',
        "drops": { "CARROT_ITEM": 3 },
        "speed": { 1: 20, 2: 20, 3: 18, 4: 18, 5: 16, 6: 16, 7: 14, 8: 14, 9: 12, 10: 12, 11: 10, 12: 8 },
        "tags": ["farming_crop_minion"]
    },
    "POTATO_MINION": {
        'display': 'Potato',
        "drops": { "POTATO_ITEM": 3 },
        "speed": { 1: 20, 2: 20, 3: 18, 4: 18, 5: 16, 6: 16, 7: 14, 8: 14, 9: 12, 10: 12, 11: 10, 12: 8 },
        "tags": ["farming_crop_minion"]
    },
    "MUSHROOM_MINION": {
        'display': 'Mushroom',
        "drops": { "RED_MUSHROOM": 0.5, "BROWN_MUSHROOM": 0.5 },
        "speed": { 1: 30, 2: 30, 3: 28, 4: 28, 5: 26, 6: 26, 7: 23, 8: 23, 9: 20, 10: 20, 11: 16, 12: 12 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "tags": ["farming_crop_minion"]
    },
    "CACTUS_MINION": {
        'display': 'Cactus',
        "drops": { "CACTUS": 3 },
        "speed": { 1: 27, 2: 27, 3: 25, 4: 25, 5: 23, 6: 23, 7: 21, 8: 21, 9: 18, 10: 18, 11: 15, 12: 12 },
        "tags": ["farming_crop_minion"]
    },
    "COCOA_BEANS_MINION": {
        'display': 'Cocoa Beans',
        "drops": { "INK_SACK:3": 3 },
        "speed": { 1: 27, 2: 27, 3: 25, 4: 25, 5: 23, 6: 23, 7: 21, 8: 21, 9: 18, 10: 18, 11: 15, 12: 12 },
        "tags": ["farming_crop_minion"]
    },
    "SUGAR_CANE_MINION": {
        'display': 'Sugar Cane',
        "drops": { "SUGAR_CANE": 3 },
        "speed": { 1: 22, 2: 22, 3: 20, 4: 20, 5: 18, 6: 18, 7: 16, 8: 16, 9: 14.5, 10: 14.5, 11: 12, 12: 9 },
        "tags": ["farming_crop_minion"]
    },
    "NETHER_WART_MINION": {
        'display': 'Nether Wart',
        "drops": { "NETHER_STALK": 2.5 },  # correct (2025-10-18)
        "speed": { 1: 50, 2: 50, 3: 47, 4: 47, 5: 44, 6: 44, 7: 41, 8: 41, 9: 38, 10: 38, 11: 32, 12: 27 },
        "tags": ["farming_crop_minion"]
    },
    "FLOWER_MINION": {
        'display': 'Flower',
        "drops": { "YELLOW_FLOWER": 0.35, "RED_ROSE": 0.15, "RED_ROSE:1": 0.5 / 11, "RED_ROSE:2": 0.5 / 11, "RED_ROSE:3": 0.5 / 11, "RED_ROSE:4": 0.5 / 11, "RED_ROSE:5": 0.5 / 11, "RED_ROSE:6": 0.5 / 11, "RED_ROSE:7": 0.5 / 11, "RED_ROSE:8": 0.5 / 11, "DOUBLE_PLANT:1": 0.5 / 11, "DOUBLE_PLANT:4": 0.5 / 11, "DOUBLE_PLANT:5": 0.5 / 11 },  # check
        "speed": { 1: 30, 2: 29, 3: 28, 4: 27, 5: 26, 6: 25, 7: 24, 8: 23, 9: 22, 10: 20, 11: 18, 12: 15 },
        "storage": { 1: 15, 2: 15, 3: 15, 4: 15, 5: 15, 6: 15, 7: 15, 8: 15, 9: 15, 10: 15, 11: 15, 12: 15 },
        "notes": { "Special Layout": "only spawn, no large flowers (water flushing, low roof)" },
        "tags": ["foraging_minion"]  # correct
    },
    "SUNFLOWER_MINION": {
        'display': 'Sunflower',
        "drops": { "DOUBLE_PLANT": 1, "MOONFLOWER": 1 },
        "speed": { 1: 24, 2: 23, 3: 22, 4: 21, 5: 20, 6: 19, 7: 18, 8: 17, 9: 16, 10: 15, 11: 14, 12: 13},
        "storage": { 1: 2, 2: 3, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15 },
        "tags": ["farming_crop_minion"]
    },
    "FISHING_MINION": {
        'display': 'Fishing',
        "drops": { "RAW_FISH": 0.54, "RAW_FISH:1": 0.225, "RAW_FISH:3": 0.117, "RAW_FISH:2": 0.036, "PRISMARINE_CRYSTALS": (2 + (11 / 15)) / 100, "PRISMARINE_SHARD": (2 + (11 / 15)) / 100, "SPONGE": (2 + (11 / 15)) / 100 },  # good average (2025-10-24)
        "speed": { 1: 75, 2: 75, 3: 67, 4: 67, 5: 59, 6: 59, 7: 51, 8: 51, 9: 43, 10: 43, 11: 35, 12: 30 },
        "storage": { 1: 10, 2: 10, 3: 10, 4: 11, 5: 11, 6: 12, 7: 12, 8: 13, 9: 13, 10: 14, 11: 15 },
        "notes": { "Always": "only harvests" }
    },
    "ZOMBIE_MINION": {
        'display': 'Zombie',
        "drops": { "ROTTEN_FLESH": 1, "CARROT_ITEM": 0.01, "POTATO_ITEM": 0.01, "POISONOUS_POTATO": 0.02 },  # correct
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "REVENANT_MINION": {
        'display': 'Revenant',
        "drops": { "ROTTEN_FLESH": 3.16, "DIAMOND": 0.2 },
        "speed": { 1: 29, 2: 29, 3: 26, 4: 26, 5: 23, 6: 23, 7: 19, 8: 19, 9: 14.5, 10: 14.5, 11: 10, 12: 8 },
        "afkcorrupt": 1.83,
        "notes": { "AFK": "multiple corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "VOIDLING_MINION": {
        'display': 'Voidling',
        "drops": { "OBSIDIAN": 2.5, "QUARTZ": 0.4, "ENCHANTED_ENDER_PEARL": 0.000625 },
        "speed": { 1: 45, 2: 45, 3: 42, 4: 42, 5: 39, 6: 39, 7: 35, 8: 35, 9: 30, 10: 30, 11: 24 },
        "afkcorrupt": 1.5,
        "notes": { "AFK": "multiple corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "INFERNO_MINION": {
        'display': 'Inferno',
        "drops": { "CRUDE_GABAGOOL": 1 },
        "speed": { 1: 1013, 2: 982, 3: 950, 4: 919, 5: 886, 6: 855, 7: 823, 8: 792, 9: 760, 10: 728, 11: 697 },
        "afkcorrupt": 0,
        "notes": { "Inferno": "can use inferno fuel", "AFK": "no corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "VAMPIRE_MINION": {
        'display': 'Vampire',
        "drops": { "HEMOVIBE": 1 },
        "speed": { 1: 190, 2: 190, 3: 175, 4: 175, 5: 160, 6: 160, 7: 140, 8: 140, 9: 117, 10: 117, 11: 95 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "SKELETON_MINION": {
        'display': 'Skeleton',
        "drops": { "BONE": 1.5 },  # correct
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "afkcorrupt": 1.5,
        "notes": { "AFK": "multiple corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "CREEPER_MINION": {
        'display': 'Creeper',
        "drops": { "SULPHUR": 1 },
        "speed": { 1: 27, 2: 27, 3: 25, 4: 25, 5: 23, 6: 23, 7: 21, 8: 21, 9: 18, 10: 18, 11: 14 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "SPIDER_MINION": {
        'display': 'Spider',
        "drops": { "STRING": 1, "SPIDER_EYE": 0.5 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "TARANTULA_MINION": {
        'display': 'Tarantula',
        "drops": { "STRING": 3.16, "SPIDER_EYE": 1, "IRON_INGOT": 0.2 },
        "speed": { 1: 29, 2: 29, 3: 26, 4: 26, 5: 23, 6: 23, 7: 19, 8: 19, 9: 14.5, 10: 14.5, 11: 10, 12: 8 },
        "afkcorrupt": 1.83,
        "notes": { "AFK": "multiple corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "CAVE_SPIDER_MINION": {
        'display': 'Cave Spider',
        "drops": { "STRING": 0.5, "SPIDER_EYE": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "BLAZE_MINION": {
        'display': 'Blaze',
        "drops": { "BLAZE_ROD": 1 },
        "speed": { 1: 33, 2: 33, 3: 31, 4: 31, 5: 28.5, 6: 28.5, 7: 25, 8: 25, 9: 21, 10: 21, 11: 16.5, 12: 15 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "MAGMA_CUBE_MINION": {
        'display': 'Magma Cube',
        "drops": { "MAGMA_CREAM": 2 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 28, 6: 28, 7: 25, 8: 25, 9: 22, 10: 22, 11: 18, 12: 16 },
        "afkcorrupt": 2,
        "notes": { "AFK": "multiple corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "ENDERMAN_MINION": {
        'display': 'Enderman',
        "drops": { "ENDER_PEARL": 1 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 28, 6: 28, 7: 25, 8: 25, 9: 22, 10: 22, 11: 18 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "GHAST_MINION": {
        'display': 'Ghast',
        "drops": { "GHAST_TEAR": 1 },
        "speed": { 1: 50, 2: 50, 3: 47, 4: 47, 5: 44, 6: 44, 7: 41, 8: 41, 9: 38, 10: 38, 11: 32, 12: 30 },
        "tags": ["mob_minion", "combat_minion"]
    },
    "SLIME_MINION": {
        'display': 'Slime',
        "drops": { "SLIME_BALL": 2 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 12 },
        "afkcorrupt": 2,
        "notes": { "AFK": "multiple corrupt drops" },
        "tags": ["mob_minion", "combat_minion"]
    },
    "COW_MINION": {
        'display': 'Cow',
        "drops": { "RAW_BEEF": 1, "LEATHER": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13, 12: 10 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "tags": ["mob_minion", "farm_animal_minion"]
    },
    "PIG_MINION": {
        'display': 'Pig',
        "drops": { "PORK": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13, 12: 10 },
        "tags": ["mob_minion", "farm_animal_minion"]
    },
    "CHICKEN_MINION": {
        'display': 'Chicken',
        "drops": { "RAW_CHICKEN": 1, "FEATHER": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 18, 10: 18, 11: 15, 12: 12 },
        "storage": { 1: 3, 2: 5, 3: 5, 4: 7, 5: 7 },
        "tags": ["mob_minion", "farm_animal_minion"]
    },
    "SHEEP_MINION": {
        'display': 'Sheep',
        "drops": { "MUTTON": 1, "WOOL": 1 },
        "speed": { 1: 24, 2: 24, 3: 22, 4: 22, 5: 20, 6: 20, 7: 18, 8: 18, 9: 16, 10: 16, 11: 12, 12: 9 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "tags": ["mob_minion", "farm_animal_minion"]
    },
    "RABBIT_MINION": {
        'display': 'Rabbit',
        "drops": { "RABBIT": 1, "RABBIT_FOOT": 0.7, "RABBIT_HIDE": 0.7 },  # correct
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13, 12: 10 },
        "storage": { 1: 3, 2: 5, 3: 5, 4: 7, 5: 7 },
        "tags": ["mob_minion", "farm_animal_minion"]
    },
    "OAK_MINION": {
        'display': 'Oak',
        "drops": { "LOG": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" },
        "tags": ["foraging_minion", "wood_minion"]
    },
    "SPRUCE_MINION": {
        'display': 'Spruce',
        "drops": { "LOG:1": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" },
        "tags": ["foraging_minion", "wood_minion"]
    },
    "BIRCH_MINION": {
        'display': 'Birch',
        "drops": { "LOG:2": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" },
        "tags": ["foraging_minion", "wood_minion"]
    },
    "DARK_OAK_MINION": {
        'display': 'Dark Oak',
        "drops": { "LOG_2:1": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" },
        "tags": ["foraging_minion", "wood_minion"]
    },
    "ACACIA_MINION": {
        'display': 'Acacia',
        "drops": { "LOG_2": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" },
        "tags": ["foraging_minion", "wood_minion"]
    },
    "JUNGLE_MINION": {
        'display': 'Jungle',
        "drops": { "LOG:3": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" },
        "tags": ["foraging_minion", "wood_minion"]
    },

    # Mayors

    "MAYOR_AATROX": {
        'display': "Aatrox",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_COLE": {
        'display': "Cole",
        "speed_boost": 25,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": ["mining_minion"]
    },
    "MAYOR_DIANA": {
        'display': "Diana",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": []
    },
    "MAYOR_DIAZ": {
        'display': "Diaz",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_FINNEGAN": {
        'display': "Finnegan",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_FOXY": {
        'display': "Foxy",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_MARINA": {
        'display': "Marina",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_PAUL": {
        'display': "Paul",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_JERRY": {
        'display': "Jerry",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_DERPY": {
        'display': "Derpy",
        "speed_boost": 0,
        "drop_multiplier": 2,
        "xp_multiplier": 1.5,
        "tax_multiplier": 4,
        "affected_minions": []
    },
    "MAYOR_SCORPIUS": {
        'display': "Scorpius",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1,
        "tax_multiplier": 1,
        "affected_minions": None
    },
    "MAYOR_AURA": {
        'display': "Aura",
        "speed_boost": 0,
        "drop_multiplier": 1,
        "xp_multiplier": 1.5,
        "tax_multiplier": 2,
        "affected_minions": []
    }
}


#%% Other data

inferno_fuel_data = {
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

standard_storage = { 1: 1, 2: 3, 3: 3, 4: 6, 5: 6, 6: 9, 7: 9, 8: 12, 9: 12, 10: 15, 11: 15, 12: 15 }

attribute_shards = {
    "Common": { 1: 1, 2: 4, 3: 9, 4: 15, 5: 22, 6: 30, 7: 40, 8: 54, 9: 72, 10: 96 },
    "Uncommon": { 1: 1, 2: 3, 3: 6, 4: 10, 5: 15, 6: 21, 7: 28, 8: 36, 9: 48, 10: 64 },
    "Rare": { 1: 1, 2: 3, 3: 6, 4: 9, 5: 13, 6: 17, 7: 22, 8: 28, 9: 36, 10: 48 },
    "Epic": { 1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 16, 8: 20, 9: 25, 10: 32 },
    "Legendary": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 9, 7: 12, 8: 15, 9: 19, 10: 24 }
}

pet_item_scrub_cost = { "Common": 25000, "Uncommon": 50000, "Rare": 100000, "Epic": 250000, "Legendary": 500000, "Mythic": 1000000, "Divine": 2500000 }


#%% Option Lists

minion_options = {
    'Custom': 'CUSTOM_MINION',
    'Cobblestone': 'COBBLESTONE_MINION',
    'Obsidian': 'OBSIDIAN_MINION',
    'Glowstone': 'GLOWSTONE_MINION',
    'Gravel': 'GRAVEL_MINION',
    'Sand': 'SAND_MINION',
    'Red Sand': 'RED_SAND_MINION',
    'Mycelium': 'MYCELIUM_MINION',
    'Clay': 'CLAY_MINION',
    'Ice': 'ICE_MINION',
    'Snow': 'SNOW_MINION',
    'Coal': 'COAL_MINION',
    'Iron': 'IRON_MINION',
    'Gold': 'GOLD_MINION',
    'Diamond': 'DIAMOND_MINION',
    'Lapis': 'LAPIS_MINION',
    'Redstone': 'REDSTONE_MINION',
    'Emerald': 'EMERALD_MINION',
    'Quartz': 'QUARTZ_MINION',
    'End Stone': 'END_STONE_MINION',
    'Mithril': 'MITHRIL_MINION',
    'Hard Stone': 'HARD_STONE_MINION',
    'Wheat': 'WHEAT_MINION',
    'Melon': 'MELON_MINION',
    'Pumpkin': 'PUMPKIN_MINION',
    'Carrot': 'CARROT_MINION',
    'Potato': 'POTATO_MINION',
    'Mushroom': 'MUSHROOM_MINION',
    'Cactus': 'CACTUS_MINION',
    'Cocoa Beans': 'COCOA_BEANS_MINION',
    'Sugar Cane': 'SUGAR_CANE_MINION',
    'Nether Wart': 'NETHER_WART_MINION',
    'Flower': 'FLOWER_MINION',
    'Sunflower': 'SUNFLOWER_MINION',
    'Fishing': 'FISHING_MINION',
    'Zombie': 'ZOMBIE_MINION',
    'Revenant': 'REVENANT_MINION',
    'Voidling': 'VOIDLING_MINION',
    'Inferno': 'INFERNO_MINION',
    'Vampire': 'VAMPIRE_MINION',
    'Skeleton': 'SKELETON_MINION',
    'Creeper': 'CREEPER_MINION',
    'Spider': 'SPIDER_MINION',
    'Tarantula': 'TARANTULA_MINION',
    'Cave Spider': 'CAVE_SPIDER_MINION',
    'Blaze': 'BLAZE_MINION',
    'Magma Cube': 'MAGMA_CUBE_MINION',
    'Enderman': 'ENDERMAN_MINION',
    'Ghast': 'GHAST_MINION',
    'Slime': 'SLIME_MINION',
    'Cow': 'COW_MINION',
    'Pig': 'PIG_MINION',
    'Chicken': 'CHICKEN_MINION',
    'Sheep': 'SHEEP_MINION',
    'Rabbit': 'RABBIT_MINION',
    'Oak': 'OAK_MINION',
    'Spruce': 'SPRUCE_MINION',
    'Birch': 'BIRCH_MINION',
    'Dark Oak': 'DARK_OAK_MINION',
    'Acacia': 'ACACIA_MINION',
    'Jungle': 'JUNGLE_MINION'
}

inferno_fuel_grade_options = {
    'Hypergolic Gabagool': 'HYPERGOLIC_GABAGOOL',
    'Heavy Gabagool': 'HEAVY_GABAGOOL',
    'Fuel Gabagool': 'FUEL_GABAGOOL',
}

inferno_fuel_distillate_options = {
    'Magma Cream Distillate': 'MAGMA_CREAM_DISTILLATE',
    'Blaze Rod Distillate': 'BLAZE_ROD_DISTILLATE',
    'Nether Wart Distillate': 'NETHER_STALK_DISTILLATE',
    'Glowstone Distillate': 'GLOWSTONE_DUST_DISTILLATE',
    'Gabagool Distillate': 'CRUDE_GABAGOOL_DISTILLATE',
}

fuel_options = {
    "None": "NONE",
    "Coal": "COAL",
    "Block Of Coal": "COAL_BLOCK",
    "Enchanted Coal": "ENCHANTED_COAL",
    "Enchanted Charcoal": "ENCHANTED_CHARCOAL",
    "Hamster Wheel": "HAMSTER_WHEEL",
    "Foul Flesh": "FOUL_FLESH",
    "Enchanted Bread": "ENCHANTED_BREAD",
    "Catalyst": "CATALYST",
    "Hyper Catalyst": "HYPER_CATALYST",
    "Tasty Cheese": "CHEESE_FUEL",
    "Solar Panel": "SOLAR_PANEL",
    "Enchanted Lava Bucket": "ENCHANTED_LAVA_BUCKET",
    "Magma Bucket": "MAGMA_BUCKET",
    "Plasma Bucket": "PLASMA_BUCKET",
    "Everburning Flame": "EVERBURNING_FLAME",
    "Inferno Minion Fuel": "INFERNO_FUEL",
    "Dayswitch": "DAYSWITCH",
    "Nightswitch": "NIGHTSWITCH",
    "Thorny Vines": "THORNY_VINES"
}

upgrade_options = {
    "None": "NONE",
    "Auto Smelter": "AUTO_SMELTER",
    "Compactor": "COMPACTOR",
    "Super Compactor 3000": "SUPER_COMPACTOR_3000",
    "Dwarven Super Compactor": "DWARVEN_COMPACTOR",
    "Diamond Spreading": "DIAMOND_SPREADING",
    "Potato Spreading": "POTATO_SPREADING",
    "Minion Expander": "MINION_EXPANDER",
    "Enchanted Egg": "ENCHANTED_EGG",
    "Flint Shovel": "FLINT_SHOVEL",
    "Flycatcher": "FLYCATCHER_UPGRADE",
    "Krampus Helmet": "KRAMPUS_HELMET",
    "Lesser Soulflow Engine": "LESSER_SOULFLOW_ENGINE",
    "Soulflow Engine": "SOULFLOW_ENGINE",
    "Corrupt Soil": "CORRUPT_SOIL",
    "Berberis Fuel Injector": "BERBERIS_FUEL_INJECTOR",
    "Enchanted Shears": "ENCHANTED_SHEARS",
    "Sleepy Hollow": "SLEEPY_HOLLOW",
    "Hunter Knife": "HUNTER_KNIFE"
}

pet_exp_boost_options = {
    "None": "NONE",
    "Common Mining Exp Boost": "PET_ITEM_MINING_SKILL_BOOST_COMMON",
    "Uncommon Mining Exp Boost": "PET_ITEM_MINING_SKILL_BOOST_UNCOMMON",
    "Rare Mining Exp Boost": "PET_ITEM_MINING_SKILL_BOOST_RARE",
    "Common Farming Exp Boost": "PET_ITEM_FARMING_SKILL_BOOST_COMMON",
    "Uncommon Farming Exp Boost": "PET_ITEM_FARMING_SKILL_BOOST_UNCOMMON",
    "Rare Farming Exp Boost": "PET_ITEM_FARMING_SKILL_BOOST_RARE",
    "Epic Farming Exp Boost": "PET_ITEM_FARMING_SKILL_BOOST_EPIC",
    "Common Fishing Exp Boost": "PET_ITEM_FISHING_SKILL_BOOST_COMMON",
    "Uncommon Fishing Exp Boost": "PET_ITEM_FISHING_SKILL_BOOST_UNCOMMON",
    "Rare Fishing Exp Boost": "PET_ITEM_FISHING_SKILL_BOOST_RARE",
    "Epic Fishing Exp Boost": "PET_ITEM_FISHING_SKILL_BOOST_EPIC",
    "Common Combat Exp Boost": "PET_ITEM_COMBAT_SKILL_BOOST_COMMON",
    "Uncommon Combat Exp Boost": "PET_ITEM_COMBAT_SKILL_BOOST_UNCOMMON",
    "Rare Combat Exp Boost": "PET_ITEM_COMBAT_SKILL_BOOST_RARE",
    "Epic Combat Exp Boost": "PET_ITEM_COMBAT_SKILL_BOOST_EPIC",
    "Common Foraging Exp Boost": "PET_ITEM_FORAGING_SKILL_BOOST_COMMON",
    "Epic Foraging Exp Boost": "PET_ITEM_FORAGING_SKILL_BOOST_EPIC",
    "All Skills Exp Boost": "PET_ITEM_ALL_SKILLS_BOOST_COMMON",
    "All Skills Exp Super-Boost": "ALL_SKILLS_SUPER_BOOST",
}

floating_crystal_options = {
    "None": "NONE",
    "Farm Crystal": "FARM_CRYSTAL",
    "Woodcutting Crystal": "WOODCUTTING_CRYSTAL",
    "Mithril Crystal": "MITHRIL_CRYSTAL",
    "Winter Crystal": "WINTER_ISLAND_CRYSTAL",
    "Mithril + Winter Crystal": "MITHRIL_WINTER_CRYSTAL"
}

chest_options = {
    "None": "NONE",
    "Small Storage": "SMALL_ENCHANTED_CHEST",
    "Medium Storage": "MEDIUM_ENCHANTED_CHEST",
    "Large Storage": "LARGE_ENCHANTED_CHEST",
    "X-Large Storage": "XLARGE_ENCHANTED_CHEST",
    "XX-Large Storage": "XXLARGE_ENCHANTED_CHEST",
}

hopper_options = {
    "None": "NONE",
    "Budget Hopper": "BUDGET_HOPPER",
    "Enchanted Hopper": "ENCHANTED_HOPPER",
}

beacon_options = {
    "None": "NONE",
    "Beacon I": "BEACON_1",
    "Beacon II": "BEACON_2",
    "Beacon III": "BEACON_3",
    "Beacon IV": "BEACON_4",
    "Beacon V": "BEACON_5",
}

potato_accessory_options = {
    "None": "NONE",
    "Potato Talisman": "POTATO_TALISMAN",
    "Potato Ring": "POTATO_RING"
}

mayor_options = {
    'None': "NONE",
    'Aatrox': "MAYOR_AATROX",
    'Cole': "MAYOR_COLE",
    'Diana': "MAYOR_DIANA",
    'Diaz': "MAYOR_DIAZ",
    'Finnegan': "MAYOR_FINNEGAN",
    'Foxy': "MAYOR_FOXY",
    'Marina': "MAYOR_MARINA",
    'Paul': "MAYOR_PAUL",
    'Jerry': "MAYOR_JERRY",
    'Derpy': "MAYOR_DERPY",
    'Scorpius': "MAYOR_SCORPIUS",
    'Aura': "MAYOR_AURA"
}


#%% Pets

# name pet: {valid rarities: [boost base, added boost per level], "affected_minions": [affected minions]}
boost_pets = {
    "None": { "affected_minions": [] },
    # "Chicken": {"Legendary": [0, 0.3], "affected_minions": ["Chicken"]},  # reworked in skyblock 0.23.1
    "Magma Cube": {
        "Common": [0, 0.2], "Uncommon": [0, 0.25],
        "Rare": [0, 0.25], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affected_minions": ["SLIME_MINION", "MAGMA_CUBE_MINION"]  # affects magma cube minion is correct
    },
    "Mooshroom Cow": {
        "Common": [0, 0.2], "Uncommon": [0, 0.2],
        "Rare": [0, 0.3], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affected_minions": ["MUSHROOM_MINION", "MYCELIUM_MINION"]
    },
    "Ocelot": {
        "Rare": [0, 0.3], "Epic": [0, 0.3], "Legendary": [0, 0.3],
        "affected_minions": ["foraging_minion"]
    },
    "Pigman": {
        "Common": [0, 0.1], "Uncommon": [0, 0.2],
        "Rare": [0, 0.2], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affected_minions": ["PIG_MINION"]
    },
    "Rabbit": {
        "Legendary": [0, 0.3], "Mythic": [0, 0.3],
        "affected_minions": ["farming_crop_minion"]
    },
    "Snail": {
        "Common": [0, 0.1], "Uncommon": [0, 0.2],
        "Rare": [0, 0.2], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affected_minions": ["RED_SAND_MINION"]
    },
    "Spider": {
        "Legendary": [0, 0.3], "Mythic": [0, 0.3],
        "affected_minions": ["SPIDER_MINION", "TARANTULA_MINION", "CAVE_SPIDER_MINION"]
    }
}

all_pets = {
    "None": { 'type': 'all', 'rarity': 'Legendary' },
    "Custom Pet": { 'type': 'farming', 'rarity': 'Legendary' },
    'Ammonite': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Ankylosaurus': { 'type': 'combat', 'rarity': 'Legendary' },
    'Armadillo': { 'type': 'mining', 'rarity': 'Legendary' },
    'Baby Yeti': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Bal': { 'type': 'mining', 'rarity': 'Legendary' },
    'Bat': { 'type': 'mining', 'rarity': 'Legendary' },
    'Bee': { 'type': 'farming', 'rarity': 'Legendary' },
    "Bingo": { 'type': 'all', 'rarity': 'Common' },
    'Black Cat': { 'type': 'combat', 'rarity': 'Legendary' },
    'Blaze': { 'type': 'combat', 'rarity': 'Legendary' },
    'Blue Whale': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Chicken': { 'type': 'farming', 'rarity': 'Legendary' },
    'Crow': { 'type': 'combat', 'rarity': 'Legendary' },
    'Dolphin': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Eerie': { 'type': 'combat', 'rarity': 'Legendary' },
    'Elephant': { 'type': 'farming', 'rarity': 'Legendary' },
    'Ender Dragon': { 'type': 'combat', 'rarity': 'Legendary' },
    'Enderman': { 'type': 'combat', 'rarity': 'Legendary' },
    'Endermite': { 'type': 'mining', 'rarity': 'Legendary' },
    'Flying Fish': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Frog': { 'type': 'foraging', 'rarity': 'Legendary' },
    'Ghoul': { 'type': 'combat', 'rarity': 'Legendary' },
    'Giraffe': { 'type': 'foraging', 'rarity': 'Legendary' },
    'Glacite Golem': { 'type': 'mining', 'rarity': 'Legendary' },
    'Goblin': { 'type': 'mining', 'rarity': 'Legendary' },
    'Golden Dragon': { 'type': 'combat', 'rarity': 'Dragon' },
    'Golden Dragon Egg': { 'type': 'combat', 'rarity': 'Legendary' },
    'Golem': { 'type': 'combat', 'rarity': 'Legendary' },
    'Grandma Wolf': { 'type': 'combat', 'rarity': 'Legendary' },
    'Griffin': { 'type': 'combat', 'rarity': 'Legendary' },
    'Guardian': { 'type': 'enchanting', 'rarity': 'Legendary' },
    'Hedgehog': { 'type': 'farming', 'rarity': 'Legendary' },
    'Hermit Crab': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Horse': { 'type': 'combat', 'rarity': 'Legendary' },
    'Hound': { 'type': 'combat', 'rarity': 'Legendary' },
    'Jerry': { 'type': 'combat', 'rarity': 'Legendary' },
    'Jade Dragon': { 'type': 'foraging', 'rarity': 'Dragon' },
    'Jade Dragon Egg': { 'type': 'foraging', 'rarity': 'Legendary' },
    'Jellyfish': { 'type': 'alchemy', 'rarity': 'Legendary' },
    'Kuudra': { 'type': 'combat', 'rarity': 'Legendary' },
    'Lion': { 'type': 'foraging', 'rarity': 'Legendary' },
    'Magma Cube': { 'type': 'combat', 'rarity': 'Legendary' },
    'Mammoth': { 'type': 'combat', 'rarity': 'Legendary' },
    'Megalodon': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Mithril Golem': { 'type': 'mining', 'rarity': 'Legendary' },
    'Mole': { 'type': 'mining', 'rarity': 'Legendary' },
    'Monkey': { 'type': 'foraging', 'rarity': 'Legendary' },
    'Mooshroom Cow': { 'type': 'farming', 'rarity': 'Legendary' },
    'Mosquito': { 'type': 'farming', 'rarity': 'Legendary' },
    'Ocelot': { 'type': 'foraging', 'rarity': 'Legendary' },
    'Owl': { 'type': 'taming', 'rarity': 'Legendary' },
    'Parrot': { 'type': 'alchemy', 'rarity': 'Legendary' },
    'Penguin': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Phoenix': { 'type': 'combat', 'rarity': 'Legendary' },
    'Pig': { 'type': 'farming', 'rarity': 'Legendary' },
    'Pigman': { 'type': 'combat', 'rarity': 'Legendary' },
    'Precursor Drone': { 'type': 'combat', 'rarity': 'Common' },
    'Rabbit': { 'type': 'farming', 'rarity': 'Legendary' },
    'Rat': { 'type': 'combat', 'rarity': 'Legendary' },
    'Reindeer': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Rift Ferret': { 'type': 'combat', 'rarity': 'Epic' },
    'Rock': { 'type': 'mining', 'rarity': 'Legendary' },
    'Rose Dragon': { 'type': 'farming', 'rarity': 'Dragon' },
    'Rose Dragon Egg': { 'type': 'farming', 'rarity': 'Legendary' },
    'Scatha': { 'type': 'mining', 'rarity': 'Legendary' },
    'Sheep': { 'type': 'alchemy', 'rarity': 'Legendary' },
    'Silverfish': { 'type': 'mining', 'rarity': 'Legendary' },
    'Skeleton': { 'type': 'combat', 'rarity': 'Legendary' },
    'Skeleton Horse': { 'type': 'combat', 'rarity': 'Legendary' },
    'Slug': { 'type': 'farming', 'rarity': 'Legendary' },
    'Snail': { 'type': 'mining', 'rarity': 'Legendary' },
    'Snowman': { 'type': 'combat', 'rarity': 'Legendary' },
    'Spider': { 'type': 'combat', 'rarity': 'Legendary' },
    'Spinosaurus': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Spirit': { 'type': 'combat', 'rarity': 'Legendary' },
    'Squid': { 'type': 'fishing', 'rarity': 'Legendary' },
    'T-Rex': { 'type': 'combat', 'rarity': 'Legendary' },
    'Tarantula': { 'type': 'combat', 'rarity': 'Legendary' },
    'Tiger': { 'type': 'combat', 'rarity': 'Legendary' },
    'Turtle': { 'type': 'combat', 'rarity': 'Legendary' },
    'Wither Skeleton': { 'type': 'mining', 'rarity': 'Legendary' },
    'Wolf': { 'type': 'combat', 'rarity': 'Legendary' },
    'Zombie': { 'type': 'combat', 'rarity': 'Legendary' }
}

max_lvl_pet_xp_amounts = { "Common": 5624785, "Uncommon": 8644220, "Rare": 12626665, "Epic": 18608500, "Legendary": 25353230, "Mythic": 25353230, "Dragon": 210255385 }


#%% Data check functions

def has_data_tag(data_ID, tag):
    if data_ID not in calculator_data:
        print(f"ERROR - has_data_tag - data ID {data_ID} not in calculator data")
        return False
    if tag is None:
        return False
    if len(tag) == 0:
        return True
    if data_ID == tag or data_ID in tag:
        return True
    if "tags" not in calculator_data[data_ID]:
        return False
    if type(tag) == str and tag in calculator_data[data_ID]["tags"]:
        return True
    if type(tag) != list:
        return False
    for search_tag in tag:
        if search_tag in calculator_data[data_ID]["tags"]:
            return True
    return False


#%% Minion Cost Functions

def minionCostTypes(materials, upgradetype, twelve=False, edits=None):
    if upgradetype == "single enchanted":  # like Cobblestone
        base = materials[0]
        enchanted = materials[1]
        cost_dict = {1: {base: 80}, 2: {base: 160}, 3: {base: 320}, 4: {base: 512}, 5: {enchanted: 8}, 6: {enchanted: 16}, 7: {enchanted: 32}, 8: {enchanted: 64}, 9: {enchanted: 128}, 10: {enchanted: 256}, 11: {enchanted: 512}}
        if twelve is True:
            cost_dict[12] = {enchanted: 1024}
    if upgradetype == "double enchanted":  # like Coal
        base = materials[0]
        enchanted = materials[1]
        super_enchanted = materials[2]
        cost_dict = {1: {base: 80}, 2: {base: 160}, 3: {base: 320}, 4: {base: 512}, 5: {enchanted: 8}, 6: {enchanted: 24}, 7: {enchanted: 64}, 8: {enchanted: 128}, 9: {enchanted: 256}, 10: {enchanted: 512}, 11: {super_enchanted: 8}}
        if twelve is True:
            cost_dict[12] = {super_enchanted: 16}
    if upgradetype == "expensive enchanted":  # like Glowstone
        base = materials[0]
        enchanted = materials[1]
        super_enchanted = materials[2]
        cost_dict = {1: {base: 128}, 2: {base: 256}, 3: {base: 512}, 4: {enchanted: 8}, 5: {enchanted: 24}, 6: {enchanted: 64}, 7: {enchanted: 128}, 8: {enchanted: 256}, 9: {enchanted: 512}, 10: {super_enchanted: 8}, 11: {super_enchanted: 16}}
        if twelve is True:
            cost_dict[12] = {super_enchanted: 32}
    if upgradetype == "very expensive enchanted":  # like Lapis Lazuli
        base = materials[0]
        enchanted = materials[1]
        super_enchanted = materials[2]
        cost_dict = {1: {base: 256}, 2: {base: 512}, 3: {enchanted: 8}, 4: {enchanted: 24}, 5: {enchanted: 64}, 6: {enchanted: 128}, 7: {enchanted: 256}, 8: {enchanted: 512}, 9: {super_enchanted: 8}, 10: {super_enchanted: 16}, 11: {super_enchanted: 32}}
        if twelve is True:
            cost_dict[12] = {super_enchanted: 64}
    if edits is not None:
        for tier, edit in edits.items():
            cost_dict[tier] = edit
    try:
        return deepcopy(cost_dict)
    except UnboundLocalError:
        print(f"Minion cost calculation failed with {materials}")
        return {}


def minionCostSum(minion_type, final_tier):
    final_cost = {}
    tier_loop = range(1, final_tier + 1)
    for tier in tier_loop:
        for item, amount in minionCosts[minion_type][tier].items():
            if item not in final_cost:
                final_cost[item] = 0
            final_cost[item] += amount
    return deepcopy(final_cost)


#%% Minion Costs

minionCosts = {
    "CUSTOM_MINION": minionCostTypes(["CUSTOM", "ENCHANTED_CUSTOM"], "single enchanted", True),
    "COBBLESTONE_MINION": minionCostTypes(["COBBLESTONE", "ENCHANTED_COBBLESTONE"], "single enchanted", True),
    "OBSIDIAN_MINION": minionCostTypes(["OBSIDIAN", "ENCHANTED_OBSIDIAN"], "single enchanted", True),
    "GLOWSTONE_MINION": minionCostTypes(["GLOWSTONE_DUST", "ENCHANTED_GLOWSTONE_DUST", "ENCHANTED_GLOWSTONE"], "expensive enchanted", True),
    "GRAVEL_MINION": minionCostTypes(["GRAVEL", "ENCHANTED_FLINT"], "single enchanted", False),
    "SAND_MINION": minionCostTypes(["SAND", "ENCHANTED_SAND"], "single enchanted", False),
    "RED_SAND_MINION": minionCostTypes(["SAND:1", "ENCHANTED_RED_SAND", "ENCHANTED_RED_SAND_CUBE"], "expensive enchanted", True, {1: {'SAND:1': 80}, 4: {'ENCHANTED_RED_SAND': 16}, 5: {'ENCHANTED_RED_SAND': 32}}),
    "MYCELIUM_MINION": minionCostTypes(["MYCEL", "ENCHANTED_MYCELIUM", "ENCHANTED_MYCELIUM_CUBE"], "expensive enchanted", True, {1: {'MYCEL': 80}, 4: {'ENCHANTED_MYCELIUM': 16}, 5: {'ENCHANTED_MYCELIUM': 32}}),
    "CLAY_MINION": minionCostTypes(["CLAY_BALL", "ENCHANTED_CLAY_BALL"], "single enchanted", True, {12: {"ENCHANTED_CLAY_BLOCK": 8}}),
    "ICE_MINION": {1: {"ICE": 80}, 2: {"ICE": 160}, 3: {"ICE": 320}, 4: {"ICE": 512}, 5: {"PACKED_ICE": 128}, 6: {"PACKED_ICE": 256}, 7: {"PACKED_ICE": 512}, 8: {"ENCHANTED_ICE": 64}, 9: {"ENCHANTED_ICE": 128}, 10: {"ENCHANTED_ICE": 256}, 11: {"ENCHANTED_ICE": 512}, 12: {"ENCHANTED_ICE": 1024}},
    "SNOW_MINION": {1: {}, 2: {"SNOW_BLOCK": 32}, 3: {"SNOW_BLOCK": 64}, 4: {"SNOW_BLOCK": 128}, 5: {"SNOW_BLOCK": 256}, 6: {"SNOW_BLOCK": 512}, 7: {"ENCHANTED_SNOW_BLOCK": 8}, 8: {"ENCHANTED_SNOW_BLOCK": 16}, 9: {"ENCHANTED_SNOW_BLOCK": 32}, 10: {"ENCHANTED_SNOW_BLOCK": 64}, 11: {"ENCHANTED_SNOW_BLOCK": 128}, 12: {"ENCHANTED_SNOW_BLOCK": 1024}},
    "COAL_MINION": minionCostTypes(["COAL", "ENCHANTED_COAL", "ENCHANTED_COAL_BLOCK"], "double enchanted", True),
    "IRON_MINION": minionCostTypes(["IRON_INGOT", "ENCHANTED_IRON", "ENCHANTED_IRON_BLOCK"], "double enchanted", True),
    "GOLD_MINION": minionCostTypes(["GOLD_INGOT", "ENCHANTED_GOLD", "ENCHANTED_GOLD_BLOCK"], "double enchanted", True),
    "DIAMOND_MINION": minionCostTypes(["DIAMOND", "ENCHANTED_DIAMOND", "ENCHANTED_DIAMOND_BLOCK"], "double enchanted", True),
    "LAPIS_MINION": minionCostTypes(["INK_SACK:4", "ENCHANTED_LAPIS_LAZULI", "ENCHANTED_LAPIS_LAZULI_BLOCK"], "very expensive enchanted", True),
    "REDSTONE_MINION": minionCostTypes(["REDSTONE", "ENCHANTED_REDSTONE", "ENCHANTED_REDSTONE_BLOCK"], "expensive enchanted", True),
    "EMERALD_MINION": minionCostTypes(["EMERALD", "ENCHANTED_EMERALD", "ENCHANTED_EMERALD_BLOCK"], "double enchanted", True),
    "QUARTZ_MINION": minionCostTypes(["QUARTZ", "ENCHANTED_QUARTZ", "ENCHANTED_QUARTZ_BLOCK"], "double enchanted", True),
    "END_STONE_MINION": minionCostTypes(["ENDER_STONE", "ENCHANTED_ENDSTONE"], "single enchanted", False),
    "MITHRIL_MINION": minionCostTypes(["MITHRIL_ORE", "ENCHANTED_MITHRIL", "REFINED_MITHRIL"], "double enchanted", True),
    "HARD_STONE_MINION": minionCostTypes(["HARD_STONE", "ENCHANTED_HARD_STONE", "CONCENTRATED_STONE"], "expensive enchanted", True, {1: {'HARD_STONE': 256}, 2: {'HARD_STONE': 512}, 3: {'ENCHANTED_HARD_STONE': 8}, 4: {'ENCHANTED_HARD_STONE': 16}, 5: {'ENCHANTED_HARD_STONE': 32}, 10: {"CONCENTRATED_STONE": 4}, 11: {"CONCENTRATED_STONE": 8}, 12: {"CONCENTRATED_STONE": 16}}),
    "WHEAT_MINION": minionCostTypes(["WHEAT", "ENCHANTED_WHEAT"], "single enchanted", True),
    "MELON_MINION": {1: {"MELON": 256}, 2: {"MELON": 512}, 3: {"MELON_BLOCK": 128}, 4: {"MELON_BLOCK": 256}, 5: {"MELON_BLOCK": 512}, 6: {"ENCHANTED_MELON": 64}, 7: {"ENCHANTED_MELON": 128}, 8: {"ENCHANTED_MELON": 256}, 9: {"ENCHANTED_MELON": 512}, 10: {"ENCHANTED_MELON_BLOCK": 8}, 11: {"ENCHANTED_MELON_BLOCK": 16}, 12: {"ENCHANTED_MELON_BLOCK": 32}},
    "PUMPKIN_MINION": minionCostTypes(["PUMPKIN", "ENCHANTED_PUMPKIN"], "single enchanted", True),
    "CARROT_MINION": minionCostTypes(["CARROT_ITEM", "ENCHANTED_CARROT", "ENCHANTED_GOLDEN_CARROT"], "expensive enchanted", True),
    "POTATO_MINION": minionCostTypes(["POTATO_ITEM", "ENCHANTED_POTATO", "ENCHANTED_BAKED_POTATO"], "expensive enchanted", True),
    "MUSHROOM_MINION": minionCostTypes(["RED_MUSHROOM", "ENCHANTED_RED_MUSHROOM"], "single enchanted", True, {12: {"ENCHANTED_RED_MUSHROOM": 512, "ENCHANTED_BROWN_MUSHROOM": 512}}),
    "CACTUS_MINION": minionCostTypes(["CACTUS", "ENCHANTED_CACTUS_GREEN", "ENCHANTED_CACTUS"], "expensive enchanted", True),
    "COCOA_BEANS_MINION": minionCostTypes(["INK_SACK:3", "ENCHANTED_COCOA", "ENCHANTED_COOKIE"], "double enchanted", True),
    "SUGAR_CANE_MINION": minionCostTypes(["SUGAR_CANE", "ENCHANTED_SUGAR", "ENCHANTED_SUGAR_CANE"], "expensive enchanted", True),
    "NETHER_WART_MINION": minionCostTypes(["NETHER_STALK", "ENCHANTED_NETHER_STALK"], "single enchanted", True),
    "FLOWER_MINION": minionCostTypes(["YELLOW_FLOWER", "ENCHANTED_DANDELION", "ENCHANTED_POPPY"], "double enchanted", True, {1: {}}),
    "SUNFLOWER_MINION": {1: {"DOUBLE_PLANT": 128}, 2: {"DOUBLE_PLANT": 160}, 3: {"DOUBLE_PLANT": 320}, 4: {"DOUBLE_PLANT": 512}, 5: {"ENCHANTED_SUNFLOWER": 8}, 6: {"ENCHANTED_SUNFLOWER": 24}, 7: {"ENCHANTED_SUNFLOWER": 64}, 8: {"ENCHANTED_SUNFLOWER": 128}, 9: {"ENCHANTED_SUNFLOWER": 512}, 10: {"COMPACTED_SUNFLOWER": 8}, 11: {"COMPACTED_SUNFLOWER": 16}, 12: {"COMPACTED_SUNFLOWER": 32}},
    "FISHING_MINION": {1: {'RAW_FISH': 64}, 2: {'RAW_FISH': 128}, 3: {'RAW_FISH': 256}, 4: {'RAW_FISH': 512}, 5: {'ENCHANTED_RAW_FISH': 8}, 6: {'ENCHANTED_RAW_FISH': 24}, 7: {'ENCHANTED_RAW_FISH': 64}, 8: {'ENCHANTED_RAW_FISH': 128}, 9: {'ENCHANTED_RAW_FISH': 256}, 10: {'ENCHANTED_RAW_FISH': 512}, 11: {'ENCHANTED_COOKED_FISH': 8}, 12: {'ENCHANTED_COOKED_FISH': 16}},
    "ZOMBIE_MINION": minionCostTypes(["ROTTEN_FLESH", "ENCHANTED_ROTTEN_FLESH"], "single enchanted", False),
    "REVENANT_MINION": {},
    "VOIDLING_MINION": {},
    "INFERNO_MINION": {},
    "VAMPIRE_MINION": minionCostTypes(["HEMOVIBE", "HEMOGLASS"], "single enchanted", False),
    "SKELETON_MINION": minionCostTypes(["BONE", "ENCHANTED_BONE"], "single enchanted", False),
    "CREEPER_MINION": minionCostTypes(["SULPHUR", "ENCHANTED_GUNPOWDER", "ENCHANTED_FIREWORK_ROCKET"], "double enchanted", False, {11: {"ENCHANTED_FIREWORK_ROCKET": 16}}),
    "SPIDER_MINION": minionCostTypes(["STRING", "ENCHANTED_STRING"], "single enchanted", False),
    "TARANTULA_MINION": {},
    "CAVE_SPIDER_MINION": minionCostTypes(["SPIDER_EYE", "ENCHANTED_SPIDER_EYE", "ENCHANTED_FERMENTED_SPIDER_EYE"], "double enchanted", False, {11: {"ENCHANTED_FERMENTED_SPIDER_EYE": 16}}),
    "BLAZE_MINION": minionCostTypes(["BLAZE_ROD", "ENCHANTED_BLAZE_POWDER", "ENCHANTED_BLAZE_ROD"], "double enchanted", True),
    "MAGMA_CUBE_MINION": minionCostTypes(["MAGMA_CREAM", "ENCHANTED_MAGMA_CREAM"], "single enchanted", True),
    "ENDERMAN_MINION": {1: {"ENDER_PEARL": 64}, 2: {"ENDER_PEARL": 128}, 3: {"ENCHANTED_ENDER_PEARL": 8}, 4: {"ENCHANTED_ENDER_PEARL": 24}, 5: {"ENCHANTED_ENDER_PEARL": 48}, 6: {"ENCHANTED_ENDER_PEARL": 96}, 7: {"ENCHANTED_EYE_OF_ENDER": 8}, 8: {"ENCHANTED_EYE_OF_ENDER": 24}, 9: {"ENCHANTED_EYE_OF_ENDER": 48}, 10: {"ENCHANTED_EYE_OF_ENDER": 96}, 11: {"ENCHANTED_EYE_OF_ENDER": 192}},
    "GHAST_MINION": {1: {"GHAST_TEAR": 64}, 2: {"GHAST_TEAR": 128}, 3: {"GHAST_TEAR": 256}, 4: {"GHAST_TEAR": 512}, 5: {"ENCHANTED_GHAST_TEAR": 256}, 6: {"ENCHANTED_GHAST_TEAR": 512}, 7: {"SILVER_FANG": 32}, 8: {"SILVER_FANG": 64}, 9: {"SILVER_FANG": 128}, 10: {"SILVER_FANG": 256}, 11: {"SILVER_FANG": 512}, 12: {"SILVER_FANG": 1024}},
    "SLIME_MINION": minionCostTypes(["SLIME_BALL", "ENCHANTED_SLIME_BALL", "ENCHANTED_SLIME_BLOCK"], "double enchanted", False),
    "COW_MINION": {1: {"RAW_BEEF": 64}, 2: {"RAW_BEEF": 128}, 3: {"RAW_BEEF": 256}, 4: {"RAW_BEEF": 512}, 5: {"ENCHANTED_RAW_BEEF": 8}, 6: {"ENCHANTED_RAW_BEEF": 24}, 7: {"ENCHANTED_RAW_BEEF": 64}, 8: {"ENCHANTED_RAW_BEEF": 128}, 9: {"ENCHANTED_RAW_BEEF": 256}, 10: {"ENCHANTED_RAW_BEEF": 512}, 11: {"ENCHANTED_LEATHER": 512}, 12: {"ENCHANTED_LEATHER": 1024}},  # correct
    "PIG_MINION": minionCostTypes(["PORK", "ENCHANTED_PORK", "ENCHANTED_GRILLED_PORK"], "double enchanted", True, {1: {"PORK": 64}, 2: {"PORK": 128}, 3: {"PORK": 256}}),
    "CHICKEN_MINION": minionCostTypes(["RAW_CHICKEN", "ENCHANTED_RAW_CHICKEN"], "single enchanted", True, {1: {"RAW_CHICKEN": 64}, 2: {"RAW_CHICKEN": 128}, 3: {"RAW_CHICKEN": 256}}),
    "SHEEP_MINION": minionCostTypes(["MUTTON", "ENCHANTED_MUTTON", "ENCHANTED_COOKED_MUTTON"], "double enchanted", True, {1: {"MUTTON": 64}, 2: {"MUTTON": 128}, 3: {"MUTTON": 256}}),
    "RABBIT_MINION": minionCostTypes(["RABBIT", "ENCHANTED_RABBIT", "ENCHANTED_COOKED_RABBIT"], "double enchanted", True, {1: {"RABBIT": 64}, 2: {"RABBIT": 128}, 3: {"RABBIT": 256}}),
    "OAK_MINION": minionCostTypes(["LOG", "ENCHANTED_OAK_LOG"], "single enchanted", False),
    "SPRUCE_MINION": minionCostTypes(["LOG:1", "ENCHANTED_SPRUCE_LOG"], "single enchanted", False),
    "BIRCH_MINION": minionCostTypes(["LOG:2", "ENCHANTED_BIRCH_LOG"], "single enchanted", False),
    "DARK_OAK_MINION": minionCostTypes(["LOG_2:1", "ENCHANTED_DARK_OAK_LOG"], "single enchanted", False),
    "ACACIA_MINION": minionCostTypes(["LOG_2", "ENCHANTED_ACACIA_LOG"], "single enchanted", False),
    "JUNGLE_MINION": minionCostTypes(["LOG:3", "ENCHANTED_JUNGLE_LOG"], "single enchanted", False)
}

minionCosts["REVENANT_MINION"] = {
    1: { "REVENANT_FLESH": 80, "ENCHANTED_ROTTEN_FLESH": 256, "ENCHANTED_DIAMOND": 256 },
    2: { "REVENANT_FLESH": 140, **minionCostSum("ZOMBIE_MINION", 1) },
    3: { "REVENANT_FLESH": 280, **minionCostSum("ZOMBIE_MINION", 2) },
    4: { "REVENANT_FLESH": 448, **minionCostSum("ZOMBIE_MINION", 3) },
    **{ i: { "REVENANT_VISCERA": 7 * 2**(i - 5), **minionCostSum("ZOMBIE_MINION", i - 1) } for i in range(5, 12) },
    12: { "REVENANT_VISCERA": 64 }
}
minionCosts["VOIDLING_MINION"] = {
    1: { "NULL_SPHERE": 80, **minionCostSum("ENDERMAN_MINION", 1) },
    2: { "NULL_SPHERE": 140, **minionCostSum("OBSIDIAN_MINION", 1) },
    3: { "NULL_SPHERE": 280, **minionCostSum("ENDERMAN_MINION", 2) },
    4: { "NULL_SPHERE": 448, **minionCostSum("OBSIDIAN_MINION", 3) },
    **{ i: { "NULL_OVOID": 7 * 2**(i - 5), **minionCostSum(f"{'OBSIDIAN_MINION' if i % 2 == 0 else 'ENDERMAN_MINION'}", i - 1) } for i in range(5, 12) }
}
minionCosts["INFERNO_MINION"] = {
    1: { "DERELICT_ASHE": 80, **minionCostSum("BLAZE_MINION", 1)},
    2: {"DERELICT_ASHE": 320 },
    **{ i: {"MOLTEN_POWDER": 8 * 2**(i - 3)} for i in range(3, 9) },
    9: { 'MOLTEN_POWDER': 256, "INFERNO_VERTEX": 16 },
    10: { 'MOLTEN_POWDER': 256, "INFERNO_VERTEX": 48 }
}
minionCosts["INFERNO_MINION"][11] = { "INFERNO_VERTEX": 48, "INFERNO_APEX": 1, **minionCostSum("INFERNO_MINION", 8) }
minionCosts["INFERNO_MINION"][11]["MOLTEN_POWDER"] += 256
minionCosts["TARANTULA_MINION"] = {
    1: { "TARANTULA_WEB": 80, "ENCHANTED_FERMENTED_SPIDER_EYE": 1 },
    2: { "TARANTULA_WEB": 140, **minionCostSum("SPIDER_MINION", 1) },
    3: { "TARANTULA_WEB": 280, **minionCostSum("SPIDER_MINION", 2) },
    4: { "TARANTULA_WEB": 448, **minionCostSum("SPIDER_MINION", 3) },
    **{ i: {"TARANTULA_SILK": 7 * 2**(i - 5), **minionCostSum("SPIDER_MINION", i - 1)} for i in range(5, 12) },
    12: { "TARANTULA_SILK": 64 }
}

extraMinionCosts = {
    "CUSTOM_MINION": { 6: { "TESTING": 2 }, 12: { "COINS": 1, "NON_EXISTENT": 1, "TEST": 2 } },
    "COBBLESTONE_MINION": { 12: { "COINS": 2000000 } },
    "OBSIDIAN_MINION": { 12: { "COINS": 2000000 } },
    "GLOWSTONE_MINION": { 12: { "COINS": 2000000 } },
    "RED_SAND_MINION": { 12: { "COINS": 2000000 } },
    "MYCELIUM_MINION": { 12: { "COINS": 2000000 } },
    "CLAY_MINION": { 12: { "COINS": 2000000, "FISHY_TREAT": 256 } },
    "ICE_MINION": { 12: { "COINS": 1000000, "NORTH_STARS": 300 } },
    "SNOW_MINION": { 12: { "COINS": 2000000, "NORTH_STARS": 500 } },
    "COAL_MINION": { 12: { "COINS": 2000000 } },
    "IRON_MINION": { 12: { "COINS": 2000000 } },
    "GOLD_MINION": { 12: { "COINS": 2000000 } },
    "DIAMOND_MINION": { 12: { "COINS": 2000000 } },
    "LAPIS_MINION": { 12: { "COINS": 2000000 } },
    "REDSTONE_MINION": { 12: { "COINS": 2000000 } },
    "EMERALD_MINION": { 12: { "COINS": 2000000 } },
    "QUARTZ_MINION": { 12: { "COINS": 2000000 } },
    "MITHRIL_MINION": { 12: { "COINS": 2000000 } },
    "HARD_STONE_MINION": { 12: { "COINS": 2000000 } },
    "WHEAT_MINION": { 12: { "PELTS": 75 } },
    "MELON_MINION": { 12: { "PELTS": 75 } },
    "PUMPKIN_MINION": { 12: { "PELTS": 75 } },
    "CARROT_MINION": { 12: { "PELTS": 75 } },
    "POTATO_MINION": { 12: { "PELTS": 75 } },
    "MUSHROOM_MINION": { 12: { "PELTS": 75 } },
    "CACTUS_MINION": { 12: { "PELTS": 75 } },
    "COCOA_BEANS_MINION": { 12: { "PELTS": 75 } },
    "SUGAR_CANE_MINION": { 12: { "PELTS": 75 } },
    "NETHER_WART_MINION": { 12: { "PELTS": 75 } },
    "FLOWER_MINION": { 1: { "T1_FROM_DARK_AUCTION": 1 } },
    "FISHING_MINION": { 12: { "COINS": 2000000, "FISHY_TREAT": 256 } },
    "REVENANT_MINION": { 12: { "COINS": 2000000 } },
    "VAMPIRE_MINION": { 1: { "BAT_PERSON_HELMET": 1 } },
    "TARANTULA_MINION": { 12: { "COINS": 2000000 } },
    "BLAZE_MINION": { 12: { "COINS": 2000000 } },
    "MAGMA_CUBE_MINION": { 12: { "COINS": 2000000 } },
    "GHAST_MINION": { 12: { "COINS": 2000000 } },
    "COW_MINION": { 12: { "PELTS": 75 } },
    "PIG_MINION": { 12: { "PELTS": 75 } },
    "CHICKEN_MINION": { 12: { "PELTS": 75 } },
    "SHEEP_MINION": { 12: { "PELTS": 75 } },
    "RABBIT_MINION": { 12: { "PELTS": 75 } },
}
