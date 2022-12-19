import time
import json
from get_game_config import get_attribute_from_item_id

def timestamp_now() -> int:
    return int(time.time())

def add_map_item(map: dict, index: int, item: int, x: int, y: int, orientation: int = 0, timestamp: int = timestamp_now(), attr: dict = {}, store: list = [], player: int = 1):
    map["items"][str(index)] = [item, x, y, timestamp, orientation, store, attr, player]

def add_map_item_from_item(map: dict, index: int, item: list):
    map["items"][str(index)] = item

def apply_resources(save: dict, map: dict, resource: list) -> None:
    # So these will be negative if the user used resources and positive if the user gained resources, we can detect cheats by checking if any are less than 0 after applying
    unknown = resource[0]
    xp = resource[1]
    gold = resource[2]
    wood = resource[3]
    oil = resource[4]
    steel = resource[5]
    cash = resource[6]
    mana = resource[7]

    map["xp"] = max(map["xp"] + xp, 0)
    map["gold"] = max(map["gold"] + gold, 0)
    map["wood"] = max(map["wood"] + wood, 0)
    map["oil"] = max(map["oil"] + oil, 0)
    map["steel"] = max(map["steel"] + steel, 0)
    save["playerInfo"]["cash"] = max(save["playerInfo"]["cash"] + cash, 0)
    save["privateState"]["mana"] = max(save["privateState"]["mana"] + mana, 0)
    # map["timestamp"] = timestamp_now()

    # print(f"\n [?] Resources changed\n    Unknown {unknown}\n    Xp {xp}\n    gold {gold}\n    Wood {wood}\n    Oil {oil}\n    Steel {steel}\n    Cash {cash}\n    Mana {mana}")