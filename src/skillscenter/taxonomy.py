"""Clasificacion de entradas en secciones estables para el catalogo."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from .models import Item, normalizar

MAX_CATEGORIAS = 3
CATEGORIA_FALLBACK = "otros"

PISTAS_TIPO = {
    "mcp_server": "mcp",
    "modelo": "modelos",
    "skill": "skills",
    "paquete": None,
    "repo": None,
    "post": None,
    "noticia": None,
    "recurso": None,
}


@lru_cache(maxsize=1)
def cargar_categorias() -> tuple[dict[str, Any], ...]:
    texto = resources.files("skillscenter").joinpath("data/categorias.json").read_text("utf-8")
    datos = json.loads(texto)
    for categoria in datos:
        categoria["claves_normalizadas"] = [
            normalizar(clave) for clave in categoria.get("claves", []) if clave
        ]
    return tuple(sorted(datos, key=lambda c: c.get("orden", 500)))


def categorias_por_id() -> dict[str, dict[str, Any]]:
    return {c["id"]: c for c in cargar_categorias()}


def clasificar(item: Item) -> list[str]:
    """Devuelve hasta tres ids de categoria ordenados por afinidad."""
    texto = " ".join([item.nombre, item.descripcion, item.tipo, *item.topics])
    normalizado = normalizar(texto)
    tokens = set(normalizado.split())

    puntajes: dict[str, float] = {}

    for categoria in cargar_categorias():
        aciertos = 0.0
        for clave in categoria["claves_normalizadas"]:
            if " " in clave:
                if clave in normalizado:
                    aciertos += 1.5
            elif clave in tokens:
                aciertos += 1.0
        if aciertos:
            puntajes[categoria["id"]] = aciertos

    pista = PISTAS_TIPO.get(item.tipo)
    if pista:
        puntajes[pista] = puntajes.get(pista, 0.0) + 1.5

    orden = {c["id"]: c.get("orden", 500) for c in cargar_categorias()}
    elegidas = sorted(puntajes, key=lambda c: (-puntajes[c], orden.get(c, 500)))
    elegidas = elegidas[:MAX_CATEGORIAS]
    return elegidas or [CATEGORIA_FALLBACK]
