# data reader task versioning internal test

from DataReader.data_reader_task_versioning_internal import DataReaderTaskVersioningInternal
from configs.core_config import CoreConfig
from configs.task_versioning_config import TaskVersioningConfig
from model.data_path import DataPath


# Core config
core_conf = CoreConfig(user_config_path="config/core_config.json") # defualt config
# Task versioning config
tv_conf = TaskVersioningConfig(user_config_path="config/task_versioning.json") # user config

workspace = core_conf.stream_root_as_path
print(f"Workspace: {workspace}")

# Pick components roots based on kernel mode
if core_conf.is_kernel_internal:
    print("Kernel mode: internal.")
    comp : str = tv_conf.internal_roots
else:
    print("Kernel mode: external.")
    comp : str = tv_conf.external_roots

print(f"Components to scan: {comp}")
print(f"Type of components: {type(comp)}")

if tv_conf.has_previous_release and tv_conf.previous_release_root:
    prev_workspace = tv_conf.previous_release_root_as_path
    if prev_workspace.exists():
        print(f"Previous stream root detected: {prev_workspace}")
    else:
        print("Previous stream root specified but not found -> Modified will be N/A")



ini = DataPath(workspace / comp / core_conf.image_config_name)
print(f"\nLooking for Imgconf.ini at: {ini}")

prev_ini = None
if prev_workspace:
    candidate = prev_workspace / comp / core_conf.image_config_name
    if candidate.exists():
        prev_ini = DataPath(candidate)
        print(f"Baseline Imgconf.ini: {prev_ini}")
    else:
        print(f"Baseline Imgconf.ini not found for {comp} -> Modified will be N/A")

reader = DataReaderTaskVersioningInternal(imgconf_path=ini, prev_imgconf_path=prev_ini)

#tasks = reader.scan_files()
#print(tasks)