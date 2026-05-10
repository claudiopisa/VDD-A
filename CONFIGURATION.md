# Configuration Guide

VDD-A uses a **two-level configuration system** to separate what the user provides from what the code keeps as static defaults.

- **User config**: JSON input under `config/`, edited per document or environment.
- **Default config**: immutable Python dataclasses under `src/configs/default_config/`, used as versioned constants and parsing rules.

## Overview

```
┌─────────────────────────────────────────┐
│     User Configuration (JSON files)     │  ← What the user provides
│   config/core_config.json               │  ← Paths, metadata, modes
│   config/file_versioning.json           │
│   config/task_versioning.json           │
└────────────────┬────────────────────────┘
                 │ loaded by
                 ↓
┌─────────────────────────────────────────┐
│   XyzConfig classes                     │  ← Runtime config objects
│   CoreConfig                            │  ← Merge user + default
│   FileVersioningConfig                  │  ← Provide accessors
│   TaskVersioningConfig                  │
└────────────────┬────────────────────────┘
                 │ contains
                 ↓
         ┌───────────────┐
         │               │
    ┌────┴────┐    ┌─────┴──────┐
    │          │    │            │
User Config  Default Config   Defaults are immutable
(mutable)    (frozen dataclass) structural constants
    │          │    │            │
    │          │    └─────┬──────┘
    │          │          │
    └────┬─────┴──────┬───┘
         │ properties │
         ↓            ↓
    Config object exposes both
    - user_config: JsonParser for user input
    - default_config: Dataclass for static rules
```

## Layer 1: User Configuration (JSON Files)

**Location**: `config/` directory (at root level)

**Purpose**: User-provided input that varies per document/environment

**Characteristics**:
- Mutable (can be changed by editing JSON files)
- Environment-specific (paths, metadata, mode settings)
- Validates paths exist
- Provides document-specific parameters

### `core_config.json`

Core settings shared across all versioning operations.

```json
{
    "vdd_type": "vital",
    "input_mode": "localSource",
    "kernel_mode": "internal",
    "paths": {
        "stream_root": "C:\\path\\to\\source\\tree",
        "output_dir": "C:\\path\\to\\output",
        "rtc_cache_dir": "C:\\path\\to\\cache"
    },
    "metadata": {
        "doc_name": "VDD Document Title"
    }
}
```

| Key | Values | Purpose |
|---|---|---|
| `vdd_type` | `"vital"` \| `"non_vital"` | Document classification |
| `input_mode` | `"localSource"` | How source data is provided (future: could be remote) |
| `kernel_mode` | `"internal"` \| `"external"` | Kernel architecture → affects task parsing paths |
| `paths.stream_root` | Absolute path | Root of source tree to scan |
| `paths.output_dir` | Absolute path | Where to write `.docx` output |
| `paths.rtc_cache_dir` | Absolute path | Cache directory for optimizations |
| `metadata.doc_name` | String | Human-readable document title |

### `file_versioning.json`

Configuration for Chapter 2 (file versioning).

```json
{
    "mode": "version",
    "version_extraction_criteria": "Versione:\\s*(\\d+\\.\\d+)",
    "metadata": {
        "title": "LIST OF WSPHS+ SW FILES AND RELEVANT VERSIONS",
        "columns_name": ["Name", "Version"]
    }
}
```

| Key | Purpose |
|---|---|
| `mode` | Version extraction method (`"version"` is the only supported mode) |
| `version_extraction_criteria` | Regex pattern to extract version from source code comments |
| `metadata.title` | Chapter title in the Word document |
| `metadata.columns_name` | Column header names in the output table |

### `task_versioning.json`

Configuration for Chapter 3 (task versioning).

```json
{
    "previous_release": {
        "enabled": true,
        "root": "C:\\path\\to\\previous\\release",
        "version": "1.0"
    },
    "metadata": {
        "title": "TASK LIST",
        "columns_name": ["Name", "Type", "Version", "Modified"]
    },
    "app_tasks": ["ixl.ini", "srlw.ini"]
}
```

| Key | Purpose |
|---|---|
| `previous_release.enabled` | Whether to compare against a baseline release |
| `previous_release.root` | Path to previous release stream root |
| `previous_release.version` | Version label for the baseline |
| `metadata.title` | Chapter title in the Word document |
| `metadata.columns_name` | Column header names (typically includes "Modified" status) |
| `app_tasks` | List of `.ini` files to parse for application tasks |

---

## Layer 2: Default Configuration (Immutable Dataclasses)

**Location**: `src/configs/default_config/` directory

**Purpose**: Static structural constants and rules that never change at runtime

**Characteristics**:
- Immutable (`frozen=True` dataclasses)
- Code-based (defined in Python)
- Shared across all users
- Defines parsing rules, exclusion patterns, XML tag names, etc.

### Default Config Classes

#### `CoreDefaultConfig`

Static defaults for core document structure.

```python
@dataclass(frozen=True)
class CoreDefaultConfig:
    components: SoftwareComponents = field(default_factory=SoftwareComponents)
    xml_generator_config: XMLGeneratorConfig = field(default_factory=XMLGeneratorConfig)
    image_config_name: str = "Imgconf.ini"
```

- **SoftwareComponents**: Maps component names like `NSPC` (Safety Nucleus), `NS_KERNEL`, `SIMNS`, etc.
- **XMLGeneratorConfig**: Indentation style, encoding, XML declaration settings
- **image_config_name**: Standard INI filename for kernel configuration

#### `FileVersioningDefaultConfig`

Static rules for file versioning scanning.

```python
@dataclass(frozen=True)
class FileVersioningDefaultConfig:
    rules: Rules = field(default_factory=Rules)
    # rules contains:
    #   - inclusion.extensions: [".c", ".h", ".ads", ".adb", ".asm", ".s"]
    #   - exclusion.dirs: ["Protocols_win32", ".vscode", "BIN", ...]
    #   - exclusion.dirs_contains: [...]
    #   - exclusion.files: ["resource.h", "Loader.c", ...]
    tags: FileVersioningTag = field(default_factory=FileVersioningTag)
```

**Examples of static rules**:
- Allowed file extensions: `.c`, `.h`, `.ads`, `.adb`, `.asm`, `.s`
- Excluded directories: `BIN`, `OBJ`, `.vscode`, `MakeBatches`, etc.
- Path-based exclusions: "SONS-RTS" directory excludes `.ads`/`.adb` files
- XML output tag: `<file>`

#### `TaskVersioningDefaultConfig`

Static rules for task versioning and INI parsing.

```python
@dataclass(frozen=True)
class TaskVersioningDefaultConfig:
    roots: Roots = field(default_factory=Roots)
    sections: INISections = field(default_factory=INISections)
    app_task: AppTask = field(default_factory=AppTask)
    sys_task: SysTask = field(default_factory=SysTask)
    rules: Rules = field(default_factory=Rules)
    tags: TaskVersioningTag = field(default_factory=TaskVersioningTag)
    num_tasks: str = "NumTask"
```

**Static parsing constants**:
- **Roots**: Internal mode → `NSPC`, External mode → `NSPC` + `NS_KERNEL`
- **INISections**: Section names in `.ini` files: `"Settings"`, `"CONTAINER"`, `"AP"`
- **AppTask**: Field names in INI files → `"NomeTask"`, `"V1_FileTask"`, `"TipoTask"`, `"VersioneTask"`
- **SysTask**: Kernel field names → `"FileBoot"`, `"FileBootAPs"`, `"V1_FileLoader"`, etc.
- **Excluded task types**: `"NO_SCHED"`, `"RBC"`
- **XML output tag**: `<task>`

---

## Layer 3: Runtime Config Objects

Each config class **merges** both layers and provides convenient accessors.

### Example: `CoreConfig`

```python
config = CoreConfig(user_config_path="config/core_config.json")

# Access user configuration
print(config.user_config.vdd_type)          # "vital"
print(config.stream_root)                   # Path from JSON

# Access default configuration
print(config.default_config.components)     # SoftwareComponents dataclass
print(config.components.SAFETY_NUCLEUS)     # "NSPC"
```

### Example: `FileVersioningConfig`

```python
fv_config = FileVersioningConfig(
    user_config_path="config/file_versioning.json",
    core_user_config_path=core_config
)

# User layer: what this document needs
print(fv_config.version_extraction_criteria)  # Regex from JSON
print(fv_config.title)                        # "LIST OF WSPHS+ SW FILES..."

# Default layer: static rules for scanning
print(fv_config.allowed_extensions)           # [".c", ".h", ".ads", ...]
print(fv_config.excluded_dirs)                # ["BIN", "OBJ", ...]
```

### Example: `TaskVersioningConfig`

```python
tv_config = TaskVersioningConfig(
    user_config_path="config/task_versioning.json",
    core_user_config_path=core_config
)

# User layer: document-specific settings
print(tv_config.has_previous_release())       # True/False from JSON
print(tv_config.app_tasks)                    # ["ixl.ini", "srlw.ini"]

# Default layer: static INI parsing rules
print(tv_config.app_task.name)                # "NomeTask"
print(tv_config.sys_task.kernel_key)          # "FileKernel"
print(tv_config.excluded_task_types)          # ("NO_SCHED", "RBC")
```

---

## How Automatic Default Loading Works

When you create a config object, the `DefaultConfigLoader` automatically loads the matching default config:

```python
class FileVersioningConfig(Config):
    def __init__(self, user_config_path, core_user_config_path):
        self.user_config = self.load_user_config(user_config_path)
        # ↓ Automatically loads FileVersioningDefaultConfig
        self.default_config = self.load_default_config()
```

**Naming Convention**:
- `FileVersioningConfig` → `FileVersioningDefaultConfig`
- `CoreConfig` → `CoreDefaultConfig`
- `TaskVersioningConfig` → `TaskVersioningDefaultConfig`

**Resolution Process**:
1. Get class name: `FileVersioningConfig`
2. Remove `Config` suffix: `FileVersioning`
3. Convert to snake_case: `file_versioning`
4. Append `_default_config`: `file_versioning_default_config`
5. Import from: `configs.default_config.file_versioning_default_config`
6. Instantiate: `FileVersioningDefaultConfig()`

---

## Design Rationale

### Why Two Levels?

**User Config (Mutable)**:
- Varies per document/environment
- Requires validation of paths and existence
- User-friendly JSON format
- Changed for each VDD generation

**Default Config (Immutable)**:
- Never changes at runtime
- Structural constants and parsing rules
- Avoids code duplication across instances
- Type-safe (frozen dataclasses prevent accidents)

### Benefits

1. **Separation of Concerns**: User input stays separate from application constants.
2. **Type Safety**: Immutable dataclasses catch misconfiguration early.
3. **Maintainability**: Rules stay in one place, not scattered in code.
4. **Extensibility**: Add new default configs without modifying existing ones.
5. **Documentation**: Dataclass fields serve as self-documenting API.

### Practical Rule of Thumb

- If a value changes for each VDD run, it belongs in the **user config** JSON.
- If a value is a stable rule, field name, tag name, or exclusion list, it belongs in the **default config** dataclasses.

---

## Extending Configuration

### Adding a New User Config Parameter

1. **Edit the JSON file** (e.g., `config/file_versioning.json`)
2. **No code changes needed** — it will be automatically available as an attribute

```python
fv_config.user_config.my_new_setting  # automatically populated
```

### Adding a New Default Setting

1. **Edit the corresponding default config file** (e.g., `file_versioning_default_config.py`)
2. **Add a field to the dataclass**:

```python
@dataclass(frozen=True)
class FileVersioningDefaultConfig:
    # ... existing fields ...
    my_new_constant: str = "default_value"
```

3. **Access it**:

```python
fv_config.default_config.my_new_constant
```

---

## Summary Table

| Aspect | User Config | Default Config |
|---|---|---|
| **Location** | `config/*.json` | `src/configs/default_config/*.py` |
| **Mutability** | Mutable | Immutable (frozen) |
| **Format** | JSON | Python dataclass |
| **Scope** | Per-document | Global/application-wide |
| **Examples** | Paths, metadata, modes | Rules, tag names, constants |
| **Changed by** | End user | Developers |
| **Access** | `config.user_config.*` | `config.default_config.*` |
| **Validation** | Path existence checks | Type hints + frozen dataclass |

