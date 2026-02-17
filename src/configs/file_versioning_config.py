# FileVersioningConfig class inherits from Config abstract class

from pathlib import Path
from configs.config import Config
from configs.default_config.file_versioning_default_config import FileVersioningDefaultConfig, Rules, ExclusionRules, InclusionRules


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

    @property
    def root(self):
        return self.default_config.root
    
    @property
    def exclusion_rules(self):
        return self.default_config.rules.exclusion
    
    @property
    def inclusion_rules(self):
        return self.default_config.rules.inclusion
    
    @property
    def allowed_extensions(self):
        return self.default_config.rules.inclusion.extensions
    
    @property
    def excluded_dirs(self):
        return self.default_config.rules.exclusion.dirs
    
    @property
    def excluded_dirs_contains(self):
        return self.default_config.rules.exclusion.dirs_contains
    
    @property
    def excluded_files(self):
        return self.default_config.rules.exclusion.files
    
    @property
    def excluded_path_ext(self):
        return self.default_config.rules.exclusion.path_ext_blacklist
    
    @property
    def version_extraction_criteria(self):
        return self.user_config.version_extraction_criteria
    
    @property
    def mode(self):
        return self.user_config.mode
    
    @property
    def metadata(self):
        metadata_str = ""
        for key, value in self.user_config.metadata.items():
            metadata_str += f"{key}: {value}\n"

        return metadata_str
    
    @property
    def title(self):
        return self.user_config.metadata.title
    
    @property
    def columns_name(self):
        return self.user_config.metadata.columns_name
    
    def __repr__(self):
        pretty_print_str_user = "File Versioning User Configuration:\n"

        for key, value in self.user_config.items():
            if isinstance(value, dict):
                pretty_print_str_user += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    pretty_print_str_user += f"\t{sub_key}:\t{sub_value}\n"
            else:
                pretty_print_str_user += f"{key}:\t{value}\n"

        pretty_print_str_default = "\nFile Versioning Default Configuration:\n"
        
        for key, value in self.default_config.__dict__.items():
            if isinstance(value, Rules):
                pretty_print_str_default += f"{key}:\n"

                for sub_key, sub_value in value.__dict__.items():

                    if isinstance(sub_value, ExclusionRules) or isinstance(sub_value, InclusionRules):
                        pretty_print_str_default += f"\t{sub_key}:\n"

                        for sub_sub_key, sub_sub_value in sub_value.__dict__.items():
                            pretty_print_str_default += f"\t\t{sub_sub_key}:\t{sub_sub_value}\n"
                    else:
                        pretty_print_str_default += f"\t{sub_key}:\t{sub_value}\n"
            else:
                pretty_print_str_default += f"{key}:\t{value}\n"
        
        return pretty_print_str_user + pretty_print_str_default
