from enum import Enum


class ConfigKeysGlobal(str, Enum):
    """
    Enum che standardizza i percorsi degli attributi di configurazione globale.
    Eredita da str per poter usare direttamente i valori come stringhe senza .value.
    """
    
    # Attributi di primo livello
    VDD_TYPE = "vdd_type"
    KERNEL_MODE = "kernel_mode"
    INPUT_MODE = "input_mode"
    ROOTS = "roots"
    PATHS = "paths"
    METADATA = "metadata"
    
    # Percorsi annidati - Roots
    ROOTS_INTERNAL = ROOTS + ".internal"
    ROOTS_EXTERNAL = ROOTS + ".external"
    
    # Percorsi annidati - Paths
    STREAM_ROOT = PATHS + ".stream_root"
    COMPONENTS = PATHS + ".components"
    
    # Percorsi annidati - Metadata
    DOC_NAME = METADATA + ".doc_name"
    
    # Lista delle chiavi obbligatorie per la configurazione globale
    @classmethod
    def get_required_keys(cls) -> list:
        """
        Ritorna la lista delle chiavi obbligatorie per una configurazione valida.
        
        Returns:
            list: Lista di ConfigKeysGlobal con le chiavi richieste
        """
        return [
            cls.VDD_TYPE,
            cls.KERNEL_MODE,
            cls.INPUT_MODE,
            cls.ROOTS,
            cls.STREAM_ROOT,
            cls.COMPONENTS,
            cls.DOC_NAME,
        ]
