# DefaultConfigLoader - Automatic Default Configuration Loading

## Overview

The `DefaultConfigLoader` class automatically loads the correct default configuration based on your config class name. No manual imports or mappings needed!

## How It Works

### Naming Convention

The loader follows this simple pattern:
- `XyzConfig` → `XyzDefaultConfig`
- Module: `xyz_config.py` → `default_config/xyz_default_config.py`

### Examples:
- `CoreConfig` → `CoreDefaultConfig` (from `core_default_config.py`)
- `FileVersioningConfig` → `FileVersioningDefaultConfig` (from `file_versioning_default_config.py`)
- `TaskVersioningConfig` → `TaskVersioningDefaultConfig` (from `task_versioning_default_config.py`)

## Usage

### 1. Create Your Config Class

Inherit from `Config` base class:

```python
from pathlib import Path
from configs.config import Config
from ConfigLoader.user_config_loader import UserConfigLoader

class MyFeatureConfig(Config):
    def __init__(self, user_config_path: str | Path):
        self.user_config_path = user_config_path
        self.user_config = self.load_user_config(user_config_path)
        # Automatically loads MyFeatureDefaultConfig!
        self.default_config = self.load_default_config()

    def load_user_config(self, path: str | Path):
        self.user_config = UserConfigLoader(path)
        return self.user_config
```

### 2. Create Your Default Config Class

Create a file `configs/default_config/my_feature_default_config.py`:

```python
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class MyFeatureDefaultConfig:
    setting_1: str = "default_value"
    setting_2: List[str] = field(default_factory=lambda: ["item1", "item2"])
    enabled: bool = True
```

### 3. Use It!

```python
from configs.my_feature_config import MyFeatureConfig

config = MyFeatureConfig(user_config_path="config/my_feature.json")

# Access default configuration
print(config.default_config.setting_1)  # "default_value"
print(config.default_config.setting_2)  # ["item1", "item2"]
```

## Benefits

1. **Automatic Resolution**: No need to manually import default config classes
2. **Convention over Configuration**: Follow naming conventions, everything works automatically
3. **Type Safety**: Each config class has its strongly-typed default config
4. **Maintainable**: Add new configs without modifying the loader
5. **Clear Structure**: Naming convention makes relationships obvious

## Advanced: Manual Registration

If you need custom mappings that don't follow the convention:

```python
from configs.default_config_loader import DefaultConfigLoader
from configs.default_config.special_default_config import SpecialDefaultConfig

# Register a custom mapping
DefaultConfigLoader.register('MySpecialConfig', SpecialDefaultConfig)
```

## File Structure

```
src/configs/
├── config.py                          # Base Config class
├── default_config_loader.py           # DefaultConfigLoader class
├── core_config.py                     # CoreConfig
├── file_versioning_config.py          # FileVersioningConfig
├── task_versioning_config.py          # TaskVersioningConfig
└── default_config/
    ├── core_default_config.py         # CoreDefaultConfig
    ├── file_versioning_default_config.py  # FileVersioningDefaultConfig
    └── task_versioning_default_config.py  # TaskVersioningDefaultConfig
```

## The Magic Behind It

The `Config` base class has a `load_default_config()` method that:
1. Gets the current class name (e.g., `FileVersioningConfig`)
2. Removes the `Config` suffix → `FileVersioning`
3. Converts to snake_case → `file_versioning`
4. Adds `_default_config` → `file_versioning_default_config`
5. Imports from `configs.default_config.file_versioning_default_config`
6. Instantiates `FileVersioningDefaultConfig`
7. Returns the instance

All of this happens automatically when you call `self.load_default_config()`!

## Testing

Run the demo:
```bash
cd src
python demo_default_config_loader.py
```

## Requirements

- Python 3.10+ (uses `str | Path` union type hints)
- Config classes must end with `Config`
- Default config modules must exist in `configs/default_config/`
- Default config classes must end with `DefaultConfig`
