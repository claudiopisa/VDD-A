import xml.etree.ElementTree as ET
from model.file.file_collection import FileCollection
from utils import get_logger
from ..xml_parser import XMLParser

logger = get_logger(__name__)

PARAGRAPH_TAG = "paragraph"
SUBPARAGRAPH_TAG = "subparagraph"
TABLE_TAG = "table"
ROW_TAG = "task"

class FileVersioningParser(XMLParser):
    def __init__(self, 
                 root_name: str, 
                 identation: bool = True, 
                 indent_space: str = "  ", 
                 encoding: str = "utf-8", 
                 xml_declaration: bool = True,
                 paragraph_title: str = "LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS",
                 paragraph_number: int | str = "2",
                 file_collection: FileCollection = None
        ):
        super().__init__(root_name, identation, indent_space, encoding, xml_declaration)
        self.paragraph_title = paragraph_title
        self.paragraph_number = paragraph_number
        self.file_collection = file_collection

        self.paragraph = ET.SubElement(self.root, 
                           PARAGRAPH_TAG, 
                                       number=str(self.paragraph_number), 
                                       title=self.paragraph_title
                                       )
        
        if self.file_collection:
            self.parse()
            logger.info("File collection parsed and XML structure created successfully.")
    
    #kinda useless
    def set_file_collection(self, file_collection: FileCollection):
        self.file_collection = file_collection

    def parse(self):
        for i, (folder, files) in enumerate(self.file_collection.items(), start=1):
            subparagraph = ET.SubElement(self.paragraph, 
                                         SUBPARAGRAPH_TAG, 
                                         number=f"{self.paragraph_number}.{i}", 
                                         title=folder
                                         )
            table = ET.SubElement(subparagraph, TABLE_TAG)
            for file in files:
                ET.SubElement(
                    table,
                    ROW_TAG,
                    name=file.name,
                    version=str(file.version),
                ) 

        