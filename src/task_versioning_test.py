from DataReader.data_reader_file_versioning import DataReaderFileVersioning
from configs.core_config import CoreConfig
from configs.task_versioning_config import TaskVersioningConfig

#core config
core_conf = CoreConfig(user_config_path="config/core_config.json")

#task versioning config 
tv_conf =  TaskVersioningConfig(user_config_path="config/task_versioning.json")

workspace = core_conf.stream_root_as_path
print(f"Workspace: {workspace}")
print(core_conf.components)
component = core_conf.components.NSPC
root = workspace / component
print(f"Root: {root}")
