import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

def build_ch3_xml(tasks, out_xml: Path):
    root = ET.Element("document")

    ch3 = ET.SubElement(
        root,
        "paragraph",
        number="3",
        title="TASK VERSION IDENTIFICATION"
    )

    table = ET.SubElement(ch3, "table")

    for t in tasks:
        ET.SubElement(
            table,
            "row",
            name=t.name,
            type=t.type,
            version=t.version,
            modified=t.modified
        )

    rough = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")

    out_xml.parent.mkdir(parents=True, exist_ok=True)
    out_xml.write_text(pretty, encoding="utf-8")
