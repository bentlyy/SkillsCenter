"""Servidor MCP del radar.

Expone el catalogo SQLite como herramientas para que un agente busque skills,
detecte tendencias y dispare una sincronizacion puntual. No genera la web: solo
devuelve datos verificables de la base local.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from mcp.server.mcpserver import MCPServer

from . import config, db
from .digest import generar_digest
from .pipeline import sincronizar as _sincronizar

mcp = MCPServer(
    "skillscenter",
    instructions=(
        "Busca skills y herramientas de IA en un catalogo local que se alimenta de "
        "GitHub, Reddit, Hacker News, el registro MCP, awesome-lists, PyPI, npm y "
        "Hugging Face. Usa 'buscar' para consultas, 'tendencias' para lo que mas "
        "crece, 'novedades' para lo recien descubierto y 'ficha' para el detalle. "
        f"Base de datos: {config.ruta_db()}. "
        "Flujo recomendado: estadisticas -> buscar/tendencias -> ficha -> sincronizar."
    ),
)


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


@contextmanager
def _bd() -> Iterator[Any]:
    conn = db.conectar()
    try:
        db.inicializar(conn)
        yield conn
    finally:
        conn.close()


def _resumen(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "slug": item["slug"],
        "uid": item["uid"],
        "nombre": item["nombre"],
        "fuente": item["fuente"],
        "tipo": item["tipo"],
        "url": item["url"],
        "descripcion": (item.get("descripcion") or "")[:280],
        "autor": item.get("autor"),
        "topics": (item.get("topics") or [])[:12],
        "metricas": item.get("metricas") or {},
        "score": item.get("score"),
        "crec_7d": item.get("crec_7d"),
        "categorias": item.get("categorias") or [],
        "ultima_vez_visto": item.get("ultima_vez_visto"),
    }


@mcp.tool()
def buscar(
    consulta: str = "",
    categoria: str | None = None,
    fuente: str | None = None,
    tipo: str | None = None,
    orden: str = "relevancia",
    limite: int = 20,
) -> str:
    """Busca en el catalogo por texto libre y filtros.

    Args:
        consulta: Texto a buscar (acepta acentos o no; usa prefijos).
        categoria: id de seccion (mcp, agentes, skills, rag, programacion, ...).
        fuente: github, mcp_registry, awesome, hackernews, reddit, pypi, npm, huggingface.
        tipo: repo, skill, mcp_server, post, noticia, paquete, modelo, recurso.
        orden: relevancia, calor, crecimiento, recientes, estrellas o descargas.
        limite: maximo de resultados (1-200).
    """
    with _bd() as conn:
        items = db.buscar(
            conn,
            consulta=consulta,
            categoria=categoria,
            fuente=fuente,
            tipo=tipo,
            orden=orden,
            limite=limite,
        )
        return _json({"total": len(items), "items": [_resumen(i) for i in items]})


@mcp.tool()
def tendencias(
    periodo: str = "7d",
    fuente: str | None = None,
    categoria: str | None = None,
    orden: str = "calor",
    limite: int = 20,
) -> str:
    """Lista lo mas relevante visto en el periodo.

    Args:
        periodo: 24h, 7d, 30d o 90d.
        fuente: filtra por fuente.
        categoria: filtra por id de seccion.
        orden: calor (score), crecimiento (variacion 7d) o recientes.
        limite: maximo de resultados (1-200).
    """
    with _bd() as conn:
        items = db.tendencias(
            conn,
            periodo=periodo,
            fuente=fuente,
            categoria=categoria,
            orden=orden,
            limite=limite,
        )
        return _json(
            {"total": len(items), "periodo": periodo, "items": [_resumen(i) for i in items]}
        )


@mcp.tool()
def novedades(dias: int = 1, fuente: str | None = None, limite: int = 20) -> str:
    """Entradas descubiertas por primera vez en los ultimos dias."""
    with _bd() as conn:
        items = db.nuevos(conn, dias=dias, limite=limite, fuente=fuente)
        return _json({"total": len(items), "dias": dias, "items": [_resumen(i) for i in items]})


@mcp.tool()
def ficha(item: str) -> str:
    """Detalle de una entrada por slug, uid o url, con historico y puntuaciones."""
    with _bd() as conn:
        datos = db.ficha(conn, item)
        if datos is None:
            return _json({"error": "no encontrado", "clave": item})
        return _json(datos)


@mcp.tool()
def categorias() -> str:
    """Secciones del catalogo con su numero de entradas."""
    with _bd() as conn:
        return _json(db.listar_categorias(conn))


@mcp.tool()
def fuentes() -> str:
    """Estado de cada fuente: ultima ejecucion, errores y entradas."""
    with _bd() as conn:
        return _json(db.listar_fuentes(conn))


@mcp.tool()
def estadisticas() -> str:
    """Totales del catalogo por fuente, tipo y seccion."""
    with _bd() as conn:
        return _json(db.estadisticas(conn))


@mcp.tool()
def sincronizar(fuente: str | None = None, limite: int | None = None) -> str:
    """Ejecuta el rastreo ahora (puede tardar uno o dos minutos).

    Args:
        fuente: id de una sola fuente; si se omite, ejecuta todas.
        limite: entradas por fuente; por defecto usa el limite de cada fuente.
    """
    with _bd() as conn:
        resumen = _sincronizar(
            conn,
            fuentes=[fuente] if fuente else None,
            limite=limite,
        )
        return _json(resumen)


@mcp.tool()
def digest(dias: int = 1, limite: int = 15) -> str:
    """Informe Markdown con novedades, mayor crecimiento y top por seccion."""
    with _bd() as conn:
        return generar_digest(conn, dias=dias, limite=limite)


def main() -> None:
    mcp.run()
