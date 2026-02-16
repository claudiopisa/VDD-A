"""
Demo: Flatten Config - Converting config data to class attributes

Shows different approaches to access configuration data.
"""

from configs.core_config import CoreConfig
import json
from pathlib import Path

# Create a sample config file for testing
SAMPLE_CONFIG = {
    "setting_1": "value_1",
    "setting_2": 42,
    "nested_config": {
        "option_a": True,
        "option_b": "test"
    }
}

def create_sample_config():
    """Create a sample configuration file."""
    config_path = Path("config/sample_flatten.json")
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(SAMPLE_CONFIG, f, indent=2)
    return config_path


def demo_flatten():
    """Demonstrate the flatten feature."""
    print("="*60)
    print("DEMO: Flatten Config Attributes")
    print("="*60)
    
    # Create sample config
    config_path = create_sample_config()
    
    # Load config (flatten=True by default)
    config = CoreConfig(user_config_path=config_path)
    
    print("\n1. BEFORE FLATTEN (accessing via user_config):")
    print(f"   config.user_config = {config.user_config}")
    
    print("\n2. AFTER FLATTEN (accessing directly as attributes):")
    print(f"   config.setting_1 = {config.setting_1}")
    print(f"   config.setting_2 = {config.setting_2}")
    print(f"   config.nested_config = {config.nested_config}")
    
    print("\n3. All attributes in config instance:")
    for key, value in vars(config).items():
        if not key.startswith('_'):
            print(f"   {key} = {value}")
    
    print("\n4. Access nested config:")
    if hasattr(config, 'nested_config'):
        nested = config.nested_config
        if isinstance(nested, dict):
            print(f"   config.nested_config['option_a'] = {nested['option_a']}")
            print(f"   config.nested_config['option_b'] = {nested['option_b']}")
    
    print("\n" + "="*60)
    print("ALTERNATIVE: Access via user_config (also works)")
    print("="*60)
    print("Both approaches are valid:")
    print(f"   Direct:      config.setting_1 = {config.setting_1}")
    print(f"   Via object:  config.user_config.setting_1 = {config.user_config.setting_1}")


def demo_without_flatten():
    """Demonstrate loading without flattening."""
    print("\n" + "="*60)
    print("DEMO: Without Flatten (flatten=False)")
    print("="*60)
    
    config_path = Path("config/sample_flatten.json")
    
    # Would need to modify CoreConfig to accept flatten parameter
    # config = CoreConfig(user_config_path=config_path)
    # config.user_config = config.load_user_config(config_path, flatten=False)
    
    print("\nIf flatten=False, you would access via:")
    print("   config.user_config.setting_1")
    print("   config.user_config.setting_2")
    print("\nWith flatten=True (default), you can access via:")
    print("   config.setting_1  ✓")
    print("   config.setting_2  ✓")


if __name__ == "__main__":
    try:
        demo_flatten()
        demo_without_flatten()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have a valid config file or adjust the demo.")
