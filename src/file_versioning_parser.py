import xml.etree.ElementTree as ET
from pathlib import Path

from data_reader import FileVersioning
from configs import CoreConfig, FileVersioningConfig
from utils import setup_logging, get_logger
from model import File

root = ET.Element("FileVersioning")

# Paragraph principale
paragraph = ET.SubElement(root, "paragraph",
    number="2",
    title="LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS"
)

# Dummy values for testing without scan_files().
# Expected shape: dict[folder_path, list[File]]
out: dict[str, list[File]] = {
    r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\INCLUDE": [
        File(name="basdef16.h", version="1.2"),
        File(name="basedef.h", version="3.2"),
        File(name="bitmask.h", version="1.1"),
    ],
    r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\INC_PROT": [
        File(name="APLDiag.h", version="1.3"),
        File(name="Cdb.h", version="1.9"),
        File(name="ParametersSRL.h", version=None),
    ],
}

for idx, (folder, files) in enumerate(out.items(), start=1):
    subparagraph = ET.SubElement(paragraph, "subparagraph", number=f"2.{idx}", title=folder)
    table = ET.SubElement(subparagraph, "table")
    for file in files:
        ET.SubElement(
            table,
            "task",
            name=file.name,
            version=str(file.version),
        )

tree = ET.ElementTree(root)
ET.indent(tree, space="  ")
tree.write("file_versioning.xml", encoding="utf-8", xml_declaration=True)


setup_logging(level = "DEBUG")
logger = get_logger(__name__)

#core_conf = CoreConfig(user_config_path="config/core_config.json")
#fv_conf = FileVersioningConfig(user_config_path="config/file_versioning.json", core_user_config_path=core_conf)

#reader = FileVersioning(config=fv_conf)

#out = reader.scan_files() # output is FileCollection object

#print(out)

