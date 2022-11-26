
from sessions import session, save_session
from get_game_config import get_game_config, get_level_from_xp, get_name_from_item_id, get_attribute_from_mission_id, get_xp_from_level, get_attribute_from_item_id, get_item_from_subcat_functional
from constants import Constant
from engine import timestamp_now

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

    if cmd == "stub":
        print(" ".join(args))

    elif cmd == "buy":
        # args[0] - command order id (can be ignored for now)
        # args[1] - item_id
        # args[2] - map tile x
        # args[3] - map tile y
        # args[4] - player_team
        # args[5] - orientation
        # args[6] - unknown
        # args[7] - buy reason, "b" is when player buys the item from the shop for resources
        # print(f"\nitem={args[1]}\nx={args[2]}\ny={args[3]}\norientation={args[5]}\nplayerID={args[4]}\nreason={args[7]}")

        town_id = 0 # In Social Wars there's no multiple maps thing, but maybe it's args[6]

        map = save["maps"][town_id]
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
            # TODO: Use up resources

        # Add item to map
        map["items"] += [ [item_id, x, y, 0, orientation, [], {}, playerID] ]

        print("Add", str(get_name_from_item_id(item_id)), "at", f"({x},{y})")
        return

    elif cmd == "complete_tutorial":
        tutorial_step = args[0]
        print("Tutorial step", tutorial_step, "reached.")
        if tutorial_step >= 25:
            print("Tutorial COMPLETED!")
            save["playerInfo"]["completed_tutorial"] = 1
            save["privateState"]["dragonNestActive"] = 1 # I assume this is also valid for Social Wars?
        return

    else:
        print(f"Unhandled command '{cmd}' -> args", args)
        return
