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
import HSB_minion_data as md


def old_corrupted_frags(calculator):
    # This Add-on is inactive, to turn it back on add this function to `add_ons_package` at the bottom of this file.
    """Outputs the total profit for the old price of Corrupted Fragments"""
    if "CORRUPTED_FRAGMENT" not in calculator.itemtype_profit.list:
        calculator.collect_addon_output("Old Corrupted Frag profit", "Setup does not produce Corrupted Fragments")
        return
    corrupted_frag_profit = calculator.itemtype_profit.list["CORRUPTED_FRAGMENT"]
    total_profit = calculator.total_profit.get()
    calculator.collect_addon_output("Old Corrupted Frag profit", f"{calculator.huim.reduced_number(total_profit + 19 * corrupted_frag_profit, 2)}")
    return


def old_enchanted_hopper(calculator):
    # This Add-on is inactive, to turn it back on add this function to `add_ons_package` at the bottom of this file.
    """Outputs the total profit for the old sell rate of Enchanted Hoppers"""
    if calculator.hopper.get() != "Enchanted Hopper" or calculator.sell_loc.get() != "Hopper":
        calculator.collect_addon_output("Old Enchanted Hopper profit", "Setup does not use Enchanted Hoppers")
        return
    profit = calculator.total_profit.get()
    calculator.collect_addon_output("Old Enchanted Hopper profit", f"{calculator.huim.reduced_number(profit * (9 / 7), 2)}")
    return


def bad_luck_inferno(calculator, setup_data=None, outputs=None, return_value=False):
    """Outputs the profit of the common Hypergolic drops and the price per Inferno Vertex"""
    if setup_data is None:
        setup_data = calculator.huim.get_from_GUI(["fuel", "inferno_grade", "bazaar_buy_type", "bazaar_sell_type", "bazaar_taxes", "bazaar_flipper", "mayor"])
        outputs = calculator.huim.get_from_GUI(["total_profit", "itemtype_profit", "harvests"])
    if setup_data["fuel"] != "INFERNO_FUEL":
        calculator.collect_addon_output("Bad Luck Inferno", "No Inferno Minion Fuel Found")
        return
    total_profit = outputs["total_profit"]
    if setup_data["inferno_grade"] != "HYPERGOLIC_GABAGOOL":
        if return_value:
            return total_profit
        calculator.collect_addon_output("Bad Luck Inferno", "No Hypergolic Items Found")
        return
    item_type_profit = outputs["itemtype_profit"]
    no_rng_profit_average = total_profit - item_type_profit["INFERNO_APEX"] - item_type_profit["REAPER_PEPPER"] - item_type_profit["GABAGOOL_THE_FISH"]
    if return_value:
        return no_rng_profit_average
    prediction_interval_size = 1.96  # for 95% of cases within the interval, https://en.wikipedia.org/wiki/Prediction_interval#Known_mean,_known_variance
    interval_radius_vertex_amount = prediction_interval_size * math.sqrt(outputs["harvests"] * md.inferno_fuel_data["drops"]["INFERNO_VERTEX"] * (1 - md.inferno_fuel_data["drops"]["INFERNO_VERTEX"]))
    per_vertex = calculator.get_price("INFERNO_VERTEX", setup_data, "sell", "bazaar")
    interval_min = no_rng_profit_average - per_vertex * interval_radius_vertex_amount
    interval_max = no_rng_profit_average + per_vertex * interval_radius_vertex_amount
    calculator.collect_addon_output("Bad Luck Inferno Profit", f"average: {calculator.huim.reduced_number(no_rng_profit_average, 2)}, 95% of cases: {calculator.huim.reduced_number(interval_min, 2)} -- {calculator.huim.reduced_number(interval_max, 2)}, average (no Vertexes): {calculator.huim.reduced_number(no_rng_profit_average - item_type_profit["INFERNO_VERTEX"], 2)}")
    return


def setup_repay_time(calculator):
    """Outputs the time (in days) it take for a setup to repay itself"""
    setup_data = calculator.huim.get_from_GUI(["time_seconds", "setupcost", "free_will", "freewillcost", "total_profit"])
    setupcost = setup_data["setupcost"]
    profit = setup_data["total_profit"]
    if profit < 0:
        calculator.collect_addon_output("Setup Repay Time", "Negative profit, cannot repay")
        return
    try:
        profitpersecond = profit / setup_data["time_seconds"]
        repay_time_s = setupcost / profitpersecond
    except ZeroDivisionError:
        calculator.collect_addon_output("Setup Repay Time", "Division by zero")
        return
    repay_time = np.round(repay_time_s / 86400, 2)
    calculator.collect_addon_output("Setup Repay Time", f"{repay_time} Days")
    return


def basic_minion_loop(calculator):
    setup_data = calculator.huim.get_from_GUI(calculator.ID_order)
    cost_filter = calculator.huim.edit_vars_output["setup_cost_limit"].get()
    if cost_filter == 0:
        cost_filter = math.inf
    markdown_output = calculator.huim.edit_vars_output["markdown_output"].get()
    calculated_setup_profits = {}
    calculated_setup_costs = {}
    loop_minion_options = list(md.minion_options.values())
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
        if "CORRUPT_SOIL" in upgrades and not md.has_data_tag(loop_minion, "mob_minion"):
            continue
        setup_data["minion"] = loop_minion
        setup_data["miniontier"] = list(md.calculator_data[setup_data["minion"]]["speed"].keys())[-1]
        if super_compactor:
            if loop_minion in loop_minion_smelting:
                setup_data["upgrade1"] = "DWARVEN_COMPACTOR"
            else:
                setup_data["upgrade1"] = "SUPER_COMPACTOR_3000"
        outputs = calculator.calculate(setup_data=setup_data, return_outputs=True)

        if outputs["setupcost"] < cost_filter:
            calculated_setup_profits[loop_minion] = outputs["total_profit"]
            calculated_setup_costs[loop_minion] = outputs["setupcost"]
    if len(calculated_setup_profits) == 0:
        calculator.collect_addon_output("Basic Minion Loop", "No setups pass the cost filter")
        return
    setup_data.update(calculator.decode_id(outputs["calculated_ID"]))
    setup_data["used_pet_prices"] = outputs["used_pet_prices"]
    setup_data["bazaar_update_txt"] = calculator.bazaar_update_txt.get()
    output_str = calculator.text_output(calculation_data=setup_data, output_switches={}, output_order={
            "amount": None,
            "Upgrades: ": { "": {"fuel", "hopper", "upgrade1", "upgrade2", "chest", "beacon", "crystal", "postcard", "infusion", "free_will"}},
            "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
            "Inferno Info": {"\n> ": ["inferno_grade", "inferno_distillate", "inferno_eyedrops", "rising_celsius_override"]},
            "afk": {"\n> ": ["afkpet", "afkpet_rarity", "afkpet_lvl", "enchanted_clock", "special_layout", "potato_accessory"]},
            "player_harvests": {"\n> ": ["player_looting"]},
            "Wisdoms": {"\n> ": ["combat_wisdom", "mining_wisdom", "farming_wisdom", "fishing_wisdom", "foraging_wisdom", "alchemy_wisdom"]},
            "mayor": None,
            "levelingpet": {
                "\n> ": ["taming", "falcon_attribute", "petxpboost", "beastmaster", "toucan_attribute", "expshareitem"],
                "\n> Exp Share Pets: ": {"expsharepet", "expsharepetslot2", "expsharepetslot3"}
            },
            "used_pet_prices": None,
            "": {"": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper"]},
            }, markdown=markdown_output, to_terminal=False)
    if markdown_output:
        output_str += "\n```"
    else:
        output_str += "\n"
    output_str += f"\nMinion: profit, setup cost (limit: {calculator.huim.reduced_number(cost_filter)})"
    for _ in range(10):
        if len(calculated_setup_profits) == 0:
            break
        top_minion = max(calculated_setup_profits, key=calculated_setup_profits.get)
        output_str += "\n" + md.calculator_data[top_minion]["display"] + ": " + calculator.huim.reduced_number(calculated_setup_profits[top_minion]) + ", " + calculator.huim.reduced_number(calculated_setup_costs[top_minion])
        del calculated_setup_profits[top_minion]
    if markdown_output:
        output_str += "\n```"
    output_str += "\n"
    if calculator.output_to_clipboard.get():
        calculator.clipboard_clear()
        calculator.clipboard_append(output_str)
    calculator.huim.logger.info("\n" + output_str)
    calculator.collect_addon_output("Basic Minion Loop", "See terminal")
    return


def inferno_minion_loop(calculator):
    setup_data = calculator.huim.get_from_GUI(calculator.ID_order)
    calculated_setup_profits = {}
    calculated_setup_bad_luck_profits = {}
    calculated_setup_costs = {}

    cost_filter = calculator.huim.edit_vars_output["setup_cost_limit"].get()
    if cost_filter == 0:
        cost_filter = math.inf
    minion_amount_limit = calculator.huim.edit_vars_output["amount_limit"].get()
    if minion_amount_limit < 1:
        calculator.collect_addon_output("Inferno Minion Loop", "Positive minion amount limit is required")
        return
    markdown_output = calculator.huim.edit_vars_output["markdown_output"].get()
    setup_data["minion"] = "INFERNO_MINION"
    setup_data["fuel"] = "INFERNO_FUEL"
    setup_data["chest"] = "XXLARGE_ENCHANTED_CHEST"
    setup_data["rising_celsius_override"] = True

    loop_tiers = range(1, 12)
    loop_amounts = range(1, minion_amount_limit + 1)
    for loop_tier in loop_tiers:
        setup_data["miniontier"] = loop_tier
        for loop_amount in loop_amounts:
            setup_data["amount"] = loop_amount
            outputs = calculator.calculate(setup_data=setup_data, return_outputs=True)
            bad_luck_profit = bad_luck_inferno(calculator, setup_data=setup_data, outputs=outputs, return_value=True)
            cost = outputs["setupcost"]
            if cost < cost_filter:
                calculated_setup_costs[f"{loop_tier}, {loop_amount}"] = cost
                calculated_setup_profits[f"{loop_tier}, {loop_amount}"] = outputs["total_profit"]
                calculated_setup_bad_luck_profits[f"{loop_tier}, {loop_amount}"] = bad_luck_profit
    if len(calculated_setup_bad_luck_profits) == 0:
        calculator.collect_addon_output("Inferno Minion Loop", "No setups pass the cost filter")
        return
    setup_data.update(calculator.decode_id(outputs["calculated_ID"]))
    setup_data["used_pet_prices"] = outputs["used_pet_prices"]
    setup_data["bazaar_update_txt"] = calculator.bazaar_update_txt.get()
    output_str = calculator.text_output(calculation_data=setup_data, output_switches={}, output_order={
            "Upgrades: ": { "": {"fuel", "hopper", "upgrade1", "upgrade2", "chest", "beacon", "crystal", "postcard", "infusion", "free_will"}},
            "Beacon Info": {"\n> ": ["scorched", "B_constant", "B_acquired"]},
            "Inferno Info": {"\n> ": ["inferno_grade", "inferno_distillate", "inferno_eyedrops", "rising_celsius_override"]},
            "afk": {"\n> ": ["afkpet", "afkpet_rarity", "afkpet_lvl", "enchanted_clock", "special_layout", "potato_accessory"]},
            "player_harvests": {"\n> ": ["player_looting"]},
            "Wisdoms": {"\n> ": ["combat_wisdom", "mining_wisdom", "farming_wisdom", "fishing_wisdom", "foraging_wisdom", "alchemy_wisdom"]},
            "mayor": None,
            "levelingpet": {
                "\n> ": ["taming", "falcon_attribute", "petxpboost", "beastmaster", "toucan_attribute", "expshareitem"],
                "\n> Exp Share Pets: ": {"expsharepet", "expsharepetslot2", "expsharepetslot3"}
            },
            "used_pet_prices": None,
            "": {"": ["sell_loc", "bazaar_update_txt", "bazaar_sell_type", "bazaar_buy_type", "bazaar_taxes", "bazaar_flipper"]},
            }, markdown=markdown_output, to_terminal=False)
    if markdown_output:
        output_str += "\n```"
    else:
        output_str += "\n"
    output_str += f"\nTier, Amount (limit: {calculator.huim.reduced_number(minion_amount_limit)}): bad luck profit, setup cost (limit: {calculator.huim.reduced_number(cost_filter)}), true average profit"
    for _ in range(10):
        if len(calculated_setup_bad_luck_profits) == 0:
            break
        top_minion = max(calculated_setup_bad_luck_profits, key=calculated_setup_bad_luck_profits.get)
        output_str += "\n" + top_minion + ": " + calculator.huim.reduced_number(calculated_setup_bad_luck_profits[top_minion]) + ", " + calculator.huim.reduced_number(calculated_setup_costs[top_minion]) + ", " + calculator.huim.reduced_number(calculated_setup_profits[top_minion])
        del calculated_setup_bad_luck_profits[top_minion]
    if markdown_output:
        output_str += "\n```"
    output_str += "\n"
    if calculator.output_to_clipboard.get():
        calculator.clipboard_clear()
        calculator.clipboard_append(output_str)
    calculator.huim.logger.info("\n" + output_str)
    calculator.collect_addon_output("Inferno Minion Loop", "See terminal")
    return

def basic_minion_loop_inputs(calculator):
    calculator.huim.edit_vars(lambda: basic_minion_loop(calculator), {"setup_cost_limit": {"dtype": float, "display": "Setup Cost Limit", "initial": 0, "options": None}, "markdown_output": {"dtype": bool, "display": "Markdown Output", "initial": True, "options": None}}, False)
    return

def inferno_minion_loop_inputs(calculator):
    calculator.huim.edit_vars(lambda: inferno_minion_loop(calculator), {"setup_cost_limit": {"dtype": float, "display": "Setup Cost Limit", "initial": 0, "options": None}, "amount_limit": {"dtype": int, "display": "Minion Amount Limit", "initial": 32, "options": None}, "markdown_output": {"dtype": bool, "display": "Markdown Output", "initial": True, "options": None}}, False)
    return

def craft_material_amount(calculator):
    setup_data = calculator.huim.get_from_GUI(["minion", "miniontier", "amount", "extracost"])
    materials = md.minionCostSum(setup_data["minion"], setup_data["miniontier"])
    extra_costs_string = setup_data["extracost"]
    materials_string = ", ".join([f"{amount * setup_data["amount"]} {md.calculator_data[material]["display"]}" for material, amount in materials.items()])
    if len(extra_costs_string) != 0:
        materials_string += ", " + extra_costs_string
    calculator.collect_addon_output("Minion Crafting Materials", materials_string)
    return


add_ons_package = {"Minion Crafting": craft_material_amount, "Days to Repay Setup": setup_repay_time, "Basic Minion Loop": basic_minion_loop_inputs, "Bad Luck Inferno": bad_luck_inferno, "Inferno Minion Loop": inferno_minion_loop_inputs}
# "Old Corrupted Frags": old_corrupted_frags
# "Old Enchanted Hopper": old_enchanted_hopper
