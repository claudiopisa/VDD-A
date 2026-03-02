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
   

    def __init__(self, reader_config: TaskVersioningConfig, imgconf_path: str | Path, prev_imgconf_path: Optional[str | Path] = None):
        super().__init__(imgconf=imgconf_path, prev_imgconf=prev_imgconf_path)
        
        self.config = reader_config
        self.prev_config: Optional[dict[str, str]] = {}
        self.tasks: TaskList = TaskList()


    # refactor read sys tasks in order to handle prev config as well
    def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):
        # with old `config` implementation:
        #
        """boot = Path(section.get(self.config.sys_task.BOOT, " ")).stem
        boot_ap = Path(section.get(self.config.sys_task.BOOT_AP, " ")).stem
        loader = Path(section.get(self.config.sys_task.LOADER, " ")).stem
        kernel = Path(section.get(self.config.sys_task.KERNEL, " ")).stem
        kernel_version = section.get(self.config.sys_task.KERNEL_VERSION, " ")"""

        #new config implementation with TaskVersioningConfig:
        boot            = Path(section.get(self.config.boot_key, " ")).stem
        boot_ap         = Path(section.get(self.config.boot_ap_key, " ")).stem
        loader          = Path(section.get(self.config.loader_key, " ")).stem
        kernel          = Path(section.get(self.config.kernel_key, " ")).stem
        kernel_version  = section.get(self.config.kernel_version_key, " ").strip() # do i need to strip ? 

        if not is_prev:
            modified = "N/A" if not self._has_prev_imgconf() else ("NO" if self.prev_config.get(kernel) == kernel_version else "YES")
            self.tasks.append(Task(name=boot, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=boot_ap, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=loader, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=kernel, type="SYSTEM", version=kernel_version, modified=modified))
        else:
            self.prev_config[kernel] = kernel_version
            # TODO: save also other sys tasks versions

    
    # util function that contains for loop that itertes over ini file and salves info into a dict and returns it
    def _read_app_tasks(self, section, is_prev: bool):

        #check if prev is valid
        if is_prev and not self._has_prev_imgconf():
            raise Exception("Previous imgconf not available but trying to read previous app tasks -> this should not happen, check the logic for enabling previous release and loading prev imgconf")
        
        try:
            num_tasks = int(section.get(self.config.num_tasks, "").strip())
        except ValueError:
            raise Exception(f"NumTask value not found or not valid in the INI file: {self.prev_imgconf if is_prev else self.imgconf}")
            # TODO: add fallback with regex

        i = 1
        while i <= num_tasks:
            type_ = section.get(f"{self.config.app_type_key}{i}", "").strip()

            if type_ and type_.upper() not in self.config.excluded_task_types:

                name = Path(section.get(f"{self.config.app_path_key}{i}", "").strip()).stem
                version = section.get(f"{self.config.app_version_key}{i}", "").strip()
                
                if not is_prev:
                    modified = "N/A" if not self._has_prev_imgconf() else ("NO" if self.prev_config.get(name) == version else "YES")
                    self.tasks.append(Task(name=name, type=type_, version=version, modified=modified))
                else:
                    #out[name] = version
                    self.prev_config[name] = version

            i += 1


    """def scan_files_old(self) -> TaskList:
        if self.prev_imgconf:
            prev_parser = INIParser(self.prev_imgconf)
            prev_section = prev_parser.get_section(self.config.sections.SETTINGS)
            self._read_sys_tasks(prev_section, is_prev=True)
            self._read_app_tasks(prev_section, is_prev=True)

        # load current 
        parser = INIParser(self.imgconf)
        section = parser.get_section(self.config.sections.SETTINGS)
        self._read_sys_tasks(section, is_prev=False)
        self._read_app_tasks(section, is_prev=False)
            
        return self.tasks"""

    # simple utility function that checks whether the previous release is enabled and has root specified and, if so, check if prev imgconf exists
    def _has_prev_imgconf(self) -> bool:
        return self.config.has_previous_release() and self.prev_imgconf and self.prev_imgconf.exists()
    
    # simple utility function that evaluates the `modified` status (DOENST WORK !!!)
    def _modified_status(self, name: str) -> str:
        if not self._has_prev_imgconf():
            return "N/A"
        else:
            prev_version = self.prev_config.get(name)
            if prev_version is None:
                return "N/A"
            else:
                current_version = self.prev_config.get(name)  # for both sys and app tasks we save them in the same dict with name as key, so we can use the same logic to get the current version

                return "NO" if prev_version == current_version else "YES"
    
    # TODO: handle duplicate task names (sigle task could be rescheduled and appear multiple times in the imgconf)
    def scan_files(self) -> TaskList:
        # load prev
        if self._has_prev_imgconf():
            #print("DEBUG| Previous imgconf detected, loading previous tasks versions for comparison...")
            prev_parser = INIParser(self.prev_imgconf)
            prev_section = prev_parser.get_section(self.config.sys_internal_section)
            self._read_sys_tasks(prev_section, is_prev=True)
            self._read_app_tasks(prev_section, is_prev=True)

        # load current 
        parser = INIParser(self.imgconf)
        section = parser.get_section(self.config.sys_internal_section)
        self._read_sys_tasks(section, is_prev=False)
        self._read_app_tasks(section, is_prev=False)

        return self.tasks