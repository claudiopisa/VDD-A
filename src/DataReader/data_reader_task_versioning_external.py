from collections import defaultdict, deque
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
    def __init__old(self, reader_config: TaskVersioningConfig, sys_imgconf_path: str | Path, app_imgconf_paths: dict[str, Path], task_order: str | Path, prev_sys_imgconf_path: Optional[str | Path] = None, prev_app_imgconf_path: Optional[str | Path] = None, prev_task_order: Optional[str | Path] = None):
        
        if prev_sys_imgconf_path is not None and prev_app_imgconf_path is not None:
            super().__init__(sys_imgconf=sys_imgconf_path, app_imgconf=app_imgconf_paths, prev_sys_imgconf=prev_sys_imgconf_path, prev_app_imgconf=prev_app_imgconf_path)  # Pass all paths to the base class constructor
        
        elif sys_imgconf_path is not None and len(app_imgconf_paths) == 0:
            raise ValueError("App imgconf path must be provided if sys imgconf path is provided.")
        
        elif sys_imgconf_path is None and len(app_imgconf_paths) > 0:
            raise ValueError("Sys imgconf path must be provided if app imgconf path is provided.")
        
        else:
            # prepare app imgconf parameter
            
            imgconf_kwargs = {
                "sys_imgconf": sys_imgconf_path,
            }

            imgconf_kwargs.update(app_imgconf_paths)  # add all app imgconf paths to the kwargs dict

            #super().__init__(sys_imgconf=sys_imgconf_path, app_imgconf=app_imgconf_paths)  # Pass only current paths to the base class constructor
            super().__init__(**imgconf_kwargs)  # Pass all current paths as kwargs to the base class constructor

        self.config: TaskVersioningConfig = reader_config  # Load config for task versioning
        self.prev_sys_config: Optional[dict[str, str]] = {}
        self.task_order: Path = Path(task_order) if isinstance(task_order, str) else task_order
        self.prev_task_order: Optional[Path] = Path(prev_task_order) if isinstance(prev_task_order, str) else prev_task_order if prev_task_order else None
        self.prev_app_config: Optional[dict[str, str]] = {}
    
        self.tasks: TaskList = TaskList()

    def __init__(
        self,
        reader_config: TaskVersioningConfig,
        sys_imgconf_path: str | Path,
        app_imgconf_paths: dict[str, Path],
        task_order: str | Path,
        prev_sys_imgconf_path: Optional[str | Path] = None,
        prev_app_imgconf_paths: Optional[dict[str, Path]] = None,
        prev_task_order: Optional[str | Path] = None,
    ):
        if sys_imgconf_path is None:
            raise ValueError("sys_imgconf_path is required")
        if not app_imgconf_paths:
            raise ValueError("app_imgconf_paths is required")
        if task_order is None:
            raise ValueError("task_order is required")

        self.config: TaskVersioningConfig = reader_config
        self.task_order: Path = Path(task_order)
        self.prev_task_order: Optional[Path] = Path(prev_task_order) if prev_task_order else None

        # Mantieni sempre i dict app separati come attributi di classe (non nel base)
        self.app_imgconf_paths: dict[str, Path] = {k: Path(v) for k, v in app_imgconf_paths.items()}
        self.prev_app_imgconf_paths: dict[str, Path] = (
            {k: Path(v) for k, v in prev_app_imgconf_paths.items()} if prev_app_imgconf_paths else {}
        )

        kwargs = {"sys_imgconf": sys_imgconf_path}
        kwargs.update(self.app_imgconf_paths)

        if prev_sys_imgconf_path is not None:
            kwargs["prev_sys_imgconf"] = prev_sys_imgconf_path

        # Evita collisioni tra current e previous
        if self.prev_app_imgconf_paths:
            kwargs.update({f"prev_{k}": v for k, v in self.prev_app_imgconf_paths.items()})

        super().__init__(**kwargs)

        self.prev_sys_config: dict[str, str] = {}
        self.prev_app_config: dict[str, str] = {}
        self.prev_app_versions_by_name = defaultdict(deque)
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

    
    # Not really needed, so far
    """def _extract_section_len(self, section: dict[str, str]) -> int:
        indices = set()
        pattern = re.compile(rf"{re.escape(self.config.app_name_key)}(\d+)") # `escape` is really needed here to avoid issues with special characters in the key, e.g. if we have "APP_NAME_" as key, the underscore is a special character in regex and it would cause issues if not escaped

        for option in section.keys():
            match = pattern.match(option)
            if match:
                indices.add(match.group(1))

        return len(indices)"""
    
    def _read_taskorder(self, taskorder_path: Path) -> list[dict[str, str]]:
        # taskorder.ini has n sections, while the maximum number possible is N. Therefore we have AP0, ..., AP(n-1). 
        # As for now, the maximum number of AP sections is N=4 (AP0..AP3), but we want to be able to handle more in case we have more in the future, so we need to extract the indices dynamically.
        # The .ini file has a arbitrary number of section, from n = 0 to n = N, where N is unknown a priori. 
        # The minimum number of section is n=1, therefore we can have 0 < n <= N sections, so we always have at least AP0.
        parser = INIParser(taskorder_path)
        has_sections = True
        sections: list[dict[str, str]] = []
        i = 0

        while has_sections:
            try:
                section = parser.get_section(f"{self.config.ap_section_key}{i}") # find APi section, where 0 <= i <= N-1, N is unknown a priori
                sections.append(section)
                i += 1
            except Exception: # catch the custom exception raised by INIParser when section is not found
                has_sections = False
                continue

        return sections
    


    def _has_prev_imgconf(self) -> bool:
        return (
            self.config.has_previous_release()
            and self.prev_sys_imgconf is not None
            and self.prev_sys_imgconf.exists()
            and bool(self.prev_app_imgconf_paths)
            and self.prev_task_order is not None
            and self.prev_task_order.exists()
        )
    
    def scan_files_old(self) -> TaskList:
        if self._has_prev_imgconf():
            #prev_sys_parser = INIParser(self.prev_sys_imgconf)
            #prev_sys_section = prev_sys_parser.get_section(self.config.sys_external_section)
            #self._read_sys_tasks(prev_sys_section, is_prev=True)

            #prev_app_parser = INIParser(self.prev_app_imgconf)
            #prev_app_section = prev_app_parser.get_section(self.config.app_external_section)
            #self._read_app_tasks(prev_app_section, is_prev=True)

            pass

        # load current
        sys_parser = INIParser(self.sys_imgconf)
        sys_section = sys_parser.get_section(self.config.sys_external_section)
        self._read_sys_tasks(sys_section, is_prev=False)

        for path in self.app_imgconf.values():
            app_parser = INIParser(path)
            app_section = app_parser.get_section(self.config.app_external_section)
            self._read_app_task(app_section, is_prev=False)


        return self.tasks
    

    def _flatten_taskorder_names(self, sections: list[dict[str, str]]) -> list[str]:
        ordered_names: list[str] = []

        for sec in sections:
            # Estraggo indici da chiavi NomeTask{i} senza regex
            #indices: list[int] = []
            #prefix = self.config.app_name_key  # es: NomeTask

            #for key in sec.keys():
                #if key.startswith(prefix):
                  # suffix = key[len(prefix):]
                    #if suffix.isdigit():
                     #   indices.append(int(suffix))

            #indices.sort()

            size = len(sec)

            for i in range(1, size + 1):
                raw = sec.get(f"{self.config.app_name_key}{i}", "").strip()
                if raw:
                    ordered_names.append(Path(raw).stem)

        return ordered_names

    def _build_app_catalog(self, app_paths: dict[str, Path]) -> dict[str, list[dict[str, str]]]:
        """
        Catalogo: task_name -> [{type, version}, ...]
        Le entry multiple gestiscono casi di duplicati/reschedule.
        """
        catalog: dict[str, list[dict[str, str]]] = defaultdict(list)

        for _, ini_path in app_paths.items():
            section = INIParser(ini_path).get_section(self.config.app_external_section)

            # Trovo indici presenti tramite NomeTask{i}
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

                if not raw_name:
                    continue
                if type_ and type_.upper() in self.config.excluded_task_types:
                    continue

                name = Path(raw_name).stem
                catalog[name].append(
                    {
                        "type": type_ if type_ else "APP",
                        "version": version if version else "<N/A>",
                    }
                )

        return catalog

    def _read_app_task(self, ordered_names: list[str], catalog: dict[str, list[dict[str, str]]], is_prev: bool):
        """
        Consuma task in ordine taskorder.
        - is_prev=True: salva versioni baseline in coda per nome.
        - is_prev=False: crea Task e confronta con baseline.
        """
        if is_prev and not self._has_prev_imgconf():
            raise ValueError("Previous imgconf not available but trying to read previous app tasks")

        used_index_by_name: dict[str, int] = defaultdict(int)

        for name in ordered_names:
            entries = catalog.get(name, [])
            #entries = catalog[name] if name in catalog else []
            if not entries:
                # Task schedulato ma non trovato nei container
                continue

            idx = used_index_by_name[name]
            if idx >= len(entries):
                # Se il task appare piu volte del numero di entry disponibili, ignoro extra
                continue

            used_index_by_name[name] += 1
            entry = entries[idx]
            curr_version = entry["version"]
            curr_type = entry["type"]

            if is_prev:
                self.prev_app_versions_by_name[name].append(curr_version)
                continue

            if not self._has_prev_imgconf():
                modified = "N/A"
            else:
                if self.prev_app_versions_by_name[name]:
                    prev_version = self.prev_app_versions_by_name[name].popleft()
                    modified = "NO" if prev_version == curr_version else "YES"
                else:
                    modified = "N/A"

            self.tasks.append(
                Task(
                    name=name,
                    type=curr_type,
                    version=curr_version,
                    modified=modified,
                )
            )

    def scan_files(self) -> TaskList:
        # 1) previous baseline
        if self._has_prev_imgconf():
            prev_sys_section = INIParser(self.prev_sys_imgconf).get_section(self.config.sys_external_section)
            self._read_sys_tasks(prev_sys_section, is_prev=True)

            prev_sections = self._read_taskorder(self.prev_task_order)
            prev_ordered_names = self._flatten_taskorder_names(prev_sections)
            prev_catalog = self._build_app_catalog(self.prev_app_imgconf_paths)
            self._read_app_task(prev_ordered_names, prev_catalog, is_prev=True)

        # 2) current
        sys_section = INIParser(self.sys_imgconf).get_section(self.config.sys_external_section)
        self._read_sys_tasks(sys_section, is_prev=False)

        curr_sections = self._read_taskorder(self.task_order)
        curr_ordered_names = self._flatten_taskorder_names(curr_sections)
        curr_catalog = self._build_app_catalog(self.app_imgconf_paths)
        self._read_app_task(curr_ordered_names, curr_catalog, is_prev=False)

        return self.tasks