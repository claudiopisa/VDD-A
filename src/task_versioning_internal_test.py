from DataReader.data_reader_task_versioning_internal import DataReaderTaskVersioningInternal
from configs.core_config import CoreConfig
from configs.task_versioning_config import TaskVersioningConfig
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

# Core config
core_conf = CoreConfig(user_config_path=CONFIG_DIR / "core_config.json")
# Task versioning config
tv_conf = TaskVersioningConfig(user_config_path=CONFIG_DIR / "task_versioning.json")

workspace = core_conf.stream_root_as_path
print(f"Workspace: {workspace}")

# Pick components roots based on kernel mode
if core_conf.is_kernel_internal:
    print("Kernel mode is internal.")
    comp = tv_conf.internal_roots
else:
    print("Kernel mode is external.")
    comp = tv_conf.external_roots


prev_workspace = None
if tv_conf.has_previous_release() and tv_conf.previous_release_root:
    prev_workspace = tv_conf.previous_release_root_as_path
    if prev_workspace.exists():
        print(f"Previous stream root detected: {prev_workspace}")
    else:
        print("Previous stream root specified but not found -> Modified will be N/A")


imgconf = workspace / comp / core_conf.image_config_name
print(f"\nCurrent Imgconf.ini at: {imgconf}")

prev_imgconf = None
if prev_workspace:
    candidate = prev_workspace / comp / core_conf.image_config_name
    if candidate.exists():
        prev_imgconf = candidate
        print(f"Prev Imgconf.ini: {prev_imgconf}")
    else:
        print(f"Prev Imgconf.ini not found for {comp} -> Modified will be N/A")

reader = DataReaderTaskVersioningInternal(reader_config=tv_conf, imgconf_path=imgconf, prev_imgconf_path=prev_imgconf)
tasks = reader.scan_files()
print(tasks)

