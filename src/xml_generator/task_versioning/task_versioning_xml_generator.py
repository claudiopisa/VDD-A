import xml.etree.ElementTree as ET
from model.task.task_list import TaskList
from configs import TaskVersioningConfig
from utils import get_logger
from ..xml_generator import XMLGenerator

logger = get_logger(__name__)

class TaskVersioningXMLGenerator(XMLGenerator):
    """
    XML generator for the **task-versioning** section of a VDD document.

    Builds an XML tree with the structure::

        <TaskVersioning>
          <paragraph number="3" title="...">
            <table>
              <task name="..." type="..." version="..." modified="..." />
              ...
            </table>
          </paragraph>
        </TaskVersioning>

    Unlike :class:`FileVersioningXMLGenerator`, all tasks share a single
    flat ``<table>`` — there are no ``<subparagraph>`` elements.

    If a :class:`~model.task.task_list.TaskList` is supplied at construction
    time, :meth:`generate` is called automatically.
    """

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
        """
        Parameters
        ----------
        root_name : str
            Tag name of the XML root element (e.g. ``"TaskVersioning"``).
        identation : bool
            Whether to pretty-print the output (default: ``True``).
        indent_space : str
            String used for each indentation level (default: two spaces).
        encoding : str
            File encoding (default: ``"utf-8"``).
        xml_declaration : bool
            Whether to include the XML declaration header (default: ``True``).
        paragraph_title : str
            Value of the ``title`` attribute on the ``<paragraph>`` element
            (typically read from ``config.title``).
        paragraph_number : int | str
            Value of the ``number`` attribute on the ``<paragraph>`` element
            (default: ``"3"``).
        attribute_names : list[str]
            Names of the XML attributes written on each ``<task>`` row
            element.  Must match attributes present on
            :class:`~model.task.task.Task` objects
            (default: ``["name", "type", "version", "modified"]``).
        tasks : TaskList | None
            The task data to serialise.  When provided, :meth:`generate` is
            called immediately during construction.
        config : TaskVersioningConfig
            Configuration object that provides XML tag constants via
            ``config.tags``.
        """
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
        """
        Populate the XML tree from :attr:`tasks`.

        Creates a single ``<table>`` under ``self.paragraph`` and appends
        one ``<task>`` element per entry in :attr:`tasks`.  Attribute values
        are read from the corresponding properties of each
        :class:`~model.task.task.Task` object via :func:`getattr`.

        A warning is logged for any attribute that evaluates to a falsy value.
        """
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

        

        