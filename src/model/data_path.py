from pathlib import Path
from typing import Optional


class DataPath:
    def __init__(self, path: str | Path, file_name: Optional[str] = None):
        self.path = Path(path)
        print(f"Initializing DataPath with path: {self.path}")

        if not self.path.exists():
            raise FileNotFoundError(f"Data file '{self.path}' does not exist.")
        if not self.path.is_file():
            raise ValueError(f"Data file '{self.path}' is not a file.")

        if not file_name:
            if self.has_father():
                self.alt_name = self.get_father() + "_" + self.path.stem
            else:
                self.alt_name = self.path.stem
        else:
            self.alt_name = file_name

    def __fspath__(self) -> str:
        return str(self.path)

    def __str__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"DataPath({self.path})"

    def __getattr__(self, name: str):
        return getattr(self.path, name)

    def has_father(self) -> bool:
        return len(self.parts) >= 2

    #def get_father(self) -> Optional[str]:
    #    return self.path.parent.stem if self.path.parent != self.path else None

    def get_father(self) -> Optional[str]:
        return self.path.parent.parent.stem if self.has_father() else None