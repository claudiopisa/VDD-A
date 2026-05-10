import xml.etree.ElementTree as ET
from pathlib import Path

from data_reader import FileVersioning
from configs import CoreConfig, FileVersioningConfig
from utils import set_logger, get_logger
from serializer import FileVersioningSerializer

set_logger(level = "DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
fv_conf = FileVersioningConfig(user_config_path="config/file_versioning.json", core_user_config_path=core_conf)

reader = FileVersioning(config=fv_conf)

out = reader.scan_files() # output is FileCollection object

print(out)

xml_gen = FileVersioningSerializer(
    root_name="FileVersioning",
    paragraph_title=fv_conf.title,
    paragraph_number=2,
    file_collection=out,
    config=fv_conf,
)
xml_gen.save("file_versioning_output.xml")


