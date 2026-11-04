"""Exporta la muestra de las landings y el catalogo completo del buscador.

- `landings/assets/datos.js`: 70 entradas para los 25 prototipos visuales.
- `landings/assets/catalogo.js`: todo el catalogo en formato compacto para
  `04-compact.html`. Solo guarda nombre, url, fuente, tipo, uso, score, metrica,
  descripcion corta y topics; nunca el contenido de la skill.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from skillscenter import db, facetas

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
destino_muestra = raiz / "landings" / "assets" / "datos.js"
destino_catalogo = raiz / "landings" / "assets" / "catalogo.js"


def _json(valor: str | None, defecto):
    try:
        return json.loads(valor or "")
    except ValueError:
        return defecto


def _recortar(texto: str, maximo: int) -> str:
    texto = " ".join((texto or "").split())
    if len(texto) <= maximo:
        return texto
    corte = texto[:maximo].rsplit(" ", 1)[0].rstrip(" .,;:")
    return f"{corte}…"


def _topics(valor: str | None) -> list[str]:
    crudos = _json(valor, [])
    limpios = []
    for topic in crudos:
        if not isinstance(topic, str):
            continue
        topic = re.sub(r"<[^>]+>", " ", topic).strip()
        if topic and len(topic) <= 48 and all(c.isprintable() for c in topic):
            limpios.append(topic)
    return list(dict.fromkeys(limpios))[:8]


def _compacto(numero: float) -> str:
    numero = float(numero or 0)
    if numero >= 1_000_000:
        return f"{numero / 1_000_000:.1f}M".replace(".0M", "M")
    if numero >= 1_000:
        return f"{round(numero / 1_000)}k"
    return str(int(numero))


def _metrica(metricas: dict) -> str:
    if metricas.get("estrellas"):
        return "★ " + _compacto(metricas["estrellas"])
    if metricas.get("descargas"):
        return "↓ " + _compacto(metricas["descargas"])
    if metricas.get("likes"):
        return "♥ " + _compacto(metricas["likes"])
    if metricas.get("puntos"):
        return f"{int(metricas['puntos'])} pts"
    if metricas.get("forks"):
        return "⑂ " + _compacto(metricas["forks"])
    return ""


def _filas(conexion: sqlite3.Connection) -> list[sqlite3.Row]:
    return conexion.execute(
        """
        SELECT i.*,
               (SELECT score FROM puntuaciones p WHERE p.item_id = i.id
                 ORDER BY p.fecha DESC LIMIT 1) AS score,
               (SELECT c.id FROM item_categorias ic
                  JOIN categorias c ON c.id = ic.categoria_id
                 WHERE ic.item_id = i.id ORDER BY c.orden LIMIT 1) AS cat_id,
               (SELECT c.nombre FROM item_categorias ic
                  JOIN categorias c ON c.id = ic.categoria_id
                 WHERE ic.item_id = i.id ORDER BY c.orden LIMIT 1) AS cat
          FROM items i
        """
    ).fetchall()


def _muestra(filas: list[sqlite3.Row]) -> dict:
    por_fuente: dict[str, list[dict]] = {}
    for fila in filas:
        por_fuente.setdefault(fila["fuente"], []).append(dict(fila))

    seleccion = []
    vistos = set()
    for fuente in por_fuente:
        ordenados = sorted(
            por_fuente[fuente], key=lambda f: (f["score"] or 0, f["nombre"]), reverse=True
        )
        for fila in ordenados[:10]:
            if fila["uid"] in vistos:
                continue
            vistos.add(fila["uid"])
            seleccion.append(fila)

    seleccion.sort(key=lambda f: (f["score"] or 0, f["nombre"]), reverse=True)

    items = []
    for fila in seleccion:
        metricas = _json(fila["metricas"], {})
        items.append(
            {
                "nombre": fila["nombre"],
                "fuente": NOMBRES.get(fila["fuente"], fila["fuente"]),
                "fuenteId": fila["fuente"],
                "tipo": fila["tipo"],
                "url": fila["url"],
                "desc": _recortar(fila["descripcion"] or "", 140),
                "cat": fila["cat"],
                "score": round(fila["score"] or 0),
                "metricas": metricas,
            }
        )

    fuentes = [
        {"id": f, "nombre": NOMBRES.get(f, f), "n": len(v)}
        for f, v in sorted(por_fuente.items(), key=lambda kv: -len(kv[1]))
    ]
    categorias = Counter((fila["cat"] or "otros") for fila in filas)
    return {
        "actualizado": date.today().isoformat(),
        "total": len(filas),
        "fuentes": len(por_fuente),
        "categorias": len(categorias),
        "nuevos": len(filas),
        "fuentesDetalle": fuentes,
        "categoriasDetalle": [
            {"nombre": c, "n": n} for c, n in sorted(categorias.items(), key=lambda kv: -kv[1])
        ],
        "items": items,
    }


def _catalogo(filas: list[sqlite3.Row]) -> dict:
    fuentes = Counter(fila["fuente"] for fila in filas)
    definiciones = facetas.definiciones()
    tipos = definiciones["tipos"]
    usos = definiciones["usos"]

    tipos_orden = {t["id"]: i for i, t in enumerate(tipos)}
    usos_orden = {u["id"]: i for i, u in enumerate(usos)}
    fuentes_orden = {
        fuente: i
        for i, fuente in enumerate(f for f, _ in sorted(fuentes.items(), key=lambda kv: -kv[1]))
    }

    conteo_tipos: Counter[str] = Counter()
    conteo_usos: Counter[str] = Counter()
    categorias = set()
    items = []

    ordenadas = sorted(filas, key=lambda fila: (-(fila["score"] or 0), fila["nombre"].casefold()))
    for fila in ordenadas:
        topics = _topics(fila["topics"])
        categoria = fila["cat_id"] or ""
        tipo = facetas.clasificar_tipo(
            fila["nombre"],
            fila["descripcion"] or "",
            fila["tipo"],
            topics,
            categoria,
        )
        elegidos = facetas.clasificar_usos(
            fila["nombre"],
            fila["descripcion"] or "",
            fila["tipo"],
            topics,
            categoria,
        )
        conteo_tipos[tipo] += 1
        conteo_usos.update(elegidos)
        if fila["cat"]:
            categorias.add(fila["cat"])

        items.append(
            [
                fila["nombre"],
                fila["url"],
                fuentes_orden[fila["fuente"]],
                tipos_orden[tipo],
                fila["cat"] or "",
                round(fila["score"] or 0),
                [usos_orden[uso] for uso in elegidos],
                _metrica(_json(fila["metricas"], {})),
                _recortar(fila["descripcion"] or "", 170),
                " ".join(
                    topics,
                ),
            ]
        )

    fuentes_detalle = [
        {
            "id": fuente,
            "nombre": NOMBRES.get(fuente, fuente),
            "n": total,
        }
        for fuente, total in sorted(fuentes.items(), key=lambda kv: -kv[1])
    ]
    return {
        "actualizado": date.today().isoformat(),
        "total": len(items),
        "categorias": len(categorias),
        "fuentes": fuentes_detalle,
        "tipos": [{**tipo, "n": conteo_tipos.get(tipo["id"], 0)} for tipo in tipos],
        "usos": [{**uso, "n": conteo_usos.get(uso["id"], 0)} for uso in usos],
        # item = [nombre, url, fuente, tipo, categoria, score, usos, metrica, desc, topics]
        "items": items,
    }


def _escribir(ruta: Path, variable: str, datos: dict, compacto: bool) -> int:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if compacto:
        cuerpo = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    else:
        cuerpo = json.dumps(datos, ensure_ascii=False, indent=2)
    ruta.write_text(f"window.{variable} = {cuerpo};\n", encoding="utf-8")
    return ruta.stat().st_size


def main() -> None:
    conexion = db.conectar()
    conexion.row_factory = sqlite3.Row
    filas = _filas(conexion)

    muestra = _muestra(filas)
    tam_muestra = _escribir(destino_muestra, "RADAR", muestra, compacto=False)

    catalogo = _catalogo(filas)
    tam_catalogo = _escribir(destino_catalogo, "CATALOGO", catalogo, compacto=True)

    print(
        f"{len(muestra['items'])} items de muestra -> {destino_muestra} "
        f"({tam_muestra / 1024:.0f} KB)"
    )
    print(
        f"{len(catalogo['items'])} items de catalogo -> {destino_catalogo} "
        f"({tam_catalogo / 1024:.0f} KB)"
    )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
