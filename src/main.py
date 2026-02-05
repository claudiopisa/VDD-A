from pathlib import Path
from ConfigLoader.loaders.global_config import ConfigLoaderGlobal
from ConfigLoader.loaders.file_versioning import ConfigLoaderFileVersioning
from DataReader.data_reader_file_versioning import DataReaderFileVersioning
from version_extractor import extract_version
#from parser import build_ch2_xml_new
#from doc_gen import render_ch2_new

try:
    global_cfg = ConfigLoaderGlobal("config/global_config.json")
    ch2_cfg = ConfigLoaderFileVersioning("config/ch2_config.json")
except Exception as e:
    print(f"Error | {e}")
    exit(1)

workspace = global_cfg.get_stream_root(as_path=True)

component = global_cfg.get_components().NSPC
root = workspace / component

print(root)

allowed_ext = ch2_cfg.get_allowed_extensions()
exclude_dirs = ch2_cfg.get_excluded_dirs()
chapter_title = ch2_cfg.get_title()
version_extraction_criteria = ch2_cfg.get_version_extraction_criteria()

try:
    ch2_reader = DataReaderFileVersioning(root, ch2_cfg)
except Exception as e:
    print(f"Error | {e}")
    exit(1)

rows = []

for file in ch2_reader.scan_files():
    version = extract_version(file)
    rows.append((str(file), version))  #lista di tuple

for r in rows:
    print(r)

print(f"\nTotale file trovati: {len(rows)}")

print("parsing")

#build_ch2_xml_new(rows, chapter_title, out="ch2_test_2.xml")

