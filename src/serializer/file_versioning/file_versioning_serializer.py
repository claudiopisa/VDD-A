import xml.etree.ElementTree as ET
from model.file.file_collection import FileCollection
from configs import FileVersioningConfig
from utils import get_logger
from ..serializer import Serializer

logger = get_logger(__name__)

class FileVersioningSerializer(Serializer):
    """
    XML generator for the **file-versioning** section of a VDD document.

    Builds an XML tree with the structure::

        <FileVersioning>
          <paragraph number="2" title="...">
            <subparagraph number="2.1" title="<folder path>">
              <table>
                <file name="..." version="..." />
                ...
              </table>
            </subparagraph>
            ...
          </paragraph>
        </FileVersioning>

    If a :class:`~model.file.file_collection.FileCollection` is supplied at
    construction time, :meth:`generate` is called automatically.
    """

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
        """
        Args:
            root_name (str): Tag name of the XML root element (e.g.
                ``"FileVersioning"``).
            identation (bool): Whether to pretty-print the output
                (default: ``True``).
            indent_space (str): String used for each indentation level
                (default: two spaces).
            encoding (str): File encoding (default: ``"utf-8"``).
            xml_declaration (bool): Whether to include the XML declaration
                header (default: ``True``).
            paragraph_title (str): Value of the ``title`` attribute on the
                ``<paragraph>`` element.
            paragraph_number (int | str): Value of the ``number`` attribute
                on the ``<paragraph>`` element (default: ``"2"``).
            attribute_names (list[str]): Names of the XML attributes written
                on each ``<file>`` row element. Must match attributes present
                on :class:`~model.file.file.File` objects
                (default: ``["name", "version"]``).
            file_collection (FileCollection | None): The file data to
                serialise. When provided, :meth:`generate` is called
                immediately during construction.
            config (FileVersioningConfig): Configuration object that provides
                XML tag constants via ``config.tags``.
        """
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
        """
        Set the file collection after construction.

        Args:
            file_collection (FileCollection): The file data to serialise.
                Call :meth:`generate` afterwards to populate the XML tree.
        """
        self.file_collection = file_collection

    # three nested loop, but the inner loop is just to get the attributes, so it should be fine for now  (i hope so)
    def generate(self):
        """
        Populate the XML tree from :attr:`file_collection`.

        Iterates over every folder/files pair in the
        :class:`~model.file.file_collection.FileCollection`, creating one
        ``<subparagraph>`` per folder and one ``<file>`` element per file
        inside a ``<table>`` child.

        Each ``<file>`` element carries the attributes listed in
        ``self.attributes`` (derived from ``attribute_names`` passed at
        construction time). Values are read from the corresponding
        properties of each :class:`~model.file.file.File` object via
        :func:`getattr`.
        """
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
        

