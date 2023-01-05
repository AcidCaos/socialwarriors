import json
import os

from bundle import AUCTIONS_DIR

__auctions = json.load(open(os.path.join(AUCTIONS_DIR, "auctions.json")))

def get_auctions():
    bets = []

    for uuid in __auctions:
        bets.append(json.loads(json.dumps(__auctions[uuid])))

    return bets