from dataclasses import dataclass, field
from typing import List, Dict
from .core_default_config import SoftwareComponents, XMLTag

@dataclass(frozen=True)  # frozen=True makes the instance immutable
class ExclusionRules:
    dirs: List[str] = field(default_factory=lambda: [
        "Protocols_win32", ".vscode", "BIN", "INCMAKE", 
        "MakeBatches", "SWIXL", "LIB", "EXE", "OBJ", "DEPS"
    ])

    dirs_contains: List[str] = field(default_factory=lambda: ["AdaTask"])
    
    files: List[str] = field(default_factory=lambda: [
        "resource.h", "Loader.c", "boot.asm", "bootAP.asm"
    ])
    
    path_ext_blacklist: List[Dict[str, any]] = field(default_factory=lambda: [
        {"path_contains": "SONS-RTS", "extensions": [".ads", ".adb"]}
    ])

@dataclass(frozen=True)
class InclusionRules:
    extensions: List[str] = field(default_factory=lambda: [
        ".c", ".h", ".ads", ".adb", ".asm", ".s"
    ])

@dataclass(frozen=True)
class Rules:
    exclusion: ExclusionRules = field(default_factory=ExclusionRules)
    inclusion: InclusionRules = field(default_factory=InclusionRules)

@dataclass(frozen=True)
class FileVersioningTag(XMLTag):
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