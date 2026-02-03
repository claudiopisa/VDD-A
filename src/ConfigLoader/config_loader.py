import json
from pathlib import Path
from enum import Enum
from types import SimpleNamespace



class ConfigLoader:
    def __init__(self, path: str):
        self.path = Path(path)
        raw = self._load() # load raw data from json
        self.config_data = self._parse(raw) # parse raw data 
        self.__dict__.update(self.config_data.__dict__) # set attributes from parsed data
        #alternativa
        #for k, v in self.config_data.__dict__.items():
            #setattr(self, k, v)

         
    def _load(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"Error | File not found at path: {self.path}")

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error | JSON Decode Error at {self.path}: {e}")
        
        print("DEBUG | Config Loaded")

    def _parse(self, elem):
        if not type(elem) == dict:
            return elem
        
        parsed = {}
        for k, v in elem.items():
            if type(v) == dict: # se elem ha dizionario innestato
                parsed[k] = self._parse(v)
            #elif isinstance(v, list): # se elem ha lista innestata
                #parsed[k] = [self._parse(x) for x in v]
            else: # altrimenti diventa attributo semplice (caso base)
                parsed[k] = v

        return SimpleNamespace(**parsed) # converte parsed in SimpleNamespace in modo da poter accedere agli attributi con la notazione a punto


#main 

a = ConfigLoader("config/global_config.json")
b = ConfigLoader("config/ch2_config.json")

for k,v in a.__dict__.items():
    print (f"{k}: {v}")
    print("----")

print(b.mode)

