import json
import jsonpatch

config = json.load(open("./config/main.json"))

# Apply required previous patches
patch = json.load(open("./config/patch/atom_fusion_item.json", 'r'))
jsonpatch.apply_patch(config, patch, in_place=True)

patch = json.load(open("./config/patch/unit_patch.json", 'r'))
jsonpatch.apply_patch(config, patch, in_place=True)

patch_str = ""
bool_first = True
for index, item in enumerate(config["items"]):

    # exclude non-unit items
    if item["type"] != "u":
        continue
    # exclude chained promos
    if "chained" in item["name"].lower():
        continue
    # exclude workers
    if item["group_type"] == "WORKER":
        continue
    # exclude drones
    if "drone" in item["name"].lower():
        continue
    # explicit exclusions
    exclude_list = ["1043", "1017"] # 1043-Air Strike, 1017-General Mike
    if item["id"] in exclude_list:
        continue

    # some config values for the formula
    a = int(item["attack"])
    ar = int(item["attack_range"])
    ai = int(item["attack_interval"])
    d = int(item["defense"])
    l = int(item["life"])
    v = int(item["velocity"])

    # some way to approximate power (aka breeding order)
    breeding_order = int( (10 * a * ar)/(ai + 1) + (10 * d) + (l/100) + v )
    sm_training_time = 1000 * breeding_order # in seconds

    # make patch
    patch_breeding_order = {
        "op": "add",
        "path": f"/items/{index}/breeding_order",
        "value": f"{breeding_order}"
    }
    sm_training_time_order = {
        "op": "add",
        "path": f"/items/{index}/sm_training_time",
        "value": f"{sm_training_time}"
    }

    patch_str += ("[" if bool_first else ",") + "\n\n" + json.dumps(patch_breeding_order) + ",\n" + json.dumps(sm_training_time_order)
    bool_first = False

patch_str += "\n\n]"

# write patch file
fd = open("./config/patch/atom_fusion_items_data.json", 'w')
fd.write(patch_str)
fd.close()