# Gameplay loop
#   1. Boot up introduction, and main menu
#      Prompt user for which option to choose
#       1. Start game
#       2. Load game using .txt file
#       3. Options
#           - Edit field
#           - adjust spawning frequency
#           - change game mode
#       4. Quit (terminate program)
#   2. Start Game
#       a. Start new game using default game variables
#           - Takes into account changes made in options menu
#           - skipped if user loads game
#       b. show map
#           - During the first turn, no monsters are on the map
#       c. combat menu
#           0. Cheat mode
#               - gives gold and allows defenders to 1 hit
#           1. buy unit
#               - archer
#               - wall
#               - cannon ( Fires on odd turns only)
#               - ronin ( Can only attack monsters directly in front)
#           2. upgrade unit
#               - upgrade cost is cost of unit + 2 * number of times it has been upgraded
#               - scan for any ally unit on field , else return to combat menu
#                   - archer upgrade -> Stats +1
#                   - wall upgrade -> HP + 5
#                   - canon upgrade -> Stats +1, +10% chance to knock monster 1 space
#                   - ronin upgrade -> Stats +1, +1 Range
#           3 end turn
#           4. save game
#               - Opens .txt file and writes game_vars & field
#           5. Spells
#               - fireball 3x3
#               - healing circle
#           6. quit (terminate program)
#   3. End turn (Print all actions taken between turns)
#       a. calculate end of turn variables
#           - gold, turn
#       b. Process defender actions
#           a. check if defender is in same row as monster
#           b. if true, calculate damage dealt
#           c. update the monster current health
#               - if it is a skeleton, receive half damage from archer
#           d. if monster health <= 0, then remove from field
#       c. Process monster movement
#           - monsters will move equal to their movement speed towards left
#           - if there is a mob / unit in front, only walk up and end monster turn
#           - if defender unit is directly in front, deal damage to defender
#               - if defender health <= 0, then remove from field
#           - if monster goes off the left field, player loses the game
#       d. update danger and threat levels
#           - spawn new monsters every 2 rounds
#           - I did this because the game felt too easy with the original
#             where only 1 monster spawn when a monster dies
#   4. show the main map (cycle starts again from 2b)
# ----------------------------------------------------------------------------------#


# 0 Upon booting up the game, import necessary modules
import random
import math
import json

# 0.1 Game variables
game_vars = {
    "turn": 0,  # Current Turn
    "monster_kill_target": 20,  # kills needed to win game
    "monsters_killed": 0,  # monsters killed so far
    "num_monsters": 0,  # monsters on the field
    "spawn_frequency": 3,  # turns between each monster spawning naturally
    "gold": 15,  # gold held
    "THREAT": 0,  # current threat metre level
    "max_threat": 10,  # length of threat metre
    "danger_level": 1,  # rate at which danger increases
    "DANGER": 1,  # DANGER level
    "columns": 7,  # number of columns in the field
    "rows": 5,  # number of rows in the field
    "first_time_shop": 1,  # Detects if it is first time showing the shop
    "first_time_spell_shop": 1,  # Detects if it is first time showing spells
    "game_mode": 0,  # game modes normal = 0, endless = 1
    "options_changed": 0,  # options changed = False = 0 , options changed = True = 1
}

row_name = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
field = [[None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None]]

# Monster and Defender Data
defender_list = ['ARCHR', 'WALL', 'CANON', 'RONIN']
monster_list = ['ZOMBI', 'WWOLF', 'SKELE']
defenders = {'ARCHR': {'NAME': 'Archer',
                       'maxHP': 6,
                       'min_damage': 2,
                       'max_damage': 4,
                       'PRICE': 5,
                       },
             'WALL': {'NAME': 'Wall',
                      'maxHP': 20,
                      'min_damage': 0,
                      'max_damage': 0,
                      'PRICE': 3,
                      },
             'CANON': {'NAME': 'Cannon',
                       'maxHP': 8,
                       'min_damage': 3,
                       'max_damage': 6,
                       'PRICE': 7,
                       },
             'RONIN': {'NAME': 'Ronin',
                       'maxHP': 10,
                       'min_damage': 5,
                       'max_damage': 8,
                       'PRICE': 5,
                       },
             }

monsters = {'ZOMBI': {'NAME': 'Zombie',
                      'maxHP': 15,
                      'min_damage': 3,
                      'max_damage': 6,
                      'MOVES': 3,
                      'REWARD': 3
                      },
            'WWOLF': {'NAME': 'Werewolf',
                      'maxHP': 10,
                      'min_damage': 1,
                      'max_damage': 4,
                      'MOVES': 2,
                      'REWARD': 4
                      },
            'SKELE': {'NAME': 'Skeleton',
                      'maxHP': 10,
                      'min_damage': 1,
                      'max_damage': 3,
                      'MOVES': 1,
                      'REWARD': 4
                      },
            }


# place_unit()
#    Places a unit at the given position
#    This function works for both defender and monster
#    Returns False if the position is invalid
#       - Position is not on the field of play
#       - Position is occupied
#       - Defender is placed past the first 3 columns
#    Returns True if placement is successful

def place_unit(position, unit_name):
    # check if the position is valid
    # note that units of any type can be placed into any row , check row validity
    if position[0].isalpha() is True and position[0].upper() in row_name[:game_vars["rows"]]:
        if game_vars["columns"] >= int(position[1:]) > 0:  # check column validity, 0< input <max
            unit_row_index = row_name.index(position[0].upper())
            unit_column_index = int(position[1:]) - 1
            if field[unit_row_index][unit_column_index] is None:  # if empty proceed,

                # IF UNIT IS ALLY
                if unit_name in defender_list and int(position[1:]) <= 3:  # if unit bought not in correct position
                    # units always start of with max health, and upgrade level 0
                    field[unit_row_index][unit_column_index] = [unit_name, defenders[unit_name]["maxHP"],
                                                                defenders[unit_name]["maxHP"], 0]

                    return True

                # ELSE IF UNIT IS ENEMY
                elif unit_name in monster_list:
                    field[unit_row_index][unit_column_index] = [unit_name, monsters[unit_name]["maxHP"],
                                                                monsters[unit_name]["maxHP"]]

                    return True

                # Prompt user to enter valid position
                else:
                    print("Units bought MUST be placed in the first three columns")
                    return False
            else:
                # space is occupied thus return false
                return False
        else:
            print("Column specified is not valid")
            return False
    else:
        print("Row specified is not valid")
        return False


# generate_field()
#   - function that only executes when field settings have been changed
#   - else, the default 5x7 field will be used
def generate_field():
    global field
    new_field = []
    for i in range(0, game_vars["rows"]):
        row = []
        for j in range(0, game_vars["columns"]):
            row.append(None)
        new_field.append(row)
        field = new_field
    return field


# show_main_menu()
#   - Upon booting up the game, show the introduction message
#   - Display all the options for the user to pick from
#   - Prompt the user to choose from the aforementioned options
def show_main_menu():
    print("Desperate Defenders\n" + "-" * 19 + "\nDefend the city from undead monsters!")
    print("1. Start new game\n2. Load saved game\n3. Game options\n4. Quit")
    print("-" * 19)

    while True:  # Prompt the user for their choice.
        try:
            main_menu_choice = int(input("Your choice? "))
            assert 4 >= main_menu_choice >= 1
        except ValueError:
            print("Invalid input, please enter NUMBER between 1 and 4")
            continue
        except AssertionError:
            print("Invalid input, please enter number between 1 and 4")
            continue
        else:
            if main_menu_choice == 1:  # 1. start game
                # The default game variables are stored in the dictionary as game_vars
                # Checking if the field has been altered in the menu
                if game_vars["options_changed"] == 1:
                    generate_field()
                    print(field)
                if game_vars["game_mode"] == 1:
                    # In endless, reward is doubled, and starting gold is increased
                    # Increase the amount of monster needed to kill in order to win
                    game_vars.update({"gold": 25})
                    monsters["ZOMBI"].update({"REWARD": 6})
                    monsters["WWOLF"].update({"REWARD": 8})
                    monsters["SKELE"].update({"REWARD": 8})
                    game_vars.update({"monster_kill_target": 30})
                start_game()
            elif main_menu_choice == 2:  # 2. load game
                load_game()
            elif main_menu_choice == 3:  # 3. options
                options_menu()
            elif main_menu_choice == 4:  # 4. quit
                quit_game()
            break
    return


# Start the game
def start_game():
    print("-" * 19 + "\nDefend the city from undead monsters!\nGood Luck and have fun!\n")
    draw_field()


# load_game()
#   - Read from existing text file through json module
#   - Note that there is only 1 save file at a time
#   - Overwrite the field and game_vars with the new values
def load_game():
    global field
    global game_vars
    print("LOADING....")
    save_file = open("save.txt", "r")  # Open the file containing the save
    save_information = json.load(save_file)
    game_vars, field = save_information
    save_file.close()
    draw_field()


# options_menu()
#   - Prompt user to choose which setting they want to change
#       1. Size of field
#       2. Monster spawning frequency
#       3. Game mode
#   - Updates game_vars values accordingly
def options_menu():
    print("Customize the game the way you want to play!")
    print("1. Edit field size\n2. Adjust spawning frequency\n3. Change game mode")
    while True:
        try:
            user_choice = int(input("Your Choice? "))
            assert 1 <= user_choice <= 3
        except TypeError:
            print("Please enter a valid input")
            continue
        except AssertionError:
            print("Please enter a valid input")
            continue
        except ValueError:
            print("Please enter a number")
        else:
            # Edit Field Size
            if user_choice == 1:
                while True:
                    print("Would you like to change number of rows or columns? (Default is 5x7)")
                    print("1. Rows\n2. Columns\n3. Exit")
                    try:  # Prompt user whether to edit row or column
                        user_choice = int(input("Your Choice? "))
                        assert 1 <= user_choice <= 3
                    except TypeError:
                        print("Please enter a number")
                        continue
                    except AssertionError:
                        print("Please enter a valid number")
                        continue
                    except ValueError:
                        print("Please enter a number")
                        continue

                    else:  # Executes when user has entered valid input
                        # Editing number of rows
                        if user_choice == 1:
                            while True:
                                # Prompts user about how many rows they want to have
                                # User is limited to 26 due to alphabetical constraints
                                print("How many rows would you like to have? (Min = 2, Max = 26")
                                try:
                                    user_choice = int(input("Your Choice? "))
                                    # Must have at least 1 row
                                    assert 1 < user_choice <= 26
                                except TypeError:
                                    print("Please enter a number")
                                    continue
                                except AssertionError:
                                    print("Please enter a number between 1 and 26")
                                    continue
                                except ValueError:
                                    print("Please enter a number")
                                    continue
                                else:
                                    game_vars.update({"rows": user_choice})
                                    game_vars.update({"options_changed": 1})
                                    print("The field will now have {} rows. Good Luck!".format(
                                        game_vars["rows"]))
                                    show_main_menu()
                        # Editing number of columns
                        elif user_choice == 2:
                            while True:
                                # Prompts user about how many rows they want to have
                                # Limit choices by numerical limitations
                                print("How many columns would you like to have? Must be more than 4")
                                try:
                                    user_choice = int(input("Your Choice? "))
                                    # Must have at least 1 row
                                    assert 4 <= user_choice
                                except TypeError:
                                    print("Please enter a number")
                                    continue
                                except AssertionError:
                                    print("Please enter a number more than 4")
                                    continue
                                except ValueError:
                                    print("Please enter a number")
                                    continue
                                else:
                                    game_vars.update({"columns": user_choice})
                                    game_vars.update({"options_changed": 1})
                                    print("The field will now have {} columns. Good Luck!".format(
                                        game_vars["columns"]))
                                    show_main_menu()

                        else:
                            show_main_menu()

            # Changing monster spawn frequency
            elif user_choice == 2:
                while True:
                    print("How many turns between each monster spawning? (Default is 3)")
                    try:
                        user_choice = int(input("Your Choice? "))
                        assert user_choice > 0
                    except TypeError:
                        print("Please enter a number")
                        continue
                    except AssertionError:
                        print("Please enter a positive number")
                        continue
                    except ValueError:
                        print("Please enter a number")
                        continue
                    else:
                        game_vars.update({"spawn_frequency": user_choice})
                        game_vars.update({"options_changed": 1})
                        print("Monsters will now spawn every {} turns. Good Luck!".format(game_vars["spawn_frequency"]))
                        show_main_menu()
            # Change game mode
            else:
                while True:
                    print("Which game mode would you like to play?"
                          + "\n1. Classic --- Only 1 monster spawns each wave"
                          + "\n2. Endless --- Multiple monsters spawn each wave")
                    try:
                        user_choice = int(input("Your Choice? "))
                        assert 1 <= user_choice <= 2
                    except TypeError:
                        print("Please enter a number")
                        continue
                    except AssertionError:
                        print("Please enter a number between 1 and 2")
                        continue
                    except ValueError:
                        print("Please enter a number")
                        continue
                    else:
                        if user_choice == 1:
                            game_vars.update({"game_mode": 0})
                            print("Game mode changed to classic.")
                        elif user_choice == 2:
                            game_vars.update({"game_mode": 1})
                            print("A thick fog surrounds the city. An endless horde awaits."
                                  + "\nGame mode changed to endless")
                        show_main_menu()


# quit_game()
def quit_game():
    print("Bye! Know that the monsters are still invading while you are gone!")
    exit()


# show_combat_menu() , prompts the user at the start of each round
#   - Displays the choices that the user can take at the start of each round
#   - Updates the variables depending on the user choice
def show_combat_menu():
    print("{:<16}{:<16}\n{:<16}{:<16}\n{:<16}{:<16}".format("1. Buy Unit", "2. Upgrade Unit",
                                                            "3. End Turn", "4. Save game",
                                                            "5. Spells", "6. Quit"))
    while True:
        try:
            combat_choice = int(input("Your choice? "))
            assert 6 >= combat_choice >= 0
        except ValueError:
            print("Invalid input, please enter number between 1 and 6")
            continue
        except AssertionError:
            print("Invalid input, please enter number between 1 and 6")
            continue
        else:
            if combat_choice == 0:  # 0. Cheat mode ( hidden from user)
                game_vars.update({"gold": 1000})
                defenders["ARCHR"].update({"min_damage": 1000000})
                defenders["ARCHR"].update({"max_damage": 10000000})
                defenders["CANON"].update({"min_damage": 1000000})
                defenders["CANON"].update({"max_damage": 10000000})
                defenders["RONIN"].update({"min_damage": 1000000})
                defenders["RONIN"].update({"max_damage": 10000000})
                show_combat_menu()
            elif combat_choice == 1:  # 1. buy unit
                buy_unit()
            elif combat_choice == 2:  # 2. Upgrade unit
                upgrade_unit_menu()
            elif combat_choice == 3:  # 3. end turn
                end_turn()
            elif combat_choice == 4:  # 4. save game
                save_game()
            elif combat_choice == 5:  #
                spells_menu()
            elif combat_choice == 6:  # quit
                quit_game()
            break


# buy_unit() , opens the shop then calls the place functions once unit selected
#   - open first time tutorial
#   - print UI of the choices
#   - Prompts user for choice of which unit to buy
#   - Checks if the user has sufficient gold to buy the unit
#       - if the user does not have enough gold, user will be returned to menu
#   - If user has enough gold, it will prompt user where to place unit
#   - Once user has placed the unit, it will return to the combat menu
def buy_unit():
    # tutorial
    if game_vars["first_time_shop"] == 1:
        print("Welcome to the shop! You can purchase your units to help you defend the city using gold.")
        game_vars.update({"first_time_shop": 0})  # update first time shop

    # Display Shop UI
    print("What do you wish to buy?")
    for i in range(0, len(defender_list)):
        print("{}. {} ({} Gold)".format(i + 1,
                                        defenders[defender_list[i]]["NAME"],
                                        defenders[defender_list[i]]["PRICE"]
                                        ))
    print("{}. Return to combat menu".format(len(defender_list) + 1))

    # prompt the user about which unit to  buy
    while True:
        try:
            unit_choice = int(input("Your choice? "))
            assert len(defender_list) + 1 >= unit_choice >= 1
        except ValueError:
            print("Invalid input, please enter number between 1 and 2")
            continue
        except AssertionError:
            print("Invalid input, please enter number between 1 and 2")
            continue
        else:  # Verify if the user has enough gold
            if unit_choice == len(defender_list) + 1:
                show_combat_menu()
            if defenders[defender_list[unit_choice - 1]]["PRICE"] <= game_vars["gold"]:
                new_gold = game_vars["gold"] - defenders[defender_list[unit_choice - 1]]["PRICE"]
                game_vars.update({"gold": new_gold})
                print("You have successfully bought the unit!")
                print("You have {} gold left.".format(game_vars["gold"]))
                unit_name = defender_list[unit_choice - 1]
                while True:  # prompt user where to place
                    position = input("Place where? ")
                    try:
                        assert place_unit(position, unit_name) is True
                    except AssertionError:
                        print("Specified position is invalid")
                        continue
                    except ValueError:
                        print("Please enter row and column i.e. A3")
                        continue
                    except IndexError:
                        print("You have entered invalid position, please enter row and column")
                        continue
                    else:
                        return show_combat_menu()

            else:
                print("Insufficient gold, you only have {} gold".format(game_vars["gold"]))
                return show_combat_menu()


# upgrade_unit()
#    1. Introduction
#    Returns False if the position is invalid
#       - Position is not on the field of play
#       - Position is occupied
#       - Defender is placed past the first 3 columns
#    Returns True if placement is successful
def upgrade_unit_menu():
    # First, check if there are any units that can be upgraded
    no_unit_on_field = True
    for i in range(0, game_vars["rows"]):
        for j in range(0, 3):
            try:
                assert field[i][j][0] in defender_list  # verify that unit is defender, not monster
            except TypeError:
                continue
            except AssertionError:
                continue
            else:
                no_unit_on_field = False
                break

    # if there are no units that can be upgraded, return player to combat menu
    if no_unit_on_field:
        print("You have no units on the field to upgrade. Now returning to combat menu.")
        show_combat_menu()

    # print an introductory message
    print("Equip your units with better equipment using gold!")

    # prompt user to choose which unit to upgrade
    valid_for_upgrade = False
    while True:
        try:
            unit_choice = input("Please enter the coordinate of the unit you wish to upgrade or press 'x' to exit."
                                + "\nYour choice? ")
            if unit_choice == "x":
                show_combat_menu()

            # check row validity
            if unit_choice[0].isalpha() is True and unit_choice[0].upper() in row_name[:game_vars["rows"]]:
                # check column validity
                if game_vars["columns"] >= int(unit_choice[1:]) > 0:
                    unit_row_index = row_name.index(unit_choice[0].upper())
                    unit_column_index = int(unit_choice[1:]) - 1
                    print("You have selected '{}'".format(field[unit_row_index][unit_column_index][0]))
                    assert field[unit_row_index][unit_column_index][0] in defender_list
                else:
                    raise ValueError
            else:
                raise ValueError
        # Reject invalid inputs, including empty coordinate, and enemies
        except TypeError:
            print("Coordinate is empty, please input a valid coordinate.")
            continue
        except AssertionError:
            print("You cannot upgrade enemy monsters, please try again.")
            continue
        except ValueError:
            print("You have entered an invalid coordinate, please try again.")
            continue
        except IndexError:
            print("Coordinate is empty, please input a valid coordinate.")
            continue

        # Else, if user has input a valid coordinate, allow unit to be upgraded
        else:
            valid_for_upgrade = True
            break

    if valid_for_upgrade is True:

        # check which kind of unit is present
        if field[unit_row_index][unit_column_index][0] == "WALL":
            upgrade_cost = 3 + field[unit_row_index][unit_column_index][3] * 2
        else:  # for everyone else
            upgrade_cost = 5 + field[unit_row_index][unit_column_index][3] * 2

        while True:
            try:
                # print the costs and current gold or exit
                print("You currently own {} gold, you will need {} gold to upgrade the unit." \
                      .format(game_vars['gold'], upgrade_cost))
                print("It will cost an additional 2 gold each time you upgrade a unit")
                print("1. Upgrade\n2. Exit")
                user_choice = int(input("Your Choice? "))
                assert user_choice == 1 or user_choice == 2
            except TypeError:
                print("Please enter a valid input.")
                continue
            except AssertionError:
                print("Please enter a valid input")
                continue
            else:
                if user_choice == 1:
                    break
                else:
                    return show_combat_menu()

        if game_vars["gold"] >= upgrade_cost:
            # Check for gold, then update the gold values respectively
            new_gold = game_vars["gold"] - upgrade_cost
            game_vars.update({"gold": new_gold})

            # proceed to upgrading the unit regardless, influences future cost
            field[unit_row_index][unit_column_index][3] += 1
            # Upgrade walls HP
            if field[unit_row_index][unit_column_index][0] == "WALL":
                field[unit_row_index][unit_column_index][1] += 5
                field[unit_row_index][unit_column_index][2] += 5
            # Else, for other units, upgrade Min and Max HP by 1
            else:
                field[unit_row_index][unit_column_index][1] += 1
                field[unit_row_index][unit_column_index][2] += 1
            print("Successfully upgraded the unit!")
            return show_combat_menu()
        else:
            print("You do not have enough gold. Now returning to combat menu.")
            show_combat_menu()
    else:
        return show_combat_menu()


# end_turn()
#   - After the user has the decided to end the turn, this function will update
#     multiple game variables REGARDLESS of what the user has performed
#       1. Defender Attack
#           - Check if game is won
#       2. Monster Advance
#           - Check if monster exits player field
#       3. Monster Attack
#       4. Spawn Monster
#       5. Threat and danger calculation
#   - It includes gold, turn counter, threat and danger
def end_turn():
    print("", "-" * 43)
    print("You have ended your turn")
    print("Unit and Defender actions:")

    # defender attack
    for x in range(0, game_vars["rows"]):  # go through each row
        row = x
        for y in range(3):  # process each unit in the first 3 columns
            column = y
            try:
                assert field[x][y][0] in defender_list
            except TypeError:  # filters None
                continue
            except AssertionError:
                continue
            else:
                defender_name = field[x][y][0]
                defender_attack(defender_name, row, column)

                continue

    # check if the user has won the game through monsters killed
    if game_vars["monsters_killed"] >= game_vars["monster_kill_target"]:
        win_game()

    # monster advance
    for i in range(0, game_vars["rows"]):  # go through each row
        row = i
        for j in range(0, game_vars["columns"]):  # process each monster from left to right
            column = j
            try:
                assert field[i][j][0] in monster_list
            except AssertionError:  # if the unit in question is in defender list
                continue
            except TypeError:  # if it is None
                continue
            else:
                monster_name = field[i][j][0]
                monster_advance(monster_name, row, column)

    # spawn monster according to spawn frequency
    if game_vars["turn"] % game_vars["spawn_frequency"] == 0:
        spawn_monster()
    # first monster spawns after the first turn
    elif game_vars["turn"] == 0:
        spawn_monster()

    # threat increase by 1 to (danger_level) each round
    # as threat increases, more monsters will spawn
    threat_increase = random.randint(1, game_vars["danger_level"])
    if game_vars["THREAT"] + threat_increase >= 10:
        new_threat = 0
        print("Threat level exceeds 10! A new monster has emerged!")
        spawn_monster()
    else:
        new_threat = game_vars["THREAT"] + threat_increase
    game_vars.update({"THREAT": new_threat})

    # danger level - as it increases, monsters gain additional stats.
    game_vars.update({"DANGER": game_vars["DANGER"] + 1})  # increases by 1 each round regardless
    if game_vars["DANGER"] % 12 == 0:
        # danger_level is a variable that determines "Danger Level " in the UI
        # Danger increases by 1 every 12 turns
        game_vars.update({"danger_level": game_vars["danger_level"] + 1})
        print("The monsters grow increasingly stronger ...")
        for mon in monsters:
            # Increase the monster attributes by 1 every time Danger increases
            monsters[mon].update({"maxHP": monsters[mon]["maxHP"] + 1})
            monsters[mon].update({"min_damage": monsters[mon]["min_damage"] + 1})
            monsters[mon].update({"max_damage": monsters[mon]["max_damage"] + 1})
            monsters[mon].update({"REWARD": monsters[mon]["REWARD"] + 1})

    print("", "-" * 43)
    # process var first
    game_vars.update({"gold": game_vars["gold"] + 1})  # add 1 gold per round
    game_vars.update({"turn": game_vars["turn"] + 1})  # update the turn counter each round
    draw_field()


# save_game()
#   Saves the current game progress, by storing game_vars and field
#   Also prompts user if they would like to continue or quit game
def save_game():
    print("SAVING....")
    save_file = open("save.txt", "w")
    # saving the game variables,
    save_information = [game_vars, field]
    json.dump(save_information, save_file)
    save_file.close()
    print("Save complete")

    while True:
        try:
            user_choice = int(input("Would you like to continue?"
                                    + "\n1. Yes"
                                    + "\n2. No"
                                    + "\nYour choice? "))
            assert user_choice == 1 or user_choice == 2
        except AssertionError:
            print("Please enter a valid number")
            continue
        except TypeError:
            print("Please enter a valid number")
            continue
        except ValueError:
            print("Please enter a valid number")
            continue
        else:
            if user_choice == 1:
                print("+-----Resuming the game-----+")
                show_combat_menu()
            else:
                quit_game()


# spells_menu():
#   Prompts user tutorial if first time accessing shop
#       1. Fireball
#       2. healing circle
#   Displays total damage dealt or total healing
#   Draw field , but do NOT take a turn
def spells_menu():
    # tutorial for shop
    if game_vars["first_time_spell_shop"] == 1:
        print("... Welcome to my atelier, harness the power of the mystic arts... for a price.")
        print("Tip: Spells do not consume turns!")
        game_vars.update({"first_time_spell_shop": 0})  # update first time shop

    spell_choice = ''
    while True:
        print("What do you wish to buy?")
        print("1. Fireball 3x3 (7 Gold)"
              + "\n2. Healing Circle 3x3 (5 Gold)"
              + "\n3. Return to combat menu")

        try:
            user_choice = int(input("Your Choice? "))
            assert 1 <= user_choice <= 3
        except AssertionError:
            print("Please select a number between 1 and 3")
        except TypeError:
            print("Please select a number between 1 and 3")
        except ValueError:
            print("Please select a number between 1 and 3")
        else:
            if user_choice == 1:  # 1. Fire Blast 3x3 7 gold
                # check if user has enough gold
                if game_vars["gold"] < 7:
                    print("Insufficient Gold, returning to combat menu.")
                    show_combat_menu()
                spell_choice = 1
                break

            elif user_choice == 2:  # 2. Healing circle 3x3 5 gold
                # check if user has enough gold
                if game_vars["gold"] < 5:
                    print("Insufficient Gold, returning to combat menu.")
                    show_combat_menu()
                spell_choice = 2
                break

            else:  # 3. Return to combat menu
                show_combat_menu()

    # If player has enough gold, and has chosen either spell 1 or spell 2, execute this loop
    # Prompt the user about where the center of the spell should be.
    spell_row_index = ''
    spell_column_index = ''
    while True:
        try:
            center = input("Where to target center of spell? ")
            if center[0].isalpha() is True and center[0].upper() in row_name[:game_vars["rows"]]:
                if 0 < int(center[1:]) <= game_vars["columns"]:
                    spell_row_index = row_name.index(center[0].upper())
                    spell_column_index = int(center[1:]) - 1
                else:
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            print("Please enter a valid coordinate on the field i.e. 'A3'")
            continue
        except TypeError:
            print("Please enter a valid coordinate on the field i.e. 'A3'")
            continue
        except IndexError:
            print("You have entered invalid position, please enter row and column")
            continue
        else:
            break

    # Calculate the radius of the spell
    # If the row above the input coordinate is outside field, replace with coordinate row
    top_row = int(spell_row_index) - 1
    if top_row == -1:
        top_row = int(spell_row_index)
    # If the row below the input coordinate is outside field, replace with coordinate row
    bottom_row = int(spell_row_index) + 1
    if bottom_row == game_vars["rows"] + 1:
        bottom_row = int(spell_row_index)
    # If the column left of the input coordinate is outside field, replace with coordinate column
    left_column = int(spell_column_index) - 1
    if left_column == -1:
        left_column = int(spell_column_index)
    # If the column right of the input coordinate is outside field, replace with coordinate column
    right_column = int(spell_column_index) + 1
    if right_column == game_vars["columns"] + 1:
        right_column = int(spell_column_index)

    # FIREBALL
    if spell_choice == 1:
        print("*" + "=*" * 21)
        total_damage = 0
        for row in range(top_row, bottom_row + 1):
            for column in range(left_column, right_column + 1):
                try:
                    assert field[row][column][0] in monster_list
                except AssertionError:  # ignores allies
                    continue
                except TypeError:  # ignores if empty
                    continue
                except IndexError:  # ignores invalid index positions aka out of bound
                    continue
                else:
                    # Damage the monster with the fireball damage
                    # If the monster is in the direct center, it does twice the damage
                    fireball_damage = 5
                    center_multiplier = 2
                    if row == spell_row_index and column == spell_column_index:
                        fireball_damage = fireball_damage * center_multiplier
                    field[row][column][1] = field[row][column][1] - fireball_damage
                    total_damage += fireball_damage
                    print("Fireball did {} damage to {}!".format(fireball_damage, field[row][column][0]))
                    # If the monster is killed, then the monster is removed from field
                    # Also updates the gold and threat level
                    if field[row][column][1] <= 0:
                        new_monsters_killed = game_vars["monsters_killed"] + 1
                        game_vars.update({"monsters_killed": new_monsters_killed})
                        gold_after_kill = game_vars["gold"] + monsters[field[row][column][0]]["REWARD"]
                        game_vars.update({"gold": gold_after_kill})
                        print("{} was killed! You gained {} gold as a reward!".format(
                            (field[row][column][0]),
                            monsters[
                                field[row][column]
                                [0]]["REWARD"]
                        ))
                        new_threat = game_vars["THREAT"] + monsters[field[row][column][0]]["REWARD"]
                        game_vars.update({"THREAT": new_threat})
                        field[row][column] = None
                    continue

        print("Fireball did a total of {} damage!".format(total_damage))
        print("*" + "=*" * 21)
        draw_field()

    # HEALING CIRCLE
    if spell_choice == 2:
        print("*" + "=*" * 21)
        total_healing = 0
        for row in range(top_row, bottom_row + 1):
            for column in range(left_column, right_column + 1):
                try:
                    assert field[row][column][0] in defender_list
                except AssertionError:  # ignores monsters
                    continue
                except TypeError:  # ignores if empty
                    continue
                except IndexError:  # ignores invalid index positions aka out of bound
                    continue
                else:
                    # If the unit is at max HP, then ignore and continue
                    if field[row][column][1] == field[row][column][2]:
                        continue

                    # Calculate the healing of injured units
                    healing = 5
                    center_multiplier = 2
                    if row == spell_row_index and column == spell_column_index:
                        healing = healing * center_multiplier

                    # Apply the healing to the unit
                    original_HP = field[row][column][1]
                    field[row][column][1] += healing

                    # If the min HP is now higher than max HP
                    # Total healing done is max HP minus the original hp
                    if field[row][column][1] > field[row][column][2]:
                        healing_done = field[row][column][2] - original_HP
                        total_healing += healing_done
                        field[row][column][1] = field[row][column][2]
                        print("{} was healed for {} HP!".format(field[row][column][0], healing_done))
                        continue
                    else:
                        total_healing += healing
                        print("{} was healed for {} HP!".format(field[row][column][0], healing))
                        continue
        # Print the total healing done by the spell, and show the field again before returning to main menu
        print("Healing circle rejuvenated units for {} HP!".format(total_healing))
        print("*" + "=*" * 21)
        draw_field()


# defender_attack(field,game_vars)
#   - should check if it is a wall
#   - check if unit is a cannon, and check turn. If even, do nothing.
#   - if it is not a wall, it will check for enemies in the lane
#   - if there are enemies, then attack
#       - if unit is ronin, check if enemy is directly in range, else do nothing.
#       - if health falls to 0 or below, monster dies
#       - print that the monster has died
#   - if monster is alive and attacked by cannon
#       - determine chance of push back
def defender_attack(defender_name, defender_row, defender_column):
    if defender_name == "WALL":  # wall just doesn't do anything
        return
    if defender_name == "CANON" and game_vars["turn"] % 2 != 0:  # only attacks on odd turns
        print("Cannon is preparing to fire!")
        return
    # Scanning columns beginning with the position directly in front, to the end of row
    for attack_column in range(defender_column + 1, game_vars["columns"]):

        try:
            # ignore allies
            if field[defender_row][attack_column][0] in defender_list:
                raise ValueError
            assert field[defender_row][attack_column][0] is None  # assert if empty
        except AssertionError:  # assertion error means monster in the way

            # RONIN EFFECTS
            # Ronin can only attack monsters directly in front of it, thus only checks 1 space in front
            if field[defender_row][defender_column][0] == "RONIN" \
                    and attack_column > defender_column + 1 + (1 * field[defender_row][defender_column][3]):
                print("The Ronin waits patiently to strike")
                return

            # calculate min and max damage while accounting for upgrade level
            total_min_damage = defenders[defender_name]["min_damage"] + 1 * field[defender_row][defender_column][3]
            total_max_damage = defenders[defender_name]["max_damage"] + 1 * field[defender_row][defender_column][3]
            # the unit being attacked is field[row][column - 1], [1] references current HP
            defender_damage = random.randint(total_min_damage, total_max_damage)

            # if the monster is skeleton, and attacked by archer, half the damage
            if field[defender_row][attack_column][0] == "SKELE" and defender_name == "ARCHR":
                defender_damage = math.ceil(defender_damage / 2)  # ensure number is int.
                print("The archer shoots! But the arrows passed through the Skeleton!")

            # print damage dealt and units involved
            print("{} inflicted {} damage to {}!".format(defender_name,
                                                         defender_damage,
                                                         field[defender_row][attack_column][0]))
            field[defender_row][attack_column][1] = field[defender_row][attack_column][1] - defender_damage

            # If the monster is killed, then the monster is removed from field
            # Also updates the gold and threat level
            if field[defender_row][attack_column][1] <= 0:
                new_monsters_killed = game_vars["monsters_killed"] + 1
                game_vars.update({"monsters_killed": new_monsters_killed})
                gold_after_kill = game_vars["gold"] + monsters[field[defender_row][attack_column][0]]["REWARD"]
                game_vars.update({"gold": gold_after_kill})
                print("{} was killed! You gained {} gold as a reward!".format((field[defender_row][attack_column][0]),
                                                                              monsters[
                                                                                  field[defender_row][attack_column]
                                                                                  [0]]["REWARD"]
                                                                              ))
                new_threat = game_vars["THREAT"] + monsters[field[defender_row][attack_column][0]]["REWARD"]
                game_vars.update({"THREAT": new_threat})
                field[defender_row][attack_column] = None

            # Cannon Special Effect applies only if the  monster has NOT died
            # cannon_choice > 50, push back monster
            elif field[defender_row][defender_column][0] == "CANON" and attack_column < game_vars["columns"]:

                # Check the upgrade level of cannon +10 % chance to pushback per upgrade level
                if field[defender_row][defender_column][3] == 0:
                    cannon_choice = random.randint(1, 100)
                else:
                    if field[defender_row][defender_column][3] >= 10:
                        cannon_choice = 100
                    else:
                        chance = 10 * field[defender_row][defender_column][3]
                        cannon_choice = random.randint(chance, 100)

                # verify if the cannon RNG allows it to push back monster
                if field[defender_row][attack_column + 1] is None and cannon_choice > 50:
                    print("The Canon fired! The {} moves back 1 step!".format(field[defender_row][attack_column][0]))
                    field[defender_row][attack_column + 1] = field[defender_row][attack_column]
                    field[defender_row][attack_column] = None
                else:
                    print("Cannon fired! But the {} holds its ground!".format(field[defender_row][attack_column][0]))

            break
        except TypeError:  # if there is nothing in the way
            continue
        except ValueError:  # if it is a defender in the way
            continue

        else:
            continue
    return


# monster_advance()
#   - Need to check the spaces in front of the unit
#   - But only from the space in front of the maximum possible space using for loop
#   - IF there is something DIRECTLY in front check unit type
#           IF
#           Unit is a monster -> do nothing
#           ELSE
#           Unit is a defender -> do attack function
#   - ELSE if there is nothing in front
#           IF
#           enter player field -> game over
#           ELSE
#           monster just moves

def monster_advance(monster_name, row, column):
    # immediately check for a game over scenario
    temp_mon = field[row][column]
    moves = monsters[monster_name]["MOVES"]

    # scan the columns ahead of the unit
    steps = 0
    attack_allowed = True
    for x in range(column - 1, column - moves - 1, -1):  # i.e. range(6 , 4, - 1) -> 6 5
        field[row][x + 1] = None  # Delete the previous position
        if field[row][x] is not None:  # Check if unit in front is monster or unit
            if field[row][x][0] in defender_list and attack_allowed is True:
                monster_attack(monster_name, row, x + 1)
                field[row][x + 1] = temp_mon
                if steps >= 1:
                    print("{} has taken {} step(s) in lane {}".format(monster_name, steps, row_name[row]))

                return
            else:
                field[row][x + 1] = temp_mon
                if steps >= 1:
                    print("{} has taken {} step(s) in lane {}".format(monster_name, steps, row_name[row]))
                return
        else:
            if x == -1:
                print("{} has taken {} step(s) in lane {}".format(monster_name, steps, row_name[row]))
                print("{} has reached the city!".format(monster_name))
                print("Monsters have plunged the town in darkness! Everyone dies!")
                quit_game()
            else:
                field[row][x] = temp_mon
                steps += 1
                attack_allowed = False

    # print the movement to notify the user
    print("{} has taken {} step(s) in lane {}".format(monster_name, steps, row_name[row]))


# monster_attack
#   - function serves to calculate the damage that a monster will do to a unit
#   - uses RNG to determine damage
#   - print damage dealt
#   - if inflicted damage kills monster, replace with none
def monster_attack(monster_name, row, column):
    # the unit being attacked is field[row][column - 1], [1] references current HP
    monster_damage = random.randint(monsters[monster_name]["min_damage"],
                                    monsters[monster_name]["max_damage"])
    print("{} inflicted {} damage to {}!".format(monster_name,
                                                 monster_damage,
                                                 field[row][column - 1][0]
                                                 ))
    field[row][column - 1][1] = field[row][column - 1][1] - monster_damage
    if field[row][column - 1][1] <= 0:
        field[row][column - 1] = None

    return


# spawn_monster()
#   - Spawns a random monster in a random lane on the right side
#   - if in endless mode, random number of mobs will spawn
def spawn_monster():
    game_mode = game_vars["game_mode"]

    # Regular game mode: mob spawns according to spawn frequency
    if game_mode == 0:
        while True:
            try:
                unit_name = monster_list[random.randint(0, len(monster_list) - 1)]
                spawn_row_index = random.randint(0, game_vars["rows"] - 1)  # randomize which row to spawn
                spawn_row = row_name[spawn_row_index]
                spawn_column = game_vars["columns"]
                position = spawn_row + str(spawn_column)
                assert place_unit(position, unit_name) is True
            except AssertionError:
                continue
            else:
                place_unit(position, unit_name)
                break

    # ( Endless Horde )
    elif game_mode == 1:
        # number of monsters that will be spawned this round is random
        num_monster_spawn = random.randint(1, game_vars["rows"])
        for i in range(0, num_monster_spawn + 1):
            unit_name = monster_list[random.randint(0, len(monster_list) - 1)]
            spawn_row_index = random.randint(0, game_vars["rows"] - 1)  # which row to spawn
            spawn_row = row_name[spawn_row_index]
            spawn_column = game_vars["columns"]
            position = spawn_row + str(spawn_column)
            place_unit(position, unit_name)

    return


# draw_field() function , UI for main game showing map, appears upon starting game
#                         and at the end every round
#   - retrieve the variables that define game state
#   - printing the actual map
#   - Row 1 , 2 , 3 --- Rules state that players can only place in first 3 columns
#   - print row name A, B , C ... --- reference to game_var setting
#   - try: if any monster or unit is there
#   - except: print blank space instead
#   - print the UI below
#   - format is [unit name, current HP, max Hp]
def draw_field():
    print("{:4}{:6}{:6}{:6}".format("", "1", "2", "3"))
    print(" +" + "-----+" * game_vars["columns"])

    for i in range(0, game_vars["rows"]):  # print per row
        # first line
        print(row_name[i], end="")  # row name
        print("|", end="")
        for j in range(0, game_vars["columns"]):  # print per column
            try:
                # noinspection PyUnresolvedReferences
                print(f"{field[i][j][0]:5}|", end="")  # print unit name
            except TypeError:
                print("{:5}|".format(""), end="")  # if return None, then print blank
            except IndexError:
                print("{:5}|".format(""), end="")
        # second line
        print("\n |", end="")
        for j in range(0, game_vars["columns"]):
            try:
                if field[i][j][2] >= 100:  # if max hp is more than 100, only display 99 but retain value
                    display_max_HP = 99
                else:
                    display_max_HP = field[i][j][2]
                if field[i][j][1] >= 100:
                    display_min_HP = 99
                else:
                    display_min_HP = field[i][j][1]

                print(f"{display_min_HP:>2}/{display_max_HP:<2}|", end="")  # print unit current hp / max hp
            except TypeError:
                print("{:5}|".format(""), end="")
            except IndexError:
                print("{:5}|".format(""), end="")
        print("\n +" + "-----+" * game_vars["columns"])

    print("{:<6}{:<6}".format("Turn", game_vars["turn"]), end="")  # current turn number
    print("{}{}".format("Threat = [", "-" * game_vars["THREAT"]), end="")  # current threat bar
    print("{}]".format(" " * (game_vars["max_threat"] - game_vars["THREAT"])), end="")  # Threat bar inverse
    print("{:<5}{:<13}{}".format("", "Danger Level", game_vars["danger_level"]))  # current danger Level
    print("{:<8}{:<4}".format("Gold =", game_vars["gold"]), end="")  # current gold
    print("{}{}/{}".format("Monsters killed = ", game_vars["monsters_killed"],
                           game_vars["monster_kill_target"]))  # progress

    show_combat_menu()


# win_game()
def win_game():
    print("+" + "-" * 60 + "+")
    print("Congratulations! You managed to defend the city from monsters!")
    print("+" + "-" * 60 + "+")
    exit()


# ===================================#
# Begin the game.
show_main_menu()
# ===================================#
# obsolete saving mechanism
'''saved_game_vars = save_file.readline()  # Read the first line containing the saved game_vars
saved_game_vars = saved_game_vars.strip("\n")  # Remove EOL character
saved_game_vars = saved_game_vars[1:-1]  # Remove the brackets
saved_game_vars = saved_game_vars.split(", ")  # Make it into a list, because it is initially a string
# update each value in the dictionary to match according to the save file
# Since python dictionaries are now ordered according to insertion order,
# can proceed to update each value accordingly
# Else, save the original game_vars as string
i = 0
for j in game_vars.keys():
    game_vars.update({j: int(saved_game_vars[i])})
    i += 1

saved_field = save_file.readline()
saved_field = saved_field.strip("\n")  # Remove EOL character
saved_field = saved_field[1:-1]  # Remove the brackets
saved_field = saved_field.split(", ")  # Make it into a list, because it is initially a string
print(saved_field)
print(type(saved_field))'''
