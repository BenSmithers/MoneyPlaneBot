"""
This script manages the database of moneyplanes, and essentially serves as an interface between the discord bot code and the actual "MoneyPlane" objects themselves 

The sync happens two ways:
    - when `check_sync` is called, and it has been an hour since the last sync 
    - when sync is called directly 

In main_parser, sync should be called when SIGINT is sent to the program 
check_sync should be called whenever the database is written to 

NULL_MONEY is returned when a moneyplane is expected, but there is no such moneyplane available 
"""

from moneyPlaneBot.moneyplane import MoneyPlane
from moneyPlaneBot.enums import MoneyPlaneResult
import json
import os 
from time import time

DATABASE_DIR = os.path.join(os.path.dirname(__file__))

NULL_MONEY  = MoneyPlane(-1, -1, "NULL")

class DataBase:
    def __init__(self):
        self._moneyplanes = {} ## moneyplane_id->moneyplane 
        self._lastsync = time()
        self._database = os.path.join(DATABASE_DIR, "moneyplanes.json")
        
        if os.path.exists(self._database):
            print("Loading Database")
            _obj = open(self._database, 'rt')
            data = json.load(_obj)
            _obj.close()

            for key in data.keys():
                
                self._moneyplanes[int(key)] = MoneyPlane.build_from_json(data[key])

    def get_unresolved(self):
        unr = {}
        for key in self._moneyplanes:
            if self.get_moneyplane(key).result==MoneyPlaneResult.confliced or self.get_moneyplane(key).result==MoneyPlaneResult.unknown:
                unr[key] = self.get_moneyplane(key)
        return unr

    def get_score_dict(self):
        out_dict = {}
        for key in self._moneyplanes:
            points, result = self.get_moneyplane(key).get_effect()

            if result == MoneyPlaneResult.confliced or result==MoneyPlaneResult.unknown or result==MoneyPlaneResult.nowitnesses:
                continue

            else:
                for key in points:
                    if key in out_dict:
                        out_dict[key] += points[key]
                    else:
                        out_dict[key] = points[key]

        return out_dict

    def check_sync(self):
        now = time()

        if int(abs(now - self._lastsync))>1: # one minute
            self.sync()

    def new_moneyplane(self, money_id:int, owner_id:int, bet=""):
        """
            Creates a new moneyplane object and adds it to the dictionary.

            Throws KeyError if moneyplane already registered 
        """
        if money_id in self._moneyplanes:
            raise ValueError("Moneyplane already exists with ID {}".format(money_id)) 

        new_plane = MoneyPlane(money_id, owner_id, bet)
        self._moneyplanes[money_id] = new_plane

        self.check_sync()


    def get_moneyplane(self, money_id:int)->MoneyPlane:
        if money_id in self._moneyplanes:
            return self._moneyplanes[money_id]
        else:
            return NULL_MONEY

    def sync(self):
        """
        Syncronize the databasefile with the active memory in this database object 
        eventually we'll want to just save the diff's (saving on IO), but for now it has to save the whole thing at once... 
        """
        self._lastsync = time()
        _to_save = {}
        for key in self._moneyplanes:
            _to_save[key] = self._moneyplanes[key].to_json()

        _obj = open(self._database, 'wt')
        json.dump(_to_save, _obj, indent=4)
        _obj.close()


    def fetch_scores(self)->dict:
        self.check_sync()
    
    def crash_add(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 

        mp.add_state(user_id, MoneyPlaneResult.crashed)
        self.check_sync()
        
    def land_add(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 

        mp.add_state(user_id, MoneyPlaneResult.landed)
        self.check_sync()

    def witness_add(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 

        mp.add_witness(user_id)
        self.check_sync()
        
    def witness_remove(self, message_id:int, user_id:int):
        # cannot remove witness
        pass

    def cosign_add(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 
        mp.add_cosigner(user_id)
        self.check_sync()

    def cosign_remove(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 

        mp.remove_cosign(user_id)
        self.check_sync()

    def rumble_add(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 

        mp.add_rumble(user_id)
        self.check_sync()

    def rumble_remove(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return

        mp.remove_rumble(user_id) 
        self.check_sync()

    def longshot_add(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 
        
        mp.add_longshot(user_id)
        self.check_sync()
        
    def longshot_remove(self, message_id:int, user_id:int):
        mp = self.get_moneyplane(message_id)
        if mp.id not in self._moneyplanes:
            return 
        
        mp.remove_longshot(user_id)
        self.check_sync()
    
