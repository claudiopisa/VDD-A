


from configs.core_config import CoreConfig


coreConfig = CoreConfig(user_config_path="config/core_config.json")

print(coreConfig.vdd_type)
print(coreConfig.input_mode)
print(coreConfig.stream_root)
print(coreConfig.output_dir)
print(coreConfig.rtc_cache_dir)
print(coreConfig.document_name)
print(coreConfig.internal_root)
print(coreConfig.external_root)
print(coreConfig.components)

