import xml.etree.ElementTree as ET
from model.task.task_list import TaskList
from utils import get_logger
from ..xml_parser import XMLParser

logger = get_logger(__name__)

PARAGRAPH_TAG = "paragraph"
SUBPARAGRAPH_TAG = "subparagraph"
TABLE_TAG = "table"
ROW_TAG = "task"

class TaskVersioningParser(XMLParser):
    def __init__(self, 
                 root_name: str, 
                 identation: bool = True, 
                 indent_space: str = "  ", 
                 encoding: str = "utf-8", 
                 xml_declaration: bool = True,
                 paragraph_title: str = "",
                 paragraph_number: int | str = "3",
                 task_list: TaskList = None
        ):
        super().__init__(root_name, identation, indent_space, encoding, xml_declaration)
        self.paragraph_title = paragraph_title
        self.paragraph_number = paragraph_number
        self.task_list = task_list

        self.paragraph = ET.SubElement(self.root, 
                           PARAGRAPH_TAG, 
                                       number=str(self.paragraph_number), 
                                       title=self.paragraph_title
                                       )
        
        if self.task_list:
            self.parse()
            logger.info("Task list parsed and XML structure created successfully.")

    def parse(self):
        #TODO: implement parsing logic based on the structure of TaskList and the desired XML output
        pass