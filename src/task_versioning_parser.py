from data_reader import TaskVersioningInternal
from configs import CoreConfig, TaskVersioningConfig
from utils import set_logger, get_logger
from serializer import TaskVersioningSerializer

set_logger(level="DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
tv_conf = TaskVersioningConfig(
    user_config_path="config/task_versioning.json",
    core_user_config_path=core_conf,
)

reader = TaskVersioningInternal(config=tv_conf)
task_list = reader.scan_files()

print(task_list)

xml_gen = TaskVersioningSerializer(
    root_name="TaskVersioning",
    paragraph_title=tv_conf.title,
    paragraph_number=3,
    tasks=task_list,
    config=tv_conf,
)
xml_gen.save("task_versioning_output.xml")
