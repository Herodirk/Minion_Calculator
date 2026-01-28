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
import HSB_minion_data as md


def old_corrupted_frags(calculator):
    # This Add-on is inactive, to turn it back on add this function to `add_ons_package` at the bottom of this file.
    """Outputs the total profit for the old price of Corrupted Fragments"""
    if "CORRUPTED_FRAGMENT" not in calculator.itemtype_profit.list:
        calculator.collect_addon_output("Old Corrupted Frag profit", "Setup does not produce Corrupted Fragments")
        return
    corrupted_frag_profit = calculator.itemtype_profit.list["CORRUPTED_FRAGMENT"]
    total_profit = calculator.total_profit.get()
    calculator.collect_addon_output("Old Corrupted Frag profit", f"{calculator.reduced_number(total_profit + 19 * corrupted_frag_profit, 2)}")
    return


def old_enchanted_hopper(calculator):
    # This Add-on is inactive, to turn it back on add this function to `add_ons_package` at the bottom of this file.
    """Outputs the total profit for the old sell rate of Enchanted Hoppers"""
    if calculator.hopper.get() != "Enchanted Hopper" or calculator.sell_loc.get() != "Hopper":
        calculator.collect_addon_output("Old Enchanted Hopper profit", "Setup does not use Enchanted Hoppers")
        return
    profit = calculator.total_profit.get()
    calculator.collect_addon_output("Old Enchanted Hopper profit", f"{calculator.reduced_number(profit * (9 / 7), 2)}")
    return


def bad_luck_inferno(calculator, setup_data=None, outputs=None, return_value=False):
    """Outputs the profit of the common Hypergolic drops and the price per Inferno Vertex"""
    if setup_data is None:
        setup_data = calculator.get_from_GUI(["fuel", "inferno_grade", "bazaar_buy_type", "bazaar_sell_type", "bazaar_taxes", "bazaar_flipper", "mayor"])
        outputs = calculator.get_from_GUI(["total_profit", "itemtype_profit"])
    if setup_data["fuel"] != "INFERNO_FUEL":
        calculator.collect_addon_output("Bad Luck Inferno", "No Inferno Minion Fuel Found")
        return
    if setup_data["inferno_grade"] != "Hypergolic Gabagool":
        calculator.collect_addon_output("Bad Luck Inferno", "No Hypergolic Items Found")
        return
    total_profit = outputs["total_profit"]
    item_type_profit = outputs["itemtype_profit"]
    no_rng_profit = total_profit - item_type_profit["INFERNO_APEX"] - item_type_profit["REAPER_PEPPER"] - item_type_profit["INFERNO_VERTEX"] - item_type_profit["GABAGOOL_THE_FISH"]
    per_vertex = calculator.get_price("INFERNO_VERTEX", setup_data, "sell", "bazaar")
    if return_value:
        return no_rng_profit
    calculator.collect_addon_output("Bad Luck Inferno Profit", f"{calculator.reduced_number(no_rng_profit, 2)} + {calculator.reduced_number(per_vertex, 2)} per Inferno Vertex")
    return


def setup_repay_time(calculator):
    """Outputs the time (in days) it take for a setup to repay itself"""
    setup_data = calculator.get_from_GUI(["time_seconds", "setupcost", "free_will", "freewillcost", "total_profit", "bazaar_taxes", "bazaar_flipper", "mayor"])
    totaltime = setup_data["time_seconds"]
    setupcost = setup_data["setupcost"]
    if setup_data["free_will"]:
        setupcost += setup_data["freewillcost"]
    profit = setup_data["total_profit"]
    if profit < 0:
        calculator.collect_addon_output("Setup Repay Time", "Negative profit, cannot repay")
        return
    try:
        profitpersecond = profit / totaltime
        repay_time_s = setupcost / profitpersecond
    except ZeroDivisionError:
        calculator.collect_addon_output("Setup Repay Time", "Division by zero")
        return
    repay_time = np.round(repay_time_s / 86400, 2)
    calculator.collect_addon_output("Setup Repay Time", f"{repay_time} Days")
    return


def basic_minion_loop(calculator):
    setup_data = calculator.get_from_GUI(calculator.ID_order)
    calculated_setup_profits = {}
    calculated_setup_costs = {}
    loop_minion_options = list(md.minionList.keys())
    loop_minion_skip = ["Custom"]
    loop_minion_smelting = ["Iron", "Gold", "Cactus"]
    loop_minion_combat = ["Zombie", "Revenant", "Voidling", "Inferno", "Vampire", "Skeleton", "Creeper", "Spider", "Tarantula", "Cave Spider", "Blaze", "Magma Cube", "Enderman", "Ghast", "Slime", "Cow", "Pig", "Chicken", "Sheep", "Rabbit"]
    super_compactor = False
    if setup_data["upgrade1"] in ["Super Compactor 3000", "Dwarven Super Compactor"]:
        super_compactor = True
    if setup_data["upgrade2"] in ["Super Compactor 3000", "Dwarven Super Compactor"]:
        super_compactor = True
        setup_data["upgrade2"] = setup_data["upgrade1"]
        setup_data["upgrade1"] = "Super Compactor 3000"
    
    upgrades = [setup_data["upgrade1"], setup_data["upgrade2"]]
    for loop_minion in loop_minion_options:
        if loop_minion in loop_minion_skip:
            continue
        if loop_minion not in loop_minion_combat and "Corrupt Soil" in upgrades:
            continue
        setup_data["minion"] = loop_minion
        setup_data["miniontier"] = list(md.minionList[setup_data["minion"]]["speed"].keys())[-1]
        if super_compactor:
            if loop_minion in loop_minion_smelting:
                setup_data["upgrade1"] = "Dwarven Super Compactor"
            else:
                setup_data["upgrade1"] = "Super Compactor 3000"
        outputs = calculator.calculate(setup_data=setup_data, return_outputs=True)

        calculated_setup_profits[loop_minion] = outputs["total_profit"]
        calculated_setup_costs[loop_minion] = outputs["setupcost"]
        # if setup_data["free_will"]:
        #     calculated_setup_costs[loop_minion] += outputs["freewillcost"]
    print("Minion : profit , setup cost")
    for _ in range(10):
        top_minion = max(calculated_setup_profits, key=calculated_setup_profits.get)
        print(top_minion, ":", calculator.reduced_number(calculated_setup_profits[top_minion]), ",", calculator.reduced_number(calculated_setup_costs[top_minion]))
        del calculated_setup_profits[top_minion]
    print("\n")
    calculator.collect_addon_output("Basic Minion Loop", "See terminal")
    return


def inferno_minion_loop(calculator):
    setup_data = calculator.get_from_GUI(calculator.ID_order)
    calculated_setup_profits = {}
    calculated_setup_bad_luck_profits = {}
    calculated_setup_costs = {}

    cost_filter = 6000000000
    # input the full number as filter, so no abbreviations like "6B"
    # saving this file and restarting the calculator is needed to apply changes.
    # will make this into a good working input in the GUI later.

    setup_data["minion"] = "Inferno"
    setup_data["fuel"] = "INFERNO_FUEL"
    setup_data["chest"] = "XX-Large"
    setup_data["rising_celsius_override"] = True

    loop_tiers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    loop_amounts = list(np.arange(1, 32))
    for loop_tier in loop_tiers:
        setup_data["miniontier"] = loop_tier
        for loop_amount in loop_amounts:
            setup_data["amount"] = loop_amount
            outputs = calculator.calculate(setup_data=setup_data, return_outputs=True)
            bad_luck_profit = bad_luck_inferno(calculator, setup_data=setup_data, outputs=outputs, return_value=True)
            cost = outputs["setupcost"]
            # if setup_data["free_will"]:
            #     cost += outputs["freewillcost"]
            if cost < cost_filter:
                calculated_setup_costs[f"{loop_tier}, {loop_amount}"] = cost
                calculated_setup_profits[f"{loop_tier}, {loop_amount}"] = outputs["total_profit"]
                calculated_setup_bad_luck_profits[f"{loop_tier}, {loop_amount}"] = bad_luck_profit
    print("Tier, Amount : bad luck profit , minion cost, true average profit")
    for _ in range(10):
        top_minion = max(calculated_setup_bad_luck_profits, key=calculated_setup_bad_luck_profits.get)
        print(top_minion, ":", calculator.reduced_number(calculated_setup_bad_luck_profits[top_minion]), ",", calculator.reduced_number(calculated_setup_costs[top_minion]), ",", calculator.reduced_number(calculated_setup_profits[top_minion]))
        del calculated_setup_bad_luck_profits[top_minion]
    print(f"Bad Luck Profit: + {calculator.reduced_number(calculator.get_price('INFERNO_VERTEX', setup_data, 'sell', 'bazaar'), 2)} per Inferno Vertex")
    print("\n")
    calculator.collect_addon_output("Inferno Minion Loop", "See terminal")
    return


def craft_material_amount(calculator):
    setup_data = calculator.get_from_GUI(["minion", "miniontier", "amount", "extracost"])
    materials = md.minionCostSum(setup_data["minion"], setup_data["miniontier"])
    extra_costs_string = setup_data["extracost"]
    materials_string = ", ".join([f"{amount * setup_data["amount"]} {md.itemList[material]["display"]}" for material, amount in materials.items()])
    if len(extra_costs_string) != 0:
        materials_string += ", " + extra_costs_string
    calculator.collect_addon_output("Minion Crafting Materials", materials_string)
    return


add_ons_package = {"Minion Crafting": craft_material_amount, "Days to Repay Setup": setup_repay_time, "Basic Minion Loop": basic_minion_loop, "Bad Luck Inferno": bad_luck_inferno, "Inferno Minion Loop": inferno_minion_loop}
# "Old Corrupted Frags": old_corrupted_frags
# "Old Enchanted Hopper": old_enchanted_hopper
