from pathlib import Path
import json
from types import SimpleNamespace
from typing import Dict, Any, Union

#make class static


class UserConfigLoader():
    @staticmethod
    def load(path: str | Path) -> Dict[str, Any]:
        if isinstance(path, str):
            path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Error class {UserConfigLoader.__name__} | file not found: {path}")
        elif not path.is_file():
            raise ValueError(f"Error class {UserConfigLoader.__name__} | path is not a file: {path}")
 
        try:
            with open(path, "r", encoding="utf-8") as file:
                #return json.load(file)
                return json.load(file, object_hook=lambda elem: SimpleNamespace(**elem))

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error class {UserConfigLoader.__name__} | file not found: {path}") from e 
        except json.JSONDecodeError as e:
            raise ValueError(f"Error class {UserConfigLoader.__name__} | JSON Decode Error at {path}: {e}") from e