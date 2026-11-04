"""Configuracion y rutas del radar.

La base de datos vive por defecto en el directorio de datos del usuario, no en
el repositorio: SQLite sobre OneDrive (u otra carpeta sincronizada) puede
corromperse con archivos WAL. Se puede sobreescribir con ``SKILL_RADAR_DB``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

USER_AGENT = "skill-radar/0.1 (+https://github.com/bentlyy/skill-radar)"

TIEMPO_ESPERA = 25.0
REINTENTOS = 3
PAUSA_REINTENTO = 1.5


def directorio_datos() -> Path:
    """Directorio estable para la base de datos."""
    personalizado = os.getenv("SKILL_RADAR_DIR")
    if personalizado:
        return Path(personalizado).expanduser()

    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        raiz = Path(base) if base else Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        raiz = Path.home() / "Library" / "Application Support"
    else:
        raiz = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    return raiz / "skill-radar"


def ruta_db() -> Path:
    """Ruta del archivo SQLite (``SKILL_RADAR_DB`` tiene prioridad)."""
    personalizada = os.getenv("SKILL_RADAR_DB")
    if personalizada:
        return Path(personalizada).expanduser()
    return directorio_datos() / "radar.db"


def token_github() -> str | None:
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or None


def credenciales_reddit() -> tuple[str, str] | None:
    cliente = os.getenv("REDDIT_CLIENT_ID")
    secreto = os.getenv("REDDIT_CLIENT_SECRET")
    if cliente and secreto:
        return cliente, secreto
    return None


def user_agent() -> str:
    return os.getenv("SKILL_RADAR_UA", USER_AGENT)


def nombre_bd(ruta: Path | None = None) -> str:
    return str(ruta or ruta_db())
