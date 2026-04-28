from configs.core_config import CoreConfig
from configs.file_versioning_config import FileVersioningConfig
from document_builder import DocumentBuilder, FileVersioningRenderer
from utils import set_logger, get_logger

set_logger(level = "DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
fv_conf = FileVersioningConfig(user_config_path="config/file_versioning.json", core_user_config_path=core_conf)

builder = DocumentBuilder(output_path="fileVersioning.docx")
renderer = FileVersioningRenderer(
            xml_path="C:\\Users\\claud\\repo\\claudiopisa\\VDD-A\\chapter2_new2.xml",
            config=fv_conf)

builder.add_section(renderer)
builder.save()