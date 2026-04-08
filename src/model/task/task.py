from dataclasses import dataclass
from typing import ClassVar
from model import Entry


@dataclass
class Task(Entry):
    name: str
    type_: str
    version: str
    modified: str = "N/A"  # per ora non hai baseline precedente

    # Static attribute. Keeps track of the max length of each field across all Task instances, used for formatting the output in a clean way.
    # key string values must be the exact same as the attribute class names 
    _length_cache: ClassVar[dict[str, int]] = {
        "name": len("NAME"),
        "type_": len("TYPE"),
        "version": len("VERSION"),
        "modified": len("MODIFIED"),
    }

    # Special method called automatically after the dataclass __init__ method, used to update
    # the max length of each field in the _length_cache dictionary every time a new Task
    # instance is created.
    #def __post_init__(self):
     #   """Aggiorna i max ogni volta che un Task viene creato."""
      #  for key, current_max in Task._length_cache.items():
       #     Task._length_cache[key] = max(current_max, len(str(getattr(self, key))))
