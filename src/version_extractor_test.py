import re
from pathlib import Path 

#VERSION_REG = re.compile(r"(\\*|//|--|;|#).*Versione\\w*\\s*:?")

# Load the whole file into memory and then read it line by line
def extract_version_old(filepath, criteria):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read() # read the entire file into memory
    
    # Search for the "Versione:" pattern followed by the version number
    match = re.search(criteria, content)
    
    if match:
        return match.group(1)
    return None


VERSION_VALUE_RE = re.compile(
    r'Version\w*\s*:\s*([A-Za-z]?\d+(?:\.\d+)+)',
    re.IGNORECASE
)

# Open the file and read it line by line, without loading the whole file into memory.
def extract_version(path: Path, criteria=None):
    version = None

    #VERSION_VALUE_RE = re.compile(
    #    r"(?:\\\\*|//|--|;|#).*Versione\\s*:?\\s*(\\d+\\.\\d+)",
    #    re.IGNORECASE
    #)
    # old regex json "version_extraction_criteria": "(?:\\\\*|//|--|;|#).*Versione\\s*:?\\s*(\\d+\\.\\d+)",

    
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        i = 0
        found = False
        
        """while i < max_lines and not found:
            line = f[i]
            version = VERSION_VALUE_RE.search(line)
            if version:
                found = True
                #return m.group(1) # stop at the first match found
            i += 1"""
                
        """for i, line in enumerate(f):
            if i >= max_lines:
                break
            m = VERSION_VALUE_RE.search(line)
            if m:
                return m.group(1)"""
        
        for line in f:
            m = VERSION_VALUE_RE.search(line)
            if m:
                return m.group(1)


    return version
