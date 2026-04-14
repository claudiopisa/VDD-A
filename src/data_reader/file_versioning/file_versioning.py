import logging
from pathlib import Path
import os
import re
from configs.file_versioning_config import FileVersioningConfig
from model.file.file import File
from model.file.file_collection import FileCollection
from ..data_reader import DataReader

VERSION_NOT_FOUND = "NOT_FOUND"
VERSION_NOT_AVAILABLE = "N/A"

logger = logging.getLogger(__name__)

class FileVersioning(DataReader):
    def __init__(self, config: FileVersioningConfig):
        super().__init__(config=config)

        root = self._retrieve_paths()
        self.parse_data_paths(data_path=root)

    def _retrieve_paths(self) -> Path:
        workspace = self.config.core.stream_root_as_path
        component = self.config.component_root
        root = workspace / component

        if not root.exists():
            raise FileNotFoundError(f"Root path does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"Root path is not a directory: {root}")
        
        return root
    

    def _scan_files(self) -> FileCollection:
        excluded_dirs = {d.lower() for d in self.config.excluded_dirs}
        allowed_ext = {e.lower() for e in self.config.allowed_extensions}
        criteria = self.config.version_extraction_criteria

        #files = FileList()
        files = FileCollection()

        for dir_path, dir_names, file_names in os.walk(self.data_path):
            #per poter potare l alber odelle directory bisogna modificare dirnames a runtime
            dir_names[:] = [d for d in dir_names if d.lower() not in excluded_dirs]

            for name in file_names:
                p = Path(dir_path) / name
                if p.suffix.lower() in allowed_ext: # suffix returns the file extension
                    # extract version (uses configured criteria when present)
                    version = self._extract_version(p, criteria)

                    if version == VERSION_NOT_FOUND:
                        logger.warning("Version not found for file: %s", p)
                        version = VERSION_NOT_AVAILABLE

                    #files.append(File(path=str(p), version=version))
                    files.add(folder=str(p.parent), file=File(name=name, version=version))

        return files


    def _extract_version(self, path: Path, criteria=None) -> str:    
        VERSION_VALUE_RE = re.compile(
            r"(?:\\\\*|//|--|;|#).*Versione\\s*:?\\s*(\\d+\\.\\d+)" if criteria is None else criteria,
            re.IGNORECASE
        )
    # old JSON regex: "version_extraction_criteria": "(?:\\\\*|//|--|;|#).*Versione\\s*:?\\s*(\\d+\\.\\d+)",
     
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = VERSION_VALUE_RE.search(line)
                if match:
                    return match.group(1)

        return VERSION_NOT_FOUND

        
"""def scan_files(root: Path, allowed_ext: set[str], exclude_dirs: set[str]):
    exclude_dirs = {d.lower() for d in exclude_dirs} # create sets for excluded directories and allowed extensions
    allowed_ext = {e.lower() for e in allowed_ext}

    for dirpath, dirnames, filenames in os.walk(root):
        # to prune the directory tree, dirnames must be modified at runtime
        dirnames[:] = [d for d in dirnames if d.lower() not in exclude_dirs]

        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in allowed_ext: # suffix returns the file extension
                yield p"""





