from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig
from utils.ini_parser import INIParser
from .data_reader import DataReader

import re

from model.task import Task
from model.task_list import TaskList

class DataReaderTaskVersioningInternal(DataReader):
    def __init__(self, imgconf_path: str | Path, prev_imgconf_path: Optional[str | Path] = None):
        super().__init__(imgconf_path, prev_imgconf_path)  # Pass both paths to the base class constructor

        self.imgconf = self._normalize_path(imgconf_path)
        self.prev_imgconf = self._normalize_path(prev_imgconf_path) if prev_imgconf_path else None
        
        self.config = TaskVersioningDefaultConfig()  # Load default config for task versioning
        #self.prev_config: dict[str, str] = self._load_prev_config() if self.prev_imgconf else {}
        self.tasks: TaskList = TaskList()


    def _read_sys_tasks(self, section: dict[str, str]):

        # get BOOT, BOOT_AP, LOADER, KERNEL, KERNEL_VERSION from config
        boot = section.get(self.config.sys_task.BOOT, " ")
        boot_ap = section.get(self.config.sys_task.BOOT_AP, " ")
        loader = section.get(self.config.sys_task.LOADER, " ")
        kernel = section.get(self.config.sys_task.KERNEL, " ")
        kernel_version = section.get(self.config.sys_task.KERNEL_VERSION, " ")
    
        self.tasks.append(Task(name=boot, type="SYSTEM", version="<TODO>"))
        self.tasks.append(Task(name=boot_ap, type="SYSTEM", version="<TODO>"))
        self.tasks.append(Task(name=loader, type="SYSTEM", version="<TODO>"))
        self.tasks.append(Task(name=kernel, type="SYSTEM", version=kernel_version), modified="NO" if (self.prev_imgconf and self.prev_config.get(self.config.sys_task.KERNEL_VERSION) == kernel_version) else "YES")

    def _read_app_tasks(self, section: dict[str, str]):
        # TODO
        return 

    def scan_files(self) -> TaskList:
        # load current config
        parser = INIParser(self.imgconf)
        section = parser.get_section(self.config.sections.internal)

        self._read_sys_tasks(section)
        self._read_app_tasks(section)

        return self.tasks   