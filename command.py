import json

from sessions import session, save_session
from get_game_config import get_name_from_item_id, get_attribute_from_item_id, get_attribute_from_goal_id, get_xp_from_level, get_weekly_reward_length, get_inventory_item_name, get_collection_name, get_collection_prize, get_premium_days
from constants import Constant
from engine import timestamp_now, apply_resources, map_add_item, map_add_item_from_item, map_get_item, map_pop_item, map_delete_item, push_unit, pop_unit, add_store_item, remove_store_item, bought_unit_add, unit_collection_complete, set_goals, inventory_set, inventory_add, inventory_remove, add_click, activate_item_click, buy_si_help, finish_si, push_dead_unit, resurrect_hero, push_queue_unit, pop_queue_unit, map_lose_item, push_queue_unit2
from math import ceil

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
        if tutorial_step >= 25 or tutorial_step == 15:
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
            map["idCurrentMission"] = value
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
        
        resurrectable = False
        if reason == "KILL":
            resurrectable = push_dead_unit(save["privateState"], item)
        name = str(get_name_from_item_id(item[0]))
        map_delete_item(map, item_index)

        if resurrectable:
            print(f"Remove {name} (Resurrectable). Reason: {reason}")
        else:
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
        orientation = args[5]
        unknown_autoactivable_bool = args[6]
        unknown_imgIndex = args[7] # one of these might be timestamp
        name = str(get_name_from_item_id(item_id))

        remove_store_item(map, item_id)
        map_add_item(map, item_index, item_id, x, y, orientation=orientation)
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
        _type = args[0] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["researchStepNumber"][_type] += 1
        save["privateState"]["timeStampDoResearch"][_type] = time_now

        print("Research step for", ["Area 51", "Robotic Center"][_type])

    elif cmd == "research_buy_step_cash":
        cash = args[0]
        _type = args[1] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["timeStampDoResearch"][_type] = 0

        print("Buy research step for", ["Area 51", "Robotic Center"][_type])

    elif cmd == "next_research_item":
        _type = args[0] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["researchItemNumber"][_type] += 1
        save["privateState"]["researchStepNumber"][_type] = 0
        save["privateState"]["timeStampDoResearch"][_type] = 0

        print("Finished research for", ["Area 51", "Robotic Center"][_type])

    elif cmd == "reset_research_item":
        _type = args[0] # 0: TYPE_AREA_51 ,  1: TYPE_ROBOTIC

        save["privateState"]["researchItemNumber"][_type] = 0
        save["privateState"]["researchStepNumber"][_type] = 0
        save["privateState"]["timeStampDoResearch"][_type] = 0

        print("Reset research for", ["Area 51", "Robotic Center"][_type])

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

        unit = pop_unit(building, item_id)
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

        map["idCurrentMission"] = str(next_mission)
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

    elif cmd == "darts_reset":
        seed = args[0]

        privateState = save["privateState"]
        privateState["dartsRandomSeed"] = seed
        privateState["dartsBalloonsShot"] = []
        privateState["dartsHasFree"] = True
        privateState["dartsGotExtra"] = False
        privateState["timeStampDartsReset"] = time_now
        privateState["timeStampDartsNewFree"] = time_now

        print(f"Reset Targets (SEED: {seed})")

    elif cmd == "darts_new_free":
        privateState = save["privateState"]
        privateState["dartsHasFree"] = True
        privateState["timeStampDartsNewFree"] = time_now

        print(f"Given free Targets shot")

    elif cmd == "darts_shoot_balloon":
        index = args[0]
        won_extra = args[1]

        privateState = save["privateState"]
        targets = privateState["dartsBalloonsShot"]
        if index not in targets:
            targets.append(index)
        
        privateState["dartsHasFree"] = False
        privateState["timeStampDartsNewFree"] = time_now
        if won_extra:
            privateState["dartsGotExtra"] = True

        if won_extra:
            print(f"Shot Target {index} and won the game!")
        else:
            print(f"Shot Target {index}")

    elif cmd == "buy_premium_account":
        package_index = args[0]
        days = get_premium_days(package_index)

        privateState = save["privateState"]
        ts_premium = privateState["timeStampEndPremium"]
        if time_now >= ts_premium:
            privateState["timeStampEndPremium"] = time_now + days * 86400
            print(f"Bought Premium Account for {days} day(s)")
        else:
            privateState["timeStampEndPremium"] += days * 86400
            print(f"Extended Premium Account for {days} day(s)")

    elif cmd == "resurrect_hero":
        index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        used_syringe = args[4]

        resurrect_hero(save["privateState"], item_id)
        map_add_item(map, index, item_id, x, y)

        print(f"Resurrected", str(get_name_from_item_id(item_id)))

    elif cmd == "set_resource_allies":
        resource = args[0]
        index = args[1]

        item = map_get_item(map, index)
        if item:
            item[3] = time_now
            finish_si(item)
        
        map["resourceAlliesMarket"] = resource
        print("Set Allies Market resource")

    elif cmd == "buy_mana_new":
        print("Bought mana") # Nothing needs to be done here :)

    elif cmd == "buy_magic":
        magic_id = args[0]

        privateState = save["privateState"]
        magics = privateState["magics"]
        if str(magic_id) in magics:
            magics[str(magic_id)] += min(50, magics[str(magic_id)] + 1)
        else:
            magics[str(magic_id)] = 0

        print("Bought magic spell")

    elif cmd == "use_magic":
        magic_id = args[0]

        privateState = save["privateState"]
        magics = privateState["magics"]
        if str(magic_id) in magics:
            magics[str(magic_id)] = min(50, magics[str(magic_id)] + 1)
        else:
            magics[str(magic_id)] = 0
        
        print("Used magic spell")

    elif cmd == "push_queue_unit":
        index = args[0]

        item = map_get_item(map, index)
        if not item:
            print("Error: item not found.")
            return

        push_queue_unit(item)
        print("Pushed unit.")
    
    elif cmd == "push_queue_unit2":
        atom_fusion_index = args[0]
        unit_id = args[1]

        atom_fusion = map_get_item(map, atom_fusion_index)
        if not atom_fusion:
            print("Error: Atom Fusion not found.")
            return
        
        push_queue_unit2(atom_fusion, unit_id)
        print("Pushed", get_name_from_item_id(unit_id), "to Atom Fusion.")

    elif cmd == "pop_queue_unit":
        index = args[0]

        item = map_get_item(map, index)
        if not item:
            print("Error: item not found.")
            return

        pop_queue_unit(item)
        print("Popped unit.")

    elif cmd == "buy_offer_pack":
        package_id = args[0]
        item_list = args[1]

        items = json.loads(item_list)
        for item in items:
            add_store_item(map, item)

        print("Bought Offer Pack")
    
    elif cmd == "buy_powerups":
        powerup_index = args[0]

        # TODO

        print("Buy Atom Fusion PowerUP")
    
    elif cmd == "soulmixer_speedup":
        atom_fusion_index = args[0]

        atom_fusion = map_get_item(map, atom_fusion_index)

        # Quite useless cost calculation for understanding it
        start = atom_fusion[6]["ts"]
        now = timestamp_now()
        sm_training_time = int(get_attribute_from_item_id(atom_fusion[6]["ui"], "sm_training_time"))

        remaining_time = sm_training_time - (now - start)
        cash_cost = ceil(remaining_time / 3600)

        # Set start timestamp to 0 so that if refreshed, the timer will be gone
        atom_fusion[6]["ts"] = 0

        print(f"Buy Atom Fusion Speedup for {get_name_from_item_id(atom_fusion[6]['ui'])}. Cost: {cash_cost} cash.")

    elif cmd == "admin_set_quest_rank":
        quest_index = args[0]
        difficulty = args[1]

        privateState = save["privateState"]
        privateState["questsRank"][str(quest_index)] = difficulty 

    elif cmd == "end_quest":
        response = None

        try:
            response = json.loads(args[0])
        except:
            print("Error: Failed to parse command.")
            return

        if not response:
            print("Error: Failed to parse command.")
            return

        win = False
        duration = 0
        units = None
        _map = 0
        difficulty = None
        voluntary_end = True
        quest_id = None

        if "win" in response:
            win = response["win"]
        if "duration" in response:
            duration = response["duration"]
        if "units" in response:
            units = response["units"]
        if "map" in response:
            _map = response["map"]
        if "difficulty" in response:
            difficulty = max(1, min(3, response["difficulty"]))
        if "voluntary_end" in response:
            voluntary_end = response["voluntary_end"]
        if "quest_id" in response:
            quest_id = response["quest_id"]

        # Lost units
        privateState = save["privateState"]
        for unit in units:
            # item_id (not on map), sent_to_battle, A, B 
            lost = max(0, unit[2] - unit[3]) # number of loses is A - B
            if lost > 0:
                item = unit[0]
                print(f"Lost {lost} {get_name_from_item_id(unit[0])}(s)")
                map_lose_item(map, privateState, unit[0], lost)

        if not quest_id:
            print("Error: No quest played.")
            return
        
        map["questTimes"][str(quest_id)] = time_now
        if win:
            print(f"Won quest {quest_id}")
        else:
            print(f"Failed quest {quest_id}")

    elif cmd == "end_attack":
        response = None
        unknown = args[1]

        try:
            response = json.loads(args[0])
        except:
            print("Error: Failed to parse command.")
            return

        if not response:
            print("Error: Failed to parse command.")
            return

        # TODO: Parse more data in the future
        # TODO: Affect victim player save
        # TODO: Attack logs
        
        voluntary_end = True
        victim = None # Victim info
        attacker = None # Attacker info
        resources = None # Which resources the attacker won
        honor = 0 # Honor increase
        duration = 0
        townhall_gold = 0 # How much gold was taken from town hall?
        win = False
        different_island = True
        victim_units = None
        attacker_units = None
        resources_victim = None # Subtract these from victim

        if "voluntary_end" in response:
            voluntary_end = response["voluntary_end"]
        if "victim" in response:
            victim = response["victim"]
        if "attacker" in response:
            attacker = response["attacker"]
        if "resources" in response:
            resources = response["resources"]
        if "honor" in response:
            honor = response["honor"]
        if "duration" in response:
            duration = response["duration"]
        if "townhall_gold" in response:
            townhall_gold = response["townhall_gold"]
        if "win" in response:
            win = response["win"]
        if "different_island" in response:
            different_island = response["different_island"]
        if "victim_units" in response:
            victim_units = response["victim_units"]
        if "attacker_units" in response:
            attacker_units = response["attacker_units"]
        if "resources_victim" in response:
            resources_victim = response["resources_victim"]
        
        # Lost units
        privateState = save["privateState"]
        for unit in attacker_units:
            # item_id (not on map), sent_to_battle, A, B 
            lost = max(0, unit[2] - unit[3]) # number of loses is A - B
            if lost > 0:
                item = unit[0]
                print(f"Lost {lost} {get_name_from_item_id(unit[0])}(s)")
                map_lose_item(map, privateState, unit[0], lost)

        if "name" in victim:
            name = victim["name"]
            if win:
                print(f"Won battle against {name}")
            else:
                print(f"Lost battle against {name}")
        else:
            if win:
                print(f"Won battle")
            else:
                print(f"Lost battle")

    elif cmd == "rt_open_graph_unit":
        item = args[0]

        privateState = save["privateState"]
        if "publishedOpenGraphUnit" not in privateState:
            privateState["publishedOpenGraphUnit"] = []
        if type(privateState["publishedOpenGraphUnit"]) != list:
            privateState["publishedOpenGraphUnit"] = []
        if str(item) not in privateState["publishedOpenGraphUnit"]:
            privateState["publishedOpenGraphUnit"].append(str(item))
        
        print(f"Open Unit Graph for {get_name_from_item_id(item)}")

    elif cmd == "first_time_marketplace":
        privateState = save["privateState"]
        privateState["marketPlaceFirstTime"] = True
        
        print("Seen Auction House")

    elif cmd == "fast_forward":
        seconds = args[0]

        privateState = save["privateState"]

        map["timestamp"] = max(0, map["timestamp"] - seconds)
        map["timestampLastChapter"] = max(0, map["timestampLastChapter"] - seconds)
        map["timestampLastTreasure"] = max(0, map["timestampLastTreasure"] - seconds)
        map["timestampLastTrade"] = max(0, map["timestampLastTrade"] - seconds)
        privateState["timestampLastBonus"] = max(0, privateState["timestampLastBonus"] - seconds)
        # privateState["timeStampMondayBonus"] = max(0, privateState["timeStampMondayBonus"] - seconds) # don't process weekly things
        privateState["timestampLastAllianceBonus"] = max(0, privateState["timestampLastAllianceBonus"] - seconds)
        # privateState["timeStampDartsReset"] = max(0, privateState["timeStampDartsReset"] - seconds) # don't process weekly things
        privateState["timeStampDartsNewFree"] = max(0, privateState["timeStampDartsNewFree"] - seconds)
        privateState["tsAttacksReset"] = max(0, privateState["tsAttacksReset"] - seconds)
        privateState["tsSpyingsReset"] = max(0, privateState["tsSpyingsReset"] - seconds)

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

            # building timers (atom fusion)
            if data[6]:
                if "ts" in data[6]:
                    data[6]["ts"] = max(0, data[6]["ts"] - seconds)

        # quest times
        questTimes = map["questTimes"]
        for key in questTimes:
            questTimes[key] = max(0, questTimes[key] - seconds)

        print(f"Fast forwarded {seconds} seconds")

    elif cmd == "ping":
        print("Pong")

    elif cmd == "set_variables":
        print("Set player resources")

    else:
        print(f"Unhandled command '{cmd}' -> args", args)
        return