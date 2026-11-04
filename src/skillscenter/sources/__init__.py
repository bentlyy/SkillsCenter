"""Registro de fuentes.

El orden importa: las listas curadas van primero para que GitHub y el registro
MCP enriquezcan despues las mismas entradas con metricas reales.
"""

from __future__ import annotations

from .awesome import Awesome
from .base import Fuente, Resultado
from .github import Github
from .hackernews import HackerNews
from .huggingface import HuggingFace
from .mcp_registry import McpRegistry
from .npm import Npm
from .pypi import Pypi
from .reddit import Reddit

FABRICAS: tuple[type[Fuente], ...] = (
    Awesome,
    Github,
    McpRegistry,
    HackerNews,
    Reddit,
    Pypi,
    Npm,
    HuggingFace,
)

__all__ = [
    "Awesome",
    "Fuente",
    "Github",
    "HackerNews",
    "HuggingFace",
    "McpRegistry",
    "Npm",
    "Pypi",
    "Reddit",
    "Resultado",
    "todas",
]


def todas() -> list[Fuente]:
    return [fabrica() for fabrica in FABRICAS]
