"""
ConfigLoader - Opzione B
Versione che:
- conserva i dati originali in `self._data` (accesso dict-like)
- crea attributi su `self` per le chiavi valide (dot-notation)
- supporta dict annidati e liste ricorsivamente
- implementa l'interfaccia Mapping (`__getitem__`, `__iter__`, `__len__`)
- fornisce `to_dict()` per ottenere un dict pulito
- evita di sovrascrivere attributi/metodi della classe
- opzionalmente può rendere l'istanza immutabile (freeze)

Non sovrascrive l'implementazione originale.
"""
from __future__ import annotations

import json
import keyword
from pathlib import Path
from collections.abc import Mapping
from typing import Any, Dict, Iterable


def _is_valid_attr(name: str) -> bool:
    """Controlla se un nome può essere usato come attributo Python sicuro."""
    return name.isidentifier() and not keyword.iskeyword(name) and not name.startswith("_")


def _wrap(value: Any) -> Any:
    """Avvolge dizionari e liste ricorsivamente in ConfigLoaderOptionB."""
    if isinstance(value, dict):
        return ConfigLoaderOptionB.from_dict(value)
    if isinstance(value, list):
        return [_wrap(x) for x in value]
    return value


class ConfigLoaderOptionB(Mapping):
    """Loader di configurazione (Opzione B).

    Esempi:
        cfg = ConfigLoaderOptionB('config/global_config.json')
        print(cfg.vdd_type)       # se vdd_type è una chiave valida
        print(cfg['vdd_type'])    # accesso dict-like sempre disponibile
        print(cfg.to_dict())      # dict "pulito" (pronto per json)
    """

    def __init__(self, source: str | dict, *, make_attrs: bool = True, freeze: bool = False):
        # during init it's allowed to set attributes
        object.__setattr__(self, "_frozen", False)

        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {path}")
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        elif isinstance(source, dict):
            raw = source
        else:
            raise TypeError("source must be a path or a dict")

        if not isinstance(raw, dict):
            raise ValueError("Top-level JSON must be an object/dict")

        data: Dict[str, Any] = {}
        for k, v in raw.items():
            wrapped = _wrap(v)
            data[k] = wrapped
            if make_attrs and _is_valid_attr(k) and not hasattr(self.__class__, k) and k not in vars(self):
                # set attribute only if it doesn't conflict with class attributes
                object.__setattr__(self, k, wrapped)

        object.__setattr__(self, "_data", data)

        # freeze if requested
        if freeze:
            object.__setattr__(self, "_frozen", True)

    @classmethod
    def from_dict(cls, d: dict, **kwargs) -> "ConfigLoaderOptionB":
        return cls(d, **kwargs)

    # Mapping methods -----------------------------------------------
    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterable[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # fallback for attribute-style access for keys that couldn't be set as attrs
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"No such config attribute: {name!r}")

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError("ConfigLoaderOptionB instance is frozen and cannot be modified")
        # allow setting of internal attributes and adding new config keys
        if name in ("_data", "_frozen") or name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        # if trying to set a key that exists in _data, update both _data and attribute (if valid)
        if name in self._data:
            wrapped = _wrap(value)
            self._data[name] = wrapped
            if _is_valid_attr(name):
                object.__setattr__(self, name, wrapped)
            return
        # adding new keys: behave like dict assignment
        wrapped = _wrap(value)
        self._data[name] = wrapped
        if _is_valid_attr(name) and not hasattr(self.__class__, name):
            object.__setattr__(self, name, wrapped)

    def to_dict(self) -> Dict[str, Any]:
        """Restituisce una copia 'pulita' dei dati come dict nativo.

        Ricorsivamente converte eventuali ConfigLoaderOptionB annidati in dict.
        """
        def _unwrap(v: Any):
            if isinstance(v, ConfigLoaderOptionB):
                return v.to_dict()
            if isinstance(v, list):
                return [_unwrap(x) for x in v]
            return v

        return {k: _unwrap(v) for k, v in self._data.items()}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data!r})"


# breve demo (non eseguire su import)
if __name__ == "__main__":
    # demo usando i file di configurazione presenti nella repo
    try:
        cfg = ConfigLoaderOptionB("config/global_config.json")
        print("Esempio: cfg.vdd_type ->", getattr(cfg, "vdd_type", "<no vdd_type>"))
        print("Esempio dict-like: cfg['mode'] ->", cfg["mode"] if "mode" in cfg else "<no mode>")
        print("to_dict() =>", cfg.to_dict())

        # mostra comportamento con chiavi non valide
        cfg2 = ConfigLoaderOptionB({"a-b": 1, "valid": 2})
        print("cfg2.valid ->", cfg2.valid)
        print("cfg2['a-b'] ->", cfg2["a-b"])

        # freeze example
        cfg3 = ConfigLoaderOptionB({"k": 1}, freeze=True)
        try:
            cfg3.k = 2
        except Exception as e:
            print("Impossibile modificare cfg3 (frozen):", e)

        print(cfg.vdd_type)  # accesso dot-notation

    except Exception as e:
        print("Demo errore:", e)
