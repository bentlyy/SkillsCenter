from datetime import date

import pytest

from skillscenter import db
from skillscenter.models import Item
from skillscenter.pipeline import _guardar


@pytest.fixture
def conn(tmp_path):
    conexion = db.conectar(tmp_path / "radar.db")
    db.inicializar(conexion)
    yield conexion
    conexion.close()


def _item(estrellas):
    return Item(
        uid="github:foo/bar",
        fuente="github",
        tipo="repo",
        nombre="foo/bar",
        url="https://github.com/foo/bar",
        descripcion="agentes con mcp",
        topics=["mcp"],
        metricas={"estrellas": estrellas},
        actualizado_fuente="2026-01-08T00:00:00+00:00",
    )


def test_guardar_calcula_crecimiento_con_historico(conn):
    _guardar(conn, [_item(100)], date(2026, 1, 1))
    _guardar(conn, [_item(250)], date(2026, 1, 8))

    fila = conn.execute(
        "SELECT crec_7d, score FROM puntuaciones ORDER BY fecha DESC LIMIT 1"
    ).fetchone()
    assert fila["crec_7d"] == pytest.approx(1.5)
    assert fila["score"] > 0

    snapshots = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    assert snapshots == 2


def test_guardar_no_duplica_si_se_ejecuta_dos_veces_el_mismo_dia(conn):
    _guardar(conn, [_item(100)], date(2026, 1, 1))
    _guardar(conn, [_item(110)], date(2026, 1, 1))
    assert conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1
