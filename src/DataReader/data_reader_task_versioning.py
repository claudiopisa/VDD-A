from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


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
    
class DataReaderTaskVersioning:
    def __init__(self, imgconf_path: str | Path):
        self.imgconf_path = Path(imgconf_path) if isinstance(imgconf_path, str) else imgconf_path
        if not self.imgconf_path.exists():
            raise FileNotFoundError(f"Imgconf.ini not found: {self.imgconf_path}")
        
        self._parser = self._init_parser()

    def _init_parser(self) -> ConfigParser:
        parser = ConfigParser(
            interpolation=None,
            comment_prefixes=(";", "#", "//"),
            inline_comment_prefixes=(";", "#", "//"),
            delimiters=("=",),
            strict=False,
        )
        parser.optionxform = str  # preserva case

        with self.imgconf_path.open("r", encoding="utf-8", errors="ignore") as file:
            parser.read_file(file)

        return parser
    
    def read_tasks(self) -> TaskList:
        if "Settings" not in self._parser:
            raise ValueError("Missing [Settings] section in Imgconf.ini")

        #reset length cache before reading tasks, to ensure that the max length is calculated correctly based on the current set of tasks being read, without being influenced by any previous reads or Task instances that may have been created.
        Task.reset_length_cache()

        #load the entire setting section
        settings = self._parser["Settings"]
        tasks: TaskList = TaskList()

        # System tasks, such as BOOT, BOOTAP, Loader, Kernel, are in the [Settings] section with chiavi come FileBootVer, FileBootAPVer, FileLoaderVer, FileKernelVer
        # BOOT
        if "FileBoot" in settings:
            name = Path(settings.get("FileBoot", "").strip()).stem
            tasks.append(Task(name="BOOT", type="SYSTEM", version="<TODO >"))

        # BOOTAP
        if "FileBootAPs" in settings:
            name = Path(settings.get("FileBootAPs", "").strip()).stem
            tasks.append(Task(name="BOOTAP", type="SYSTEM", version="<TODO>"))

        # Loader (per ora just mark as TODO, file extraction can be added later)
        if "V1_FileLoader"in settings:
            name = Path(settings.get("V1_FileLoader", "").strip()).stem
            tasks.append(Task(name="Loader", type="SYSTEM", version="<TODO>"))

        # Kernel
        if "RelKernel" in settings:
            name = Path(settings.get("RelKernel", "").strip()).stem
            version = settings.get("RelKernel", "").strip()
            tasks.append(Task(name="KERNEL", type="SYSTEM", version=version))
  
            
        # Application tasks
        try:
            num_tasks = int(settings.get("NumTask", "0").strip() or "0")
        except ValueError:
            num_tasks = 0

        for i in range(1, num_tasks + 1):
            type = settings.get(f"TipoTask{i}", "").strip()

            # if task is not type NO_SCHED or RBC, then read its version
            if type and type.upper() not in ("NO_SCHED", "RBC"):
                version = settings.get(f"RelTask{i}", "").strip()
                name = Path(settings.get(f"V1_FileTask{i}", "").strip()).stem

                tasks.append(Task(name=name, type=type, version=version, modified="N/A"))

        return tasks

