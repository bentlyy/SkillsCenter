"""Lanzamientos y discusion en Hacker News via la API publica de Algolia."""

from __future__ import annotations

import html
import re

from ..http import Cliente
from ..models import Item
from .base import Fuente, Resultado

API = "https://hn.algolia.com/api/v1/search_by_date"

CONSULTAS = (
    "mcp server",
    "ai agent",
    "ai agents",
    "claude skill",
    "llm tool",
    "local llm",
    "rag",
    "prompt engineering",
)


class HackerNews(Fuente):
    id = "hackernews"
    nombre = "Hacker News"
    tipo = "comunidad"
    url = "https://news.ycombinator.com"
    limite_por_defecto = 30

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        por_consulta = max(5, min(limite, 100))
        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for consulta in CONSULTAS:
            try:
                datos = cliente.get_json(
                    API,
                    params={
                        "query": consulta,
                        "tags": "story",
                        "numericFilters": "points>3",
                        "hitsPerPage": por_consulta,
                    },
                )
            except Exception as exc:
                avisos.append(f"{consulta}: {exc}")
                continue

            for hit in datos.get("hits", []):
                item = _a_item(hit, consulta)
                if item is not None:
                    vistos.setdefault(item.uid, item)

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)


def _a_item(hit: dict, consulta: str) -> Item | None:
    identificador = hit.get("objectID")
    titulo = hit.get("title")
    if not identificador or not titulo:
        return None

    url_externa = hit.get("url") or f"https://news.ycombinator.com/item?id={identificador}"
    return Item(
        uid=f"hackernews:{identificador}",
        fuente="hackernews",
        tipo="noticia",
        nombre=_texto(titulo),
        url=url_externa,
        descripcion=_texto(hit.get("story_text") or ""),
        autor=hit.get("author"),
        homepage=f"https://news.ycombinator.com/item?id={identificador}",
        topics=["hackernews", consulta],
        metricas={
            "puntos": hit.get("points") or 0,
            "comentarios": hit.get("num_comments") or 0,
        },
        creado_en=hit.get("created_at"),
        actualizado_fuente=hit.get("created_at"),
        estado="activo",
    )


def _texto(valor: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", valor or "")).strip()
