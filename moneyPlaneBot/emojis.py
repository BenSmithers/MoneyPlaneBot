import json
import os 

_obj = open(os.path.join(os.path.dirname(__file__), "emoji_data.json"),'rt')
_raw = json.load(_obj)
_obj.close()


def process(what):
    """
    cuts out the number from the entry
    """
    ret =  [ 
        int(entry.split(":")[-1][:-1]) for entry in what
    ]
    return ret


WITNESS = process(_raw["witness"])
CRASH= process(_raw["crashed"])
RUMBLE = process(_raw["rumble"])
LAND = process(_raw["landed"])
COSIGN = process(_raw["cosign"])
NUT = process(_raw["celebrate"])
LONG = process(_raw["longshot"])

RAWWITNESS = _raw["witness"]
RAWCRASH= _raw["crashed"]
RAWRUMBLE = _raw["rumble"]
RAWLAND = _raw["landed"]
RAWCOSIGN = _raw["cosign"]
RAWNUT = _raw["celebrate"]
RAWLONG = _raw["longshot"]