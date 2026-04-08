from collections import defaultdict, deque
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional, Sequence

from configs.task_versioning_config import TaskVersioningConfig
from data_reader.task_versioning.task_versioning import TaskVersioning
from model.image_config.image_config_parser import ImageConfigParser
from ..data_reader import DataReader

import re

from model.task.task import Task
from model.task.task_list import TaskList
from utils.logger import get_logger


logger = get_logger(__name__)


type PathInput = str | Path
type PathSequence = Sequence[PathInput]
type ImageConfigPathDict = dict[str, Path | list[Path]]

class TaskVersioningExternal(TaskVersioning):
        
    # Kernel is external: we have 1 ini file for the sys tasks and N ini files (usually 2, ixl.ini and srlw.ini) for app tasks (current stream), and optionally the same for the previous stream, resulting in a max of 2N app inis + 2 sys ini (current + previous). 

    def __init__old(self, reader_config: TaskVersioningConfig):
        self.config = reader_config
        self.core = self.config.core

        if self.core.is_kernel_internal:
            raise ValueError("TaskVersioningExternal should not be used in internal kernel mode, check your core config kernel_mode value")
        
        #if not self.config.app_tasks:
            #raise ValueError("No app tasks specified in config, at least one is required for external kernel mode")
        
        if self.config.has_previous_release() and not self.config.previous_release_root:
            raise ValueError("Previous release enabled but no previous_release_root specified in config")
        
        #retireve roots and paths based on kernel mode
        workspace = self.core.stream_root_as_path
        logger.debug("Workspace resolved: %s", workspace)

        # create current paths
        self.sys_imgconf_path, self.app_imgconf_paths, self.taskorder_imgconf_path = self._retrieve_paths(workspace)

        logger.debug("Resolved sys_imgconf_path: %s", self.sys_imgconf_path)
        logger.debug("Resolved app_imgconf_paths: %s", self.app_imgconf_paths)
        logger.debug("Resolved taskorder_imgconf_path: %s", self.taskorder_imgconf_path)

        self.prev_sys_imgconf_path = None
        self.prev_app_imgconf_paths = None
        self.prev_taskorder_imgconf_path = None

        #create prev paths
        if self.config.has_previous_release():
            prev_workspace = self.config.previous_release_root_as_path
            logger.debug("Previous workspace resolved: %s", prev_workspace)

            self.prev_sys_imgconf_path, self.prev_app_imgconf_paths, self.prev_taskorder_imgconf_path = self._retrieve_paths(prev_workspace)

            logger.debug("Resolved prev_sys_imgconf_path: %s", self.prev_sys_imgconf_path)
            logger.debug("Resolved prev_app_imgconf_paths: %s", self.prev_app_imgconf_paths)
            logger.debug("Resolved prev_taskorder_imgconf_path: %s", self.prev_taskorder_imgconf_path)

         # DataReader normalizes all paths (single or list/tuple)
        super().__init__(
            sys_imgconf=self.sys_imgconf_path,
            app_imgconf=self.app_imgconf_paths,
            task_order=self.taskorder_imgconf_path,
            prev_sys_imgconf=self.prev_sys_imgconf_path,
            prev_app_imgconf=self.prev_app_imgconf_paths,
            prev_task_order=self.prev_taskorder_imgconf_path,
        )

        self.prev_sys_config: dict[str, str] = {}
        self.prev_app_config: dict[str, deque[str]] = defaultdict(deque)
        self.tasks: TaskList = TaskList()

    def __init__(self, config: TaskVersioningConfig):
        super().__init__(config=config)

        if self.core.is_kernel_internal:
            raise ValueError("TaskVersioningExternal should not be used in internal kernel mode, check your core config kernel_mode value")
        
        #if not self.config.app_tasks:
            #raise ValueError("No app tasks specified in config, at least one is required for external kernel mode")

        curr_paths: ImageConfigPathDict = self._retrieve_paths(is_prev=False)
        logger.debug("Resolved curr paths: %s", curr_paths)

        prev_paths: Optional[ImageConfigPathDict] = {}
        if self.config.has_previous_release():
            prev_paths = self._retrieve_paths(is_prev=True)
            logger.debug("Resolved prev paths: %s", prev_paths)

        self.parse_data_paths(**curr_paths, **prev_paths)

        self.prev_sys_config: dict[str, str] = {}
        self.prev_app_config: dict[str, deque[str]] = defaultdict(deque)
        self.tasks: TaskList = TaskList()


    #handle both current and prev case
    def _retrieve_paths(self, is_prev: bool) -> ImageConfigPathDict:
        workspace = self.config.previous_release_root_as_path if is_prev else self.core.stream_root_as_path
        logger.debug("%s workspace resolved: %s", "Previous" if is_prev else "Current", workspace)

        app_root = workspace / self.config.app_root
        sys_root = workspace / self.config.sys_root

        logger.debug("Resolving paths with app_root: %s and sys_root: %s", app_root, sys_root)

        return {
            f"{'prev_' if is_prev else ''}sys_imgconf_path"  : sys_root / self.core.image_config_name,
            f"{'prev_' if is_prev else ''}app_imgconf_paths" : [app_root / task for task in self.config.get_app_tasks(as_dict=False)],
            f"{'prev_' if is_prev else ''}task_order_path"   : app_root / "taskorder.ini",
        }


    def _has_prev_imgconf(self) -> bool:
        return (
            super()._has_prev_imgconf()
            and "prev_sys_imgconf_path" in self._data
            and "prev_app_imgconf_paths" in self._data
            and "prev_task_order_path" in self._data
        )

    """def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):
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
            self.prev_sys_config[kernel] = kernel_version"""

    
    def _read_taskorder(self, taskorder_path: Path) -> list[dict[str, str]]:
        # taskorder.ini has n sections, while the maximum number possible is N. Therefore we have AP0, ..., AP(n-1). 
        # As for now, the maximum number of AP sections is N=4 (AP0..AP3), but we want to be able to handle more in case we have more in the future, so we need to extract the indices dynamically.
        # The .ini file has a arbitrary number of section, from n = 0 to n = N, where N is unknown a priori. 
        # The minimum number of section is n=1, therefore we can have 0 < n <= N sections, so we always have at least AP0.
        parser = ImageConfigParser(taskorder_path)
        has_sections = True
        sections: list[dict[str, str]] = []
        i = 0

        while has_sections:
            try:
                section = parser.get_section(f"{self.config.ap_section_key}{i}") # find APi section, where 0 <= i <= N-1, N is unknown a priori
                sections.append(section)
                i += 1
            except Exception: # catch the custom exception raised by ImageConfigParser when section is not found
                has_sections = False

        return sections


    def _has_prev_imgconf_old(self) -> bool:
        return (
            self.config.has_previous_release()
            and self.prev_sys_imgconf is not None
            and self.prev_sys_imgconf.exists()
            and bool(self.prev_app_imgconf_paths)
            and self.prev_task_order is not None
            and self.prev_task_order.exists()
        )
    

    def _flatten_taskorder_names(self, sections: list[dict[str, str]]) -> list[str]:
        ordered_names: list[str] = []

        for sec in sections: # for each AP0, ..., APn
            # Extract indices from NomeTask{i} keys without using regex
            #indices: list[int] = []
            #prefix = self.config.app_name_key  # es: NomeTask

            #for key in sec.keys():
                #if key.startswith(prefix):
                  # suffix = key[len(prefix):]
                    #if suffix.isdigit():
                     #   indices.append(int(suffix))

            #indices.sort()

            size = len(sec) # number of tasks within section

            for i in range(1, size + 1):
                raw = sec.get(f"{self.config.app_name_key}{i}", "").strip()
                if raw:
                    ordered_names.append(Path(raw).stem)

        return ordered_names

    def _build_app_catalog(self, app_paths: Sequence[Path]) -> dict[str, list[dict[str, str]]]:
        """
        Catalog: task_name -> [{type, version}, ...]
        Each task name (dictionary key) is associated with a list of occurrences,
        whether they appear in the same file or in different files.
        Multiple entries handle duplicate/reschedule cases.
        """
        catalog: dict[str, list[dict[str, str]]] = defaultdict(list)

        for ini_path in app_paths:
            section = ImageConfigParser(ini_path).get_section(self.config.app_external_section)

            # Find the indices available through NomeTask{i}
            """indices: list[int] = []
            prefix = self.config.app_name_key
            for key in section.keys():
                if key.startswith(prefix):
                    suffix = key[len(prefix):]
                    if suffix.isdigit():
                        indices.append(int(suffix))
            indices = sorted(set(indices))"""

            size = len(section)

            for i in range(1, size + 1):
                raw_name = section.get(f"{self.config.app_name_key}{i}", "").strip()
                type_ = section.get(f"{self.config.app_type_key}{i}", "").strip()
                version = section.get(f"{self.config.app_version_key}{i}", "").strip()

                #if not raw_name:
                #    continue
                #if type_ and type_.upper() in self.config.excluded_task_types:
                  #  continue

                if raw_name and (type_.upper() not in self.config.excluded_task_types):
                    name = Path(raw_name).stem
                    catalog[name].append(
                        {
                            "type": type_ if type_ else "APP",
                            "version": version if version else "<N/A>",
                        }
                    )

        return catalog

    def _read_app_tasks(self, ordered_names: list[str], catalog: dict[str, list[dict[str, str]]], is_prev: bool):
        """
        Consume tasks in taskorder order.
        - is_prev=True: save baseline versions in a per-name queue.
        - is_prev=False: create Task objects and compare them with the baseline.
        """
        if is_prev and not self._has_prev_imgconf():
            raise ValueError("Previous imgconf not available but trying to read previous app tasks")

        used_index_by_name: dict[str, int] = defaultdict(int)

        for name in ordered_names:
            entries = catalog.get(name, [])
            #entries = catalog[name] if name in catalog else []
            if not entries:
                # Task scheduled but not found in the containers
                continue

            idx = used_index_by_name[name]
            if idx >= len(entries):
                # If the task appears more times than the available entries, ignore the extras
                continue

            used_index_by_name[name] += 1
            entry = entries[idx]
            curr_version = entry["version"]
            curr_type = entry["type"]

            if is_prev:
                self.prev_app_config[name].append(curr_version)
                continue

            if not self._has_prev_imgconf():
                modified = "N/A"
            else:
                if self.prev_app_config[name]:
                    prev_version = self.prev_app_config[name].popleft()
                    modified = "NO" if prev_version == curr_version else "YES"
                else:
                    modified = "N/A"

            self.tasks.append(
                Task(
                    name=name,
                    type_=curr_type,
                    version=curr_version,
                    modified=modified,
                )
            )

    def _scan_files(self) -> TaskList:
        logger.debug("Starting external task scan")

        # 1) previous baseline
        if self._has_prev_imgconf():
            logger.debug("Previous release detected: loading baseline task versions")

            prev_sys_section = ImageConfigParser(self.prev_sys_imgconf).get_section(self.config.sys_external_section)
            self._read_sys_tasks(prev_sys_section, is_prev=True)

            prev_sections = self._read_taskorder(self.prev_task_order)
            prev_ordered_names = self._flatten_taskorder_names(prev_sections)
            prev_catalog = self._build_app_catalog(self.prev_app_imgconf)
            self._read_app_tasks(prev_ordered_names, prev_catalog, is_prev=True)

        # 2) current
        logger.debug("Loading current release task versions")

        sys_section = ImageConfigParser(self.sys_imgconf_path).get_section(self.config.sys_external_section)
        self._read_sys_tasks(sys_section, is_prev=False)
    
        curr_sections = self._read_taskorder(self.task_order_path)
        curr_ordered_names = self._flatten_taskorder_names(curr_sections)
        curr_catalog = self._build_app_catalog(self.app_imgconf_paths)
        self._read_app_tasks(curr_ordered_names, curr_catalog, is_prev=False)

        logger.info("External task scan completed: %d tasks loaded", len(self.tasks))

        #return self.tasks