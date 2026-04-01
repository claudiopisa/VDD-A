from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig
from configs.task_versioning_config import TaskVersioningConfig

from .data_reader import DataReader

import re

from model.task.task import Task
from model.task.task_list import TaskList
from abc import ABC, abstractmethod
from utils.logger import get_logger

logger = get_logger(__name__)
    

class DataReaderTaskVersioning(DataReader):
    #Use cases:
    # Kernel is internal: we have max 2 ini files to read, current and optional previous, the former in the NSPC dir, the latter in the previous stream root if available. Both contain a [Settings] section with BOOT, BOOTAP, Loader, Kernel and application tasks with their type and version. We compare BOOT, BOOTAP, Loader, Kernel and application tasks versions between current and previous ini to determine if they are modified or not.
    # Kernel is external: we have 1 ini file for the sys tasks and N ini files (usually 2, ixl.ini and srlw.ini) for app tasks (current stream), and optionally the same for the previous stream, resulting in a max of 2N app inis + 2 sys ini (current + previous). The sys ini contains BOOT, BOOTAP, Loader, Kernel with their version, while the app ini(s) contain application tasks with their type and version. We compare BOOT, BOOTAP, Loader, Kernel versions from the sys ini and application tasks versions from the app ini(s) between current and previous stream to determine if they are modified or not.
    
    def __init__old(self, reader_config: TaskVersioningConfig):
        self.config = reader_config
        self.prev_config: Optional[dict[str, str]] = None
        self.tasks: TaskList = TaskList()

    def __init__(self, config: TaskVersioningConfig):
        super().__init__(config=config)
        self.prev_config: Optional[dict[str, str]] = {}
        self.tasks: TaskList = TaskList()

        #retireve roots and paths based on kernel mode
        #self.workspace = self.core.stream_root_as_path
        #logger.debug("Workspace resolved: %s", self.workspace)

    
    @abstractmethod
    def _scan_files(self):
        pass

    def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):
        boot            = Path(section.get(self.config.boot_key, " ")).stem.upper()
        boot_ap         = Path(section.get(self.config.boot_ap_key, " ")).stem.upper()
        loader          = Path(section.get(self.config.loader_key, " ")).stem.upper()
        kernel          = Path(section.get(self.config.kernel_key, " ")).stem.upper()
        kernel_version  = section.get(self.config.kernel_version_key, " ").strip().upper() # do i need to strip ? 

        #logger.debug("Reading sys tasks: boot=%s, boot_ap=%s, loader=%s, kernel=%s, kernel_version=%s", boot, boot_ap, loader, kernel, kernel_version)

        #if names are empty, raise exception
        if not boot or not boot_ap or not loader or not kernel \
            or len(boot) == 0 or len(boot_ap) == 0 or len(loader) == 0 or len(kernel) == 0:
            raise ValueError("One or more sys task names are empty in the imgconf section %s", section)

        if not is_prev:
            modified = "N/A" if not self._has_prev_imgconf() else ("NO" if self.prev_sys_config.get(kernel) == kernel_version else "YES")
            self.tasks.append(Task(name=boot, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=boot_ap, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=loader, type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=kernel, type="SYSTEM", version=kernel_version, modified=modified))
        else:
            self.prev_sys_config[kernel] = kernel_version

    @abstractmethod
    def _read_app_tasks(self, section: dict[str, str], is_prev: bool):
        pass
        
    
    def _has_prev_imgconf(self) -> bool:
        return self.config.has_previous_release() and self.config.previous_release_root
    