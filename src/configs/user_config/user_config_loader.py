from pathlib import Path
import json
from types import SimpleNamespace
from typing import Dict, Any


class UserConfigLoader:
    
    def __init__(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Error class {UserConfigLoader.__name__} | file not found: {path}")
        elif not path.is_file():
            raise ValueError(f"Error class {UserConfigLoader.__name__} | path is not a file: {path}")
        
        self.config_data: Dict[str, Any] | SimpleNamespace = self._load(path)

    def _load(self, path: str | Path, return_dict : bool = False) -> Dict[str, Any] | SimpleNamespace:
        with path.open("r", encoding="utf-8") as file:
            if return_dict:
                return json.load(file)
            return json.load(file, object_hook=lambda elem: SimpleNamespace(**elem))