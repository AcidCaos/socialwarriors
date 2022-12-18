import json

from sessions import session, save_session
from get_game_config import get_name_from_item_id, get_attribute_from_item_id, get_attribute_from_goal_id, get_xp_from_level
from constants import Constant
from engine import timestamp_now, apply_cost, apply_collect

def command(USERID, data):
    first_number = data["first_number"]
    publishActions = data["publishActions"]
    timestamp = data["ts"]
    tries = data["tries"]
    accessToken = data["accessToken"]
    commands = data["commands"]

    for i, comm in enumerate(commands):
        unknown_id = comm[0]
        cmd = comm[1]
        args = comm[2]
        unknown_list = comm[3]
        do_command(USERID, unknown_id, cmd, args, unknown_list)
    save_session(USERID) # Save session

def do_command(USERID, __1, cmd, args, __2):
    save = session(USERID)
    print (" [+] COMMAND: ", cmd, "(", args, ") -> ", sep='', end='')

    if cmd == "buy":
        item_index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        playerID = args[4] # player team
        orientation = args[5]
        unknown = args[6]
        reason = args[7]

        map = save["maps"][0]

        if reason == "b":
            # Give player xp
            xp = int(get_attribute_from_item_id(item_id, "xp"))
            map["xp"] += xp
            # Use up resources
            apply_cost(save["playerInfo"], map, item_id)

        # Add item to map
        map["items"][str(item_index)] = [item_id, x, y, 0, orientation, [], {}, playerID]

        print("Add", str(get_name_from_item_id(item_id)), "at", f"({x},{y})")
        return

    elif cmd == "complete_tutorial":
        tutorial_step = args[0]
        print("Tutorial step", tutorial_step, "reached.")
        if tutorial_step >= 25:
            print("Tutorial COMPLETED!")
            save["playerInfo"]["completed_tutorial"] = 1
        return
    
    elif cmd == "set_goals":
        goal_id = args[0]
        progress = json.loads(args[1]) # format: [visited, currentStep]
        save["privateState"]["goals"][goal_id] = progress
        print(f"Goal '", get_attribute_from_goal_id(goal_id, "title"), "' progressed.", sep='')
    
    elif cmd == "complete_goal":
        goal_id = args[0]

        map = save["maps"][0]

        # Reward
        reward = get_attribute_from_goal_id(goal_id, "reward")
        map["gold"] += reward
        print(f"Goal '", get_attribute_from_goal_id(goal_id, "title"), "' completed and rewarded.", sep='')

    elif cmd == "level_up":
        new_level = args[0]

        map = save["maps"][0]

        xp_expected = get_xp_from_level(max(0, new_level - 1))
        map["level"] = new_level
        map["xp"] = max(xp_expected, map["xp"]) # Keep up with XP
        print("Level up! New level:", new_level)

    elif cmd == "set_quest_var":
        key = args[0]
        value = args[1]

        map = save["maps"][0]

        # questVars = {
        #     "id": 0,
        #     "spawned": False,
        #     "ended": False,
        #     "visited": False,
        #     "activators": [],
        #     "boss": [],
        #     "treasure": [],
        #     "killed": []
        # }
        questVars = map["currentQuestVars"]

        # TODO: Check that those values are actually the same
        if key == "id":
            map["idCurrentMission"] = int(value)
        # TODO: What should be there in the first place?
        if not map["currentQuestVars"]:
            map["currentQuestVars"] = {}
        # TODO: Should it be type-parsed?
        map["currentQuestVars"][key] = value
        print(f"Set current quest {key} to '{value}'")

    elif cmd == "move":
        item_index = args[0]
        x = args[1]
        y = args[2]
        frame = args[3]
        string = args[4]

        map = save["maps"][0]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return

        # Move item
        item = map["items"][str(item_index)]
        item[1] = x
        item[2] = y
        print("Move", str(get_name_from_item_id(item[0])), "to", f"({x},{y})")
    
    elif cmd == "collect":
        item_index = args[0]

        map = save["maps"][0]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return
        
        item = map["items"][str(item_index)]
        item_id = item[0]

        # Apply collect
        collect = int(get_attribute_from_item_id(item_id, "collect"))
        collect_type = get_attribute_from_item_id(item_id, "collect_type")
        collect_xp = int(get_attribute_from_item_id(item_id, "collect_xp"))
        max_collects = int(get_attribute_from_item_id(item_id, "max_collects"))

        map["xp"] += collect_xp
        apply_collect(save["playerInfo"], map, collect_type, collect)

        print("Collect", str(get_name_from_item_id(item[0])))
    
    elif cmd == "sell":
        item_index = args[0]
        reason = args[1]

        map = save["maps"][0]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return
        
        # Delete item
        name = str(get_name_from_item_id(map["items"][str(item_index)][0]))
        del map["items"][str(item_index)]

        # TODO: Substract resources

        print(f"Remove {name}. Reason: {reason}")
    
    elif cmd == "kill":
        item_index = args[0]
        reason = args[1]

        map = save["maps"][0]
        
        if str(item_index) not in map["items"]:
            print("Error: item not found.")
        
        # Delete item
        name = str(get_name_from_item_id(map["items"][str(item_index)][0]))
        del map["items"][str(item_index)]

        print(f"Kill {name}. Reason: {reason}")
    
    elif cmd == "kill_iid":
        item_id = args[0]
        reason_str = args[1]

        map = save["maps"][0]

        # XP Reward
        xp_reward = int(get_attribute_from_item_id(item_id, "xp"))
        map["xp"] += xp_reward

        print("Killed", str(get_name_from_item_id(item_id)))

    elif cmd == "batch_remove":
        index_list = json.loads(args[0])

        map = save["maps"][0]

        # Delete items
        for index in index_list:
            if str(index) in map["items"]:
                del map["items"][str(index)]
        
        print(f"Removed {len(index_list)} items.")

    elif cmd == "orient":
        item_index = args[0]
        orientation = args[1]

        map = save["maps"][0]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return
        
        # XP Reward
        map["items"][str(item_index)][4] = int(orientation)

        print("Rotate", str(get_name_from_item_id(map["items"][str(item_index)][0])))

    elif cmd == "expand":
        expansion = args[0]

        map = save["maps"][0]

        map["expansions"] += [int(expansion)]
        # TODO: Substract resources
        print("Unlocked Expansion", expansion)

    elif cmd == "store_item":
        item_index = args[0]

        map = save["maps"][0]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return

        item_id = map["items"][str(item_index)][0]
        name = str(get_name_from_item_id(item_id))

        # Add to store
        if str(item_id) not in map["store"]:
            map["store"][str(item_id)] = 1
        else:
            map["store"][str(item_id)] += 1
        
        # Delete item from map
        del map["items"][str(item_index)]

        print(f"Store {name}.")
    
    elif cmd == "place_stored_item":
        item_index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        playerID = args[4]
        frame = args[5]
        unknown_autoactivable_bool = args[6]
        unknown_imgIndex = args[7]

        map = save["maps"][0]
        name = str(get_name_from_item_id(item_id))

        # Remove from store
        if str(item_id) in map["store"]:
            map["store"][str(item_id)] = max(0, map["store"][str(item_id)] - 1)

        # Add to map
        map["items"][str(item_index)] = [item_id, x, y, 0, 0, [], {}, playerID]

        print(f"Placed stored {name}.")
    
    elif cmd == "sell_stored_item":
        item_id = args[0]

        map = save["maps"][0]
        name = str(get_name_from_item_id(item_id))

        # Remove from store
        if str(item_id) in map["store"]:
            map["store"][str(item_id)] = max(0, map["store"][str(item_id)] - 1)
        
        # TODO: Add resources

        print(f"Sell stored {name}.")

    elif cmd == "store_add_items":
        item_id_list = args[0]

        map = save["maps"][0]
        # Add to store
        for item_id in item_id_list:
            if str(item_id) not in map["store"]:
                map["store"][str(item_id)] = 1
            else:
                map["store"][str(item_id)] += 1

        print("Add to store", ", ".join([get_name_from_item_id(item_id) for item_id in item_id_list]))

    elif cmd == "next_research_step":
        type = args[0] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["researchStepNumber"][type] += 1
        save["privateState"]["timeStampDoResearch"][type] = timestamp_now()

        print("Research step for", ["Area 51", "Robotic Center"][type])

    elif cmd == "research_buy_step_cash":
        cash = args[0]
        type = args[1] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["timeStampDoResearch"][type] = 0

        # Substract cash
        save["playerInfo"]["cash"] = max(0, save["playerInfo"]["cash"] - cash)

        print("Buy research step for", ["Area 51", "Robotic Center"][type])

    elif cmd == "next_research_item":
        type = args[0] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["researchItemNumber"][type] += 1
        save["privateState"]["researchStepNumber"][type] = 0
        save["privateState"]["timeStampDoResearch"][type] = 0

        print("Finished research for", ["Area 51", "Robotic Center"][type])

    elif cmd == "flash_debug":
        cash = args[0]
        unknown = args[1]
        xp = args[2]
        gold = args[3]
        oil = args[4]
        steel = args[5]
        wood = args[6]

        map = save["maps"][0]
        playerInfo = save["playerInfo"]

        # Keep up with resources
        playerInfo["cash"] = cash
        map["xp"] = xp
        map["gold"] = gold
        map["oil"] = oil
        map["steel"] = steel
        map["wood"] = wood

        print("Keep up with resources.")
    
    elif cmd == "add_xp_unit":
        item_index = args[0]
        xp_gain = args[1]
        level = args[2]

        map = save["maps"][0]
        
        item_properties = map["items"][str(item_index)][6]
        if "xp" not in item_properties:
            item_properties["xp"] = xp_gain
        else:
            item_properties["xp"] += xp_gain

        item_properties["level"] = level

        print("Added", xp_gain, "XP to", get_name_from_item_id(map["items"][str(item_index)][0]))
    
    else:
        print(f"Unhandled command '{cmd}' -> args", args)
        return
