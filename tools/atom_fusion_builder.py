import json
import jsonpatch
import math

# Load config
config = json.load(open("../config/main.json"))

# Apply required previous patches
patch = json.load(open("../config/patch/atom_fusion_item.json", 'r'))
jsonpatch.apply_patch(config, patch, in_place=True)
patch = json.load(open("../config/patch/unit_patch.json", 'r'))
jsonpatch.apply_patch(config, patch, in_place=True)

# Load list of excluded units from Atom Fusion
exclude_list = json.load(open("atom_fusion_excluded_units.json", 'r'))

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
	# explicit exclusions
	if item["id"] in exclude_list:
		# print(f'Excluded [{item["id"]}]{item["name"]}')
		continue

	# some config values for the formula
	a = int(item["attack"])
	ar = int(item["attack_range"])
	ai = int(item["attack_interval"])
	d = int(item["defense"])
	l = int(item["life"])
	v = int(item["velocity"])

	# some way to approximate power (aka breeding order)
	#breeding_order = int( (10 * a * ar)/(ai + 1) + (10 * d) + (l/100) + v )

	dps = a / (ai / 30)

	breeding_order = 1
	if l > 8000: # TIER 4
		breeding_order = int(max(220, min(2000, -510 + pow(l / 900, 3) + pow(dps * 1, 0.5))))
	elif l > 2500: # TIER 3
		breeding_order = int(max(150, min(219, 150 + pow(l / 1100, 2) + pow(dps * 1, 0.5))))
	elif l > 1600: # TIER 2
		breeding_order = int(max(75, min(149, 10 + pow(l / 225, 2) + pow(dps * 5, 0.5))))
	else: # TIER 1
		breeding_order = int(max(1, min(74, -4 + pow(l / 200, 2) + pow(dps * 5, 0.5))))
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

	print(f'{breeding_order} = [{item["id"]}]{item["name"]}')

	patch_str += ("[" if bool_first else ",") + "\n\n" + json.dumps(patch_breeding_order) + ",\n" + json.dumps(sm_training_time_order)
	bool_first = False

patch_str += "\n\n]"

# write patch file
fd = open("../config/patch/atom_fusion_items_data.json", 'w')
fd.write(patch_str)
fd.close()