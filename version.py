from engine import timestamp_now

version_name = "pre-alpha 0.01"
version_code = "0.01a"

def migrate_loaded_save(save: dict) -> bool:
    # 0.01a saves
    if "version" not in save:
        save["version"] = "0.01a"

    return True