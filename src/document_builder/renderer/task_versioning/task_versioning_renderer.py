from docx import Document
from pathlib import Path
import xml.etree.ElementTree as ET

from configs import TaskVersioningConfig
from utils import logger

from ..renderer import Renderer

class TaskVersioningRenderer(Renderer):
    """
    Renderer for the **task-versioning** section of a VDD document.

    Reads a task-versioning XML produced by
    :class:`~xml_generator.task_versioning.TaskVersioningXMLGenerator` and
    writes the corresponding Word content into a ``python-docx``
    :class:`Document`:

    * A **level-1 heading** for the chapter (from ``<paragraph>``).
    * A single flat **table** for all tasks
      (from ``<table>/<task>`` elements).
    """

    def __init__(self, xml_path: str | Path, config: TaskVersioningConfig):
        """
        Parameters
        ----------
        xml_path : str | Path
            Path to the task-versioning XML file to render.
        config : TaskVersioningConfig
            Configuration object that provides tag constants
            (``config.tags``) and column headers (``config.columns_name``).
        """
        super().__init__(xml_path)
        self.config = config
        self.tags = self.config.tags
        self.headers = self.config.columns_name

    def render_section(self, document: Document):
        """
        Write the task-versioning chapter into ``document``.

        Adds the following content in order:

        1. A level-1 heading ``"<number>. <title>"`` from the
           ``<paragraph>`` element.
        2. If a ``<table>`` child is present, a formatted Word table via
           :meth:`~Renderer.render_table`.

        Parameters
        ----------
        document : Document
            The ``python-docx`` document to append content to.

        Raises
        ------
        ValueError
            If the XML root does not contain a ``<paragraph>`` element.
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
            chapter_number = "3"

        # add paragraph heading
        heading = document.add_heading(f"{chapter_number}. {chapter_title}", level=1)

        #table
        table_elem = paragraph.find(self.tags.TABLE)
        if table_elem is not None:
            self.render_table(
                document=document,
                table_elem=table_elem,
                headers=self.headers,
                tags=self.tags,
            )

