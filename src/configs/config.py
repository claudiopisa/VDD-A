from abc import ABC, abstractmethod
from pathlib import Path

class Config(ABC):
    @abstractmethod
    def load_user_config(self, path: str | Path):
        pass
    
    @abstractmethod
    def load_default_config(self):
        pass