import json
from pathlib import Path
from enum import Enum
from types import SimpleNamespace
from abc import abstractmethod



class ConfigLoader:
    def __init__(self, path: str | Path):
        if isinstance(path, str):
            self.path = Path(path)
        elif isinstance(path, Path):
            self.path = path
        else:
            raise TypeError(f"Error class {self.__class__.__name__} | Path must be a string or Path object, got {type(path)}")

        try:
            self.config_data = self._load()
        except Exception as e:
            raise ValueError(f"Error class {self.__class__.__name__} | problem loading config from {self.path}: {e}") 
        #raw = self._load() # load raw data from json
        #self.config_data = self._parse(raw) # parse raw data 
        #self.__dict__.update(self.config_data.__dict__) # set attributes from parsed data
        #alternativa
        #for k, v in self.config_data.__dict__.items():
            #setattr(self, k, v)

         
    def _load(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"Error class {self.__class__.__name__} | File not found at path: {self.path}")

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                #return json.load(file)
                return json.load(file, object_hook=lambda elem: SimpleNamespace(**elem))

        except json.JSONDecodeError as e:
            raise ValueError(f"Error class {self.__class__.__name__} | JSON Decode Error at {self.path}: {e}")
        
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

    
                
    #crea metodo astratto per validazione che deve essere implementato dalle sottoclassi
    @abstractmethod
    def validate(self):
        pass
    
#main 

#a = ConfigLoader("config/global_config.json")
#b = ConfigLoader("config/ch2_config.json")

#for k,v in a.__dict__.items():
 #   print (f"{k}: {v}")
 #   print("----")

#print(b.mode)

