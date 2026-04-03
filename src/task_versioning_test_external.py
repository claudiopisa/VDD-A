from data_reader import TaskVersioningExternal
from configs.task_versioning_config import TaskVersioningConfig
from configs.core_config import CoreConfig
from utils.logger import setup_logging, get_logger

setup_logging(level = "DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
tv_conf = TaskVersioningConfig(user_config_path="config/task_versioning.json", core_user_config_path=core_conf)

reader = TaskVersioningExternal(config=tv_conf)

out = reader.scan_files()

print(out)
