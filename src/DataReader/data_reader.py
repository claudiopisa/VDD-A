from pathlib import Path
from abc import ABC, abstractmethod

class DataReader(ABC):
    
    def __init__(self, *data_paths: Path | str):
        # if len is 1, return a single Path object
        # else if len is > 1, return a list of Path objects
        """if len(data_paths) == 1:
            self.data = self._normalize_path(data_paths[0])
        else:
            self.data = [self._normalize_path(data_path) for data_path in data_paths]

        self.data_paths: list[Path] = []"""


        self._data: dict[str, Path] = {}

        for data_path in data_paths:
            path = self._normalize_path(data_path)
            key = path.stem  # Use the filename without extension as key from Path object
            
            if key in self._data:
                raise ValueError(f"Duplicate key '{key}' derived from data path '{data_path}'. Please ensure unique filenames for each data path.")
            
            self._data[key] = path


        """for data_path in data_paths:
            if isinstance(data_path, str):
                data_path = Path(data_path)
            if not data_path.exists():
                raise FileNotFoundError(f"Data path '{data_path}' does not exist.")
            if not data_path.is_file():
                raise ValueError(f"Data path '{data_path}' is not a file.")
            
            self.data_paths.append(data_path)"""
        
        # Keep reference to first path for backward compatibility
        #self.data_path = self.data_paths[0] if self.data_paths else None
    
    @abstractmethod
    def scan_files(self):
        pass

    def _normalize_path(self, path: str | Path) -> Path:
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Data path '{path}' does not exist.")
        if not path.is_file():
            raise ValueError(f"Data path '{path}' is not a file.")
        
        return path
    
    def __getattr__(self, name: str) -> Path:
        if name not in self._data:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return self._data[name]
    
