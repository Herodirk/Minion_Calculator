@author: Herodirk

Main file for the minion calculator.
Notable features:
    near infinite customizable setup
    Corrupt soil calculations
    Inferno minions calculations
    Pet leveling calculations
    Setup cost calculations
Visit https://herodirk.github.io/ for an online manual.
To open the calculator: run this file, run the function start_app()

Current major limitations:
    (Lesser) Soulflow Engines might not be accurate (there seems to be some weird rounding in game)
    Inferno drop chances might be unaccurate (in game Hypixel seem to have higher chances)
    Item prices from AH (like pets and Everburning Flame) have to be updated manually
    Unknown average wool amount from Enchanted Shears
    For offline calculations of mob minions: Hypixel takes 5 actions to spawn in mobs, this calculator does not account for that
    Dyes (Byzantium and Flame) are included in the base drops of their minions, but they should only be there if the player harvests
Lesser limitations are listed on the support discord server,
the invite to that server is at the bottom of https://herodirk.github.io/

This program and related files (Hkinter.py and HSB_minion_data.py) are protected under a GNU GENERAL PUBLIC LICENSE (Version 3)
Herodirk: I dont want any legal trouble, just ask me for permission if you want to copy parts of the code for your own public projects. Copying for private projects is fine.
