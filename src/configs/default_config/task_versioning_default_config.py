from dataclasses import asdict, dataclass, field
from typing import List, Tuple

from configs.default_config.core_default_config import SoftwareComponents

@dataclass(frozen=True)
class AppTask:
    name    : str = "NomeTask"
    path    : str = "V1_FileTask"
    type_   : str = "TipoTask" #Note: `type` is a reserved keyword, hence the underscore suffix
    version : str = "RelTask"


@dataclass(frozen=True)
class SysTask:
    BOOT            : str = "FileBoot"
    BOOT_AP         : str = "FileBootAPs"
    LOADER          : str = "V1_FileLoader"
    KERNEL          : str = "V1_FileKernel"
    KERNEL_VERSION  : str = "RelKernel"

@dataclass(frozen=True)
class InclusionRules:
    internal: str = "Imgconf.ini"
    external: Tuple[str, ...] = field(default_factory=lambda: ("ixl.ini", "srlw.ini"))

@dataclass(frozen=True)
class ExclusionRules:
    task_type: Tuple[str, ...] = field(default_factory=lambda: ("NO_SCHED", "RBC"))

#@dataclass(frozen=True)
#class INISections:
#    settings: str = "Settings"
#    container: str = "CONTAINER"

@dataclass(frozen=True)
class INISections:
    SETTINGS    : str = "Settings"
    CONTAINER   : str = "CONTAINER"
    AP            : str = "AP"

@dataclass(frozen=True)
class ExternalRoots:
    app: str = SoftwareComponents.SAFETY_NUCLEUS          # "NSPC"
    sys: str = SoftwareComponents.SAFETY_NUCLEUS_KERNEL   # "NS_KERNEL"


@dataclass(frozen=True)
class Roots:
    #both app and sys has SAFETY_NUCLEUS as root
    internal: str        = field(default_factory=lambda: SoftwareComponents.SAFETY_NUCLEUS)
    # whereas in external mode, app → NSPC and sys → NS_KERNEL
    external: ExternalRoots = field(default_factory=ExternalRoots)

@dataclass(frozen=True)
class Rules:
    inclusion: InclusionRules = field(default_factory=InclusionRules)
    exclusion: ExclusionRules = field(default_factory=ExclusionRules)

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

    def __repr__(self):
        return f"TaskVersioningDefaultConfig(roots={asdict(self.roots)})"