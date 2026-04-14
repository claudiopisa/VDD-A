import xml.etree.ElementTree as ET
from pathlib import Path

from data_reader import FileVersioning
from configs import CoreConfig, FileVersioningConfig
from utils import setup_logging, get_logger
from model import File
from parsers import FileVersioningParser

setup_logging(level = "DEBUG")
logger = get_logger(__name__)

core_conf = CoreConfig(user_config_path="config/core_config.json")
fv_conf = FileVersioningConfig(user_config_path="config/file_versioning.json", core_user_config_path=core_conf)

reader = FileVersioning(config=fv_conf)

out = reader.scan_files() # output is FileCollection object

print(out)

parser = FileVersioningParser(root_name="FileVersioning",
                              paragraph_title=fv_conf.title,
                              paragraph_number=2,
                              file_collection=out)


parser.parse()
parser.save("file_versioning_output.xml")


