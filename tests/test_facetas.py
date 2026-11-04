from skill_radar import facetas


def test_tipo_agente_por_nombre_y_categoria():
    assert (
        facetas.clasificar_tipo(
            "CowAgent",
            "Open-source personal AI assistant & Agent Harness.",
            "repo",
            ["ai-agent"],
            "agentes",
        )
        == "agente"
    )


def test_tipo_modelo_no_se_confunde_con_mcp():
    assert (
        facetas.clasificar_tipo(
            "MiniCPM4-MCP-i1-GGUF",
            "",
            "modelo",
            ["gguf", "mcp"],
            "modelos",
        )
        == "modelo"
    )


def test_tipo_prompt_y_skill():
    assert facetas.clasificar_tipo("awesome-prompts", "Curated prompts", "repo") == "prompt"
    assert facetas.clasificar_tipo("skillfish", "Skill manager para agentes", "paquete") == "skill"


def test_tipo_script_no_confunde_client():
    assert facetas.clasificar_tipo("foo", "HTTP client for the API", "paquete") == "paquete"
    assert facetas.clasificar_tipo("foo-cli", "Command line tool", "paquete") == "script"


def test_tipo_articulo_y_mcp():
    assert facetas.clasificar_tipo("Nueva noticia", "", "noticia") == "articulo"
    assert facetas.clasificar_tipo("weather-mcp", "Servidor MCP del clima", "mcp_server") == "mcp"


def test_usos_son_ortogonales_al_tipo():
    usos = facetas.clasificar_usos(
        "code-agent",
        "Agente autonomo que escribe codigo y revisa tests",
        "repo",
        ["agent", "code"],
        "agentes",
    )
    assert "codigo" in usos
    assert len(usos) <= 3


def test_usos_prompt_y_modelo():
    prompts = facetas.clasificar_usos(
        "prompt-library", "Biblioteca de prompts para agentes", "repo", ["prompt"], "skills"
    )
    assert prompts[0] == "prompts"

    datos = facetas.clasificar_usos(
        "bge-base", "", "modelo", ["feature-extraction", "sentence-similarity"], "modelos"
    )
    assert "datos" in datos or "investigacion" in datos


def test_usos_nunca_vacio():
    for tipo in (
        "agente",
        "modelo",
        "mcp_server",
        "skill",
        "prompt",
        "paquete",
        "repo",
        "post",
        "noticia",
        "recurso",
    ):
        usos = facetas.clasificar_usos("x", "", tipo, [], "otros")
        assert usos
        assert set(usos) <= {u["id"] for u in facetas.USOS}
