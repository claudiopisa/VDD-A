from dataclasses import asdict, dataclass, field
from typing import List, Tuple

from configs.default_config.core_default_config import SoftwareComponents


@dataclass(frozen=True)
class Roots:
    #internal: List[str] = field(default_factory=lambda: ("NSPC",))
    #internal: Union[str, List[str]] = "NSPC" # se si vuole opzionalemnte una lista o una stringa
    
    internal: SoftwareComponents    = field(default_factory=lambda: SoftwareComponents.SAFETY_NUCLEUS)
    external: Tuple[str, ...]       = field(default_factory=lambda: (SoftwareComponents.SAFETY_NUCLEUS, SoftwareComponents.SAFETY_NUCLEUS_KERNEL))

    #old way
    #internal: str               = "NSPC"
    #external: Tuple[str, ...]   = field(default_factory=lambda: ("NSPC", "NS_KERNEL"))
    
@dataclass(frozen=True)
class TaskVersioningDefaultConfig:
    """
    Default configuration for task versioning operations.
    
    Contains only structural/static defaults.
    User-specific config (kernel_mode, previous_release, metadata)
    come from JSON files and should NOT be in this default config.
    """
    
    # Structural defaults
    #component_roots: List[str] = field(default_factory=lambda: ["NSPC"])
    roots: Roots = field(default_factory=Roots)

    def __repr__(self):
        return f"TaskVersioningDefaultConfig(roots={asdict(self.roots)})"