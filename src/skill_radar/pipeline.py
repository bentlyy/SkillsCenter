"""Orquestacion: recolectar, normalizar, puntuar y guardar."""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Iterable
from datetime import date
from typing import Any

from . import db
from .http import Cliente
from .models import Item
from .scoring import crecimiento_pct, heat, metrica_principal
from .sources import todas
from .taxonomy import clasificar


def sincronizar(
    conn: sqlite3.Connection,
    fuentes: Iterable[str] | None = None,
    limite: int | None = None,
    cliente: Cliente | None = None,
    hoy: date | None = None,
) -> dict[str, Any]:
    """Ejecuta las fuentes indicadas y devuelve un resumen por fuente."""
    seleccion = set(fuentes) if fuentes else None
    dia = hoy or date.today()
    resumen: dict[str, Any] = {}
    propio = cliente is None

    if propio:
        cliente = Cliente()

    try:
        for fuente in todas():
            if seleccion and fuente.id not in seleccion:
                continue

            disponible, motivo = fuente.disponible()
            if not disponible:
                resumen[fuente.id] = {"estado": "omitida", "motivo": motivo}
                db.marcar_fuente(conn, fuente.id, ok=False, error=motivo)
                db.registrar_evento(conn, fuente.id, "info", f"Omitida: {motivo}")
                conn.commit()
                continue

            inicio = time.perf_counter()
            try:
                resultado = fuente.recolectar(cliente, limite or fuente.limite_por_defecto)
                nuevas = _guardar(conn, resultado.items, dia)
                duracion = round((time.perf_counter() - inicio) * 1000)

                db.marcar_fuente(conn, fuente.id, ok=True, vistos=len(resultado.items), error=None)
                db.registrar_evento(
                    conn,
                    fuente.id,
                    "ok",
                    f"{len(resultado.items)} entradas, {nuevas} nuevas",
                    {"ms": duracion, "avisos": resultado.avisos[:5]},
                )
                conn.commit()

                resumen[fuente.id] = {
                    "estado": "ok",
                    "items": len(resultado.items),
                    "nuevas": nuevas,
                    "ms": duracion,
                    "avisos": resultado.avisos,
                }
            except Exception as exc:
                conn.rollback()
                duracion = round((time.perf_counter() - inicio) * 1000)
                mensaje = str(exc)[:300]
                db.marcar_fuente(conn, fuente.id, ok=False, error=mensaje)
                db.registrar_evento(conn, fuente.id, "error", mensaje, {"ms": duracion})
                conn.commit()
                resumen[fuente.id] = {
                    "estado": "error",
                    "error": mensaje,
                    "ms": duracion,
                }
    finally:
        if propio and cliente is not None:
            cliente.cerrar()

    return resumen


def _guardar(conn: sqlite3.Connection, items: list[Item], dia: date) -> int:
    nuevas = 0
    fecha = dia.isoformat()

    for item in items:
        categorias = clasificar(item)
        item_id, es_nueva = db.upsert_item(conn, item, categorias)
        nuevas += int(es_nueva)

        actual = metrica_principal(item.metricas)
        previas_7 = db.metricas_previas(conn, item_id, dias=7, fecha=fecha)
        previas_30 = db.metricas_previas(conn, item_id, dias=30, fecha=fecha)

        crec_7 = crecimiento_pct(
            actual, metrica_principal(previas_7) if previas_7 is not None else None
        )
        crec_30 = crecimiento_pct(
            actual, metrica_principal(previas_30) if previas_30 is not None else None
        )

        db.guardar_snapshot(conn, item_id, item.metricas, fecha)
        db.guardar_puntuacion(conn, item_id, heat(item, crec_7, dia), crec_7, crec_30, fecha)

    return nuevas
