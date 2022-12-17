import json

from sessions import session, save_session
from get_game_config import get_name_from_item_id, get_attribute_from_item_id, get_attribute_from_goal_id, get_xp_from_level
from constants import Constant
from engine import timestamp_now, apply_cost

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
        # args[0] - map key/id for the item
        # args[1] - item_id
        # args[2] - map tile x
        # args[3] - map tile y
        # args[4] - player_team
        # args[5] - orientation
        # args[6] - unknown
        # args[7] - buy reason, "b" is when player buys the item from the shop for resources
        # print(f"\nitem={args[1]}\nx={args[2]}\ny={args[3]}\norientation={args[5]}\nplayerID={args[4]}\nreason={args[7]}")

        map = save["maps"][0]
        
        map_item_index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        playerID = args[4]
        orientation = args[5]
        unknown = args[6]
        reason = args[7]

        if reason == "b":
            # Give player xp
            xp = int(get_attribute_from_item_id(item_id, "xp"))
            map["xp"] += xp
            # Use up resources
            apply_cost(save["playerInfo"], map, item_id)

        # Add item to map
        map["items"][str(map_item_index)] = [item_id, x, y, 0, orientation, [], {}, playerID]

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
        # Reward
        reward = get_attribute_from_goal_id(goal_id, "reward")
        map = save["maps"][0]
        map["gold"] += reward
        print(f"Goal '", get_attribute_from_goal_id(goal_id, "title"), "' completed and rewarded.", sep='')

    elif cmd == "move":
        map_item_index = args[0]
        x = args[1]
        y = args[2]
        frame = args[3]
        string = args[4]

        # Move item
        map = save["maps"][0]
        item = map["items"][str(map_item_index)]
        item[1] = x
        item[2] = y
        print("Move", str(get_name_from_item_id(item[0])), "to", f"({x},{y})")

    elif cmd == "kill_iid":
        item_id = args[0]
        reason_str = args[1]

        # XP Reward
        map = save["maps"][0]
        xp_reward = int(get_attribute_from_item_id(item_id, "xp"))
        map["xp"] += xp_reward

        print("Killed", str(get_name_from_item_id(item_id)))

    else:
        print(f"Unhandled command '{cmd}' -> args", args)
        return
