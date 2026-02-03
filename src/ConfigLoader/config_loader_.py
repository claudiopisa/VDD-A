import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

class ConfigLoader:
    def __init__(self, path: str):
        self.path = Path(path)
        raw = self._load()
        self.config_data = self._parse(raw)
        self.__dict__.update(self.config_data.__dict__)

    def _load(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"Error | File not found at path: {self.path}")
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error | JSON Decode Error at {self.path}: {e}")

    def _parse(self, elem: Any):
        if not isinstance(elem, dict):
            return elem

        parsed = {}
        for k, v in elem.items():
            if isinstance(v, dict):
                parsed[k] = self._parse(v)
            elif isinstance(v, list):
                parsed[k] = [self._parse(x) for x in v]
            else:
                parsed[k] = v

        return SimpleNamespace(**parsed)

    def __dir__(self):
        base = set(super().__dir__())
        dynamic = set(self.__dict__.keys())

        return sorted(base | dynamic)

    def keys(self):
        """Chiavi top-level disponibili (dinamiche)."""
        return sorted(self.config_data.__dict__.keys())

    def describe(self, obj=None, indent=0):
        """Stampa una mini-mappa della config (anche annidata)."""
        if obj is None:
            obj = self.config_data

        pad = " " * indent
        if isinstance(obj, SimpleNamespace):
            for k, v in obj.__dict__.items():
                t = type(v).__name__
                print(f"{pad}- {k}: {t}")
                if isinstance(v, SimpleNamespace):
                    self.describe(v, indent + 2)
        else:
            print(f"{pad}{obj}")


cfg = ConfigLoader("config/global_config.json")
print(cfg.vdd_type)
print(cfg.roots.internal)

print(cfg.keys())
cfg.describe()
print("roots" in dir(cfg))  # True
