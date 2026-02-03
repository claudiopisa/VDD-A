import json


class ConfigLoader:
    
    def __init__(self, file):
        try:
            with open(file, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print("ERROR | File not found.")
    
        for key, value in self.data.items():
            setattr(self, key, value)

        

cfg = ConfigLoader("config.json")

print(cfg)

