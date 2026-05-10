"""Default configuration values for file versioning features."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from .core_default_config import SoftwareComponents, Tag

@dataclass(frozen=True)  # frozen=True makes the instance immutable
class ExclusionRule:
    """Rules that exclude directories/files from file version scanning.

    Attributes:
        dirs: Directory names that are always excluded.
        dirs_contains: Directory path fragments that trigger exclusion.
        files: Specific file names that are excluded.
        path_ext_blacklist: Path-based extension blacklists.
    """

    dirs: List[str] = field(default_factory=lambda: [
        "Protocols_win32", ".vscode", "BIN", "INCMAKE", 
        "MakeBatches", "SWIXL", "LIB", "EXE", "OBJ", "DEPS"
    ])

    dirs_contains: List[str] = field(default_factory=lambda: ["AdaTask"])
    
    files: List[str] = field(default_factory=lambda: [
        "resource.h", "Loader.c", "boot.asm", "bootAP.asm"
    ])
    
    path_ext_blacklist: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"path_contains": "SONS-RTS", "extensions": [".ads", ".adb"]}
    ])

@dataclass(frozen=True)
class InclusionRule:
    """Rules that define which extensions are included in scanning.

    Attributes:
        extensions: File extensions accepted by default.
    """

    extensions: List[str] = field(default_factory=lambda: [
        ".c", ".h", ".ads", ".adb", ".asm", ".s"
    ])

@dataclass(frozen=True)
class Rule:
    """Container for inclusion and exclusion rule sets.

    Attributes:
        exclusion: Exclusion rule set.
        inclusion: Inclusion rule set.
    """

    exclusion: ExclusionRule = field(default_factory=ExclusionRule)
    inclusion: InclusionRule = field(default_factory=InclusionRule)

@dataclass(frozen=True)
class FileVersioningTag(Tag):
    """Tags used by file versioning output.

    Attributes:
        ROW: Tag name used for each file row.
    """

    ROW: str = "file"


@dataclass(frozen=True)
class FileVersioningDefaultConfig:
    """
    Default configuration for file versioning operations.
    
    Contains only structural/static rules.
    User-specific config (version_extraction_criteria, mode, metadata)
    come from JSON files and should NOT be in this default config.
    """
    #root: List[str] = field(default_factory=lambda: ["NSPC"])
    root: str = SoftwareComponents.SAFETY_NUCLEUS
    version_extraction_criteria: str = r"(?:\\\\*|//|--|;|#).*Versione\s*:?\\s*(\d+\.\d+)" 
    rules: Rule = field(default_factory=Rule)
    tags: FileVersioningTag = field(default_factory=FileVersioningTag)


# Singleton instance
"""CONFIG = FileVersioningDefaultConfig()

# Usage
print(CONFIG.root)
print(CONFIG.rules.exclusion.dirs)

# This raises an error (frozen=True)
# CONFIG.mode = "other"  # FrozenInstanceError"""