"""Default core configuration values used by config classes.

This module contains immutable dataclasses that define structural defaults
shared across document-generation flows.
"""

from dataclasses import asdict, dataclass, field
from typing import Tuple, Dict, Any



@dataclass(frozen=True)
class SoftwareComponents:
    """Canonical software component identifiers.

    Attributes:
        SAFETY_NUCLEUS: Identifier for the safety nucleus component.
        KERNEL: Identifier for the kernel component.
        SIMULATOR: Identifier for the simulator component.
        NON_VITAL_ENV: Identifier for the non-vital environment component.
        NON_VITAL_TOOLS: Identifier for the non-vital tools component.
    """

    SAFETY_NUCLEUS:     str = "NSPC"
    KERNEL:             str = "NS_KERNEL"
    SIMULATOR:          str = "SIMNS"
    NON_VITAL_ENV:      str = "SWNV"
    NON_VITAL_TOOLS:    str = "NS_TOOLS"

    def __repr__(self):
        """Return a human-readable representation with usage example.

        Returns:
            str: Readable summary of available components.
        """
        return f"Available components(NSPC='{self.SAFETY_NUCLEUS}', NS_KERNEL='{self.KERNEL}', SIMNS='{self.SIMULATOR}', SWNV='{self.NON_VITAL_ENV}', TOOLS='{self.NON_VITAL_TOOLS}').\n Usage example: config_object.components.SAFETY_NUCLEUS to access the string 'NSPC'."

@dataclass(frozen=True)
class XMLTag:
    """Default XML tags used by rendered output.

    Attributes:
        PARAGRAPH: XML tag name for paragraph nodes.
        SUBPARAGRAPH: XML tag name for subparagraph nodes.
        TABLE: XML tag name for table nodes.
    """

    PARAGRAPH: str = "paragraph"
    SUBPARAGRAPH: str = "subparagraph"
    TABLE: str = "table"

@dataclass(frozen=True)
class XMLGeneratorConfig:
    """Configuration defaults for XML generation.

    Attributes:
        IDENTATION: Whether indentation is enabled in generated XML.
        INDENT_SPACE: Indentation token used when indentation is enabled.
        ENCODING: Output XML encoding.
        XML_DECLARATION: Whether to include XML declaration header.
        TAGS: Default XML tags container.
    """

    #ROOT_NAME: str = "default_root"
    IDENTATION: bool = True
    INDENT_SPACE: str = "  "
    ENCODING: str = "utf-8"
    XML_DECLARATION: bool = True
    TAGS: XMLTag = field(default_factory=XMLTag)

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
    xml_generator_config: XMLGeneratorConfig = field(default_factory=XMLGeneratorConfig)
    image_config_name: str = "Imgconf.ini"
    
    def __repr__(self):
        """Return a concise debug representation for the core defaults.

        Returns:
            str: String representation of core default settings.
        """
        return f"CoreDefaultConfig(components={asdict(self.components)}, image_config_name='{self.image_config_name}')"
    
# Singleton instance
#CONFIG = CoreDefaultConfig()

# Usage
#print(CONFIG.roots.internal)  # ["NSPC"]
#print(CONFIG.components.SAFETY_NUCLEUS)  # "NSPC"

# This raises an error (frozen=True)
# CONFIG.roots.internal.append("test")  # It works but still mutates the list (watch out!)