from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig

from .data_reader import DataReader

import re

from model.task import Task
from model.task_list import TaskList
    
@dataclass
class Sources:
    # "internal" | "external"
    mode: str

    # sys ini (internal: NSPC/Imgconf.ini; external: NS_KERNEL/Imgconf.ini)
    sys_current: Path
    sys_previous: Optional[Path] = None

    # app ini (internal: {} ; external: {"ixl": path, "srlw": path, ...})
    app_current: dict[str, Path] = None
    app_previous: Optional[dict[str, Path]] = None

    def __post_init__(self):
        if self.app_current is None:
            object.__setattr__(self, "app_current", {})

class DataReaderTaskVersioning(DataReader):
    #Use cases:
    # Kernel is internal: we have max 2 ini files to read, current and optional previous, the former in the NSPC dir, the latter in the previous stream root if available. Both contain a [Settings] section with BOOT, BOOTAP, Loader, Kernel and application tasks with their type and version. We compare BOOT, BOOTAP, Loader, Kernel and application tasks versions between current and previous ini to determine if they are modified or not.
    # Kernel is external: we have 1 ini file for the sys tasks and N ini files (usually 2, ixl.ini and srlw.ini) for app tasks (current stream), and optionally the same for the previous stream, resulting in a max of 2N app inis + 2 sys ini (current + previous). The sys ini contains BOOT, BOOTAP, Loader, Kernel with their version, while the app ini(s) contain application tasks with their type and version. We compare BOOT, BOOTAP, Loader, Kernel versions from the sys ini and application tasks versions from the app ini(s) between current and previous stream to determine if they are modified or not.
    
    def __init__(self, sources: Sources):
        self.sources = sources

        # fils needed to be validated and passed to parent constructor for path checks and attribute creation
        paths: list[Path] = [sources.sys_current]
        if sources.sys_previous:
            paths.append(sources.sys_previous)

        paths.extend(sources.app_current.values())
        if sources.app_previous:
            paths.extend(sources.app_previous.values())

        super().__init__(*paths)

        self.config = TaskVersioningDefaultConfig()
        self.prev_config: dict[str, str] = self._load_prev_config() # uses self.sources to load properly 
        self.tasks: TaskList = TaskList()

    

    @classmethod
    def from_internal(cls, current_imgconf: Path, previous_imgconf: Optional[Path] = None) -> "DataReaderTaskVersioning":

        prev = previous_imgconf if (previous_imgconf and previous_imgconf.exists()) else None
        
        sources = Sources(
            mode="internal",
            sys_current=current_imgconf,
            sys_previous=prev,
            app_current={},
            app_previous=None
        )

        return cls(sources)

    @classmethod
    def from_external(
        cls,
        stream_root: Path,
        previous_stream_root: Optional[Path] = None,
        sys_conf: Path = Path("NS_KERNEL") / "Imgconf.ini",
        app_conf: Path = Path("NSPC") / "Configurazioni",
        app_files: tuple[str, ...] = ("ixl.ini", "srlw.ini")
    ) -> "DataReaderTaskVersioning":
        
        sys_current = stream_root / sys_conf
        sys_previous = (previous_stream_root / sys_conf) if previous_stream_root else None
        if sys_previous and not sys_previous.exists():
            sys_previous = None
        
        # App inis: only the known ones (ixl.ini, srlw.ini)
        app_dir = stream_root / app_conf
        #app_current = {p.stem: p for p in app_dir if p.name in ("ixl.ini", "srlw.ini")}
        #app_current = {p.stem: p for p in app_dir.glob("*.ini") if p.name in ("ixl.ini", "srlw.ini")}
        app_current: dict[str, Path] = {}
        for fname in app_files:
            p = app_dir / fname
            if p.exists():
                app_current[p.stem] = p

        # previous app: match by stem name
        app_previous: dict[str, Path] = {} # stores the paths of previous app confs, if available, keyed by their stem (e.g. ixl, srlw)
        if previous_stream_root:
            prev_app_dir = previous_stream_root / app_conf
            for name in app_current.keys():
                candidate = prev_app_dir / f"{name}.ini"
                if candidate.exists():
                    app_previous[name] = candidate
        
        sources = Sources(
            mode="external",
            sys_current=sys_current,
            sys_previous=sys_previous,
            app_current=app_current,
            app_previous=app_previous if app_previous else None
        )

        return cls(sources)
    
    #def __init__(self, imgconf_path: str | Path, previous_imgconf_path: str | Path | None = None, kernel_mode: str = "internal"):
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
    
    def _load_prev_config_old(self, prev_imgconf_path: Path) -> dict[str, str]:
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
    
    def _load_prev_config(self) -> dict[str, str]:
       
        out: dict[str, str] = {}

        # No previous sys ini => no baseline at all => return empty
        if not self.sources.sys_previous:
            return out

        # -----------------------------
        # Previous system ini (Settings)
        # -----------------------------
        prev_sys_parser = self._init_parser(self.sources.sys_previous)
        if self.config.sections.settings in prev_sys_parser:
            prev_settings = prev_sys_parser[self.config.sections.settings]

            # Kernel version
            if self.config.sys_task.kernel_version in prev_settings:
                out["KERNEL"] = prev_settings.get(self.config.sys_task.kernel_version, "").strip()

            # Internal mode: app tasks are also in Settings
            if self.sources.mode == "internal":
                try:
                    num = int(prev_settings.get(self.config.num_tasks, "0").strip())
                except ValueError:
                    num = 0

                for i in range(1, num + 1):
                    t = prev_settings.get(f"{self.config.app_task.type}{i}", "").strip()
                    if t and t.upper() not in self.config.rules.exclusion.task_type:
                        # NOTE: se hai backslash nei path, qui in futuro meglio usare PureWindowsPath
                        name = Path(prev_settings.get(f"{self.config.app_task.path}{i}", "").strip()).stem
                        ver = prev_settings.get(f"{self.config.app_task.version}{i}", "").strip()
                        if name:
                            out[name] = ver

        # -----------------------------
        # External mode: previous app containers
        # -----------------------------
        if self.sources.mode == "external" and self.sources.app_previous:
            for stem, prev_ini in self.sources.app_previous.items():
                prev_app_parser = self._init_parser(prev_ini)
                if self.config.sections.container not in prev_app_parser:
                    continue

                c = prev_app_parser[self.config.sections.container]
                for i in self._container_indices(c):
                    name = c.get(f"{self.config.app_task.name}{i}", "").strip()
                    ver = c.get(f"{self.config.app_task.version}{i}", "").strip()
                    if name:
                        out[name] = ver

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
        # 1) Sys tasks
        sys_parser = self._init_parser(self.sources.sys_current)
        if self.config.sections.settings in sys_parser:
            self._read_sys_tasks(sys_parser[self.config.sections.settings])


        # 2) App tasks
        if not self.sources.app_current: 
            #Internal: app tasks are in sys_current [Settings]
            self._read_app_tasks_internal(sys_parser[self.config.sections.settings])
        else:
            #External: app tasks are in separate ini(s)
            for conf_path in self.sources.app_current.values():
                app_parser = self._init_parser(conf_path)
                if self.config.sections.container in app_parser:
                    self._read_app_tasks_external(app_parser[self.config.sections.container])

    def scan_files_temp(self) -> TaskList:
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

