from pathlib import Path
from ConfigLoader.loaders.global_config import ConfigLoaderGlobal
from ConfigLoader.loaders.file_versioning import ConfigLoaderFileVersioning
from DataReader.data_reader_file_versioning import DataReaderFileVersioning
from version_extractor import extract_version
from parsers.xml_writer import build_ch2_xml_attr_rows
from DocGen.doc_gen import generate_chapter2_docx
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

#for file in ch2_reader.scan_files():
#    version = extract_version(file, version_extraction_criteria)
#    rows.append((str(file), version))  #lista di tuple

rows = list(ch2_reader.scan_files())

for r in rows:
    print(r)

print(f"\nTotale file trovati: {len(rows)}")

print("parsing")

# Generate XML for chapter 2
xml_output = build_ch2_xml_attr_rows(rows, chapter_title, out="chapter2_new2.xml")
print(f"XML generated: {xml_output}")

#build_ch2_xml_new(rows, chapter_title, out="ch2_test_2.xml")

output_docx = generate_chapter2_docx(xml_output, "chapter2_output_test.docx")