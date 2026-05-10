"""Default configuration package.

This package contains immutable, frozen dataclasses that define structural
defaults and constants for the VDD-A system. These are NOT user-configurable
values — they are compile-time constants such as:

- Component identifiers ("NSPC", "NS_KERNEL", etc.)
- Scanning rules (file extensions, excluded directories)
- Parser-specific field mappings ("NomeTask", "V1_FileTask", etc.)
- XML tag names ("paragraph", "subparagraph", "table")

Architecture:
    The defaults follow a hierarchical composition pattern (typically 3 levels):
    
        DefaultConfig
        ├─ simple_value: str
        ├─ component: SomeComponent
        └─ container: RuleSet
           ├─ rule1: Rule1
           └─ rule2: Rule2

Why frozen=True?
    All dataclasses use frozen=True to prevent accidental runtime mutations.
    Defaults must never change after initialization.

Usage:
    Clients should ALWAYS consume defaults via the Config interface
    (e.g., FileVersioningConfig, TaskVersioningConfig) rather than directly.
    
    ✓  config.excluded_dirs  (via FileVersioningConfig property)
    ✗  config.default_config.rules.exclusion.dirs  (verbose direct access)
    
    The Config interface flattens the hierarchy, eliminating verbosity.

See Also:
    - DEFAULT_CONFIG_ARCHITECTURE.md: Complete design rationale and patterns
    - USAGE_EXAMPLES.md: Practical code examples
    - README_DEFAULT_CONFIG_LOADER.md: How defaults are auto-discovered
"""

from .default_config_loader import DefaultConfigLoader
from .core_default_config import CoreDefaultConfig
from .file_versioning_default_config import FileVersioningDefaultConfig
from .task_versioning_default_config import TaskVersioningDefaultConfig

__all__ = [
	"DefaultConfigLoader",
	"CoreDefaultConfig",
	"FileVersioningDefaultConfig",
	"TaskVersioningDefaultConfig",
]