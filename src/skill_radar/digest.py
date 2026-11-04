"""Informe diario en Markdown a partir del catalogo."""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any

from . import db


def generar_digest(conn: sqlite3.Connection, dias: int = 1, limite: int = 15) -> str:
    hoy = date.today().isoformat()
    stats = db.estadisticas(conn)
    nuevas = db.nuevos(conn, dias=dias, limite=limite)
    calientes = db.tendencias(conn, periodo="7d", orden="crecimiento", limite=limite)
    categorias = {c["id"]: c for c in db.listar_categorias(conn)}

    lineas: list[str] = [
        f"# Radar de skills IA - {hoy}",
        "",
        "## Resumen",
        "",
        f"- Entradas en el catalogo: **{stats['total']}**",
        f"- Nuevas en 24 h: **{stats['nuevos_24h']}** · nuevas en 7 dias: **{stats['nuevos_7d']}**",
        f"- Fuentes activas: **{len(stats['por_fuente'])}**",
        "",
    ]

    lineas.extend(_bloque("Nuevas entradas", nuevas, categorias))
    con_crecimiento = [i for i in calientes if i.get("crec_7d") is not None]
    if con_crecimiento:
        lineas.extend(_bloque("Mayor crecimiento (7 dias)", con_crecimiento, categorias))

    lineas.extend(["## Por seccion", ""])
    for categoria in db.listar_categorias(conn):
        if categoria["id"] == "otros" or not categoria["items"]:
            continue
        top = db.buscar(conn, categoria=categoria["id"], orden="calor", limite=3)
        if not top:
            continue
        lineas.append(f"### {categoria['nombre']} ({categoria['items']})")
        lineas.extend(_lista(top))
        lineas.append("")

    return "\n".join(lineas).rstrip() + "\n"


def _bloque(
    titulo: str, items: list[dict[str, Any]], categorias: dict[str, dict[str, Any]]
) -> list[str]:
    if not items:
        return [f"## {titulo}", "", "_Sin entradas en este periodo._", ""]
    return [f"## {titulo}", "", *_lista(items, categorias), ""]


def _lista(
    items: list[dict[str, Any]], categorias: dict[str, dict[str, Any]] | None = None
) -> list[str]:
    lineas = []
    for item in items:
        detalle = _detalle(item)
        etiquetas = ""
        if categorias:
            nombres = [
                categorias[c]["nombre"]
                for c in item.get("categorias", [])
                if c in categorias and c != "otros"
            ]
            if nombres:
                etiquetas = f" · _{', '.join(nombres[:2])}_"
        lineas.append(f"- [{item['nombre']}]({item['url']}) - {detalle}{etiquetas}")
    return lineas


def _detalle(item: dict[str, Any]) -> str:
    partes: list[str] = []
    descripcion = (item.get("descripcion") or "").strip()
    if descripcion:
        partes.append(descripcion[:180])
    partes.append(item.get("fuente", "?"))
    metricas = item.get("metricas") or {}
    for clave, etiqueta in (
        ("estrellas", "estrellas"),
        ("descargas", "descargas"),
        ("puntos", "puntos"),
        ("likes", "likes"),
    ):
        if metricas.get(clave):
            partes.append(f"{int(metricas[clave]):,} {etiqueta}".replace(",", "."))
            break
    if item.get("score") is not None:
        partes.append(f"calor {item['score']:.1f}")
    if item.get("crec_7d") is not None:
        partes.append(f"{item['crec_7d'] * 100:+.1f}% 7d")
    return " · ".join(partes)
