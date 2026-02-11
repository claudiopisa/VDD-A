from enum import Enum


class ConfigKeysFileVersioning(str, Enum):

    # Attributi di primo livello
    VERSIONING_MODE = "mode"
    ALLOWED_EXTENSIONS = "allowed_extensions"
    VERSION_EXTRACTION_CRITERIA = "version_extraction_criteria"
    RULES = "rules"
    METADATA = "metadata"
    
    # Percorsi annidati - Exclusion rules
    EXCLUDED_DIRS = RULES + ".exclusion.dirs"
    EXCLUDED_FILES = RULES + ".exclusion.files"
    
    # Percorsi annidati - Metadata
    TITLE = METADATA + ".title"
    COLUMNS_NAME = METADATA + ".columns_name"
    
    # Lista delle chiavi obbligatorie per la configurazione di file versioning
    @classmethod
    def get_required_keys(cls) -> list:
        """
        Ritorna la lista delle chiavi obbligatorie per una configurazione valida.
        
        Returns:
            list: Lista di ConfigKeysEnum con le chiavi richieste
        """
        return [
            cls.VERSIONING_MODE,
            cls.ALLOWED_EXTENSIONS,
            cls.VERSION_EXTRACTION_CRITERIA,
            cls.EXCLUDED_DIRS,
            cls.EXCLUDED_FILES,
            cls.TITLE,
            cls.COLUMNS_NAME,
        ]
