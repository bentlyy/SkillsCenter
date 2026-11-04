from datetime import date, timedelta

from skillscenter.models import Item
from skillscenter.scoring import (
    crecimiento_pct,
    factor_crecimiento,
    factor_frescura,
    heat,
    log_norm,
    metrica_principal,
)


def _item(estrellas=0, fuente="github", actualizado=None, **metricas):
    return Item(
        uid=f"{fuente}:x/{estrellas}",
        fuente=fuente,
        tipo="repo",
        nombre="x",
        url="https://example.com",
        metricas={"estrellas": estrellas, **metricas},
        actualizado_fuente=actualizado,
    )


def test_metrica_principal_elige_la_mejor():
    assert metrica_principal({"estrellas": 10, "descargas": 500}) == 500
    assert metrica_principal({}) == 0


def test_log_norm_es_monotona_y_tope():
    assert log_norm(0) == 0.0
    assert log_norm(100) < log_norm(1000) < log_norm(100_000)
    assert log_norm(10_000_000) == 1.0


def test_mas_estrellas_implica_mas_calor():
    flojo = heat(_item(10), None, hoy=date(2026, 1, 1))
    fuerte = heat(_item(50_000), None, hoy=date(2026, 1, 1))
    assert fuerte > flojo


def test_crecimiento_y_frescura_afectan_el_score():
    base = _item(1000, actualizado="2024-01-01")
    caliente = heat(base, 0.8, hoy=date(2026, 1, 1))
    frio = heat(base, -0.2, hoy=date(2026, 1, 1))
    assert caliente > frio

    reciente = _item(1000, actualizado="2025-12-30")
    viejo = _item(1000, actualizado="2023-01-01")
    assert heat(reciente, None, hoy=date(2026, 1, 1)) > heat(viejo, None, hoy=date(2026, 1, 1))


def test_factor_frescura_sin_fecha_es_neutro():
    assert factor_frescura(None) == 0.4
    assert factor_frescura(date.today().isoformat()) > 0.99


def test_factor_crecimiento_acotado():
    assert factor_crecimiento(None) == 0.167
    assert factor_crecimiento(-5) == 0.0
    assert factor_crecimiento(10) == 1.0


def test_crecimiento_pct():
    assert crecimiento_pct(120, 100) == 0.2
    assert crecimiento_pct(50, 100) == -0.5
    assert crecimiento_pct(100, None) is None
    assert crecimiento_pct(100, 0) is None


def test_dias_negativos_no_rompen_frescura():
    futuro = (date.today() + timedelta(days=5)).isoformat()
    assert factor_frescura(futuro) == 1.0
