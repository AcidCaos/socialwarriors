
from sessions import session, save_session
from get_game_config import get_game_config
from constants import Constant
from engine import timestamp_now

def command(USERID, data):
    first_number = data["first_number"]
    publishActions = data["publishActions"]
    timestamp = data["ts"]
    tries = data["tries"]
    accessToken = data["accessToken"]
    commands = data["commands"]
    
    for i, comm in enumerate(commands):
        unknown_id = comm[0]
        cmd = comm[1]
        args = comm[2]
        unknown_list = comm[3]
        do_command(USERID, unknown_id, cmd, args, unknown_list)
    save_session(USERID) # Save session

def do_command(USERID, __1, cmd, args, __2):
    save = session(USERID)
    print (" [+] COMMAND: ", cmd, "(", args, ") -> ", sep='', end='')

    if cmd == "stub":
        print(" ".join(args))
    
    else:
        print(f"Unhandled command '{cmd}' -> args", args)
        return
    
