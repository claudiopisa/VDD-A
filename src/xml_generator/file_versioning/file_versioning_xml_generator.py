import xml.etree.ElementTree as ET
from model.file.file_collection import FileCollection
from configs import FileVersioningConfig, FileVersioningTags
from utils import get_logger
from ..xml_generator import XMLGenerator

logger = get_logger(__name__)

class FileVersioningXMLGenerator(XMLGenerator):
    def __init__(self, 
                 root_name: str, 
                 identation: bool = True, 
                 indent_space: str = "  ", 
                 encoding: str = "utf-8", 
                 xml_declaration: bool = True,
                 paragraph_title: str = "LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS",
                 paragraph_number: int | str = "2",
                 attribute_names: list[str] = ["name", "version"],
                 file_collection: FileCollection = None,
                 *,
                 config: FileVersioningConfig,
        ):
        super().__init__(root_name, identation, indent_space, encoding, xml_declaration)
        self.paragraph_title = paragraph_title
        self.paragraph_number = paragraph_number
        self.attributes: dict = {attr: "" for attr in attribute_names}
        self.file_collection = file_collection
        self.config = config
        self.tags = self.config.tags

        self.paragraph = ET.SubElement(self.root,
                                       self.tags.PARAGRAPH, 
                                       number=str(self.paragraph_number), 
                                       title=self.paragraph_title
                                       )
        
        if self.file_collection:
            self.generate()
            logger.info("File collection XML generated successfully.")
    
    #kinda useless
    def set_file_collection(self, file_collection: FileCollection):
        self.file_collection = file_collection

    # three nested loop, but the inner loop is just to get the attributes, so it should be fine for now  (i hope so)
    def generate(self):
        for i, (folder, files) in enumerate(self.file_collection.items(), start=1):
            subparagraph = ET.SubElement(self.paragraph, 
                                         self.tags.SUBPARAGRAPH, 
                                         number=f"{self.paragraph_number}.{i}", 
                                         title=folder
                                         )
            
            table = ET.SubElement(subparagraph, self.tags.TABLE)
            for file in files:
                for attr in self.attributes.keys():
                    value = getattr(file, attr, "")
                    self.attributes[attr] = "" if value is None else str(value)

                ET.SubElement(
                    table,
                    self.tags.ROW,
                    **self.attributes,
                ) 

        