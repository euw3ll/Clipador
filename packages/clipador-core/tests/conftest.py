import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parents[2]
    paths = [
        root / "packages" / "clipador-core" / "src",
        root / "packages" / "clipador-adapters" / "src",
    ]
    for path in paths:
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


_ensure_src_on_path()
