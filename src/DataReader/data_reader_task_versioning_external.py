from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig
from model.ini.ini_parser import INIParser
from .data_reader import DataReader

import re

from model.task.task import Task
from model.task.task_list import TaskList

class DataReaderTaskVersioningExternal(DataReader):
        # Kernel is external: we have 1 ini file for the sys tasks and N ini files (usually 2, ixl.ini and srlw.ini) for app tasks (current stream), and optionally the same for the previous stream, resulting in a max of 2N app inis + 2 sys ini (current + previous). 
    #def __init__(self, sys_ini_path: str | Path, app_ini_paths: list[str | Path], prev_sys_ini_path: Optional[str | Path] = None, prev_app_ini_paths: Optional[list[str | Path]] = None):
    def __init__(self, sys_imgconf_path: str | Path, app_imgconf_path: str | Path, prev_sys_imgconf_path: Optional[str | Path] = None, prev_app_imgconf_path: Optional[str | Path] = None):
        if prev_sys_imgconf_path is not None and prev_app_imgconf_path is not None:
            super().__init__(sys_imgconf_path, app_imgconf_path, prev_sys_imgconf_path, prev_app_imgconf_path)  # Pass all paths to the base class constructor
        elif sys_imgconf_path is not None and app_imgconf_path is None:
            raise ValueError("App imgconf path must be provided if sys imgconf path is provided.")
        elif sys_imgconf_path is None and app_imgconf_path is not None:
            raise ValueError("Sys imgconf path must be provided if app imgconf path is provided.")
        else:
            super().__init__(sys_imgconf_path, app_imgconf_path)  # Pass only current paths to the base class constructor
        
        """self.sys_imgconf = self._normalize_path(sys_imgconf_path)
        self.app_imgconf = self._normalize_path(app_imgconf_path)
        self.prev_sys_imgconf = self._normalize_path(prev_sys_imgconf_path) if prev_sys_imgconf_path else None
        self.prev_app_imgconf = self._normalize_path(prev_app_imgconf_path) if prev_app_imgconf_path else None"""

        #use dict from superclasse that has already normalized paths
        
