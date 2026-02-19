from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from .data_reader import DataReader


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
    
    def __init__(self, imgconf_path: str | Path, previous_imgconf_path: str | Path | None = None):
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
        
        # Access files (max 2: current and optional previous)
        self.imgconf_path = self.data_paths[0]
        self.previous_imgconf_path = self.data_paths[1] if len(self.data_paths) > 1 else None
        
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
    
    def _load_prev_config(self, prev_imgconf_path: Path) -> dict[str, str]:
        parser = self._init_parser(prev_imgconf_path)

        if "Settings" not in parser:
            raise ValueError("Missing [Settings] section in previous Imgconf.ini")
        
        settings = parser["Settings"]
        out: dict[str, str] = {}

         # Kernel
        if "RelKernel" in settings:
            out["KERNEL"] = settings.get("RelKernel", "").strip()

        # Application tasks
        try:
            num_tasks = int(settings.get("NumTask").strip())
        except ValueError:
            num_tasks = None

        #if num_task is none, then cannot continue loading tasks
        if num_tasks is None:
            raise ValueError("Invalid NumTask value in previous Imgconf.ini")


        for i in range(1, num_tasks + 1):
            type_ = settings.get(f"TipoTask{i}", "").strip()
            if type_ and type_.upper() not in ("NO_SCHED", "RBC"):
                name = Path(settings.get(f"V1_FileTask{i}", "").strip()).stem
                version = settings.get(f"RelTask{i}", "").strip()
                if name:
                    out[name] = version

        return out

    def scan_files(self) -> TaskList:
        
        if "Settings" not in self._parser:
            raise ValueError("Missing [Settings] section in Imgconf.ini")

        #reset length cache before reading tasks, to ensure that the max length is calculated correctly based on the current set of tasks being read, without being influenced by any previous reads or Task instances that may have been created.
        Task.reset_length_cache()

        #load the entire setting section
        settings = self._parser["Settings"]
        #tasks: TaskList = TaskList()

        if self.previous_imgconf_path:
            prev_config = self._load_prev_config(self.previous_imgconf_path)


        # System tasks, such as BOOT, BOOTAP, Loader, Kernel, are in the [Settings] section with chiavi come FileBootVer, FileBootAPVer, FileLoaderVer, FileKernelVer
        # BOOT
        if "FileBoot" in settings:
            name = Path(settings.get("FileBoot", "").strip()).stem
            self.tasks.append(Task(name="BOOT", type="SYSTEM", version="<TODO>"))

        # BOOTAP
        if "FileBootAPs" in settings:
            name = Path(settings.get("FileBootAPs", "").strip()).stem
            self.tasks.append(Task(name="BOOTAP", type="SYSTEM", version="<TODO>"))

        # Loader (per ora just mark as TODO, file extraction can be added later)
        if "V1_FileLoader"in settings:
            name = Path(settings.get("V1_FileLoader", "").strip()).stem
            self.tasks.append(Task(name="Loader", type="SYSTEM", version="<TODO>"))

        # Kernel
        if "RelKernel" in settings:
            name = Path(settings.get("RelKernel", "").strip()).stem
            version = settings.get("RelKernel", "").strip()
            self.tasks.append(Task(name="KERNEL", 
                                   type="SYSTEM", 
                                   version=version, 
                                   modified=("NO" if (self.previous_imgconf_path and prev_config.get("KERNEL") == version) 
                                              else ("YES" if self.previous_imgconf_path 
                                                    else "N/A"))))
  
            
        # Application tasks
        try:
            num_tasks = int(settings.get("NumTask", "0").strip())
        except ValueError:
            num_tasks = None

        #if num_task is none, then cannot continue loading tasks
        if num_tasks is None:
            raise ValueError("Invalid NumTask value in Imgconf.ini")

        for i in range(1, num_tasks + 1):
            type = settings.get(f"TipoTask{i}", "").strip()

            # if task is not type NO_SCHED or RBC, then read its version
            if type and type.upper() not in ("NO_SCHED", "RBC"):
                version = settings.get(f"RelTask{i}", "").strip()
                name = Path(settings.get(f"V1_FileTask{i}", "").strip()).stem

                self.tasks.append(Task(
                                        name=name, 
                                        type=type, 
                                        version=version, 
                                        modified=("NO" if (self.previous_imgconf_path and prev_config.get(name) == version) 
                                                  else ("YES" if self.previous_imgconf_path 
                                                        else "N/A"))))

        return self.tasks

