from pathlib import Path
import os
from abc import ABC, abstractmethod
import DataReader


from ConfigLoader.config_loader import VersioningMode

class DataReaderFileVersioning(DataReader):
    def __init__(self, data_path: Path | str, rules, mode : VersioningMode):
        super.__init__(data_path, rules)
        self.rules = rules
        self.mode = mode

    def scan_files(self):
        excluded_dirs = {d.lower() for d in self.rules["exclusion"]["dirs"]}
        allowed_ext = {e.lower() for e in self.rules["inclusion"]["extension"]}

        for dir_path, dir_names, file_names in os.walk(self.data_path):
            #per poter potare l alber odelle directory bisogna modificare dirnames a runtime
            dir_names[:] = [d for d in dir_names if d.lower() not in excluded_dirs]

            for name in file_names:
                p = Path(dir_path) / name
                if p.suffix.lower() in allowed_ext: #suffix ritorna la parte finale
                    yield p




        
def scan_files(root: Path, allowed_ext: set[str], exclude_dirs: set[str]):
    exclude_dirs = {d.lower() for d in exclude_dirs} # crea set per dir escluse e estensioni ammesse
    allowed_ext = {e.lower() for e in allowed_ext}

    for dirpath, dirnames, filenames in os.walk(root):
        #per poter potare l alber odelle directory bisogna modificare dirnames a runtime
        dirnames[:] = [d for d in dirnames if d.lower() not in exclude_dirs]

        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in allowed_ext: #suffix ritorna la parte finale
                yield p





