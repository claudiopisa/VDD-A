# src/ConfigLoader/loaders/task_versioning.py
from __future__ import annotations
from pathlib import Path
from ConfigLoader.config_loader import ConfigLoader

class ConfigLoaderTaskVersioning(ConfigLoader):
    def stream_root(self) -> Path:
        return Path(self.input["stream_root"])

    def nspc_root(self) -> Path:
        return self.stream_root() / self.input["nspc_dir"]

    def imgconf_path(self) -> Path:
        return self.nspc_root() / self.input["imgconf_name"]

    def kernel_mode(self) -> str:
        return self.kernel_mode  # from json, copied into self.__dict__ by your base loader

    def version_regex(self) -> str:
        return self.version_extraction["regex"]

    def system_tasks_spec(self) -> dict:
        return self.system_tasks

    def app_task_spec(self) -> dict:
        return self.application_tasks

    def modified_mode(self) -> str:
        return self.modified["mode"]

    def table_title(self) -> str:
        return self.metadata["title"]

    def table_columns(self) -> list[str]:
        return self.metadata["columns_name"]
