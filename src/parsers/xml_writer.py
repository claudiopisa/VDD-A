from pathlib import Path
from collections import defaultdict
from lxml import etree
from typing import List, Tuple


def build_ch2_xml_attr_rows(rows: List[Tuple[str, str]], title: str, out: str | Path = "chapter2_new.xml") -> Path:
    """Create chapter2 XML where each <table> contains <row name="..." version="..."/> elements.

    Args:
        rows: iterable of (full_path, version) tuples
        title: paragraph title
        out: output XML path

    Returns:
        Path to written XML file
    """
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for full_path, version in rows:
        p = Path(full_path)
        folder = str(p.parent).replace("/", "\\")
        grouped[folder].append((p.name, version))

    doc = etree.Element("document")
    par = etree.SubElement(doc, "paragraph", number="2", title=title)

    for idx, folder in enumerate(sorted(grouped.keys()), start=1):
        subpar = etree.SubElement(par, "subparagraph", number=f"2.{idx}", title=folder)
        table = etree.SubElement(subpar, "table")

        for file_name, version in sorted(grouped[folder], key=lambda x: x[0].lower()):
            attrs = {"name": file_name, "version": "" if version is None else str(version)}
            etree.SubElement(table, "row", **attrs)

    tree = etree.ElementTree(doc)
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(out_path), pretty_print=True, xml_declaration=True, encoding="utf-8")

    return out_path
