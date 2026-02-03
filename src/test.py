from pathlib import Path
from config_loader import ConfigLoader

from config_loader import ConfigLoader, ConfigLoaderFileVersioning


    #global_cfg = ConfigLoader("config/global_config.json").data
ch2_cfg = ConfigLoaderFileVersioning("config/ch2_config.json").data

