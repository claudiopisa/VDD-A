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
    
    def __str__(self):
        # Provide a compact, user-friendly view of the default configuration.
        payload = asdict(self)
        return f"{self.__class__.__name__}({json.dumps(payload, indent=2)})"

    def __repr__(self):
        return self.__str__()
# Singleton instance
#CONFIG = CoreDefaultConfig()

# Utilizzo
#print(CONFIG.roots.internal)  # ["NSPC"]
#print(CONFIG.components.NSPC)  # "NSPC"

# Questo solleverà un errore (frozen=True)
# CONFIG.roots.internal.append("test")  # Funziona ma modifica la lista (attenzione!)