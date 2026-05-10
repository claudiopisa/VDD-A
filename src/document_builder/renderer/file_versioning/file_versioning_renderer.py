from docx import Document
from pathlib import Path
import xml.etree.ElementTree as ET

from configs import FileVersioningConfig
from utils import logger

from ..renderer import Renderer

class FileVersioningRenderer(Renderer):
    """
    Renderer for the **file-versioning** section of a VDD document.

    Reads a file-versioning XML produced by
    :class:`~serializer.file_versioning.FileVersioningSerializer` and
    writes the corresponding Word content into a ``python-docx``
    :class:`Document`:

    * A **level-1 heading** for the chapter (from ``<paragraph>``).
    * A **level-2 heading** for each sub-folder (from ``<subparagraph>``).
    * A **table** for the files in each
      sub-folder (from ``<table>/<file>`` elements).
    """

    def __init__(self, xml_path: str | Path, config: FileVersioningConfig):
        """
        Args:
            xml_path (str | Path): Path to the file-versioning XML file
                to render.
            config (FileVersioningConfig): Configuration object that provides
                tag constants (``config.tags``) and column headers
                (``config.columns_name``).
        """
        super().__init__(xml_path)
        self.config = config
        self.tags = self.config.tags
        self.headers = self.config.columns_name

    def render_section(self, document: Document):
        """
        Write the file-versioning chapter into ``document``.

        Adds the following content in order:

        1. A level-1 heading ``"<number>. <title>"`` from the
           ``<paragraph>`` element.
        2. For each ``<subparagraph>``: a level-2 heading and, if a
           ``<table>`` child is present, a formatted Word table via
           :meth:`~Renderer.render_table`.

        Args:
            document (Document): The ``python-docx`` document to append
                content to.

        Raises:
            ValueError: If the XML root does not contain a ``<paragraph>``
                element.
        """
        #Parse XML
        #paragraph
        paragraph = self.root.find(self.tags.PARAGRAPH)
        if paragraph is None:
            raise ValueError(f"XML does not contain a {self.tags.PARAGRAPH!r} element.")
        
        #set main chapter title
        chapter_title = paragraph.get('title')
        if chapter_title is None:
            logger.warning(f"{self.tags.PARAGRAPH!r} element is missing 'title' attribute. Trying to retrieve from user config.")
            chapter_title = self.config.title

        chapter_number = paragraph.get("number")
        if chapter_number is None:
            logger.warning(f"{self.tags.PARAGRAPH!r} element is missing 'number' attribute. Using default placeholder.")
            chapter_number = "2"

        # add paragraph heading
        heading = document.add_heading(f"{chapter_number}. {chapter_title}", level=1)
        
        #subparagraphs
        subparagraphs = paragraph.findall(self.tags.SUBPARAGRAPH)

        for subpar in subparagraphs:
            subpar_number = subpar.get("number")
            if subpar_number is None:
                logger.warning(f"{self.tags.SUBPARAGRAPH!r} element is missing 'number' attribute. Using default placeholder.")
                subpar_number = ""

            subpar_title = subpar.get("title")
            if subpar_title is None:
                logger.warning(f"{self.tags.SUBPARAGRAPH!r} element is missing 'title' attribute. Using default placeholder.")
                subpar_title = ""

            # Add subparagraph heading
            subheading = document.add_heading(f"{subpar_number} {subpar_title}", level=2)
            
            #table
            table_elem = subpar.find(self.tags.TABLE)
            if table_elem is not None:
                self.render_table(
                    document=document,
                    table_elem=table_elem,
                    headers=self.headers,
                    tags=self.tags,
                    table_style='Light Grid Accent 1',
                )
                    
                    # Set column widths (optional, can be adjusted as needed)
                    #for row in table.rows:
                        #for cell in row.cells:
                            #cell.width = Inches(4.5)
 