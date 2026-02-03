import json 
from types import SimpleNamespace

class Test:
    def __init__(self):
        self.path = "config/ch2_config.json"

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error | JSON Decode Error at {self.path}: {e}")

    
    def parse(self, data):
        if type(data) == dict:
            for k, v in data.items():
                if type(v) == dict:
                    converted = self.parse(v)
                    setattr(self, k, converted)
                    return converted
                else:
                    converted = SimpleNamespace(v)
                    setattr(self, k, converted) 
                    return converted                   
                #setattr(self, k, SimpleNamespace(**v))
        else:
            setattr(self, k, v)


a = Test()

#for k, v in a.data:
    #print(type(a.data[k]))

#for k, v in a.__dict__.items():
    #print(f"{k}: {v}")

#a.parse(a.data)

#print(a.rules.inclusion)
#print(a.rules.inclusion.extensions)


data1 = {
    "rules": {
        "exc" : {
            "z" : "value"
        }
    }
}

data2 = {
    "x": {
        "y": 1
    },
    "a": 2
}

data = {
    "a": 2,
    "x": {"y": 1},
}

x = {
    "y": 1
}


d = SimpleNamespace(data)
t = SimpleNamespace(x)

print(d.a)
print(t)

metadata = {
      "title": "LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS",
      "columns_name" : ["File name", "File version"]
    }


def parse(elem):
    if type(elem) == dict:
        for k, v in elem.items():
            #print(f"DEBUG  | {k}, {v}")
            if type(v) == dict: # se ha dizionario innestato
                parsed = parse(v)
                print("DEBUG | ", parsed)
                elem[k] = parsed
            #else:
                #print("DEBUG | elem: ", elem)
                #return SimpleNamespace(**elem)
        return SimpleNamespace(**elem)
    return elem
            
p = parse(metadata)

print("parsed:", p)
print("parsed:", p.title)
print("parsed:", p.columns_name)


e = SimpleNamespace(data)


#for k, v in x.items():
    #if type(v) == dict:
        #e = SimpleNamespace(**v)



