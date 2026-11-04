"""Puntuacion de calor y crecimiento.

El score no pretende ser una verdad absoluta: es una forma reproducible de
mezclar popularidad, crecimiento reciente, frescura y fiabilidad de la fuente
para que el catalogo pueda ordenarse sin depender de una unica metrica.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import date

from .models import Item, dias_desde

PESOS_FUENTE: dict[str, float] = {
    "github": 1.00,
    "mcp_registry": 1.00,
    "awesome": 0.95,
    "reddit": 0.90,
    "hackernews": 0.90,
    "pypi": 0.85,
    "npm": 0.85,
    "huggingface": 0.85,
}

PESO_POPULARIDAD = 0.45
PESO_CRECIMIENTO = 0.30
PESO_FRESCURA = 0.15
PESO_FUENTE = 0.10

TECHO_POPULARIDAD = 1_000_000
VIDA_MEDIA_DIAS = 90


def metrica_principal(metricas: Mapping[str, float]) -> float:
    """Toma la metrica de traccion disponible segun el tipo de fuente."""
    candidatas = ("estrellas", "puntos", "descargas", "likes", "forks")
    return max((float(metricas.get(k, 0) or 0) for k in candidatas), default=0.0)


def log_norm(valor: float, techo: float = TECHO_POPULARIDAD) -> float:
    if valor <= 0:
        return 0.0
    return min(1.0, math.log10(valor + 1) / math.log10(techo + 1))


def factor_frescura(actualizado: str | None, hoy: date | None = None) -> float:
    dias = dias_desde(actualizado, hoy)
    if dias is None:
        return 0.4
    if dias < 0:
        dias = 0
    return math.exp(-dias / VIDA_MEDIA_DIAS)


def factor_crecimiento(crecimiento: float | None) -> float:
    """Mapea -25%..+125% a 0..1; sin historico devuelve un valor neutro."""
    if crecimiento is None:
        return 0.167
    return max(0.0, min(1.0, (crecimiento + 0.25) / 1.5))


def heat(
    item: Item,
    crecimiento_7d: float | None = None,
    hoy: date | None = None,
) -> float:
    popularidad = log_norm(metrica_principal(item.metricas))
    frescura = factor_frescura(item.actualizado_fuente or item.creado_en, hoy)
    crecimiento = factor_crecimiento(crecimiento_7d)
    fuente = PESOS_FUENTE.get(item.fuente, 0.8)

    score = (
        PESO_POPULARIDAD * popularidad
        + PESO_CRECIMIENTO * crecimiento
        + PESO_FRESCURA * frescura
        + PESO_FUENTE * fuente
    )
    return round(score * 100, 2)


def crecimiento_pct(actual: float, anterior: float | None) -> float | None:
    if anterior is None or anterior <= 0:
        return None
    variacion = (actual - anterior) / anterior
    return round(max(-1.0, min(10.0, variacion)), 4)
