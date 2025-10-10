# -*- coding: utf-8 -*-
"""
@author: Herodirk

File containing data of hypixel skyblock minions.
Data includes:
- List of minion related items with skyblock ID, prices and possible gained skill xp
- Skyblock IDs of minion upgrades
- Lists of compactor, super compactor and auto smelter transformations, inferno minion chances
- List of minions with their drop amounts, speed and notes
- Functions for calculating minion crafting cost
- List of minion costs

Bazaar data from https://api.hypixel.net
AH data from https://sky.coflnet.com/data (currently only Postcard)

Items that are not on bazaar will have "# not in bazaar" behind the display name,
some of these are on the auction house and have "(AH)" behind "# not in bazaar",
these AH only items must have their custom prices updated manually,
each of these items has a date behind them showing when they were last updated.

There are a few illogical things here. If information has been confirmed, there is "# correct" behind it with the date of the test.
If that date is missing, it was confirmed by an old test and might need to be checked again.
"""

from copy import deepcopy
import numpy as np

#%% Bazaar Buy and Sell types:

bazaar_buy_types = {"Buy Order": "sellPrice", "Insta Buy": "buyPrice", "Custom": "custom"}
bazaar_sell_types = {"Sell Offer": "buyPrice", "Insta Sell": "sellPrice", "Custom": "custom"}

#%% Smelter List:

smelting_data = {
    'COBBLESTONE': 'STONE',
    'SAND': 'GLASS',
    'SAND:1': 'GLASS',
    'CLAY_BALL': 'CLAY_BRICK',
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

#%% item list

itemList = {
    "NONE": {
        'display': "None",  # not in bazaar (doesn't exist)
        "prices": { "custom": 0 },
        "upgrade": { 'speed': 0, 'drop': 1, 'duration': 0, 'special': { "type": "None" } }
    },
    'CUSTOM': {
        'display': 'Custom',  # not in bazaar (doesn't exist)
        "prices": { 'custom': 1 },
        'xp': { 'combat': 1 }
    },
    'COMPACTED_CUSTOM': {
        'display': 'Compacted Custom',  # not in bazaar (doesn't exist)
        "prices": { 'custom': 4 },
        'xp': { 'combat': 4 }
    },
    'ENCHANTED_CUSTOM': {
        'display': 'Enchanted Custom',  # not in bazaar (doesn't exist)
        "prices": { 'custom': 160 },
        'xp': { 'combat': 160 }
    },
    'LUSH_BERBERIS': {
        'display': 'Lush Berberis',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 10 }
    },
    'ENCHANTED_LUSH_BERBERIS': {
        'display': 'Enchanted Lush Berberis',
        "prices": { 'npc': 480 },
        'xp': { 'farming': 1600 }
    },
    'RED_GIFT': {
        'display': 'Red Gift',
        "prices": { 'npc': 0 },
        'xp': { 'mining': 0 }
    },
    'PURPLE_CANDY': {
        'display': 'Purple Candy',
        "prices": { 'npc': 0 },
        'xp': { 'combat': 0 }
    },
    'RAW_SOULFLOW': {
        'display': 'Raw Soulflow',
        "prices": { 'npc': 0 },
        'xp': { 'combat': 0 }
    },
    'SOULFLOW': {
        'display': 'Soulflow',
        "prices": { 'npc': 1 },
        'xp': { 'combat': 0 }
    },
    'SULPHUR_ORE': {
        'display': 'Sulphur',
        "prices": { 'npc': 10 },
        'xp': { 'mining': 0 }
    },
    'ENCHANTED_SULPHUR': {
        'display': 'Enchanted Sulphur',
        "prices": { 'npc': 1600 },
        'xp': { 'mining': 0 }
    },
    'ENCHANTED_SULPHUR_CUBE': {
        'display': 'Enchanted Sulphur Cube',
        "prices": { 'npc': 256000 },
        'xp': { 'mining': 0 }
    },
    'CORRUPTED_FRAGMENT': {
        'display': 'Corrupted Fragment',
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0 }
    },
    'COBBLESTONE': {
        'display': 'Cobblestone',
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0.1 }
    },
    'ENCHANTED_COBBLESTONE': {
        'display': 'Enchanted Cobblestone',
        "prices": { 'npc': 160 },
        'xp': { 'mining': 16 }
    },
    'STONE': {
        'display': 'Stone',  # not in bazaar
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0.1 }
    },
    'OBSIDIAN': {
        'display': 'Obsidian',
        "prices": { 'npc': 7 },
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_OBSIDIAN': {
        'display': 'Enchanted Obsidian',
        "prices": { 'npc': 1440 },
        'xp': { 'mining': 64 }
    },
    'GLOWSTONE_DUST': {
        'display': 'Glowstone Dust',
        "prices": { 'npc': 2 },
        'xp': { 'mining': 0.2 }
    },
    'GLOWSTONE': {
        'display': 'Glowstone',  # not in bazaar
        "prices": { 'npc': 8 },
        'xp': { 'mining': 0.8 }
    },
    'ENCHANTED_GLOWSTONE_DUST': {
        'display': 'Enchanted Glowstone Dust',
        "prices": { 'npc': 320 },
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_GLOWSTONE': {
        'display': 'Enchanted Glowstone',
        "prices": { 'npc': 51200 },
        'xp': { 'mining': 6144 }  # correct
    },
    'GRAVEL': {
        'display': 'Gravel',
        "prices": { 'npc': 3 },
        'xp': { 'mining': 0.2 }
    },
    'FLINT': {
        'display': 'Flint',
        "prices": { 'npc': 4 },
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_FLINT': {
        'display': 'Enchanted Flint',
        "prices": { 'npc': 640 },
        'xp': { 'mining': 32 }
    },
    'SAND': {
        'display': 'Sand',
        "prices": { 'npc': 2 },
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_SAND': {
        'display': 'Enchanted Sand',
        "prices": { 'npc': 320 },
        'xp': { 'mining': 32 }
    },
    'SAND:1': {
        'display': 'Red Sand',
        "prices": { 'npc': 5 },
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_RED_SAND': {
        'display': 'Enchanted Red Sand',
        "prices": { 'npc': 800 },
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_RED_SAND_CUBE': {
        'display': 'Enchanted Red Sand Cube',
        "prices": { 'npc': 128000 },
        'xp': { 'mining': 5120 }
    },
    'GLASS': {
        'display': 'Glass',  # not in bazaar
        "prices": { 'npc': 2 },
        'xp': { 'mining': 0 }
    },
    'MYCEL': {
        'display': 'Mycelium',
        "prices": { 'npc': 5 },
        'xp': { 'mining': 0.2 }
    },
    'ENCHANTED_MYCELIUM': {
        'display': 'Enchanted Mycelium',
        "prices": { 'npc': 800 },
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_MYCELIUM_CUBE': {
        'display': 'Enchanted Mycelium Cube',
        "prices": { 'npc': 128000 },
        'xp': { 'mining': 5120 }
    },
    'CLAY_BALL': {
        'display': 'Clay Ball',
        "prices": { 'npc': 3 },
        'xp': { 'fishing': 0.1 }
    },
    'CLAY': {
        'display': 'Clay',  # not in bazaar
        "prices": { 'npc': 12 },
        'xp': { 'fishing': 0.4 }
    },
    'ENCHANTED_CLAY_BALL': {
        'display': 'Enchanted Clay Ball',
        "prices": { 'npc': 480 },
        'xp': { 'fishing': 16 }
    },
    'ENCHANTED_CLAY_BLOCK': {
        'display': 'Enchanted Clay Block', # all correct
        "prices": { 'npc': 76800 },
        'xp': { 'fishing': 2560 }
    },
    'CLAY_BRICK': {
        'display': 'Brick',  # not in bazaar
        "prices": { 'npc': 2 },
        'xp': { 'mining': 0 }
    },
    'BRICK': {
        'display': 'Bricks',  # not in bazaar
        "prices": { 'npc': 3 },
        'xp': { 'mining': 0 }
    },
    'ICE': {
        'display': 'Ice',
        "prices": { 'npc': 0.5 },
        'xp': { 'mining': 0.5 }
    },
    'PACKED_ICE': {
        'display': 'Packed Ice',
        "prices": { 'npc': 4.5 },
        'xp': { 'mining': 4.5 }
    },
    'ENCHANTED_ICE': {
        'display': 'Enchanted Ice',
        "prices": { 'npc': 80 },
        'xp': { 'mining': 80 }
    },
    'ENCHANTED_PACKED_ICE': {
        'display': 'Enchanted Packed Ice',
        "prices": { 'npc': 12800 },
        'xp': { 'mining': 12800 }
    },
    'SNOW_BALL': {
        'display': 'Snowball',
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0.1 }
    },
    'SNOW_BLOCK': {
        'display': 'Snow Block',
        "prices": { 'npc': 4 },
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_SNOW_BLOCK': {
        'display': 'Enchanted Snow Block',  # correct
        "prices": { 'npc': 600 },
        'xp': { 'mining': 64 }
    },
    'COAL': {
        'display': 'Coal',
        "prices": { 'npc': 2 },
        'xp': { 'mining': 0.3 },
        'upgrade': { 'speed': 5, 'drop': 1, 'duration': 1800 }
    },
    'COAL_BLOCK': {
        'display': 'Block of Coal',  # not in bazaar
        "prices": { 'npc': 18 },
        'xp': { 'mining': 2.7 },
        'upgrade': { 'speed': 5, 'drop': 1, 'duration': 18000 }
    },
    'ENCHANTED_COAL': {
        'display': 'Enchanted Coal',
        "prices": { 'npc': 320 },
        'xp': { 'mining': 48 },
        'upgrade': { 'speed': 10, 'drop': 1, 'duration': 86400 }
    },
    'ENCHANTED_COAL_BLOCK': {
        'display': 'Enchanted Coal Block',
        "prices": { 'npc': 51000 },  # correct
        'xp': { 'mining': 7680 }
    },
    'IRON_ORE': {
        'display': 'Iron Ore',  # not in bazaar
        "prices": { 'npc': 3 },
        'xp': { 'mining': 0.3 }
    },
    'IRON_INGOT': {
        'display': 'Iron Ingot',
        "prices": { 'npc': 3 },
        'xp': { 'mining': 0.3 }
    },
    'IRON_BLOCK': {
        'display': 'Block of Iron',  # not in bazaar
        "prices": { 'npc': 27 },
        'xp': { 'mining': 2.7 }
    },
    'ENCHANTED_IRON': {
        'display': 'Enchanted Iron Ingot',
        "prices": { 'npc': 480 },
        'xp': { 'mining': 48 }
    },
    'ENCHANTED_IRON_BLOCK': {
        'display': 'Enchanted Iron Block',
        "prices": { 'npc': 76800 },
        'xp': { 'mining': 7680 }
    },
    'GOLD_ORE': {
        'display': 'Gold Ore',  # not in bazaar
        "prices": { 'npc': 3 },
        'xp': { 'mining': 0.4 }
    },
    'GOLD_INGOT': {
        'display': 'Gold Ingot',
        "prices": { 'npc': 4 },
        'xp': { 'mining': 0.4 }
    },
    'GOLD_BLOCK': {
        'display': 'Block of Gold',  # not in bazaar
        "prices": { 'npc': 36 },
        'xp': { 'mining': 3.6 }
    },
    'ENCHANTED_GOLD': {
        'display': 'Enchanted Gold Ingot',
        "prices": { 'npc': 640 },
        'xp': { 'mining': 64 }
    },
    'ENCHANTED_GOLD_BLOCK': {
        'display': 'Enchanted Gold Block',  # correct
        "prices": { 'npc': 102000 },
        'xp': { 'mining': 10240 }
    },
    'DIAMOND': {
        'display': 'Diamond',
        "prices": { 'npc': 8 },
        'xp': { 'mining': 0.4 }
    },
    'DIAMOND_BLOCK': {
        'display': 'Block of Diamond',  # not in bazaar
        "prices": { 'npc': 72 },
        'xp': { 'mining': 3.6 }
    },
    'ENCHANTED_DIAMOND': {
        'display': 'Enchanted Diamond',
        "prices": { 'npc': 1280 },
        'xp': { 'mining': 64 }
    },
    'ENCHANTED_DIAMOND_BLOCK': {
        'display': 'Enchanted Diamond Block',
        "prices": { 'npc': 204800 },
        'xp': { 'mining': 10240 }
    },
    'INK_SACK:4': {
        'display': 'Lapis Lazuli',
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0.1 }
    },
    'LAPIS_BLOCK': {
        'display': 'Block of Lapis Lazuli',  # not in bazaar
        "prices": { 'npc': 9 },
        'xp': { 'mining': 0.9 }
    },
    'ENCHANTED_LAPIS_LAZULI': {
        'display': 'Enchanted Lapis Lazuli',
        "prices": { 'npc': 160 },
        'xp': { 'mining': 16 }
    },
    'ENCHANTED_LAPIS_LAZULI_BLOCK': {
        'display': 'Enchanted Lapis Lazuli Block',
        "prices": { 'npc': 25600 },
        'xp': { 'mining': 2560 }
    },
    'REDSTONE': {
        'display': 'Redstone Dust',
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0.2 }
    },
    'REDSTONE_BLOCK': {
        'display': 'Block of Redstone',  # not in bazaar
        "prices": { 'npc': 9 },
        'xp': { 'mining': 1.8 }
    },
    'ENCHANTED_REDSTONE': {
        'display': 'Enchanted Redstone Dust',
        "prices": { 'npc': 160 },
        'xp': { 'mining': 32 }
    },
    'ENCHANTED_REDSTONE_BLOCK': {
        'display': 'Enchanted Redstone Block',
        "prices": { 'npc': 25600 },
        'xp': { 'mining': 5120 }
    },
    'EMERALD': {
        'display': 'Emerald',
        "prices": { 'npc': 6 },
        'xp': { 'mining': 0.4 }
    },
    'EMERALD_BLOCK': {
        'display': 'Block of Emerald',  # not in bazaar
        "prices": { 'npc': 54 },
        'xp': { 'mining': 3.6 }
    },
    'ENCHANTED_EMERALD': {
        'display': 'Enchanted Emerald',
        "prices": { 'npc': 960 },
        'xp': { 'mining': 64 }
    },
    'ENCHANTED_EMERALD_BLOCK': {
        'display': 'Enchanted Emerald Block',
        "prices": { 'npc': 153600 },
        'xp': { 'mining': 10240 }
    },
    'QUARTZ': {
        'display': 'Nether Quartz',
        "prices": { 'npc': 4 },
        'xp': { 'mining': 0.3 }
    },
    'QUARTZ_BLOCK': {
        'display': 'Block of Quartz',  # not in bazaar
        "prices": { 'npc': 16 },
        'xp': { 'mining': 1.2 }
    },
    'ENCHANTED_QUARTZ': {
        'display': 'Enchanted Nether Quartz',
        "prices": { 'npc': 640 },
        'xp': { 'mining': 48 }
    },
    'ENCHANTED_QUARTZ_BLOCK': {
        'display': 'Enchanted Quartz Block',
        "prices": { 'npc': 102400 },
        'xp': { 'mining': 7680 }
    },
    'ENDER_STONE': {
        'display': 'End Stone',
        "prices": { 'npc': 2 },
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_ENDSTONE': {
        'display': 'Enchanted End Stone',
        "prices": { 'npc': 320 },
        'xp': { 'mining': 64 }  # correct
    },
    'MITHRIL_ORE': {
        'display': 'Mithril',
        "prices": { 'npc': 8 },
        'xp': { 'mining': 0.4 }
    },
    'ENCHANTED_MITHRIL': {
        'display': 'Enchanted Mithril',
        "prices": { 'npc': 1280 },
        'xp': { 'mining': 64 }
    },
    'REFINED_MITHRIL': {
        'display': 'Refined Mithril',
        "prices": { 'custom': 650000 }
    },
    'HARD_STONE': {
        'display': 'Hard Stone',
        "prices": { 'npc': 1 },
        'xp': { 'mining': 0.1 }
    },
    'ENCHANTED_HARD_STONE': {
        'display': 'Enchanted Hard Stone',
        "prices": { 'npc': 576 },
        'xp': { 'mining': 57.6 }
    },
    'CONCENTRATED_STONE': {
        'display': 'Concentrated Stone',  # correct
        "prices": { 'npc': 200000 },
        'xp': { 'mining': 33177.6 }
    },
    'WHEAT': {
        'display': 'Wheat',
        "prices": { 'npc': 6 },
        'xp': { 'farming': 0.2 }
    },
    'HAY_BLOCK': {
        'display': 'Hay Bale',  # not produced anymore by minions
        "prices": { 'npc': 54 },
        'xp': { 'farming': 1.8 }
    },
    'SEEDS': {
        'display': 'Seeds',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_BREAD': {
        'display': 'Enchanted Bread',
        "prices": { 'npc': 60 },  # correct
        'xp': { 'farming': 1.8 },  # not produced anymore by minions
        "upgrade": { 'speed': 5, 'drop': 1, 'duration': 43200 }
    },
    'ENCHANTED_WHEAT': {
        'display': 'Enchanted Wheat',
        "prices": { 'npc': 960 },
        'xp': { 'farming': 32 }  # correct
    },
    'ENCHANTED_HAY_BALE': {
        'display': 'Enchanted Hay Bale',
        "prices": { 'npc': 153600 },
        'xp': { 'farming': 5120 }  # correct
    },
    'ENCHANTED_SEEDS': {
        'display': 'Enchanted Seeds',
        "prices": { 'npc': 480 },
        'xp': { 'farming': 16 }
    },
    'BOX_OF_SEEDS': {
        'display': 'Box of Seeds',
        "prices": { 'npc': 76800 },
        'xp': { 'farming': 2560 }
    },
    'MELON': {
        'display': 'Melon Slice',
        "prices": { 'npc': 2 },
        'xp': { 'farming': 0.1 }
    },
    'MELON_BLOCK': {
        'display': 'Melon',
        "prices": { 'npc': 18 },
        'xp': { 'farming': 0.9 }
    },
    'ENCHANTED_MELON': {
        'display': 'Enchanted Melon Slice',
        "prices": { 'npc': 320 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_MELON_BLOCK': {
        'display': 'Enchanted Melon',
        "prices": { 'npc': 51200 },
        'xp': { 'farming': 2560 }
    },
    'PUMPKIN': {
        'display': 'Pumpkin',
        "prices": { 'npc': 10 },
        'xp': { 'farming': 0.3 }
    },
    'ENCHANTED_PUMPKIN': {
        'display': 'Enchanted Pumpkin',
        "prices": { 'npc': 1600 },
        'xp': { 'farming': 48 }
    },
    'POLISHED_PUMPKIN': {
        'display': 'Polished Pumpkin',
        "prices": { 'npc': 256000 },
        'xp': { 'farming': 7680 }
    },
    'CARROT_ITEM': {
        'display': 'Carrot',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_CARROT': {
        'display': 'Enchanted Carrot',  # correct
        "prices": { 'npc': 480 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_GOLDEN_CARROT': {
        'display': 'Enchanted Golden Carrot',
        "prices": { 'npc': 61440 }  # correct
    },
    'POTATO_ITEM': {
        'display': 'Potato',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_POTATO': {
        'display': 'Enchanted Potato',  # correct
        "prices": { 'npc': 480 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_BAKED_POTATO': {
        'display': 'Enchanted Baked Potato',
        "prices": { 'npc': 76800 },
        'xp': { 'farming': 2560 }
    },
    'RED_MUSHROOM': {
        'display': 'Red Mushroom',
        "prices": { 'npc': 10 },
        'xp': { 'farming': 0.3 }
    },
    'BROWN_MUSHROOM': {
        'display': 'Brown Mushroom',
        "prices": { 'npc': 10 },
        'xp': { 'farming': 0.3 }
    },
    'HUGE_MUSHROOM_2': {
        'display': 'Red Mushroom Block',
        "prices": { 'npc': 10 },  # correct
        'xp': { 'farming': 0.3 }  # correct
    },
    'HUGE_MUSHROOM_1': {
        'display': 'Brown Mushroom Block',
        "prices": { 'npc': 10 },  # correct
        'xp': { 'farming': 0.3 }  # correct
    },
    'ENCHANTED_RED_MUSHROOM': {
        'display': 'Enchanted Red Mushroom',
        "prices": { 'npc': 1600 },
        'xp': { 'farming': 48 }
    },
    'ENCHANTED_BROWN_MUSHROOM': {
        'display': 'Enchanted Brown Mushroom',
        "prices": { 'npc': 1600 },
        'xp': { 'farming': 48 }
    },
    'ENCHANTED_HUGE_MUSHROOM_2': {
        'display': 'Enchanted Red Mushroom Block',
        "prices": { 'npc': 51200 },
        'xp': { 'farming': 1536 }
    },
    'ENCHANTED_HUGE_MUSHROOM_1': {
        'display': 'Enchanted Brown Mushroom Block',
        "prices": { 'npc': 51200 },
        'xp': { 'farming': 1536 }
    },
    'CACTUS': {
        'display': 'Cactus',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.2 }
    },
    'INK_SACK:2': {
        'display': 'Cactus Green',  # not in bazaar
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_CACTUS_GREEN': {
        'display': 'Enchanted Cactus Green',
        "prices": { 'npc': 480 },
        'xp': { 'farming': 80 }  # correct
    },
    'ENCHANTED_CACTUS': {
        'display': 'Enchanted Cactus',
        "prices": { 'npc': 76800 },
        'xp': { 'farming': 12800 }  # correct
    },
    'INK_SACK:3': {
        'display': 'Cocoa Beans',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_COCOA': {
        'display': 'Enchanted Cocoa Beans',
        "prices": { 'npc': 480 },
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_COOKIE': {
        'display': 'Enchanted Cookie',
        "prices": { 'npc': 61500 }  # correct
    },
    'SUGAR_CANE': {
        'display': 'Sugar Cane',
        "prices": { 'npc': 4 },
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_SUGAR': {
        'display': 'Enchanted Sugar',
        "prices": { 'npc': 640 },
        'xp': { 'alchemy': 16 }  # correct type
    },
    'ENCHANTED_SUGAR_CANE': {
        'display': 'Enchanted Sugar Cane',
        "prices": { 'npc': 102400 },
        'xp': { 'farming': 2560 }  # correct type
    },
    'NETHER_STALK': {
        'display': 'Nether Wart',
        "prices": { 'npc': 4 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_NETHER_STALK': {
        'display': 'Enchanted Nether Wart',  # correct
        "prices": { 'npc': 640 },
        'xp': { 'farming': 32 }
    },
    'MUTANT_NETHER_STALK': {
        'display': 'Mutant Nether Wart',  # correct
        "prices": { 'npc': 102400 },
        'xp': { 'farming': 5120 }
    },
    'YELLOW_FLOWER': {
        'display': 'Dandelion',
        "prices": { 'npc': 1 },
        'xp': { 'foraging': 0.1 }
    },
    'RED_ROSE': {
        'display': 'Poppy',
        "prices": { 'npc': 1 },
        'xp': { 'foraging': 0.1 }
    },
    'SMALL_FLOWER': {
        'display': 'Small Flower',  # not in bazaar
        "prices": { 'npc': 1 },
        'xp': { 'foraging': 0.1 }
    },
    'LARGE_FLOWER': {
        'display': 'Large Flower',  # not in bazaar
        "prices": { 'npc': 1 },
        'xp': { 'foraging': 0.2 }
    },
    'ENCHANTED_DANDELION': {
        'display': 'Enchanted Dandelion',
        "prices": { 'npc': 160 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_POPPY': {
        'display': 'Enchanted Poppy',
        "prices": { 'npc': 576 },
        'xp': { 'foraging': 57.6 }
    },
    'RAW_FISH': {
        'display': 'Raw Cod',
        "prices": { 'npc': 6 },
        'xp': { 'fishing': 0.5 }
    },
    'RAW_FISH:1': {
        'display': 'Raw Salmon',
        "prices": { 'npc': 10 },
        'xp': { 'fishing': 0.7 }
    },
    'RAW_FISH:3': {
        'display': 'Pufferfish',
        "prices": { 'npc': 15 },
        'xp': { 'fishing': 1 }
    },
    'RAW_FISH:2': {
        'display': 'Tropical Fish',
        "prices": { 'npc': 20 },
        'xp': { 'fishing': 2 }
    },
    'PRISMARINE_CRYSTALS': {
        'display': 'Prismarine Crystals',
        "prices": { 'npc': 5 },
        'xp': { 'fishing': 0.5 }
    },
    'PRISMARINE_SHARD': {
        'display': 'Prismarine Shard',
        "prices": { 'npc': 5 },
        'xp': { 'fishing': 0.5 }
    },
    'SPONGE': {
        'display': 'Sponge',
        "prices": { 'npc': 50 },
        'xp': { 'fishing': 0.5 }
    },
    'ENCHANTED_RAW_FISH': {
        'display': 'Enchanted Raw Cod',
        "prices": { 'npc': 960 },
        'xp': { 'fishing': 80 }
    },
    'ENCHANTED_RAW_SALMON': {
        'display': 'Enchanted Raw Salmon',
        "prices": { 'npc': 1600 },
        'xp': { 'fishing': 112 }
    },
    'ENCHANTED_PUFFERFISH': {
        'display': 'Enchanted Pufferfish',
        "prices": { 'npc': 2400 },
        'xp': { 'fishing': 160 }
    },
    'ENCHANTED_CLOWNFISH': {
        'display': 'Enchanted Tropical Fish',
        "prices": { 'npc': 3200 },
        'xp': { 'fishing': 320 }
    },
    'ENCHANTED_PRISMARINE_CRYSTALS': {
        'display': 'Enchanted Prismarine Crystals',
        "prices": { 'npc': 400 },
        'xp': { 'fishing': 40 }
    },
    'ENCHANTED_PRISMARINE_SHARD': {
        'display': 'Enchanted Prismarine Shard',
        "prices": { 'npc': 400 },
        'xp': { 'fishing': 40 }
    },
    'ENCHANTED_SPONGE': {
        'display': 'Enchanted Sponge',
        "prices": { 'npc': 2000 },
        'xp': { 'fishing': 20 }
    },
    'ENCHANTED_COOKED_FISH': {
        'display': 'Enchanted Cooked Cod',  # correct
        "prices": { 'npc': 150000 },
        'xp': { 'fishing': 12800 }
    },
    'ENCHANTED_COOKED_SALMON': {
        'display': 'Enchanted Cooked Salmon',
        "prices": { 'npc': 256000 },
        'xp': { 'fishing': 17920 }
    },
    'ENCHANTED_WET_SPONGE': {
        'display': 'Enchanted Wet Sponge',
        "prices": { 'npc': 80000 },
        'xp': { 'fishing': 800 }
    },
    'ROTTEN_FLESH': {
        'display': 'Rotten Flesh',
        "prices": { 'npc': 2 },
        'xp': { 'combat': 0.3 }
    },
    'POISONOUS_POTATO': {
        'display': 'Poisonous Potato',
        "prices": { 'npc': 10 },
        'xp': { 'farming': 0 }
    },
    'ENCHANTED_ROTTEN_FLESH': {
        'display': 'Enchanted Rotten Flesh',
        "prices": { 'npc': 320 },
        'xp': { 'combat': 48 }
    },
    'ENCHANTED_POISONOUS_POTATO': {
        'display': 'Enchanted Poisonous Potato',
        "prices": { 'npc': 1600 },
        'xp': { 'farming': 0 }
    },
    'ENCHANTED_ENDER_PEARL': {
        'display': 'Enchanted Ender Pearl',
        "prices": { 'npc': 140 },
        'xp': { 'combat': 9 }
    },
    'ENCHANTED_EYE_OF_ENDER': {
        'display': 'Enchanted Eye of Ender',
        "prices": { "custom": 6500 }
    },
    'DYE_BYZANTIUM': {
        'display': 'Byzantium Dye',  # not in bazaar (AH), also not used
        "prices": { 'npc': 0 },
        'xp': { 'combat': 0 }
    },
    'ABSOLUTE_ENDER_PEARL': {
        'display': 'Absolute Ender Pearl',
        "prices": { 'npc': 11200 },
        'xp': { 'combat': 720 }  # correct
    },
    'CRUDE_GABAGOOL': {
        'display': 'Crude Gabagool',
        "prices": { 'npc': 1 },
        'xp': { 'combat': 0 }
    },
    'VERY_CRUDE_GABAGOOL': {
        'display': 'Very Crude Gabagool',
        "prices": { 'npc': 1 },  # correct
        'xp': { 'combat': 0 }
    },
    'DYE_FLAME': {
        'display': 'Flame Dye',  # not in bazaar (AH), also not used
        "prices": { 'npc': 0 },
        'xp': { 'combat': 0 }
    },
    'CHILI_PEPPER': {
        'display': 'Chili Pepper',
        "prices": { 'npc': 5000 },
        'xp': { 'combat': 0 }
    },
    'STUFFED_CHILI_PEPPER': {
        'display': 'Stuffed Chili Pepper',
        "prices": { 'npc': 200000 },  # correct
        'xp': { 'combat': 0 }
    },
    'INFERNO_VERTEX': {
        'display': 'Inferno Vertex',
        "prices": { 'npc': 0, "custom": 6500000 },
        'xp': { 'combat': 0 }
    },
    'INFERNO_APEX': {
        'display': 'Inferno Apex',
        "prices": { 'npc': 0, "custom": 150000000 },
        'xp': { 'combat': 0 }
    },
    'REAPER_PEPPER': {
        'display': 'Reaper Pepper',
        "prices": { 'npc': 0 },
        'xp': { 'combat': 0 }
    },
    'GABAGOOL_THE_FISH': {
        'display': 'Gabagool the Fish',  # not in bazaar (AH)
        "prices": { "custom": 11000000 },  # 2025-10-6
        'xp': { 'combat': 0 }  # unsure if correctly implemented
    },
    'HYPERGOLIC_IONIZED_CERAMICS': {
        'display': 'Hypergolic Ionized Ceramics',
        "prices": { 'npc': 0 },
        'xp': { 'combat': 0 }
    },
    'HEMOVIBE': {
        'display': 'Hemovibe',
        "prices": { 'npc': 100 },
        'xp': { 'combat': 5 }
    },
    'HEMOGLASS': {
        'display': 'Hemoglass',
        "prices": { 'npc': 16000 },
        'xp': { 'combat': 800 }  # correct
    },
    'HEMOBOMB': {
        'display': 'Hemobomb',
        "prices": { 'npc': 240000 },
        'xp': { 'combat': 0 }
    },
    'BONE': {
        'display': 'Bone',
        "prices": { 'npc': 2 },
        'xp': { 'combat': 0.2 }
    },
    'ENCHANTED_BONE': {
        'display': 'Enchanted Bone',
        "prices": { 'npc': 320 },
        'xp': { 'combat': 32 }
    },
    'SULPHUR': {
        'display': 'Gunpowder',
        "prices": { 'npc': 4 },
        'xp': { 'combat': 0.3 }
    },
    'ENCHANTED_GUNPOWDER': {
        'display': 'Enchanted Gunpowder',
        "prices": { 'npc': 640 },
        'xp': { 'combat': 48 }
    },
    'ENCHANTED_FIREWORK_ROCKET': {
        'display': 'Enchanted Firework Rocket',
        "prices": { 'npc': 41000 }  # correct
    },
    'STRING': {
        'display': 'String',
        "prices": { 'npc': 3 },
        'xp': { 'combat': 0.2 }
    },
    'SPIDER_EYE': {
        'display': 'Spider Eye',
        "prices": { 'npc': 3 },
        'xp': { 'combat': 0.3 }
    },
    'ENCHANTED_STRING': {
        'display': 'Enchanted String',
        "prices": { 'npc': 576 },  # correct
        'xp': { 'combat': 38 }  # correct
    },
    'ENCHANTED_SPIDER_EYE': {
        'display': 'Enchanted Spider Eye',
        "prices": { 'npc': 480 },
        'xp': { 'combat': 48 }
    },
    'ENCHANTED_FERMENTED_SPIDER_EYE': {
        'display': 'Enchanted Fermented Spider Eye',
        "prices": { 'npc': 31000 }
    },
    'BLAZE_ROD': {
        'display': 'Blaze Rod',
        "prices": { 'npc': 9 },
        'xp': { 'combat': 0.3 }
    },
    'ENCHANTED_BLAZE_POWDER': {
        'display': 'Enchanted Blaze Powder',
        "prices": { 'npc': 1440 },
        'xp': { 'combat': 48 }
    },
    'ENCHANTED_BLAZE_ROD': {
        'display': 'Enchanted Blaze Rod',
        "prices": { 'npc': 230400 },
        'xp': { 'combat': 7680 }
    },
    'MAGMA_CREAM': {
        'display': 'Magma Cream',
        "prices": { 'npc': 8 },
        'xp': { 'combat': 0.2 }
    },
    'ENCHANTED_MAGMA_CREAM': {
        'display': 'Enchanted Magma Cream',
        "prices": { 'npc': 1280 },
        'xp': { 'combat': 32 }
    },
    'WHIPPED_MAGMA_CREAM': {
        'display': 'Whipped Magma Cream',
        "prices": { 'npc': 204800 },
        'xp': { 'combat': 5120 }
    },
    'ENDER_PEARL': {
        'display': 'Ender Pearl',
        "prices": { 'npc': 7 },
        'xp': { 'combat': 0.3 }
    },
    'GHAST_TEAR': {
        'display': 'Ghast Tear',
        "prices": { 'npc': 16 },
        'xp': { 'combat': 0.5 }
    },
    'ENCHANTED_GHAST_TEAR': {
        'display': 'Enchanted Ghast Tear',
        "prices": { 'npc': 80 },
        'xp': { 'combat': 7.5 }  # correct
    },
    'SILVER_FANG': {
        'display': 'Silver Fang',  # no xp entry is correct, cannot be made in minion
        "prices": { 'npc': 2000 }
    },
    'SLIME_BALL': {
        'display': 'Slimeball',
        "prices": { 'npc': 5 },
        'xp': { 'combat': 0.2 }
    },
    'SLIME_BLOCK': {
        'display': 'Slime Block',  # not in bazaar
        "prices": { 'npc': 45 },
        'xp': { 'combat': 1.8 }
    },
    'ENCHANTED_SLIME_BALL': {
        'display': 'Enchanted Slimeball',
        "prices": { 'npc': 800 },
        'xp': { 'combat': 32 }
    },
    'ENCHANTED_SLIME_BLOCK': {
        'display': 'Enchanted Slime Block',
        "prices": { 'npc': 128000 },
        'xp': { 'combat': 5120 }
    },
    'RAW_BEEF': {
        'display': 'Raw Beef',
        "prices": { 'npc': 4 },
        'xp': { 'farming': 0.1 }
    },
    'LEATHER': {
        'display': 'Leather',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_RAW_BEEF': {
        'display': 'Enchanted Raw Beef',
        "prices": { 'npc': 640 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_LEATHER': {
        'display': 'Enchanted Leather',
        "prices": { 'npc': 480 },  # correct
        'xp': { 'farming': 115 }  # correct
    },
    'PORK': {
        'display': 'Raw Porkchop',  # correct
        "prices": { 'npc': 5 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_PORK': {
        'display': 'Enchanted Raw Porkchop',  # correct
        "prices": { 'npc': 800 },
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_GRILLED_PORK': {
        'display': 'Enchanted Cooked Porkchop',  # correct
        "prices": { 'npc': 128000 },
        'xp': { 'farming': 5120 }
    },
    'RAW_CHICKEN': {
        'display': 'Raw Chicken',
        "prices": { 'npc': 4 },
        'xp': { 'farming': 0.1 }
    },
    'FEATHER': {
        'display': 'Feather',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.2 }
    },
    'EGG': {
        'display': 'Egg',
        "prices": { 'npc': 3 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_RAW_CHICKEN': {
        'display': 'Enchanted Raw Chicken',
        "prices": { 'npc': 640 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_FEATHER': {
        'display': 'Enchanted Feather',
        "prices": { 'npc': 480 },
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_EGG': {
        'display': 'Enchanted Egg',
        "prices": { 'npc': 432 },  # correct
        'xp': { 'farming': 115 },  # correct
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "add", "item": { "EGG": 1 } }
        }
    },
    'SUPER_EGG': {
        'display': 'Super Enchanted Egg',
        "prices": { 'npc': 0 },  # correct
        'xp': { 'farming': 16560 }
    },
    'OMEGA_EGG': {
        'display': 'Omega Enchanted Egg',
        "prices": { 'npc': 0 },
        'xp': { 'farming': 149040 }
    },
    'WOOL': {
        'display': 'White Wool',
        "prices": { 'npc': 2 },
        'xp': { 'farming': 0.1 }
    },
    'MUTTON': {
        'display': 'Raw Mutton',
        "prices": { 'npc': 5 },
        'xp': { 'farming': 0.1 }
    },
    'ENCHANTED_WOOL': {
        'display': 'Enchanted Wool',
        "prices": { 'npc': 320 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_MUTTON': {
        'display': 'Enchanted Raw Mutton',
        "prices": { 'npc': 800 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_COOKED_MUTTON': {
        'display': 'Enchanted Cooked Mutton',
        "prices": { 'npc': 128000 },
        'xp': { 'farming': 2560 }
    },
    'RABBIT': {
        'display': 'Raw Rabbit',
        "prices": { 'npc': 4 },
        'xp': { 'farming': 0.1 }
    },
    'RABBIT_FOOT': {
        'display': "Rabbit's Foot",
        "prices": { 'npc': 5 },
        'xp': { 'farming': 0.2 }
    },
    'RABBIT_HIDE': {
        'display': 'Rabbit Hide',
        "prices": { 'npc': 5 },
        'xp': { 'farming': 0.2 }
    },
    'ENCHANTED_RABBIT': {
        'display': 'Enchanted Raw Rabbit',  # both correct
        "prices": { 'npc': 640 },
        'xp': { 'farming': 16 }
    },
    'ENCHANTED_COOKED_RABBIT': {
        'display': 'Enchanted Cooked Rabbit',  # both correct
        "prices": { 'npc': 102400 },
        'xp': { 'farming': 2560 }
    },
    'ENCHANTED_RABBIT_FOOT': {
        'display': 'Enchanted Rabbit Foot',  # both correct
        "prices": { 'npc': 800 },
        'xp': { 'farming': 32 }
    },
    'ENCHANTED_RABBIT_HIDE': {
        'display': 'Enchanted Rabbit Hide',  # both correct
        "prices": { 'npc': 800 },
        'xp': { 'farming': 115 }
    },
    'LOG': {
        'display': 'Oak Log',
        "prices": { 'npc': 2 },
        'xp': { 'foraging': 0.1 }
    },
    'LOG:1': {
        'display': 'Spruce Log',
        "prices": { 'npc': 2 },
        'xp': { 'foraging': 0.1 }
    },
    'LOG:2': {
        'display': 'Birch Log',
        "prices": { 'npc': 2 },
        'xp': { 'foraging': 0.1 }
    },
    'LOG_2:1': {
        'display': 'Dark Oak Log',
        "prices": { 'npc': 2 },
        'xp': { 'foraging': 0.1 }
    },
    'LOG_2': {
        'display': 'Acacia Log',
        "prices": { 'npc': 2 },
        'xp': { 'foraging': 0.1 }
    },
    'LOG:3': {
        'display': 'Jungle Log',
        "prices": { 'npc': 2 },
        'xp': { 'foraging': 0.1 }
    },
    'ENCHANTED_OAK_LOG': {
        'display': 'Enchanted Oak Log',
        "prices": { 'npc': 320 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_SPRUCE_LOG': {
        'display': 'Enchanted Spruce Log',
        "prices": { 'npc': 320 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_BIRCH_LOG': {
        'display': 'Enchanted Birch Log',
        "prices": { 'npc': 320 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_DARK_OAK_LOG': {
        'display': 'Enchanted Dark Oak Log',
        "prices": { 'npc': 320 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_ACACIA_LOG': {
        'display': 'Enchanted Acacia Log',
        "prices": { 'npc': 320 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_JUNGLE_LOG': {
        'display': 'Enchanted Jungle Log',
        "prices": { 'npc': 320 },
        'xp': { 'foraging': 16 }
    },
    'ENCHANTED_CHARCOAL': {
        'display': 'Enchanted Charcoal',
        "prices": {},
        "upgrade": { 'speed': 20, 'drop': 1, 'duration': 129600 }
    },
    'HAMSTER_WHEEL': {
        'display': 'Hamster Wheel',
        "prices": {},
        "upgrade": { 'speed': 50, 'drop': 1, 'duration': 86400 }
    },
    'FOUL_FLESH': {
        'display': 'Foul Flesh',
        "prices": {},
        "upgrade": { 'speed': 90, 'drop': 1, 'duration': 18000 }
    },
    'CATALYST': {
        'display': 'Catalyst',
        "prices": {},
        "upgrade": { 'speed': 0, 'drop': 3, 'duration': 10800 }
    },
    'HYPER_CATALYST': {
        'display': 'Hyper Catalyst',
        "prices": {},
        "upgrade": { 'speed': 0, 'drop': 4, 'duration': 21600 }
    },
    'CHEESE_FUEL': {
        'display': 'Tasty Cheese',
        "prices": {},
        "upgrade": { 'speed': 0, 'drop': 2, 'duration': 3600 }
    },
    'SOLAR_PANEL': {
        'display': 'Solar Panel',
        "prices": {},
        "upgrade": { 'speed': 25, 'drop': 1, 'duration': 0 }
    },
    'ENCHANTED_LAVA_BUCKET': {
        'display': 'Enchanted Lava Bucket',
        "prices": {},
        "upgrade": { 'speed': 25, 'drop': 1, 'duration': 0 }
    },
    'MAGMA_BUCKET': {
        'display': 'Magma Bucket',
        "prices": {},
        "upgrade": { 'speed': 30, 'drop': 1, 'duration': 0 }
    },
    'PLASMA_BUCKET': {
        'display': 'Plasma Bucket',
        "prices": {},
        "upgrade": { 'speed': 35, 'drop': 1, 'duration': 0 }
    },
    'INFERNO_FUEL': {
        'display': 'Inferno Minion Fuel',
        "prices": { "custom": 1 },  # this custom price will be automatically updated by the calculator based on grade and distilate
        "upgrade": { 'speed': 0, 'drop': 1, 'duration': 86400 }
    },
    'BUDGET_HOPPER': {
        'display': 'Budget Hopper',
        "prices": { "custom": 10000 }
    },
    'ENCHANTED_HOPPER': {
        'display': 'Enchanted Hopper',
        "prices": { "custom": 1200000 }
    },
    'AUTO_SMELTER': {
        'display': 'Auto Smelter',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "replace", "list": smelting_data }
        }
    },
    'COMPACTOR': {
        'display': 'Compactor',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "compact" }
        }
    },
    'SUPER_COMPACTOR_3000': {
        'display': 'Super Compactor 3000',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "enchant" }
        }
    },
    'DWARVEN_COMPACTOR': {
        'display': 'Dwarven Super Compactor',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "replace, enchant", "list": smelting_data }
        }
    },
    'DIAMOND_SPREADING': {
        'display': 'Diamond Spreading',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "generate", "item": { "DIAMOND": 1 }, "chance": 0.1 }
        }
    },
    'POTATO_SPREADING': {
        'display': 'Potato Spreading',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "generate", "item": { "POTATO_ITEM": 1 }, "chance": 0.05 }
        }
    },
    'MINION_EXPANDER': {
        'display': 'Minion Expander',
        "prices": {},
        "upgrade": {
            'speed': 5, 'drop': 1,
            'special': { "type": "expand" }
        }
    },
    'FLINT_SHOVEL': {
        'display': 'Flint Shovel',  # not in bazaar (AH)
        "prices": { "custom": 61.25 },  # = two sticks from Lumber Merchant + 10 flint from Pat
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "replace", "list": { "GRAVEL": "FLINT" } }
        }
    },
    'FLYCATCHER_UPGRADE': {
        'display': 'Flycatcher',
        "prices": {},
        "upgrade": {
            'speed': 20, 'drop': 1,
            'special': { "type": "None" }
        }
    },
    'KRAMPUS_HELMET': {
        'display': 'Krampus Helmet',  # not in bazaar (AH)
        "prices": { "custom": 500000 },  # 2025-10-6, take this price when Jerry's Workshop is open
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "generate", "item": { "RED_GIFT": 1 }, "chance": 0.000045 }
        }
    },
    'LESSER_SOULFLOW_ENGINE': {
        'display': 'Lesser Soulflow Engine',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 0.5,
            'special': { "type": "timer", "item": { "RAW_SOULFLOW": 1 }, "cooldown": 180 }
        }
    },
    'SOULFLOW_ENGINE': {
        'display': 'Soulflow Engine',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 0.5,
            'special': { "type": "timer", "item": { "RAW_SOULFLOW": 1 }, "cooldown": 90 }
        }
    },
    'CORRUPT_SOIL': {
        'display': 'Corrupt Soil',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "add", "item": { "SULPHUR_ORE": 1, "CORRUPTED_FRAGMENT": 1 } }
        }
    },
    'BERBERIS_FUEL_INJECTOR': {
        'display': 'Berberis Fuel Injector',
        "prices": {},
        "upgrade": {
            'speed': 15, 'drop': 1,
            'special': { "type": "timer", "item": { "LUSH_BERBERIS": 1 }, "cooldown": 300 }
        }
    },
    'ENCHANTED_SHEARS': {
        'display': 'Enchanted Shears',  # not in bazaar (AH)
        "prices": { "custom": 1600 },  # = 320 iron from Iron Forger
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "add", "item": { "WOOL": 2 } }  # probably correct, not entirely sure
        }
    },
    'SLEEPY_HOLLOW': {
        'display': 'Sleepy Hollow',
        "prices": {},
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "generate", "item": { "PURPLE_CANDY": 1 }, "chance": 0.00015 }
        }
    },
    'INFERNO_FUEL_BLOCK': {
        'display': 'Inferno Fuel Block',
        "prices": { "custom": 65000 }
    },
    'HYPERGOLIC_GABAGOOL': {
        'display': 'Hypergolic Gabagool',
        "prices": { "custom": 5500000 }
    },
    'HEAVY_GABAGOOL': {
        'display': 'Heavy Gabagool',
        "prices": { "custom": 500000 }
    },
    'FUEL_GABAGOOL': {
        'display': 'Fuel Gabagool',
        "prices": { "custom": 20000 }
    },
    'MAGMA_CREAM_DISTILLATE': {
        'display': 'Magma Cream Distillate',
        "prices": { "custom": 5000 }
    },
    'BLAZE_ROD_DISTILLATE': {
        'display': 'Blaze Rod Distillate',
        "prices": { "custom": 5500 }
    },
    'NETHER_STALK_DISTILLATE': {
        'display': 'Nether Wart Distillate',
        "prices": { "custom": 5000 }
    },
    'GLOWSTONE_DUST_DISTILLATE': {
        'display': 'Glowstone Distillate',
        "prices": { "custom": 4900 }
    },
    'CRUDE_GABAGOOL_DISTILLATE': {
        'display': 'Gabagool Distillate',
        "prices": { "custom": 85000 }
    },
    'CAPSAICIN_EYEDROPS_NO_CHARGES': {
        'display': 'Capsaicin Eyedrops',
        "prices": { "custom": 1700000 }
    },
    "POWER_CRYSTAL": {
        'display': 'Power Crystal',
        "prices": { "custom": 600000 },
        'duration': 172800
    },
    "SCORCHED_POWER_CRYSTAL": {
        'display': 'Scorched Power Crystal',
        "prices": { "custom": 2000000 },
        'duration': 172800
    },
    "MITHRIL_INFUSION": {
        'display': "Mithril Infusion",
        "prices": { "custom": 6500000 }
    },
    "STARFALL": {
        'display': "Starfall",
        "prices": { "custom": 1500 }
    },
    "PLASMA": {
        'display': "Plasma",
        "prices": { "custom": 20000 }
    },
    "REVENANT_FLESH": {
        'display': "Revenant Flesh",
        "prices": { "custom": 20 }
    },
    "REVENANT_VISCERA": {
        'display': "Revenant Viscera",
        "prices": { "custom": 85000 }
    },
    "NULL_SPHERE": {
        'display': "Null Sphere",
        "prices": { "custom": 10 }
    },
    "NULL_OVOID": {
        'display': "Null Ovoid",
        "prices": { "custom": 120000 }
    },
    "DERELICT_ASHE": {
        'display': "Derelict Ashe",
        "prices": { "custom": 900 }
    },
    "MOLTEN_POWDER": {
        'display': "Molten Powder",
        "prices": { "custom": 250000 }
    },
    "TARANTULA_WEB": {
        'display': "Tarantula Web",
        "prices": { "custom": 350 }
    },
    "TARANTULA_SILK": {
        'display': "Tarantula Silk",
        "prices": { "custom": 250000 }
    },
    "FLAMES": {
        'display': "Flames",
        "prices": {}
    },
    "FREE_WILL": {
        'display': "Free Will",
        'prices': {}
    },
    "POTATO_TALISMAN": {
        'display': "Potato Talisman",  # not in bazaar (AH)
        'prices': { "custom": 45000000 }
    },
    "SMALL_ENCHANTED_CHEST": {
        'display': "Small Storage",
        'prices': {}
    },
    "MEDIUM_ENCHANTED_CHEST": {
        'display': "Medium Storage",
        'prices': {}
    },
    "LARGE_ENCHANTED_CHEST": {
        'display': "Large Storage",
        'prices': {}
    },
    "XLARGE_ENCHANTED_CHEST": {
        'display': "X-Large Storage",
        'prices': {}
    },
    "XXLARGE_ENCHANTED_CHEST": {
        'display': "XX-Large Storage",
        'prices': {}
    },
    "PRISMARINE:1": {
        'display': "Prismarine Bricks",
        'prices': { 'npc': 5 },
        'xp': { 'mining': 0 }
    },
    "HUNTER_KNIFE": {
        'display': "Hunter Knife",
        "prices": { "custom": 500000 },  # 500k from Rusty
        "upgrade": {
            'speed': 0, 'drop': 1,
            'special': { "type": "replace", "list": { "POTATO_ITEM": "FRENCH_FRIES" } }
        }
    },
    "FRENCH_FRIES": {
        'display': "French Fries",
        'prices': { "npc": 1 },
        'xp': { 'farming': 0 }
    },
    'PET_ITEM_MINING_SKILL_BOOST_COMMON': {
        'display': 'Common Mining Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_MINING_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Mining Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 250000 }
    },
    'PET_ITEM_MINING_SKILL_BOOST_RARE': {
        'display': 'Rare Mining Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 50000 }
    },
    'PET_ITEM_FARMING_SKILL_BOOST_COMMON': {
        'display': 'Common Farming Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_FARMING_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Farming Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 50000 }
    },
    'PET_ITEM_FARMING_SKILL_BOOST_RARE': {
        'display': 'Rare Farming Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 500000 }
    },
    'PET_ITEM_FARMING_SKILL_BOOST_EPIC': {
        'display': 'Epic Farming Exp Boost',  # not in bazaar (Duncan)
        'prices': { 'custom': 1500000 }
    },
    'PET_ITEM_FISHING_SKILL_BOOST_COMMON': {
        'display': 'Common Fishing Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_FISHING_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Fishing Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 47000 }
    },
    'PET_ITEM_FISHING_SKILL_BOOST_RARE': {
        'display': 'Rare Fishing Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 300000 }
    },
    'PET_ITEM_FISHING_SKILL_BOOST_EPIC': {
        'display': 'Epic Fishing Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 2500000 }  # 2025-10-6
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_COMMON': {
        'display': 'Common Combat Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_UNCOMMON': {
        'display': 'Uncommon Combat Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 200000 }
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_RARE': {
        'display': 'Rare Combat Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 2500000 }  # 2025-10-6
    },
    'PET_ITEM_COMBAT_SKILL_BOOST_EPIC': {
        'display': 'Epic Combat Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 9500000 }  # 2025-10-6
    },
    'PET_ITEM_FORAGING_SKILL_BOOST_COMMON': {
        'display': 'Common Foraging Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 60000 }
    },
    'PET_ITEM_FORAGING_SKILL_BOOST_EPIC': {
        'display': 'Epic Foraging Exp Boost',  # not in bazaar (AH)
        'prices': { 'custom': 6000000 }  # 2025-10-6
    },
    'PET_ITEM_ALL_SKILLS_BOOST_COMMON': {
        'display': 'All Skills Exp Boost',  # not in bazaar (Zog)
        'prices': { 'custom': 50000 }
    },
    'ALL_SKILLS_SUPER_BOOST': {
        'display': 'All Skills Exp Super-Boost',  # not in bazaar (AH)
        'prices': { 'custom': 5000000 }  # 2025-10-6
    },
    "PET_ITEM_EXP_SHARE_DROP": {
        "display": "Exp Share Core",
        "prices": {}
    },
    "SHARD_TOUCAN": {
        "display": "Toucan",
        "prices": {}
    },
    "SHARD_FALCON": {
        "display": "Falcon",
        "prices": {}
    },
    # The following items are on the Auction House, but can be created from items from the bazaar
    # If the custom price of an item here is set to 0, the equivalent price from bazaar will be calculated
    # Otherwise it will use the inputted number.
    'EVERBURNING_FLAME': {
        'display': 'Everburning Flame',  # not in bazaar (AH)
        "prices": { "custom": 0 },
        "upgrade": { 'speed': 40, 'drop': 1, 'duration': 0 }
    },
    # equivalent bazaar price: 1 Plasma Bucket, 16 Flames, 2 Enchanted Sulphur Cubes, 2 Enchanted Red Sand Cubes
    "POSTCARD": {
        'display': "Postcard",  # not in bazaar (AH)
        'prices': { "custom": 0 }
    },
    # equivalent bazaar price: taken from Auction House through https://sky.coflnet.com/data
    "PET_ITEM_EXP_SHARE": {
        'display': "Exp Share",
        'prices': { "custom": 0 }
    },
    # equivalent bazaar price: Exp Share price = Exp Share Core price + 72 * Enchanted Gold price
}

#%% Inferno minion List

infernofuel_data = {
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

#%% Option lists with display to ID translator

getID = {
    'Hypergolic Gabagool': 'HYPERGOLIC_GABAGOOL',
    'Heavy Gabagool': 'HEAVY_GABAGOOL',
    'Fuel Gabagool': 'FUEL_GABAGOOL',
    'Magma Cream Distillate': 'MAGMA_CREAM_DISTILLATE',
    'Blaze Rod Distillate': 'BLAZE_ROD_DISTILLATE',
    'Nether Wart Distillate': 'NETHER_STALK_DISTILLATE',
    'Glowstone Distillate': 'GLOWSTONE_DUST_DISTILLATE',
    'Gabagool Distillate': 'CRUDE_GABAGOOL_DISTILLATE',
    'Capsaicin Eyedrops': 'CAPSAICIN_EYEDROPS_NO_CHARGES',
    "Budget Hopper": "BUDGET_HOPPER",
    "Enchanted Hopper": "ENCHANTED_HOPPER",
    'Oak Log': 'LOG',
    'Spruce Log': 'LOG:1',
    'Birch Log': 'LOG:2',
    'Dark Oak Log': 'LOG_2:1',
    'Acacia Log': 'LOG_2',
    'Jungle Log': 'LOG:3',
    'Small': "SMALL_ENCHANTED_CHEST",
    'Medium': "MEDIUM_ENCHANTED_CHEST",
    'Large': "LARGE_ENCHANTED_CHEST",
    'X-Large': "XLARGE_ENCHANTED_CHEST",
    'XX-Large': "XXLARGE_ENCHANTED_CHEST",
    'Common Mining Exp Boost': 'PET_ITEM_MINING_SKILL_BOOST_COMMON',
    'Uncommon Mining Exp Boost': 'PET_ITEM_MINING_SKILL_BOOST_UNCOMMON',
    'Rare Mining Exp Boost': 'PET_ITEM_MINING_SKILL_BOOST_RARE',
    'Common Farming Exp Boost': 'PET_ITEM_FARMING_SKILL_BOOST_COMMON',
    'Uncommon Farming Exp Boost': 'PET_ITEM_FARMING_SKILL_BOOST_UNCOMMON',
    'Rare Farming Exp Boost': 'PET_ITEM_FARMING_SKILL_BOOST_RARE',
    'Epic Farming Exp Boost': 'PET_ITEM_FARMING_SKILL_BOOST_EPIC',
    'Common Fishing Exp Boost': 'PET_ITEM_FISHING_SKILL_BOOST_COMMON',
    'Uncommon Fishing Exp Boost': 'PET_ITEM_FISHING_SKILL_BOOST_UNCOMMON',
    'Rare Fishing Exp Boost': 'PET_ITEM_FISHING_SKILL_BOOST_RARE',
    'Epic Fishing Exp Boost': 'PET_ITEM_FISHING_SKILL_BOOST_EPIC',
    'Common Combat Exp Boost': 'PET_ITEM_COMBAT_SKILL_BOOST_COMMON',
    'Uncommon Combat Exp Boost': 'PET_ITEM_COMBAT_SKILL_BOOST_UNCOMMON',
    'Rare Combat Exp Boost': 'PET_ITEM_COMBAT_SKILL_BOOST_RARE',
    'Epic Combat Exp Boost': 'PET_ITEM_COMBAT_SKILL_BOOST_EPIC',
    'Common Foraging Exp Boost': 'PET_ITEM_FORAGING_SKILL_BOOST_COMMON',
    'Epic Foraging Exp Boost': 'PET_ITEM_FORAGING_SKILL_BOOST_EPIC',
    'All Skills Exp Boost': 'PET_ITEM_ALL_SKILLS_BOOST_COMMON',
    'All Skills Exp Super-Boost': 'ALL_SKILLS_SUPER_BOOST',
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
    "Inferno Minion Fuel": "INFERNO_FUEL"
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

#%% Compactor List


compactorList = {
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

#%% Enchanter List (Super Compactor 3000 and Dwarven Super Compactor)


enchanterList = {
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
    'POTATO_ITEM': { 'makes': 'ENCHANTED_POTATO', 'per': 160 },
    'ENCHANTED_POTATO': { 'makes': 'ENCHANTED_BAKED_POTATO', 'per': 160 },
    'RED_MUSHROOM': { 'makes': 'ENCHANTED_RED_MUSHROOM', 'per': 160 },
    'BROWN_MUSHROOM': { 'makes': 'ENCHANTED_BROWN_MUSHROOM', 'per': 160 },
    'HUGE_MUSHROOM_2': { 'makes': 'ENCHANTED_RED_MUSHROOM', 'amount': 9, 'per': 160 },
    'HUGE_MUSHROOM_1': { 'makes': 'ENCHANTED_BROWN_MUSHROOM', 'amount': 9, 'per': 160 },
    'ENCHANTED_RED_MUSHROOM': { 'makes': 'ENCHANTED_HUGE_MUSHROOM_2', 'per': 32 },
    'ENCHANTED_BROWN_MUSHROOM': { 'makes': 'ENCHANTED_HUGE_MUSHROOM_1', 'per': 32 },
    'INK_SACK:2': { 'makes': 'ENCHANTED_CACTUS_GREEN', 'per': 160 },
    'ENCHANTED_CACTUS_GREEN': { 'makes': 'ENCHANTED_CACTUS', 'per': 160 },
    'INK_SACK:3': { 'makes': 'ENCHANTED_COCOA', 'per': 160 },
    'SUGAR_CANE': { 'makes': 'ENCHANTED_SUGAR', 'per': 160 },
    'ENCHANTED_SUGAR': { 'makes': 'ENCHANTED_SUGAR_CANE', 'per': 160 },
    'NETHER_STALK': { 'makes': 'ENCHANTED_NETHER_STALK', 'per': 160 },
    'ENCHANTED_NETHER_STALK': { 'makes': 'MUTANT_NETHER_STALK', 'per': 160 },
    'YELLOW_FLOWER': { 'makes': 'ENCHANTED_DANDELION', 'per': 160 },
    'RED_ROSE': { 'makes': 'ENCHANTED_POPPY', 'per': 576 },
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


#%% pet xp boost items
# perhaps merge with their entries in itemList?

pet_xp_boosts = {
    "None": ["all", 0],
    'Common Mining Exp Boost': ['mining', 20],
    'Uncommon Mining Exp Boost': ['mining', 30],
    'Rare Mining Exp Boost': ['mining', 40],
    'Common Farming Exp Boost': ['farming', 20],
    'Uncommon Farming Exp Boost': ['farming', 30],
    'Rare Farming Exp Boost': ['farming', 40],
    'Epic Farming Exp Boost': ['farming', 50],
    'Common Fishing Exp Boost': ['fishing', 20],
    'Uncommon Fishing Exp Boost': ['fishing', 30],
    'Rare Fishing Exp Boost': ['fishing', 40],
    'Epic Fishing Exp Boost': ['fishing', 50],
    'Common Combat Exp Boost': ['combat', 20],
    'Uncommon Combat Exp Boost': ['combat', 30],
    'Rare Combat Exp Boost': ['combat', 40],
    'Epic Combat Exp Boost': ['combat', 50],
    'Common Foraging Exp Boost': ['foraging', 20],
    'Epic Foraging Exp Boost': ['foraging', 50],
    'All Skills Exp Boost': ['all', 10],
    'All Skills Exp Super-Boost': ['all', 20],
}

#%% Floating Crystals

floating_crystals = {
    "None": { 0: [] },
    "Farm Crystal": { 10: ['Wheat', 'Melon', 'Pumpkin', 'Carrot', 'Potato', 'Cactus', 'Cocoa Beans', 'Sugar Cane', 'Mushroom', 'Nether Wart'] },
    "Woodcutting Crystal": { 10: ['Oak', 'Spruce', 'Birch', 'Dark Oak', 'Acacia', 'Jungle', "Flower"] },  # flower minion is correct
    "Mithril Crystal": { 10: ['Cobblestone', 'Obsidian', 'Glowstone', 'Gravel', 'Sand', 'Red Sand', 'Mycelium', 'Ice', 'Snow', 'Coal', 'Iron', 'Gold', 'Diamond', 'Lapis', 'Redstone', 'Emerald', 'Quartz', 'End Stone', 'Mithril', 'Hard Stone'] },
    "Winter Crystal": { 5: ["Snow", "Ice"] },
    "Winter + Mithril Crystal": { 15: ["Snow", "Ice"] }  # correct
}

#%% Minion Storage

minion_chests = { "None": 0, "Small": 3, "Medium": 9, "Large": 15, "X-Large": 21, "XX-Large": 27 }

standard_storage = { 1: 1, 2: 3, 3: 3, 4: 6, 5: 6, 6: 9, 7: 9, 8: 12, 9: 12, 10: 15, 11: 15, 12: 15 }


#%% Hoppers

hopper_data = {
    "None": 1,
    "Budget Hopper": 0.5,
    "Enchanted Hopper": 0.9,
}

#%% Mayors

affected_by_cole = ['Cobblestone', 'Obsidian', 'Glowstone', 'Gravel', 'Sand', 'Ice', 'Coal', 'Iron', 'Gold', 'Diamond', 'Lapis', 'Redstone', 'Emerald', 'Quartz', 'End Stone', 'Mithril']

#%% Minion boosting pets

# name pet: {valid rarities: [boost base, added boost per level], "affects": [affected minions]}
boost_pets = {
    "None": { "affects": [] },
    # "Chicken": {"Legendary": [0, 0.3], "affects": ["Chicken"]},  # reworked in skyblock 0.23.1
    "Magma Cube": {
        "Common": [0, 0.2], "Uncommon": [0, 0.25],
        "Rare": [0, 0.25], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affects": ["Slime", "Magma Cube"]  # affects magma cube minion is correct
    },
    "Mooshroom Cow": {
        "Common": [0, 0.2], "Uncommon": [0, 0.2],
        "Rare": [0, 0.3], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affects": ["Mushroom", "Mycelium"]
    },
    "Ocelot": {
        "Rare": [0, 0.3], "Epic": [0, 0.3], "Legendary": [0, 0.3],
        "affects": ['Oak', 'Spruce', 'Birch', 'Dark Oak', 'Acacia', 'Jungle', "Flower"]  # yes flower minion correct
    },
    "Pigman": {
        "Common": [0, 0.1], "Uncommon": [0, 0.2],
        "Rare": [0, 0.2], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affects": ["Pig"]
    },
    "Rabbit": {
        "Legendary": [0, 0.3], "Mythic": [0, 0.3],
        "affects": ['Wheat', 'Melon', 'Pumpkin', 'Carrot', 'Potato', 'Cactus', 'Cocoa Beans', 'Sugar Cane', 'Mushroom', 'Nether Wart']
    },
    "Snail": {
        "Common": [0, 0.1], "Uncommon": [0, 0.2],
        "Rare": [0, 0.2], "Epic": [0, 0.3],
        "Legendary": [0, 0.3], "affects": ["Red Sand"]
    },
    "Spider": {
        "Legendary": [0, 0.3], "Mythic": [0, 0.3],
        "affects": ["Spider", "Tarantula", "Cave Spider"]
    }
}


#%% Attribute shards

attribute_shards = {
    "Common": { 1: 1, 2: 4, 3: 9, 4: 15, 5: 22, 6: 30, 7: 40, 8: 54, 9: 72, 10: 96 },
    "Uncommon": { 1: 1, 2: 3, 3: 6, 4: 10, 5: 15, 6: 21, 7: 28, 8: 36, 9: 48, 10: 64 },
    "Rare": { 1: 1, 2: 3, 3: 6, 4: 9, 5: 13, 6: 17, 7: 22, 8: 28, 9: 36, 10: 48 },
    "Epic": { 1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 16, 8: 20, 9: 25, 10: 32 },
    "Legendary": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 9, 7: 12, 8: 15, 9: 19, 10: 24 }
}


#%% Pets

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
    'Rabbit': { 'type': 'farming', 'rarity': 'Legendary' },
    'Rat': { 'type': 'combat', 'rarity': 'Legendary' },
    'Reindeer': { 'type': 'fishing', 'rarity': 'Legendary' },
    'Rift Ferret': { 'type': 'combat', 'rarity': 'Epic' },
    'Rock': { 'type': 'mining', 'rarity': 'Legendary' },
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

max_lvl_pet_xp_amounts = { "Common": 5624785, "Uncommon": 8644220, "Rare": 12626665, "Epic": 18608500, "Legendary": 25353230, "Dragon": 210255385 }

#%% Minion List:
# average drop amount from hypixel skyblock fandom wiki or self tested

minionList = {
    "Custom": {
        "drops": {
            "CUSTOM": 1
        },
        "speed": {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            11: 11,
            12: 12
        },
        "afkcorrupt": 2,
        "notes": { "Custom": "Custom Minion does not exist", "AFK": "multiple corrupt drops" }
    },
    "Cobblestone": {
        "drops": { "COBBLESTONE": 1 },
        "speed": { 1: 14, 2: 14, 3: 12, 4: 12, 5: 10, 6: 10, 7: 9, 8: 9, 9: 8, 10: 8, 11: 7, 12: 6 },
        "notes": { "Special Layout": "only harvests (cobble generator)" }
    },
    "Obsidian": {
        "drops": { "OBSIDIAN": 1 },
        "speed": { 1: 45, 2: 45, 3: 42, 4: 42, 5: 39, 6: 39, 7: 35, 8: 35, 9: 30, 10: 30, 11: 24, 12: 21 }
    },
    "Glowstone": {
        "drops": { "GLOWSTONE_DUST": 3 },
        "speed": { 1: 25, 2: 25, 3: 23, 4: 23, 5: 21, 6: 21, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13, 12: 11 }
    },
    "Gravel": {
        "drops": { "GRAVEL": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "notes": { "Special Layout": "only spawn (gravity blocks)" }
    },
    "Sand": {
        "drops": { "SAND": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13 },
        "notes": { "Special Layout": "only spawn (gravity blocks)" }
    },
    "Red Sand": {
        "drops": { "SAND:1": 1 },
        "speed": { 1: 26, 2: 25, 3: 24, 4: 23, 5: 22, 6: 21, 7: 20, 8: 19, 9: 18, 10: 16, 11: 13, 12: 11 },
        "storage": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15 },
        "notes": { "Special Layout": "only spawn (gravity blocks)" }
    },
    "Mycelium": {
        "drops": { "MYCEL": 1 },
        "speed": { 1: 26, 2: 25, 3: 24, 4: 23, 5: 22, 6: 21, 7: 20, 8: 19, 9: 18, 10: 16, 11: 13, 12: 11 },
        "storage": { 1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 12, 10: 14, 11: 15, 12: 15 },
        "notes": { "Special Layout": "only harvests (natural spreading)" }
    },
    "Clay": {
        "drops": { "CLAY_BALL": 4 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 27.5, 6: 27.5, 7: 24, 8: 24, 9: 20, 10: 20, 11: 16, 12: 14 }
    },
    "Ice": {
        "drops": { "ICE": 1 },
        "speed": { 1: 14, 2: 14, 3: 12, 4: 12, 5: 10, 6: 10, 7: 9, 8: 9, 9: 8, 10: 8, 11: 7, 12: 6 },
        "notes": { "Special Layout": "only harvests (frozen biome)" }
    },
    "Snow": {
        "drops": { "SNOW_BALL": 4 },
        "speed": { 1: 13, 2: 13, 3: 12, 4: 12, 5: 11, 6: 11, 7: 9.5, 8: 9.5, 9: 8, 10: 8, 11: 6.5, 12: 5.8 }
    },
    "Coal": {
        "drops": { "COAL": 1 },
        "speed": { 1: 15, 2: 15, 3: 13, 4: 13, 5: 12, 6: 12, 7: 10, 8: 10, 9: 9, 10: 9, 11: 7, 12: 6 }
    },
    "Iron": {
        "drops": { "IRON_ORE": 1 },
        "speed": { 1: 17, 2: 17, 3: 15, 4: 15, 5: 14, 6: 14, 7: 12, 8: 12, 9: 10, 10: 10, 11: 8, 12: 7 }
    },
    "Gold": {
        "drops": { "GOLD_ORE": 1 },
        "speed": { 1: 22, 2: 22, 3: 20, 4: 20, 5: 18, 6: 18, 7: 16, 8: 16, 9: 14, 10: 14, 11: 11, 12: 9 }
    },
    "Diamond": {
        "drops": { "DIAMOND": 1 },
        "speed": { 1: 29, 2: 29, 3: 27, 4: 27, 5: 25, 6: 25, 7: 22, 8: 22, 9: 19, 10: 19, 11: 15, 12: 12 }
    },
    "Lapis": {
        "drops": { "INK_SACK:4": 6 },  # correct
        "speed": { 1: 29, 2: 29, 3: 27, 4: 27, 5: 25, 6: 25, 7: 23, 8: 23, 9: 21, 10: 21, 11: 18, 12: 16 }
    },
    "Redstone": {
        "drops": { "REDSTONE": 4.5 },
        "speed": { 1: 29, 2: 29, 3: 27, 4: 27, 5: 25, 6: 25, 7: 23, 8: 23, 9: 21, 10: 21, 11: 18, 12: 16 }
    },
    "Emerald": {
        "drops": { "EMERALD": 1 },
        "speed": { 1: 28, 2: 28, 3: 26, 4: 26, 5: 24, 6: 24, 7: 21, 8: 21, 9: 18, 10: 18, 11: 14, 12: 12 }
    },
    "Quartz": {
        "drops": { "QUARTZ": 1 },
        "speed": { 1: 22.5, 2: 22.5, 3: 21, 4: 21, 5: 19, 6: 19, 7: 17, 8: 17, 9: 14.5, 10: 14.5, 11: 11.5, 12: 10 }
    },
    "End Stone": {
        "drops": { "ENDER_STONE": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 13 }
    },
    "Mithril": {
        "drops": { "MITHRIL_ORE": 2 },
        "speed": { 1: 80, 2: 80, 3: 75, 4: 75, 5: 70, 6: 70, 7: 65, 8: 65, 9: 60, 10: 60, 11: 55, 12: 50 }
    },
    "Hard Stone": {
        "drops": { "HARD_STONE": 2 },  # correct
        "speed": { 1: 14, 2: 14, 3: 12, 4: 12, 5: 10, 6: 10, 7: 9, 8: 9, 9: 8, 10: 8, 11: 7, 12: 6 }
    },
    "Wheat": {
        "drops": { "WHEAT": 1, "SEEDS": 1.5 },  # correct
        "speed": { 1: 15, 2: 15, 3: 13, 4: 13, 5: 11, 6: 11, 7: 10, 8: 10, 9: 9, 10: 9, 11: 8, 12: 7 },
        "storage": { 1: 2, 2: 4, 3: 4 },
        "notes": { "AFK": "can skip planting with Wheat Crystal (not 100% of the time, depends on minion speed)" }
    },
    "Melon": {
        "drops": { "MELON": 5 },
        "speed": { 1: 24, 2: 24, 3: 22.5, 4: 22.5, 5: 21, 6: 21, 7: 18.5, 8: 18.5, 9: 16, 10: 16, 11: 13, 12: 10 },
        "notes": { "AFK": "only harvests" }
    },
    "Pumpkin": {
        "drops": { "PUMPKIN": 1 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 27, 6: 27, 7: 24, 8: 24, 9: 20, 10: 20, 11: 16, 12: 12 },
        "notes": { "AFK": "only harvests" }
    },
    "Carrot": {
        "drops": { "CARROT_ITEM": 3 },
        "speed": { 1: 20, 2: 20, 3: 18, 4: 18, 5: 16, 6: 16, 7: 14, 8: 14, 9: 12, 10: 12, 11: 10, 12: 8 }
    },
    "Potato": {
        "drops": { "POTATO_ITEM": 3 },
        "speed": { 1: 20, 2: 20, 3: 18, 4: 18, 5: 16, 6: 16, 7: 14, 8: 14, 9: 12, 10: 12, 11: 10, 12: 8 }
    },
    "Mushroom": {
        "drops": { "RED_MUSHROOM": 0.5, "BROWN_MUSHROOM": 0.5 },
        "speed": { 1: 30, 2: 30, 3: 28, 4: 28, 5: 26, 6: 26, 7: 23, 8: 23, 9: 20, 10: 20, 11: 16, 12: 12 },
        "storage": { 1: 2, 2: 4, 3: 4 }
    },
    "Cactus": {
        "drops": { "CACTUS": 3 },
        "speed": { 1: 27, 2: 27, 3: 25, 4: 25, 5: 23, 6: 23, 7: 21, 8: 21, 9: 18, 10: 18, 11: 15, 12: 12 }
    },
    "Cocoa Beans": {
        "drops": { "INK_SACK:3": 3 },
        "speed": { 1: 27, 2: 27, 3: 25, 4: 25, 5: 23, 6: 23, 7: 21, 8: 21, 9: 18, 10: 18, 11: 15, 12: 12 }
    },
    "Sugar Cane": {
        "drops": { "SUGAR_CANE": 3 },
        "speed": { 1: 22, 2: 22, 3: 20, 4: 20, 5: 18, 6: 18, 7: 16, 8: 16, 9: 14.5, 10: 14.5, 11: 12, 12: 9 }
    },
    "Nether Wart": {
        "drops": { "NETHER_STALK": 3 },
        "speed": { 1: 50, 2: 50, 3: 47, 4: 47, 5: 44, 6: 44, 7: 41, 8: 41, 9: 38, 10: 38, 11: 32, 12: 27 }
    },
    "Flower": {
        "drops": { "YELLOW_FLOWER": 1 / 14, "RED_ROSE": 1 / 14, "SMALL_FLOWER": 8 / 14, "LARGE_FLOWER": 4 / 14 },
        "speed": { 1: 30, 2: 29, 3: 28, 4: 27, 5: 26, 6: 25, 7: 24, 8: 23, 9: 22, 10: 20, 11: 18, 12: 15 },
        "storage": { 1: 15, 2: 15, 3: 15, 4: 15, 5: 15, 6: 15, 7: 15, 8: 15, 9: 15, 10: 15, 11: 15, 12: 15 },
        "notes": { "Special Layout": "only spawn, no large flowers (water flushing, low roof)" }
    },
    "Fishing": {
        "drops": { "RAW_FISH": 0.5, "RAW_FISH:1": 0.25, "RAW_FISH:3": 0.12, "RAW_FISH:2": 0.04, "PRISMARINE_CRYSTALS": 0.03, "PRISMARINE_SHARD": 0.03, "SPONGE": 0.03 },
        "speed": { 1: 75, 2: 75, 3: 67, 4: 67, 5: 59, 6: 59, 7: 51, 8: 51, 9: 43, 10: 43, 11: 35, 12: 30 },
        "storage": { 1: 10, 2: 10, 3: 10, 4: 11, 5: 11, 6: 12, 7: 12, 8: 13, 9: 13, 10: 14, 11: 15 },
        "notes": { "Always": "only harvests" }
    },
    "Zombie": {
        "drops": { "ROTTEN_FLESH": 1, "CARROT_ITEM": 0.01, "POTATO_ITEM": 0.01, "POISONOUS_POTATO": 0.02 },  # correct
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 }
    },
    "Revenant": {
        "drops": { "ROTTEN_FLESH": 3.16, "DIAMOND": 0.2 },
        "speed": { 1: 29, 2: 29, 3: 26, 4: 26, 5: 23, 6: 23, 7: 19, 8: 19, 9: 14.5, 10: 14.5, 11: 10, 12: 8 },
        "afkcorrupt": 1.83,
        "notes": { "AFK": "multiple corrupt drops" }
    },
    "Voidling": {
        "drops": { "OBSIDIAN": 2.5, "QUARTZ": 0.4, "ENCHANTED_ENDER_PEARL": 0.000625 },
        "speed": { 1: 45, 2: 45, 3: 42, 4: 42, 5: 39, 6: 39, 7: 35, 8: 35, 9: 30, 10: 30, 11: 24 },
        "afkcorrupt": 1.5,
        "notes": { "AFK": "multiple corrupt drops" }
    },
    "Inferno": {
        "drops": { "CRUDE_GABAGOOL": 1 },
        "speed": { 1: 1013, 2: 982, 3: 950, 4: 919, 5: 886, 6: 855, 7: 823, 8: 792, 9: 760, 10: 728, 11: 697 },
        "afkcorrupt": 0,
        "notes": { "Inferno": "can use inferno fuel", "AFK": "no corrupt drops" }
    },
    "Vampire": {
        "drops": { "HEMOVIBE": 1 },
        "speed": { 1: 190, 2: 190, 3: 175, 4: 175, 5: 160, 6: 160, 7: 140, 8: 140, 9: 117, 10: 117, 11: 95 }
    },
    "Skeleton": {
        "drops": { "BONE": 1.5 },  # correct
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "afkcorrupt": 1.5,
        "notes": { "AFK": "multiple corrupt drops" }
    },
    "Creeper": {
        "drops": { "SULPHUR": 1 },
        "speed": { 1: 27, 2: 27, 3: 25, 4: 25, 5: 23, 6: 23, 7: 21, 8: 21, 9: 18, 10: 18, 11: 14 }
    },
    "Spider": {
        "drops": { "STRING": 1, "SPIDER_EYE": 0.5 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "storage": { 1: 2, 2: 4, 3: 4 }
    },
    "Tarantula": {
        "drops": { "STRING": 3.16, "SPIDER_EYE": 1, "IRON_INGOT": 0.2 },
        "speed": { 1: 29, 2: 29, 3: 26, 4: 26, 5: 23, 6: 23, 7: 19, 8: 19, 9: 14.5, 10: 14.5, 11: 10, 12: 8 },
        "afkcorrupt": 1.83,
        "notes": { "AFK": "multiple corrupt drops" }
    },
    "Cave Spider": {
        "drops": { "STRING": 0.5, "SPIDER_EYE": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13 },
        "storage": { 1: 2, 2: 4, 3: 4 }
    },
    "Blaze": {
        "drops": { "BLAZE_ROD": 1 },
        "speed": { 1: 33, 2: 33, 3: 31, 4: 31, 5: 28.5, 6: 28.5, 7: 25, 8: 25, 9: 21, 10: 21, 11: 16.5, 12: 15 }
    },
    "Magma Cube": {
        "drops": { "MAGMA_CREAM": 2 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 28, 6: 28, 7: 25, 8: 25, 9: 22, 10: 22, 11: 18, 12: 16 },
        "afkcorrupt": 2,
        "notes": { "AFK": "multiple corrupt drops" }
    },
    "Enderman": {
        "drops": { "ENDER_PEARL": 1 },
        "speed": { 1: 32, 2: 32, 3: 30, 4: 30, 5: 28, 6: 28, 7: 25, 8: 25, 9: 22, 10: 22, 11: 18 }
    },
    "Ghast": {
        "drops": { "GHAST_TEAR": 1 },
        "speed": { 1: 50, 2: 50, 3: 47, 4: 47, 5: 44, 6: 44, 7: 41, 8: 41, 9: 38, 10: 38, 11: 32, 12: 30 }
    },
    "Slime": {
        "drops": { "SLIME_BALL": 2 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 19, 8: 19, 9: 16, 10: 16, 11: 12 },
        "afkcorrupt": 2,
        "notes": { "AFK": "multiple corrupt drops" }
    },
    "Cow": {
        "drops": { "RAW_BEEF": 1, "LEATHER": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13, 12: 10 },
        "storage": { 1: 2, 2: 4, 3: 4 }
    },
    "Pig": {
        "drops": { "PORK": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13, 12: 10 }
    },
    "Chicken": {
        "drops": { "RAW_CHICKEN": 1, "FEATHER": 1 },
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 18, 10: 18, 11: 15, 12: 12 },
        "storage": { 1: 3, 2: 5, 3: 5, 4: 7, 5: 7 }
    },
    "Sheep": {
        "drops": { "MUTTON": 1, "WOOL": 1 },
        "speed": { 1: 24, 2: 24, 3: 22, 4: 22, 5: 20, 6: 20, 7: 18, 8: 18, 9: 16, 10: 16, 11: 12, 12: 9 },
        "storage": { 1: 2, 2: 4, 3: 4 }
    },
    "Rabbit": {
        "drops": { "RABBIT": 1, "RABBIT_FOOT": 0.7, "RABBIT_HIDE": 0.7 },  # correct
        "speed": { 1: 26, 2: 26, 3: 24, 4: 24, 5: 22, 6: 22, 7: 20, 8: 20, 9: 17, 10: 17, 11: 13, 12: 10 },
        "storage": { 1: 3, 2: 5, 3: 5, 4: 7, 5: 7 }
    },
    "Oak": {
        "drops": { "LOG": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" }
    },
    "Spruce": {
        "drops": { "LOG:1": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" }
    },
    "Birch": {
        "drops": { "LOG:2": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" }
    },
    "Dark Oak": {
        "drops": { "LOG_2:1": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" }
    },
    "Acacia": {
        "drops": { "LOG_2": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" }
    },
    "Jungle": {
        "drops": { "LOG:3": 3 },
        "speed": { 1: 48, 2: 48, 3: 45, 4: 45, 5: 42, 6: 42, 7: 38, 8: 38, 9: 33, 10: 33, 11: 27 },
        "notes": { "AFK": "+1 wood drop" }
    }
}

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
    tier_loop = np.arange(final_tier) + 1
    for tier in tier_loop:
        for item, amount in minionCosts[minion_type][tier].items():
            if item not in final_cost:
                final_cost[item] = 0
            final_cost[item] += amount
    return deepcopy(final_cost)

#%% Minion Costs


minionCosts = {
    "Custom": minionCostTypes(["CUSTOM", "ENCHANTED_CUSTOM"], "single enchanted", True),
    "Cobblestone": minionCostTypes(["COBBLESTONE", "ENCHANTED_COBBLESTONE"], "single enchanted", True),
    "Obsidian": minionCostTypes(["OBSIDIAN", "ENCHANTED_OBSIDIAN"], "single enchanted", True),
    "Glowstone": minionCostTypes(["GLOWSTONE_DUST", "ENCHANTED_GLOWSTONE_DUST", "ENCHANTED_GLOWSTONE"], "expensive enchanted", True),
    "Gravel": minionCostTypes(["GRAVEL", "ENCHANTED_FLINT"], "single enchanted", False),
    "Sand": minionCostTypes(["SAND", "ENCHANTED_SAND"], "single enchanted", False),
    "Red Sand": minionCostTypes(["SAND:1", "ENCHANTED_RED_SAND", "ENCHANTED_RED_SAND_CUBE"], "expensive enchanted", True, {1: {'SAND:1': 80}, 4: {'ENCHANTED_RED_SAND': 16}, 5: {'ENCHANTED_RED_SAND': 32}}),
    "Mycelium": minionCostTypes(["MYCEL", "ENCHANTED_MYCELIUM", "ENCHANTED_MYCELIUM_CUBE"], "expensive enchanted", True, {1: {'MYCEL': 80}, 4: {'ENCHANTED_MYCELIUM': 16}, 5: {'ENCHANTED_MYCELIUM': 32}}),
    "Clay": minionCostTypes(["CLAY_BALL", "ENCHANTED_CLAY_BALL"], "single enchanted", True, {12: {"ENCHANTED_CLAY_BLOCK": 8}}),
    "Ice": {1: {"ICE": 80}, 2: {"ICE": 160}, 3: {"ICE": 320}, 4: {"ICE": 512}, 5: {"PACKED_ICE": 128}, 6: {"PACKED_ICE": 256}, 7: {"PACKED_ICE": 512}, 8: {"ENCHANTED_ICE": 64}, 9: {"ENCHANTED_ICE": 128}, 10: {"ENCHANTED_ICE": 256}, 11: {"ENCHANTED_ICE": 512}, 12: {"ENCHANTED_ICE": 1024}},
    "Snow": {1: {}, 2: {"SNOW_BLOCK": 32}, 3: {"SNOW_BLOCK": 64}, 4: {"SNOW_BLOCK": 128}, 5: {"SNOW_BLOCK": 256}, 6: {"SNOW_BLOCK": 512}, 7: {"ENCHANTED_SNOW_BLOCK": 8}, 8: {"ENCHANTED_SNOW_BLOCK": 16}, 9: {"ENCHANTED_SNOW_BLOCK": 32}, 10: {"ENCHANTED_SNOW_BLOCK": 64}, 11: {"ENCHANTED_SNOW_BLOCK": 128}, 12: {"ENCHANTED_SNOW_BLOCK": 1024}},
    "Coal": minionCostTypes(["COAL", "ENCHANTED_COAL", "ENCHANTED_COAL_BLOCK"], "double enchanted", True),
    "Iron": minionCostTypes(["IRON_INGOT", "ENCHANTED_IRON", "ENCHANTED_IRON_BLOCK"], "double enchanted", True),
    "Gold": minionCostTypes(["GOLD_INGOT", "ENCHANTED_GOLD", "ENCHANTED_GOLD_BLOCK"], "double enchanted", True),
    "Diamond": minionCostTypes(["DIAMOND", "ENCHANTED_DIAMOND", "ENCHANTED_DIAMOND_BLOCK"], "double enchanted", True),
    "Lapis": minionCostTypes(["INK_SACK:4", "ENCHANTED_LAPIS_LAZULI", "ENCHANTED_LAPIS_LAZULI_BLOCK"], "very expensive enchanted", True),
    "Redstone": minionCostTypes(["REDSTONE", "ENCHANTED_REDSTONE", "ENCHANTED_REDSTONE_BLOCK"], "expensive enchanted", True),
    "Emerald": minionCostTypes(["EMERALD", "ENCHANTED_EMERALD", "ENCHANTED_EMERALD_BLOCK"], "double enchanted", True),
    "Quartz": minionCostTypes(["QUARTZ", "ENCHANTED_QUARTZ", "ENCHANTED_QUARTZ_BLOCK"], "double enchanted", True),
    "End Stone": minionCostTypes(["ENDER_STONE", "ENCHANTED_ENDSTONE"], "single enchanted", False),
    "Mithril": minionCostTypes(["MITHRIL_ORE", "ENCHANTED_MITHRIL", "REFINED_MITHRIL"], "double enchanted", True),
    "Hard Stone": minionCostTypes(["HARD_STONE", "ENCHANTED_HARD_STONE", "CONCENTRATED_STONE"], "expensive enchanted", True, {1: {'HARD_STONE': 256}, 2: {'HARD_STONE': 512}, 3: {'ENCHANTED_HARD_STONE': 8}, 4: {'ENCHANTED_HARD_STONE': 16}, 5: {'ENCHANTED_HARD_STONE': 32}, 10: {"CONCENTRATED_STONE": 4}, 11: {"CONCENTRATED_STONE": 8}, 12: {"CONCENTRATED_STONE": 16}}),
    "Wheat": minionCostTypes(["WHEAT", "ENCHANTED_WHEAT"], "single enchanted", True),
    "Melon": {1: {"MELON": 256}, 2: {"MELON": 512}, 3: {"MELON_BLOCK": 128}, 4: {"MELON_BLOCK": 256}, 5: {"MELON_BLOCK": 512}, 6: {"ENCHANTED_MELON": 64}, 7: {"ENCHANTED_MELON": 128}, 8: {"ENCHANTED_MELON": 256}, 9: {"ENCHANTED_MELON": 512}, 10: {"ENCHANTED_MELON_BLOCK": 8}, 11: {"ENCHANTED_MELON_BLOCK": 16}, 12: {"ENCHANTED_MELON_BLOCK": 32}},
    "Pumpkin": minionCostTypes(["PUMPKIN", "ENCHANTED_PUMPKIN"], "single enchanted", True),
    "Carrot": minionCostTypes(["CARROT_ITEM", "ENCHANTED_CARROT", "ENCHANTED_GOLDEN_CARROT"], "expensive enchanted", True),
    "Potato": minionCostTypes(["POTATO_ITEM", "ENCHANTED_POTATO", "ENCHANTED_BAKED_POTATO"], "expensive enchanted", True),
    "Mushroom": minionCostTypes(["RED_MUSHROOM", "ENCHANTED_RED_MUSHROOM"], "single enchanted", True, {12: {"ENCHANTED_RED_MUSHROOM": 512, "ENCHANTED_BROWN_MUSHROOM": 512}}),
    "Cactus": minionCostTypes(["CACTUS", "ENCHANTED_CACTUS_GREEN", "ENCHANTED_CACTUS"], "expensive enchanted", True),
    "Cocoa Beans": minionCostTypes(["INK_SACK:3", "ENCHANTED_COCOA", "ENCHANTED_COOKIE"], "double enchanted", True),
    "Sugar Cane": minionCostTypes(["SUGAR_CANE", "ENCHANTED_SUGAR", "ENCHANTED_SUGAR_CANE"], "expensive enchanted", True),
    "Nether Wart": minionCostTypes(["NETHER_STALK", "ENCHANTED_NETHER_STALK"], "single enchanted", True),
    "Flower": minionCostTypes(["YELLOW_FLOWER", "ENCHANTED_DANDELION", "ENCHANTED_POPPY"], "double enchanted", True, {1: {}}),
    "Fishing": {1: {'RAW_FISH': 64}, 2: {'RAW_FISH': 128}, 3: {'RAW_FISH': 256}, 4: {'RAW_FISH': 512}, 5: {'ENCHANTED_RAW_FISH': 8}, 6: {'ENCHANTED_RAW_FISH': 24}, 7: {'ENCHANTED_RAW_FISH': 64}, 8: {'ENCHANTED_RAW_FISH': 128}, 9: {'ENCHANTED_RAW_FISH': 256}, 10: {'ENCHANTED_RAW_FISH': 512}, 11: {'ENCHANTED_COOKED_FISH': 8}, 12: {'ENCHANTED_COOKED_FISH': 16}},
    "Zombie": minionCostTypes(["ROTTEN_FLESH", "ENCHANTED_ROTTEN_FLESH"], "single enchanted", False),
    "Revenant": {},
    "Voidling": {},
    "Inferno": {},
    "Vampire": minionCostTypes(["HEMOVIBE", "HEMOGLASS"], "single enchanted", False),
    "Skeleton": minionCostTypes(["BONE", "ENCHANTED_BONE"], "single enchanted", False),
    "Creeper": minionCostTypes(["SULPHUR", "ENCHANTED_GUNPOWDER", "ENCHANTED_FIREWORK_ROCKET"], "double enchanted", False, {11: {"ENCHANTED_FIREWORK_ROCKET": 16}}),
    "Spider": minionCostTypes(["STRING", "ENCHANTED_STRING"], "single enchanted", False),
    "Tarantula": {},
    "Cave Spider": minionCostTypes(["SPIDER_EYE", "ENCHANTED_SPIDER_EYE", "ENCHANTED_FERMENTED_SPIDER_EYE"], "double enchanted", False, {11: {"ENCHANTED_FERMENTED_SPIDER_EYE": 16}}),
    "Blaze": minionCostTypes(["BLAZE_ROD", "ENCHANTED_BLAZE_POWDER", "ENCHANTED_BLAZE_ROD"], "double enchanted", True),
    "Magma Cube": minionCostTypes(["MAGMA_CREAM", "ENCHANTED_MAGMA_CREAM"], "single enchanted", True),
    "Enderman": {1: {"ENDER_PEARL": 64}, 2: {"ENDER_PEARL": 128}, 3: {"ENCHANTED_ENDER_PEARL": 8}, 4: {"ENCHANTED_ENDER_PEARL": 24}, 5: {"ENCHANTED_ENDER_PEARL": 48}, 6: {"ENCHANTED_ENDER_PEARL": 96}, 7: {"ENCHANTED_EYE_OF_ENDER": 8}, 8: {"ENCHANTED_EYE_OF_ENDER": 24}, 9: {"ENCHANTED_EYE_OF_ENDER": 48}, 10: {"ENCHANTED_EYE_OF_ENDER": 96}, 11: {"ENCHANTED_EYE_OF_ENDER": 192}},
    "Ghast": {1: {"GHAST_TEAR": 64}, 2: {"GHAST_TEAR": 128}, 3: {"GHAST_TEAR": 256}, 4: {"GHAST_TEAR": 512}, 5: {"ENCHANTED_GHAST_TEAR": 256}, 6: {"ENCHANTED_GHAST_TEAR": 512}, 7: {"SILVER_FANG": 32}, 8: {"SILVER_FANG": 64}, 9: {"SILVER_FANG": 128}, 10: {"SILVER_FANG": 256}, 11: {"SILVER_FANG": 512}, 12: {"SILVER_FANG": 1024}},
    "Slime": minionCostTypes(["SLIME_BALL", "ENCHANTED_SLIME_BALL", "ENCHANTED_SLIME_BLOCK"], "double enchanted", False),
    "Cow": {1: {"RAW_BEEF": 64}, 2: {"RAW_BEEF": 128}, 3: {"RAW_BEEF": 256}, 4: {"RAW_BEEF": 512}, 5: {"ENCHANTED_RAW_BEEF": 8}, 6: {"ENCHANTED_RAW_BEEF": 24}, 7: {"ENCHANTED_RAW_BEEF": 64}, 8: {"ENCHANTED_RAW_BEEF": 128}, 9: {"ENCHANTED_RAW_BEEF": 256}, 10: {"ENCHANTED_RAW_BEEF": 512}, 11: {"ENCHANTED_LEATHER": 512}, 12: {"ENCHANTED_LEATHER": 1028}},  # correct, first launch of 0.23.1 has 1028 instead of the expected 1024
    "Pig": minionCostTypes(["PORK", "ENCHANTED_PORK", "ENCHANTED_GRILLED_PORK"], "double enchanted", True, {1: {"PORK": 64}, 2: {"PORK": 128}, 3: {"PORK": 256}}),
    "Chicken": minionCostTypes(["RAW_CHICKEN", "ENCHANTED_RAW_CHICKEN"], "single enchanted", True, {1: {"RAW_CHICKEN": 64}, 2: {"RAW_CHICKEN": 128}, 3: {"RAW_CHICKEN": 256}}),
    "Sheep": minionCostTypes(["MUTTON", "ENCHANTED_MUTTON", "ENCHANTED_COOKED_MUTTON"], "double enchanted", True, {1: {"MUTTON": 64}, 2: {"MUTTON": 128}, 3: {"MUTTON": 256}}),
    "Rabbit": minionCostTypes(["RABBIT", "ENCHANTED_RABBIT", "ENCHANTED_COOKED_RABBIT"], "double enchanted", True, {1: {"RABBIT": 64}, 2: {"RABBIT": 128}, 3: {"RABBIT": 256}}),
    "Oak": minionCostTypes(["LOG", "ENCHANTED_OAK_LOG"], "single enchanted", False),
    "Spruce": minionCostTypes(["LOG:1", "ENCHANTED_SPRUCE_LOG"], "single enchanted", False),
    "Birch": minionCostTypes(["LOG:2", "ENCHANTED_BIRCH_LOG"], "single enchanted", False),
    "Dark Oak": minionCostTypes(["LOG_2:1", "ENCHANTED_DARK_OAK_LOG"], "single enchanted", False),
    "Acacia": minionCostTypes(["LOG_2", "ENCHANTED_ACACIA_LOG"], "single enchanted", False),
    "Jungle": minionCostTypes(["LOG:3", "ENCHANTED_JUNGLE_LOG"], "single enchanted", False)
}

minionCosts["Revenant"] = {
    1: { "REVENANT_FLESH": 80, "ENCHANTED_ROTTEN_FLESH": 256, "ENCHANTED_DIAMOND": 256 },
    2: { "REVENANT_FLESH": 140, **minionCostSum("Zombie", 1) },
    3: { "REVENANT_FLESH": 280, **minionCostSum("Zombie", 2) },
    4: { "REVENANT_FLESH": 448, **minionCostSum("Zombie", 3) },
    **{ i: { "REVENANT_VISCERA": 7 * 2**(i - 5), **minionCostSum("Zombie", i - 1) } for i in np.arange(5, 12) },
    12: { "REVENANT_VISCERA": 64 }
}
minionCosts["Voidling"] = {
    1: { "NULL_SPHERE": 80, **minionCostSum("Enderman", 1) },
    2: { "NULL_SPHERE": 140, **minionCostSum("Obsidian", 1) },
    3: { "NULL_SPHERE": 280, **minionCostSum("Enderman", 2) },
    4: { "NULL_SPHERE": 448, **minionCostSum("Obsidian", 3) },
    **{ i: { "NULL_OVOID": 7 * 2**(i - 5), **minionCostSum(f"{'Obsidian' if i % 2 == 0 else 'Enderman'}", i - 1) } for i in np.arange(5, 12) }
}
minionCosts["Inferno"] = {
    1: { "DERELICT_ASHE": 80, **minionCostSum("Blaze", 1)},
    2: {"DERELICT_ASHE": 320 },
    **{ i: {"MOLTEN_POWDER": 8 * 2**(i - 3)} for i in np.arange(3, 9) },
    9: { 'MOLTEN_POWDER': 256, "INFERNO_VERTEX": 16 },
    10: { 'MOLTEN_POWDER': 256, "INFERNO_VERTEX": 48 }
}
minionCosts["Inferno"][11] = { "INFERNO_VERTEX": 48, "INFERNO_APEX": 1, **minionCostSum("Inferno", 8) }
minionCosts["Inferno"][11]["MOLTEN_POWDER"] += 256
minionCosts["Tarantula"] = {
    1: { "TARANTULA_WEB": 80, "ENCHANTED_FERMENTED_SPIDER_EYE": 1 },
    2: { "TARANTULA_WEB": 140, **minionCostSum("Spider", 1) },
    3: { "TARANTULA_WEB": 280, **minionCostSum("Spider", 2) },
    4: { "TARANTULA_WEB": 448, **minionCostSum("Spider", 3) },
    **{ i: {"TARANTULA_SILK": 7 * 2**(i - 5), **minionCostSum("Spider", i - 1)} for i in np.arange(5, 12) },
    12: { "TARANTULA_SILK": 64 }
}

extraMinionCosts = {
    "Custom": { 6: { "TESTING": 2 }, 12: { "COINS": 1, "NON_EXISTENT": 1, "TEST": 2 } },
    "Cobblestone": { 12: { "COINS": 2000000 } },
    "Obsidian": { 12: { "COINS": 2000000 } },
    "Glowstone": { 12: { "COINS": 2000000 } },
    "Red Sand": { 12: { "COINS": 2000000 } },
    "Mycelium": { 12: { "COINS": 2000000 } },
    "Clay": { 12: { "COINS": 2000000, "FISHY_TREAT": 256 } },
    "Ice": { 12: { "COINS": 1000000, "NORTH_STARS": 300 } },
    "Snow": { 12: { "COINS": 2000000, "NORTH_STARS": 500 } },
    "Coal": { 12: { "COINS": 2000000 } },
    "Iron": { 12: { "COINS": 2000000 } },
    "Gold": { 12: { "COINS": 2000000 } },
    "Diamond": { 12: { "COINS": 2000000 } },
    "Lapis": { 12: { "COINS": 2000000 } },
    "Redstone": { 12: { "COINS": 2000000 } },
    "Emerald": { 12: { "COINS": 2000000 } },
    "Quartz": { 12: { "COINS": 2000000 } },
    "Mithril": { 12: { "COINS": 2000000 } },
    "Hard Stone": { 12: { "COINS": 2000000 } },
    "Wheat": { 12: { "PELTS": 75 } },
    "Melon": { 12: { "PELTS": 75 } },
    "Pumpkin": { 12: { "PELTS": 75 } },
    "Carrot": { 12: { "PELTS": 75 } },
    "Potato": { 12: { "PELTS": 75 } },
    "Mushroom": { 12: { "PELTS": 75 } },
    "Cactus": { 12: { "PELTS": 75 } },
    "Cocoa Beans": { 12: { "PELTS": 75 } },
    "Sugar Cane": { 12: { "PELTS": 75 } },
    "Nether Wart": { 12: { "PELTS": 75 } },
    "Flower": { 1: { "T1_FROM_DARK_AUCTION": 1 } },
    "Fishing": { 12: { "COINS": 2000000, "FISHY_TREAT": 256 } },
    "Revenant": { 12: { "COINS": 2000000 } },
    "Vampire": { 1: { "BAT_PERSON_HELMET": 1 } },
    "Tarantula": { 12: { "COINS": 2000000 } },
    "Blaze": { 12: { "COINS": 2000000 } },
    "Magma Cube": { 12: { "COINS": 2000000 } },
    "Ghast": { 12: { "COINS": 2000000 } },
    "Cow": { 12: { "PELTS": 75 } },
    "Pig": { 12: { "PELTS": 75 } },
    "Chicken": { 12: { "PELTS": 75 } },
    "Sheep": { 12: { "PELTS": 75 } },
    "Rabbit": { 12: { "PELTS": 75 } },
}

#%% other crafting costs

upgrades_material_cost = {
    "beacon": {
        1: { "ENCHANTED_MITHRIL": 192, "STARFALL": 64 },
        2: { "REFINED_MITHRIL": 5 },
        3: { "REFINED_MITHRIL": 10 },
        4: { "REFINED_MITHRIL": 20, "PLASMA": 1 },
        5: { "REFINED_MITHRIL": 40, "PLASMA": 5 }
    },
    "crystal": {
        "Farm Crystal": { "ENCHANTED_PUMPKIN": 96, "ENCHANTED_QUARTZ": 1 },
        "Woodcutting Crystal": { "ENCHANTED_SPRUCE_LOG": 96, "ENCHANTED_QUARTZ": 1 },
        "Mithril Crystal": { "ENCHANTED_MITHRIL": 16, "ENCHANTED_QUARTZ": 1 },
        "Winter Crystal": {},
        "Winter + Mithril Crystal": { "ENCHANTED_MITHRIL": 16, "ENCHANTED_QUARTZ": 1 }
    },
    "EVERBURNING_FLAME": { "PLASMA_BUCKET": 1, "FLAMES": 16, "ENCHANTED_SULPHUR_CUBE": 2, "ENCHANTED_RED_SAND_CUBE": 2 }
}

