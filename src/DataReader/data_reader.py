from pathlib import Path
from abc import ABC, abstractmethod
from model.data_path import DataPath

class DataReader(ABC):
    
    """def __init_old__(self, *data_paths: Path | str):


        self._data: dict[str, Path] = {}

        for data_path in data_paths:
            path = self._normalize_path(data_path)
            key = path.alt_name if path.alt_name else path.stem 

            # no duplicates allowed
            if key in self._data:
                raise ValueError(f"Duplicate key '{key}' derived from data path '{data_path}'. Please ensure unique filenames for each data path.")
            
            self._data[key] = path"""

    #new version with kwargs
    def __init__(self, **data_paths: Path |  str):
        self._data: dict[str, Path] = {}
        for key, path in data_paths.items():
            if path is not None:
                path = self._normalize_path(path)
                self._data[key] = path # use key as name and path as value in the dict
                #setattr(self, key, path) # set attribute for direct access (e.g., self.imgconf)
                 
    @abstractmethod
    def scan_files(self):
        pass

    def _normalize_path(self, path: str | Path) -> DataPath:
        # the given `path` argument must be either a string or a Path object, thanks to the type hint, hence, we directly convert it to a DataPath object
        data_path = DataPath(path)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data path '{path}' does not exist.")
        if not data_path.is_file():
            raise ValueError(f"Data path '{path}' is not a file.")
        
        return data_path
    
    def __getattr__(self, name: str) -> DataPath:
        if name not in self._data:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return self._data[name]
    
    def get(self, name: str) -> DataPath:
        return self.__getattr__(name)
    
    
