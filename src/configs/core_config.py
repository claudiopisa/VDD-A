#CoreConfig class inherites from Config abstract class 

from pathlib import Path

from configs.config import Config

class CoreConfig(Config):
    """
    Core configuration for VDD documents.
    
    Provides access to configuration data through:
    - self.user_config: User-specific configuration from JSON file (DottedDict with dot notation)
    - self.default_config: Static structural defaults (CoreDefaultConfig dataclass)
    
    Example usage:
        config = CoreConfig("config/core_config.json")
        
        # Access user configuration
        vdd_type = config.user_config.vdd_type
        stream_root = config.user_config.paths.stream_root
        
        # Access default configuration
        internal_roots = config.default_config.roots.internal
        components = config.default_config.components
    """
    
    def __init__(self, user_config_path: str | Path):
        self.user_config_path = user_config_path
        self.user_config = self.load_user_config(user_config_path)
        self.default_config = self.load_default_config()

    # User configuration properties for convenient access
    @property
    def vdd_type(self):
        return self.user_config.vdd_type
    
    @property
    def input_mode(self):
        return self.user_config.input_mode
    
    @property
    def stream_root(self):
        return self.user_config.paths.stream_root
    
    @property
    def output_dir(self):
        return self.user_config.paths.output_dir
    
    @property
    def rtc_cache_dir(self):
        return self.user_config.paths.rtc_cache_dir
    
    @property
    def document_name(self):
        return self.user_config.metadata.doc_name
    
    # Default configuration properties for convenient access
    @property
    def internal_root(self):
        return self.default_config.roots.internal
    
    @property
    def external_root(self):
        return self.default_config.roots.external
    
    @property
    def components(self):
        return self.default_config.components
    


