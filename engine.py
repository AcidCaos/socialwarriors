import time
import json
from get_game_config import get_attribute_from_item_id

def timestamp_now() -> int:
    return int(time.time())

def apply_cost(playerInfo: dict, map: dict, item_id: int) -> None:
    costs_str = get_attribute_from_item_id(item_id, "costs")
    if costs_str:
        costs = json.loads(costs_str)
        if "w" in costs:
            map["wood"] = max(map["wood"] - costs["w"], 0)
        if "g" in costs:
            map["gold"] = max(map["gold"] - costs["g"], 0)
        if "s" in costs:
            map["steel"] = max(map["steel"] - costs["s"], 0)
        if "c" in costs:
            playerInfo["cash"] = max(playerInfo["cash"] - costs["c"], 0)
        if "o" in costs:
            map["oil"] = max(map["oil"] - costs["o"], 0)
