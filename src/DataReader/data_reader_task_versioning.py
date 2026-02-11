from configparser import ConfigParser
from pathlib import Path

class TaskVersion:
    def __init__(self, name, type_, version, modified="N/A"):
        self.name = name
        self.type = type_
        self.version = version
        self.modified = modified


class DataReaderTaskVersioning:
    def __init__(self, imgconf_path: Path):
        self.imgconf_path = imgconf_path

    def read_tasks(self) -> list[TaskVersion]:
        if not self.imgconf_path.exists():
            raise FileNotFoundError(f"Imgconf.ini not found: {self.imgconf_path}")

        parser = ConfigParser()
        parser.read(self.imgconf_path, encoding="utf-8")

        tasks = []

        for section in parser.sections():
            name = parser.get(section, "Name", fallback=None)
            type_ = parser.get(section, "Type", fallback=None)
            version = parser.get(section, "Version", fallback=None)

            if not name or not type_ or not version:
                continue  # sezione incompleta → skip

            tasks.append(TaskVersion(
                name=name,
                type_=type_,
                version=version,
                modified="N/A"   # per ora
            ))

        return tasks
