"""Capa SQLite: esquema, altas, snapshots, busqueda y tendencias."""

from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from . import config
from .fuentes import FUENTES
from .models import Item, iso, normalizar
from .taxonomy import cargar_categorias

ESQUEMA_VERSION = 1

ESQUEMA = """
CREATE TABLE IF NOT EXISTS fuentes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    url TEXT,
    descripcion TEXT,
    activo INTEGER NOT NULL DEFAULT 1,
    ultima_ejecucion TEXT,
    ultimo_ok TEXT,
    ultimo_error TEXT,
    items_vistos INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    uid TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    fuente TEXT NOT NULL,
    tipo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL,
    homepage TEXT,
    autor TEXT,
    licencia TEXT,
    lenguaje TEXT,
    topics TEXT NOT NULL DEFAULT '[]',
    metricas TEXT NOT NULL DEFAULT '{}',
    creado_en TEXT,
    actualizado_fuente TEXT,
    primera_vez_visto TEXT NOT NULL,
    ultima_vez_visto TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'activo',
    aprobado INTEGER NOT NULL DEFAULT 1,
    origen TEXT NOT NULL DEFAULT 'crawler'
);

CREATE INDEX IF NOT EXISTS idx_items_fuente ON items(fuente);
CREATE INDEX IF NOT EXISTS idx_items_tipo ON items(tipo);
CREATE INDEX IF NOT EXISTS idx_items_primera ON items(primera_vez_visto);
CREATE INDEX IF NOT EXISTS idx_items_ultima ON items(ultima_vez_visto);

CREATE TABLE IF NOT EXISTS snapshots (
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    fecha TEXT NOT NULL,
    metricas TEXT NOT NULL,
    PRIMARY KEY (item_id, fecha)
);

CREATE TABLE IF NOT EXISTS puntuaciones (
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    fecha TEXT NOT NULL,
    score REAL NOT NULL,
    crec_7d REAL,
    crec_30d REAL,
    PRIMARY KEY (item_id, fecha)
);

CREATE TABLE IF NOT EXISTS categorias (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    orden INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS item_categorias (
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    categoria_id TEXT NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, categoria_id)
);

CREATE TABLE IF NOT EXISTS aportes (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    url TEXT NOT NULL,
    descripcion TEXT,
    categoria TEXT,
    tipo TEXT,
    autor TEXT,
    email TEXT,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    creado_en TEXT NOT NULL,
    revisado_en TEXT,
    nota_revision TEXT
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY,
    fecha TEXT NOT NULL,
    fuente TEXT,
    nivel TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    extra TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    item_id UNINDEXED,
    nombre,
    descripcion,
    topics,
    tokenize='unicode61 remove_diacritics 2'
);
"""


def conectar(ruta: str | Path | None = None) -> sqlite3.Connection:
    destino = Path(ruta or config.ruta_db())
    destino.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(destino), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def inicializar(conn: sqlite3.Connection) -> None:
    conn.executescript(ESQUEMA)
    conn.execute(f"PRAGMA user_version={ESQUEMA_VERSION}")

    for fuente in FUENTES:
        conn.execute(
            """
            INSERT INTO fuentes (id, nombre, tipo, url, descripcion)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nombre=excluded.nombre,
                tipo=excluded.tipo,
                url=excluded.url,
                descripcion=excluded.descripcion
            """,
            (
                fuente["id"],
                fuente["nombre"],
                fuente["tipo"],
                fuente["url"],
                fuente["descripcion"],
            ),
        )

    for categoria in cargar_categorias():
        conn.execute(
            """
            INSERT INTO categorias (id, nombre, descripcion, orden)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nombre=excluded.nombre,
                descripcion=excluded.descripcion,
                orden=excluded.orden
            """,
            (
                categoria["id"],
                categoria["nombre"],
                categoria.get("descripcion", ""),
                categoria.get("orden", 100),
            ),
        )

    conn.commit()


# ---------------------------------------------------------------------------
# Escritura


def upsert_item(
    conn: sqlite3.Connection,
    item: Item,
    categorias: Iterable[str] | None = None,
    momento: datetime | None = None,
) -> tuple[int, bool]:
    """Inserta o actualiza una entrada. Devuelve (id, es_nueva)."""
    timestamp = iso(momento)
    fila = conn.execute(
        "SELECT id, fuente, tipo, metricas, topics FROM items WHERE uid=?", (item.uid,)
    ).fetchone()

    fuente = item.fuente
    tipo = item.tipo
    metricas = item.metricas
    topics = item.topics

    if fila:
        previas = _json_dict(fila["metricas"])
        if not item.metricas and previas:
            metricas = previas
            fuente = fila["fuente"]
            tipo = fila["tipo"]
        topics = list(dict.fromkeys([*_json_list(fila["topics"]), *item.topics]))[:25]

    datos = (
        fuente,
        tipo,
        item.nombre,
        item.descripcion,
        item.url,
        item.homepage,
        item.autor,
        item.licencia,
        item.lenguaje,
        json.dumps(topics, ensure_ascii=False),
        json.dumps(metricas, ensure_ascii=False),
        item.creado_en,
        item.actualizado_fuente or timestamp,
        timestamp,
        item.estado,
    )

    if fila:
        item_id = int(fila["id"])
        conn.execute(
            """
            UPDATE items SET
                fuente=?, tipo=?, nombre=?, descripcion=?, url=?, homepage=?,
                autor=?, licencia=?, lenguaje=?, topics=?, metricas=?,
                creado_en=COALESCE(?, creado_en),
                actualizado_fuente=COALESCE(?, actualizado_fuente),
                ultima_vez_visto=?, estado=?
            WHERE id=?
            """,
            (*datos, item_id),
        )
        es_nueva = False
    else:
        cursor = conn.execute(
            """
            INSERT INTO items (
                uid, slug, fuente, tipo, nombre, descripcion, url, homepage,
                autor, licencia, lenguaje, topics, metricas, creado_en,
                actualizado_fuente, primera_vez_visto, ultima_vez_visto, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.uid,
                item.slug,
                fuente,
                tipo,
                item.nombre,
                item.descripcion,
                item.url,
                item.homepage,
                item.autor,
                item.licencia,
                item.lenguaje,
                json.dumps(topics, ensure_ascii=False),
                json.dumps(metricas, ensure_ascii=False),
                item.creado_en,
                item.actualizado_fuente or timestamp,
                timestamp,
                timestamp,
                item.estado,
            ),
        )
        item_id = int(cursor.lastrowid)
        es_nueva = True

    if categorias is not None:
        conn.execute("DELETE FROM item_categorias WHERE item_id=?", (item_id,))
        for categoria in dict.fromkeys(categorias):
            conn.execute(
                "INSERT OR IGNORE INTO item_categorias (item_id, categoria_id) VALUES (?, ?)",
                (item_id, categoria),
            )

    _fts_actualizar(conn, item_id, item.nombre, item.descripcion, topics)
    return item_id, es_nueva


def guardar_snapshot(
    conn: sqlite3.Connection,
    item_id: int,
    metricas: Mapping[str, float],
    fecha: str | None = None,
) -> None:
    dia = fecha or date.today().isoformat()
    conn.execute(
        """
        INSERT INTO snapshots (item_id, fecha, metricas) VALUES (?, ?, ?)
        ON CONFLICT(item_id, fecha) DO UPDATE SET metricas=excluded.metricas
        """,
        (item_id, dia, json.dumps(dict(metricas), ensure_ascii=False)),
    )


def metricas_previas(
    conn: sqlite3.Connection, item_id: int, dias: int, fecha: str | None = None
) -> dict[str, float] | None:
    objetivo = (date.fromisoformat(fecha) if fecha else date.today()) - timedelta(days=dias)
    fila = conn.execute(
        """
        SELECT metricas FROM snapshots
        WHERE item_id=? AND fecha<=?
        ORDER BY fecha DESC LIMIT 1
        """,
        (item_id, objetivo.isoformat()),
    ).fetchone()
    if fila is None:
        return None
    return _json_dict(fila["metricas"])


def guardar_puntuacion(
    conn: sqlite3.Connection,
    item_id: int,
    score: float,
    crec_7d: float | None,
    crec_30d: float | None,
    fecha: str | None = None,
) -> None:
    dia = fecha or date.today().isoformat()
    conn.execute(
        """
        INSERT INTO puntuaciones (item_id, fecha, score, crec_7d, crec_30d)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_id, fecha) DO UPDATE SET
            score=excluded.score, crec_7d=excluded.crec_7d, crec_30d=excluded.crec_30d
        """,
        (item_id, dia, float(score), crec_7d, crec_30d),
    )


def reindexar_fts(conn: sqlite3.Connection) -> int:
    conn.execute("DELETE FROM items_fts")
    filas = conn.execute("SELECT id, nombre, descripcion, topics FROM items").fetchall()
    for fila in filas:
        topics = " ".join(_json_list(fila["topics"]))
        _fts_insert(conn, int(fila["id"]), fila["nombre"], fila["descripcion"], topics)
    return len(filas)


def _fts_actualizar(
    conn: sqlite3.Connection,
    item_id: int,
    nombre: str,
    descripcion: str,
    topics: Iterable[str],
) -> None:
    conn.execute("DELETE FROM items_fts WHERE item_id=?", (item_id,))
    _fts_insert(conn, item_id, nombre, descripcion, " ".join(topics))


def _fts_insert(
    conn: sqlite3.Connection, item_id: int, nombre: str, descripcion: str, topics: str
) -> None:
    conn.execute(
        "INSERT INTO items_fts (item_id, nombre, descripcion, topics) VALUES (?, ?, ?, ?)",
        (
            item_id,
            normalizar(nombre),
            normalizar(descripcion),
            normalizar(topics),
        ),
    )


# ---------------------------------------------------------------------------
# Lectura


def consulta_fts(texto: str) -> str:
    tokens = [t for t in normalizar(texto).split() if len(t) >= 2][:8]
    return " AND ".join(f'"{token}"*' for token in tokens)


def buscar(
    conn: sqlite3.Connection,
    consulta: str = "",
    categoria: str | None = None,
    fuente: str | None = None,
    tipo: str | None = None,
    orden: str = "relevancia",
    limite: int = 20,
) -> list[dict[str, Any]]:
    limite = max(1, min(int(limite), 200))
    columnas = """
        i.id, i.uid, i.slug, i.fuente, i.tipo, i.nombre, i.descripcion, i.url,
        i.homepage, i.autor, i.licencia, i.lenguaje, i.topics, i.metricas,
        i.creado_en, i.actualizado_fuente, i.primera_vez_visto, i.ultima_vez_visto,
        i.estado, i.origen, p.score, p.crec_7d, p.crec_30d,
        (SELECT GROUP_CONCAT(ic.categoria_id, ',')
           FROM item_categorias ic WHERE ic.item_id = i.id) AS categorias
    """
    ultima_puntuacion = """
        LEFT JOIN (
            SELECT item_id, score, crec_7d, crec_30d FROM (
                SELECT item_id, score, crec_7d, crec_30d,
                       ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY fecha DESC) AS rn
                FROM puntuaciones
            ) WHERE rn = 1
        ) p ON p.item_id = i.id
    """

    fts = consulta_fts(consulta)
    condiciones: list[str] = ["i.aprobado = 1"]
    parametros: list[Any] = []

    if fts:
        origen = "FROM items_fts JOIN items i ON i.id = items_fts.item_id " + ultima_puntuacion
        condiciones.append("items_fts MATCH ?")
        parametros.append(fts)
        rank = ", bm25(items_fts) AS rank"
    else:
        origen = "FROM items i " + ultima_puntuacion
        rank = ", NULL AS rank"

    if categoria:
        condiciones.append(
            "EXISTS (SELECT 1 FROM item_categorias ic "
            "WHERE ic.item_id = i.id AND ic.categoria_id = ?)"
        )
        parametros.append(categoria)
    if fuente:
        condiciones.append("i.fuente = ?")
        parametros.append(fuente)
    if tipo:
        condiciones.append("i.tipo = ?")
        parametros.append(tipo)

    ordenes = {
        "relevancia": "rank ASC NULLS LAST, p.score DESC NULLS LAST, i.nombre ASC",
        "calor": "p.score DESC NULLS LAST, i.nombre ASC",
        "crecimiento": "p.crec_7d DESC NULLS LAST, p.score DESC NULLS LAST",
        "recientes": "i.ultima_vez_visto DESC, p.score DESC",
        "estrellas": (
            "CAST(json_extract(i.metricas, '$.estrellas') AS REAL) DESC NULLS LAST, "
            "p.score DESC NULLS LAST"
        ),
        "descargas": (
            "CAST(json_extract(i.metricas, '$.descargas') AS REAL) DESC NULLS LAST, "
            "p.score DESC NULLS LAST"
        ),
    }
    clausula_orden = ordenes.get(orden, ordenes["relevancia"])
    filtro = " AND ".join(condiciones)

    sql = f"SELECT {columnas}{rank} {origen} WHERE {filtro} ORDER BY {clausula_orden} LIMIT ?"
    parametros.append(limite)

    return [_fila_a_dict(fila) for fila in conn.execute(sql, parametros).fetchall()]


def tendencias(
    conn: sqlite3.Connection,
    periodo: str = "7d",
    fuente: str | None = None,
    categoria: str | None = None,
    orden: str = "calor",
    limite: int = 20,
) -> list[dict[str, Any]]:
    dias = _dias_periodo(periodo)
    desde = (date.today() - timedelta(days=dias)).isoformat()
    limite = max(1, min(int(limite), 200))
    condiciones = ["i.aprobado = 1", "i.ultima_vez_visto >= ?"]
    parametros: list[Any] = [desde]

    if fuente:
        condiciones.append("i.fuente = ?")
        parametros.append(fuente)
    if categoria:
        condiciones.append(
            "EXISTS (SELECT 1 FROM item_categorias ic "
            "WHERE ic.item_id = i.id AND ic.categoria_id = ?)"
        )
        parametros.append(categoria)

    if orden == "crecimiento":
        clausula = "p.crec_7d DESC NULLS LAST, p.score DESC NULLS LAST"
    elif orden == "recientes":
        clausula = "i.primera_vez_visto DESC, p.score DESC NULLS LAST"
    else:
        clausula = "p.score DESC NULLS LAST, i.nombre ASC"

    filtro = " AND ".join(condiciones)
    sql = f"""
        SELECT
            i.id, i.uid, i.slug, i.fuente, i.tipo, i.nombre, i.descripcion, i.url,
            i.homepage, i.autor, i.licencia, i.lenguaje, i.topics, i.metricas,
            i.creado_en, i.actualizado_fuente, i.primera_vez_visto, i.ultima_vez_visto,
            i.estado, i.origen, p.score, p.crec_7d, p.crec_30d,
            (SELECT GROUP_CONCAT(ic.categoria_id, ',')
               FROM item_categorias ic WHERE ic.item_id = i.id) AS categorias
        FROM items i
        LEFT JOIN (
            SELECT item_id, score, crec_7d, crec_30d FROM (
                SELECT item_id, score, crec_7d, crec_30d,
                       ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY fecha DESC) AS rn
                FROM puntuaciones
            ) WHERE rn = 1
        ) p ON p.item_id = i.id
        WHERE {filtro}
        ORDER BY {clausula}
        LIMIT ?
    """
    parametros.append(limite)
    return [_fila_a_dict(f) for f in conn.execute(sql, parametros).fetchall()]


def nuevos(
    conn: sqlite3.Connection, dias: int = 1, limite: int = 20, fuente: str | None = None
) -> list[dict[str, Any]]:
    desde = (date.today() - timedelta(days=max(1, dias))).isoformat()
    condiciones = ["i.aprobado = 1", "i.primera_vez_visto >= ?"]
    parametros: list[Any] = [desde]
    if fuente:
        condiciones.append("i.fuente = ?")
        parametros.append(fuente)
    parametros.append(max(1, min(int(limite), 200)))

    filtro = " AND ".join(condiciones)
    sql = f"""
        SELECT
            i.id, i.uid, i.slug, i.fuente, i.tipo, i.nombre, i.descripcion, i.url,
            i.homepage, i.autor, i.licencia, i.lenguaje, i.topics, i.metricas,
            i.creado_en, i.actualizado_fuente, i.primera_vez_visto, i.ultima_vez_visto,
            i.estado, i.origen, p.score, p.crec_7d, p.crec_30d,
            (SELECT GROUP_CONCAT(ic.categoria_id, ',')
               FROM item_categorias ic WHERE ic.item_id = i.id) AS categorias
        FROM items i
        LEFT JOIN (
            SELECT item_id, score, crec_7d, crec_30d FROM (
                SELECT item_id, score, crec_7d, crec_30d,
                       ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY fecha DESC) AS rn
                FROM puntuaciones
            ) WHERE rn = 1
        ) p ON p.item_id = i.id
        WHERE {filtro}
        ORDER BY p.score DESC NULLS LAST, i.primera_vez_visto DESC
        LIMIT ?
    """
    return [_fila_a_dict(f) for f in conn.execute(sql, parametros).fetchall()]


def ficha(conn: sqlite3.Connection, clave: str) -> dict[str, Any] | None:
    fila = conn.execute(
        """
        SELECT * FROM items
        WHERE uid=? OR slug=? OR url=? OR lower(nombre)=lower(?)
        ORDER BY CASE
            WHEN uid=? THEN 0 WHEN slug=? THEN 1 WHEN url=? THEN 2 ELSE 3
        END, id
        LIMIT 1
        """,
        (clave, clave, clave, clave, clave, clave, clave),
    ).fetchone()
    if fila is None:
        return None

    datos = _fila_a_dict(fila)
    item_id = int(fila["id"])

    datos["categorias_detalle"] = [
        dict(c)
        for c in conn.execute(
            """
            SELECT c.id, c.nombre, c.orden FROM categorias c
            JOIN item_categorias ic ON ic.categoria_id = c.id
            WHERE ic.item_id = ? ORDER BY c.orden
            """,
            (item_id,),
        ).fetchall()
    ]

    datos["historial"] = [
        {"fecha": s["fecha"], **u}
        for s in conn.execute(
            "SELECT fecha, metricas FROM snapshots WHERE item_id=? ORDER BY fecha DESC LIMIT 40",
            (item_id,),
        ).fetchall()
        for u in [_json_dict(s["metricas"])]
    ]

    datos["puntuaciones"] = [
        dict(p)
        for p in conn.execute(
            """
            SELECT fecha, score, crec_7d, crec_30d FROM puntuaciones
            WHERE item_id=? ORDER BY fecha DESC LIMIT 40
            """,
            (item_id,),
        ).fetchall()
    ]
    return datos


def estadisticas(conn: sqlite3.Connection) -> dict[str, Any]:
    hoy = date.today()
    hace_1 = (hoy - timedelta(days=1)).isoformat()
    hace_7 = (hoy - timedelta(days=7)).isoformat()

    total = conn.execute("SELECT COUNT(*) FROM items WHERE aprobado=1").fetchone()[0]
    nuevos_24h = conn.execute(
        "SELECT COUNT(*) FROM items WHERE aprobado=1 AND primera_vez_visto >= ?", (hace_1,)
    ).fetchone()[0]
    nuevos_7d = conn.execute(
        "SELECT COUNT(*) FROM items WHERE aprobado=1 AND primera_vez_visto >= ?", (hace_7,)
    ).fetchone()[0]

    por_fuente = {
        fila["fuente"]: fila["n"]
        for fila in conn.execute(
            "SELECT fuente, COUNT(*) AS n FROM items WHERE aprobado=1 "
            "GROUP BY fuente ORDER BY n DESC"
        ).fetchall()
    }
    por_tipo = {
        fila["tipo"]: fila["n"]
        for fila in conn.execute(
            "SELECT tipo, COUNT(*) AS n FROM items WHERE aprobado=1 GROUP BY tipo ORDER BY n DESC"
        ).fetchall()
    }
    por_categoria = {
        fila["categoria_id"]: fila["n"]
        for fila in conn.execute(
            """
            SELECT ic.categoria_id, COUNT(*) AS n FROM item_categorias ic
            JOIN items i ON i.id = ic.item_id
            WHERE i.aprobado=1 GROUP BY ic.categoria_id ORDER BY n DESC
            """
        ).fetchall()
    }
    aportes_pendientes = conn.execute(
        "SELECT COUNT(*) FROM aportes WHERE estado='pendiente'"
    ).fetchone()[0]

    return {
        "total": total,
        "nuevos_24h": nuevos_24h,
        "nuevos_7d": nuevos_7d,
        "por_fuente": por_fuente,
        "por_tipo": por_tipo,
        "por_categoria": por_categoria,
        "aportes_pendientes": aportes_pendientes,
        "base_de_datos": str(config.ruta_db()),
    }


def listar_fuentes(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    filas = conn.execute(
        """
        SELECT f.*, COALESCE(c.n, 0) AS items
        FROM fuentes f
        LEFT JOIN (SELECT fuente, COUNT(*) AS n FROM items WHERE aprobado=1 GROUP BY fuente) c
          ON c.fuente = f.id
        ORDER BY items DESC, f.nombre
        """
    ).fetchall()
    return [dict(f) for f in filas]


def listar_categorias(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    filas = conn.execute(
        """
        SELECT c.id, c.nombre, c.descripcion, c.orden, COALESCE(n.total, 0) AS items
        FROM categorias c
        LEFT JOIN (
            SELECT ic.categoria_id, COUNT(*) AS total FROM item_categorias ic
            JOIN items i ON i.id = ic.item_id
            WHERE i.aprobado=1 GROUP BY ic.categoria_id
        ) n ON n.categoria_id = c.id
        ORDER BY c.orden
        """
    ).fetchall()
    return [dict(f) for f in filas]


# ---------------------------------------------------------------------------
# Estado de fuentes y eventos


def marcar_fuente(
    conn: sqlite3.Connection,
    fuente: str,
    ok: bool,
    vistos: int = 0,
    error: str | None = None,
) -> None:
    timestamp = iso()
    conn.execute(
        """
        UPDATE fuentes SET
            ultima_ejecucion=?,
            ultimo_ok=CASE WHEN ? THEN ? ELSE ultimo_ok END,
            ultimo_error=?,
            items_vistos=?
        WHERE id=?
        """,
        (timestamp, 1 if ok else 0, timestamp, error, vistos, fuente),
    )


def registrar_evento(
    conn: sqlite3.Connection,
    fuente: str | None,
    nivel: str,
    mensaje: str,
    extra: Mapping[str, Any] | None = None,
) -> None:
    conn.execute(
        "INSERT INTO eventos (fecha, fuente, nivel, mensaje, extra) VALUES (?, ?, ?, ?, ?)",
        (
            iso(),
            fuente,
            nivel,
            mensaje,
            json.dumps(dict(extra), ensure_ascii=False) if extra else None,
        ),
    )


def eventos_recientes(conn: sqlite3.Connection, limite: int = 20) -> list[dict[str, Any]]:
    return [
        dict(f)
        for f in conn.execute(
            "SELECT * FROM eventos ORDER BY id DESC LIMIT ?", (max(1, limite),)
        ).fetchall()
    ]


# ---------------------------------------------------------------------------
# Aportes de usuarios (base para la web)


def crear_aporte(
    conn: sqlite3.Connection,
    nombre: str,
    url: str,
    descripcion: str = "",
    categoria: str | None = None,
    tipo: str = "recurso",
    autor: str | None = None,
    email: str | None = None,
) -> int:
    if not nombre.strip() or not url.strip():
        raise ValueError("nombre y url son obligatorios")
    cursor = conn.execute(
        """
        INSERT INTO aportes (nombre, url, descripcion, categoria, tipo, autor, email, creado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (nombre.strip(), url.strip(), descripcion.strip(), categoria, tipo, autor, email, iso()),
    )
    return int(cursor.lastrowid)


def listar_aportes(
    conn: sqlite3.Connection, estado: str | None = None, limite: int = 100
) -> list[dict[str, Any]]:
    if estado:
        filas = conn.execute(
            "SELECT * FROM aportes WHERE estado=? ORDER BY id DESC LIMIT ?",
            (estado, max(1, limite)),
        ).fetchall()
    else:
        filas = conn.execute(
            "SELECT * FROM aportes ORDER BY id DESC LIMIT ?", (max(1, limite),)
        ).fetchall()
    return [dict(f) for f in filas]


def marcar_aporte(
    conn: sqlite3.Connection, aporte_id: int, estado: str, nota: str | None = None
) -> None:
    if estado not in ("pendiente", "aprobado", "rechazado"):
        raise ValueError("estado invalido")
    conn.execute(
        "UPDATE aportes SET estado=?, revisado_en=?, nota_revision=? WHERE id=?",
        (estado, iso(), nota, aporte_id),
    )


# ---------------------------------------------------------------------------
# Utilidades


def _json_dict(texto: str | None) -> dict[str, float]:
    if not texto:
        return {}
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        return {}
    if not isinstance(datos, dict):
        return {}
    return {k: float(v) for k, v in datos.items() if isinstance(v, (int, float))}


def _json_list(texto: str | None) -> list[str]:
    if not texto:
        return []
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        return []
    return [str(x) for x in datos] if isinstance(datos, list) else []


def _fila_a_dict(fila: sqlite3.Row) -> dict[str, Any]:
    datos = dict(fila)
    datos["topics"] = _json_list(datos.get("topics"))
    datos["metricas"] = _json_dict(datos.get("metricas"))
    if "categorias" in datos:
        crudo = datos.get("categorias") or ""
        datos["categorias"] = [c for c in re.split(r",", crudo) if c]
    return datos


def _dias_periodo(periodo: str) -> int:
    texto = (periodo or "7d").strip().lower()
    equivalencias = {"24h": 1, "dia": 1, "día": 1, "1d": 1, "7d": 7, "30d": 30, "90d": 90}
    if texto in equivalencias:
        return equivalencias[texto]
    match = re.fullmatch(r"(\d+)\s*d", texto)
    if match:
        return max(1, min(int(match.group(1)), 365))
    return 7
