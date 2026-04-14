from collections.abc import Iterable, Iterator, MutableMapping

from .file import File

type FileCollectionItems = Iterable[tuple[str, File]]


class FileCollection(MutableMapping[str, list[File]]):
	"""Dictionary-like collection of files grouped by folder path."""

	def __init__(self, items: FileCollectionItems | None = None):
		self._files: dict[str, list[File]] = {}

		if items is not None:
			for folder, file in items:
				self.add(folder, file)
    
    
	def __getitem__(self, key: str) -> list[File]:
		return self._files[key]

	def __setitem__(self, key: str, value: list[File]) -> None:
		if not isinstance(value, list):
			raise TypeError("Value must be a list of File")
		if not all(isinstance(file, File) for file in value):
			raise TypeError("All items must be File instances")
		
		self._files[key] = value

	def __delitem__(self, key: str) -> None:
		del self._files[key]

	def __iter__(self) -> Iterator[str]:
		return iter(self._files)

	def __len__(self) -> int:
		return len(self._files)

	def __repr__(self) -> str:
		out = "FileCollection:\n"
		for folder, files in self._files.items():
			out += f"[{folder}]\n"
			out += File.format_header_row("NAME", "VERSION") + "\n"
			for file in files:
				out += f"{file}\n"

		return out

	def add(self, folder: str, file: File) -> None:
		if folder not in self._files:
			self._files[folder] = []
			
		self._files[folder].append(file)

	def extend(self, items: FileCollectionItems) -> None:
		for folder, file in items:
			self.add(folder, file)

	def to_list(self) -> list[File]:
		files: list[File] = []

		for grouped_files in self._files.values():
			files.extend(grouped_files)
			
		return files

	def to_path_version_rows(self) -> list[tuple[str, str | None]]:
		rows: list[tuple[str, str | None]] = []

		for folder, files in self._files.items():
			for file in files:
				rows.append((f"{folder}\\{file.name}", file.version))

		return rows

	@classmethod
	def from_files(cls, items: FileCollectionItems) -> "FileCollection":
		return cls(items)
	
    