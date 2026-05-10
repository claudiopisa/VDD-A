# VDD-Automation

Automated generation of **Version Difference Document (VDD)** reports in Word (`.docx`) format from XML versioning data.

Given a source tree and configuration files, VDD-A:
1. Scans source files and task configuration to extract version information.
2. Serialises the result into structured XML.
3. Renders the XML into a formatted Word document, ready for delivery.

---

## Project structure

```
VDD-A/
├── config/                  # User configuration (JSON)
│   ├── core_config.json
│   ├── file_versioning.json
│   └── task_versioning.json
├── src/
│   ├── configs/             # Config loaders (user + default)
│   ├── data_reader/         # Source scanning (file/task versioning)
│   ├── document_builder/    # Word document builder + renderers
│   ├── model/               # Domain model (File, Task, …)
│   ├── utils/               # Logger, JSON parser, …
│   └── xml_generator/       # XML serialisation
├── generate_docs.py         # Documentation generator (pdoc)
└── requirements.txt
```

---

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Configuration

All configuration lives in `config/`. Copy and edit the JSON files to match your environment.

### `core_config.json`

| Key | Description |
|---|---|
| `vdd_type` | Document type: `"vital"` or `"non_vital"` |
| `input_mode` | Source input mode: `"localSource"` |
| `kernel_mode` | Kernel type: `"internal"` or `"external"` |
| `paths.stream_root` | Root directory of the source tree |
| `paths.output_dir` | Directory where the `.docx` is written |
| `metadata.doc_name` | Name shown in the document |

### `file_versioning.json`

| Key | Description |
|---|---|
| `mode` | Version extraction mode: `"version"` |
| `version_extraction_criteria` | Regex pattern to extract version strings from source files |
| `metadata.title` | Chapter title in the Word document |
| `metadata.columns_name` | Column headers for the file table (e.g. `["Name", "Version"]`) |

### `task_versioning.json`

| Key | Description |
|---|---|
| `previous_release.enabled` | Whether to compare against a previous release |
| `previous_release.root` | Path to the previous release source tree |
| `metadata.title` | Chapter title in the Word document |
| `metadata.columns_name` | Column headers for the task table (e.g. `["Name", "Type", "Version", "Modified"]`) |
| `app_tasks` | List of `.ini` task configuration files to include |

---

## Usage

### 1 — Generate the versioning XML

Run the appropriate parser to scan sources and produce the intermediate XML:

```bash
cd src
python file_versioning_test.py   # produces file_versioning.xml
python task_versioning_test_internal.py  # produces task_versioning_output.xml
```

### 2 — Build the Word document

```python
from configs import CoreConfig, FileVersioningConfig, TaskVersioningConfig
from document_builder import DocumentBuilder, FileVersioningRenderer
from document_builder.renderer.task_versioning.task_versioning_renderer import TaskVersioningRenderer

core_conf = CoreConfig("config/core_config.json")
fv_conf   = FileVersioningConfig("config/file_versioning.json", core_conf)
tv_conf   = TaskVersioningConfig("config/task_versioning.json", core_conf)

builder = DocumentBuilder(output_path="output/VDD.docx")
builder.add_section(FileVersioningRenderer("file_versioning.xml", fv_conf)) \
       .add_section(TaskVersioningRenderer("task_versioning_output.xml", tv_conf)) \
       .save()
```

See [`src/doc_builder_demo.py`](src/doc_builder_demo.py) for a complete runnable example.

---

## API documentation

Generated HTML documentation is available at:  
**https://claudiopisa.github.io/VDD-A/**

To regenerate it locally:

```bash
# Static HTML → docs/
python generate_docs.py

# Live preview in the browser
python generate_docs.py --live
```

---

## Architecture overview

```
JSON configs ──► Config objects
                      │
Source tree ──► DataReader ──► Model (FileCollection / TaskList)
                                     │
                               XMLGenerator ──► versioning.xml
                                                     │
                                              Renderer ──► DocumentBuilder ──► .docx
```

| Layer | Responsibility |
|---|---|
| `configs` | Load and merge user JSON + static defaults |
| `data_reader` | Scan source trees, extract version info |
| `model` | Domain objects: `File`, `Task`, `FileCollection`, `TaskList` |
| `xml_generator` | Serialise model objects to structured XML |
| `document_builder` | Parse XML and render to Word via `python-docx` |
