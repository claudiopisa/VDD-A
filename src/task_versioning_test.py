from pathlib import Path
from DataReader.data_reader_file_versioning import DataReaderFileVersioning
from DataReader.data_reader_task_versioning import DataReaderTaskVersioning
from configs.core_config import CoreConfig
from configs.task_versioning_config import TaskVersioningConfig

#core config
core_conf = CoreConfig(user_config_path="config/core_config.json")

#task versioning config 
tv_conf =  TaskVersioningConfig(user_config_path="config/task_versioning.json")

workspace = core_conf.stream_root_as_path
print(f"Workspace: {workspace}")

if core_conf.is_kernel_internal:
    print("Kernel mode is internal.")
    components = tv_conf.internal_roots
else:
    print("Kernel mode is external.")
    components = tv_conf.external_roots

print(f"Components to scan: {components}")


ini = workspace / components / core_conf.image_config_name
print(f"Looking for Imgconf.ini at: {ini}")

reader = DataReaderTaskVersioning(ini)
tasks = reader.read_tasks_imgconf()

print(tasks)