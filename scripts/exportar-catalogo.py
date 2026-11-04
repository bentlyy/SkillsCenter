"""Vuelca el catalogo a Markdown y CSV en informes/."""

import csv
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from skillscenter import db

NOMBRES = {
    "github": "GitHub",
    "mcp_registry": "Registro MCP",
    "awesome": "Listas curadas",
    "hackernews": "Hacker News",
    "reddit": "Reddit",
    "pypi": "PyPI",
    "npm": "npm",
    "huggingface": "Hugging Face",
}

raiz = Path(__file__).resolve().parents[1]
salida = raiz / "informes"
salida.mkdir(exist_ok=True)


def metrica(fila):
    try:
        datos = json.loads(fila.get("metricas") or "{}")
    except ValueError:
        return ""
    partes = []
    if datos.get("estrellas"):
        partes.append(f"estrellas {datos['estrellas']:,}")
    if datos.get("descargas"):
        partes.append(f"descargas {datos['descargas']:,}")
    if datos.get("likes"):
        partes.append(f"likes {datos['likes']:,}")
    if datos.get("puntos"):
        partes.append(f"{datos['puntos']} pts")
    if datos.get("forks"):
        partes.append(f"forks {datos['forks']:,}")
    return " · ".join(partes)


def clave(fila):
    return (fila.get("score") or 0, fila.get("nombre") or "")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    conexion = db.conectar()
    conexion.row_factory = sqlite3.Row
    filas = conexion.execute(
        """
        SELECT i.*,
               (SELECT score FROM puntuaciones p WHERE p.item_id = i.id
                 ORDER BY p.fecha DESC LIMIT 1) AS score,
               (SELECT group_concat(c.nombre, ', ')
                  FROM item_categorias ic JOIN categorias c ON c.id = ic.categoria_id
                 WHERE ic.item_id = i.id) AS cats
          FROM items i
        """
    ).fetchall()

    por_fuente = defaultdict(list)
    for fila in filas:
        por_fuente[fila["fuente"]].append(dict(fila))

    lineas = [
        f"# Catalogo SkillsCenter — {date.today().isoformat()}",
        "",
        f"**{len(filas)} entradas unicas** en {len(por_fuente)} fuentes.",
        "",
    ]
    for fuente, items in sorted(por_fuente.items(), key=lambda kv: -len(kv[1])):
        items.sort(key=clave, reverse=True)
        lineas += [
            f"## {NOMBRES.get(fuente, fuente)} ({len(items)})",
            "",
            "| # | Nombre | Metricas | Pts | Categorias | Descripcion |",
            "|---|---|---|---|---|---|",
        ]
        for i, fila in enumerate(items, 1):
            enlace = f"[{fila['nombre']}]({fila['url']})"
            desc = (fila["descripcion"] or "").replace("|", "/").replace("\n", " ")
            cats = (fila["cats"] or "").replace("|", "/")
            lineas.append(
                f"| {i} | {enlace} | {metrica(fila)} | {fila['score'] or 0:.0f} "
                f"| {cats} | {desc[:90].strip()} |"
            )
        lineas.append("")

    destino_md = salida / "catalogo-completo.md"
    destino_md.write_text("\n".join(lineas), encoding="utf-8")

    destino_csv = salida / "catalogo-completo.csv"
    with destino_csv.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "fuente",
                "tipo",
                "nombre",
                "url",
                "descripcion",
                "metricas",
                "categorias",
                "score",
                "slug",
                "uid",
                "primera_vez_visto",
                "ultima_vez_visto",
            ]
        )
        for fila in filas:
            w.writerow(
                [
                    fila["fuente"],
                    fila["tipo"],
                    fila["nombre"],
                    fila["url"],
                    fila["descripcion"],
                    fila["metricas"],
                    fila["cats"],
                    fila["score"],
                    fila["slug"],
                    fila["uid"],
                    fila["primera_vez_visto"],
                    fila["ultima_vez_visto"],
                ]
            )

    print(f"{len(filas)} entradas -> {destino_md}")
    print(f"{len(filas)} entradas -> {destino_csv}")


if __name__ == "__main__":
    main()
