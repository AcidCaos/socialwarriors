import json
import os

from bundle import AUCTIONS_DIR, CONFIG_DIR
from engine import timestamp_now
from get_game_config import get_name_from_item_id

class AuctionHouse():
    def __init__(self):
        # PATHS
        self.PATH_AH_CONFIG = CONFIG_DIR
        self.FILE_AH_CONFIG = os.path.join(self.PATH_AH_CONFIG, "auctionhouse.json")

        self.PATH_AH_STATE = AUCTIONS_DIR
        self.FILE_AH_STATE = os.path.join(self.PATH_AH_STATE, "auctions.json")

        # CONFIG
        self.config = {
            "auctions": []
        }
        if os.path.exists(self.FILE_AH_CONFIG):
            self.config = json.load(open(self.FILE_AH_CONFIG))
        else:
            print("No Auction House config exists")

        # STATE
        self.auction_state = {
            "auctions": {}
        }
        if not os.path.exists(self.PATH_AH_STATE):
            os.makedirs(self.PATH_AH_STATE)
        if os.path.exists(self.FILE_AH_CONFIG):
            self.auction_state = json.load(open(self.FILE_AH_STATE))
            self.auctions = self.auction_state["auctions"]

        self.init_auctions()

    def init_auctions(self):
        updated = self._remove_auctions()
        updated |= self.update_all_auctions(timestamp_now(), update=False)

        if updated:
            self._write_state()

    def update_all_auctions(self, time_now: int, update: bool = True):
        updated = False
        for auction in self.config["auctions"]:
            updated |= self.update_auction(auction, time_now)

        if update and updated:
            self._write_state()

        return updated

    def _remove_auctions(self):
        # Remove auctions that don't exist in config anymore to allow for changes
        to_delete = []
        for uuid in self.auctions:
            if not self.get_auction_config(uuid):
                to_delete.append(uuid)
        for uuid in to_delete:
            name = get_name_from_item_id(self.auctions[uuid]["idUnit"])
            print(f"Deleted auction for {name} -> UUID: {uuid}")
            del self.auctions[uuid]
        return len(to_delete) > 0

    def get_auction_config(self, uuid: str):
        for auction in self.config["auctions"]:
            if auction["uuid"] == uuid:
                return auction

        return None

    def update_auction(self, auction: dict, time_now: int):
        uuid = str(auction["uuid"])
        seconds = auction["interval"] * 60

        updated = False
        if uuid in self.auctions:
            updated |= self._update_auction(self.auctions[uuid], uuid, auction, seconds, time_now)
        else:
            updated |= self._create_auction(uuid, auction, seconds, time_now)

        return updated    

    # Creates auction on AH
    def _create_auction(self, uuid: str, auction: dict, seconds: int, time_now: int):
        bet = {
            "uuid": uuid,
            "idUnit": auction["unit"],
            "level": auction["level"],
            "beginDate": time_now,
            "endDate": time_now + seconds,
            "beginPrice": auction["price"],
            "currentPrice": auction["price"],
            "priceIncrement": auction["priceIncrement"],
            "betPrice": auction["betPrice"],
            "round": 1,
            "betUsers": [],
            "betUsersPrev": [],
            "bidders": [],
            "prevRoundBidders": [],
            "userRounds": []
        }

        self.auctions[uuid] = bet

        name = get_name_from_item_id(auction["unit"])
        print(f"Created auction for {name} as it didn't exist! -> UUID: {uuid}")
        return True

    # Updates existing auction on AH
    def _update_auction(self, bet: dict, uuid: str, auction: dict, seconds: int, time_now: int):
        if bet["idUnit"] != auction["unit"]:
            # If unit on AH state is no longer in config, overwrite it
            return self._create_auction(uuid, auction, seconds, time_now)

        # Just see if it needs updating
        if time_now > bet["endDate"]:
            if len(bet["betUsers"]) > 0 and time_now - bet["endDate"] < 60:
                return False
            difference = time_now - bet["endDate"]
            
            # TODO: rounds

            # How many times this item has expired
            count_expired = difference // seconds
            # How many seconds should have passed since new entry was generated
            remaining = difference % seconds

            bet["level"] = auction["level"]
            bet["beginDate"] = time_now - remaining
            bet["endDate"] = bet["beginDate"] + seconds
            bet["beginPrice"] = auction["price"]
            bet["currentPrice"] = auction["price"]
            bet["priceIncrement"] = auction["priceIncrement"]
            bet["betPrice"] = auction["betPrice"]
            bet["round"] = 1
            bet["betUsers"] = []
            bet["betUsersPrev"] = []
            bet["bidders"] = []
            bet["prevRoundBidders"] = []
            bet["userRounds"] = []

            # print(json.dumps(bet, indent="\t"))

            name = get_name_from_item_id(auction["unit"])
            print(f"Restarted auction for {name} as it expired! -> UUID: {uuid}")
            return True

        return False

    def _write_state(self):
        try:
            with open(self.FILE_AH_STATE, 'w') as f:
                json.dump(self.auction_state, f, indent="\t")
        except:
            print("Error: Could not write Auction House state to disk!")

    def _set_bet_flags(self, bet: dict, user_id: str, checkFinish: int = 0):
        # Manage some flags
        bet["isPrivate"] = 0
        bet["isWinning"] = 0
        bet["won"] = 1
        bet["finished"] = timestamp_now() >= bet["endDate"]
        bet["betDetail"] = []

        betUsers = bet["betUsers"]
        if len(betUsers) > 0:
            last = max(0, len(betUsers) - 1)
            user = betUsers[last]
            if user["user_id"] == user_id:
                bet["isWinning"] = 1
            if checkFinish:
                if bet["isWinning"]:
                    bet["betWinner"] = user_id

## FOR SERVER

    def set_bet(self, user_id: str, uuid: str, bet_amount: int, bet_round: int):
        if uuid in self.auctions:
            auction = self.auctions[uuid]

            user = {
                "user_id": user_id,
                "fb_name": "Test",
                "bet": bet_amount,
                "fb_picture": ""
            }
            bidder = {
                "user_id": user_id,
                "fb_name": "Test",
                "bet": bet_amount,
                "fb_picture": ""
            }

            auction["betUsers"].append(user)
            auction["bidders"].append(bidder)
            auction["currentPrice"] = bet_amount + auction["priceIncrement"]

        pass

    def get_auctions(self, user_id: str, level: int):
        self.update_all_auctions(timestamp_now())

        bets = []

        for uuid in self.auctions:
            bet = json.loads(json.dumps(self.auctions[uuid]))

            self._set_bet_flags(bet, user_id)

            bets.append(bet)

        return bets

    def get_auction_detail(self, user_id: str, uuid: str, checkFinish: int):
        if uuid in self.auctions:
            auction_data = self.get_auction_config(uuid)
            if not auction_data:
                return None
            if self.update_auction(auction_data, timestamp_now()):
                self._write_state()
            bet = json.loads(json.dumps(self.auctions[uuid]))

            self._set_bet_flags(bet, user_id, checkFinish)

            return bet

        return None