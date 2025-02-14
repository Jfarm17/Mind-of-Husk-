import sys

def parse_value(key, value):
    """Parse a string value into the appropriate Python data type."""
    value = value.strip()
    if key.startswith("r_obj") or key.startswith("r_hiddenobj"):
        if value.startswith("[") and value.endswith("]"):
            return [item.strip().strip('"') for item in value[1:-1].split(",") if item.strip()]
        else:
            return [value.strip().strip('"')]
    elif value.startswith("[") and value.endswith("]"):
        return [item.strip().strip('"') for item in value[1:-1].split(",") if item.strip()]
    elif value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    elif value == "":
        return []
    else:
        return value.strip().strip('"')

def parse_file(file_path):
    """Parse a configuration file into a structured dictionary."""
    data = {
        "GameSettings": {},
        "Locations": [],
        "NPCs": []
    }
    current_section = None
    section_data = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if not line or line == "---":
                if current_section == "Locations" and section_data:
                    data["Locations"].append(section_data)
                elif current_section == "NPCs" and section_data:
                    data["NPCs"].append(section_data)
                section_data = {}

            if ":" in line:
                key, value = line.split(":", 1)
                value = parse_value(key.strip(), value)

                if key.startswith("game_"):
                    current_section = "GameSettings"
                    data["GameSettings"][key.strip()] = value
                elif key.startswith("r_"):
                    current_section = "Locations"
                    section_data[key.strip()] = value
                elif key.startswith("npc_"):
                    current_section = "NPCs"
                    section_data[key.strip()] = value
                else:
                    section_data[key.strip()] = value

                if key == 'r_id':
                    section_data['r_id'] = value

        if current_section == "Locations" and section_data:
            data["Locations"].append(section_data)
        elif current_section == "NPCs" and section_data:
            data["NPCs"].append(section_data)

    return data

def locations_to_dict(locations):
    """Convert a list of locations into a dictionary keyed by location IDs."""
    locations_dict = {}
    for loc in locations:
        loc_id = loc.get('r_id')
        if loc_id is not None:
            objs = loc.get('r_objs', loc.get('r_obj', []))
            hidobjs = loc.get('r_hiddenobj', loc.get('r_hiddenobj', []))
            locations_dict[loc_id] = {
                'r_desc': loc.get('r_desc', ''),
                'r_objs': objs if isinstance(objs, list) else [objs],
                'r_hiddenobj': hidobjs if isinstance(hidobjs, list) else [hidobjs]
            }
    return locations_dict

def flame_in_pillar():
    """Check if all required pillars have a flame."""
    required_pillars = ['1', '3', '6', '7']
    for pillar in required_pillars:
        if 'flame' not in locations_dict[pillar]['r_objs']:
            return False
    return True

def check_for_flame_and_add_hidden_path():
    """Add a hidden path if all pillars have a flame."""
    if flame_in_pillar():
        if locations_dict['1']['r_hiddenpath'] == "":
            locations_dict['1']['r_hiddenpath'] = '9'
            print("The hidden path to the House of Memories has been revealed!")

def search(current_loc):
    """Search the current location for hidden paths and objects."""
    if current_loc in locations_dict:
        location = locations_dict[current_loc]
        if 'r_hiddenpath' in location:
            print("A hidden path is revealed to you.")
        if 'r_hiddenobj' in location:
            hidden_objects = location['r_hiddenobj']
            print("You have found hidden objects:" + str(hidden_objects))
            for obj in hidden_objects:
                location['r_objs'].append(obj)
            location['r_hiddenobj'] = []
        else:
            print("No hidden objects found.")
        location['search_done'] = True

def map_movement(direction, current_loc, game_sizex, game_sizey):
    """Move the player in the specified direction."""
    current_loc = int(current_loc)
    if direction == "r_north":
        if current_loc - game_sizex > 0:
            x = current_loc - game_sizex
        else:
            x = current_loc + game_sizex * (game_sizey - 1)
        return str(x)
    elif direction == "r_south":
        if current_loc + game_sizex <= game_sizex * game_sizey:
            x = current_loc + game_sizex
        else:
            x = current_loc - game_sizex * (game_sizey - 1)
        return str(x)
    elif direction == "r_east":
        if current_loc % game_sizex != 0:
            x = current_loc + 1
        else:
            x = current_loc - (game_sizex - 1)
        return str(x)
    elif direction == "r_west":
        if (current_loc - 1) % game_sizex != 0:
            x = current_loc - 1
        else:
            x = current_loc + (game_sizex - 1)
        return str(x)
    return str(current_loc)

def take(location_id, item_name, locations_dict):
    """Take an item from the current location."""
    location = locations_dict.get(location_id)
    if location:
        if item_name in location['r_objs']:
            location['r_objs'].remove(item_name)
            inv.append(item_name)
            print(f"You took the {item_name}.")
        else:
            print(f"There is no {item_name} here to take.")
    else:
        print(f"Location '{location_id}' not found.")

def take_hidden_path(current_loc, cmd, hp):
    """Follow a hidden path if available."""
    if "follow" in cmd.lower():
        if current_loc in locations_dict:
            location = locations_dict[current_loc]
            if 'search_done' not in location or not location['search_done']:
                print("There is no hidden path to follow.")
                return current_loc, hp
            if 'r_hiddenpath' in location and location['r_hiddenpath']:
                new_location = location['r_hiddenpath']
                print(f"Moving to {new_location}.")
                if new_location in locations_dict:
                    if "flame" in inv:
                        hp = damage(hp, "flame")
                    elif "Stick of pain" in inv:
                        hp = damage(hp, "Stick of pain")
                    current_loc = new_location
                    return current_loc, hp
                else:
                    print(f"Invalid new location: {new_location}.")
                    return current_loc, hp
            else:
                print("There is no hidden path here.")
        else:
            print(f"Location ID {current_loc} not found.")
    else:
        print("Command does not involve following a hidden path.")
    return current_loc, hp

def drop(current_loc, item):
    """Drop an item in the current location."""
    if current_loc in locations_dict:
        location = locations_dict[current_loc]
        if item in inv:
            location['r_objs'].append(item)
            inv.remove(item)
            print(f"You have dropped '{item}' in '{location['r_desc']}'")
        else:
            print("You don't have this item to drop.")
    else:
        print(f"Location '{current_loc}' not found.")

def print_location_info(current_loc):
    """Print the current location's information."""
    if current_loc in locations_dict:
        location = locations_dict[current_loc]
        print(location['r_desc'])
        if 'r_objs' in location:
            objects = location.get('r_objs', [])
            if objects:
                print("You see:", objects)
    else:
        print("Location ID", current_loc, "not found.")

def talk_to_npc(current_loc, npc_id, npcs, player_inventory):
    """Interact with an NPC in the current location."""
    npc = next((npc for npc in npcs if npc['npc_id'] == str(npc_id)), None)
    if not npc:
        print(f"NPC with ID {npc_id} not found.")
        return
    if npc['npc_location'] != current_loc:
        print(f"{npc['npc_name']} is not here.")
        return

    print("Talking to " + str(npc['npc_name']) + ": " + str(npc['npc_desc']))
    print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][0]))
    print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][7]))

    for i, dialogue in enumerate(npc['npc_interact']):
        print(f"{i + 1}. {dialogue}")

    while True:
        try:
            choice = int(input("Choose an option: ")) - 1
            if choice < 0 or choice >= len(npc['npc_interact']):
                print("Invalid choice.")
                continue
            selected_dialogue = npc['npc_interact'][choice]
            print("You chose: " + str(selected_dialogue))

            if selected_dialogue == "What is my goal?":
                print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][5]))
            elif selected_dialogue == "End Dialogue":
                print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][2]))
                break
            elif selected_dialogue == "Give her an apple":
                if "apple" in player_inventory:
                    if "giant toenail" in npc['npc_inv']:
                        player_inventory.append("giant toenail")
                        npc['npc_inv'].remove("giant toenail")
                        print(str(npc['npc_name']) + " says: Thank you, I have a gift for you!")
                    else:
                        print("Sorry sweetie, I have no more gifts for you, but I'll still take the apple")
                    player_inventory.remove("apple")
                    npc['npc_inv'].append("apple")
                else:
                    print(str(npc['npc_name']) + " says: YOU MAGGOT. YOU DON'T EVEN HAVE AN APPLE FOR ME")
            elif selected_dialogue == "I have no flame":
                print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][8]))
            elif selected_dialogue == "I do have a flame":
                while True:
                    if "flame" in player_inventory:
                        print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][4]))
                        for i, interactables in enumerate(npc['npc_interact_2']):
                            print(f"{i + 1}. {interactables}")
                        try:
                            choice = int(input("Choose an option: ")) - 1
                            if choice < 0 or choice >= len(npc['npc_interact_2']):
                                print("Invalid choice.")
                                continue
                            selected_dialogue = npc['npc_interact_2'][choice]
                            if selected_dialogue == "Give flame":
                                print("The Human Mind. You were supposed to be selfish. You were supposed to be realized. You gave into a false pillar. Your journey ends here.")
                                sys.exit()
                            elif selected_dialogue == "Don't give her the flame":
                                print(f"{npc['npc_name']} says: Fine. Your loss you wuss.")
                                break
                        except:
                            print("Please input a recognizable option")
                    else:
                        print(f"{npc['npc_name']} says: YOU LIAR, you do not have a flame.")
                        print("Dialogue ends")
                        return
        except:
            print("Invalid input. Please enter a number.")

def damage(hp, damage_type):
    """Apply damage to the player based on the damage type."""
    if damage_type == "flame":
        hp -= 1
        print(f"Flame is searing your skin. You have {hp} hp left.")
    elif damage_type == "Stick of pain":
        hp -= 2
        print(f"The stick is causing you pain. You have {hp} hp left.")
    if hp <= 0:
        hp = 0
        print("You have reached zero hp. Game Over!")
    return hp

def edible(x):
    """Check if an item is edible."""
    return x in ["apple", "rice", "green herb", "health potion", "green potion"]

# Initialize game variables
config_file = 'mind_of_husk_config.txt'
parsed_data = parse_file(config_file)
game_settings = parsed_data.get("GameSettings", {})
locations_dict = locations_to_dict(parsed_data.get("Locations", []))
npcs = parsed_data.get("NPCs", [])

for loc in locations_dict.values():
    if 'r_obj' not in loc:
        loc['r_obj'] = []
    if 'r_hiddenobj' not in loc:
        loc['r_hiddenobj'] = []

inv = []
game_sizex = int(game_settings["game_xsize"])
game_sizey = int(game_settings["game_ysize"])
current_location = game_settings["game_start"]
death_count = 0
hp = 2
flint_health = 4

# Main game loop
if config_file == "mind_of_husk_config.txt":
    print("\t" + str(game_settings["game_name"]) + "\t")
    print("\tMade from the mind of Joshua Farmer and copious amounts of passion/caffeine")
    print("")
    print("You stand alone, ontop of a mound of corpses. Your mind muddled with confusion. Thoughts of yours lost of time. You try to recall the name given to you by your mother. You can’t remember her face. ")
    name = input("What is your name?: ")
    print("You remember your name. It is", name)
    print("You gather yourself, and brush off the dust. A pool of blood with a reflection of your blank stare.")
    while True:
        stare = input("Will you continue to stare? Y/N: " )
        if stare.lower() == "yes" or stare.lower() == "y":
            death_count = death_count + 1
            print("One day has passed")
            if death_count == 3:
                print("You starved to death and fully became a husk. I guess you were born to never to remember who you are. ")
                sys.exit()
        if stare.lower() == "no" or stare.lower() == "n":
            print("You have firmed your resolve. Take this apple. Eat it to gather your strength.")
            inv.append("apple")
            break
    print_location_info(current_location)
    while True:
        check_for_flame_and_add_hidden_path()
        if hp <= 0:
            print("You have reached zero hp. You will never remember who you were. You will always be nothing but a husk. Death has come for you, and death shall take you.")
            break
        locations_dict[current_location]
        cmd = input("Enter an action: ")

        if cmd == "exit":
            break
        if cmd == "inv":
            print(" ", inv)
        if cmd == "stat":
            print("Health:", hp)
        if eat.lower() in cmd.lower()[0:3]:
            item = cmd[4:].strip()
            if item == "":
                print("Specify what you want to eat")
            else:
                if item in inv:
                    if edible(item) == False:
                        print("You cannot eat", item)
                    else:
                        print("You ate the", item)
                        if hp >= 3:
                            print("Your health cannot exceed the maximum threshold of 3")
                        else:
                            hp = hp + 1
                            print("Your hp was increased by 1 and is now", hp)
                        inv.remove(cmd[4:])
                else:
                    print("You cannot consume that because you do not have that in your inventory")
        elif cmd.lower() == "flame" or cmd.lower() == "create flame":
            if "flint and steel" in inv:
                if flint_health == 0:
                    print("Your flint has run out of uses")
                    inv.remove("flint and steel")
                else:
                    inv.append("flame")
                    flint_health = flint_health - 1
                    print("You have created a sacred flame. Your flint and steel only has", flint_health, "more uses")
            else:
                print("You do not have flint and steel")
        elif cmd.lower() == "goal":
            if "Human Effigy" in inv:
                inv.remove("Human Effigy")
                print("\n You husk of man. You'd use an effigy of your self to remember your goal? \n You must light the four pillars across the locations in the lands between death. \n You must leave a flame. Flint and steel may create the flame. Then you shall be set free and your memories will reveal their selves.")
            else:
                print("You need an effigy of human origin to know your goal")
        elif move.lower() in cmd.lower()[0:4]:
            item = cmd[5:].strip()
            if item.lower() == "north":
                current_location = map_movement("r_north", current_location, game_sizex, game_sizey)
                if "flame" in inv:
                    hp = damage(hp, "flame")
                elif "Stick of pain" in inv:
                    hp = damage(hp, "Stick of pain")
                print_location_info(current_location)
            elif item.lower() == "east":
                current_location = map_movement("r_east", current_location, game_sizex, game_sizey)
                if "flame" in inv:
                    hp = damage(hp, "flame")
                elif "Stick of pain" in inv:
                    hp = damage(hp, "Stick of pain")
                print_location_info(current_location)
            elif item.lower() == "west":
                current_location = map_movement("r_west", current_location, game_sizex, game_sizey)
                if "flame" in inv:
                    hp = damage(hp, "flame")
                elif "Stick of pain" in inv:
                    hp = damage(hp, "Stick of pain")
                print_location_info(current_location)
            elif item.lower() == "south":
                current_location = map_movement("r_south", current_location, game_sizex, game_sizey)
                if "flame" in inv:
                    hp = damage(hp, "flame")
                elif "Stick of pain" in inv:
                    hp = damage(hp, "Stick of pain")
                print_location_info(current_location)
        elif get.lower() in cmd.lower()[0:4]:
            item = cmd[5:].strip()
            if item == "":
                print("Specify what you want taken.")
            else:
                take(current_location, item, locations_dict)
        if look.lower() in cmd.lower()[0:6]:
            item = cmd[7:].strip()
            search(current_location)
        elif lose.lower() in cmd.lower()[0:4]:
            item = cmd[5:].strip()
            if item == "":
                print("Specify what you want to drop.")
            else:
                drop(current_location, item)
        if convo.lower() in cmd.lower()[0:4]:
            talk_to_npc(current_location, 1, npcs, inv)
        if follow.lower() in cmd.lower()[0:6]:
            try:
                if locations_dict[current_location]['r_hiddenpath'] == "":
                    print("You are unable to take this path at the moment")
                else:
                    current_location, hp = take_hidden_path(current_location, follow.lower(), hp)
            except:
                "No path in this location"
        if "Ancient Yo Momma Joke" in inv and read.lower() in cmd.lower()[0:4]:
            print("Yo momma so dumb, she didn't realize this was a game guide")
            print("Your goal is literally to light four pillars and remember who you are. Find the house of memories. Oh the parietal is a lie.\nGame Commands: \n Move - move to another map location by pairing move with a cardinal direction \n Search - search area for hidden objects and paths \n Talk - talk to an NPC in an area \n Take - take an item from an area \n ")
        elif "Ancient Yo Momma Joke" not in inv and read.lower() in cmd.lower()[0:4]:
            print("You know you can't read anything unless it has yo momma joke in the title")
        if "Realization" in inv:
            print("You have remembered who you are. You remember your mother's bosom. Flames have reiginited your passion for life. Your memories restored. Love lost and regained. You amaze me. I'm surprised you made it thus far. You are I and I am you. We are the same. We are one. We are", name)
            break
else:
    print(locations_dict)
    print_location_info(current_location)
    while True:
        if hp <= 0:
            print("You have reached zero hp. You will never remember who you were. You will always be nothing but a husk. Death has come for you, and death shall take you.")
            break
        cmd = input("Enter an action: ")
        if cmd == "exit":
            break
        if cmd == "inv":
            print(" ", inv)
        if cmd == "stat":
            print("Health:", hp)
        if eat.lower() in cmd.lower()[0:3]:
            item = cmd[4:].strip()
            if item == "":
                print("Specify what you want to eat")
            else:
                if item in inv:
                    if edible(item) == False:
                        print("You cannot eat", item)
                    else:
                        print("You ate the", item)
                        if hp >= 3:
                            print("Your health cannot exceed the maximum threshold of 3")
                        else:
                            hp = hp + 1
                            print("Your hp was increased by 1 and is now", hp)
                        inv.remove(cmd[4:])
                else:
                    print("You cannot consume that because you do not have that in your inventory")
        elif cmd.lower() == "flame" or cmd.lower() == "create flame":
            if "flint and steel" in inv:
                if flint_health == 0:
                    print("Your flint has run out of uses")
                    inv.remove("flint and steel")
                else:
                    inv.append("flame")
                    flint_health = flint_health - 1
                    print("You have created a sacred flame. Your flint and steel only has", flint_health, "more uses")
            else:
                print("You do not have flint and steel")
        elif cmd.lower() == "goal":
            print("\n You husk of man. Need an effigy of your self to remember your goal? \n You must light the four pillars across the locations in the lands between death. \n You must leave a flame. Flint and steel may create the flame. Then you shall be set free and your memories will reveal their selves.")
        elif move.lower() in cmd.lower()[0:4]:
            item = cmd[5:].strip()
            if item.lower() == "north":
                current_location = map_movement("r_north", current_location, game_sizex, game_sizey)
                print_location_info(current_location)
            elif item.lower() == "east":
                current_location = map_movement("r_east", current_location, game_sizex, game_sizey)
                print_location_info(current_location)
            elif item.lower() == "west":
                current_location = map_movement("r_west", current_location, game_sizex, game_sizey)
                print_location_info(current_location)
            elif item.lower() == "south":
                current_location = map_movement("r_south", current_location, game_sizex, game_sizey)
                print_location_info(current_location)
        elif get.lower() in cmd.lower()[0:4]:
            item = cmd[5:].strip()
            if item == "":
                print("Specify what you want taken.")
            else:
                take(current_location, item, locations_dict)
        if look.lower() in cmd.lower()[0:6]:
            item = cmd[7:].strip()
            search(current_location)
        elif lose.lower() in cmd.lower()[0:4]:
            item = cmd[5:].strip()
            if item == "":
                print("Specify what you want to drop.")
            else:
                drop(current_location, item)
        if convo.lower() in cmd.lower()[0:4]:
            talk_to_npc(current_location, 1, npcs, inv)
        if follow.lower() in cmd.lower()[0:6]:
            try:
                if locations_dict[current_location]['r_hiddenpath'] == "":
                    print("You are unable to take this path at the moment")
                else:
                    current_location, hp = take_hidden_path(current_location, follow.lower(), hp)
            except:
                "No path in this location"
