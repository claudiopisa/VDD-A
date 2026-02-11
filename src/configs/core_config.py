#CoreConfig class inherites from Config abstract class 

from abc import ABC, abstractmethod
from pathlib import Path


from ConfigLoader.user_config_loader import UserConfigLoader
from configs.config import Config
from configs.default_config.core_default_config_loader import CoreDefaultConfig

class CoreConfig(Config):
    def __init__(self, user_config_path: str | Path):
        self.user_config_path = user_config_path
        self.user_config = self.load_user_config(user_config_path)
        self.default_config = self.load_default_config

    def load_user_config(self, path: str | Path):
        self.user_config = UserConfigLoader(path)
    
    def load_default_config(self):
        self.default_config = CoreDefaultConfig()