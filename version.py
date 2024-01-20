from engine import timestamp_now

version_name = "alpha 0.02"
version_code = "0.02a"

def migrate_loaded_save(save: dict):
    
    # 0.01a saves
    _changed = False
    if "version" not in save or save["version"] is None:
        _changed = True
        save["version"] = "0.01a"
        print(" [!] Applied version to save")

    privateState = save["privateState"]
    maps = save["maps"]

    # 0.01a fixes
    if save["version"] == "0.01a":
        if "inventoryItems" not in privateState:
            privateState["inventoryItems"] = None
        if type(privateState["inventoryItems"]) != dict:
            _changed = True
            privateState["inventoryItems"] = {}
            print(" [!] Applied inventory fix")
        if "deadHeroes" not in privateState:
            privateState["deadHeroes"] = None
        if type(privateState["deadHeroes"]) != dict:
            _changed = True
            privateState["deadHeroes"] = {}
            print(" [!] Applied hospital fix")
        if "magics" not in privateState:
            privateState["magics"] = None
        if type(privateState["magics"]) != dict:
            _changed = True
            privateState["magics"] = {}
            print(" [!] Applied magics fix")
        for map in maps:
            if "questTimes" not in map:
                map["questTimes"] = None
            if type(map["questTimes"]) != dict:
                _changed = True
                map["questTimes"] = {}
                print(" [!] Applied quest fix")
    
    # 0.02a migration
    if save["version"] == "0.01a":
        _changed = True
        save["version"] = "0.02a"

    return _changed