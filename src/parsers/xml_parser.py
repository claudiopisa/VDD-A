import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod 

class XMLParser(ABC):
    def __init__(self, root_name: str, identation: bool = True, indent_space: str = "  ", encoding: str = "utf-8", xml_declaration: bool = True):
        self.root = ET.Element(root_name)
        self.tree = ET.ElementTree(self.root)
        self.identation = identation
        self.indent_space = indent_space
        
        if identation:
            ET.indent(self.tree, space=indent_space)
        
        self.encoding = encoding
        self.xml_declaration = xml_declaration

    def save(self, file_path: str):
        if self.identation:
            ET.indent(self.tree, space=self.indent_space)
        self.tree.write(file_path, encoding=self.encoding, xml_declaration=self.xml_declaration)
    
    @abstractmethod
    def parse(self):
        pass