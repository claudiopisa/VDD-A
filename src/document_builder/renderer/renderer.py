from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from docx import Document
import xml.etree.ElementTree as ET

class Renderer(ABC):
    def __init__(self, xml_path: str | Path):
        if not isinstance(xml_path, Path):
            xml_path = Path(xml_path)
        
        self.xml_path = xml_path
        self.root = ET.parse(self.xml_path).getroot()

    #def render_table(self, table_elem: ET.Element[str]):
        #rows = table_elem.findall("row")

    @abstractmethod
    def render_section(self, document: Document):
        pass
    
