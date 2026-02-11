from dataclasses import dataclass, field
from typing import Tuple, Dict

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
    roots:      Roots       = field(default_factory=Roots)
    components: Components  = field(default_factory=Components)

# Singleton instance
#CONFIG = CoreDefaultConfig()

# Utilizzo
#print(CONFIG.roots.internal)  # ["NSPC"]
#print(CONFIG.components.NSPC)  # "NSPC"

# Questo solleverà un errore (frozen=True)
# CONFIG.roots.internal.append("test")  # Funziona ma modifica la lista (attenzione!)