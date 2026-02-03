from pathlib import Path
from ConfigLoader.config_loader import ConfigLoader
from FileScanner.file_scanner import scan_files
from version_extractor import extract_version
from parser import build_ch2_xml_new
from doc_gen import render_ch2_new

try:
    global_cfg = ConfigLoader("config/global_config.json").data
    ch2_cfg = ConfigLoader("config/ch2_config.json").data
except Exception as e:
    print(f"Error | {e}")
    exit(1)

workspace = Path(global_cfg["paths"]["stream_root"])
component = global_cfg["paths"]["components"]["NSPC"]
root = workspace / component

print(root)

allowed_ext = set(ch2_cfg["scan"]["allowed_extensions"])
exclude_dirs = set(ch2_cfg["scan"]["exclude"]["dirs_exact"])
chapter_title = ch2_cfg["title"]
version_extraction_criteria = ch2_cfg["scan"]["version_extraction_criteria"]

rows = []

for file in scan_files(root, allowed_ext, exclude_dirs):
    version = extract_version(file)
    rows.append((str(file), version))  #lista di tuple

for r in rows:
    print(r)

print(f"\nTotale file trovati: {len(rows)}")

print("parsing")

build_ch2_xml_new(rows, chapter_title, out="ch2_test_2.xml")

