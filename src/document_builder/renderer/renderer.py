from abc import ABC, abstractmethod
from typing import Callable, Sequence
import logging
from pathlib import Path
from docx import Document
import xml.etree.ElementTree as ET

from configs.default_config.core_default_config import XMLTag


logger = logging.getLogger(__name__)

class Renderer(ABC):
    """
    Abstract base class for all VDD document renderers.

    A renderer is responsible for reading a versioning XML file and writing
    the corresponding content into a ``python-docx`` :class:`Document`.

    Concrete subclasses must implement :meth:`render_section`.  The shared
    :meth:`render_table` helper is available for writing formatted tables
    without duplicating boilerplate.

    Typical usage (via :class:`~document_builder.DocumentBuilder`)::

        builder = DocumentBuilder(template="template.docx")
        builder.add_section(FileVersioningRenderer("versioning.xml", config))
    """

    def __init__(self, xml_path: str | Path):
        """
        Parameters
        ----------
        xml_path : str | Path
            Path to the versioning XML file.  Parsed once at construction
            time; the root element is stored in ``self.root``.
        """
        if not isinstance(xml_path, Path):
            xml_path = Path(xml_path)
        
        self.xml_path = xml_path
        self.root = ET.parse(self.xml_path).getroot()

    def render_table(
        self,
        document: Document,
        table_elem: ET.Element,
        headers: Sequence[str],
        tags: XMLTag,
        table_style: str = "Table Grid",
        header_to_attr: Callable[[str], str] | None = None,
    ) -> None:
        """
        Render an XML table element into a Word document table.

        Reads row elements from ``table_elem``, creates a Word table with a
        bold header row, and fills one data row per XML element found.

        Parameters
        ----------
        document : Document
            The ``python-docx`` :class:`Document` object to append the table
            to. The table is added at the current end of the document.
        table_elem : ET.Element
            The XML element whose **direct children** matching ``tags.ROW``
            are treated as data rows (e.g. the ``<table>`` element parsed from
            the versioning XML). If no children are found the method logs a
            warning and returns without adding anything to the document.
        headers : Sequence[str]
            Ordered list of column labels written into the **first (header)
            row** of the Word table. Each label is rendered in **bold**.
            The number of columns in the table equals ``len(headers)``.
        tags : XMLTag
            Dataclass holding XML tag name constants. Only ``tags.ROW`` is
            used here — it identifies which child tag name to look for inside
            ``table_elem`` (e.g. ``"file"`` for file-versioning or ``"task"``
            for task-versioning).
        table_style : str
            Name of a built-in Word table style applied to the whole table
            (default: ``"Table Grid"``). Any style available in the target
            ``.docx`` template is accepted, e.g. ``"Light Grid Accent 1"``.
        header_to_attr : Callable[[str], str] | None
            A function that converts a header label into the corresponding
            XML attribute name to read from each row element.

            Use this when the column label shown in the document does **not**
            match the XML attribute name 1-to-1. For example::

                # Column "Task Name"  →  XML attribute "name"
                # Column "Last Modified"  →  XML attribute "modified"
                render_table(
                    ...,
                    headers=["Task Name", "Last Modified"],
                    header_to_attr=lambda h: {"Task Name": "name",
                                              "Last Modified": "modified"}[h],
                )

            .. note::
                When ``None`` (default), the mapping is derived automatically:
                strip whitespace, lowercase, replace spaces with underscores.
                This works whenever the header already matches the attribute
                name after that transformation (e.g. ``"Version"`` → ``"version"``
                or ``"Task Type"`` → ``"task_type"``).
        """
        rows = table_elem.findall(tags.ROW) # list of file elements, i.e. rows of the table

        if len(rows) == 0:
            logger.warning(f"No {tags.ROW!r} elements found in the XML. The table will be empty.")
            return

        if header_to_attr is None:
            header_to_attr = lambda header: header.strip().lower().replace(" ", "_")
        
        # Add table with headers
        table =  document.add_table(rows=1, cols=len(headers))
        table.style = table_style

        # Set header row
        header_cells = table.rows[0].cells # list of cells in the first row (header row)
        for i, header in enumerate(headers):
            header_cells[i].text = header

        # Make header row font bold
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.bold = True

        # Add data rows
        for elem in rows:
            row_cells = table.add_row().cells # list of cells in the new row
            for i, header in enumerate(headers):
                attr_name = header_to_attr(header)
                cell_value = elem.get(attr_name, None)
                if cell_value is None:
                    logger.warning(
                        f"{tags.ROW!r} element is missing {attr_name!r} attribute for header {header!r}. "
                        "Using empty string as placeholder."
                    )
                    cell_value = ""
                    
                row_cells[i].text = cell_value
            
        
    @abstractmethod
    def render_section(self, document: Document):
        pass
    
