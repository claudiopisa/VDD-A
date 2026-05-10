# Default Config Usage Examples

This document shows practical examples of how to use default configs correctly and how the Config interface solves verbosity.

---

## Example 1: File Versioning Scanner Setup

### ❌ Wrong: Direct DefaultConfig Access (Confusing)

```python
from configs.default_config.file_versioning_default_config import FileVersioningDefaultConfig

# Direct instantiation (not recommended)
defaults = FileVersioningDefaultConfig()

# Deeply nested access
root = defaults.root
allowed_extensions = defaults.rules.inclusion.extensions  # Hard to read
excluded_dirs = defaults.rules.exclusion.dirs
version_pattern = defaults.version_extraction_criteria

# Set up scanner
scanner = FileVersioningScanner(
    root=root,
    allowed_extensions=allowed_extensions,
    excluded_dirs=excluded_dirs,
    version_pattern=version_pattern,
)
```

**Problems**:
- No type validation (what if JSON config is malformed?)
- Nested accessor paths are hard to remember
- No semantic meaning in variable names

### ✅ Correct: Config Interface (Clean & Maintainable)

```python
from configs import FileVersioningConfig

# Load with user config + auto-loaded defaults
config = FileVersioningConfig(
    user_config_path="config/file_versioning.json",
    core_user_config_path="config/core_config.json"
)

# Flat, semantic access
scanner = FileVersioningScanner(
    root=config.root,
    allowed_extensions=config.allowed_extensions,
    excluded_dirs=config.excluded_dirs,
    version_pattern=config.version_extraction_criteria,
)
```

**Benefits**:
- Single Config instance handles both user config + defaults
- Flat properties are self-documenting
- Type-safe (Config validates on load)

---

## Example 2: Task Versioning Renderer

### ❌ Verbose Direct Access

```python
from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig

defaults = TaskVersioningDefaultConfig()

# Multiple nested accesses to get related values
app_name_key = defaults.app_task.name        # "NomeTask"
app_path_key = defaults.app_task.path        # "V1_FileTask"
sys_boot_key = defaults.sys_task.BOOT        # "FileBoot"
paragraph_tag = defaults.tags.PARAGRAPH      # "paragraph"
row_tag = defaults.tags.ROW                  # "task"
internal_root = defaults.roots.internal      # "NSPC"

# Pass all separately to renderer
renderer = TaskVersioningRenderer(
    app_name_key=app_name_key,
    app_path_key=app_path_key,
    sys_boot_key=sys_boot_key,
    tags=defaults.tags,
    internal_root=internal_root,
)
```

### ✅ Clean Via Config Interface

```python
from configs import TaskVersioningConfig

config = TaskVersioningConfig(
    user_config_path="config/task_versioning.json",
    core_user_config_path="config/core_config.json"
)

# All related values grouped and easy to understand
renderer = TaskVersioningRenderer(
    app_name_key=config.app_name_key,
    app_path_key=config.app_path_key,
    sys_boot_key=config.boot_key,
    tags=config.tags,
    internal_root=config.internal_roots,
)
```

---

## Example 3: Conditional Logic Based on Defaults

### Scenario: Different behavior for internal vs external kernel mode

### ❌ Verbose

```python
from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig

defaults = TaskVersioningDefaultConfig()

if self.core_config.is_kernel_internal:
    root = defaults.roots.internal
    # Access pattern is clear but long
else:
    root = defaults.roots.external.app
```

### ✅ Semantic

```python
from configs import TaskVersioningConfig

task_config = TaskVersioningConfig(...)

if self.core_config.is_kernel_internal:
    root = task_config.internal_roots  # Clear intent, one property
else:
    root = task_config.app_root  # Precalculated by Config
```

**The Config interface provides computed properties** that hide the verbose nesting:

```python
class TaskVersioningConfig(Config):
    @property
    def app_root(self):
        """Returns NSPC for internal kernel, NSPC/Configurazioni for external."""
        if self.core.is_kernel_internal:
            return self.internal_roots
        else:
            return f"{self.external_roots.app}/Configurazioni"
```

---

## Example 4: Testing

### Testing Default Values

```python
from configs.default_config.file_versioning_default_config import FileVersioningDefaultConfig

def test_default_excluded_dirs():
    """Verify default excluded directories are correct."""
    defaults = FileVersioningDefaultConfig()
    
    assert "INCMAKE" in defaults.rules.exclusion.dirs
    assert "Protocols_win32" in defaults.rules.exclusion.dirs
    assert ".vscode" in defaults.rules.exclusion.dirs

def test_default_file_extensions():
    """Verify default included file extensions."""
    defaults = FileVersioningDefaultConfig()
    
    assert ".c" in defaults.rules.inclusion.extensions
    assert ".h" in defaults.rules.inclusion.extensions
    assert ".ads" in defaults.rules.inclusion.extensions
```

**This is OK**: Tests access defaults directly because they're testing the defaults themselves.

### Testing Config Interface

```python
from configs import FileVersioningConfig

def test_config_excluded_dirs_property():
    """Verify the Config interface correctly exposes excluded dirs."""
    config = FileVersioningConfig(
        user_config_path="test_fixtures/file_versioning.json",
        core_user_config_path="test_fixtures/core_config.json"
    )
    
    # Test the property, not the internal nesting
    assert config.excluded_dirs == config.default_config.rules.exclusion.dirs

def test_config_flat_properties():
    """Verify Config provides convenient flat properties."""
    config = FileVersioningConfig(...)
    
    # All of these should work
    assert isinstance(config.allowed_extensions, list)
    assert isinstance(config.excluded_dirs, list)
    assert isinstance(config.version_extraction_criteria, str)
```

---

## Example 5: Document Generation Pipeline

### Complete Workflow

```python
from configs import CoreConfig, FileVersioningConfig, TaskVersioningConfig
from data_reader import FileVersioning, TaskVersioningExternal
from serializer import FileVersioningSerializer, TaskVersioningSerializer
from document_builder import DocumentBuilder

# 1. Load configs (user + defaults)
core_config = CoreConfig("config/core_config.json")
file_config = FileVersioningConfig(
    "config/file_versioning.json",
    core_user_config_path=core_config
)
task_config = TaskVersioningConfig(
    "config/task_versioning.json",
    core_user_config_path=core_config
)

# 2. Read data using default rules
file_reader = FileVersioning(config=file_config)
file_collection = file_reader.read(file_config.root)

task_reader = TaskVersioningExternal(config=task_config)
task_list = task_reader.read()

# 3. Serialize to XML
file_serializer = FileVersioningSerializer(config=file_config)
file_xml = file_serializer.generate(file_collection)

task_serializer = TaskVersioningSerializer(config=task_config)
task_xml = task_serializer.generate(task_list)

# 4. Render to Word document
builder = DocumentBuilder(template="template.docx")
builder.add_file_versioning(file_xml, config=file_config)
builder.add_task_versioning(task_xml, config=task_config)
builder.save("output.docx")

# Notice: All config access is flat (config.root, config.tags, etc.)
# No verbose nesting (config.default_config.rules.exclusion.dirs)
```

---

## Takeaways

<table>
  <thead>
    <tr>
      <th>Pattern</th>
      <th>Use Case</th>
      <th>Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Config Interface</strong></td>
      <td>Consuming defaults</td>
      <td><code>config.excluded_dirs</code></td>
    </tr>
    <tr>
      <td><strong>Direct DefaultConfig</strong></td>
      <td>Testing defaults</td>
      <td><code>assert "dir" in defaults.rules.exclusion.dirs</code></td>
    </tr>
    <tr>
      <td><strong>Via DefaultConfigLoader</strong></td>
      <td>Auto-discovery</td>
      <td>Config classes use it automatically</td>
    </tr>
  </tbody>
</table>

**Rule of Thumb**:
- **Clients**: Always use `Config` subclass (FileVersioningConfig, TaskVersioningConfig)
- **Tests**: Can use `DefaultConfig` directly when testing defaults themselves
- **Never**: Hardcode constants like `"NSPC"` or `".c"` — they live in defaults for a reason
