"""Default configuration values for file versioning features."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from .core_default_config import SoftwareComponents, XMLTag

@dataclass(frozen=True)  # frozen=True makes the instance immutable
class ExclusionRules:
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
class InclusionRules:
    """Rules that define which extensions are included in scanning.

    Attributes:
        extensions: File extensions accepted by default.
    """

    extensions: List[str] = field(default_factory=lambda: [
        ".c", ".h", ".ads", ".adb", ".asm", ".s"
    ])

@dataclass(frozen=True)
class Rules:
    """Container for inclusion and exclusion rule sets.

    Attributes:
        exclusion: Exclusion rule set.
        inclusion: Inclusion rule set.
    """

    exclusion: ExclusionRules = field(default_factory=ExclusionRules)
    inclusion: InclusionRules = field(default_factory=InclusionRules)

@dataclass(frozen=True)
class FileVersioningTag(XMLTag):
    """XML tags used by file versioning output.

    Attributes:
        ROW: XML tag name used for each file row.
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
    rules: Rules = field(default_factory=Rules)
    tags: FileVersioningTag = field(default_factory=FileVersioningTag)


# Singleton instance
"""CONFIG = FileVersioningDefaultConfig()

# Usage
print(CONFIG.root)
print(CONFIG.rules.exclusion.dirs)

# This raises an error (frozen=True)
# CONFIG.mode = "other"  # FrozenInstanceError"""