from pathlib import Path
from configparser import ConfigParser

class INIParser:
    def __init__(self, ini_path: str | Path):
        self.ini_path = Path(ini_path)
        if not self.ini_path.exists():
            raise FileNotFoundError(f"INI file '{self.ini_path}' does not exist.")
        #if not self.ini_path.is_file():
            #raise ValueError(f"INI path '{self.ini_path}' is not a file.")
        
        self.config = ConfigParser(
            interpolation=None,  # Disable interpolation to preserve raw values
            comment_prefixes=(";", "#", "//"),
            inline_comment_prefixes=(";", "#", "//"),
            delimiters=("=", ),
            strict=False,  # Support both ';' and '#' as comment prefixes
        )
        self.config.optionxform = str  # Preserve case sensitivity of keys

        #self.config.read(self.ini_path) # it fails silently if the file is not found, so we do it in the constructor after validating the path
        with self.ini_path.open() as file:
            self.config.read_file(file)

    
    def get(self, section: str, key: str) -> str:
        if not self.config.has_section(section):
            raise KeyError(f"Section '{section}' not found in INI file.")
        if not self.config.has_option(section, key):
            raise KeyError(f"Key '{key}' not found in section '{section}' of INI file.")
        
        return self.config.get(section, key)
    
    def get_section(self, section: str) -> dict[str, str]:
        if not self.config.has_section(section):
            #raise KeyError(f"Section '{section}' not found in INI file.")
            # raise custom exception to distinguish between "section not found" and "key not found"
            raise Exception(f"Section '{section}' not found in INI file: {self.ini_path}")
        
        return dict(self.config.items(section)) # convert SectionProxy to a regular dictionary 
    
