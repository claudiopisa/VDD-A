from pathlib import Path
from collections import defaultdict
from pydoc import doc
from lxml import etree

#class that read data from a source and parse it as XML for a xdoc document
class XMLParser:
    def __init__(self, chapter, data):
        self.chapter = chapter
        self.section_count = 0
        self.data = data
        
    
    def parse_table(self):


        for row in self.data:
            self.section_count += 1
            entry = etree.SubElement(self.root, "entry", id=str(self.section_count))
            filename_elem = etree.SubElement(entry, "filename")
            filename_elem.text = row[0]
            version_elem = etree.SubElement(entry, "version")
            version_elem.text = row[1]
        return self.root
    
    

    
    """def build_ch2_xml(self, rows: list[tuple[str, str]],
                  paragraph_title: str = "LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS",
                  out_path: str | Path = "chapter2.xml") -> Path:
       

    """

def build_ch2_xml(rows, title):
    # raggruppa i file per cartella 
    grouped = defaultdict(list) # dizionario di liste
    for full_path, version in rows:
        p = Path(full_path)
        folder = str(p.parent).replace("/", "\\") #per windows
        grouped[folder].append((p.name, version)) # crea un dizionario di liste, key:path valore: lista con nome filee versionee

    # il path nel documento diventa il sottoparagrafo. Raggruppiamo i file per cartella (sottoparagrafo)

    print(grouped)  # test

    doc = etree.Element("document") # root

    par = etree.SubElement(doc, "paragraph", number="2", title=title)
    for idx, folder in enumerate(sorted(grouped.keys()), start=1):
        subpar = etree.SubElement(par, "subparagraph", number=f"2.{idx}", title=folder) 
        table = etree.SubElement(subpar, "table")

        # crea sezione colonne
        cols = etree.SubElement(table, "columns")
        c1 = etree.SubElement(cols, "column", key="file_name")
        c1.text = "File Name"
        c2 = etree.SubElement(cols, "column", key="file_version")
        c2.text = "File Version"
            
        # crea sezione righe
        rows_el = etree.SubElement(table, "rows")

        #test
        """for filename, version in grouped[folder]:
            row = etree.SubElement(table, "row")
            file_elem = etree.SubElement(row, "filename")
            file_elem.text = filename
            version_elem = etree.SubElement(row, "version")
            version_elem.text = version"""

        for file_name, val in sorted(grouped[folder], key=lambda x: x[0].lower()):
            row_el = etree.SubElement(rows_el, "row")

            #write filename
            cell1 = etree.SubElement(row_el, "cell", key="file_name")
            cell1.text = file_name

            #write version
            cell2 = etree.SubElement(row_el, "cell", key="file_version")
            cell2.text = "" if val is None else str(val)


    # crea xml
    tree = etree.ElementTree(doc)
    out_path = Path("chapter2.xml")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(out_path), pretty_print=True, xml_declaration=True, encoding="utf-8")
        
    return out_path


def build_ch2_xml_new(rows, title, out="chapter2_new.xml"):
    # raggruppa i file per cartella 
    grouped = defaultdict(list) # dizionario di liste
    for full_path, version in rows:
        p = Path(full_path)
        folder = str(p.parent).replace("/", "\\") #per windows
        grouped[folder].append((p.name, version)) # crea un dizionario di liste, key:path valore: lista con nome filee versionee

    # il path nel documento diventa il sottoparagrafo. Raggruppiamo i file per cartella (sottoparagrafo)

    doc = etree.Element("document") # root

    folders = sorted(grouped.keys())
    par = etree.SubElement(doc, "paragraph", number="2", title=title) # aggiunge paragrafo (alla root)
    for idx, folder in enumerate(folders, start=1):
        subpar = etree.SubElement(par, "subparagraph", number=f"2.{idx}", title=folder) # aggiunge sottoparagrafo al paragrafo
        table = etree.SubElement(subpar, "table") # aggiunge tabella al sottoparagrafo

        for file_name, version in sorted(grouped[folder], key=lambda x: x[0].lower()):
            row = etree.SubElement(table, "row")

            #file name cell
            cell1 = etree.SubElement(row, "name")
            cell1.text = file_name

            #file version cell
            cell2 = etree.SubElement(row, "version")
            cell2.text = str(version)

    print("Saving XML doc")
    # crea xml
    tree = etree.ElementTree(doc)
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(out_path), pretty_print=True, xml_declaration=True, encoding="utf-8")
    print("done")
        
    return out_path


#main

# Esempio 
rows = [
    (r"NSPC_1.9.0.0\SWPG\INC_PROT\APLDiag.h", "1.3"),
    (r"NSPC_1.9.0.0\SWPG\INC_PROT\bbfatalmsg.h", "1.1"),
    (r"NSPC_1.9.0.0\SWPG\INC_XYZ\foo.h", "2.0"),
]

#build_ch2_xml(rows)

build_ch2_xml_new(rows, "LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS")
