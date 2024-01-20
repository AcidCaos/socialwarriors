import json
import os
import copy
import uuid
import random
from flask import session

from version import version_code
from engine import timestamp_now
from version import migrate_loaded_save
from constants import Quests
from bundle import VILLAGES_DIR, QUESTS_DIR, SAVES_DIR

__villages = {}  # ALL static neighbors
__quests = {}  # ALL static quests
__saves = {}  # ALL saved villages
'''__saves = {
    "USERID_1": {
        "playerInfo": {.
            ...
            "pid": "USERID_1",
            ...
        },
        "maps": [{...},{...}]
        "privateState": {...}
    },
    "USERID_2": {...}
}'''

__initial_village = json.load(open(os.path.join(VILLAGES_DIR, "initial.json")))

# Load saved villages

def load_saves():
    global __saves

    # Empty in memory
    __saves = {}

    # Saves dir check
    if not os.path.exists(SAVES_DIR):
        try:
            print(f"Creating '{SAVES_DIR}' folder...")
            os.mkdir(SAVES_DIR)
        except:
            print(f"Could not create '{SAVES_DIR}' folder.")
            exit(1)
    if not os.path.isdir(SAVES_DIR):
        print(f"'{SAVES_DIR}' is not a folder... Move the file somewhere else.")
        exit(1)

    # Saves in /saves
    for file in os.listdir(SAVES_DIR):
        print(f" * Loading SAVE: village at {file}... ", end='')
        try:
            save = json.load(open(os.path.join(SAVES_DIR, file)))
        except json.decoder.JSONDecodeError as e:
            print("Corrupted JSON.")
            continue
        if not is_valid_village(save):
            print("Invalid Save")
            continue
        USERID = save["playerInfo"]["pid"]
        print("PLAYER USERID:", USERID)
        __saves[str(USERID)] = save
        modified = migrate_loaded_save(save) # check save version for migration
        if modified:
            save_session(USERID)

def load_static_villages():
    global __villages

    # Empty in memory
    __villages = {}

    # Static neighbors in /villages
    for file in os.listdir(VILLAGES_DIR):
        if file == "initial.json" or not file.endswith(".json"):
            continue
        print(f" * Loading STATIC NEIGHBOUR: village at {file}... ", end='')
        village = json.load(open(os.path.join(VILLAGES_DIR, file)))
        if not is_valid_village(village):
            print("Invalid neighbour")
            continue
        USERID = village["playerInfo"]["pid"]
        print("STATIC USERID:", USERID)
        __villages[str(USERID)] = village

def load_quests():
    global __quests

    # Empty in memory
    __quests = {}

    # Static quests in /villages/quest
    for file in os.listdir(QUESTS_DIR):
        print(f" * Loading ", end='')
        village = json.load(open(os.path.join(QUESTS_DIR, file)))
        if not is_valid_village(village):
            print("Invalid Quest")
            continue
        QUESTID = village["playerInfo"]["pid"]
        assert file.split(".")[0] == QUESTID
        quest_name = Quests.QUEST[QUESTID] if QUESTID in Quests.QUEST else "?"
        print(quest_name)
        __quests[str(QUESTID)] = village

# New village

def new_village() -> str:
    # Generate USERID
    USERID: str = str(uuid.uuid4())
    assert USERID not in all_userid()
    # Copy init
    village = copy.deepcopy(__initial_village)
    # Custom values
    village["version"] = None # Do not set version, migrate_loaded_save() does it
    village["playerInfo"]["pid"] = USERID
    village["maps"][0]["timestamp"] = timestamp_now()
    # Make sure that the game will initialize targets by calling darts_reset
    village["privateState"]["timeStampDartsReset"] = 0
    # Migrate it if needed
    migrate_loaded_save(village)
    # Memory saves
    __saves[USERID] = village
    # Generate save file
    save_session(USERID)
    print("Done.")
    return USERID

# Access functions

def all_saves_userid() -> list:
    "Returns a list of the USERID of every saved village."
    return list(__saves.keys())

def all_userid() -> list:
    "Returns a list of the USERID of every village."
    return list(__villages.keys()) + list(__saves.keys()) + list(__quests.keys())

def save_info(USERID: str) -> dict:
    save = __saves[USERID]
    default_map = save["playerInfo"]["default_map"]
    empire_name = str(save["playerInfo"]["name"])
    xp = save["maps"][default_map]["xp"]
    level = save["maps"][default_map]["level"]
    return{"userid": USERID, "name": empire_name, "xp": xp, "level": level}

def all_saves_info() -> list:
    saves_info = []
    for userid in __saves:
        saves_info.append(save_info(userid))
    return list(saves_info)

def session(USERID: str) -> dict:
    assert(isinstance(USERID, str))
    return __saves[USERID] if USERID in __saves else None

def neighbor_session(USERID: str) -> dict:
    assert(isinstance(USERID, str))
    if USERID in __saves:
        return __saves[USERID]
    if USERID in __quests:
        return __quests[USERID]
    if USERID in __villages:
        return __villages[USERID]

def fb_friends_str(USERID: str) -> list:
    friends = []
    # static villages
    for key in __villages:
        vill = __villages[key]
        if vill["playerInfo"]["pid"] == "100000030" \
           or vill["playerInfo"]["pid"] == "100000031": # general Mike
            continue
        frie = {}
        frie["uid"] = vill["playerInfo"]["pid"]
        frie["pic_square"] = vill["playerInfo"]["pic"]
        friends += [frie]
    # other players
    for key in __saves:
        vill = __saves[key]
        if vill["playerInfo"]["pid"] == USERID:
            continue
        frie = {}
        frie["uid"] = vill["playerInfo"]["pid"]
        frie["pic_square"] = vill["playerInfo"]["pic"]
        friends += [frie]
    return friends

def neighbors(USERID: str):
    neighbors = []
    # static villages
    for key in __villages:
        vill = __villages[key]
        if vill["playerInfo"]["pid"] == "100000030" \
           or vill["playerInfo"]["pid"] == "100000031": # general Mike
            continue
        neigh = vill["playerInfo"]
        neigh = json.loads(json.dumps(vill["playerInfo"]))
        neigh["xp"] = vill["maps"][0]["xp"]
        neigh["level"] = vill["maps"][0]["level"]
        neigh["gold"] = vill["maps"][0]["gold"]
        neigh["wood"] = vill["maps"][0]["wood"]
        neigh["oil"] = vill["maps"][0]["oil"]
        neigh["steel"] = vill["maps"][0]["steel"]
        neighbors += [neigh]
    # other players
    for key in __saves:
        vill = __saves[key]
        if vill["playerInfo"]["pid"] == USERID:
            continue
        neigh = json.loads(json.dumps(vill["playerInfo"])) # Stop clogging up playerInfo when just wanting to send some data from save from a neighbour
        neigh["xp"] = vill["maps"][0]["xp"]
        neigh["level"] = vill["maps"][0]["level"]
        neigh["gold"] = vill["maps"][0]["gold"]
        neigh["wood"] = vill["maps"][0]["wood"]
        neigh["oil"] = vill["maps"][0]["oil"]
        neigh["steel"] = vill["maps"][0]["steel"]
        neighbors += [neigh]
    return neighbors

# Check for valid village
# The reason why this was implemented is to warn the user if a save game from Social Empires was used by accident

def is_valid_village(save: dict):
    if "playerInfo" not in save or "maps" not in save or "privateState" not in save:
        # These are obvious
        return False
    for map in save["maps"]:
        if "oil" not in map or "steel" not in map:
            return False
        if "stone" in map or "food" in map:
            return False
        if "items" not in map:
            return False
        if type(map["items"]) != dict:
            return False

    return True

# Persistency

def backup_session(USERID: str):
    # TODO 
    return

def save_session(USERID: str):
    # TODO 
    file = f"{USERID}.save.json"
    print(f" * Saving village at {file}... ", end='')
    village = session(USERID)
    with open(os.path.join(SAVES_DIR, file), 'w') as f:
        json.dump(village, f, indent=4)
    print("Done.")
