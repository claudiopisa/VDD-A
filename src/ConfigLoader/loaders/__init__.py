"""
Package per i loader delle configurazioni.
"""

from .file_versioning import ConfigLoaderFileVersioning
from .global_config import ConfigLoaderGlobal

__all__ = ["ConfigLoaderFileVersioning", "ConfigLoaderGlobal"]
