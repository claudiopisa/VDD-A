from DataReader.data_reader_file_versioning import DataReaderFileVersioning
from configs.core_config import CoreConfig
from configs.file_versioning_config import FileVersioningConfig

#core config
core_conf = CoreConfig(user_config_path="config/core_config.json")

#file versioning config 
fv_conf = FileVersioningConfig(user_config_path="config/file_versioning.json", core_user_config_path=core_conf)


#print(coreConfig)
#print(fileVersioningConfig)

workspace = core_conf.stream_root_as_path
#print(f"Workspace: {workspace}")
#print(type(workspace))

print(core_conf.components)
component = core_conf.components.NSPC
root = workspace / component

print(f"Root: {root}")

allowed_ext = fv_conf.allowed_extensions
excluded_dirs = fv_conf.excluded_dirs
print(f"Allowed extensions: {allowed_ext}")
print(f"Excluded directories: {excluded_dirs}")

#data reader

try:
    fv_reader = DataReaderFileVersioning(root, fv_conf)
except Exception as e:
    print(f"Error initializing Data Reader for File Versioning: {e}")

rows = list(fv_reader.scan_files())

print(f"\nTotale file trovati: {len(rows)}")