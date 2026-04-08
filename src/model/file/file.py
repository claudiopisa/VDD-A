from dataclasses import dataclass
from typing import ClassVar
#from ..entry import Entry
from model import Entry

@dataclass
class File(Entry):
    path: str
    version: str | None

    # Static attribute. Keeps track of the max length of each field across all File instances, used for formatting the output in a clean way.
    # key string values must be the exact same as the attribute class names 
    _length_cache: ClassVar[dict[str, int]] = {
        "path": len("PATH"),
        "version": len("VERSION"),
    }
