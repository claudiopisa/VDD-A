from docx import Document
from pathlib import Path
import xml.etree.ElementTree as ET

from configs import TaskVersioningConfig
from utils import logger

from ..renderer import Renderer

class TaskVersioningRenderer(Renderer):
    def __init__(self, xml_path: str | Path, config: TaskVersioningConfig):
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
            chapter_number = "3"

        # add paragraph heading
        heading = document.add_heading(f"{chapter_number}. {chapter_title}", level=1)

        #table
        table_elem = paragraph.find(self.tags.TABLE)
        if table_elem is not None:
            task_list = table_elem.findall(self.tags.ROW) # list of file elements, i.e. rows of the table

            if len(task_list) == 0:
                logger.warning(f"No {self.tags.ROW!r} elements found in the XML. The table will be empty.")
                return
            
            # Add table with headers
            table =  document.add_table(rows=1, cols=len(self.headers))
            table.style = 'Table Grid'

            #set header row
            header_cells = table.rows[0].cells
            for i, header in enumerate(self.headers):
                header_cells[i].text = header

            #make header row bold
            for cell in header_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True

            # Add task rows
            for task in task_list:
                row_cells = table.add_row().cells # add cells to row
                for i, header in enumerate(self.headers):
                    attr_name = header.strip().lower().replace(" ", "_")
                    cell_value = task.get(attr_name, None) # get value for the current header, default to empty string if not found
                    
                    if cell_value is None:
                        logger.warning(
                            f"Task element is missing attribute {attr_name!r} for header {header!r}. Using empty string as default."
                        )
                        cell_value = ""
                    
                    row_cells[i].text = cell_value

