"""
Test file to check CoreConfig with DotDict
Run from: cd src && python test_core_config.py
"""

from configs.core_config import CoreConfig

# Test
print("Attempting to create CoreConfig...")
try:
    coreConfig = CoreConfig(user_config_path="config/core_config.json")
    print(f"✓ Success! CoreConfig created")
    print(f"  Type: {type(coreConfig)}")
    
    print("\n--- Default Config Root ---")
    print(coreConfig.default_config.roots)
    
    print("\n--- User Config Metadata (DotDict) ---")
    print(coreConfig.user_config.metadata)
    print(f"  Type: {type(coreConfig.user_config.metadata)}")
    
    print("\n--- Direct Attribute Access ---")
    print(f"Internal root: {coreConfig.default_config.roots.internal}")
    print(f"Doc name: {coreConfig.user_config.metadata.doc_name}")
    
    print("\n--- DotDict: Both access styles work ---")
    print(f"  Dot notation: coreConfig.user_config.metadata.doc_name = {coreConfig.user_config.metadata.doc_name}")
    print(f"  Dict style:   coreConfig.user_config.metadata['doc_name'] = {coreConfig.user_config.metadata['doc_name']}")
    
except FileNotFoundError as e:
    print(f"✗ FileNotFoundError: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
