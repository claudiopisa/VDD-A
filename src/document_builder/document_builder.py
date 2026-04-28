from typing import IO, Iterable

from docx import Document
from document_builder.renderer.renderer import Renderer
from pathlib import Path
from datetime import datetime
from utils import get_logger

logger = get_logger(__name__)

class DocumentBuilder:
    def __init__(self, template: str | IO[bytes] | None = None, output_path: str | Path | None = None):
        self.document = Document(template) # Note: `Document` can accept `None` as a template, in which case it creates a blank document.

        if output_path is not None and not isinstance(output_path, Path):
            output_path = Path(output_path)
        self.output_path = output_path

        #self.renderer: Renderer | None = None

    def set_renderer(self, renderer: Renderer):
        self.renderer = renderer
        return self

    def add_section(self, renderer: Renderer):
        renderer.render_section(self.document)

        return self

    #def generate_many(self, renderers: Iterable[Renderer]):
     #   for renderer in renderers:
      #      self.add_chapter(renderer)
      # return self

    def save(self, overwrite: bool = False):
        if self.output_path is None:
            # if output_path not defined, save in current directory
            self.output_path = Path.cwd() / f"Document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        if overwrite:
            save_path = self.output_path
        else:
            # Simple, cheap strategy: append a short timestamp suffix.
            suffix = datetime.now().strftime("_%Y%m%d_%H%M%S")
            save_path = self.output_path.with_name(f"{self.output_path.stem}{suffix}{self.output_path.suffix}")

        self.document.save(str(save_path))

        return save_path