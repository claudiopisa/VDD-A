from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig

from .data_reader import DataReader

import re


@dataclass
class Task:
    name: str
    type: str
    version: str
    modified: str = "N/A"  # per ora non hai baseline precedente

    # Static attribute. Keeps track of the max length of each field across all Task instances, used for formatting the output in a clean way.
    _length_cache: ClassVar[dict[str, int]] = {
        "name": len("NAME"),
        "type": len("TYPE"),
        "version": len("VERSION"),
        "modified": len("MODIFIED"),
    }

    # Special method called automatically after the dataclass __init__ method, used to update
    # the max length of each field in the _length_cache dictionary every time a new Task
    # instance is created.
    def __post_init__(self):
        """Aggiorna i max ogni volta che un Task viene creato."""
        for key, current_max in Task._length_cache.items():
            Task._length_cache[key] = max(current_max, len(str(getattr(self, key))))

    @classmethod
    def reset_length_cache(cls) -> None:
        cls._length_cache = {
            "name": len("NAME"),
            "type": len("TYPE"),
            "version": len("VERSION"),
            "modified": len("MODIFIED"),
        }

    @classmethod
    def format_row(cls, name: str, type_: str, version: str, modified: str) -> str:
        gap = "  "
        return (
            f"{name:<{cls._length_cache['name']}}"
            f"{gap}{type_:<{cls._length_cache['type']}}"
            f"{gap}{version:<{cls._length_cache['version']}}"
            f"{gap}{modified:<{cls._length_cache['modified']}}"
        )

    @classmethod
    def format_header_row(cls, name: str, type_: str, version: str, modified: str) -> str:
        gap = "  "
        return (
            f"{name:^{cls._length_cache['name']}}"
            f"{gap}{type_:^{cls._length_cache['type']}}"
            f"{gap}{version:^{cls._length_cache['version']}}"
            f"{gap}{modified:^{cls._length_cache['modified']}}"
        )

    def __repr__(self):
        return Task.format_row(self.name, self.type, self.version, self.modified)
    
class TaskList(list[Task]): #TaskList composizione con Task.
    
    def __repr__(self):
        out = "TaskList:\n"
        out += Task.format_header_row("NAME", "TYPE", "VERSION", "MODIFIED") + "\n"
        for task in self:
            out += f"{task}\n"

        return out
    
class DataReaderTaskVersioning(DataReader):
    
    def __init__(self, imgconf_path: str | Path, previous_imgconf_path: str | Path | None = None, kernel_mode: str = "internal"):
        """
        Initialize with current imgconf and optional previous version.
        
        Args:
            imgconf_path: Current imgconf file (mandatory)
            previous_imgconf_path: Previous imgconf file for comparison (optional)
        """
        # Build paths list for variadic parent
        paths = [imgconf_path] # temp list
        if previous_imgconf_path: # check if previous imgconf is passed 
            paths.append(previous_imgconf_path)
        
        super().__init__(*paths) # paths are validated by parent constructor and creates an attribute lists of files
        
        self.config = TaskVersioningDefaultConfig()
        self.kernel_mode = kernel_mode

        # Access files (max 2: current and optional previous)
        self.imgconf_path = self.data_paths[0]
        self.previous_imgconf_path = self.data_paths[1] if len(self.data_paths) > 1 else None
        self.prev_config = self._load_prev_config(self.previous_imgconf_path) if self.previous_imgconf_path else None

        self.stream_root = self._get_stream_root(self.imgconf_path)
        self.prev_stream_root = self._get_stream_root(self.previous_imgconf_path) if self.previous_imgconf_path else None

        self.app_component = None
        self.kernel_component = None
        self.app_config_dir = None
        self.prev_app_config_dir = None

        if self.kernel_mode == "external":
            if isinstance(self.config.roots.external, (tuple, list)) and len(self.config.roots.external) >= 2:
                self.app_component = self.config.roots.external[0]
                self.kernel_component = self.config.roots.external[1]

            if self.stream_root and self.app_component:
                self.app_config_dir = self.stream_root / self.app_component / "Configurazioni"

            if self.prev_stream_root and self.app_component:
                self.prev_app_config_dir = self.prev_stream_root / self.app_component / "Configurazioni"

        self._parser = self._init_parser(self.imgconf_path)

        self.tasks: TaskList = TaskList()

        
    def _init_parser(self, imgconf_path: Path) -> ConfigParser:
        parser = ConfigParser(
            interpolation=None,
            comment_prefixes=(";", "#", "//"),
            inline_comment_prefixes=(";", "#", "//"),
            delimiters=("=",),
            strict=False,
        )
        parser.optionxform = str  # preserva case
        
        with imgconf_path.open("r", encoding="utf-8", errors="ignore") as file:
            parser.read_file(file)

        return parser

    def _get_stream_root(self, imgconf_path: Path | None) -> Path | None:
        if imgconf_path is None:
            return None

        return imgconf_path.parents[1] if len(imgconf_path.parents) >= 2 else None
    
    def _container_indices(self, section) -> list[int]:
        """
        Caso kernel esterno i file .ini non hanno num task
        Estrae gli indici i presenti per chiavi tipo NomeTask{i}.
        Esempio: NomeTask1, NomeTask2 -> [1,2]
        """
        idx = set()
        #rx = re.compile(r"^NomeTask(\d+)$")
        rx = re.compile(rf"^{self.config.app_task.name}(\d+)$")
        for k in section.keys():
            m = rx.match(k)
            if m:
                idx.add(int(m.group(1)))

        return sorted(idx)
    
    def _load_prev_config(self, prev_imgconf_path: Path) -> dict[str, str]:
        #parser = self._init_parser(prev_imgconf_path)

        #if self.kernel_mode == "internal":
            #section_name = self.config.sections.internal
        #else:
            #section_name = self.config.sections.external 

        #if section_name not in parser:
            #raise ValueError(f"Missing [{section_name}] section in previous Imgconf.ini")
        
        #section = parser[section_name]
        out: dict[str, str] = {}

        

        if self.kernel_mode == "internal":
            parser = self._init_parser(prev_imgconf_path)
            section = parser[self.config.sections.settings]

            if self.config.sys_task.kernel_version in section:
                out["KERNEL"] = section.get(self.config.sys_task.kernel_version, "").strip()
                
            try:
                num_tasks = int(section.get(self.config.num_tasks, "").strip())
            except ValueError:
                num_tasks = None

            if num_tasks is None:
                raise ValueError("Invalid NumTask value in previous Imgconf.ini")

            for i in range(1, num_tasks + 1):
                type_ = section.get(f"{self.config.app_task.type}{i}", "").strip()
                if type_ and type_.upper() not in self.config.rules.exclusion.task_type:
                    name = Path(section.get(f"{self.config.app_task.path}{i}", "").strip()).stem
                    version = section.get(f"{self.config.app_task.version}{i}", "").strip()
                    if name:
                        out[name] = version
        else:
            # External kernel mode: load from previous kernel Imgconf + app config files
            if prev_imgconf_path:
                kernel_parser = self._init_parser(prev_imgconf_path)
                kernel_section = kernel_parser[self.config.sections.settings]
                if self.config.sys_task.kernel_version in kernel_section:
                    out["KERNEL"] = kernel_section.get(self.config.sys_task.kernel_version, "").strip()

            if not self.prev_app_config_dir:
                return out

            conf_files = self.config.rules.inclusion.external
            for conf_file in conf_files:
                conf_path = self.prev_app_config_dir / conf_file
                if not conf_path.exists():
                    continue

                ext_parser = self._init_parser(conf_path)
                section = ext_parser[self.config.sections.container]

                for i in self._container_indices(section):
                    name = section.get(f"{self.config.app_task.name}{i}", "").strip()
                    version = section.get(f"{self.config.app_task.version}{i}", "").strip()
                    if name:
                        out[name] = version

        return out
    
    def _read_sys_tasks(self, section) -> None:
        # System tasks, such as BOOT, BOOTAP, Loader, Kernel, are in the [Settings] section with chiavi come FileBootVer, FileBootAPVer, FileLoaderVer, FileKernelVer
        # BOOT
        if self.config.sys_task.boot in section:
            name = Path(section.get(self.config.sys_task.boot, "").strip()).stem
            self.tasks.append(Task(name="BOOT", type="SYSTEM", version="<TODO>"))

        # BOOTAP
        if self.config.sys_task.boot_ap in section:
            name = Path(section.get(self.config.sys_task.boot_ap, "").strip()).stem
            self.tasks.append(Task(name="BOOTAP", type="SYSTEM", version="<TODO>"))

        # Loader (per ora just mark as TODO, file extraction can be added later)
        if self.config.sys_task.loader in section:
            name = Path(section.get(self.config.sys_task.loader, "").strip()).stem
            self.tasks.append(Task(name="Loader", type="SYSTEM", version="<TODO>"))

        # Kernel
        if self.config.sys_task.kernel_version in section:
            version = section.get(self.config.sys_task.kernel_version, "").strip()
            self.tasks.append(Task(name="KERNEL", 
                                   type="SYSTEM", 
                                   version=version, 
                                   modified=("NO" if (self.previous_imgconf_path and self.prev_config.get("KERNEL") == version) 
                                              else ("YES" if self.previous_imgconf_path 
                                                    else "N/A"))))

    def scan_files(self) -> TaskList:
        if self.kernel_mode == "internal":
            parser = self._init_parser(self.imgconf_path)
            section = parser[self.config.sections.settings]
            self._read_sys_tasks(section)

            # Application tasks
            try:
                num_tasks = int(section.get(self.config.num_tasks, "0").strip())
            except ValueError:
                num_tasks = None

            if num_tasks is None:
                raise ValueError("Invalid NumTask value in Imgconf.ini")

            for i in range(1, num_tasks + 1):
                type_ = section.get(f"{self.config.app_task.type}{i}", "").strip()
                if type_ and type_.upper() not in self.config.rules.exclusion.task_type:
                    version = section.get(f"{self.config.app_task.version}{i}", "").strip()
                    name = Path(section.get(f"{self.config.app_task.path}{i}", "").strip()).stem

                    self.tasks.append(Task(
                                            name=name, 
                                            type=type_, 
                                            version=version, 
                                            modified=("NO" if (self.previous_imgconf_path and self.prev_config.get(name) == version) 
                                                      else ("YES" if self.previous_imgconf_path 
                                                            else "N/A"))))
            

        else: #kernel is external
            #kernel_parser = self._init_parser(self.imgconf_path)
            #kernel_section = kernel_parser[self.config.sections.settings]
            #self._read_sys_tasks(kernel_section)

            if not self.app_config_dir:
                print("App config directory not found, cannot read application tasks.")
                return self.tasks

            conf_files = self.config.rules.inclusion.external
            for conf_file in conf_files:
                conf_path = self.app_config_dir / conf_file
                if not conf_path.exists():
                    continue

                ext_parser = self._init_parser(conf_path)
                section = ext_parser[self.config.sections.container]

                for i in self._container_indices(section):
                    name = section.get(f"{self.config.app_task.name}{i}", "").strip()
                    type_ = section.get(f"{self.config.app_task.type}{i}", "").strip()
                    version = section.get(f"{self.config.app_task.version}{i}", "").strip()
                    if name:
                        self.tasks.append(Task(
                                            name=name, 
                                            type=type_ or "SYSTEM", 
                                            version=version, 
                                            modified=("NO" if (self.previous_imgconf_path and self.prev_config.get(name) == version) 
                                                      else ("YES" if self.previous_imgconf_path 
                                                            else "N/A"))))
        return self.tasks

    def scan_files_old(self) -> TaskList:
        
        if "Settings" not in self._parser:
            raise ValueError("Missing [Settings] section in Imgconf.ini")

        #reset length cache before reading tasks, to ensure that the max length is calculated correctly based on the current set of tasks being read, without being influenced by any previous reads or Task instances that may have been created.
        Task.reset_length_cache()

        #load the entire setting section
        #settings = self._parser["Settings"]
        if self.kernel_mode == "internal":
            parser = self._init_parser(self.imgconf_path)
            section = parser[self.config.sections.internal]
        else:
            section = self._parser[self.config.sections.external]

        #tasks: TaskList = TaskList()

        if self.previous_imgconf_path:
            prev_config = self._load_prev_config(self.previous_imgconf_path)


        # System tasks, such as BOOT, BOOTAP, Loader, Kernel, are in the [Settings] section with chiavi come FileBootVer, FileBootAPVer, FileLoaderVer, FileKernelVer
        # BOOT
        if "FileBoot" in section:
            name = Path(section.get("FileBoot", "").strip()).stem
            self.tasks.append(Task(name="BOOT", type="SYSTEM", version="<TODO>"))

        # BOOTAP
        if "FileBootAPs" in section:
            name = Path(section.get("FileBootAPs", "").strip()).stem
            self.tasks.append(Task(name="BOOTAP", type="SYSTEM", version="<TODO>"))

        # Loader (per ora just mark as TODO, file extraction can be added later)
        if "V1_FileLoader"in section:
            name = Path(section.get("V1_FileLoader", "").strip()).stem
            self.tasks.append(Task(name="Loader", type="SYSTEM", version="<TODO>"))

        # Kernel
        if "RelKernel" in section:
            name = Path(section.get("RelKernel", "").strip()).stem
            version = section.get("RelKernel", "").strip()
            self.tasks.append(Task(name="KERNEL", 
                                   type="SYSTEM", 
                                   version=version, 
                                   modified=("NO" if (self.previous_imgconf_path and self.prev_config.get("KERNEL") == version) 
                                              else ("YES" if self.previous_imgconf_path 
                                                    else "N/A"))))
  
            
        # Application tasks
        try:
            num_tasks = int(section.get("NumTask", "0").strip())
        except ValueError:
            num_tasks = None

        #if num_task is none, then cannot continue loading tasks
        if num_tasks is None:
            raise ValueError("Invalid NumTask value in Imgconf.ini")

        for i in range(1, num_tasks + 1):
            type = section.get(f"TipoTask{i}", "").strip()

            # if task is not type NO_SCHED or RBC, then read its version
            if type and type.upper() not in ("NO_SCHED", "RBC"):
                version = section.get(f"RelTask{i}", "").strip()
                name = Path(section.get(f"V1_FileTask{i}", "").strip()).stem

                self.tasks.append(Task(
                                        name=name, 
                                        type=type, 
                                        version=version, 
                                        modified=("NO" if (self.previous_imgconf_path and self.prev_config.get(name) == version) 
                                                  else ("YES" if self.previous_imgconf_path 
                                                        else "N/A"))))

        return self.tasks

