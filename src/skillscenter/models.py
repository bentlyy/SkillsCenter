"""Modelos de datos del radar."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

TIPOS = (
    "repo",
    "skill",
    "mcp_server",
    "post",
    "noticia",
    "paquete",
    "modelo",
    "recurso",
)


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def iso(momento: datetime | None = None) -> str:
    return (momento or ahora()).isoformat(timespec="seconds")


def normalizar(texto: str) -> str:
    """Minusculas, sin acentos y sin puntuacion, para buscar y clasificar."""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    sin_acentos = sin_acentos.casefold()
    return re.sub(r"[^a-z0-9]+", " ", sin_acentos).strip()


def slugify(texto: str, maximo: int = 60) -> str:
    base = normalizar(texto).replace(" ", "-")
    base = base.strip("-")[:maximo].strip("-")
    return base or "item"


def slug_unico(nombre: str, uid: str) -> str:
    """Slug legible y estable; el sufijo evita colisiones entre fuentes."""
    huella = hashlib.blake2b(uid.encode("utf-8"), digest_size=3).hexdigest()
    return f"{slugify(nombre)}-{huella}"


def _fecha(valor: str | None) -> date | None:
    if not valor:
        return None
    texto = valor.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(texto).date()
    except ValueError:
        return None


def dias_desde(valor: str | None, referencia: date | None = None) -> int | None:
    fecha = _fecha(valor)
    if fecha is None:
        return None
    return ((referencia or date.today()) - fecha).days


@dataclass(slots=True)
class Item:
    """Una entrada del catalogo, ya normalizada desde su fuente."""

    uid: str
    fuente: str
    tipo: str
    nombre: str
    url: str
    descripcion: str = ""
    autor: str | None = None
    homepage: str | None = None
    licencia: str | None = None
    lenguaje: str | None = None
    topics: list[str] = field(default_factory=list)
    metricas: dict[str, float] = field(default_factory=dict)
    creado_en: str | None = None
    actualizado_fuente: str | None = None
    estado: str = "activo"

    def __post_init__(self) -> None:
        self.uid = self.uid.strip()
        self.nombre = self.nombre.strip() or self.uid
        self.descripcion = " ".join((self.descripcion or "").split())[:600]
        self.url = self.url.strip()
        if self.tipo not in TIPOS:
            self.tipo = "recurso"
        self.topics = [t.strip() for t in self.topics if t and t.strip()][:25]
        self.metricas = {
            k: float(v) for k, v in self.metricas.items() if isinstance(v, (int, float))
        }

    @property
    def slug(self) -> str:
        return slug_unico(self.nombre, self.uid)

    def a_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "fuente": self.fuente,
            "tipo": self.tipo,
            "nombre": self.nombre,
            "url": self.url,
            "descripcion": self.descripcion,
            "autor": self.autor,
            "homepage": self.homepage,
            "licencia": self.licencia,
            "lenguaje": self.lenguaje,
            "topics": self.topics,
            "metricas": self.metricas,
            "creado_en": self.creado_en,
            "actualizado_fuente": self.actualizado_fuente,
            "estado": self.estado,
        }
