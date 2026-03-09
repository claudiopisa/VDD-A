from DataReader.data_reader_task_versioning_external import DataReaderTaskVersioningExternal
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

print(f"Components to scan: {comp}")

prev_workspace = None
if tv_conf.has_previous_release() and tv_conf.previous_release_root:
    prev_workspace = tv_conf.previous_release_root_as_path
    if prev_workspace.exists():
        print(f"Previous stream root detected: {prev_workspace}")
    else:
        print("Previous stream root specified but not found -> Modified will be N/A")



app_imgconf_root = workspace / comp[0] / "Configurazioni"
print(f"\nCurrent Imgconf.ini at: {app_imgconf_root}")

app_imgconf_kwargs =  {Path(task).stem: Path(app_imgconf_root) / task for task in tv_conf.app_tasks}

print(f"App imgconf kwargs: {app_imgconf_kwargs}")

prev_imgconf = None
if prev_workspace:
    candidate = prev_workspace / comp[0] / "Configurazioni"
    if candidate.exists():
        prev_imgconf = candidate
        print(f"Prev Imgconf.ini: {prev_imgconf}")
    else:
        print(f"Prev Imgconf.ini not found for {comp} -> Modified will be N/A")

sys_imgconf = workspace / comp[1] / core_conf.image_config_name
print(f"\nCurrent Sys Imgconf.ini at: {sys_imgconf}")

taskorder = workspace / comp[0] / "Configurazioni" / "taskorder.ini"
reader = DataReaderTaskVersioningExternal(reader_config=tv_conf, sys_imgconf_path=sys_imgconf, app_imgconf_paths=app_imgconf_kwargs, task_order=taskorder, prev_sys_imgconf_path=None, prev_app_imgconf_paths=None, prev_task_order=None)
tasks = reader.scan_files()
x = reader._read_taskorder(taskorder)

print(tasks)

