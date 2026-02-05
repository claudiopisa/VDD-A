"""
Test script per i ConfigLoader (FileVersioning e Global).
Verifica che le configurazioni siano caricate e validate correttamente.
"""

import sys
from pathlib import Path

# Aggiungere src al path per gli import
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ConfigLoader.loaders import ConfigLoaderFileVersioning, ConfigLoaderGlobal


def test_file_versioning_loader():
    """Testa il ConfigLoaderFileVersioning."""
    print("\n" + "="*60)
    print("TEST: ConfigLoaderFileVersioning")
    print("="*60)
    
    try:
        config = ConfigLoaderFileVersioning("config/ch2_config.json")
        print("✓ Configurazione caricata e validata con successo")
        
        print(f"\nAttributi estratti:")
        print(f"  - Mode: {config.get_versioning_mode()}")
        print(f"  - Allowed Extensions: {config.get_allowed_extensions()}")
        print(f"  - Excluded Dirs: {config.get_excluded_dirs()}")
        print(f"  - Excluded Files: {config.get_excluded_files()}")
        print(f"  - Version Extraction Regex: {config.get_version_extraction_criteria()}")
        print(f"  - Title: {config.get_title()}")
        print(f"  - Columns: {config.get_columns_name()}")
        
        return True
    except Exception as e:
        print(f"✗ Errore: {e}")
        return False


def test_global_loader():
    """Testa il ConfigLoaderGlobal."""
    print("\n" + "="*60)
    print("TEST: ConfigLoaderGlobal")
    print("="*60)
    
    try:
        config = ConfigLoaderGlobal("config/global_config.json")
        print("✓ Configurazione caricata e validata con successo")
        
        print(f"\nAttributi estratti:")
        print(f"  - VDD Type: {config.get_vdd_type()}")
        print(f"  - Kernel Mode: {config.get_kernel_mode()}")
        print(f"  - Input Mode: {config.get_input_mode()}")
        
        # Roots usando il kernel_mode dalla config
        roots = config.get_roots()
        print(f"  - Roots (auto): {roots}")
        
        # Roots specificando il mode
        internal_roots = config.get_roots("internal")
        external_roots = config.get_roots("external")
        print(f"  - Roots (internal): {internal_roots}")
        print(f"  - Roots (external): {external_roots}")
        
        print(f"  - Stream Root: {config.get_stream_root()}")
        print(f"  - Components: {config.get_components()}")
        print(f"  - Metadata: {config.get_doc_metadata()}")
        
        return True
    except Exception as e:
        print(f"✗ Errore: {e}")
        return False


def test_invalid_config():
    """Testa la validazione con una configurazione non valida."""
    print("\n" + "="*60)
    print("TEST: Validazione - Configurazione non valida")
    print("="*60)
    
    try:
        # Provare a caricare una config che non esiste
        config = ConfigLoaderFileVersioning("config/non_existent.json")
        print("✗ Avrebbe dovuto sollevare un errore!")
        return False
    except FileNotFoundError as e:
        print(f"✓ FileNotFoundError catturato correttamente: {e}")
        return True
    except Exception as e:
        print(f"✓ Errore catturato: {e}")
        return True


def main():
    """Esegui tutti i test."""
    print("\n" + "█"*60)
    print("█ Test dei ConfigLoader")
    print("█"*60)
    
    results = []
    results.append(("FileVersioning Loader", test_file_versioning_loader()))
    results.append(("Global Loader", test_global_loader()))
    results.append(("Invalid Config", test_invalid_config()))
    
    # Riepilogo
    print("\n" + "="*60)
    print("RIEPILOGO")
    print("="*60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("█"*60 if all_passed else "⚠"*60))
    print("█ Test completati" if all_passed else "⚠ Alcuni test hanno fallito")
    print("█"*60 if all_passed else "⚠"*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
