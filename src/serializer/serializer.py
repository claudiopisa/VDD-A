import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod 

class Serializer(ABC):
    """
    Abstract base class for XML document generators.

    Subclasses implement :meth:`generate` to populate the XML tree with
    domain-specific elements, then call :meth:`save` to write the result
    to disk.

    The tree is rooted at a single element whose tag name is given by
    ``root_name``.  Indentation and encoding are configurable at
    construction time.
    """

    def __init__(self, root_name: str, identation: bool = True, indent_space: str = "  ", encoding: str = "utf-8", xml_declaration: bool = True):
        """
        Args:
            root_name (str): Tag name of the XML root element (e.g.
                ``"FileVersioning"`` or ``"TaskVersioning"``).
            identation (bool): Whether to pretty-print the output with
                indentation (default: ``True``).
            indent_space (str): String used for each indentation level
                (default: two spaces). Only relevant when
                ``identation=True``.
            encoding (str): Character encoding written into the XML
                declaration and used when saving the file
                (default: ``"utf-8"``).
            xml_declaration (bool): Whether to prepend the
                ``<?xml version='1.0' encoding='...'?>`` declaration line
                (default: ``True``).
        """
        self.root = ET.Element(root_name)
        self.tree = ET.ElementTree(self.root)
        self.identation = identation
        self.indent_space = indent_space
        
        if identation:
            ET.indent(self.tree, space=indent_space)
        
        self.encoding = encoding
        self.xml_declaration = xml_declaration

    def save(self, file_path: str):
        """
        Write the XML tree to a file.

        Re-applies indentation before writing so the output is always
        formatted consistently regardless of when elements were added.

        Args:
            file_path (str): Destination file path (e.g.
                ``"output/versioning.xml"``).
        """
        if self.identation:
            ET.indent(self.tree, space=self.indent_space)
            
        self.tree.write(file_path, encoding=self.encoding, xml_declaration=self.xml_declaration)
    
    @abstractmethod
    def generate(self):
        """
        Populate the XML tree with domain-specific elements.

        Subclasses must implement this method.  Typically it iterates over
        the data model and appends child elements to ``self.root`` or to
        ``self.paragraph``.
        """
        pass