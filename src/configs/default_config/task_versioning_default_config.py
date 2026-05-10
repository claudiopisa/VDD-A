"""Default configuration values for task versioning features."""

from dataclasses import asdict, dataclass, field
from typing import List, Tuple

from .core_default_config import SoftwareComponents, XMLTag

@dataclass(frozen=True)
class AppTask:
    """Field names used to parse application task records.

    Attributes:
        name: Key used for task name.
        path: Key used for task path/source.
        type: Key used for task type.
        version: Key used for task version.
    """

    name    : str = "NomeTask"
    path    : str = "V1_FileTask"
    type    : str = "TipoTask"
    version : str = "RelTask"


@dataclass(frozen=True)
class SysTask:
    """Field names used to parse system task and kernel records.

    Attributes:
        BOOT: Key used for boot file.
        BOOT_AP: Key used for AP boot file.
        LOADER: Key used for loader file.
        KERNEL: Key used for kernel file.
        KERNEL_VERSION: Key used for kernel version.
    """

    BOOT            : str = "FileBoot"
    BOOT_AP         : str = "FileBootAPs"
    LOADER          : str = "V1_FileLoader"
    KERNEL          : str = "V1_FileKernel"
    KERNEL_VERSION  : str = "RelKernel"

# InclusionRules and ExclusionRules define here are the default rules for task versioning. 
# They can be overridden by user-specific rules from JSON files, whereas these defaults provide a baseline 
# for what to include or exclude when processing tasks.
@dataclass(frozen=True)
class InclusionRules:
    """Inclusion defaults for task versioning flows.

    Attributes:
        internal: Internal mode file name.
        external: External mode file names.
    """

    internal: str = "Imgconf.ini"
    external: Tuple[str, ...] = field(default_factory=lambda: ("ixl.ini", "srlw.ini")) 

@dataclass(frozen=True)
class ExclusionRules:
    """Task types excluded from processing.

    Attributes:
        task_type: Task types skipped by default.
    """

    task_type: Tuple[str, ...] = field(default_factory=lambda: ("NO_SCHED", "RBC"))

#@dataclass(frozen=True)
#class INISections:
#    settings: str = "Settings"
#    container: str = "CONTAINER"

@dataclass(frozen=True)
class INISections:
    """INI section names used by task versioning parsers.

    Attributes:
        SETTINGS: Name of the settings section.
        CONTAINER: Name of the container section.
        AP: Name of the AP section.
    """

    SETTINGS    : str = "Settings"
    CONTAINER   : str = "CONTAINER"
    AP          : str = "AP"

@dataclass(frozen=True)
class ExternalRoots:
    """Roots used in external mode.

    Attributes:
        app: Root component for app tasks.
        sys: Root component for system tasks.
    """

    app: str = SoftwareComponents.SAFETY_NUCLEUS
    sys: str = SoftwareComponents.KERNEL


@dataclass(frozen=True)
class Roots:
    """Roots used by internal and external parsing modes.

    Attributes:
        internal: Root component used in internal mode.
        external: Per-scope roots used in external mode.
    """

    #both app and sys has SAFETY_NUCLEUS as root
    internal: str = SoftwareComponents.SAFETY_NUCLEUS
    # whereas in external mode, app → NSPC and sys → NS_KERNEL
    external: ExternalRoots = field(default_factory=ExternalRoots)

@dataclass(frozen=True)
class Rules:
    """Container for task inclusion and exclusion rules.

    Attributes:
        inclusion: Inclusion rules.
        exclusion: Exclusion rules.
    """

    inclusion: InclusionRules = field(default_factory=InclusionRules)
    exclusion: ExclusionRules = field(default_factory=ExclusionRules)

@dataclass(frozen=True)
class TaskVersioningTag(XMLTag):
    """XML tags used by task versioning output.

    Attributes:
        ROW: XML tag name used for each task row.
    """

    ROW: str = "task"


@dataclass(frozen=True)
class TaskVersioningDefaultConfig:
    """
    Default configuration for task versioning operations.
    
    Contains only structural/static defaults.
    User-specific config (kernel_mode, previous_release, metadata)
    come from JSON files and should NOT be in this default config.
    """
    
    # Structural defaults
    #component_roots: List[str] = field(default_factory=lambda: ["NSPC"])
    roots: Roots = field(default_factory=Roots)
    sections: INISections = field(default_factory=INISections)
    # App tasks
    app_task: AppTask = field(default_factory=AppTask)
    # Sys tasks
    sys_task: SysTask = field(default_factory=SysTask)
    # misc
    num_tasks: str = "NumTask"
    rules: Rules = field(default_factory=Rules)
    tags: TaskVersioningTag = field(default_factory=TaskVersioningTag)

    def __repr__(self):
        """Return a concise debug representation for task defaults.

        Returns:
            str: String representation of task default settings.
        """
        return f"TaskVersioningDefaultConfig(roots={asdict(self.roots)}, sections={asdict(self.sections)}, app_task={asdict(self.app_task)}, sys_task={asdict(self.sys_task)}, num_tasks='{self.num_tasks}', rules={asdict(self.rules)})"