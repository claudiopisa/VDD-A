from dataclasses import dataclass
from typing import ClassVar


@dataclass
class File:
    path: str
    version: str | None

    # Static attribute. Keeps track of the max length of each field across all Task instances, used for formatting the output in a clean way.
    # key string values must be the exact same as the attribute class names 
    _length_cache: ClassVar[dict[str, int]] = {
        "path": len("PATH"),
        "version": len("VERSION"),
    }

     # Special method called automatically after the dataclass __init__ method, used to update
    # the max length of each field in the _length_cache dictionary every time a new File
    # instance is created.
    def __post_init__(self):
        """Aggiorna i max ogni volta che un File viene creato."""
        values = {
            "path": self.path,
            "version": "" if self.version is None else str(self.version),
        }
        for key, current_max in File._length_cache.items():
            File._length_cache[key] = max(current_max, len(values[key]))

    @classmethod
    def reset_length_cache(cls) -> None:
        cls._length_cache = {
            "path": len("PATH"),
            "version": len("VERSION"),
        }

    @classmethod
    def format_row(cls, path: str, version: str | None) -> str:
        gap = "  "
        value = "" if version is None else str(version)
        return (
            f"{path:<{cls._length_cache['path']}}"
            f"{gap}{value:<{cls._length_cache['version']}}"
        )

    @classmethod
    def format_header_row(cls, path: str, version: str) -> str:
        gap = "  "
        return (
            f"{path:^{cls._length_cache['path']}}"
            f"{gap}{version:^{cls._length_cache['version']}}"
        )

    def __iter__(self):
        # Backward compatibility with existing tuple consumers: (path, version)
        yield self.path
        yield self.version

    def __repr__(self):
        return File.format_row(self.path, self.version)