#!/usr/bin/env python3
"""Instala la skill Skill Finder en Claude Code, Codex y opencode.

Uso:
    python scripts/instalar_skill.py
    python scripts/instalar_skill.py --destino codex
    python scripts/instalar_skill.py --destino opencode --scope project --proyecto .
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "skills" / "skill-finder"
CATALOGO = RAIZ / "web" / "assets" / "catalogo.js"

RUTAS_USUARIO = {
    "claude": lambda: Path.home() / ".claude" / "skills",
    "codex": lambda: Path.home() / ".agents" / "skills",
    "opencode": lambda: Path.home() / ".config" / "opencode" / "skills",
}

RUTAS_PROYECTO = {
    "claude": Path(".claude") / "skills",
    "codex": Path(".agents") / "skills",
    "opencode": Path(".opencode") / "skills",
}


def destinos(seleccion: str, scope: str, proyecto: Path) -> list[tuple[str, Path]]:
    agentes = ["claude", "codex", "opencode"] if seleccion == "all" else [seleccion]
    if scope == "project":
        proyecto = proyecto.resolve()
        return [(agente, proyecto / RUTAS_PROYECTO[agente] / "skill-finder") for agente in agentes]
    return [(agente, RUTAS_USUARIO[agente]() / "skill-finder") for agente in agentes]


def instalar(ruta: Path) -> None:
    if ruta.exists():
        shutil.rmtree(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        ORIGEN,
        ruta,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    if CATALOGO.is_file():
        assets = ruta / "assets"
        assets.mkdir(exist_ok=True)
        shutil.copy2(CATALOGO, assets / "catalogo.js")
    if not (ruta / "SKILL.md").is_file():
        raise RuntimeError(f"La instalacion no contiene SKILL.md: {ruta}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Instala Skill Finder en Claude Code, Codex y opencode."
    )
    parser.add_argument(
        "--destino",
        choices=["all", "claude", "codex", "opencode"],
        default="all",
        help="Agente de destino (por defecto: all).",
    )
    parser.add_argument(
        "--scope",
        choices=["user", "project"],
        default="user",
        help="Instalacion global del usuario o dentro de un repositorio.",
    )
    parser.add_argument(
        "--proyecto",
        type=Path,
        default=Path.cwd(),
        help="Raiz del repositorio cuando --scope project (por defecto: cwd).",
    )
    args = parser.parse_args(argv)

    if not (ORIGEN / "SKILL.md").is_file():
        print(f"Error: no se encontro la skill en {ORIGEN}", file=sys.stderr)
        return 2
    if args.scope == "project" and not args.proyecto.is_dir():
        print(f"Error: el proyecto no existe: {args.proyecto}", file=sys.stderr)
        return 2

    instaladas: list[tuple[str, Path]] = []
    for agente, ruta in destinos(args.destino, args.scope, args.proyecto):
        try:
            instalar(ruta)
        except (OSError, RuntimeError) as exc:
            print(f"Error al instalar en {ruta}: {exc}", file=sys.stderr)
            return 1
        instaladas.append((agente, ruta))

    if not CATALOGO.is_file():
        print(
            f"Aviso: no se encontro {CATALOGO}; la skill necesitara MCP o SQLite.",
            file=sys.stderr,
        )

    print("Skill Finder instalada:")
    for agente, ruta in instaladas:
        print(f"  {agente:<9} -> {ruta}")
    print()
    print("Reinicia el agente para que descubra la skill.")
    print(f'Prueba: python "{instaladas[0][1] / "scripts" / "skill_finder.py"}" --stats')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
