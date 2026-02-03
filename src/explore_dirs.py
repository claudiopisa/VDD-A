from pathlib import Path

root = ""
for path in root.rglob("*"):
    if path.is_dir():
        print(path)
        print(path.stem)
        break