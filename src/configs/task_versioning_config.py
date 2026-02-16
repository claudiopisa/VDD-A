# TaskVersioningConfig class inherits from Config abstract class

from pathlib import Path
from configs.config import Config


class TaskVersioningConfig(Config):
    """
    Configuration for task versioning operations.
    
    Automatically loads TaskVersioningDefaultConfig through DefaultConfigLoader.
    
    Provides access to configuration data through:
    - self.user_config: User-specific configuration from JSON file (DottedDict)
    - self.default_config: Static structural defaults (TaskVersioningDefaultConfig dataclass)
    
    Example usage:
        config = TaskVersioningConfig("config/task_versioning.json")
        
        # Access user configuration
        kernel_mode = config.user_config.kernel_mode
        prev_enabled = config.user_config.previous_release.enabled
        title = config.user_config.metadata.title
        
        # Access default configuration
        component_roots = config.default_config.component_roots
    """
    
    def __init__(self, user_config_path: str | Path):
        self.user_config_path = user_config_path
        self.user_config = self.load_user_config(user_config_path)
        # DefaultConfigLoader will automatically load TaskVersioningDefaultConfig
        self.default_config = self.load_default_config()

