from model.file.file import File


class FileList(list[File]):
    def __repr__(self):
        out = "FileList:\n"
        out += File.format_header_row("PATH", "VERSION") + "\n"
        for file in self:
            out += f"{file}\n"

        return out
