from pathlib import Path
from ConfigLoader.loaders.global_config import ConfigLoaderGlobal
from ConfigLoader.loaders.file_versioning import ConfigLoaderFileVersioning
from data_reader.file_versioning.file_versioning import FileVersioning
from version_extractor_test import extract_version
from parsers.xml_writer import build_ch2_xml_attr_rows
from DocGen.doc_gen import generate_chapter2_docx
from utils.logger import setup_logging, get_logger


setup_logging()
logger = get_logger(__name__)

try:
    global_cfg = ConfigLoaderGlobal("config/global_config.json")
    ch2_cfg = ConfigLoaderFileVersioning("config/ch2_config.json")
except Exception as e:
    logger.exception("Error loading configuration: %s", e)
    exit(1)

workspace = global_cfg.get_stream_root(as_path=True)

component = global_cfg.get_components().SAFETY_NUCLEUS
root = workspace / component

logger.debug("Root path: %s", root)

allowed_ext = ch2_cfg.get_allowed_extensions()
exclude_dirs = ch2_cfg.get_excluded_dirs()
chapter_title = ch2_cfg.get_title()
version_extraction_criteria = ch2_cfg.get_version_extraction_criteria()

try:
    ch2_reader = FileVersioning(ch2_cfg)
except Exception as e:
    logger.exception("Error initializing FileVersioning: %s", e)
    exit(1)

rows = []

#for file in ch2_reader.scan_files():
#    version = extract_version(file, version_extraction_criteria)
#    rows.append((str(file), version))  #lista di tuple

rows = list(ch2_reader.scan_files())

for r in rows:
    logger.debug("Row: %s", r)

logger.info("Parsing chapter 2 data")

# Generate XML for chapter 2
xml_output = build_ch2_xml_attr_rows(rows, chapter_title, out="chapter2_new2.xml")
logger.info("XML generated: %s", xml_output)

#build_ch2_xml_new(rows, chapter_title, out="ch2_test_2.xml")

output_docx = generate_chapter2_docx(xml_output, "chapter2_output_test.docx")