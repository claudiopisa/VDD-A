from pathlib import Path
from abc import ABC, abstractmethod
from typing import Sequence

from configs.config import Config

type PathInput = str | Path
type PathValue = PathInput | Sequence[PathInput]
type NormalizedValue = Path | tuple[Path, ...]

class DataReader(ABC):
    
    def __init__old(self, reader_config: Config, **data_paths: PathValue):
        self.reader_config = reader_config
        
        self._data: dict[str, NormalizedValue] = {}
        for key, path in data_paths.items():
            if path is not None:
                if isinstance(path, (list, tuple)):
                    # if the path is a list or tuple, we normalize each path in the list and store the list of DataPath objects
                    self._data[key] = tuple(self._normalize_path(p) for p in path) # what if i use a tuple ?
                else:
                    self._data[key] = self._normalize_path(path) # use key as name and path as value in the dict
                #setattr(self, key, path) # set attribute for direct access (e.g., self.imgconf)
                 
    def __init__(self, config: Config):
        self.config = config
        self.core = self.config.core
        self._data: dict[str, NormalizedValue] = {}

    def parse_data_paths(self, **data_paths: PathValue):
        for key, path in data_paths.items():
            if path is not None:
                if isinstance(path, (list, tuple)):
                    # if the path is a list or tuple, we normalize each path in the list and store the list of DataPath objects
                    self._data[key] = tuple(self._normalize_path(p) for p in path) # what if i use a tuple ?
                else:
                    self._data[key] = self._normalize_path(path) # use key as name and path as value in the dict
    
    # Method called by the final user; acts as a wrapper for `_scan_files` (private), which is implemented by subclasses.
    def scan_files(self):
        # Ensure `parse_data_paths()` is called before `scan_files()`, otherwise there are no paths to read files from and an exception is raised.
        if not self._data:
            raise ValueError("No data paths provided to scan for files. `parse_data_paths()` must be called first.")
        
        return self._scan_files()

    @abstractmethod
    def _scan_files(self):
        pass

    @abstractmethod
    def _retrieve_paths(self, *args, **kwargs):
        pass

    # TODO: Consider to accept only directories, not path to files. DataReader should be responsible to only verify the existence of the given dir data path, whereas the scanning of files and retrieval of file paths is the responsibility of the concrete DataReader implementation (e.g., FileVersioning). This way we can have more flexibility in the type of data paths we can accept (e.g., we can accept both file and dir paths, and it's up to the concrete implementation to decide how to handle them). Moreover, this way we can also have a more consistent interface for the DataReader class, since all concrete implementations will have the same type of data path (i.e., directory) and the same method for scanning files (i.e., scan_files).
    def _normalize_path(self, path: PathInput) -> Path:
        # the given `path` argument must be either a string or a Path object, thanks to the type hint, hence, we directly convert it to a DataPath object
        if isinstance(path, str):
            path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Data path '{path}' does not exist.")
        #if not path.is_dir() 
        #if not path.is_file():
            #raise ValueError(f"Data path '{path}' is not a file.")
        if not (path.is_file() or path.is_dir()):
            raise ValueError(f"Data path '{path}' is neither a file nor a directory.")  
              
        return path
    
    # alternative to 'setattr' to get data paths as attributes (via dot notation)
    def __getattr__(self, name: str) -> NormalizedValue:
        if name not in self._data:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return self._data[name]
    
    # useless ? maybe we can use it to get all data paths as a dict
    def get(self, name: str) -> NormalizedValue:
        return self.__getattr__(name)
    
    def get_all(self) -> dict[str, NormalizedValue]:
        return self._data.copy()
