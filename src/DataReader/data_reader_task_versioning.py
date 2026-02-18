from configparser import ConfigParser
from pathlib import Path

class TaskVersion:
    def __init__(self, name, type_, version, modified="N/A"):
        self.name = name
        self.type = type_
        self.version = version
        self.modified = modified

    def __repr__(self):
        return (
            f"TaskVersion(name={self.name!r}, "
            f"type={self.type!r}, version={self.version!r}, "
            f"modified={self.modified!r})"
        )


class DataReaderTaskVersioning:
    def __init__(self, imgconf_path: Path):
        self.imgconf_path = imgconf_path

    def read_tasks(self) -> list[TaskVersion]:
        if not self.imgconf_path.exists():
            raise FileNotFoundError(f"Imgconf.ini not found: {self.imgconf_path}")

        parser = ConfigParser(
            comment_prefixes=(";", "#", "//"),
            inline_comment_prefixes=(";", "#", "//"),
        )
        parser.read(self.imgconf_path, encoding="ANSI")

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

    def read_tasks_imgconf(self) -> list[TaskVersion]:
        if not self.imgconf_path.exists():
            raise FileNotFoundError(f"Imgconf.ini not found: {self.imgconf_path}")

        parser = ConfigParser(
            comment_prefixes=(";", "#", "//"),
            inline_comment_prefixes=(";", "#", "//"),
        )
        parser.read(self.imgconf_path, encoding="ANSI")

        tasks: list[TaskVersion] = []

        for section in parser.sections():
            section_data = parser[section]

            # Match keys like TipoTask1, RelTask1, V1_FileTask1, etc.
            for key in section_data:
                if not key.lower().startswith("tipotask"):
                    continue

                suffix = key[len("tipotask"):]
                type_ = section_data.get(f"TipoTask{suffix}")
                version = section_data.get(f"RelTask{suffix}")
                name = (
                    section_data.get(f"V1_FileTask{suffix}")
                    or section_data.get(f"V2_FileTask{suffix}")
                    or f"{section}:Task{suffix}"
                )

                if not type_ or not version:
                    continue

                tasks.append(TaskVersion(
                    name=name,
                    type_=type_,
                    version=version,
                    modified="N/A",
                ))

        return tasks
