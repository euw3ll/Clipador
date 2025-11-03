"""Integração mínima do Clip Editor.

Este pacote servirá como ponte entre o módulo existente `clip-editor` e
os serviços do novo backend. Em breve replicaremos aqui o código real.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class EditorJob:
    """Representa um job de renderização de clipe."""

    id: str
    input_path: Path
    output_path: Path


__all__ = ["EditorJob"]
