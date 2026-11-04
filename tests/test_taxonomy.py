from skill_radar.models import Item
from skill_radar.taxonomy import clasificar


def _item(nombre, descripcion="", topics=None, tipo="recurso"):
    return Item(
        uid=f"test:{nombre}",
        fuente="github",
        tipo=tipo,
        nombre=nombre,
        url="https://example.com",
        descripcion=descripcion,
        topics=topics or [],
    )


def test_servidor_mcp_va_a_mcp():
    categorias = clasificar(_item("inspector", "MCP server para depurar", tipo="mcp_server"))
    assert categorias[0] == "mcp"


def test_skill_va_a_skills():
    categorias = clasificar(_item("pdf", "Claude skill para leer PDFs", tipo="skill"))
    assert "skills" in categorias


def test_clasifica_por_topic_y_descripcion():
    categorias = clasificar(_item("nano", "motor de agentes autonomos con rag"))
    assert "agentes" in categorias
    assert "rag" in categorias


def test_sin_pistas_cae_en_otros():
    assert clasificar(_item("cosa rara", "nada relevante")) == ["otros"]


def test_maximo_tres_categorias():
    item = _item(
        "todo",
        "mcp agent skill rag code image audio video data infra model automation eval search",
    )
    assert len(clasificar(item)) <= 3
