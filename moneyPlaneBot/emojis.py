import json
import os 

_obj = open(os.path.join(os.path.dirname(__file__), "emoji_data.json"),'rt')
_raw = json.load(_obj)
_obj.close()


def process(what):
    ret =  [ 
        int(entry.split(":")[-1][:-1]) for entry in what
    ]
    print(ret)
    return ret

WITNESS = process(_raw["witness"])
CRASH= process(_raw["crashed"])
RUMBLE = process(_raw["rumble"])
LAND = process(_raw["landed"])
COSIGN = process(_raw["cosign"])
NUT = process(_raw["celebrate"])



RAWWITNESS = _raw["witness"]
RAWCRASH= _raw["crashed"]
RAWRUMBLE = _raw["rumble"]
RAWLAND = _raw["landed"]
RAWCOSIGN = _raw["cosign"]
RAWNUT = _raw["celebrate"]