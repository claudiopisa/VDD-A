from configs import CoreConfig
from configs import FileVersioningConfig
from configs import TaskVersioningConfig
from document_builder import DocumentBuilder, FileVersioningRenderer
from document_builder.renderer.task_versioning.task_versioning_renderer import TaskVersioningRenderer
from utils import set_logger, get_logger

set_logger(level = "DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
fv_conf = FileVersioningConfig(user_config_path="config/file_versioning.json", core_user_config_path=core_conf)
tv_conf = TaskVersioningConfig(user_config_path="config/task_versioning.json", core_user_config_path=core_conf)

builder = DocumentBuilder(output_path="fileVersioning.docx")

builder.add_section(FileVersioningRenderer(
                        xml_path="C:\\Users\\claud\\repo\\claudiopisa\\VDD-A\\chapter2_new2.xml",
                        config=fv_conf
                        )
                    )


builder.add_section(TaskVersioningRenderer(
                        xml_path="C:\\Users\\claud\\repo\\claudiopisa\\VDD-A\\task_versioning_output.xml",
                        config=tv_conf
                        )
                    )

builder.save()