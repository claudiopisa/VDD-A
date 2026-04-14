from data_reader import TaskVersioningInternal
from configs import CoreConfig, TaskVersioningConfig
from utils import setup_logging, get_logger
from parsers import TaskVersioningParser

setup_logging(level="DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
tv_conf = TaskVersioningConfig(
    user_config_path="config/task_versioning.json",
    core_user_config_path=core_conf,
)

reader = TaskVersioningInternal(config=tv_conf)
out = reader.scan_files()
task_list = out if out is not None else reader.tasks

print(task_list)

parser = TaskVersioningParser(
    root_name="TaskVersioning",
    paragraph_title=tv_conf.title,
    paragraph_number=3,
    task_list=task_list,
)

parser.save("task_versioning_output.xml")
