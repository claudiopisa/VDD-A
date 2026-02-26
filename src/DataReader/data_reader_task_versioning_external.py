from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from configs.default_config.task_versioning_default_config import TaskVersioningDefaultConfig
from utils.ini_parser import INIParser
from .data_reader import DataReader

import re

from model.task import Task
from model.task_list import TaskList

#class DataReaderTaskVersioningExternal(DataReader):
