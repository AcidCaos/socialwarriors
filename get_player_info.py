from sessions import session, neighbors
from engine import timestamp_now

def get_player_info(USERID):
    # Update last logged in
    ts_now = timestamp_now()
    session(USERID)["playerInfo"]["last_logged_in"] = ts_now
    # player
    player_info = {
        "result": "ok",
        "processed_errors": 0,
        "timestamp": ts_now,
        "playerInfo": session(USERID)["playerInfo"],
        "map": session(USERID)["maps"][0],
        "privateState": session(USERID)["privateState"],
        "neighbors": neighbors(USERID)
    }
    return player_info