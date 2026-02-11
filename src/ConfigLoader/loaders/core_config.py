from enum import StrEnum
from pathlib import Path

from ConfigLoader.user_config_loader import UserConfigLoader
#import core_config.py
from configs.default_config.core_default_config_loader import CoreDefaultConfig


class CoreConfigLoader():

    def __init__(self, path: str):
        self.user_config = UserConfigLoader.load(path)
