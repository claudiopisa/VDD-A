# src/readers/task_versioning_reader.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import configparser

@dataclass
class TaskRow:
    name: str
    type: str
    version: str
    modified: str  # "N/A" for now

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def extract_version_from_file(path: Path, regex: str) -> str | None:
    if not path.exists():
        return None
    content = _read_text(path)
    m = re.search(regex, content)
    return m.group(1).strip() if m else None

def load_ini_flat(path: Path) -> dict[str, str]:
    """
    Imgconf.ini sembra essere un ini "flat" (chiave=valore) con possibili sezioni assenti.
    Lo leggiamo con configparser in una sezione fittizia.
    """
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if not raw.lstrip().startswith("["):
        raw = "[DEFAULT]\n" + raw

    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str  # case-sensitive keys
    cp.read_string(raw)

    # Unisci DEFAULT + eventuali sezioni
    out = dict(cp["DEFAULT"])
    for sec in cp.sections():
        out.update(dict(cp[sec]))
    return out

def resolve_nspc_relpath(nspc_root: Path, value: str) -> Path:
    """
    I path nell'ini sembrano stile windows con backslash e spesso relativi a NSPC (es: swpg\\sons\\...)
    """
    value = value.strip().strip('"').strip("'")
    value = value.replace("/", "\\")
    return (nspc_root / value).resolve()

class DataReaderTaskVersioning:
    def __init__(self, cfg):
        self.cfg = cfg

    def read_internal(self) -> list[TaskRow]:
        imgconf = self.cfg.imgconf_path()
        nspc_root = self.cfg.nspc_root()
        ini = load_ini_flat(imgconf)
        regex = self.cfg.version_regex()

        rows: list[TaskRow] = []

        # Sys tasks
        for _, spec in self.cfg.system_tasks_spec().items():
            name = spec["name"]
            typ = spec["type"]
            src = spec["version_source"]
            ini_key = src["ini_key"]

            version = "UNKNOWN"
            if src["kind"] == "ini":
                version = ini.get(ini_key, "UNKNOWN").strip()
            elif src["kind"] == "file":
                rel = ini.get(ini_key)
                if rel:
                    fpath = resolve_nspc_relpath(nspc_root, rel)
                    v = extract_version_from_file(fpath, regex)
                    version = v if v else "UNKNOWN"

            rows.append(TaskRow(name=name, type=typ, version=version, modified="N/A"))

        # App tasks
        app = self.cfg.app_task_spec()
        num_key = app["num_task_key"]
        n = int(ini.get(num_key, "0").strip() or "0")

        for idx in range(1, n + 1):
            tkey = app["type_key_tpl"].format(idx=idx)
            vkey = app["ver_key_tpl"].format(idx=idx)
            fkey = app["file_key_tpl"].format(idx=idx)

            t = ini.get(tkey, "").strip()
            v = ini.get(vkey, "").strip()
            f = ini.get(fkey, "").strip()

            # perName prende stem del file V1_FileTask{i}
            task_name = Path(f.replace("\\", "/")).stem if f else f"Task{idx}"

            rows.append(TaskRow(name=task_name, type=t or "UNKNOWN", version=v or "UNKNOWN", modified="N/A"))

        return rows
