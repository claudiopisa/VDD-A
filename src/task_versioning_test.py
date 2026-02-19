from pathlib import Path

from DataReader.data_reader_task_versioning import DataReaderTaskVersioning
from configs.core_config import CoreConfig
from configs.task_versioning_config import TaskVersioningConfig

# Core config
core_conf = CoreConfig(user_config_path="config/core_config.json")

# Task versioning config
tv_conf = TaskVersioningConfig(user_config_path="config/task_versioning.json")

workspace = core_conf.stream_root_as_path
print(f"Workspace: {workspace}")

# Pick components roots based on kernel mode
if core_conf.is_kernel_internal:
    print("Kernel mode is internal.")
    components = tv_conf.internal_roots
else:
    print("Kernel mode is external.")
    components = tv_conf.external_roots

# Normalize to an iterable
components_to_scan = (components,) if isinstance(components, str) else tuple(components)
print(f"Components to scan: {components_to_scan}")

# Optional previous stream (baseline) support
prev_workspace = None
if tv_conf.has_previous_release and tv_conf.previous_release_root:
    prev_workspace = tv_conf.previous_release_root_as_path
    if not prev_workspace.exists():
        prev_workspace = None

if prev_workspace:
    print(f"Previous stream root detected: {prev_workspace}")
else:
    print("No previous stream root (baseline) available -> Modified will be N/A")

for comp in components_to_scan:
    ini = workspace / comp / core_conf.image_config_name
    print(f"\nLooking for Imgconf.ini at: {ini}")

    prev_ini = None
    if prev_workspace:
        candidate = prev_workspace / comp / core_conf.image_config_name
        if candidate.exists():
            prev_ini = candidate
            print(f"Baseline Imgconf.ini: {prev_ini}")
        else:
            print(f"Baseline Imgconf.ini not found for {comp} -> Modified will be N/A")

    reader = DataReaderTaskVersioning(ini, previous_imgconf_path=prev_ini)
    tasks = reader.scan_files()
    print(tasks)
