"""
Example demonstrating the DefaultConfigLoader pattern.

This shows how different Config classes automatically load their
corresponding default configurations.
"""

from configs.core_config import CoreConfig
from configs.file_versioning_config import FileVersioningConfig
from configs.task_versioning_config import TaskVersioningConfig


def demo_default_config_loader():
    """Demonstrate automatic default config loading."""
    
    # Example 1: CoreConfig automatically loads CoreDefaultConfig
    print("=" * 60)
    print("Example 1: CoreConfig")
    print("=" * 60)
    core_config = CoreConfig(user_config_path="config/core_config.json")
    print(f"Config class: {core_config.__class__.__name__}")
    print(f"Default config class: {core_config.default_config.__class__.__name__}")
    print(f"Default config data: {core_config.default_config}")
    print()
    
    # Example 2: FileVersioningConfig automatically loads FileVersioningDefaultConfig
    print("=" * 60)
    print("Example 2: FileVersioningConfig")
    print("=" * 60)
    file_config = FileVersioningConfig(user_config_path="config/file_versioning.json")
    print(f"Config class: {file_config.__class__.__name__}")
    print(f"Default config class: {file_config.default_config.__class__.__name__}")
    print(f"Default config data: {file_config.default_config}")
    print(f"  - Component roots: {file_config.default_config.component_roots}")
    print(f"  - Mode: {file_config.default_config.mode}")
    print(f"  - Allowed extensions: {file_config.default_config.allowed_extensions}")
    print()
    
    # Example 3: TaskVersioningConfig automatically loads TaskVersioningDefaultConfig
    print("=" * 60)
    print("Example 3: TaskVersioningConfig")
    print("=" * 60)
    task_config = TaskVersioningConfig(user_config_path="config/task_versioning.json")
    print(f"Config class: {task_config.__class__.__name__}")
    print(f"Default config class: {task_config.default_config.__class__.__name__}")
    print(f"Default config data: {task_config.default_config}")
    print()
    
    # Show the naming convention
    print("=" * 60)
    print("Naming Convention")
    print("=" * 60)
    print("CoreConfig          -> CoreDefaultConfig")
    print("FileVersioningConfig -> FileVersioningDefaultConfig")
    print("TaskVersioningConfig -> TaskVersioningDefaultConfig")
    print()
    print("Pattern: XyzConfig -> XyzDefaultConfig")
    print("Module:  xyz_config.py -> xyz_default_config.py (in default_config/)")


if __name__ == "__main__":
    demo_default_config_loader()
