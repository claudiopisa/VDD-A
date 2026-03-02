from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig
from configs.task_versioning_config import TaskVersioningConfig
from model.ini.ini_parser import INIParser
from .data_reader import DataReader

import re

from model.task.task import Task
from model.task.task_list import TaskList

class DataReaderTaskVersioningExternal(DataReader):
        
    # Kernel is external: we have 1 ini file for the sys tasks and N ini files (usually 2, ixl.ini and srlw.ini) for app tasks (current stream), and optionally the same for the previous stream, resulting in a max of 2N app inis + 2 sys ini (current + previous). 
    
    #def __init__(self, sys_ini_path: str | Path, app_ini_paths: list[str | Path], prev_sys_ini_path: Optional[str | Path] = None, prev_app_ini_paths: Optional[list[str | Path]] = None):
    def __init__(self, reader_config: TaskVersioningConfig, sys_imgconf_path: str | Path, app_imgconf_path: str | Path, prev_sys_imgconf_path: Optional[str | Path] = None, prev_app_imgconf_path: Optional[str | Path] = None):
        
        if prev_sys_imgconf_path is not None and prev_app_imgconf_path is not None:
            super().__init__(sys_imgconf_path=sys_imgconf_path, app_imgconf_path=app_imgconf_path, prev_sys_imgconf_path=prev_sys_imgconf_path, prev_app_imgconf_path=prev_app_imgconf_path)  # Pass all paths to the base class constructor
        
        elif sys_imgconf_path is not None and app_imgconf_path is None:
            raise ValueError("App imgconf path must be provided if sys imgconf path is provided.")
        
        elif sys_imgconf_path is None and app_imgconf_path is not None:
            raise ValueError("Sys imgconf path must be provided if app imgconf path is provided.")
        
        else:
            super().__init__(sys_imgconf_path=sys_imgconf_path, app_imgconf_path=app_imgconf_path)  # Pass only current paths to the base class constructor


        self.config = reader_config  # Load config for task versioning
        self.prev_sys_config: Optional[dict[str, str]] = {}
        self.prev_app_config: Optional[dict[str, str]] = {}
        self.tasks: TaskList = TaskList()

    def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):
        boot            = Path(section.get(self.config.boot_key, " ")).stem
        boot_ap         = Path(section.get(self.config.boot_ap_key, " ")).stem
        loader          = Path(section.get(self.config.loader_key, " ")).stem
        kernel          = Path(section.get(self.config.kernel_key, " ")).stem
        kernel_version  = section.get(self.config.kernel_version_key, " ").strip() # do i need to strip ? 

        if not is_prev:
            modified = "N/A" if not self._has_prev_imgconf() else ("NO" if self.prev_sys_config.get(kernel) == kernel_version else "YES")
            self.tasks.append(Task(name=boot, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=boot_ap, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=loader, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=kernel, type="SYSTEM", version=kernel_version, modified=modified))
        else:
            self.prev_sys_config[kernel] = kernel_version

    def _read_app_task(self, section: dict[str, str], is_prev: bool):
        # check if prev is valid
        if is_prev and not self._has_prev_imgconf():
            raise ValueError("Previous imgconf not available but trying to read previous app tasks")
        
        

    def _has_prev_imgconf(self) -> bool:
        return self.config.has_previous_release() and self.prev_sys_config and self.prev_sys_config.exists() and self.prev_app_config and self.prev_app_config.exists()

    def scan_files(self) -> TaskList:
        if self._has_prev_imgconf():
            prev_sys_parser = INIParser(self.prev_sys_imgconf)
            prev_sys_section = prev_sys_parser.get_section(self.config.sys_external_section)
            self._read_sys_tasks(prev_sys_section, is_prev=True)

            prev_app_parser = INIParser(self.prev_app_imgconf)
            prev_app_section = prev_app_parser.get_section(self.config.app_external_section)
            self._read_app_tasks(prev_app_section, is_prev=True)

        # load current
        sys_parser = INIParser(self.sys_imgconf)
        sys_section = sys_parser.get_section(self.config.sys_external_section)
        self._read_sys_tasks(sys_section, is_prev=False)

        app_parser = INIParser(self.app_imgconf)
        app_section = app_parser.get_section(self.config.app_external_section)
        self._read_app_tasks(app_section, is_prev=False)

        return self.tasks        