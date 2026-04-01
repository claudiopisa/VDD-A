from pathlib import Path
import os
import re
from configs.file_versioning_config import FileVersioningConfig
from ..data_reader import DataReader


class FileVersioning(DataReader):
    def __init__(self, config: FileVersioningConfig):
        #super().__init__(data_path=data_path)
        self.config = config
        self.root = self._retrieve_paths()

        super().__init__(data_path=self.root)

    def _retrieve_paths(self) -> Path:
        workspace = self.config.core.stream_root_as_path
        component = self.config.component_root
        root = workspace / component

        if not root.exists():
            raise FileNotFoundError(f"Root path does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"Root path is not a directory: {root}")
        
        return root
    

    def scan_files(self):
        excluded_dirs = {d.lower() for d in self.config.excluded_dirs}
        allowed_ext = {e.lower() for e in self.config.allowed_extensions}
        criteria = self.config.version_extraction_criteria

        for dir_path, dir_names, file_names in os.walk(self.data_path):
            #per poter potare l alber odelle directory bisogna modificare dirnames a runtime
            dir_names[:] = [d for d in dir_names if d.lower() not in excluded_dirs]

            for name in file_names:
                p = Path(dir_path) / name
                if p.suffix.lower() in allowed_ext: #suffix ritorna la parte finale
                    # extract version (uses configured criteria when present)
                    try:
                        version = self._extract_version(p, criteria)
                    except Exception:
                        version = None

                    # yield a tuple of (string path, version) to avoid WindowsPath repr
                    yield (str(p), version)

    def _extract_version(self, path: Path, criteria=None):
        version = None
    
        VERSION_VALUE_RE = re.compile(
            r"(?:\\\\*|//|--|;|#).*Versione\\s*:?\\s*(\\d+\\.\\d+)" if criteria is None else criteria,
            re.IGNORECASE
        )
    # old regex json "version_extraction_criteria": "(?:\\\\*|//|--|;|#).*Versione\\s*:?\\s*(\\d+\\.\\d+)",
     
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = VERSION_VALUE_RE.search(line)
                if match:
                    return match.group(1)

        return version

        
"""def scan_files(root: Path, allowed_ext: set[str], exclude_dirs: set[str]):
    exclude_dirs = {d.lower() for d in exclude_dirs} # crea set per dir escluse e estensioni ammesse
    allowed_ext = {e.lower() for e in allowed_ext}

    for dirpath, dirnames, filenames in os.walk(root):
        #per poter potare l alber odelle directory bisogna modificare dirnames a runtime
        dirnames[:] = [d for d in dirnames if d.lower() not in exclude_dirs]

        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in allowed_ext: #suffix ritorna la parte finale
                yield p"""





