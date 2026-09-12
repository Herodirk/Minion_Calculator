# -*- coding: utf-8 -*-
"""
@author: Herodirk

Official Minion Calculator Add-ons.
A collection of add-ons made by Herodirk.

The Official Add-ons include:
- Minion Crafting
- Days to Repay Setup
- Basic Minion Loop
- Bad Luck Inferno
- Inferno Minion Loop
- Old Corrupted Frags (inactive)
- Old Enchanted Hopper (inactive)
"""

import numpy as np
import math

class Calc_add_ons():
    def __init__(self, calculator):
        self.calc = calculator

        self.calc.huim.new_edit_vars("basic_minion_loop", {
            "setup_cost_limit": {"dtype": float, "display": "Setup Cost Limit", "initial": 0, "options": None},
            "auto_crystal": {"dtype": bool, "display": "Automatic Crystal", "initial": True, "options": None},
            "auto_afkpet": {"dtype": bool, "display": "Automatic AFK Pet", "initial": True, "options": None},
            "markdown_output": {"dtype": bool, "display": "Markdown Output", "initial": True, "options": None}
            }, lambda results: self.basic_minion_loop(results))
        self.calc.huim.new_edit_vars("inferno_minion_loop", {"setup_cost_limit": {"dtype": float, "display": "Setup Cost Limit", "initial": 0, "options": None}, "amount_limit": {"dtype": int, "display": "Minion Amount Limit", "initial": 32, "options": None}, "markdown_output": {"dtype": bool, "display": "Markdown Output", "initial": True, "options": None}}, lambda results: self.inferno_minion_loop(results))
        self.calc.huim.new_edit_vars("collection_maxing", {"sort_by": {"dtype": str, "display": "Sort By", "initial": "Fastest Time", "options": ["Fastest Time", "Lowest Setup Cost", "Lowest Total Cost"]}, "time_limit": {"dtype": float, "display": "Time Limit", "initial": 0, "options": None}, "setup_cost_limit": {"dtype": float, "display": "Setup Cost Limit", "initial": 0, "options": None}, "amount_limit": {"dtype": int, "display": "Minion Amount Limit", "initial": 32, "options": None}, "markdown_output": {"dtype": bool, "display": "Markdown Output", "initial": True, "options": None}}, lambda results: self.collection_maxing(results))
        self.calc.huim.new_edit_vars("partial_setup_cost", {setup_part_key: {"dtype": bool, "display": setup_part_display, "initial": True, "options": None} for setup_part_key, setup_part_display in {"minion": "Minion", "fuel": "Fuel", "hopper": "Hopper", "upgrade1": "Upgrade 1", "upgrade2": "Upgrade 2", "infusion": "Infusion", "free_will": "Free Will", "chest": "Chest", "beacon": "Beacon", "crystal": "Crystal", "postcard": "Postcard", "potato_accessory": "Potato Accessory","pet_exp_boost": "Pet EXP Boost","expshareitem": "EXP Share Item","toucan_attribute": "Toucan Shards","falcon_attribute": "Falcon Shards"}.items()}, lambda results: self.partial_setup_cost(results))
        self.calc.huim.new_edit_vars("wisp_levelling", {
            "gabagool_tier": {"dtype": str, "display": "Gabagool Tier", "initial": "Crude Gabagool", "options": ["Crude Gabagool", "Fuel Gabagool", "Heavy Gabagool", "Hypergolic Gabagool"]},
            "wisp_pet": {"dtype": str, "display": "Wisp Pet", "initial": "Subzero Wisp", "options": ["Droplet Wisp", "Frost Wisp", "Glacial Wisp", "Subzero Wisp"]},
            "pet_item": {"dtype": str, "display": "Pet Item", "initial": "All Skills Exp Super-Boost", "options": ["None", "All Skills Exp Boost", "All Skills Exp Super-Boost"]},
            "taming": {"dtype": int, "display": "Taming", "initial": 60, "options": None},
            "battle_experience": {"dtype": int, "display": "Battle Experience", "initial": 10, "options": self.calc.input_options["attribute"]},
            "diana": {"dtype": bool, "display": "Diana", "initial": False, "options": None},
            "beastmaster": {"dtype": float, "display": "Beastmaster", "initial": 0, "options": None},
            "blaze_slayer": {"dtype": bool, "display": "Blaze Slayer 8", "initial": False, "options": None},
            }, self.wisp_levelling)
        self.calc.huim.new_edit_vars("calculator_data_debug", {"data_loc": {"dtype": str, "display": "Data Location", "initial": "COBBLESTONE.prices.npc", "options": None}}, self.calculator_data_debug)

        self.reverse_affected_minions = {
            "afkpet": {},
            "crystal": {}
        }
        for modifier_key in self.reverse_affected_minions.keys():
            for modifier_id in self.calc.input_options[modifier_key].values():
                if modifier_id == "NONE":
                    continue
                for affected_minion in self.calc.md.calculator_data[modifier_id]["affected_minions"]:
                    if affected_minion in self.calc.md.calculator_data:
                        self.reverse_affected_minions[modifier_key][affected_minion] = modifier_id
                        continue
                    for minion_id in self.calc.input_options["minion"].values():
                        if self.calc.md.has_data_tag(minion_id, affected_minion):
                            self.reverse_affected_minions[modifier_key][minion_id] = modifier_id

        self.add_ons_data = {
            "Minion Crafting": {"function": self.craft_material_amount, "auto_run": "post"},
            "Crystal and Pet": {"function": self.crystal_and_pet, "auto_run": "pre"},
            "Dragon Pet Source Prices": {"function": self.dragon_source_prices, "auto_run": "pre"},
            "Partial Setup Cost": {"function": self.partial_setup_cost_inputs, "auto_run": "post"},
            "Days to Repay Setup": {"function": self.setup_repay_time, "auto_run": "post"},
            "Basic Minion Loop": {"function": self.basic_minion_loop_inputs, "auto_run": "post"},
            "Bad Luck Inferno": {"function": self.bad_luck_inferno, "auto_run": "post"},
            "Inferno Minion Loop": {"function": self.inferno_minion_loop_inputs, "auto_run": "post"},
            "Exact Pet Levelling": {"function": self.exact_pet_levelling_inputs, "auto_run": "post"},
            # "Wisp Pet Levelling": {"function": self.wisp_levelling_inputs, "auto_run": "post"},
            "Chili Pepper Collection": {"function": self.collection_maxing_inputs, "auto_run": "post"},
            # "Old Corrupted Frags": {"function": self.old_corrupted_frags, "auto_run": "post"},
            # "Old Enchanted Hopper": {"function": self.old_enchanted_hopper, "auto_run": "post"},
            # "Calculator Data Debug": {"function": self.calculator_data_debug_inputs, "auto_run": "post"},
        }
        return

    def old_corrupted_frags(self):
        # This Add-on is inactive, to turn it back on uncomment the add-on in self.add_ons_data in __init__
        """Outputs the total profit for the old price of Corrupted Fragments"""
        if "CORRUPTED_FRAGMENT" not in self.calc.itemtype_profit.list:
            self.calc.collect_add_on_output("Old Corrupted Frag profit", "Setup does not produce Corrupted Fragments")
            return
        corrupted_frag_profit = self.calc.itemtype_profit.list["CORRUPTED_FRAGMENT"]
        total_profit = self.calc.total_profit.get()
        self.calc.collect_add_on_output("Old Corrupted Frag profit", f"{self.calc.huim.reduced_number(total_profit + 19 * corrupted_frag_profit, 2)}")
        return

    def old_enchanted_hopper(self):
        # This Add-on is inactive, to turn it back on uncomment the add-on in self.add_ons_data in __init__
        """Outputs the total profit for the old sell rate of Enchanted Hoppers"""
        if self.calc.hopper.get() != "Enchanted Hopper" or self.calc.sell_loc.get() != "Hopper":
            self.calc.collect_add_on_output("Old Enchanted Hopper profit", "Setup does not use Enchanted Hoppers")
            return
        profit = self.calc.total_profit.get()
        self.calc.collect_add_on_output("Old Enchanted Hopper profit", f"{self.calc.huim.reduced_number(profit * (9 / 7), 2)}")
        return

    def crystal_and_pet(self, minion_id=None, return_outputs=False):
        if minion_id is None:
            minion_id = self.calc.minion.get()
        outputs = {}
        for modifier_key in self.reverse_affected_minions.keys():
            result = "NONE"
            if minion_id in self.reverse_affected_minions[modifier_key]:
                result = self.reverse_affected_minions[modifier_key][minion_id]
            if return_outputs:
                outputs[modifier_key] = result
            else:
                self.calc.var_dict[modifier_key].set(result, True)
            if modifier_key == "afkpet":
                afkpet_level = 100
                if result == "NONE":
                    afkpet_level = 0
                if return_outputs:
                    outputs["afkpet_lvl"] = afkpet_level
                else:
                    self.calc.afkpet_lvl.set(afkpet_level)
        if return_outputs:
            return outputs
        return

    def wisp_levelling_inputs(self):
        # This Add-on is inactive, it works but is missing a lot of logic
        outputs = self.calc.huim.get_from_GUI(["items"])
        if "CRUDE_GABAGOOL" not in outputs["items"] and "VERY_CRUDE_GABAGOOL" not in outputs["items"]:
            self.calc.collect_add_on_output("Wisp Pet Levelling", "No Gabagool found")
            return
        self.calc.huim.edit_vars("wisp_levelling")
        return

    def wisp_levelling(self, results):
        setup_data = self.calc.huim.get_from_GUI(self.calc.ID_order)
        outputs = self.calc.huim.get_from_GUI(["items"])
        gabagool_tier = { "Crude Gabagool": "CRUDE_GABAGOOL", "Fuel Gabagool": "FUEL_GABAGOOL", "Heavy Gabagool": "HEAVY_GABAGOOL", "Hypergolic Gabagool": "HYPERGOLIC_GABAGOOL" }[results["gabagool_tier"]]
        wisp_pet = { "Droplet Wisp": "PET_DROPLET_WISP", "Frost Wisp": "PET_FROST_WISP", "Glacial Wisp": "PET_GLACIAL_WISP", "Subzero Wisp": "PET_SUBZERO_WISP" }[results["wisp_pet"]]
        pet_item = { "None": "NONE", "All Skills Exp Boost": "PET_ITEM_ALL_SKILLS_BOOST_COMMON", "All Skills Exp Super-Boost": "ALL_SKILLS_SUPER_BOOST" }[results["pet_item"]]

        crude_gabagool_amount = outputs["items"]["CRUDE_GABAGOOL"] + 192 * outputs["items"]["VERY_CRUDE_GABAGOOL"]
        base_xp_per_crude_gabagool = { "CRUDE_GABAGOOL": 100, "FUEL_GABAGOOL": 3200 / 24, "HEAVY_GABAGOOL": 102400 / 576, "HYPERGOLIC_GABAGOOL": 3276800 / 6912 }[gabagool_tier]
        extra_cost_per_crude_gabagool = { "CRUDE_GABAGOOL": {}, "FUEL_GABAGOOL": { "ENCHANTED_COAL": 4 / 24, "ENCHANTED_SULPHUR": 0.25 / 24 }, "HEAVY_GABAGOOL": { "ENCHANTED_COAL": 100 / 576, "ENCHANTED_SULPHUR": 6.25 / 576 }, "HYPERGOLIC_GABAGOOL": { "ENCHANTED_COAL": 1204 / 6912, "ENCHANTED_SULPHUR": 75.25 / 6912 } }[gabagool_tier]

        total_xp = base_xp_per_crude_gabagool * crude_gabagool_amount * (1 + results["taming"] / 100) * (1 + results["battle_experience"] / 100) * (1 + results["beastmaster"] / 100)
        if results["diana"]:
            total_xp *= 1.35
        if results["blaze_slayer"]:
            total_xp *= 1.2
        if pet_item != "NONE":
            total_xp *= 1 + self.calc.md.calculator_data[pet_item]["exp_boost_amount"] / 100

        pet_rarity = self.calc.md.calculator_data[wisp_pet]["pet_rarities"][0]
        max_pet_xp = self.calc.md.calculator_data[pet_rarity]["max_lvl_pet_xp_amount"]
        pets_levelled = total_xp / max_pet_xp

        total_cost = 0
        for item_id, per_gabagool_amount in extra_cost_per_crude_gabagool.items():
            total_cost += crude_gabagool_amount * per_gabagool_amount * self.calc.get_price(item_id, setup_data, "buy", "bazaar")
        self.calc.update_pet_price(wisp_pet, pet_rarity)
        pet_price_max = self.calc.md.calculator_data[wisp_pet]["pet_prices"][pet_rarity]["max"]
        pet_price_min = self.calc.md.calculator_data[wisp_pet]["pet_prices"][pet_rarity]["min"]
        pet_profit = pets_levelled * (self.calc.apply_ah_tax(pet_price_max, setup_data) - pet_price_min)
        used_prices = f"{self.calc.huim.reduced_number(pet_price_min)} - {self.calc.huim.reduced_number(pet_price_max)} (Taxed: {self.calc.huim.reduced_number(self.calc.apply_ah_tax(pet_price_max, setup_data))})"

        self.calc.collect_add_on_output("Wisp Pet Levelling", f"{self.calc.huim.reduced_number(pet_profit)} - {self.calc.huim.reduced_number(total_cost)} = {self.calc.huim.reduced_number(pet_profit - total_cost)}, Used Pet Prices: " + used_prices)
        return

    def dragon_source_prices(self):
        """Calculates dragon prices for buying from the source"""
        dragon_pet_recipes = {
            "PET_GOLDEN_DRAGON": {
                "COIN": 500000000,
                "ENCHANTED_GOLD_BLOCK": 50,
                "PERFECT_AMETHYST_GEM": 1,
                "PERFECT_JADE_GEM": 1,
                "PERFECT_SAPPHIRE_GEM": 1,
                "PERFECT_AMBER_GEM": 1,
                "PERFECT_TOPAZ_GEM": 1
            },
            "PET_JADE_DRAGON": {
                "COIN": 500000000,
                "STARLYN_PRIZE": 20,
                "FIGSTONE": 64,
                "MANGCORE": 64,
                "HELIXIS": 64,
            },
            "PET_ROSE_DRAGON": {
                "COIN": 500000000,
                "COPPER": 20000,
                "CONDENSED_HELIANTHUS": 5,
                "GLASSCORN": 1,
                "DEVOURER": 1,
                "ALL_IN_ALOE": 1,
                "PHANTOMLEAF": 1,
                "TIMESTALK": 1,
            }
        }
        setup_data = self.calc.huim.get_from_GUI(self.calc.ID_order)
        coins_per_copper = []
        for mutation, base_copper in { "ALL_IN_ALOE": 2300, "PHANTOMLEAF": 1500, "ZOMBUD": 500, "FLESHTRAP": 180 }.items():
            coins_per_copper.append((self.calc.get_price(mutation, setup_data, "buy", "bazaar") + base_copper * 2000) / (base_copper * 1.6))
        self.calc.md.calculator_data["COPPER"]["prices"]["custom"] = min(coins_per_copper)

        updated_pets = []
        for pet_slot in ["levelingpet", "expsharepet", "expsharepetslot2", "expsharepetslot3"]:
            if not self.calc.md.has_data_tag(setup_data[pet_slot], ["dragon_pet", "dragon_egg_pet"]):
                continue
            if setup_data[pet_slot] in updated_pets:
                continue
            self.calc.update_pet_price(setup_data[pet_slot], setup_data[pet_slot + "_rarity"])
            updated_pets.append(setup_data[pet_slot])
            dragon_base_id = setup_data[pet_slot].removesuffix("_EGG")
            source_cost = 0
            for item_id, amount in dragon_pet_recipes[dragon_base_id].items():
                source_cost += amount * self.calc.get_price(item_id, setup_data, "buy", "bazaar")
            self.calc.md.calculator_data[setup_data[pet_slot]]["pet_prices"][setup_data[pet_slot + "_rarity"]]["min"] = source_cost
        return

    def bad_luck_inferno(self, setup_data=None, outputs=None, return_value=False):
        """Outputs the profit of the common Hypergolic drops and the price per Inferno Vertex"""
        if setup_data is None:
            setup_data = self.calc.huim.get_from_GUI(["fuel", "inferno_grade", "bazaar_buy_type", "bazaar_sell_type", "bazaar_taxes", "bazaar_flipper", "mayor"])
            outputs = self.calc.huim.get_from_GUI(["total_profit", "itemtype_profit", "harvests"])
        if setup_data["fuel"] != "INFERNO_FUEL":
            self.calc.collect_add_on_output("Bad Luck Inferno", "No Inferno Minion Fuel Found")
            return
        total_profit = outputs["total_profit"]
        if setup_data["inferno_grade"] != "HYPERGOLIC_GABAGOOL":
            if return_value:
                return total_profit
            self.calc.collect_add_on_output("Bad Luck Inferno", "No Hypergolic Items Found")
            return
        item_type_profit = outputs["itemtype_profit"]
        no_rng_profit_average = total_profit - item_type_profit["INFERNO_APEX"] - item_type_profit["REAPER_PEPPER"] - item_type_profit["GABAGOOL_THE_FISH"]
        if return_value:
            return no_rng_profit_average
        prediction_interval_size = 1.96  # for 95% of cases within the interval, https://en.wikipedia.org/wiki/Prediction_interval#Known_mean,_known_variance
        interval_radius_vertex_amount = prediction_interval_size * math.sqrt(outputs["harvests"] * self.calc.md.inferno_fuel_data["drops"]["INFERNO_VERTEX"] * (1 - self.calc.md.inferno_fuel_data["drops"]["INFERNO_VERTEX"]))
        per_vertex = self.calc.get_price("INFERNO_VERTEX", setup_data, "sell", "bazaar")
        interval_min = no_rng_profit_average - per_vertex * interval_radius_vertex_amount
        interval_max = no_rng_profit_average + per_vertex * interval_radius_vertex_amount
        self.calc.collect_add_on_output("Bad Luck Inferno Profit", f"average: {self.calc.huim.reduced_number(no_rng_profit_average, 2)}, 95% of cases: {self.calc.huim.reduced_number(interval_min, 2)} -- {self.calc.huim.reduced_number(interval_max, 2)}, average (no Vertexes): {self.calc.huim.reduced_number(no_rng_profit_average - item_type_profit["INFERNO_VERTEX"], 2)}")
        return

    def setup_repay_time(self):
        """Outputs the time (in days) it take for a setup to repay itself"""
        setup_data = self.calc.huim.get_from_GUI(["time_seconds", "setupcost", "free_will", "total_profit"])
        setupcost = setup_data["setupcost"]
        profit = setup_data["total_profit"]
        if profit < 0:
            self.calc.collect_add_on_output("Setup Repay Time", "Negative profit, cannot repay")
            return
        try:
            profitpersecond = profit / setup_data["time_seconds"]
            repay_time_s = setupcost / profitpersecond
        except ZeroDivisionError:
            self.calc.collect_add_on_output("Setup Repay Time", "Division by zero")
            return
        repay_time = np.round(repay_time_s / 86400, 2)
        self.calc.collect_add_on_output("Setup Repay Time", f"{repay_time} Days")
        return

    def basic_minion_loop(self, results):
        setup_data = self.calc.huim.get_from_GUI(self.calc.ID_order)
        cost_filter = results["setup_cost_limit"]
        if cost_filter == 0:
            cost_filter = math.inf
        auto_crystal = results["auto_crystal"]
        auto_afkpet = results["auto_afkpet"]
        markdown_output = results["markdown_output"]
        calculated_setup_profits = {}
        calculated_setup_costs = {}
        loop_minion_options = list(self.calc.input_options["minion"].values())
        loop_minion_skip = ["CUSTOM_MINION"]
        loop_minion_smelting = ["IRON_MINION", "GOLD_MINION", "CACTUS_MINION"]
        super_compactor = False
        if setup_data["upgrade1"] in ["SUPER_COMPACTOR_3000", "DWARVEN_COMPACTOR"]:
            super_compactor = True
        if setup_data["upgrade2"] in ["SUPER_COMPACTOR_3000", "DWARVEN_COMPACTOR"]:
            super_compactor = True
            setup_data["upgrade2"] = setup_data["upgrade1"]
            setup_data["upgrade1"] = "SUPER_COMPACTOR_3000"
        
        upgrades = [setup_data["upgrade1"], setup_data["upgrade2"]]
        for loop_minion in loop_minion_options:
            if loop_minion in loop_minion_skip:
                continue
            if "CORRUPT_SOIL" in upgrades and not self.calc.md.has_data_tag(loop_minion, "mob_minion"):
                continue
            setup_data["minion"] = loop_minion
            setup_data["miniontier"] = int(list(self.calc.md.calculator_data[setup_data["minion"]]["speed"].keys())[-1])
            if super_compactor:
                if loop_minion in loop_minion_smelting:
                    setup_data["upgrade1"] = "DWARVEN_COMPACTOR"
                else:
                    setup_data["upgrade1"] = "SUPER_COMPACTOR_3000"
            if auto_crystal or auto_afkpet:
                auto_crystal_and_pet = self.crystal_and_pet(setup_data["minion"], True)
            if auto_crystal:
                setup_data["crystal"] = auto_crystal_and_pet["crystal"]
            if auto_afkpet:
                setup_data["afkpet"] = auto_crystal_and_pet["afkpet"]
                setup_data["afkpet_lvl"] = auto_crystal_and_pet["afkpet_lvl"]
            outputs = self.calc.calculate(setup_data=setup_data, return_outputs=True)

            if outputs["setupcost"] < cost_filter:
                calculated_setup_profits[loop_minion] = outputs["total_profit"]
                calculated_setup_costs[loop_minion] = outputs["setupcost"]
        if len(calculated_setup_profits) == 0:
            self.calc.collect_add_on_output("Basic Minion Loop", "No setups pass the cost filter")
            return
        setup_data.update(self.calc.decode_id(outputs["calculated_ID"]))
        setup_data.update(outputs)
        setup_data["bazaar_update_txt"] = self.calc.bazaar_update_txt.get()
        text_output_order = {
            "amount": None,
            "Upgrades: ": { "": {"fuel", "hopper", "upgrade1", "upgrade2", "chest", "beacon", "crystal", "postcard", "infusion", "free_will"}},
            "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
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
            "": {"": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper", "sell_form"]},
        }
        if auto_crystal:
            text_output_order["Upgrades: "][""].remove("crystal")
        if auto_afkpet:
            text_output_order["afk"]["%\n> "][0].remove("afkpet")
        output_str = self.calc.text_output(calculation_data=setup_data, output_switches={}, output_order=text_output_order, markdown=markdown_output, to_terminal=False)
        if markdown_output:
            if auto_crystal:
                output_str += "\nAutomatic Crystal: `True`"
            if auto_afkpet:
                output_str += "\nAutomatic AFK Pet: `True`"
            output_str += "\n```"
        else:
            if auto_crystal:
                output_str += "\nAutomatic Crystal: True"
            if auto_afkpet:
                output_str += "\nAutomatic AFK Pet: True"
            output_str += "\n"
        output_str += f"\nMinion: profit, setup cost (limit: {self.calc.huim.reduced_number(cost_filter)})"
        for _ in range(10):
            if len(calculated_setup_profits) == 0:
                break
            top_minion = max(calculated_setup_profits, key=calculated_setup_profits.get)
            output_str += "\n" + self.calc.md.calculator_data[top_minion]["display"] + ": " + self.calc.huim.reduced_number(calculated_setup_profits[top_minion]) + ", " + self.calc.huim.reduced_number(calculated_setup_costs[top_minion])
            del calculated_setup_profits[top_minion]
        if markdown_output:
            output_str += "\n```"
        output_str += "\n"
        if self.calc.output_to_clipboard.get():
            self.calc.clipboard_clear()
            self.calc.clipboard_append(output_str)
        self.calc.huim.logger.info("\n" + output_str)
        self.calc.collect_add_on_output("Basic Minion Loop", "See terminal")
        return


    def inferno_minion_loop(self, results):
        setup_data = self.calc.huim.get_from_GUI(self.calc.ID_order)
        calculated_setup_profits = {}
        calculated_setup_bad_luck_profits = {}
        calculated_setup_costs = {}

        cost_filter = results["setup_cost_limit"]
        if cost_filter == 0:
            cost_filter = math.inf
        minion_amount_limit = results["amount_limit"]
        if minion_amount_limit < 1:
            self.calc.collect_add_on_output("Inferno Minion Loop", "Positive minion amount limit is required")
            return
        markdown_output = results["markdown_output"]
        setup_data["minion"] = "INFERNO_MINION"
        setup_data["fuel"] = "INFERNO_FUEL"
        if setup_data["inferno_grade"] == "HYPERGOLIC_GABAGOOL":
            setup_data["chest"] = "XXLARGE_ENCHANTED_CHEST"
        setup_data["rising_celsius_override"] = True

        loop_tiers = range(1, 12)
        loop_amounts = range(1, minion_amount_limit + 1)
        for loop_tier in loop_tiers:
            setup_data["miniontier"] = loop_tier
            for loop_amount in loop_amounts:
                setup_data["amount"] = loop_amount
                outputs = self.calc.calculate(setup_data=setup_data, return_outputs=True)
                bad_luck_profit = self.bad_luck_inferno(setup_data=setup_data, outputs=outputs, return_value=True)
                cost = outputs["setupcost"]
                if cost < cost_filter:
                    calculated_setup_costs[f"{loop_tier}, {loop_amount}"] = cost
                    calculated_setup_profits[f"{loop_tier}, {loop_amount}"] = outputs["total_profit"]
                    calculated_setup_bad_luck_profits[f"{loop_tier}, {loop_amount}"] = bad_luck_profit
        if len(calculated_setup_bad_luck_profits) == 0:
            self.calc.collect_add_on_output("Inferno Minion Loop", "No setups pass the cost filter")
            return
        setup_data.update(self.calc.decode_id(outputs["calculated_ID"]))
        setup_data.update(outputs)
        setup_data["bazaar_update_txt"] = self.calc.bazaar_update_txt.get()
        output_str = self.calc.text_output(calculation_data=setup_data, output_switches={}, output_order={
                "Upgrades: ": { "": {"fuel", "hopper", "upgrade1", "upgrade2", "chest", "beacon", "crystal", "postcard", "infusion", "free_will"}},
                "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
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
                "": {"": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper", "sell_form"]},
                }, markdown=markdown_output, to_terminal=False)
        if markdown_output:
            output_str += "\n```"
        else:
            output_str += "\n"
        output_str += f"\nTier, Amount (limit: {self.calc.huim.reduced_number(minion_amount_limit)}): bad luck profit, setup cost (limit: {self.calc.huim.reduced_number(cost_filter)}), true average profit"
        for _ in range(10):
            if len(calculated_setup_bad_luck_profits) == 0:
                break
            top_minion = max(calculated_setup_bad_luck_profits, key=calculated_setup_bad_luck_profits.get)
            output_str += "\n" + top_minion + ": " + self.calc.huim.reduced_number(calculated_setup_bad_luck_profits[top_minion]) + ", " + self.calc.huim.reduced_number(calculated_setup_costs[top_minion]) + ", " + self.calc.huim.reduced_number(calculated_setup_profits[top_minion])
            del calculated_setup_bad_luck_profits[top_minion]
        if markdown_output:
            output_str += "\n```"
        output_str += "\n"
        if self.calc.output_to_clipboard.get():
            self.calc.clipboard_clear()
            self.calc.clipboard_append(output_str)
        self.calc.huim.logger.info("\n" + output_str)
        self.calc.collect_add_on_output("Inferno Minion Loop", "See terminal")
        return

    def basic_minion_loop_inputs(self):
        self.calc.huim.edit_vars("basic_minion_loop")
        return

    def inferno_minion_loop_inputs(self):
        self.calc.huim.edit_vars("inferno_minion_loop")
        return

    def craft_material_amount(self):
        setup_data = self.calc.huim.get_from_GUI(["minion", "miniontier", "amount", "extracost"])  # TODO: make it get calculated_ID, to stop desync inputs and output
        materials = self.calc.md.minion_cost_sum(setup_data["minion"], setup_data["miniontier"])
        extra_costs_string = setup_data["extracost"]
        materials_string = ", ".join([f"{amount * setup_data["amount"]} {self.calc.md.calculator_data[material]["display"]}" for material, amount in materials.items() if material in self.calc.md.calculator_data])
        if extra_costs_string != "None":
            materials_string += ", " + extra_costs_string
        self.calc.collect_add_on_output("Minion Crafting Materials", materials_string)
        return

    def dragon_pet_xp(self, gained_xp, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item):
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
        drag_lvl_100 = self.calc.md.calculator_data["LEGENDARY"]["max_lvl_pet_xp_amount"]
        drag_lvl_200 = self.calc.md.calculator_data["DRAGON"]["max_lvl_pet_xp_amount"]
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

    def exact_pet_levelling_inputs(self):
        setup_data = self.calc.huim.get_from_GUI(["mayor", "levelingpet", "levelingpet_rarity", "expsharepet", "expsharepetslot2", "expsharepetslot3", "expsharepet_rarity", "expsharepetslot2_rarity", "expsharepetslot3_rarity"])
        if setup_data["levelingpet"] == "NONE":
            self.calc.collect_add_on_output("Exact Pet Levelling", "No pet levelling active")
            return
        setup_pets = { "levelingpet": { "pet": setup_data["levelingpet"], "rarity": setup_data["levelingpet_rarity"], "pet_xp": {}, "levelled_pets": 0.0 } }
        for var_key in ["expsharepet", "expsharepetslot2", "expsharepetslot3"]:
            if setup_data[var_key] == "NONE" or (setup_data["mayor"] != "MAYOR_DIANA" and var_key in ["expsharepetslot2", "expsharepetslot3"]):
                continue
            setup_pets[var_key] = { "pet": setup_data[var_key], "rarity": setup_data[var_key + "_rarity"], "pet_xp": { "exp_share": 0.0 }, "levelled_pets": 0.0 }
        input_variables = {}
        for pet_slot, pet_info in setup_pets.items():
            input_variables[pet_slot + "_starting_pet_xp"] = {"dtype": float, "display": self.calc.md.calculator_data[pet_info["rarity"]]["display"] + " " + self.calc.md.calculator_data[pet_info["pet"]]["display"] + " starting pet xp", "initial": 0, "options": None}
        if "exact_pet_levelling" in self.calc.huim.edit_vars_requests:
            self.calc.huim.edit_vars_requests["exact_pet_levelling"]["frame"].destroy()
        self.calc.huim.new_edit_vars("exact_pet_levelling", input_variables, lambda results, pet_data=setup_pets: self.exact_pet_levelling(results, pet_data))
        self.calc.huim.edit_vars("exact_pet_levelling")
        return

    def exact_pet_levelling(self, results, setup_pets):
        setup_data = self.calc.huim.get_from_GUI(["mayor", "xp", "taming", "toucan_attribute", "expshareitem", "pet_exp_boost", "beastmaster", "falcon_attribute", "bazaar_buy_type", "bazaar_sell_type", "bazaar_taxes", "bazaar_flipper"])
        skill_xp = setup_data["xp"]
        main_pet = setup_pets["levelingpet"]["pet"]
        main_pet_xp = setup_pets["levelingpet"]["pet_xp"]
        if self.calc.md.has_data_tag(main_pet, "dragon_pet"):
            left_over_pet_xp = results["levelingpet_starting_pet_xp"]
            for skill, amount in skill_xp.items():
                pet_xp_boost, xp_boost_pet_item = self.calc.get_pet_xp_boosts(main_pet, skill, setup_data)
                main_pet_xp[skill], left_over_pet_xp = self.dragon_pet_xp(amount, left_over_pet_xp, pet_xp_boost, xp_boost_pet_item)
        else:
            for skill, amount in skill_xp.items():
                pet_xp_boost, xp_boost_pet_item = self.calc.get_pet_xp_boosts(main_pet, skill, setup_data)
                main_pet_xp[skill] = amount * pet_xp_boost * xp_boost_pet_item
        exp_share_boost = 0.2 * setup_data["taming"] + 10 * (setup_data["mayor"] == "MAYOR_DIANA") + setup_data["toucan_attribute"]
        exp_share_item = 15 * setup_data["expshareitem"]
        for pet_slot, pet_info in setup_pets.items():
            if pet_slot == "levelingpet":
                continue
            exp_share_pet = pet_info["pet"]
            if self.calc.md.has_data_tag(exp_share_pet, "dragon_pet"):
                if exp_share_boost == 0:
                    continue
                left_over_pet_xp = results[pet_slot + "_starting_pet_xp"]
                for skill, amount in main_pet_xp.items():
                    non_matching = self.calc.get_pet_xp_boosts(exp_share_pet, skill, setup_data, True)
                    equiv_pet_xp_boost = non_matching * (exp_share_boost / 100)
                    equiv_xp_boost_pet_item = 1 + exp_share_item / exp_share_boost
                    gained_pet_xp, left_over_pet_xp = self.dragon_pet_xp(amount, left_over_pet_xp, equiv_pet_xp_boost, equiv_xp_boost_pet_item)
                    pet_info["pet_xp"]["exp_share"] += gained_pet_xp
            else:
                for skill, amount in main_pet_xp.items():
                    non_matching = self.calc.get_pet_xp_boosts(exp_share_pet, skill, setup_data, True)
                    pet_info["pet_xp"]["exp_share"] += amount * ((exp_share_boost + exp_share_item * (not self.calc.md.has_data_tag(exp_share_pet, "dragon_egg_pet"))) / 100) * non_matching
        for pet_slot, pet_info in setup_pets.items():
            if self.calc.md.has_data_tag(pet_info["pet"], "dragon_pet"):
                max_lvl_pet_xp = self.calc.md.calculator_data["DRAGON"]["max_lvl_pet_xp_amount"]
            elif self.calc.md.has_data_tag(pet_info["pet"], "hatched_dragon_pet"):
                max_lvl_pet_xp = self.calc.md.calculator_data["DRAGON"]["max_lvl_pet_xp_amount"] - self.calc.md.calculator_data["LEGENDARY"]["max_lvl_pet_xp_amount"]
            else:
                max_lvl_pet_xp = self.calc.md.calculator_data[pet_info["rarity"]]["max_lvl_pet_xp_amount"]
            pets_levelled = (results[pet_slot + "_starting_pet_xp"] + sum(pet_info["pet_xp"].values())) / max_lvl_pet_xp
            pet_info["levelled_pets"] = pets_levelled
        output_string = ", ".join([f"{self.calc.huim.reduced_number(pet_info['levelled_pets'], 4)} {self.calc.md.calculator_data[pet_info["rarity"]]["display"]} {self.calc.md.calculator_data[pet_info["pet"]]["display"]}" for pet_info in setup_pets.values()])
        self.calc.collect_add_on_output("Exact Pet Levelling", output_string)
        return

    def collection_maxing_inputs(self):
        self.calc.huim.edit_vars("collection_maxing")
        return

    def collection_maxing(self, results):
        display_name = "Chili Pepper Collection"
        setup_data = self.calc.huim.get_from_GUI(self.calc.ID_order)
        calculated_setup_profits = {}
        calculated_setup_costs = {}
        calculated_collection_max_cost = {}
        calculated_needed_time = {}

        ordering = results["sort_by"]
        ordering_data = {"Fastest Time": calculated_needed_time, "Lowest Setup Cost": calculated_setup_costs, "Lowest Total Cost": calculated_collection_max_cost}[ordering]
        
        cost_filter = results["setup_cost_limit"]
        time_filter = results["time_limit"]
        if cost_filter == 0:
            cost_filter = math.inf
        if time_filter == 0:
            time_filter = math.inf
        minion_amount_limit = results["amount_limit"]
        if minion_amount_limit < 1:
            self.calc.collect_add_on_output(display_name, "Positive minion amount limit is required")
            return
        markdown_output = results["markdown_output"]
        setup_data["minion"] = "INFERNO_MINION"
        setup_data["fuel"] = "INFERNO_FUEL"
        setup_data["inferno_grade"] = "HYPERGOLIC_GABAGOOL"
        setup_data["chest"] = "XXLARGE_ENCHANTED_CHEST"
        setup_data["rising_celsius_override"] = True
        setup_data["sell_form"] = 1
        setup_data["scale_time"] = False
        
        loop_tiers = range(1, 12)
        loop_amounts = range(1, minion_amount_limit + 1)
        for loop_tier in loop_tiers:
            setup_data["miniontier"] = loop_tier
            for loop_amount in loop_amounts:
                setup_data["amount"] = loop_amount
                outputs = self.calc.calculate(setup_data=setup_data, return_outputs=True)
                cost = outputs["setupcost"]
                needed_time_scaling = 10000 / outputs["items"]["CHILI_PEPPER"]
                needed_time = setup_data["empty_time_amount"] * needed_time_scaling
                if cost < cost_filter and needed_time < time_filter:
                    calculated_setup_costs[f"{loop_tier}, {loop_amount}"] = cost
                    calculated_setup_profits[f"{loop_tier}, {loop_amount}"] = needed_time_scaling * outputs["total_profit"]
                    calculated_collection_max_cost[f"{loop_tier}, {loop_amount}"] = cost - needed_time_scaling * outputs["total_profit"]
                    calculated_needed_time[f"{loop_tier}, {loop_amount}"] = needed_time

        if len(calculated_collection_max_cost) == 0:
            self.calc.collect_add_on_output(display_name, "No setups pass the filters")
            return
        setup_data.update(self.calc.decode_id(outputs["calculated_ID"]))
        setup_data.update(outputs)
        setup_data["bazaar_update_txt"] = self.calc.bazaar_update_txt.get()
        output_str = self.calc.text_output(calculation_data=setup_data, output_switches={}, output_order={
                "Upgrades: ": { "": {"fuel", "hopper", "upgrade1", "upgrade2", "chest", "beacon", "crystal", "postcard", "infusion", "free_will"}},
                "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
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
                "": {"": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper", "sell_form"]},
                }, markdown=markdown_output, to_terminal=False)
        if markdown_output:
            output_str += "\n```"
        else:
            output_str += "\n"
        output_str += f"\nTier, Amount (limit: {self.calc.huim.reduced_number(minion_amount_limit)}): max collection cost, time (limit: {self.calc.huim.reduced_number(time_filter)} {setup_data["empty_time_unit"]}), setup cost (limit: {self.calc.huim.reduced_number(cost_filter)}), profit"

        for _ in range(10):
            if len(ordering_data) == 0:
                break
            top_minion = min(ordering_data, key=ordering_data.get)
            output_str += "\n" + top_minion + ": " + self.calc.huim.reduced_number(calculated_collection_max_cost[top_minion]) + ", " + f"{self.calc.huim.reduced_number(calculated_needed_time[top_minion])} {setup_data["empty_time_unit"]}" + ", " + self.calc.huim.reduced_number(calculated_setup_costs[top_minion]) + ", " + self.calc.huim.reduced_number(calculated_setup_profits[top_minion])
            del ordering_data[top_minion]
        if markdown_output:
            output_str += "\n```"
        output_str += f"\nOrdered by: {ordering}"
        if self.calc.output_to_clipboard.get():
            self.calc.clipboard_clear()
            self.calc.clipboard_append(output_str)
        self.calc.huim.logger.info("\n" + output_str)
        self.calc.collect_add_on_output(display_name, "See terminal")
        return

    def partial_setup_cost_inputs(self):
        self.calc.huim.edit_vars("partial_setup_cost")
        return

    def partial_setup_cost(self, results):
        outputs = self.calc.huim.get_from_GUI(["setupcost_breakdown"])
        partial_cost = 0
        used_parts = []
        for setup_part, state in results.items():
            if state and setup_part in outputs["setupcost_breakdown"]:
                partial_cost += outputs["setupcost_breakdown"][setup_part]
                used_parts.append(self.calc.var_dict[setup_part].get_display())
        if len(used_parts) == 0:
            self.calc.collect_add_on_output("Partial Setup Cost", "No setup parts pass the filter")
            return
        self.calc.collect_add_on_output("Partial Setup Cost", self.calc.huim.reduced_number(partial_cost) + " for " + ", ".join(used_parts))
        return

    def calculator_data_debug_inputs(self):
        # This Add-on is inactive, to turn it back on uncomment the add-on in self.add_ons_data in __init__
        self.calc.huim.edit_vars("calculator_data_debug")
        return

    def calculator_data_debug(self, results):
        self.calc.collect_add_on_output("Calculator Data", self.calc.md.get_data(results["data_loc"]))
        return