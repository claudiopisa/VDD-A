#CoreConfig class inherites from Config abstract class 

from pathlib import Path

from configs.config import Config
from configs.default_config.core_default_config import SoftwareComponents

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
    def kernel_mode(self):
        return self.user_config.kernel_mode
    
    @property
    def is_kernel_internal(self):
        return self.kernel_mode == "internal"
    
    @property
    def stream_root_as_path(self) -> Path:
        stream_root = self.stream_root
        if stream_root is not None:
            return Path(stream_root)
        
        return None
    
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
    
    @property
    def image_config_name(self):
        return self.default_config.image_config_name
    
    def __repr__(self):
        pretty_print_str_user = "User Core Configuration:\n"

        for key, value in self.user_config.items():
            if isinstance(value, dict):
                pretty_print_str_user += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    pretty_print_str_user += f"\t{sub_key}:\t{sub_value}\n"
            else:
                pretty_print_str_user += f"{key}:\t{value}\n"
        
        pretty_print_str_default = "\nDefault Core Configuration:\n"

        for key, value in self.default_config.__dict__.items():
            if isinstance(value, Roots) or isinstance(value, SoftwareComponents):
                pretty_print_str_default += f"{key}:\n"
                for sub_key, sub_value in value.__dict__.items():
                    pretty_print_str_default += f"\t{sub_key}:\t{sub_value}\n"
            else:
                pretty_print_str_default += f"{key}:\t{value}\n"
        
        return pretty_print_str_user + pretty_print_str_default
