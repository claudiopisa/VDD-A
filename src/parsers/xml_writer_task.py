# src/xml/build_ch3_xml.py
from __future__ import annotations
from pathlib import Path
import xml.etree.ElementTree as ET

def build_ch3_xml(rows, title: str, out_xml: str | Path):
    out_xml = Path(out_xml)
    doc = ET.Element("document")
    p = ET.SubElement(doc, "paragraph", number="3", title=title)
    table = ET.SubElement(p, "table")

    for r in rows:
        row = ET.SubElement(table, "row")
        ET.SubElement(row, "name").text = r.name
        ET.SubElement(row, "type").text = r.type
        ET.SubElement(row, "version").text = r.version
        ET.SubElement(row, "modified").text = r.modified

    out_xml.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(doc).write(out_xml, encoding="utf-8", xml_declaration=True)
