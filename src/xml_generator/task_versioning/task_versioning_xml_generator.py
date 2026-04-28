import xml.etree.ElementTree as ET
from model.task.task_list import TaskList
from configs import TaskVersioningConfig
from utils import get_logger
from ..xml_generator import XMLGenerator

logger = get_logger(__name__)

class TaskVersioningXMLGenerator(XMLGenerator):
    def __init__(self, 
                 root_name: str, 
                 identation: bool = True, 
                 indent_space: str = "  ", 
                 encoding: str = "utf-8", 
                 xml_declaration: bool = True,
                 paragraph_title: str = "",
                 paragraph_number: int | str = "3",
                 attribute_names: list[str] = ["name", "type", "version", "modified"],
                 tasks: TaskList = None,
                 *,
                 config: TaskVersioningConfig,
        ):
        super().__init__(root_name, identation, indent_space, encoding, xml_declaration)
        self.paragraph_title = paragraph_title
        self.paragraph_number = paragraph_number
        self.attributes: dict = {attr: "" for attr in attribute_names}
        self.tasks = tasks
        self.config = config
        self.tags = self.config.tags

        self.paragraph = ET.SubElement(self.root, 
                                       self.tags.PARAGRAPH, 
                                       number=str(self.paragraph_number), 
                                       title=self.paragraph_title
                                       )
        
        if self.tasks: #if task list is given then generate right away
            self.generate()
            logger.info("Task list XML generated successfully.")

    def generate(self):
        table = ET.SubElement(self.paragraph, self.tags.TABLE)

        for task in self.tasks:
            for attr in self.attributes.keys():
                value = getattr(task, attr, "")
                if not value:
                    logger.warning(f"Attribute {attr!r} not found. Using empty string.")
                self.attributes[attr] = str(value)

            ET.SubElement(
                table,
                self.tags.ROW,
                **self.attributes
            )
            """ET.SubElement(
                table,
                ROW_TAG,
                name=task.name,
                type=task.type,
                version=str(task.version),
                modified=str(task.modified)
            )"""

        

        