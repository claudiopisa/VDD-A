from ..config_loader import ConfigLoader
from ..keys.file_versioning import ConfigKeysFileVersioning
from typing import List, Optional


class ConfigLoaderFileVersioning(ConfigLoader):
    """
    ConfigLoader specializzato per il file versioning nella generazione del capitolo 2.
    Fornisce metodi getter per accedere agli attributi di configurazione specifici in modo safe.
    Valida la configurazione in base ai requisiti definiti in ConfigKeysEnum.
    """
    
    def __init__(self, path: str, validate: bool = True):
        """
        Inizializza il ConfigLoader per il file versioning.
        
        Args:
            path (str): Percorso del file JSON di configurazione
            validate (bool): Se True, valida la configurazione al caricamento
            
        Raises:
            ValueError: Se la configurazione non è valida e validate=True
        """
        super().__init__(path)
        if validate:
            self._validate()
    
    def _validate(self) -> None:
        """
        Valida la configurazione verificando che tutti i campi obbligatori siano presenti.
        
        Raises:
            ValueError: Se uno o più campi obbligatori sono mancanti o None
        """
        missing_keys = []
        
        for key in ConfigKeysFileVersioning.get_required_keys():
            value = self._safe_get(self, key, None)
            if value is None or (isinstance(value, list) and len(value) == 0):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(
                f"Configurazione non valida: campi obbligatori mancanti o vuoti:\n"
                f"{', '.join(missing_keys)}"
            )
    
    def _safe_get(self, obj, attr_path: str, default=None):
        """
        Ottiene un attributo annidato in modo sicuro.
        
        Args:
            obj: L'oggetto da cui leggere l'attributo
            attr_path (str): Percorso dell'attributo (es. la catena di attributi "rules.exclusion.dirs")
            default: Valore di default se l'attributo non esiste
            
        Returns:
            Il valore dell'attributo o il default
        """
        attrs = attr_path.split('.')
        current = obj
        
        for attr in attrs:
            current = getattr(current, attr, None) # intera lungo la catena di attributi (namespace)
            if current is None:
                return default
        
        return current
    
    def get_versioning_mode(self) -> Optional[str]:
        """
        Ottiene la modalità di versioning.
        
        Returns:
            str: Il valore di 'mode' dalla configurazione (es. "version"), o None se non presente
        """
        return getattr(self, ConfigKeysFileVersioning.VERSIONING_MODE, None)
    
    def get_allowed_extensions(self) -> List[str]:
        """
        Ottiene le estensioni di file consentite.
        
        Returns:
            list: Lista delle estensioni consentite, lista vuota se non presente
        """
        return getattr(self, ConfigKeysFileVersioning.ALLOWED_EXTENSIONS, [])
    
    def get_excluded_dirs(self) -> List[str]:
        """
        Ottiene le directory escluse dalla scansione.
        
        Returns:
            list: Lista delle directory da escludere, lista vuota se non presente
        """
        return self._safe_get(self, ConfigKeysFileVersioning.EXCLUDED_DIRS, [])
    
    def get_excluded_files(self) -> List[str]:
        """
        Ottiene i file esclusi dalla scansione.
        
        Returns:
            list: Lista dei file da escludere, lista vuota se non presente
        """
        return self._safe_get(self, ConfigKeysFileVersioning.EXCLUDED_FILES, [])
    
    def get_version_extraction_criteria(self) -> Optional[str]:
        """
        Ottiene il criterio (regex) per l'estrazione della versione.
        
        Returns:
            str: La regex pattern per estrarre la versione dai file, None se non presente
        """
        return getattr(self, ConfigKeysFileVersioning.VERSION_EXTRACTION_CRITERIA, None)
    
    def get_title(self) -> Optional[str]:
        """
        Ottiene il titolo per il documento generato.
        
        Returns:
            str: Il titolo del capitolo/documento, None se non presente
        """
        return self._safe_get(self, ConfigKeysFileVersioning.TITLE, None)
    
    def get_columns_name(self) -> List[str]:
        """
        Ottiene i nomi delle colonne per la tabella generata.
        
        Returns:
            list: Lista dei nomi delle colonne, lista vuota se non presente
        """
        return self._safe_get(self, ConfigKeysFileVersioning.COLUMNS_NAME, [])
