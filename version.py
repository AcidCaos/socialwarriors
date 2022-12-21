from engine import timestamp_now

version_name = "pre-alpha 0.01"
version_code = "0.01a"

def migrate_loaded_save(save: dict):
    # 0.01a saves
    _changed = False
    if "version" not in save:
        _changed = True
        save["version"] = "0.01a"
        print(" [!] Applied version to save")

    privateState = save["privateState"]
    if type(privateState["inventoryItems"]) != dict:
        _changed = True
        privateState["inventoryItems"] = {}
        print(" [!] Applied inventory fix")
    if type(privateState["deadHeroes"]) != dict:
        _changed = True
        privateState["deadHeroes"] = {}
        print(" [!] Applied hospital fix")
    if type(privateState["magics"]) != dict:
        _changed = True
        privateState["magics"] = {}
        print(" [!] Applied magics fix")

    return _changed