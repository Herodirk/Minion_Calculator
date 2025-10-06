# -*- coding: utf-8 -*-
"""
@author: Herodirk

Official Minion Calculator Add-ons.
A collection of add-ons made by Herodirk.
"""

import numpy as np
import HSB_minion_data as md


def old_corrupted_frags(calculator):
    # This Add-on is inactive, to turn it back on add this function to `add_ons_package` at the bottom of this file.
    """Outputs the total profit for the old price of Corrupted Fragments"""
    if "CORRUPTED_FRAGMENT" not in calculator.variables["itemtypeProfit"]["list"]:
        calculator.collect_addon_output("Old Corrupted Frag profit", "Setup does not produce Corrupted Fragments")
        return
    corrupted_frag_profit = calculator.variables["itemtypeProfit"]["list"]["CORRUPTED_FRAGMENT"]
    total_profit = calculator.variables["totalProfit"]["var"].get()
    calculator.collect_addon_output("Old Corrupted Frag profit", f"{calculator.reduced_number(total_profit + 19 * corrupted_frag_profit, 2)}")
    return


def bad_luck_inferno(calculator, return_value=False):
    """Outputs the profit of the common Hypergolic drops and the price per Inferno Vertex"""
    if calculator.variables["fuel"]["var"].get() != "Inferno Minion Fuel":
        calculator.collect_addon_output("Bad Luck Inferno", "No Inferno Minion Fuel Found")
        return
    if calculator.variables["infernoGrade"]["var"].get() != "Hypergolic Gabagool":
        calculator.collect_addon_output("Bad Luck Inferno", "No Hypergolic Items Found")
        return
    total_profit = calculator.variables["totalProfit"]["var"].get()
    item_type_profit = calculator.variables["itemtypeProfit"]["list"]
    no_rng_profit = total_profit - item_type_profit["INFERNO_APEX"] - item_type_profit["REAPER_PEPPER"] - item_type_profit["INFERNO_VERTEX"] - item_type_profit["GABAGOOL_THE_FISH"]
    per_vertex = calculator.getPrice("INFERNO_VERTEX", "sell", "bazaar")
    calculator.collect_addon_output("Bad Luck Inferno Profit", f"{calculator.reduced_number(no_rng_profit, 2)} + {calculator.reduced_number(per_vertex, 2)} per Inferno Vertex")
    if return_value:
        return no_rng_profit
    return


def setup_repay_time(calculator):
    """Outputs the time (in days) it take for a setup to repay itself"""
    totaltime = calculator.variables["time_seconds"]["var"].get()
    setupcost = calculator.variables["setupcost"]["var"].get()
    if calculator.variables["free_will"]["var"].get():
        setupcost += calculator.variables["freewillcost"]["var"].get()
    profit = calculator.variables["totalProfit"]["var"].get()
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


def rising_celsius_override(calculator, inGUI=True):
    """Forces the rising celsius boost to max"""
    calculator.rising_celsius_override = True
    calculator.calculate()
    if inGUI:
        calculator.update_GUI()
        calculator.collect_addon_output("Rising Celsius Override", "Forced Rising Celsius boost to max")
        pass
    calculator.rising_celsius_override = False
    return


def basic_minion_loop(calculator):
    calculated_setup_profits = {}
    calculated_setup_costs = {}
    loop_minion_options = list(md.minionList.keys())
    loop_minion_skip = ["Custom"]
    loop_minion_smelting = ["Iron", "Gold", "Cactus"]
    loop_minion_combat = ["Zombie", "Revenant", "Voidling", "Inferno", "Vampire", "Skeleton", "Creeper", "Spider", "Tarantula", "Cave Spider", "Blaze", "Magma Cube", "Enderman", "Ghast", "Slime", "Cow", "Pig", "Chicken", "Sheep", "Rabbit"]
    super_compactor = False
    if calculator.variables["upgrade1"]["var"].get() in ["Super Compactor 3000", "Dwarven Super Compactor"]:
        super_compactor = True
    if calculator.variables["upgrade2"]["var"].get() in ["Super Compactor 3000", "Dwarven Super Compactor"]:
        super_compactor = True
        calculator.variables["upgrade2"]["var"].set(calculator.variables["upgrade1"]["var"].get())
        calculator.variables["upgrade1"]["var"].set("Super Compactor 3000")
    
    upgrades = [calculator.variables["upgrade1"]["var"].get(), calculator.variables["upgrade2"]["var"].get()]
    for loop_minion in loop_minion_options:
        if loop_minion in loop_minion_skip:
            continue
        if loop_minion not in loop_minion_combat and "Corrupt Soil" in upgrades:
            continue
        calculator.variables["minion"]["var"].set(loop_minion)
        calculator.multiswitch(multi_ID="minion", control=loop_minion)
        if super_compactor:
            if loop_minion in loop_minion_smelting:
                calculator.variables["upgrade1"]["var"].set("Dwarven Super Compactor")
            else:
                calculator.variables["upgrade1"]["var"].set("Super Compactor 3000")
        calculator.calculate()
        calculated_setup_profits[loop_minion] = calculator.variables["totalProfit"]["var"].get()
        calculated_setup_costs[loop_minion] = calculator.variables["setupcost"]["var"].get()
        if calculator.variables["free_will"]["var"].get():
            calculated_setup_costs[loop_minion] += calculator.variables["freewillcost"]["var"].get()
    print("Minion : profit , setup cost")
    for _ in range(10):
        top_minion = max(calculated_setup_profits, key=calculated_setup_profits.get)
        print(top_minion, ":", calculator.reduced_number(calculated_setup_profits[top_minion]), ",", calculator.reduced_number(calculated_setup_costs[top_minion]))
        del calculated_setup_profits[top_minion]
    print("\n")
    calculator.collect_addon_output("Basic Minion Loop", "See terminal")
    return


def inferno_minion_loop(calculator):
    calculated_setup_profits = {}
    calculated_setup_bad_luck_profits = {}
    calculated_setup_costs = {}

    cost_filter = 6000000000
    # input the full number as filter, so no abbreviations like "6B"
    # saving this file and restarting the calculator is needed to apply changes.
    # will make this into a good working input in the GUI later.

    calculator.variables["minion"]["var"].set("Inferno")
    calculator.variables["fuel"]["var"].set("Inferno Minion Fuel")
    calculator.variables["chest"]["var"].set("XX-Large")

    loop_tiers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    loop_amounts = list(np.arange(1, 32))
    for loop_tier in loop_tiers:
        calculator.variables["miniontier"]["var"].set(loop_tier)
        for loop_amount in loop_amounts:
            calculator.variables["amount"]["var"].set(loop_amount)
            rising_celsius_override(calculator, False)
            bad_luck_profit = bad_luck_inferno(calculator, return_value=True)
            cost = calculator.variables["setupcost"]["var"].get()
            if calculator.variables["free_will"]["var"].get():
                cost += calculator.variables["freewillcost"]["var"].get()
            if cost < cost_filter:
                calculated_setup_costs[f"{loop_tier}, {loop_amount}"] = cost
                calculated_setup_profits[f"{loop_tier}, {loop_amount}"] = calculator.variables["totalProfit"]["var"].get()
                calculated_setup_bad_luck_profits[f"{loop_tier}, {loop_amount}"] = bad_luck_profit
    print("Tier, Amount : bad luck profit , minion cost, true average profit")
    for _ in range(10):
        top_minion = max(calculated_setup_bad_luck_profits, key=calculated_setup_bad_luck_profits.get)
        print(top_minion, ":", calculator.reduced_number(calculated_setup_bad_luck_profits[top_minion]), ",", calculator.reduced_number(calculated_setup_costs[top_minion]), ",", calculator.reduced_number(calculated_setup_profits[top_minion]))
        del calculated_setup_bad_luck_profits[top_minion]
    print(f"Bad Luck Profit: + {calculator.reduced_number(calculator.getPrice('INFERNO_VERTEX', 'sell', 'bazaar'), 2)} per Inferno Vertex")
    print("\n")
    calculator.collect_addon_output("Inferno Minion Loop", "See terminal")
    return


def craft_material_amount(calculator):
    minion = calculator.variables["minion"]["var"].get()
    tier = calculator.variables["miniontier"]["var"].get()
    minion_amount = calculator.variables["amount"]["var"].get()
    materials = md.minionCostSum(minion, tier)
    extra_costs_string = calculator.variables["extracost"]["var"].get()
    materials_string = ", ".join([f"{amount * minion_amount} {md.itemList[material]["display"]}" for material, amount in materials.items()])
    if len(extra_costs_string) != 0:
        materials_string += ", " + extra_costs_string
    calculator.collect_addon_output("Minion Crafting Materials", materials_string)
    return


add_ons_package = {"Minion Crafting": craft_material_amount, "Days to Repay Setup": setup_repay_time, "Basic Minion Loop": basic_minion_loop, "Bad Luck Inferno": bad_luck_inferno, "Rising Celsius Override": rising_celsius_override, "Inferno Minion Loop": inferno_minion_loop}
# "Old Corrupted Frags": old_corrupted_frags
