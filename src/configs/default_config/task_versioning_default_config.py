from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TaskVersioningDefaultConfig:
    """
    Default configuration for task versioning operations.
    
    Contains only structural/static defaults.
    User-specific config (kernel_mode, previous_release, metadata)
    come from JSON files and should NOT be in this default config.
    """
    
    # Structural defaults
    component_roots: List[str] = field(default_factory=lambda: ["NSPC"])

    def __repr__(self):
        return f"TaskVersioningDefaultConfig(component_roots={self.component_roots})"