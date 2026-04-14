from warnings import deprecated

from .file import File

@deprecated("FileList is deprecated. Use FileCollection instead.")
class FileList(list[File]):
    def __repr__(self):
        out = "FileList:\n"
        out += File.format_header_row("PATH", "VERSION") + "\n"
        for file in self:
            out += f"{file}\n"

        return out
