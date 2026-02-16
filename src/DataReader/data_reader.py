from pathlib import Path
import os
from abc import ABC, abstractmethod

class DataReader(ABC):

    def __init__(self, data_path: Path | str):
        if isinstance(data_path, str):
            data_path = Path(data_path) # convert string to Path if necessary
        if not data_path.exists():
            raise FileNotFoundError(f"Data path '{data_path}' does not exist.")
        if not data_path.is_file():
            raise ValueError(f"Data path '{data_path}' is not a file.")
        
        self.data_path = data_path

    @abstractmethod
    def scan_files(self):
        pass
