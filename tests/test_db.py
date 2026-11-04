import json

import pytest

from skill_radar import db
from skill_radar.models import Item


@pytest.fixture
def conn(tmp_path):
    conexion = db.conectar(tmp_path / "radar.db")
    db.inicializar(conexion)
    yield conexion
    conexion.close()


def _item(nombre="foo/bar", uid="github:foo/bar", fuente="github", **extra):
    datos = {
        "uid": uid,
        "fuente": fuente,
        "tipo": "repo",
        "nombre": nombre,
        "url": f"https://example.com/{nombre}",
        "descripcion": "Biblioteca de agentes",
        "topics": ["mcp"],
        "metricas": {"estrellas": 100},
    }
    datos.update(extra)
    return Item(**datos)


def test_inicializar_siembra_fuentes_y_categorias(conn):
    fuentes = db.listar_fuentes(conn)
    categorias = db.listar_categorias(conn)
    assert {f["id"] for f in fuentes} >= {"github", "reddit", "pypi"}
    assert {"mcp", "agentes", "otros"} <= {c["id"] for c in categorias}


def test_upsert_es_idempotente(conn):
    item = _item()
    primero, nueva1 = db.upsert_item(conn, item, ["agentes"])
    segundo, nueva2 = db.upsert_item(conn, item, ["agentes"])
    assert (primero, nueva1) == (segundo, True)
    assert nueva2 is False
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1


def test_fuente_sin_metricas_no_pisa_las_metricas_de_github(conn):
    completo = _item(topics=["mcp"], metricas={"estrellas": 5000})
    db.upsert_item(conn, completo, ["mcp"])

    pobre = _item(fuente="awesome", topics=["awesome-mcp"], metricas={})
    db.upsert_item(conn, pobre, ["mcp"])

    fila = conn.execute("SELECT fuente, topics, metricas FROM items").fetchone()
    assert fila["fuente"] == "github"
    assert "awesome-mcp" in json.loads(fila["topics"])
    assert json.loads(fila["metricas"])["estrellas"] == 5000


def test_snapshot_por_dia_es_unico(conn):
    item_id, _ = db.upsert_item(conn, _item(), ["agentes"])
    db.guardar_snapshot(conn, item_id, {"estrellas": 10}, "2026-01-01")
    db.guardar_snapshot(conn, item_id, {"estrellas": 20}, "2026-01-01")
    filas = conn.execute("SELECT metricas FROM snapshots").fetchall()
    assert len(filas) == 1
    assert json.loads(filas[0]["metricas"])["estrellas"] == 20


def test_busqueda_ignora_acentos_y_usa_prefijos(conn):
    db.upsert_item(conn, _item(nombre="Programación", descripcion="Agentes autónomos"), ["agentes"])
    assert db.buscar(conn, "programacion")[0]["nombre"] == "Programación"
    assert db.buscar(conn, "agent")[0]["nombre"] == "Programación"


def test_busqueda_filtra_por_fuente_y_categoria(conn):
    db.upsert_item(conn, _item(nombre="uno", uid="github:uno"), ["agentes"])
    db.upsert_item(
        conn,
        _item(nombre="dos", uid="mcp:dos", fuente="mcp_registry", tipo="mcp_server"),
        ["mcp"],
    )
    assert [i["nombre"] for i in db.buscar(conn, categoria="mcp")] == ["dos"]
    assert [i["nombre"] for i in db.buscar(conn, fuente="github")] == ["uno"]


def test_orden_por_calor(conn):
    a, _ = db.upsert_item(conn, _item(nombre="a", uid="github:a"), ["agentes"])
    b, _ = db.upsert_item(conn, _item(nombre="b", uid="github:b"), ["agentes"])
    db.guardar_puntuacion(conn, a, 10.0, None, None)
    db.guardar_puntuacion(conn, b, 90.0, None, None)
    assert [i["nombre"] for i in db.buscar(conn, orden="calor")] == ["b", "a"]


def test_consulta_fts_escapa_simbolos():
    assert db.consulta_fts('mcp "server" AND (x)') == '"mcp"* AND "server"* AND "and"*'
    assert db.consulta_fts("!!! ???") == ""


def test_ficha_incluye_historial_y_categorias(conn):
    item_id, _ = db.upsert_item(conn, _item(), ["agentes"])
    db.guardar_snapshot(conn, item_id, {"estrellas": 100}, "2026-01-01")
    db.guardar_puntuacion(conn, item_id, 42.0, 0.1, None, "2026-01-01")

    datos = db.ficha(conn, "foo/bar")
    assert datos is not None
    assert datos["historial"][0]["estrellas"] == 100
    assert datos["puntuaciones"][0]["score"] == 42.0
    assert datos["categorias_detalle"][0]["id"] == "agentes"


def test_aportes_de_usuarios(conn):
    aporte_id = db.crear_aporte(
        conn, "Mi skill", "https://example.com/skill", "hace cosas", categoria="skills"
    )
    assert db.listar_aportes(conn, estado="pendiente")[0]["id"] == aporte_id
    db.marcar_aporte(conn, aporte_id, "aprobado", "ok")
    assert db.listar_aportes(conn, estado="aprobado")[0]["nota_revision"] == "ok"
    with pytest.raises(ValueError):
        db.marcar_aporte(conn, aporte_id, "inventado")


def test_reindexar_fts(conn):
    db.upsert_item(conn, _item(descripcion="recuperacion aumentada"), ["rag"])
    assert db.reindexar_fts(conn) == 1
    assert db.buscar(conn, "recuperacion")
