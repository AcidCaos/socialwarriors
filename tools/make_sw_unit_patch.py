import os
import json
import copy

# CONFIG
patch_filename = "../config/patch/unit_patch.json"
output_storage = "unit_patch_storage.json" # drop in save to add all patched units to storage
input_csv = "sw_unit_patch.csv"

# DO THE THING
templates = json.load(open("unit_templates.json", 'r', encoding='utf-8'))

lines = []
patch = []
storage = {}
if os.path.exists(input_csv):
    with open(input_csv, "r") as f:
        lines = f.readlines()
        f.close()

def trimquotes(inputstr: str):
    new = inputstr
    while not new.startswith("{"):
        new = inputstr[1:]
    while not new.endswith("}"):
        new = new [:-1]
    return new

for line in lines:
    col = line.split("\t")

    ITEM_ID = col[0]
    ITEM_ASSET = col[1]
    ITEM_NAME = col[2]
    ITEM_HEALTH = col[3]
    ITEM_ATTACK = col[4]
    ITEM_RANGE = col[5]
    ITEM_SPEED = col[6]
    ITEM_INTERVAL = col[7]
    ITEM_POPULATION = col[8]
    ITEM_SYRINGES = col[9]
    ITEM_XP = col[10]
    ITEM_COST = trimquotes(col[11])
    ITEM_GROUP = col[12]
    ITEM_PROPERTIES = trimquotes(col[13])

    if ITEM_ASSET == "":
        print(f"{ITEM_NAME} Failed - Asset missing")
        continue

    if ITEM_GROUP not in templates:
        print(f"{ITEM_NAME} Failed - Template {ITEM_GROUP} not found")
        continue

    # Fetch from template
    template = templates[ITEM_GROUP]
    item = copy.deepcopy(template)

    # Update data
    item["id"] = str(ITEM_ID)
    item["img_name"] = str(ITEM_ASSET)
    item["name"] = str(ITEM_NAME)
    item["life"] = str(ITEM_HEALTH)
    item["attack"] = str(ITEM_ATTACK)
    item["attack_range"] = str(ITEM_RANGE)
    item["velocity"] = str(ITEM_SPEED)
    item["attack_interval"] = str(ITEM_INTERVAL)
    item["population"] = str(ITEM_POPULATION)
    item["syringes"] = str(ITEM_SYRINGES)
    item["xp"] = str(ITEM_XP)
    item["costs"] = ITEM_COST.replace("\\","")
    item["properties"] = ITEM_PROPERTIES.replace("\\","")

    # Create patch
    p = {}
    p["op"] = "add"
    p["path"] = "/items/-"
    p["value"] = item

    # Append to patch
    patch.append(p)
    # Append to storage
    storage[str(ITEM_ID)] = 1

    print(f"Made patch for {ITEM_NAME}")

if len(patch) > 0:
    with open(patch_filename, 'w') as f:
        json.dump(patch, f)
    with open(output_storage, 'w') as f:
        json.dump(storage, f)
        print(f"Created patch for {len(patch)} items to {patch_filename}!")
else:
    print("Patch creation failed!")