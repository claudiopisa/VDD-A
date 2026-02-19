from pathlib import Path
from abc import ABC, abstractmethod

class DataReader(ABC):
    
    def __init__(self, *data_paths: Path | str):
        self.data_paths: list[Path] = []
        
        for data_path in data_paths:
            if isinstance(data_path, str):
                data_path = Path(data_path)
            if not data_path.exists():
                raise FileNotFoundError(f"Data path '{data_path}' does not exist.")
            if not data_path.is_file():
                raise ValueError(f"Data path '{data_path}' is not a file.")
            
            self.data_paths.append(data_path)
        
        # Keep reference to first path for backward compatibility
        self.data_path = self.data_paths[0] if self.data_paths else None
    
    @abstractmethod
    def scan_files(self):
        pass
