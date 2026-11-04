"""Paquetes Python nuevos y actualizados (feeds RSS oficiales de PyPI).

PyPI no ofrece busqueda por API, pero publica RSS con los ultimos paquetes
registrados y actualizados. Se filtran por palabras clave del dominio.
"""

from __future__ import annotations

import re
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

from ..http import Cliente
from ..models import Item, normalizar
from .base import Fuente, Resultado

FEEDS = (
    "https://pypi.org/rss/packages.xml",
    "https://pypi.org/rss/updates.xml",
)

CLAVES = {
    "mcp",
    "model",
    "context",
    "protocol",
    "agent",
    "agents",
    "agentic",
    "llm",
    "llms",
    "claude",
    "gpt",
    "rag",
    "retrieval",
    "embedding",
    "embeddings",
    "prompt",
    "prompts",
    "inference",
    "transformer",
    "diffusion",
    "speech",
    "vision",
    "multimodal",
    "fine",
    "tuning",
}

PROYECTO = re.compile(r"/project/([^/]+)/")


class Pypi(Fuente):
    id = "pypi"
    nombre = "PyPI"
    tipo = "paquetes"
    url = "https://pypi.org"
    limite_por_defecto = 60

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for feed in FEEDS:
            try:
                xml = cliente.get_text(feed)
                items = _parsear(xml)
            except Exception as exc:
                avisos.append(f"{feed}: {exc}")
                continue

            for item in items:
                if item.uid not in vistos and len(vistos) < limite:
                    vistos[item.uid] = item

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)


def _parsear(xml: str) -> list[Item]:
    try:
        raiz = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return []

    items: list[Item] = []
    for nodo in raiz.iter("item"):
        titulo = (nodo.findtext("title") or "").strip()
        enlace = (nodo.findtext("link") or "").strip()
        descripcion = (nodo.findtext("description") or "").strip()
        publicado = (nodo.findtext("pubDate") or "").strip()

        if not titulo or not enlace:
            continue
        if not _relevante(titulo, descripcion):
            continue

        coincidencia = PROYECTO.search(enlace)
        nombre = coincidencia.group(1) if coincidencia else titulo.split(" ")[0]
        topics = ["pypi", "python"]
        topics.extend(sorted(CLAVES.intersection(normalizar(f"{titulo} {descripcion}").split())))

        items.append(
            Item(
                uid=f"pypi:{nombre.lower()}",
                fuente="pypi",
                tipo="paquete",
                nombre=nombre,
                url=f"https://pypi.org/project/{nombre}/",
                descripcion=descripcion,
                autor=(nodo.findtext("author") or None),
                homepage=f"https://pypi.org/project/{nombre}/",
                topics=topics,
                metricas={},
                creado_en=_fecha(publicado),
                actualizado_fuente=_fecha(publicado),
                estado="activo",
            )
        )
    return items


def _relevante(titulo: str, descripcion: str) -> bool:
    texto = normalizar(f"{titulo} {descripcion}")
    if "model context protocol" in texto:
        return True
    return bool(CLAVES.intersection(texto.split()))


def _fecha(valor: str) -> str | None:
    if not valor:
        return None
    try:
        return parsedate_to_datetime(valor).isoformat(timespec="seconds")
    except (TypeError, ValueError):
        return None
