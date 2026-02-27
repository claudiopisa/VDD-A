from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig
from configs.task_versioning_config import TaskVersioningConfig
from model.data_path import DataPath
from model.ini.ini_parser import INIParser
from .data_reader import DataReader

import re

from model.task.task import Task
from model.task.task_list import TaskList

class DataReaderTaskVersioningInternal(DataReader):
    def __init_old__(self, user_config: TaskVersioningConfig, default_config: TaskVersioningDefaultConfig, imgconf_path: str | Path, prev_imgconf_path: Optional[str | Path] = None):
        if prev_imgconf_path is not None:
            super().__init__(imgconf_path, prev_imgconf_path)  # Pass both paths to the base class constructor
        else:
            super().__init__(imgconf_path)  # Pass only the current path to the base class constructor

        self.imgconf = self._normalize_path(imgconf_path)
        self.prev_imgconf = self._normalize_path(prev_imgconf_path) if prev_imgconf_path else None
        
        self.config = default_config  # Load default config for task versioning
        self.user_config = user_config  # Load user config for task versioning
        #self.prev_config: dict[str, str] = self._load_prev_config() if self.prev_imgconf else None
        self.prev_config: Optional[dict[str, str]] = {}
        self.tasks: TaskList = TaskList()

    def __init__(self, imgconf_path: DataPath, prev_imgconf_path: Optional[DataPath] = None):
        if prev_imgconf_path is not None:
            super().__init__(imgconf_path, prev_imgconf_path)  # Pass both paths to the base class constructor
        else:
            super().__init__(imgconf_path)  # Pass only the current path to the base class constructor

        self.imgconf = self.get(imgconf_path.alt_name) 
        self.prev_imgconf = self.get(prev_imgconf_path.alt_name) if prev_imgconf_path else None
        
        self.config = TaskVersioningDefaultConfig()  # Load default config for task versioning
        self.prev_config: Optional[dict[str, str]] = {}
        self.tasks: TaskList = TaskList()


    # refactor read sys tasks in order to handle prev config as well
    def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):

        boot = Path(section.get(self.config.sys_task.BOOT, " ")).stem
        boot_ap = Path(section.get(self.config.sys_task.BOOT_AP, " ")).stem
        loader = Path(section.get(self.config.sys_task.LOADER, " ")).stem
        kernel = Path(section.get(self.config.sys_task.KERNEL, " ")).stem
        kernel_version = section.get(self.config.sys_task.KERNEL_VERSION, " ")

        if not is_prev:
            modified = "N/A" if not self.prev_imgconf else ("NO" if self.prev_config.get(kernel) == kernel_version else "YES")
            self.tasks.append(Task(name=boot, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=boot_ap, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=loader, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=kernel, type="SYSTEM", version=kernel_version, modified=modified))
        else:
            self.prev_config[kernel] = kernel_version
            # TODO: save also other sys tasks versions

    
    # util function that contains for loop that itertes over ini file and salves info into a dict and returns it
    def _read_app_tasks(self, section, is_prev: bool):
        try:
            num_tasks = int(section.get(self.config.num_tasks, "").strip())
        except ValueError:
            raise Exception(f"NumTask value not found or not valid in the INI file: {self.prev_imgconf if is_prev else self.imgconf}")
            # TODO: add fallback with regex

        i = 1
        while i <= num_tasks:
            type_ = section.get(f"{self.config.app_task.type}{i}", "").strip()

            if type_ and type_.upper() not in self.config.rules.exclusion.task_type:

                name = Path(section.get(f"{self.config.app_task.path}{i}", "").strip()).stem
                version = section.get(f"{self.config.app_task.version}{i}", "").strip()
                
                if not is_prev:
                    modified = "N/A" if not self.prev_imgconf else ("NO" if self.prev_config.get(name) == version else "YES")
                    self.tasks.append(Task(name=name, type=type_, version=version, modified=modified))
                else:
                    self.prev_config[name] = version

            i += 1


    def scan_files(self) -> TaskList:
        if self.prev_imgconf:
            prev_parser = INIParser(self.prev_imgconf)
            prev_section = prev_parser.get_section(self.config.sections.internal)
            self._read_sys_tasks(prev_section, is_prev=True)
            self._read_app_tasks(prev_section, is_prev=True)

        # load current 
        parser = INIParser(self.imgconf)
        section = parser.get_section(self.config.sections.internal)
        self._read_sys_tasks(section, is_prev=False)
        self._read_app_tasks(section, is_prev=False)
            
        return self.tasks
    

