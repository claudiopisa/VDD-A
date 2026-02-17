import json
from dataclasses import asdict, dataclass, field
from typing import Tuple, Dict, Any

@dataclass(frozen=True)
class Roots:
    #internal: List[str] = field(default_factory=lambda: ("NSPC",))
    #internal: Union[str, List[str]] = "NSPC" # se si vuole opzionalemnte una lista o una stringa
    internal: str               = "NSPC"
    external: Tuple[str, ...]   = field(default_factory=lambda: ("NSPC", "NS_KERNEL"))

@dataclass(frozen=True)
class Components:
    NSPC:       str = "NSPC"
    NS_KERNEL:  str = "NS_KERNEL"
    SWNV:       str = "SWNV"
    TOOLS:      str = "NS_TOOLS"

    def __repr__(self):
        return f"Available components(NSPC='{self.NSPC}', NS_KERNEL='{self.NS_KERNEL}', SWNV='{self.SWNV}', TOOLS='{self.TOOLS}').\n Usage example: config_object.components.NSPC to access the string 'NSPC'."

@dataclass(frozen=True)
class CoreDefaultConfig:
    """
    Default configuration for Core VDD documents.
    
    Contains only structural/static defaults (roots, components).
    User-specific config (paths, metadata, vdd_type, input_mode) 
    come from JSON files and should NOT be in this default config.
    """
    # Structural defaults
    roots:      Roots       = field(default_factory=Roots)
    components: Components  = field(default_factory=Components)
    
    def __repr__(self):
        return f"CoreDefaultConfig(roots={asdict(self.roots)}, components={asdict(self.components)})"
    
# Singleton instance
#CONFIG = CoreDefaultConfig()

# Utilizzo
#print(CONFIG.roots.internal)  # ["NSPC"]
#print(CONFIG.components.NSPC)  # "NSPC"

# Questo solleverà un errore (frozen=True)
# CONFIG.roots.internal.append("test")  # Funziona ma modifica la lista (attenzione!)