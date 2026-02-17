from pathlib import Path
import json
from typing import Dict, Any
from utils.dotted_dict import DottedDict


class UserConfigLoader:
    """
    Static utility class to load user configuration from JSON files.
    Returns the loaded data as DotDict (dict with dot notation access).
    """
    
    @staticmethod
    def load(path: str | Path, return_dict: bool = False) -> Dict[str, Any] | DottedDict:
        """
        Load user configuration from a JSON file.
        
        Args:
            path: Path to the JSON configuration file
            return_dict: If True, returns a dict; if False, returns a DottedDict
            
        Returns:
            Configuration data as Dict or DottedDict
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the path is not a file
            JSONDecodeError: If the JSON is invalid
        """
        if isinstance(path, str):
            path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Error class {UserConfigLoader.__name__} | file not found: {path}")
        elif not path.is_file():
            raise ValueError(f"Error class {UserConfigLoader.__name__} | path is not a file: {path}")
        
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if return_dict else DottedDict(data) # se data è già un dict, DottedDict lo accetta direttamente
  
    def __repr__(self):
        return f"User Configuration dump: {json.dumps(self.load(self.user_config_path, return_dict=True), indent=2)}"

# ============================================================================
# DEPRECATED - Old implementation using ConfigNamespace
# ============================================================================
# Replaced by DotDict in v2.0 (Feb 2026)
# Kept for reference/history only
#
# Old imports (DEPRECATED):
# from types import SimpleNamespace
# from configs.config_namespace import ConfigNamespace
#
# Old return type:
# @staticmethod
# def load(path: str | Path, return_dict: bool = False) -> Dict[str, Any] | ConfigNamespace:
#     """Old version returned ConfigNamespace instead of DotDict"""
#     if isinstance(path, str):
#         path = Path(path)
#     
#     if not path.exists():
#         raise FileNotFoundError(f"Error class {UserConfigLoader.__name__} | file not found: {path}")
#     elif not path.is_file():
#         raise ValueError(f"Error class {UserConfigLoader.__name__} | path is not a file: {path}")
#     
#     with path.open("r", encoding="utf-8") as file:
#         if return_dict:
#             return json.load(file)
#         return json.load(file, object_hook=lambda elem: ConfigNamespace(**elem))
#
# REASON FOR CHANGE:
# - ConfigNamespace had custom __repr__ (JSON format) but was unnecessary overhead
# - DotDict is simpler (1 class, ~40 lines) vs ConfigNamespace (~30 lines)
# - DotDict has native dict __repr__ (clean and Pythonic)
# - Both support dot notation access (obj.key)
# - DotDict is more flexible (supports both obj.key and obj['key'])
# - Easier to transition to Pydantic/Dataclass later if needed
# ============================================================================