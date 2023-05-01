from moneyPlaneBot.enums import MoneyPlaneResult
from moneyPlaneBot import point_values

class MoneyPlane:
    """
        This class is used to track a placed MoneyPlane 
    """
    def __init__(self, event_id:int, owner_id:int, moneyplane_details=""):
        self._id = event_id

        # who rumbled it 
        self._rumbles = [] 

        # who witnessed it 
        self._witnesses = []

        # who cosigned it
        self._cosigners = []

        self._crashes = []
        self._lands = []

        self._longshots = []

        # who placed it 
        self._owner = owner_id

        self._details = moneyplane_details

    @property
    def witnesses(self):
        raw = list(set(self._witnesses + self._crashes + self._lands + self._rumbles + self._cosigners))
        return raw

    @property
    def rumbles(self):
        return self._rumbles
    
    @property 
    def cosigners(self):
        return self._cosigners
    
    @property
    def owner(self):
        return self._owner

    @property
    def details(self):
        return self._details

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, MoneyPlane):
            return False
        else:
            return self._id==__o._id

    def __str__(self) -> str:
        name = self.result.name
        name = name[0].upper() + name[1:].lower()
        full_txt = "Moneyplane {}! ".format(name) + self._details
        return full_txt

    @property
    def id(self):
        return self._id

    @property
    def result(self):
        if len(self._crashes)==0 and len(self._lands)==0:
            return MoneyPlaneResult.unknown
        else:
            if len(self.witnesses)<2: # include cosigners/reviewers 
                return MoneyPlaneResult.nowitnesses
            elif len(self._crashes) == len(self._lands):
                return MoneyPlaneResult.confliced
            elif len(self._crashes) > len(self._lands):
                return MoneyPlaneResult.crashed
            else:
                return MoneyPlaneResult.landed

    def add_state(self, user_id:int, result:MoneyPlaneResult):
        assert isinstance(result, MoneyPlaneResult), "Cannot set state to type {}".format(type(result))

        # only the MoneyPlane itself can set itself to unknown, conflicted, or w/e 
        if result!=MoneyPlaneResult.crashed and result!=MoneyPlaneResult.landed:
            raise ValueError("Can only accept crashed or landed, got {}".format(result))

        if result==MoneyPlaneResult.landed:
            if user_id not in self._lands:
                self._lands.append(user_id)
        if result==MoneyPlaneResult.crashed:
            if user_id not in self._crashes:
                self._crashes.append(user_id)
                
    def add_cosigner(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        # can only cosign before it's decided 
        if self.result != MoneyPlaneResult.unknown:
            return

        if user_id not in self._cosigners:
            if user_id!=self._owner:
                self._cosigners.append(user_id)

    def remove_cosign(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        if user_id in self._cosigners:
            self._cosigners.pop(self._cosigners.index(user_id))

    # witnesses cannot be removed
    def add_witness(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        if user_id not in self._witnesses:
            if user_id != self._owner:
                self._witnesses.append(user_id)


    def add_rumble(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        if self.result != MoneyPlaneResult.unknown:
            return

        if user_id not in self._rumbles:
            self._rumbles.append(user_id)

    def remove_rumble(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        if user_id in self._rumbles:
            self._rumbles.pop(self._rumbles.index(user_id))

    def add_longshot(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        if user_id not in self._longshots:
            if user_id!=self._owner:
                self._longshots.append(user_id)

    def remove_longshot(self, user_id:int):
        assert isinstance(user_id, int), "User id was not an integer"
        if user_id in self._longshots:
            self._longshots.pop(self._longshots.index(user_id))

    def get_effect(self)->'tuple[dict, MoneyPlaneResult]':
        """
        Returns the effect of this moneyplane on scores and its current state 
        """
        result = self.result
        point_dict = {}

        if result == MoneyPlaneResult.crashed:
            """
                Any rumblers get a point 
            """

            point_dict = {user_id:point_values.RUMBLE for user_id in self._rumbles} 
            for user_id in self._cosigners:
                point_dict[user_id] = -point_values.COSIGN
            point_dict[self._owner] = -point_values.OWN
        elif result==MoneyPlaneResult.landed:
            point_dict = {user_id:point_values.COSIGN for user_id in self._cosigners}
            for user_id in self._rumbles:
                point_dict[user_id] = -point_values.RUMBLE
            point_dict[self._owner] = point_values.OWN
            
        return point_dict, result

    def to_json(self)->dict:
        return {
            "owner":self._owner,
            "id":self._id,
            "rumbles":self._rumbles,
            "witnesses":self._witnesses,
            "cosigners":self._cosigners,
            "lands":self._lands,
            "crashes":self._crashes,
            "details":self._details
        }

    @classmethod
    def build_from_json(cls, dict):
        new_moneyplane = cls(dict["id"], dict["owner"])

        new_moneyplane._cosigners = dict["cosigners"]
        new_moneyplane._witnesses = dict["witnesses"]
        new_moneyplane._rumbles = dict["rumbles"] 
        new_moneyplane._crashes = dict["crashes"]
        new_moneyplane._lands = dict["lands"]
        new_moneyplane._details = dict["details"]

        return new_moneyplane
