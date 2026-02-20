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
        # find all keys that start with "FileTask" and "RelTask"
        file_task_pattern = re.compile(rf"^{self.config.app_task.path}\d*$")  # matches FileTask, FileTask1, FileTask2, etc.
        rel_task_pattern = re.compile(rf"^{self.config.app_task.version}\d*$")  # matches RelTask, RelTask1, RelTask2, etc.

        file_tasks = {key: value for key, value in section.items() if file_task_pattern.match(key)}
        rel_tasks = {key: value for key, value in section.items() if rel_task_pattern.match(key)}

        for file_key, file_name in file_tasks.items():
            # Derive the corresponding version key by replacing the prefix
            version_key = file_key.replace(self.config.app_task.path, self.config.app_task.version)
            version = rel_tasks.get(version_key, "<TODO>")  # Get version or use placeholder if not found

            self.tasks.append(Task(name=file_name, type="APPLICATION", version=version), modified="NO" if (self.prev_imgconf and self.prev_config.get(version_key) == version) else "YES")


    def scan_files(self) -> TaskList:
        # load current config
        parser = INIParser(self.imgconf)
        section = parser.get_section(self.config.sections.internal)

        self._read_sys_tasks(section)
        self._read_app_tasks(section)
        return self.tasks   