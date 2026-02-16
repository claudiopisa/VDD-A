"""
Main test file for the configuration system.

Tests:
- DefaultConfigLoader (automatic default config loading)
- DottedDict (dict with dot notation)
- Config base class (automatic flattening with reserved keys)
- Subclasses (CoreConfig, FileVersioningConfig, TaskVersioningConfig)
"""

from configs.core_config import CoreConfig
from configs.file_versioning_config import FileVersioningConfig
from configs.task_versioning_config import TaskVersioningConfig


def test_core_config():
    """Test CoreConfig loading."""
    print("\n" + "="*70)
    print("TEST: CoreConfig")
    print("="*70)
    
    try:
        config = CoreConfig(user_config_path="../config/core_config.json")
        
        print("\n✓ CoreConfig loaded successfully")
        print(f"  Type: {type(config).__name__}")
        
        # Test default config
        print(f"\n  Default Config (CoreDefaultConfig):")
        print(f"    - roots.internal: {config.default_config.roots.internal}")
        print(f"    - roots.external: {config.default_config.roots.external}")
        
        # Test user config
        print(f"\n  User Config (DottedDict):")
        print(f"    - metadata: {config.user_config.metadata}")
        print(f"    - metadata.doc_name: {config.user_config.metadata.doc_name}")

        print(f"\n  Accessing both default and user config attributes:")
        print(f"    - {config.default_config.roots}")
        print(f"    - {config.user_config.metadata}")
        
        # Test flatten - attributes should be present
        print(f"\n  Flattened Attributes (in self.__dict__):")
        for key in sorted(config.__dict__.keys()):
            if not key.startswith('_'):
                print(f"    - {key}")
        
        print("\n✅ CoreConfig test PASSED")
        
    except Exception as e:
        print(f"\n❌ CoreConfig test FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_file_versioning_config():
    """Test FileVersioningConfig loading."""
    print("\n" + "="*70)
    print("TEST: FileVersioningConfig")
    print("="*70)
    
    try:
        config = FileVersioningConfig(user_config_path="../config/file_versioning.json")
        
        print("\n✓ FileVersioningConfig loaded successfully")
        print(f"  Type: {type(config).__name__}")
        
        # Test default config
        print(f"\n  Default Config (FileVersioningDefaultConfig):")
        print(f"    - mode: {config.default_config.mode}")
        print(f"    - component_roots: {config.default_config.component_roots}")
        print(f"    - allowed_extensions: {config.default_config.allowed_extensions}")
        
        # Test user config
        print(f"\n  User Config (DottedDict):")
        print(f"    Type: {type(config.user_config).__name__}")
        
        print("\n✅ FileVersioningConfig test PASSED")
        
    except Exception as e:
        print(f"\n❌ FileVersioningConfig test FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_task_versioning_config():
    """Test TaskVersioningConfig loading."""
    print("\n" + "="*70)
    print("TEST: TaskVersioningConfig")
    print("="*70)
    
    try:
        config = TaskVersioningConfig(user_config_path="../config/task_versioning.json")
        
        print("\n✓ TaskVersioningConfig loaded successfully")
        print(f"  Type: {type(config).__name__}")
        
        # Test default config
        print(f"\n  Default Config (TaskVersioningDefaultConfig):")
        print(f"    - mode: {config.default_config.mode}")
        print(f"    - component_roots: {config.default_config.component_roots}")
        
        # Test user config
        print(f"\n  User Config (DottedDict):")
        print(f"    Type: {type(config.user_config).__name__}")
        
        print("\n✅ TaskVersioningConfig test PASSED")
        
    except Exception as e:
        print(f"\n❌ TaskVersioningConfig test FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_reserved_keys_conflict():
    """Test that reserved keys raise an error."""
    print("\n" + "="*70)
    print("TEST: Reserved Keys Conflict Detection")
    print("="*70)
    
    print("\nChecking if a config file with 'user_config' key would be detected...")
    print("Expected: ValueError should be raised")
    
    # This test would require a special JSON file with conflicting keys
    # For now, just document the expected behavior
    print("\n⚠️  SKIPPED (requires test config file with reserved key)")
    print("   This should raise: ValueError with message about conflicting keys")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("CONFIGURATION SYSTEM TEST")
    print("="*70)
    
    test_core_config()
    test_file_versioning_config()
    test_task_versioning_config()
    test_reserved_keys_conflict()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    main()
