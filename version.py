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
    if privateState["inventoryItems"] == None:
        _changed = True
        privateState["inventoryItems"] = []
        print(" [!] Applied inventory fix")

    return _changed