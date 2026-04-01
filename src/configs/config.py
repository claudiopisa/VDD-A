from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from configs.default_config.default_config_loader import DefaultConfigLoader
from configs.user_config.user_config_loader import UserConfigLoader
from utils.json_parser import DottedDict


class Config():
    """
    Base configuration class with automatic flattening and customizable reserved keys.
    
    Automatically flattens config data into class attributes, while protecting
    reserved keys from being overwritten.
    """
    
    # Reserved keys that should NOT be flattened into class attributes
    # Using frozenset to make it immutable (cannot be modified at runtime)
    RESERVED_KEYS: frozenset[str] = frozenset({'user_config', 'default_config', 'user_config_path'})
    
    def load_user_config(self, path: str | Path):
        """
        Load user configuration from file and apply it to the instance.
        
        Automatically flattens config data into class attributes (except reserved keys).
        
        Args:
            path: Path to the JSON configuration file
            
        Returns:
            DottedDict with the loaded configuration
        """
        config_data = UserConfigLoader.load(path)
        self._apply_and_validate_config(config_data)

        return config_data
    
    def _apply_and_validate_config(self, config_data: DottedDict) -> None:
        """
        Apply and validate configuration.
        
        Checks for conflicts between config keys and reserved keys.
        Raises ValueError if conflicts are found.
        
        Args:
            config_data: Configuration data to apply
            
        Raises:
            ValueError: If config keys conflict with reserved keys
        """
        reserved_keys = self._get_reserved_keys()
        config_keys = set(config_data.keys())
        conflicts = config_keys & reserved_keys
        
        if conflicts:
            raise ValueError(
                f"Configuration keys {conflicts} conflict with reserved keys. "
                f"Reserved keys: {reserved_keys}. "
                f"Rename these keys in your config file to avoid conflicts."
            )
        
        self._flatten_config(config_data)
    
    def _flatten_config(self, config_data: DottedDict) -> None:
        """
        Flatten configuration data into class attributes.
        
        Skips reserved keys defined in _get_reserved_keys().
        
        Args:
            config_data: Configuration data to flatten
        """
        reserved_keys = self._get_reserved_keys()

        for key, value in config_data.items():
            if key not in reserved_keys:
                self.__dict__[key] = value
    
    def _get_reserved_keys(self) -> frozenset[str]:
        """
        Get the frozenset of reserved keys that should NOT be flattened.
        
        Override RESERVED_KEYS in subclasses to add custom reserved keys.
        
        Returns:
            Frozenset of reserved key names (immutable)
            
        Example:
            class MyConfig(Config):
                RESERVED_KEYS = Config.RESERVED_KEYS | {'my_internal_data', 'cache'}
                
                # The | operator works with frozensets too!
        """
        return self.RESERVED_KEYS
    
    def load_default_config(self):
        """
        Load the default configuration for this config class.
        
        Uses DefaultConfigLoader to automatically determine and load
        the correct default config based on the class name.
        
        Returns:
            Instance of the corresponding default config class
        """
        return DefaultConfigLoader.load(self)