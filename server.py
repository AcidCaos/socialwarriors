print (" [+] Loading basics...")
import os
import json
import urllib
if os.name == 'nt':
    os.system("color")

print (" [+] Loading game config...")
from get_game_config import get_game_config, patch_game_config
print (" [+] Applying config patches...")
patch_game_config()

print (" [+] Loading players...")
from get_player_info import get_player_info
from sessions import load_saved_villages, all_saves_userid, all_saves_info, save_info, new_village
load_saved_villages()

print (" [+] Loading server...")
from flask import Flask, render_template, send_from_directory, request, redirect, session
from flask.debughelpers import attach_enctype_error_multidict
from command import command
from engine import timestamp_now
from version import version_name

host = '127.0.0.1'
port = 5055

app = Flask(__name__)

print (" [+] Configuring server routes...")

##########
# ROUTES #
##########

## PAGES AND RESOURCES

@app.route("/", methods=['GET', 'POST'])
def login():
    # Log out previous session
    session.pop('USERID', default=None)
    # If logging in, set session USERID, and go to play
    if request.method == 'POST':
        session['USERID'] = request.form['USERID']
        print("[LOGIN] USERID:", request.form['USERID'])
        return redirect("/play.html")
    # Login page
    if request.method == 'GET':
        saves_info = all_saves_info()
        return render_template("login.html", saves_info=saves_info, version=version_name)

@app.route("/play.html")
def play():
    if 'USERID' not in session:
        return redirect("/")

    if session['USERID'] not in all_saves_userid():
        return redirect("/")
    
    USERID = session['USERID']
    print("[PLAY] USERID:", USERID)
    return render_template("play.html", save_info=save_info(USERID), serverTime=timestamp_now(), version=version_name)

@app.route("/new.html")
def new():
    session['USERID'] = new_village()
    return redirect("play.html")

@app.route("/crossdomain.xml")
def crossdomain():
    return send_from_directory("stub", "crossdomain.xml")

@app.route("/img/<path:path>")
def images(path):
    return send_from_directory("templates/img", path)

## GAME STATIC

@app.route("/default01.static.socialpointgames.com/static/socialwars/<path:path>")
def static_assets_loader(path):

    ## CDN
    if not os.path.exists(f"assets/{path}"):
        # File does not exists in provided assets
        if not os.path.exists(f"new_assets/assets/{path}"):
            # Download file from SP's CDN if it doesn't exist

            # Make directory
            directory = os.path.dirname(f"new_assets/assets/{path}")
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Download File
            URL = f"https://static.socialpointgames.com/static/socialwars/assets/{path}"
            try:
                response = urllib.request.urlretrieve(URL, f"new_assets/assets/{path}")
            except urllib.error.HTTPError:
                return ("", 404)

        return send_from_directory("new_assets/assets", path)
    ## CDN END


    return send_from_directory("assets", path)

## GAME DYNAMIC

@app.route("/dynamic.flash1.dev.socialpoint.es/appsfb/menvswomen/srvsexwars/track_game_status.php", methods=['POST'])
def track_game_status_response():
    status = request.values['status']
    installId = request.values['installId']
    user_id = request.values['user_id']

    print(f"track_game_status: status={status}, installId={installId}, user_id={user_id}. --", request.values)
    return ("", 200)

@app.route("/dynamic.flash1.dev.socialpoint.es/appsfb/menvswomen/srvsexwars/get_game_config.php")
def get_game_config_response():
    USERID = request.values['USERID']
    user_key = request.values['user_key']
    language = request.values['language']

    print(f"get_game_config: USERID: {USERID}. --", request.values)
    return get_game_config()

@app.route("/dynamic.flash1.dev.socialpoint.es/appsfb/menvswomen/srvsexwars/get_player_info.php", methods=['POST'])
def get_player_info_response():
    USERID = request.values['USERID']
    user_key = request.values['user_key']
    language = request.values['language']

    print(f"get_player_info: USERID: {USERID}. --", request.values)
    return (get_player_info(USERID), 200)

@app.route("/dynamic.flash1.dev.socialpoint.es/appsfb/menvswomen/srvsexwars/sync_error_track.php", methods=['POST'])
def sync_error_track_response():
    USERID = request.values['USERID']
    user_key = request.values['user_key']
    language = request.values['language']
    # error = request.values['error']
    # current_failed = request.values['current_failed']
    # tries = request.values['tries'] if 'tries' in request.values else None
    # survival = request.values['survival']
    # previous_failed = request.values['previous_failed']
    # description = request.values['description']
    # user_id = request.values['user_id']

    # print(f"sync_error_track: USERID: {USERID}. [Error: {error}] tries: {tries}. --", request.values)
    return ("", 200)

@app.route("/null")
def flash_sync_error_response():
    sp_ref_cat = request.values['sp_ref_cat']

    if sp_ref_cat == "flash_sync_error":
        reason = "reload On Sync Error"
    elif sp_ref_cat == "flash_reload_quest":
        reason = "reload On End Quest"
    elif sp_ref_cat == "flash_reload_attack":
        reason = "reload On End Attack"

    print("flash_sync_error", reason, ". --", request.values)
    return redirect("/play.html")

@app.route("/dynamic.flash1.dev.socialpoint.es/appsfb/menvswomen/srvsexwars/command.php", methods=['POST'])
def command_response():
    USERID = request.values['USERID']
    user_key = request.values['user_key']
    language = request.values['language']

    print(f"command: USERID: {USERID}. --", request.values)

    data_str = request.values['data']
    data_hash = data_str[:64]
    assert data_str[64] == ';'
    data_payload = data_str[65:]
    data = json.loads(data_payload)

    command(USERID, data)
    
    return ({"result": "success"}, 200)


########
# MAIN #
########

print (" [+] Running server...")

if __name__ == '__main__':
    app.secret_key = 'SECRET_KEY'
    app.run(host=host, port=port, debug=False)
