import json

from sessions import session, save_session
from get_game_config import get_name_from_item_id, get_attribute_from_item_id, get_attribute_from_goal_id, get_xp_from_level, get_weekly_reward_length
from constants import Constant
from engine import timestamp_now, apply_resources, map_add_item, map_add_item_from_item, map_get_item, map_pop_item, map_delete_item, push_unit, pop_unit

def command(USERID, data):
    first_number = data["first_number"]
    publishActions = data["publishActions"]
    timestamp = data["ts"]
    tries = data["tries"]
    accessToken = data["accessToken"]
    commands = data["commands"]

    for i, comm in enumerate(commands):
        map_id = comm[0]
        cmd = comm[1]
        args = comm[2]
        resources_changed = comm[3]

        # print(f"map_id = {comm[0]}") # I think this is map ID, in SW this is always 0
        # print(f"cmd = {comm[1]}")
        # print(f"args = {comm[2]}")
        # print(f"resources_changed = {comm[3]}") # So this seems to be resource modifications, because some commands don't send any args, like weekly_reward and set_variables

        do_command(USERID, map_id, cmd, args, resources_changed)
    save_session(USERID) # Save session

def do_command(USERID, map_id, cmd, args, resources_changed):
    save = session(USERID)
    time_now = timestamp_now()
    map = save["maps"][map_id]
    print (" [+] COMMAND: ", cmd, "(", args, ") -> ", sep='', end='')

    apply_resources(save, map, resources_changed)

    if cmd == "buy":
        item_index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        playerID = args[4] # player team
        orientation = args[5]
        unknown = args[6]
        reason = args[7]

        map_add_item(map, item_index, item_id, x, y, orientation=orientation, player=playerID)

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

        print(f"Goal '", get_attribute_from_goal_id(goal_id, "title"), "' completed.", sep='')

    elif cmd == "level_up":
        new_level = args[0]

        map["level"] = new_level
        print("Level up! New level:", new_level)

    elif cmd == "set_quest_var":
        key = args[0]
        value = args[1]

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

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return
        
        item = map["items"][str(item_index)]
        item_id = item[0]

        print("Collect", str(get_name_from_item_id(item[0])))
    
    elif cmd == "sell":
        item_index = args[0]
        reason = args[1]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return
        
        # Delete item
        name = str(get_name_from_item_id(map["items"][str(item_index)][0]))
        del map["items"][str(item_index)]

        print(f"Remove {name}. Reason: {reason}")
    
    elif cmd == "kill":
        item_index = args[0]
        reason = args[1]
        
        if str(item_index) not in map["items"]:
            print("Error: item not found.")
        
        # Delete item
        name = str(get_name_from_item_id(map["items"][str(item_index)][0]))
        del map["items"][str(item_index)]

        print(f"Kill {name}. Reason: {reason}")
    
    elif cmd == "kill_iid":
        item_id = args[0]
        reason_str = args[1]

        print("Killed", str(get_name_from_item_id(item_id)))

    elif cmd == "batch_remove":
        index_list = json.loads(args[0])

        # Delete items
        for index in index_list:
            if str(index) in map["items"]:
                del map["items"][str(index)]
        
        print(f"Removed {len(index_list)} items.")

    elif cmd == "orient":
        item_index = args[0]
        orientation = args[1]

        if str(item_index) not in map["items"]:
            print("Error: item not found.")
            return
        
        map["items"][str(item_index)][4] = int(orientation)

        print("Rotate", str(get_name_from_item_id(map["items"][str(item_index)][0])))

    elif cmd == "expand":
        expansion = args[0]

        map["expansions"] += [int(expansion)]

        print("Unlocked Expansion", expansion)

    elif cmd == "store_item":
        item_index = args[0]

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
        frame = args[5] # one of these might be timestamp
        unknown_autoactivable_bool = args[6]
        unknown_imgIndex = args[7] # one of these might be timestamp
        name = str(get_name_from_item_id(item_id))

        # Remove from store
        if str(item_id) in map["store"]:
            map["store"][str(item_id)] = max(0, map["store"][str(item_id)] - 1)

        map_add_item(map, item_index, item_id, x, y)

        print(f"Placed stored {name}.")
    
    elif cmd == "sell_stored_item":
        item_id = args[0]
        name = str(get_name_from_item_id(item_id))

        # Remove from store
        if str(item_id) in map["store"]:
            map["store"][str(item_id)] = max(0, map["store"][str(item_id)] - 1)

        print(f"Sell stored {name}.")

    elif cmd == "store_add_items":
        item_id_list = args[0]

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
        save["privateState"]["timeStampDoResearch"][type] = time_now

        print("Research step for", ["Area 51", "Robotic Center"][type])

    elif cmd == "research_buy_step_cash":
        cash = args[0]
        type = args[1] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["timeStampDoResearch"][type] = 0

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
        level = None
        if len(args) > 2:
            level = args[2]
        
        item_properties = map["items"][str(item_index)][6]
        if "xp" not in item_properties:
            item_properties["xp"] = xp_gain
        else:
            item_properties["xp"] += xp_gain

        if level:
            item_properties["level"] = level

        print("Added", xp_gain, "XP to", get_name_from_item_id(map["items"][str(item_index)][0]))

    elif cmd == "set_variables":
        pass

    elif cmd == "weekly_reward":
        if len(args) > 4:
            item_index = args[0]
            item_id = args[1]
            x = args[2]
            y = args[3]
            playerID = args[4] # player team

            map_add_item(map, item_index, item_id, x, y, player=playerID)

            print("Won", str(get_name_from_item_id(item_id)))
        else:
            print("Won resources")

        # Disable Monday bonus until next Monday
        save["privateState"]["timeStampMondayBonus"] = time_now
        # Advance Monday bonus
        save["privateState"]["weeklyRewardIndex"] = (save["privateState"]["weeklyRewardIndex"] + 1) % get_weekly_reward_length()

    elif cmd == "push_unit":
        index_unit = args[0]
        index_building = args[1]

        unit = map_pop_item(map, index_unit)
        building = map_get_item(map, index_building)
        push_unit(unit, building)

        print("Pushed", str(get_name_from_item_id(unit[0])), "to", str(get_name_from_item_id(building[0])))

    elif cmd == "pop_unit":
        index_building = args[0]
        index_unit = args[1]
        item_id = args[2]
        x = args[3]
        y = args[4]
        playerID = args[5] # player team
        unknown = args[6] # unknown

        building = map_get_item(map, index_building)
        unit = pop_unit(building)

        # modify item data
        unit[0] = item_id
        unit[1] = x
        unit[2] = y
        unit[7] = playerID

        map_add_item_from_item(map, index_unit, unit)

        print("Popped", str(get_name_from_item_id(unit[0])), "from", str(get_name_from_item_id(building[0])))

    elif cmd == "activate":
        item_id = args[0]
        activate = args[1]

        item = map["items"][str(item_id)]

        if activate > 0:
            item[3] = time_now
            item[6]["cp"] = args[1]
            print("Activated", str(get_name_from_item_id(item[0])), "Set CP to", str(activate))
        else:
            item[3] = time_now
            item[6] = {}
            print("Deactivated", str(get_name_from_item_id(item[0])))

    elif cmd == "collect_mission":
        next_mission = args[0]
        map["idCurrentMission"] = next_mission
        map["timestampLastChapter"] = time_now
        map["currentQuestVars"] = {}

        print("Advanced to mission", str(next_mission))

    elif cmd == "fast_forward":
        seconds = args[0]

        privateState = save["privateState"]

        map["timestamp"] = max(0, map["timestamp"] - seconds)
        map["timestampLastChapter"] = max(0, map["timestampLastChapter"] - seconds)
        map["timestampLastTreasure"] = max(0, map["timestampLastTreasure"] - seconds)
        map["timestampLastTrade"] = max(0, map["timestampLastTrade"] - seconds)
        privateState["timestampLastBonus"] = max(0, privateState["timestampLastBonus"] - seconds)
        privateState["timeStampMondayBonus"] = max(0, privateState["timeStampMondayBonus"] - seconds)
        privateState["timestampLastAllianceBonus"] = max(0, privateState["timestampLastAllianceBonus"] - seconds)
        privateState["timeStampDartsReset"] = max(0, privateState["timeStampDartsReset"] - seconds)
        privateState["timeStampDartsNewFree"] = max(0, privateState["timeStampDartsNewFree"] - seconds)

        # research timers
        research_timers = privateState["timeStampDoResearch"]
        num_research_timers = len(research_timers)
        i = 0
        while i < num_research_timers:
            research_timers[i] = max(0, research_timers[i] - seconds)
            i += 1

        # map items
        items = map["items"]
        for index in items:
            data = items[index]
            data[3] = max(0, data[3] - seconds)

        # TODO: FF map["questTimes"]

        print(f"Fast forwarded {seconds} seconds")

    else:
        print(f"Unhandled command '{cmd}' -> args", args)
        return