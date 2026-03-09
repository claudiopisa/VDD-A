# TaskVersioningConfig class inherits from Config abstract class

from pathlib import Path
from configs.config import Config
from configs.core_config import CoreConfig

class TaskVersioningConfig(Config):
    """
    Configuration for task versioning operations.
    
    Automatically loads TaskVersioningDefaultConfig through DefaultConfigLoader.
    
    Provides access to configuration data through:
    - self.user_config: User-specific configuration from JSON file (DottedDict)
    - self.default_config: Static structural defaults (TaskVersioningDefaultConfig dataclass)
    
    Example usage:
        config = TaskVersioningConfig("config/task_versioning.json")
        
        # Access user configuration
        kernel_mode = config.user_config.kernel_mode
        prev_enabled = config.user_config.previous_release.enabled
        title = config.user_config.metadata.title
        
        # Access default configuration
        component_roots = config.default_config.component_roots
    """
    
    def __init__(self, user_config_path: str | Path):
        self.user_config_path = user_config_path
        self.user_config = self.load_user_config(user_config_path)
        # DefaultConfigLoader will automatically load TaskVersioningDefaultConfig
        self.default_config = self.load_default_config()
        self.core_config = CoreConfig(user_config_path=self.user_config_path)  # Load core config for shared defaults like image_config_name

    @property
    def roots(self):
        return self.default_config.roots
    
    @property
    def internal_roots(self):
        return self.default_config.roots.internal
    
    @property
    def external_roots(self):
        return self.default_config.roots.external
    
    @property
    def sys_task(self):
        return self.default_config.sys_task
    
    @property
    def app_task(self):
        return self.default_config.app_task
    
    @property
    def boot_key(self):
        return self.sys_task.BOOT
    
    @property
    def boot_ap_key(self):
        return self.sys_task.BOOT_AP
    
    @property
    def loader_key(self):
        return self.sys_task.LOADER
    
    @property
    def kernel_key(self):
        return self.sys_task.KERNEL
    
    @property
    def kernel_version_key(self):
        return self.sys_task.KERNEL_VERSION
    
    @property
    def app_name_key(self):
        return self.app_task.name
    
    @property
    def app_path_key(self):
        return self.app_task.path
    
    @property
    def app_type_key(self):
        return self.app_task.type_
    
    @property
    def app_version_key(self):
        return self.app_task.version

    @property
    def num_tasks(self):
        return self.default_config.num_tasks
    
    @property
    def rules(self):
        return self.default_config.rules
    
    @property
    def excluded_task_types(self):
        return self.rules.exclusion.task_type
    
    #TODO: add inclusion rules    
    
    @property
    def previous_release_version(self):
        return self.user_config.previous_release.version
    
    @property
    def previous_release_root(self):
        return self.user_config.previous_release.root
    
    def has_previous_release(self) -> bool:
        return self.user_config.previous_release.enabled and self.previous_release_root is not None

    @property
    def previous_release_root_as_path(self):
        return Path(self.previous_release_root if self.has_previous_release() else "")
    
    @property
    def title(self):
        return self.user_config.metadata.title
    
    @property
    def app_tasks(self):
        return self.user_config.app_tasks
    
    def get_app_tasks(self, as_dict=True):
        if as_dict:
            # get task file nime, without `.ini` extension, as key, and the whole name with extension as value
            return {f"{Path(task).stem}": task for task in self.app_tasks}
            #return {f"{task[-3]}" for task in self.app_tasks}
        else:
            return self.app_tasks
    
    @property
    def app_internal_section(self):
        return self.default_config.sections.SETTINGS
    
    @property
    def sys_internal_section(self):
        return self.default_config.sections.SETTINGS
    
    @property
    def app_external_section(self):
        return self.default_config.sections.CONTAINER
    
    @property
    def sys_external_section(self):
        return self.default_config.sections.SETTINGS
    
    @property
    def ap_section_key(self):
        return self.default_config.sections.AP
    

