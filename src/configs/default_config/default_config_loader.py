"""
DefaultConfigLoader - Automatically loads the correct default configuration
based on the config class type.
"""

from typing import Type, Dict, Any
import re


class DefaultConfigLoader:
    """
    Loads default configuration instances based on the config class name.
    
    Maps config classes to their corresponding default config classes:
    - CoreConfig -> CoreDefaultConfig
    - FileVersioningConfig -> FileVersioningDefaultConfig
    - TaskVersioningConfig -> TaskVersioningDefaultConfig
    """
    
    # Registry to store manual mappings if needed
    _registry: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, config_class_name: str, default_config_class: Type):
        """
        Manually register a mapping between a config class and its default config.
        
        Args:
            config_class_name: Name of the config class (e.g., 'CoreConfig')
            default_config_class: The default config class to instantiate
        """
        cls._registry[config_class_name] = default_config_class
    
    @classmethod
    def load(cls, config_instance: Any) -> Any:
        """
        Load and return the appropriate default config instance.
        
        Args:
            config_instance: Instance of a Config subclass
            
        Returns:
            Instance of the corresponding default config class
            
        Raises:
            ImportError: If the default config class cannot be imported
            ValueError: If no default config exists for the given class
        """
        config_class_name = config_instance.__class__.__name__
        
        # Check if manually registered
        if config_class_name in cls._registry:
            default_config_class = cls._registry[config_class_name] # returns the actual class object, of type `type`
            return default_config_class()
        
        # Auto-resolve based on naming convention
        return cls._auto_resolve(config_class_name)
    
    @classmethod
    def _auto_resolve(cls, config_class_name: str) -> Any:
        """
        Automatically resolve the default config class based on naming convention.
        
        Convention: XyzConfig -> XyzDefaultConfig
        
        Args:
            config_class_name: Name of the config class
            
        Returns:
            Instance of the default config class
            
        Raises:
            ImportError: If the default config module cannot be imported
            ValueError: If the config class doesn't follow naming conventions
        """
        # Remove 'Config' suffix and convert to snake_case for module name
        if not config_class_name.endswith('Config'):
            raise ValueError(
                f"Config class '{config_class_name}' must end with 'Config'"
            )
        
        # Extract the base name (e.g., 'Core' from 'CoreConfig')
        base_name = config_class_name[:-6]  # Remove 'Config'
        
        # Convert to snake_case for module name
        module_name = cls._camel_to_snake(base_name) + '_default_config'
        
        # Construct default config class name
        default_class_name = base_name + 'DefaultConfig'
        
        # Dynamic import
        try:
            module = __import__(
                f'configs.default_config.{module_name}',
                fromlist=[default_class_name]
            )
            default_config_class = getattr(module, default_class_name)
            return default_config_class()
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Could not load default config for '{config_class_name}'. "
                f"Expected class '{default_class_name}' in module "
                f"'configs.default_config.{module_name}'. Error: {e}"
            )
    
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """
        Convert CamelCase to snake_case.
        
        Args:
            name: CamelCase string
            
        Returns:
            snake_case string
        """
        # Insert underscore before uppercase letters and convert to lowercase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
