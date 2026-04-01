from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from configs.task_versioning_config import TaskVersioningConfig
from model.ini.image_config_parser import INIParser
from ..data_reader import DataReader
from model.task.task import Task
from model.task.task_list import TaskList
from utils.logger import get_logger

logger = get_logger(__name__)


class TaskVersioningInternal(DataReader):

    def __init__(self, reader_config: TaskVersioningConfig):
        self.config = reader_config
        self.core = self.config.core

        if not self.core.is_kernel_internal:
            raise ValueError(
                "TaskVersioningInternal should not be used in external kernel mode, "
                "check your core config kernel_mode value"
            )

        if self.config.has_previous_release() and not self.config.previous_release_root:
            raise ValueError("Previous release enabled but no previous_release_root specified in config")

        workspace = self.core.stream_root_as_path
        logger.debug("Workspace resolved: %s", workspace)

        self.imgconf_path = self._retrieve_path(workspace)
        logger.debug("Resolved imgconf_path: %s", self.imgconf_path)

        self.prev_imgconf_path = None
        if self.config.has_previous_release():
            prev_workspace = self.config.previous_release_root_as_path
            logger.debug("Previous workspace resolved: %s", prev_workspace)
            
            self.prev_imgconf_path = self._retrieve_path(prev_workspace)
            logger.debug("Resolved prev_imgconf_path: %s", self.prev_imgconf_path)

        super().__init__(
            imgconf=self.imgconf_path,
            prev_imgconf=self.prev_imgconf_path,
        )

        self.prev_config: dict[str, str] = {}
        self.tasks: TaskList = TaskList()

    def _retrieve_path(self, workspace: Path) -> Path:
        root = workspace / self.config.app_root
        imgconf_path = root / self.core.image_config_name

        logger.debug("Resolving imgconf with root: %s -> %s", root, imgconf_path)

        return imgconf_path

    def _has_prev_imgconf(self) -> bool:
        return (
            super()._has_prev_imgconf()
            and "prev_imgconf" in self._data
        )

    """def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):
        boot           = Path(section.get(self.config.boot_key, " ")).stem.upper()
        boot_ap        = Path(section.get(self.config.boot_ap_key, " ")).stem.upper()   
        loader         = Path(section.get(self.config.loader_key, " ")).stem.upper()
        kernel         = Path(section.get(self.config.kernel_key, " ")).stem.upper()
        kernel_version = section.get(self.config.kernel_version_key, " ").strip().upper()

        if not is_prev:
            modified = "N/A" if not self._has_prev_imgconf() else (
                "NO" if self.prev_config.get(kernel) == kernel_version else "YES"
            )
            self.tasks.append(Task(name=boot,      type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=boot_ap,   type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=loader,    type="SYSTEM", version="<TODO>"))
            self.tasks.append(Task(name=kernel,    type="SYSTEM", version=kernel_version, modified=modified))
        else:
            self.prev_config[kernel] = kernel_version"""

    def _read_app_tasks(self, section: dict[str, str], is_prev: bool):
        if is_prev and not self._has_prev_imgconf():
            raise ValueError("Previous imgconf not available but trying to read previous app tasks")

        try:
            num_tasks = int(section.get(self.config.num_tasks, "").strip())
        except ValueError:
            raise ValueError(
                f"NumTask value not found or not valid in: "
                f"{self.prev_imgconf if is_prev else self.imgconf}"
            )

        for i in range(1, num_tasks + 1):
            type_ = section.get(f"{self.config.app_type_key}{i}", "").strip().upper()

            if type_.upper() not in self.config.excluded_task_types:
                raw_name = section.get(f"{self.config.app_path_key}{i}", "").strip()
                version = section.get(f"{self.config.app_version_key}{i}", "").strip()

                if not raw_name:
                    raise ValueError(f"App task name not found for task {i} in: {self.prev_imgconf if is_prev else self.imgconf}")
                if not version:
                    raise ValueError(f"App task version not found for task {i} in: {self.prev_imgconf if is_prev else self.imgconf}")

                if raw_name and version:
                    name = Path(raw_name).stem.upper()

                    if not is_prev:
                        modified = "N/A" if not self._has_prev_imgconf() else (
                            "NO" if self.prev_config.get(name) == version else "YES"
                        )
                        self.tasks.append(Task(name=name, type=type_, version=version, modified=modified))
                    else:
                        self.prev_config[name] = version

    def scan_files(self) -> TaskList:
        logger.debug("Starting internal task scan")

        if self._has_prev_imgconf():
            logger.debug("Previous release detected: loading baseline task versions")
            prev_section = INIParser(self.prev_imgconf).get_section(self.config.sys_internal_section)
            self._read_sys_tasks(prev_section, is_prev=True)
            self._read_app_tasks(prev_section, is_prev=True)

        logger.debug("Loading current release task versions")
        section = INIParser(self.imgconf).get_section(self.config.sys_internal_section)
        self._read_sys_tasks(section, is_prev=False)
        self._read_app_tasks(section, is_prev=False)

        logger.info("Internal task scan completed: %d tasks loaded", len(self.tasks))
        
        return self.tasks