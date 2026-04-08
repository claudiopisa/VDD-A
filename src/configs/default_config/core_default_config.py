import json
from dataclasses import asdict, dataclass, field
from typing import Tuple, Dict, Any



@dataclass(frozen=True)
class SoftwareComponents:
    SAFETY_NUCLEUS:     str = "NSPC"
    KERNEL:             str = "NS_KERNEL"
    SIMULATOR:          str = "SIMNS"
    NON_VITAL_ENV:      str = "SWNV"
    NON_VITAL_TOOLS:    str = "NS_TOOLS"

    def __repr__(self):
        return f"Available components(NSPC='{self.SAFETY_NUCLEUS}', NS_KERNEL='{self.KERNEL}', SIMNS='{self.SIMULATOR}', SWNV='{self.NON_VITAL_ENV}', TOOLS='{self.NON_VITAL_TOOLS}').\n Usage example: config_object.components.SAFETY_NUCLEUS to access the string 'NSPC'."

@dataclass(frozen=True)
class CoreDefaultConfig:
    """
    Default configuration for Core VDD documents.
    
    Contains only structural/static defaults (roots, components).
    User-specific coWnfig (paths, metadata, vdd_type, input_mode) 
    come from JSON files and should NOT be in this default config.
    """
    # Structural defaults
    #roots:      Roots       = field(default_factory=Roots)
    components: SoftwareComponents  = field(default_factory=SoftwareComponents)
    image_config_name: str = "Imgconf.ini"
    
    def __repr__(self):
        return f"CoreDefaultConfig(roots={asdict(self.roots)}, components={asdict(self.components)}, image_config_name='{self.image_config_name}')"
    
# Singleton instance
#CONFIG = CoreDefaultConfig()

# Usage
#print(CONFIG.roots.internal)  # ["NSPC"]
#print(CONFIG.components.NSPC)  # "NSPC"

# This raises an error (frozen=True)
# CONFIG.roots.internal.append("test")  # It works but still mutates the list (watch out!)