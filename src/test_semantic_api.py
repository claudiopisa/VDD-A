"""
Test the semantic API for users - demonstrating how to use the config getters
"""

from configs.core_config import CoreConfig
from configs.file_versioning_config import FileVersioningConfig
from configs.task_versioning_config import TaskVersioningConfig


def test_core_config_api():
    """Test CoreConfig API"""
    print("\n" + "="*70)
    print("CoreConfig - API")
    print("="*70)
    
    config = CoreConfig(user_config_path="../config/core_config.json")
    
    # User-specific configuration
    print(f"\n👤 User Configuration (from JSON):")
    print(f"   VDD Type:        {config.user_config.vdd_type}")
    print(f"   Input Mode:      {config.user_config.input_mode}")
    print(f"   Document Name:   {config.user_config.metadata.doc_name}")
    print(f"   Stream Root:     {config.user_config.paths.stream_root}")
    print(f"   Output Dir:      {config.user_config.paths.output_dir}")
    
    # Static/structural defaults
    print(f"\n🏗️ Default Configuration (static defaults):")
    print(f"   Internal Roots:  {config.default_config.roots.internal}")
    print(f"   External Roots:  {config.default_config.roots.external}")
    print(f"   Components:      {config.default_config.components.NSPC}, {config.default_config.components.NS_KERNEL}")


def test_file_versioning_api():
    """Test FileVersioningConfig API"""
    print("\n" + "="*70)
    print("FileVersioningConfig - API")
    print("="*70)
    
    config = FileVersioningConfig(user_config_path="../config/file_versioning.json")
    
    # User-specific configuration
    print(f"\n👤 User Configuration (from JSON):")
    print(f"   Mode:            {config.user_config.mode}")
    print(f"   Pattern:         {config.user_config.version_extraction_criteria[:60]}...")
    print(f"   Metadata Title:  {config.user_config.metadata.title}")
    print(f"   Columns:         {config.user_config.metadata.columns_name}")
    
    # Static defaults
    print(f"\n🏗️ Default Configuration (static defaults):")
    print(f"   Component Roots: {config.default_config.component_roots}")
    print(f"   Allowed Ext:     {config.default_config.allowed_extensions}")


def test_task_versioning_api():
    """Test TaskVersioningConfig API"""
    print("\n" + "="*70)
    print("TaskVersioningConfig - API")
    print("="*70)
    
    config = TaskVersioningConfig(user_config_path="../config/task_versioning.json")
    
    # User-specific configuration
    print(f"\n👤 User Configuration (from JSON):")
    print(f"   Kernel Mode:     {config.user_config.kernel_mode}")
    print(f"   Previous Enable: {config.user_config.previous_release.enabled}")
    print(f"   Previous Ver:    {config.user_config.previous_release.version}")
    print(f"   Metadata Title:  {config.user_config.metadata.title}")
    print(f"   Columns:         {config.user_config.metadata.columns_name}")
    
    # Static defaults
    print(f"\n🏗️ Default Configuration (static defaults):")
    print(f"   Component Roots: {config.default_config.component_roots}")


def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("CONFIGURATION SYSTEM API TEST")
    print("="*70)
    print("\nTesting access patterns:")
    print("  - User config:    config.user_config.{key}")
    print("  - Default config: config.default_config.{key}")
    
    test_core_config_api()
    test_file_versioning_api()
    test_task_versioning_api()
    
    print("\n" + "="*70)
    print("✅ ALL API TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    main()
