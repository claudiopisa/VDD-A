from configparser import ConfigParser
from pathlib import Path

from .data_reader_task_versioning__ import TaskVersion


class DataReaderTaskUnified:
    def __init__(self, imgconf_path: Path):
        self.imgconf_path = imgconf_path

    def _load_parser(self) -> ConfigParser:
        if not self.imgconf_path.exists():
            raise FileNotFoundError(f"Imgconf.ini not found: {self.imgconf_path}")

        parser = ConfigParser(
            interpolation=None,
            comment_prefixes=(";", "#", "//"),
            inline_comment_prefixes=(";", "#", "//"),
            delimiters=("=",),
            strict=False,
        )
        parser.optionxform = str

        with self.imgconf_path.open("r", encoding="utf-8", errors="ignore") as file:
            parser.read_file(file)

        return parser

    def read_tasks(self) -> list[TaskVersion]:
        parser = self._load_parser()

        if "Settings" not in parser:
            raise ValueError("Missing [Settings] section in Imgconf.ini")

        settings = parser["Settings"]
        tasks: list[TaskVersion] = []

        # --- System tasks ---
        # BOOT
        if "FileBootVer" in settings:
            boot_ver = settings.get("FileBootVer", "").strip()
            if boot_ver:
                tasks.append(
                    TaskVersion(name="BOOT", type_="SYSTEM", version=boot_ver, modified="N/A")
                )

        # BOOTAP
        if "FileBootAPVer" in settings:
            bootap_ver = settings.get("FileBootAPVer", "").strip()
            if bootap_ver:
                tasks.append(
                    TaskVersion(name="BOOTAP", type_="SYSTEM", version=bootap_ver, modified="N/A")
                )

        # Loader (for now just mark as TODO, file extraction can be added later)
        if "FileLoaderVer" in settings:
            loader_file = settings.get("FileLoaderVer", "").strip()
            if loader_file:
                tasks.append(
                    TaskVersion(
                        name="Loader", type_="SYSTEM", version="<TODO extract from file>", modified="N/A"
                    )
                )

        # Kernel
        if "RelKernel" in settings:
            kernel_ver = settings.get("RelKernel", "").strip()
            if kernel_ver:
                tasks.append(
                    TaskVersion(name="Kernel", type_="SYSTEM", version=kernel_ver, modified="N/A")
                )

        # --- Application tasks ---
        try:
            num_tasks = int(settings.get("NumTask", "0").strip() or "0")
        except ValueError:
            num_tasks = 0

        for index in range(1, num_tasks + 1):
            type_ = settings.get(f"TipoTask{index}", "").strip()
            if not type_:
                continue

            if type_.upper() in {"NO_SCHED", "RBC"}:
                continue

            version = settings.get(f"RelTask{index}", "").strip()
            if not version:
                continue

            v1_file = settings.get(f"V1_FileTask{index}", "").strip()
            task_name = Path(v1_file.replace("\\", "/")).stem if v1_file else f"Task{index}"

            tasks.append(
                TaskVersion(
                    name=task_name,
                    type_=type_,
                    version=version,
                    modified="N/A",
                )
            )

        return tasks
