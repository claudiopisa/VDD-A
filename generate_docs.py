"""
Documentation generator for VDD-A.

Run from the project root::

    python generate_docs.py              # generate static HTML into docs/
    python generate_docs.py --live       # live preview in the browser

Output is written to the ``docs/`` directory (created automatically).
Open ``docs/index.html`` to browse the generated documentation.
"""

import subprocess
import sys
from pathlib import Path

# Modules to document (relative to src/).
# Prefix a module with '!' to exclude it from the output.
MODULES = [
    "document_builder",
    "!document_builder.doc_ch3_render",   # legacy — broken @deprecated usage
    "!document_builder.doc_gen_old",       # legacy — broken @deprecated usage
    "!document_builder.doc_gen3",          # legacy — broken @deprecated usage
    "serializer",
    "configs",
    "model",
    "!model.file.file_list",               # legacy — broken @deprecated usage
    "utils",
    "!utils.pe_comparator",                # requires optional msl.loadlib dependency
]

OUTPUT_DIR = Path("docs")
SRC_DIR = Path("src")


def main():
    live = "--live" in sys.argv

    base_cmd = [
        sys.executable, "-m", "pdoc",
        "--docformat", "google",
    ]

    if live:
        print("Starting live preview — open http://localhost:8080 in your browser.")
        print("Press Ctrl+C to stop.\n")
        subprocess.run(
            base_cmd + MODULES,
            cwd=SRC_DIR,
        )
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Generating documentation into '{OUTPUT_DIR.resolve()}' ...")
        result = subprocess.run(
            base_cmd + ["--output-dir", f"../{OUTPUT_DIR}"] + MODULES,
            cwd=SRC_DIR,
        )
        if result.returncode == 0:
            print(f"\nDone. Open '{OUTPUT_DIR / 'index.html'}' to browse the docs.")
        else:
            print("\npdoc exited with errors (see output above).", file=sys.stderr)
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
