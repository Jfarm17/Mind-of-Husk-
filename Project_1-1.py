import sys ### For specfic things 
### Figure out how to turn this into an executable 
###We need a list for objects because what if the location has multiple objects###
### We are making different sections when reading so it is easier to dictate things when going forward###
def parse_value(key, value):
    """Parse a string value into the appropriate Python data type."""
    value = value.strip()
    if key.startswith("r_obj") or key.startswith("r_hiddenobj"):
        # Ensure r_obj or r_hiddenobj are treated as lists, even if they contain a single object
        if value.startswith("[") and value.endswith("]"):
            # If it's already a list, parse it as a list
            return [item.strip().strip('"') for item in value[1:-1].split(",") if item.strip()]
        else:
            # String to list
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
    data = {
        "GameSettings": {},
        "Locations": [],
        "NPCs": []
    }
    current_section = None
    section_data = {}
    ### https://stackoverflow.com/questions/56001344/python-isinstance-function ### (isinstance was previoulsy here, but still used later on)
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if not line or line == "---":
                if current_section == "Locations" and section_data:
                    data["Locations"].append(section_data)
                elif current_section == "NPCs" and section_data:
                    data["NPCs"].append(section_data)
                section_data = {}
            ###If : is in the line, it splits there ###
            if ":" in line:
                key, value = line.split(":", 1)
                value = parse_value(key.strip(), value)
            ### The sections I was talking about before ###
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
                    value 

        if current_section == "Locations" and section_data:
            data["Locations"].append(section_data)
        elif current_section == "NPCs" and section_data:
            data["NPCs"].append(section_data)

    return data

# File path for the config
###Input the game here Professor Capra###
config_file = 'mind_of_husk_config.txt'

# Parse the file
parsed_data = parse_file(config_file)

# Convert locations to a dictionary keyed by location IDs
def locations_to_dict(locations):
    locations_dict = {}
    for loc in locations:
        loc_id = loc.get('r_id')
        ### Was returning none types at one point when I wanted to convert strings to list for locations to store multiple items
        if loc_id is not None:
            # Check if 'r_objs' exists; if not, check for 'r_obj'
            objs = loc.get('r_objs', loc.get('r_obj', []))
            hidobjs = loc.get('r_hiddenobj', loc.get('r_hiddenobj', []))
            locations_dict[loc_id] = {
                'r_desc': loc.get('r_desc', ''),
                'r_objs': objs if isinstance(objs, list) else [objs],  # Ensure it's a list
                'r_hiddenobj': hidobjs if isinstance(hidobjs, list) else [hidobjs]
            }
    return locations_dict


# Access the parsed data
game_settings = parsed_data.get("GameSettings", {})
locations_dict = locations_to_dict(parsed_data.get("Locations", []))
npcs = parsed_data.get("NPCs", [])

# Ensure r_obj has a default value of an empty list if not present
for loc in locations_dict.values():
    if 'r_obj' not in loc:
        loc['r_obj'] = [] # Default to an empty list if no objects defined
        
for loc in locations_dict.values():
    if 'r_hiddenobj' not in loc:
        loc['r_hiddenobj'] = []

def flame_in_pillar():
        required_pillars = ['1', '3', '6', '7']  # IDs of all pillar locations
        for pillar in required_pillars:
            if 'flame' not in locations_dict[pillar]['r_objs']:
                return False
        return True

    
def check_for_flame_and_add_hidden_path():
        if flame_in_pillar():
            # Once all pillars have the flame, add the hidden path from Pillar of Amygdala to House of Memories
            if locations_dict['1']['r_hiddenpath'] == "":
                locations_dict['1']['r_hiddenpath'] = '9'  # ID 9 is the House of Memories
                print("The hidden path to the House of Memories has been revealed at the place where fear, rage, and anxiety are dealt with!")


###Instantiating Variables###
inv = []
    ###Need to turn these into integers for math portion. 
game_sizex = int(game_settings["game_xsize"])
game_sizey = int(game_settings["game_ysize"])
current_location = (game_settings["game_start"]) # Starting location
eat = "eat"
move = "move"
get = "take"
look = "search"
lose = "drop"
convo = "talk"
name = ""
stare = ""
follow = "follow"
read = "read"
death_count = 0
hp = 2 ####Health points for player character####
flint_health = 4

### Search function: Used to look for r_hiddenpath and r_hiddenobjs in locations. 
def search(current_loc):
    if current_loc in locations_dict:
        location = locations_dict[current_loc]
        if 'r_hiddenpath' in location:
            print("A hidden path is revealed to you.")
        ### Check and reveal hidden objects if the player is present ###
        ### We wanna add hidden objects to the locations actual inventory once searched for ###
        if 'r_hiddenobj' in location:
            hidden_objects = location['r_hiddenobj']
            print("You have found hidden objects:" + str(hidden_objects))
            for obj in hidden_objects:
                location['r_objs'].append(obj)  # Append each hidden object individually
            
            location['r_hiddenobj'] = []  # Clear the hidden object list
        else:
            print("No hidden objects found.")
        
        # Mark that the search has been performed in this location
        location['search_done'] = True
###Game based on matrices and crap like that ###
def map_movement(direction, current_loc, game_sizex, game_sizey):
    current_loc = int(current_loc)
    if direction == "r_north":
        if current_loc - game_sizex > 0:
            x = current_loc - game_sizex
        else:
            # Wrap around: Move to the last row (bottom edge)
            x = current_loc + game_sizex * (game_sizey - 1)
        return str(x)
    elif direction == "r_south":
        if current_loc + game_sizex <= game_sizex * game_sizey:
            x = current_loc + game_sizex
        else:
            # Wrap around: Move to the first row (top edge)
            x = current_loc - game_sizex * (game_sizey - 1)
        return str(x)
    elif direction == "r_east":
        if current_loc % game_sizex != 0:
            x = current_loc + 1
        else:
            # Wrap around: Move to the leftmost column
            x = current_loc - (game_sizex - 1)
        return str(x)
    elif direction == "r_west":
        if (current_loc - 1) % game_sizex != 0:
            x = current_loc - 1
        else:
            # Wrap around: Move to the rightmost column
            x = current_loc + (game_sizex - 1)
        return str(x)
    return str(current_loc)

def take(location_id, item_name, locations_dict):
    location = locations_dict.get(location_id)
    print("Current location's objects before taking: " + str(location.get('r_objs', [])))
    
    if location:
        # Check if item_name exists in the current location's objects
        if item_name in location['r_objs']:
            location['r_objs'].remove(item_name)  # Remove the item from the location
            inv.append(item_name)  # Add the item to the player's inventory
            print(f"You took the {item_name}.")
            print(f"Current location's objects after taking: {location['r_objs']}")
        else:
            print(f"There is no {item_name} here to take.")
    else:
        print(f"Location '{location_id}' not found.")


def take_hidden_path(current_loc, cmd, hp):
    if "follow" in cmd.lower():
        if current_loc in locations_dict:
            location = locations_dict[current_loc]
            
            # Check if a search has been done before allowing to take hidden path
            if 'search_done' not in location or not location['search_done']:
                print("There is no hidden path to follow.")
                return current_loc, hp  # Return the same location and hp if search hasn't been done
            
            # Check if there is a hidden path
            if 'r_hiddenpath' in location and location['r_hiddenpath']:
                new_location = location['r_hiddenpath']
                print(f"Moving to {new_location}.") 
                
                # Check if the new location exists in the location dictionary
                if new_location in locations_dict:
                    # Handle damage based on inventory
                    if "flame" in inv:
                        hp = damage(hp, "flame")
                    elif "Stick of pain" in inv:
                        hp = damage(hp, "Stick of pain")
                    
                    # Update current location to new location
                    current_loc = new_location
                    return current_loc, hp  # Return updated location and hp
                else:
                    print(f"Invalid new location: {new_location}. You cannot move there.")
                    return current_loc, hp  # Stay in the current location if the new location is invalid
            else:
                print("There is no hidden path here.")
        else:
            print(f"Location ID {current_loc} not found.")
    else:
        print("Command does not involve following a hidden path.")
    
    return current_loc, hp  # Return the same location if no movement happens

def drop(current_loc, item):
    if current_loc in locations_dict:
        location = locations_dict[current_loc]
        print(f"Current location's objects before dropping: {location['r_objs']}")
        
        # Check if the item is in the player's inventory
        if item in inv:
            # Append the item to the location's objects
            location['r_objs'].append(item)
            inv.remove(item)  # Remove the item from the inventory
            print(f"You have dropped '{item}' in '{location['r_desc']}'")
            print(f"Current location's objects after dropping: {location['r_objs']}")
        else:
            print("You don't have this item to drop.")
    else:
        print(f"Location '{current_loc}' not found.")

### Location info needs to be displayed so the player can follow 
def print_location_info(current_loc):
    """Print the current location's information."""
    if current_loc in locations_dict:
        location = locations_dict[current_loc]
        print(location['r_desc'])  # Remove curly braces
        if 'r_objs' in location:
            objects = location.get('r_objs', [])
            if objects:
                print("You see:", objects)  # Make sure to join correctly
    else:   
        print("Location ID", current_loc, "not found.")  # Removed curly braces for clarity
        
###For talking to NPCs; need to figure out how to make it more streamlined, but I guess it can't be###
def talk_to_npc(current_loc, npc_id, npcs, player_inventory):
    print(f"Current location: {current_loc}")
    print(f"NPC ID: {npc_id}")
    loop_breaker = False
    # Find the NPC by ID
    npc = next((npc for npc in npcs if npc['npc_id'] == str(npc_id)), None)
    if not npc:
        print(f"NPC with ID {npc_id} not found.")
        return   
    # Check if the NPC is in the current location
    if npc['npc_location'] != current_loc:
        print(f"{npc['npc_name']} is not here.")
        return
    
    print("Talking to " + str(npc['npc_name']) + ": " + str(npc['npc_desc']))
    print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][0]))
    print(str(npc['npc_name']) + "says: " + str(npc['npc_dialogue'][7]))
    ### Display NPC dialogue options ###
    ### https://www.geeksforgeeks.org/enumerate-in-python/# ###
    ### https://stackoverflow.com/questions/22171558/what-does-enumerate-mean ###
    ### Used some ChatGPT to help make this portion; had no clue where to start ###
    for i, dialogue in enumerate(npc['npc_interact']):
        print(f"{i + 1}. {dialogue}")    
    # Get player's choice
    while True:
        try:
            choice = int(input("Choose an option: ")) - 1
            
            if choice < 0 or choice >= len(npc['npc_interact']):
                print("Invalid choice.")
                continue  # Continue to the next loop iteration for a valid choice
            selected_dialogue = npc['npc_interact'][choice]
            print("You chose: " + str(selected_dialogue))
            
            # Handle interactions based on the selected dialogue
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
                            ### https://www.w3schools.com/python/ref_keyword_continue.asp ###
                            if choice < 0 or choice >= len(npc['npc_interact_2']):
                                print("Invalid choice.")
                                continue  # Continue to the next loop iteration for a valid choice
                            
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
                        loop_breaker = True
                        return loop_breaker
                    if loop_breaker == True:
                        break
        except:
            print("Invalid input. Please enter a number.")
                
                
def damage(hp, damage_type):
    ### FIX insight for if flame and stick are in inventory later; YOU GET SIDETRACKED JOSHUA ###
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
            
#### Add in more items bucko to the game; or delete the extra items. I say don't add in too much due to wanting the game to be a bit hard like a souls-like ###    
def edible(x):
    if x not in ["apple", "rice", "green herb", "health potion", "green potion"]:
        return False
    else:
        return True  

if config_file == "mind_of_husk_config.txt":
    print("\t"+str(game_settings["game_name"]) + "\t")
    print("\tMade from the mind of Joshua Farmer and copious amounts of passion/caffeine")
    print("")
    ###Opening of game and logic###
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
                    print("You have firmed your resolve. Take this apple. Eat it to gather your strength. \n *Hint: You can use the eat command to eat certain things in your inventory*")
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
                    print("Health:",hp)
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
                        current_location = map_movement("r_north",current_location, game_sizex, game_sizey)
                        if "flame" in inv:
                            hp = damage(hp, "flame")
                        elif "Stick of pain" in inv:
                            hp = damage(hp, "Stick of pain")
                        print_location_info(current_location)
                    elif item.lower() == "east":
                        current_location = map_movement("r_east",current_location, game_sizex, game_sizey)
                        if "flame" in inv:
                            hp = damage(hp, "flame")
                        elif "Stick of pain" in inv:
                            hp = damage(hp, "Stick of pain")
                        print_location_info(current_location)
                    elif item.lower() == "west":
                        current_location = map_movement("r_west",current_location, game_sizex, game_sizey)
                        if "flame" in inv:
                            hp = damage(hp, "flame")
                        elif "Stick of pain" in inv:
                            hp = damage(hp, "Stick of pain")
                        print_location_info(current_location)
                    elif item.lower() == "south":
                        current_location = map_movement("r_south",current_location, game_sizex, game_sizey)
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
                            take(current_location, item, locations_dict)  # Added locations_dict as a parameter

                if look.lower() in cmd.lower()[0:6]:
                        item = cmd[7:].strip()
                        search(current_location)  # No need for an item parameter, just the current location
                elif lose.lower() in cmd.lower()[0:4]:
                        item = cmd[5:].strip()
                        if item == "":
                            print("Specify what you want to drop.")
                        else:
                            drop(current_location, item)  # Added locations_dict as a parameter
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
                    print("Health:",hp)
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
                        current_location = map_movement("r_north",current_location, game_sizex, game_sizey)
                        print_location_info(current_location)
                    elif item.lower() == "east":
                        current_location = map_movement("r_east",current_location, game_sizex, game_sizey)
                        print_location_info(current_location)
                    elif item.lower() == "west":
                        current_location = map_movement("r_west",current_location, game_sizex, game_sizey)
                        print_location_info(current_location)
                    elif item.lower() == "south":
                        current_location = map_movement("r_south",current_location, game_sizex, game_sizey)
                        print_location_info(current_location)
                elif get.lower() in cmd.lower()[0:4]:
                        item = cmd[5:].strip()
                        if item == "":
                            print("Specify what you want taken.")
                        else:
                            take(current_location, item, locations_dict)  # Added locations_dict as a parameter

                if look.lower() in cmd.lower()[0:6]:
                        item = cmd[7:].strip()
                        search(current_location)  # No need for an item parameter, just the current location
                elif lose.lower() in cmd.lower()[0:4]:
                        item = cmd[5:].strip()
                        if item == "":
                            print("Specify what you want to drop.")
                        else:
                            drop(current_location, item)  # Added locations_dict as a parameter

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
