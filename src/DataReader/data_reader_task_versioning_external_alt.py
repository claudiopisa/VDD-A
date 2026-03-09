from collections import defaultdict
from pathlib import Path
from typing import Optional
import re

from configs.task_versioning_config import TaskVersioningConfig
from model.ini.ini_parser import INIParser
from model.task.task import Task
from model.task.task_list import TaskList
from .data_reader import DataReader


class DataReaderTaskVersioningExternal(DataReader):
    def __init__(
        self,
        reader_config: TaskVersioningConfig,
        sys_imgconf_path: str | Path,
        app_imgconf_path: str | Path,
        prev_sys_imgconf_path: Optional[str | Path] = None,
        prev_app_imgconf_path: Optional[str | Path] = None,
    ):
        # `app_imgconf_path` points to taskorder.ini
        if (prev_sys_imgconf_path is None) != (prev_app_imgconf_path is None):
            raise ValueError("Both prev_sys_imgconf_path and prev_app_imgconf_path must be provided together.")

        if prev_sys_imgconf_path is not None and prev_app_imgconf_path is not None:
            super().__init__(
                sys_imgconf_path=sys_imgconf_path,
                app_imgconf_path=app_imgconf_path,
                prev_sys_imgconf_path=prev_sys_imgconf_path,
                prev_app_imgconf_path=prev_app_imgconf_path,
            )
        else:
            super().__init__(
                sys_imgconf_path=sys_imgconf_path,
                app_imgconf_path=app_imgconf_path,
            )

        self.config = reader_config
        self.prev_sys_config: dict[str, str] = {}
        self.prev_app_config: dict[tuple[str, str], str] = {}
        self.tasks: TaskList = TaskList()

    def _extract_indices(self, section: dict[str, str], prefix: str) -> list[int]:
        regex = re.compile(rf"^{re.escape(prefix)}(\\d+)$")
        indices = set()
        for key in section.keys():
            match = regex.match(key)
            if match:
                indices.add(int(match.group(1)))

        return sorted(indices)

    def _iter_task_names_from_taskorder(self, taskorder_path: Path) -> list[str]:
        parser = INIParser(taskorder_path)

        # AP sections are AP0..AP3, but count is unknown a priori.
        ap_sections: list[tuple[int, str]] = []
        for section_name in parser.config.sections():
            match = re.match(r"^AP([0-3])$", section_name)
            if match:
                ap_sections.append((int(match.group(1)), section_name))

        ap_sections.sort(key=lambda item: item[0])

        ordered_names: list[str] = []
        for _, section_name in ap_sections:
            section = parser.get_section(section_name)
            for idx in self._extract_indices(section, self.config.app_name_key):
                name = section.get(f"{self.config.app_name_key}{idx}", "").strip()
                if name:
                    ordered_names.append(name)

        return ordered_names

    def _discover_task_container_paths(self, taskorder_path: Path) -> list[Path]:
        ini_dir = taskorder_path.parent
        out: list[Path] = []

        for candidate in sorted(ini_dir.glob("*.ini")):
            if candidate.name.lower() == taskorder_path.name.lower():
                continue

            parser = INIParser(candidate)
            if not parser.config.has_section("CONFIGURATION"):
                continue

            conf = parser.get_section("CONFIGURATION")
            ini_type = conf.get("TYPE", "").strip().lower()
            if ini_type != "taskcontainer_v2":
                continue

            if not parser.config.has_section(self.config.app_external_section):
                continue

            out.append(candidate)

        return out

    def _load_task_containers(self, taskorder_path: Path) -> dict[str, list[dict[str, str]]]:
        by_name: dict[str, list[dict[str, str]]] = defaultdict(list)

        for container_path in self._discover_task_container_paths(taskorder_path):
            parser = INIParser(container_path)
            section = parser.get_section(self.config.app_external_section)

            for idx in self._extract_indices(section, self.config.app_name_key):
                name = section.get(f"{self.config.app_name_key}{idx}", "").strip()
                type_ = section.get(f"{self.config.app_type_key}{idx}", "").strip()
                version = section.get(f"{self.config.app_version_key}{idx}", "").strip()

                if not name or not type_:
                    continue
                if type_.upper() in self.config.excluded_task_types:
                    continue

                by_name[name].append({"name": name, "type": type_, "version": version})

        return by_name

    def _read_sys_tasks(self, section: dict[str, str], is_prev: bool):
        boot = Path(section.get(self.config.boot_key, "")).stem
        boot_ap = Path(section.get(self.config.boot_ap_key, "")).stem
        loader = Path(section.get(self.config.loader_key, "")).stem
        kernel = Path(section.get(self.config.kernel_key, "")).stem
        kernel_version = section.get(self.config.kernel_version_key, "").strip()

        if is_prev:
            self.prev_sys_config[kernel] = kernel_version
            return

        modified = "N/A"
        if self._has_prev_imgconf():
            modified = "NO" if self.prev_sys_config.get(kernel) == kernel_version else "YES"

        if boot:
            self.tasks.append(Task(name=boot, type="SYSTEM", version="<TODO>"))
        if boot_ap:
            self.tasks.append(Task(name=boot_ap, type="SYSTEM", version="<TODO>"))
        if loader:
            self.tasks.append(Task(name=loader, type="SYSTEM", version="<TODO>"))
        if kernel:
            self.tasks.append(Task(name=kernel, type="SYSTEM", version=kernel_version, modified=modified))

    def _read_app_tasks(self, taskorder_path: Path, is_prev: bool):
        if is_prev and not self._has_prev_imgconf():
            raise ValueError("Previous imgconf not available but trying to read previous app tasks")

        ordered_names = self._iter_task_names_from_taskorder(taskorder_path)
        by_name = self._load_task_containers(taskorder_path)

        if is_prev:
            for entries in by_name.values():
                for entry in entries:
                    self.prev_app_config[(entry["name"], entry["type"])] = entry["version"]
            return

        # Duplicate-aware assignment:
        # if same task name maps to multiple container entries (different types),
        # each repeated scheduling occurrence rotates over available entries.
        next_index_by_name: dict[str, int] = defaultdict(int)

        for name in ordered_names:
            entries = by_name.get(name, [])
            if not entries:
                continue

            pick_index = next_index_by_name[name] % len(entries)
            next_index_by_name[name] += 1
            entry = entries[pick_index]

            key = (entry["name"], entry["type"])
            if not self._has_prev_imgconf():
                modified = "N/A"
            else:
                prev_version = self.prev_app_config.get(key)
                modified = "N/A" if prev_version is None else ("NO" if prev_version == entry["version"] else "YES")

            self.tasks.append(
                Task(
                    name=entry["name"],
                    type=entry["type"],
                    version=entry["version"],
                    modified=modified,
                )
            )

    def _has_prev_imgconf(self) -> bool:
        return (
            self.prev_sys_imgconf is not None
            and self.prev_app_imgconf is not None
            and self.prev_sys_imgconf.exists()
            and self.prev_app_imgconf.exists()
        )

    def scan_files(self) -> TaskList:
        Task.reset_length_cache()

        if self._has_prev_imgconf():
            prev_sys_parser = INIParser(self.prev_sys_imgconf)
            prev_sys_section = prev_sys_parser.get_section(self.config.sys_external_section)
            self._read_sys_tasks(prev_sys_section, is_prev=True)
            self._read_app_tasks(self.prev_app_imgconf, is_prev=True)

        sys_parser = INIParser(self.sys_imgconf)
        sys_section = sys_parser.get_section(self.config.sys_external_section)
        self._read_sys_tasks(sys_section, is_prev=False)

        self._read_app_tasks(self.app_imgconf, is_prev=False)

        return self.tasks
