import json
import os
import jsonpatch
from bundle import MODS_DIR, CONFIG_DIR, CONFIG_PATCH_DIR

__game_config = json.load(open(os.path.join(CONFIG_DIR, "main.json"), 'r', encoding='utf-8'))

def remove_duplicate_items():
    indexes = {}
    items = __game_config["items"]
    num_duplicate = 0

    while True:
        index = 0
        duplicate = False
        for item in items:
            if item["id"] in indexes:
                del items[indexes[item["id"]]]
                indexes.clear()
                duplicate = True
                num_duplicate += 1
                break

            indexes[item["id"]] = index
            index += 1

        if duplicate:
            continue

        print(f" * Removed {num_duplicate} duplicate items from config patches")
        break

def apply_config_patch(filename):
    patch = json.load(open(filename, 'r'))
    jsonpatch.apply_patch(__game_config, patch, in_place=True)

def patch_game_config():

    for patch_file in os.listdir(CONFIG_PATCH_DIR):
        if patch_file.endswith(".json"):
            f = os.path.join(CONFIG_PATCH_DIR, patch_file)
            apply_config_patch(f)
            print(" * Patch applied:", f)

    if os.path.exists(os.path.join(MODS_DIR, "mods.txt")):
        with open(os.path.join(MODS_DIR, "mods.txt"), "r") as f:
            lines = f.readlines()
            f.close()

        for line in lines:
            mod = line.strip()
            if mod.startswith("#"):
                continue
            if mod != "":
                mod = mod.replace(".json", "")
                mod_path = f"{MODS_DIR}/{mod}.json"
                if os.path.exists(mod_path):
                    apply_config_patch(mod_path)
                    print(" * Mod applied:", mod)
                else:
                    print(" * Mod ERROR: Could not find", mod)

    remove_duplicate_items()

print (" [+] Applying config patches and mods...")
patch_game_config()

def get_game_config() -> dict:
    return __game_config

def game_config() -> dict:
    return get_game_config()

##########
# PLAYER #
##########

def get_xp_from_level(level: int) -> int:
    return __game_config["levels"][int(level)]["exp_required"]

def get_level_from_xp(xp: int) -> int:
    i = 0
    for lvl in __game_config["levels"]:
        if lvl["exp_required"] > int(xp):
            return i
        i += 1
    return 0

#########
# ITEMS #
#########

# ID

items_dict_id_to_items_index = {int(item["id"]): i for i, item in enumerate(__game_config["items"])}

def get_item_from_id(id: int) -> dict:
    items_index = items_dict_id_to_items_index[int(id)] if int(id) in items_dict_id_to_items_index else None
    return __game_config["items"][items_index] if items_index is not None else None

def get_attribute_from_item_id(id: int, attribute_name: str) -> str:
    item = get_item_from_id(id)
    return item[attribute_name] if item and attribute_name in item else None

def get_name_from_item_id(id: int) -> str:
    return get_attribute_from_item_id(id, "name")

# subcat_functional

items_dict_subcat_functional_to_items_index = {int(item["subcat_functional"]): i for i, item in enumerate(__game_config["items"])}

def get_item_from_subcat_functional(subcat_functional: int) -> dict:
    items_index = items_dict_subcat_functional_to_items_index[int(subcat_functional)] if int(subcat_functional) in items_dict_subcat_functional_to_items_index else None
    return __game_config["items"][items_index] if items_index is not None else None

#########
# GOALS #
#########

goals_id_to_goals_index = {int(item["id"]): i for i, item in enumerate(__game_config["goals"])}

def get_goal_from_id(id: int) -> dict:
    items_index = goals_id_to_goals_index[int(id)] if int(id) in goals_id_to_goals_index else None
    return __game_config["goals"][items_index] if items_index is not None else None

def get_attribute_from_goal_id(id: int, attribute_name: str) -> str:
    goal = get_goal_from_id(id)
    return goal[attribute_name] if goal and attribute_name in goal else None

###################
# INVENTORY ITEMS #
###################

def get_inventory_item_name(item: int):
    itemstr = str(item)
    items = __game_config["inventory_items"]
    if itemstr in items:
        return items[itemstr]["name"]
    return None

def get_collection_name(collection: int):
    index = max(0, collection - 1)
    collections = __game_config["collections"]
    if index < len(collections):
        return collections[index]["name"]
    return None

def get_collection_prize(collection: int):
    index = max(0, collection - 1)
    collections = __game_config["collections"]
    if index < len(collections):
        return json.loads(collections[index]["prize"])
    return None

###################
# PREMIUM ACCOUNT #
###################

def get_premium_days(package_index: int):
    packages = __game_config["globals"]["PREMIUM_ACCOUNTS"]
    index = package_index
    if index >= len(packages):
        index = len(packages) - 1
    package = packages[index]
    if "time" in package:
        return package["time"]
    return 0

################################
# WEEKLY REWARD (MONDAY BONUS) #
################################

def get_weekly_reward_length() -> int:
    # This would be better if it was called at the start, instead of being calculated every time
    rewards = __game_config["globals"]["MONDAY_BONUS_REWARDS"]
    length = 1
    for reward in rewards:
        value = reward["value"]
        if type(value) == list:
            length = max(length, len(value))

    return length
