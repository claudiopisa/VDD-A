from pathlib import Path
from ..config_loader import ConfigLoader
from ..keys.global_config import ConfigKeysGlobal
from typing import List, Optional, Dict


class ConfigLoaderGlobal(ConfigLoader):
    """
    ConfigLoader specializzato per la configurazione globale del progetto VDD.
    Fornisce metodi getter per accedere agli attributi di configurazione specifici in modo safe.
    Valida la configurazione in base ai requisiti definiti in ConfigKeysGlobal.
    """
    
    def __init__(self, path: str, validate: bool = True):
        """
        Inizializza il ConfigLoader per la configurazione globale.
        
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
        
        for key in ConfigKeysGlobal.get_required_keys():
            value = self._safe_get(self, key, None)
            if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(
                f"Configurazione globale non valida: campi obbligatori mancanti o vuoti:\n"
                f"{', '.join(missing_keys)}"
            )
    
    def _safe_get(self, obj, attr_path: str, default=None):
        """
        Ottiene un attributo annidato in modo sicuro.
        
        Args:
            obj: L'oggetto da cui leggere l'attributo
            attr_path (str): Percorso dell'attributo (es. "paths.stream_root")
            default: Valore di default se l'attributo non esiste
            
        Returns:
            Il valore dell'attributo o il default
        """
        attrs = attr_path.split('.')
        current = obj
        
        for attr in attrs:
            current = getattr(current, attr, None)
            if current is None:
                return default
        
        return current
    
    def get_vdd_type(self) -> Optional[str]:
        """
        Ottiene il tipo di VDD.
        
        Returns:
            str: Il valore di 'vdd_type' (es. "vital"), o None se non presente
        """
        return getattr(self, ConfigKeysGlobal.VDD_TYPE, None)
    
    def get_kernel_mode(self) -> Optional[str]:
        """
        Ottiene la modalità del kernel.
        
        Returns:
            str: Il valore di 'kernel_mode' (es. "internal"), o None se non presente
        """
        return getattr(self, ConfigKeysGlobal.KERNEL_MODE, None)
    
    def get_input_mode(self) -> Optional[str]:
        """
        Ottiene la modalità di input.
        
        Returns:
            str: Il valore di 'input_mode' (es. "localSource"), o None se non presente
        """
        return getattr(self, ConfigKeysGlobal.INPUT_MODE, None)
    
    def get_roots(self, kernel_mode: Optional[str] = None) -> List[str]:
        """
        Ottiene le root directories in base al kernel mode.
        Se kernel_mode non è specificato, usa il valore della configurazione.
        
        Args:
            kernel_mode (str, optional): La modalità del kernel ("internal" o "external").
                                        Se None, usa get_kernel_mode().
        
        Returns:
            list: Lista delle root directories, lista vuota se non presente
        """
        if kernel_mode is None:
            kernel_mode = self.get_kernel_mode()
        
        if kernel_mode is None:
            return []
        
        roots_obj = self._safe_get(self, ConfigKeysGlobal.ROOTS, None)
        if roots_obj is None:
            return []
        
        return getattr(roots_obj, kernel_mode, [])
    
    def get_stream_root(self, as_path: bool = False) -> Optional[str] | Optional[Path]:
        """
        Ottiene il path della stream root.
    
        Args:
            as_path (bool): Se True, ritorna un Path object, altrimenti str
    
        Returns:
            str | Path: Il percorso della stream root, None se non presente
        """

        value = self._safe_get(self, ConfigKeysGlobal.STREAM_ROOT, None)
        if value and as_path:
            return Path(value)
        return value
    
    def get_components(self):
        """
        Ottiene la mappatura dei componenti (nome -> path relativo).
        
        Returns:
            SimpleNamespace: Oggetto con i componenti, None se non presente
        """

        return self._safe_get(self, ConfigKeysGlobal.COMPONENTS, None)
    
    def get_doc_metadata(self):
        """
        Ottiene i metadati del documento (nome, titolo, ecc).
        
        Returns:
            SimpleNamespace: Oggetto con i metadati, None se non presente
        """
        
        return self._safe_get(self, ConfigKeysGlobal.METADATA, None)
