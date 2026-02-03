from pathlib import Path
import os
from abc import ABC, abstractmethod

class DataReader:

    def __init__(self, data_path: Path | str):
        self.data_path = data_path
    
    @abstractmethod
    def scan_files(self):
        pass
