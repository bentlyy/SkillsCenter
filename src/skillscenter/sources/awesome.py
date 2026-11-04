"""Entradas de listas curadas (awesome-lists y skills oficiales).

Muchas entradas apuntan a repositorios de GitHub: se normalizan al uid de
GitHub para que el mismo proyecto no aparezca dos veces. La fuente se ejecuta
antes que GitHub para que este ultimo enriquezca con estrellas cuando lo vea.
"""

from __future__ import annotations

import re

from ..dedupe import uid_desde_url
from ..http import Cliente
from ..models import Item
from .base import Fuente, Resultado

RAW = "https://raw.githubusercontent.com"

LISTAS: tuple[dict[str, str], ...] = (
    {
        "id": "awesome-mcp-servers",
        "url": f"{RAW}/punkpeye/awesome-mcp-servers/main/README.md",
        "tipo": "mcp_server",
    },
    {
        "id": "awesome-ai-agents",
        "url": f"{RAW}/e2b-dev/awesome-ai-agents/main/README.md",
        "tipo": "recurso",
    },
    {
        "id": "awesome-claude-code",
        "url": f"{RAW}/hesreallyhim/awesome-claude-code/main/README.md",
        "tipo": "recurso",
    },
    {
        "id": "awesome-claude-skills",
        "url": f"{RAW}/travisvn/awesome-claude-skills/main/README.md",
        "tipo": "skill",
    },
    {
        "id": "anthropic-skills",
        "url": f"{RAW}/anthropics/skills/main/README.md",
        "tipo": "skill",
    },
)

ENLACE = re.compile(
    r"^\s*(?:[-*+]\s+|\d+\.\s+)?\[([^\]]{2,140})\]\((https?://[^)\s]+)\)\s*(?:[-–—:]\s*)?(.*)$"
)
SECCION = re.compile(r"^\s{0,3}#{2,4}\s+(.+?)\s*#*\s*$")
RUIDO = ("img.shields.io", "badge", "awesome.re", "github.com/sindresorhus/awesome")


class Awesome(Fuente):
    id = "awesome"
    nombre = "Listas curadas"
    tipo = "curaduria"
    url = "https://github.com/topics/awesome"
    limite_por_defecto = 150

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for lista in LISTAS:
            try:
                texto = cliente.get_text(lista["url"])
            except Exception as exc:
                avisos.append(f"{lista['id']}: {exc}")
                continue

            for item in _parsear(texto, lista):
                if item.uid not in vistos and len(vistos) < limite:
                    vistos[item.uid] = item

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)


def _parsear(texto: str, lista: dict[str, str]) -> list[Item]:
    items: list[Item] = []
    seccion = ""

    for linea in texto.splitlines():
        cabecera = SECCION.match(linea)
        if cabecera:
            seccion = _limpiar(cabecera.group(1))
            continue

        coincidencia = ENLACE.match(linea)
        if not coincidencia:
            continue

        nombre, url, descripcion = coincidencia.groups()
        nombre = _limpiar(nombre)
        if not nombre or not url or nombre.startswith("!"):
            continue
        if any(ruido in url.lower() for ruido in RUIDO):
            continue

        uid, canonica = uid_desde_url(url)
        topics = [lista["id"], "curaduria"]
        if seccion:
            topics.append(seccion)

        items.append(
            Item(
                uid=uid,
                fuente="awesome",
                tipo=lista["tipo"],
                nombre=nombre,
                url=canonica,
                descripcion=_limpiar(descripcion),
                autor=lista["id"],
                homepage=canonica,
                topics=topics,
                metricas={},
                estado="activo",
            )
        )

    return items


def _limpiar(texto: str) -> str:
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", texto or "")
    texto = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)
    texto = re.sub(r"[`*_>]+", "", texto)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return " ".join(texto.split()).strip(" -–—:|")[:300]
