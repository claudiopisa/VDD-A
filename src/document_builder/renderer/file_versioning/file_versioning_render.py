from docx import Document
from pathlib import Path
import xml.etree.ElementTree as ET

from configs import FileVersioningConfig
from utils import logger

from ..renderer import Renderer

class FileVersioningRenderer(Renderer):
    def __init__(self, xml_path: str | Path, config: FileVersioningConfig):

        super().__init__(xml_path)
        self.config = config
        self.tags = self.config.tags
        self.headers = self.config.columns_name

    def render_section(self, document: Document):
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
                task_list = table_elem.findall(self.tags.ROW) # list of file elements, i.e. rows of the table
                
                if task_list:
                    # Create Word table with header
                    table = document.add_table(rows=1, cols=len(self.headers))
                    table.style = 'Light Grid Accent 1'
                    
                    # Set header row
                    header_cells = table.rows[0].cells # `table.rows[0]` is the header row, `.cells` is the list of cells in that row
                    for i, header in enumerate(self.headers):
                        header_cells[i].text = header
                    
                    # Make header bold
                    for cell in header_cells:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.bold = True
                    
                    # Add data rows
                    for task_elem in task_list:
                        row_cells = table.add_row().cells
                        for i, header in enumerate(self.headers):
                            cell_value = task_elem.get(header.lower(), "")
                            row_cells[i].text = cell_value
                    
                    # Set column widths (optional, can be adjusted as needed)
                    #for row in table.rows:
                        #for cell in row.cells:
                            #cell.width = Inches(4.5)
 