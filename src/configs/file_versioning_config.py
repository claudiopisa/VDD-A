# FileVersioningConfig class inherits from Config abstract class

from pathlib import Path
from configs.config import Config


class FileVersioningConfig(Config):
    """
    Configuration for file versioning operations.
    
    Automatically loads FileVersioningDefaultConfig through DefaultConfigLoader.
    
    Provides access to configuration data through:
    - self.user_config: User-specific configuration from JSON file (DottedDict)
    - self.default_config: Static structural defaults (FileVersioningDefaultConfig dataclass)
    
    Example usage:
        config = FileVersioningConfig("config/file_versioning.json")
        
        # Access user configuration
        mode = config.user_config.mode
        pattern = config.user_config.version_extraction_criteria
        title = config.user_config.metadata.title
        
        # Access default configuration
        component_roots = config.default_config.component_roots
        extensions = config.default_config.allowed_extensions
    """
    
    def __init__(self, user_config_path: str | Path):
        self.user_config_path = user_config_path
        self.user_config = self.load_user_config(user_config_path)
        # DefaultConfigLoader will automatically load FileVersioningDefaultConfig
        self.default_config = self.load_default_config()

