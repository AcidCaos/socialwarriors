import json

from sessions import session, save_session
from get_game_config import get_name_from_item_id, get_attribute_from_item_id, get_attribute_from_goal_id, get_xp_from_level, get_weekly_reward_length, get_inventory_item_name, get_collection_name, get_collection_prize
from constants import Constant
from engine import timestamp_now, apply_resources, map_add_item, map_add_item_from_item, map_get_item, map_pop_item, map_delete_item, push_unit, pop_unit, add_store_item, remove_store_item, bought_unit_add, unit_collection_complete, set_goals, inventory_set, inventory_add, inventory_remove, add_click, activate_item_click, buy_si_help, finish_si

def command(USERID, data):
    first_number = data["first_number"]
    publishActions = data["publishActions"]
    timestamp = data["ts"]
    tries = data["tries"]
    accessToken = data["accessToken"]
    commands = data["commands"]

    # print(f"Number of commands to execute: {len(commands)}")

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

        if playerID == 1:
            bought_unit_add(save, item_id)

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

        set_goals(save["privateState"], goal_id, progress)

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

        if key == "idSimpleChapter":
            # The game will reset chapter past on chapters 9 and above
            # So we're gonna ignore this key to allow the player to play up to chapter 99, after that it will reset to chapter 1
            print(f"Ignored {key}")
            return

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

        item = map_get_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return

        # Move item
        item[1] = x
        item[2] = y
        print("Move", str(get_name_from_item_id(item[0])), "to", f"({x},{y})")
    
    elif cmd == "collect":
        item_index = args[0]

        item = map_get_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return

        # Update collect timers
        item[3] = time_now

        print("Collect", str(get_name_from_item_id(item[0])))
    
    elif cmd == "sell":
        item_index = args[0]
        reason = args[1]

        item = map_get_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return
        
        name = str(get_name_from_item_id(item[0]))
        map_delete_item(map, item_index)

        print(f"Remove {name}. Reason: {reason}")
    
    elif cmd == "kill":
        item_index = args[0]
        reason = args[1]
        
        item = map_get_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return
        
        name = str(get_name_from_item_id(item[0]))
        map_delete_item(map, item_index)

        print(f"Kill {name}. Reason: {reason}")
    
    elif cmd == "kill_iid":
        item_id = args[0]
        reason_str = args[1]

        print("Killed", str(get_name_from_item_id(item_id)))

    elif cmd == "batch_remove":
        index_list = json.loads(args[0])

        # Delete items
        for index in index_list:
            map_delete_item(map, index)
        
        print(f"Removed {len(index_list)} items.")

    elif cmd == "orient":
        item_index = args[0]
        orientation = args[1]

        item = map_get_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return
        
        item[4] = int(orientation)

        print("Rotate", str(get_name_from_item_id(item[0])))

    elif cmd == "expand":
        expansion = args[0]

        map["expansions"] += [int(expansion)]

        print("Unlocked Expansion", expansion)

    elif cmd == "store_item":
        item_index = args[0]

        item = map_pop_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return

        item_id = item[0]
        name = str(get_name_from_item_id(item_id))

        add_store_item(map, item_id)

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

        remove_store_item(map, item_id)
        map_add_item(map, item_index, item_id, x, y)
        bought_unit_add(save, item_id)

        print(f"Placed stored {name}.")
    
    elif cmd == "sell_stored_item":
        item_id = args[0]
        name = str(get_name_from_item_id(item_id))

        remove_store_item(map, item_id)

        print(f"Sell stored {name}.")

    elif cmd == "store_add_items":
        item_id_list = args[0]

        # Add to store
        for item_id in item_id_list:
            add_store_item(map, item_id)
            bought_unit_add(save, item_id)

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

    elif cmd == "reset_research_item":
        type = args[0] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["researchItemNumber"][type] = 0
        save["privateState"]["researchStepNumber"][type] = 0
        save["privateState"]["timeStampDoResearch"][type] = 0

        print("Reset research for", ["Area 51", "Robotic Center"][type])

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
        
        item = map_get_item(map, item_index)
        if not item:
            print("Error: item not found.")
            return

        attr = item[6]
        if "xp" not in attr:
            attr["xp"] = xp_gain
        else:
            attr["xp"] += xp_gain

        if level:
            print(f"{get_name_from_item_id(item[0])} +{xp_gain}xp BOUGHT LEVEL UP -> {level}")
        else:
            print(f"{get_name_from_item_id(item[0])} +{xp_gain}xp")

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
            bought_unit_add(save, item_id)

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

        if not unit:
            print("Error: unit not found.")
            return
        if not building:
            print("Error: building not found.")
            return

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
        if not building:
            print("Error: building not found.")
            return

        unit = pop_unit(building)
        if not unit:
            print("Error: no units in building.")
            return

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

        item = map_get_item(map, item_id)
        if not item:
            print("Error: item not found.")
            return

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
        if next_mission > 99:
            # chapters 1 - 8 are scripted
            # starting chapters 9+ works, the game has 90 entries so there's technically infinite chapters
            # so I'm not sure what to do, so I'm going to allow a restart after chapter 99, the next chapter will be 1
            next_mission = 1

        map["idCurrentMission"] = next_mission
        map["timestampLastChapter"] = time_now
        map["currentQuestVars"] = {}

        print("Advanced to mission", str(next_mission))

    elif cmd == "win_daily_bonus":
        item = args[0]
        next_id = args[1] + 1

        privateState = save["privateState"]

        # Advance & Reset dailies
        if next_id > 5:
            next_id = 1

        privateState["timestampLastBonus"] = time_now
        privateState["bonusNextId"] = next_id

        # Daily gives an item
        if item > 0:
            bought_unit_add(save, item)
            add_store_item(map, item)
            print("Put", str(get_name_from_item_id(item)), "in storage")
        else:
            print("Rewarded resources")

    elif cmd == "trade_resource":
        resource_type = args[0]
        sold = args[1] # 1 if sold, 2 if bought

        num_trades = map["numTradesDone"] + 1
        map["numTradesDone"] = min(20, num_trades)
        map["timestampLastTrade"] = time_now

        print(f"Remaining trades: {20-num_trades}")

    elif cmd == "buy_stored_item_cash":
        item_id = args[0]

        bought_unit_add(save, item_id)
        add_store_item(map, item_id)
        print("Bought", str(get_name_from_item_id(item_id)), "from unit collection")

    elif cmd == "unit_collections_completed":
        collection_id = args[0]

        unit_collection_complete(save, collection_id)
        print("Completed unit collection", str(collection_id))

    elif cmd == "add_inventory_item":
        item = args[0]
        quantity = args[1]

        inventory_add(save["privateState"], item, quantity)
        name = get_inventory_item_name(item)
        print(f"Added {quantity} {name} to inventory")

    elif cmd == "remove_inventory_item":
        item = args[0]
        quantity = args[1]

        inventory_remove(save["privateState"], item, quantity)
        name = get_inventory_item_name(item)
        print(f"Removed {quantity} {name} from inventory")

    elif cmd == "complete_collection":
        collection_id = args[0]
        bought = args[1]

        privateState = save["privateState"]

        prize = get_collection_prize(collection_id)

        for key in prize:
            add_store_item(map, int(key), prize[key])

        collection_name = get_collection_name(collection_id)

        if collection_id not in privateState["collections"]:
            privateState["collections"].append(collection_id)

        if bought:
            print(f"Bought {collection_name}")
        else:
            print(f"Completed {collection_name}")

    elif cmd == "add_click":
        index = args[0]

        item = map_get_item(map, index)
        if not item:
            print("Error: item not found.")
            return

        add_click(item)

        print("Added click to", str(get_name_from_item_id(item[0])))

    elif cmd == "activate_item_click":
        index = args[0]

        item = map_get_item(map, index)
        if not item:
            print("Error: item not found.")
            return

        activate_item_click(item)

        print("Click to build finished for", str(get_name_from_item_id(item[0])))

    elif cmd == "buy_si_help":
        index = args[0]

        item = map_get_item(map, index)
        if not item:
            print("Error: item not found.")
            return

        buy_si_help(item)

        print("Bought SI help for", str(get_name_from_item_id(item[0])))

    elif cmd == "finish_si":
        index = args[0]

        item = map_get_item(map, index)
        if not item:
            print("Error: item not found.")
            return

        finish_si(item)

        print("Finished SI for", str(get_name_from_item_id(item[0])))

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