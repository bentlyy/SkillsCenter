from skill_radar.models import Item, normalizar, slug_unico


def test_normalizar_quita_acentos_y_puntuacion():
    assert normalizar("Programación de AGENTES, nivel 2") == "programacion de agentes nivel 2"


def test_slug_es_estable_y_evita_colisiones():
    uno = slug_unico("Servidor MCP", "github:a/b")
    otro = slug_unico("Servidor MCP", "github:c/d")
    assert uno == slug_unico("Servidor MCP", "github:a/b")
    assert uno != otro
    assert uno.startswith("servidor-mcp-")


def test_item_normaliza_campos():
    item = Item(
        uid="  github:a/b ",
        fuente="github",
        tipo="inventado",
        nombre="  ",
        url="https://github.com/a/b",
        descripcion="muchos   espacios\n\ny saltos",
        topics=["mcp", "", " mcp ", "rag"],
        metricas={"estrellas": 10, "texto": "x"},
    )
    assert item.uid == "github:a/b"
    assert item.nombre == "github:a/b"
    assert item.tipo == "recurso"
    assert item.descripcion == "muchos espacios y saltos"
    assert item.topics == ["mcp", "mcp", "rag"]
    assert item.metricas == {"estrellas": 10.0}
