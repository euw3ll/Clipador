import sys
from pathlib import Path


def _ensure_paths_on_sys_path() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    backend_src = repo_root / "services" / "backend" / "src"
    core_src = repo_root / "packages" / "clipador-core" / "src"

    adapters_src = repo_root / "packages" / "clipador-adapters" / "src"

    for path in (backend_src, core_src, adapters_src):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


_ensure_paths_on_sys_path()
