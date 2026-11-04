"""CLI del radar: sincronizar, consultar e informar."""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from . import config, db
from .digest import generar_digest
from .pipeline import sincronizar


def _imprimir(datos: Any) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2))


def _conectar() -> Any:
    conn = db.conectar()
    db.inicializar(conn)
    return conn


def _cmd_init(_: argparse.Namespace) -> int:
    conn = _conectar()
    conn.close()
    print(f"Base lista en {config.ruta_db()}")
    return 0


def _cmd_sync(args: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        resumen = sincronizar(conn, fuentes=args.fuente, limite=args.limite)
    finally:
        conn.close()
    _imprimir(resumen)
    return 0 if any(r.get("estado") == "ok" for r in resumen.values()) else 1


def _cmd_stats(_: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        _imprimir(db.estadisticas(conn))
    finally:
        conn.close()
    return 0


def _cmd_fuentes(_: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        _imprimir(db.listar_fuentes(conn))
    finally:
        conn.close()
    return 0


def _cmd_categorias(_: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        _imprimir(db.listar_categorias(conn))
    finally:
        conn.close()
    return 0


def _cmd_buscar(args: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        items = db.buscar(
            conn,
            consulta=args.consulta,
            categoria=args.categoria,
            fuente=args.fuente,
            tipo=args.tipo,
            orden=args.orden,
            limite=args.limite,
        )
    finally:
        conn.close()
    _imprimir({"total": len(items), "items": items})
    return 0


def _cmd_tendencias(args: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        items = db.tendencias(
            conn,
            periodo=args.periodo,
            fuente=args.fuente,
            categoria=args.categoria,
            orden=args.orden,
            limite=args.limite,
        )
    finally:
        conn.close()
    _imprimir({"total": len(items), "items": items})
    return 0


def _cmd_digest(args: argparse.Namespace) -> int:
    conn = _conectar()
    try:
        texto = generar_digest(conn, dias=args.dias, limite=args.limite)
    finally:
        conn.close()

    if args.salida:
        destino = Path(args.salida).expanduser()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        print(f"Informe guardado en {destino}")
    else:
        print(texto)
    return 0


def _cmd_serve(_: argparse.Namespace) -> int:
    from .server import main as servir

    servir()
    return 0


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillscenter",
        description="Radar de skills y herramientas de IA.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_init = sub.add_parser("init", help="crea la base de datos")
    p_init.set_defaults(func=_cmd_init)

    p_sync = sub.add_parser("sync", help="rastrea las fuentes y actualiza el catalogo")
    p_sync.add_argument("--fuente", action="append", help="id de fuente (repetible)")
    p_sync.add_argument("--limite", type=int, help="entradas por fuente")
    p_sync.set_defaults(func=_cmd_sync)

    p_stats = sub.add_parser("stats", help="totales del catalogo")
    p_stats.set_defaults(func=_cmd_stats)

    p_fuentes = sub.add_parser("fuentes", help="estado de las fuentes")
    p_fuentes.set_defaults(func=_cmd_fuentes)

    p_cat = sub.add_parser("categorias", help="secciones del catalogo")
    p_cat.set_defaults(func=_cmd_categorias)

    p_buscar = sub.add_parser("buscar", help="busca en el catalogo")
    p_buscar.add_argument("consulta", nargs="?", default="")
    p_buscar.add_argument("--categoria")
    p_buscar.add_argument("--fuente")
    p_buscar.add_argument("--tipo")
    p_buscar.add_argument("--orden", default="relevancia")
    p_buscar.add_argument("--limite", type=int, default=20)
    p_buscar.set_defaults(func=_cmd_buscar)

    p_tend = sub.add_parser("tendencias", help="lo mas relevante del periodo")
    p_tend.add_argument("--periodo", default="7d")
    p_tend.add_argument("--fuente")
    p_tend.add_argument("--categoria")
    p_tend.add_argument("--orden", default="calor")
    p_tend.add_argument("--limite", type=int, default=20)
    p_tend.set_defaults(func=_cmd_tendencias)

    p_digest = sub.add_parser("digest", help="informe Markdown")
    p_digest.add_argument("--dias", type=int, default=1)
    p_digest.add_argument("--limite", type=int, default=15)
    p_digest.add_argument("--salida", help="ruta del .md (por defecto, stdout)")
    p_digest.set_defaults(func=_cmd_digest)

    p_serve = sub.add_parser("serve", help="arranca el servidor MCP (stdio)")
    p_serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            flujo.reconfigure(encoding="utf-8")

    args = construir_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
