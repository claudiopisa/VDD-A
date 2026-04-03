from dataclasses import dataclass
from typing import ClassVar


@dataclass
class File:
    path: str
    version: str

    # Static attribute. Keeps track of the max length of each field across all Task instances, used for formatting the output in a clean way.
    # key string values must be the exact same as the attribute class names 
    _length_cache: ClassVar[dict[str, int]] = {
        "path": len("PATH"),
        "version": len("VERSION")
    }

     # Special method called automatically after the dataclass __init__ method, used to update
    # the max length of each field in the _length_cache dictionary every time a new Task
    # instance is created.
    def __post_init__(self):
        """Aggiorna i max ogni volta che un File viene creato."""
        for key, current_max in File._length_cache.items():
            File._length_cache[key] = max(current_max, len(str(getattr(self, key))))