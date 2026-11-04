"""Dos ejes independientes para el buscador: que es y para que sirve.

El `tipo` describe la forma del artefacto (agente, modelo, servidor MCP, skill,
prompt, script, paquete...). El `uso` describe la tarea que resuelve (codigo,
prompts, investigacion, datos...). Son ortogonales: un agente puede servir para
codigo y un modelo puede servir para imagen.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .models import normalizar

TIPOS: tuple[dict[str, Any], ...] = (
    {
        "id": "agente",
        "nombre": "Agente",
        "descripcion": "Frameworks y orquestadores que ejecutan tareas",
        "alias": (
            "agent",
            "agents",
            "agente",
            "agentes",
            "autonomo",
            "orquestador",
            "ia",
        ),
    },
    {
        "id": "modelo",
        "nombre": "Modelo",
        "descripcion": "LLMs, embeddings y modelos especializados",
        "alias": ("model", "models", "modelo", "modelos", "llm", "embeddings", "ia"),
    },
    {
        "id": "mcp",
        "nombre": "MCP",
        "descripcion": "Servidores, clientes y SDKs del protocolo MCP",
        "alias": ("mcp", "servidor mcp", "model context protocol", "mcp server", "ia"),
    },
    {
        "id": "skill",
        "nombre": "Skill",
        "descripcion": "Habilidades empaquetadas para agentes",
        "alias": ("skill", "skills", "habilidad", "habilidades", "ia"),
    },
    {
        "id": "prompt",
        "nombre": "Prompt",
        "descripcion": "Plantillas, librerías y sistemas de prompts",
        "alias": ("prompt", "prompts", "instrucciones", "prompt library", "ia"),
    },
    {
        "id": "script",
        "nombre": "Script / CLI",
        "descripcion": "Herramientas de terminal, scripts y automatizaciones",
        "alias": ("script", "scripts", "cli", "command line", "terminal"),
    },
    {
        "id": "paquete",
        "nombre": "Paquete",
        "descripcion": "Librerías y paquetes instalables",
        "alias": ("paquete", "package", "libreria", "library", "npm", "pypi"),
    },
    {
        "id": "articulo",
        "nombre": "Artículo",
        "descripcion": "Noticias, posts y contenido editorial",
        "alias": ("articulo", "noticia", "post", "blog", "news"),
    },
    {
        "id": "herramienta",
        "nombre": "Herramienta",
        "descripcion": "Repos, apps y utilidades sin categoria mas especifica",
        "alias": ("herramienta", "tool", "repo", "repositorio", "app", "ia"),
    },
    {
        "id": "recurso",
        "nombre": "Recurso",
        "descripcion": "Enlaces y material de apoyo",
        "alias": ("recurso", "resource", "material", "enlace"),
    },
)

USOS: tuple[dict[str, Any], ...] = (
    {
        "id": "codigo",
        "nombre": "Código",
        "descripcion": "Escribir, revisar, probar o desplegar código",
        "alias": ("programar", "escribir codigo", "desarrollo", "programacion", "developer"),
    },
    {
        "id": "prompts",
        "nombre": "Prompts",
        "descripcion": "Crear, organizar o mejorar instrucciones",
        "alias": ("crear prompts", "disenar prompts", "instrucciones", "prompt engineering"),
    },
    {
        "id": "investigacion",
        "nombre": "Investigación",
        "descripcion": "Buscar, leer, recuperar y sintetizar información",
        "alias": ("investigar", "buscar informacion", "research", "rag", "busqueda"),
    },
    {
        "id": "datos",
        "nombre": "Datos",
        "descripcion": "Analizar, transformar y consultar datos",
        "alias": ("analizar datos", "analisis de datos", "sql", "etl", "dataframe"),
    },
    {
        "id": "automatizacion",
        "nombre": "Automatización",
        "descripcion": "Orquestar tareas, agentes y flujos de trabajo",
        "alias": ("automatizar", "flujo de trabajo", "workflow", "agente", "agents"),
    },
    {
        "id": "contenido",
        "nombre": "Contenido",
        "descripcion": "Escribir, resumir, traducir y conversar",
        "alias": ("escribir", "redactar", "texto", "documentacion", "chat"),
    },
    {
        "id": "imagen",
        "nombre": "Imagen",
        "descripcion": "Generar, editar o analizar imágenes",
        "alias": ("generar imagenes", "editar imagenes", "vision", "image"),
    },
    {
        "id": "audio",
        "nombre": "Audio y voz",
        "descripcion": "Voz, transcripción, música y sonido",
        "alias": ("voz", "hablar", "transcribir", "speech", "tts"),
    },
    {
        "id": "video",
        "nombre": "Video",
        "descripcion": "Generar, editar o animar vídeo",
        "alias": ("generar video", "editar video", "animacion", "film"),
    },
    {
        "id": "diseno",
        "nombre": "Diseño",
        "descripcion": "Interfaces, componentes y sistemas visuales",
        "alias": ("disenar", "interfaz", "ui", "ux", "frontend"),
    },
    {
        "id": "infraestructura",
        "nombre": "Infraestructura",
        "descripcion": "Desplegar, servir y operar modelos",
        "alias": ("desplegar", "servidor", "gpu", "docker", "cloud"),
    },
    {
        "id": "evaluacion",
        "nombre": "Evaluación",
        "descripcion": "Medir, probar y monitorear calidad",
        "alias": ("evaluar", "medir", "benchmark", "testing", "calidad"),
    },
    {
        "id": "integracion",
        "nombre": "Integración",
        "descripcion": "Conectar APIs, plugins, datos y servicios",
        "alias": ("conectar", "api", "plugin", "webhook", "integrar"),
    },
    {
        "id": "general",
        "nombre": "General",
        "descripcion": "Utilidad transversal sin uso dominante",
        "alias": ("otros", "general", "multiproposito"),
    },
)


def _n(texto: str) -> str:
    return normalizar(texto)


CLAVES_PROMPT = tuple(
    _n(c)
    for c in (
        "prompt library",
        "prompt libraries",
        "prompt management",
        "system prompt",
        "system prompts",
        "prompt template",
        "prompt templates",
        "prompt collection",
        "prompts for",
    )
)

CLAVES_AGENTE = tuple(
    _n(c)
    for c in (
        "agent framework",
        "agent platform",
        "agent orchestration",
        "ai agent",
        "autonomous agent",
        "autonomous agents",
        "multi agent",
        "multiagent",
    )
)

CLAVES_SCRIPT = tuple(
    _n(c) for c in ("cli", "command line", "command-line", "shell", "script", "scripts", "terminal")
)

CATEGORIA_USOS: dict[str, tuple[str, ...]] = {
    "mcp": ("integracion",),
    "agentes": ("automatizacion", "codigo"),
    "skills": ("prompts", "contenido"),
    "rag": ("investigacion", "datos"),
    "programacion": ("codigo",),
    "imagen": ("imagen", "diseno"),
    "audio": ("audio",),
    "video": ("video",),
    "datos": ("datos", "investigacion"),
    "infra": ("infraestructura",),
    "modelos": (),
    "automatizacion": ("automatizacion",),
    "evaluacion": ("evaluacion",),
    "busqueda": ("investigacion",),
    "otros": (),
}

CLAVES_USO: dict[str, tuple[str, ...]] = {
    "codigo": tuple(
        _n(c)
        for c in (
            "code",
            "coding",
            "programming",
            "developer",
            "developers",
            "ide",
            "codegen",
            "copilot",
            "refactor",
            "debug",
            "debugging",
            "code review",
            "unit test",
            "testing framework",
            "sdk",
            "typescript",
            "python",
            "javascript",
            "rust",
            "golang",
            "cli",
        )
    ),
    "prompts": tuple(
        _n(c)
        for c in (
            "prompt",
            "prompts",
            "prompt engineering",
            "system prompt",
            "prompt library",
            "prompt management",
            "prompt template",
            "instruction",
            "instructions",
            "jailbreak",
        )
    ),
    "investigacion": tuple(
        _n(c)
        for c in (
            "research",
            "search",
            "browser",
            "browsing",
            "crawler",
            "crawling",
            "rag",
            "retrieval",
            "knowledge base",
            "memory",
            "semantic search",
            "web search",
            "arxiv",
            "paper",
            "papers",
            "documentation",
            "research assistant",
        )
    ),
    "datos": tuple(
        _n(c)
        for c in (
            "data",
            "analytics",
            "database",
            "sql",
            "pandas",
            "etl",
            "dataframe",
            "dataset",
            "datasets",
            "scraping",
            "scraper",
            "business intelligence",
            "vector database",
            "embeddings",
            "feature extraction",
            "sentence similarity",
            "text embeddings",
            "token classification",
            "fill mask",
            "zero shot classification",
            "csv",
        )
    ),
    "automatizacion": tuple(
        _n(c)
        for c in (
            "automation",
            "workflow",
            "workflows",
            "n8n",
            "zapier",
            "rpa",
            "agent",
            "agents",
            "agentic",
            "orchestration",
            "orchestrator",
            "multi agent",
            "pipeline",
            "integration",
        )
    ),
    "contenido": tuple(
        _n(c)
        for c in (
            "writing",
            "content",
            "blog",
            "copywriting",
            "copy",
            "documentation",
            "docs",
            "chat",
            "assistant",
            "presentation",
            "slides",
            "seo",
            "marketing",
            "summarization",
            "translation",
            "text generation",
            "image text to text",
            "question answering",
        )
    ),
    "imagen": tuple(
        _n(c)
        for c in (
            "image",
            "images",
            "diffusion",
            "stable diffusion",
            "vision",
            "image generation",
            "text to image",
            "flux",
            "midjourney",
            "photo",
            "ocr",
            "segmentation",
            "object detection",
            "text to image",
            "image segmentation",
            "image classification",
        )
    ),
    "audio": tuple(
        _n(c)
        for c in (
            "audio",
            "voice",
            "speech",
            "tts",
            "asr",
            "whisper",
            "music",
            "transcription",
            "text to speech",
            "speech recognition",
            "automatic speech recognition",
            "sound",
        )
    ),
    "video": tuple(
        _n(c)
        for c in (
            "video",
            "videos",
            "animation",
            "avatar",
            "text to video",
            "video generation",
            "film",
        )
    ),
    "diseno": tuple(
        _n(c)
        for c in (
            "design",
            "ui",
            "ux",
            "tailwind",
            "css",
            "figma",
            "component",
            "components",
            "shadcn",
            "layout",
            "typography",
            "frontend",
        )
    ),
    "infraestructura": tuple(
        _n(c)
        for c in (
            "inference",
            "serving",
            "gpu",
            "cuda",
            "deploy",
            "deployment",
            "docker",
            "kubernetes",
            "observability",
            "llmops",
            "local llm",
            "quantization",
            "fine tuning",
            "cloud",
            "self hosted",
        )
    ),
    "evaluacion": tuple(
        _n(c)
        for c in (
            "eval",
            "evaluation",
            "benchmark",
            "benchmarks",
            "testing",
            "test",
            "guardrails",
            "red teaming",
            "monitoring",
            "metrics",
            "tracing",
        )
    ),
    "integracion": tuple(
        _n(c)
        for c in (
            "mcp",
            "api",
            "connector",
            "integration",
            "plugin",
            "plugins",
            "sdk",
            "client",
            "adapter",
            "webhook",
            "slack",
            "twilio",
            "notion",
            "database",
        )
    ),
}

FALLBACK_USO = {
    "agente": "automatizacion",
    "modelo": "contenido",
    "mcp": "integracion",
    "skill": "prompts",
    "prompt": "prompts",
    "script": "codigo",
    "paquete": "general",
    "articulo": "investigacion",
    "herramienta": "codigo",
    "recurso": "general",
}

_ORDEN_USO = {u["id"]: i for i, u in enumerate(USOS)}


def _texto(
    nombre: str,
    descripcion: str,
    topics: Sequence[str],
    categoria: str,
) -> str:
    return _n(" ".join([nombre, descripcion or "", *topics, categoria or ""]))


def clasificar_tipo(
    nombre: str,
    descripcion: str = "",
    tipo: str = "recurso",
    topics: Sequence[str] = (),
    categoria: str = "",
) -> str:
    """Devuelve el id del tipo de artefacto mas probable."""
    nombre_n = _n(nombre)
    desc_n = _n(descripcion)
    topics_n = _n(" ".join(topics))
    cat_n = _n(categoria)
    texto = f"{nombre_n} {desc_n} {topics_n} {cat_n}"

    if tipo in {"post", "noticia"}:
        return "articulo"
    if tipo == "modelo" or cat_n == "modelos":
        return "modelo"
    if tipo == "mcp_server" or cat_n == "mcp" or "mcp" in nombre_n.split():
        return "mcp"

    if "prompt" in nombre_n or any(clave in desc_n for clave in CLAVES_PROMPT):
        return "prompt"
    if tipo == "skill" or "skill" in nombre_n or cat_n == "skills":
        return "skill"
    if cat_n == "agentes" or "agent" in nombre_n or any(clave in desc_n for clave in CLAVES_AGENTE):
        return "agente"
    tokens = set(f"{nombre_n} {desc_n}".split())
    if any(clave in texto if " " in clave else clave in tokens for clave in CLAVES_SCRIPT):
        return "script"
    if tipo == "paquete":
        return "paquete"
    if tipo == "repo":
        return "herramienta"
    return "recurso"


def clasificar_usos(
    nombre: str,
    descripcion: str = "",
    tipo: str = "recurso",
    topics: Sequence[str] = (),
    categoria: str = "",
    maximo: int = 3,
) -> list[str]:
    """Devuelve hasta `maximo` usos ordenados por afinidad, nunca una lista vacia."""
    texto = _texto(nombre, descripcion, topics, categoria)
    tokens = set(texto.split())
    puntajes: dict[str, float] = {}

    for uso in CATEGORIA_USOS.get(_n(categoria), ()):
        puntajes[uso] = puntajes.get(uso, 0.0) + 2.0

    for uso, claves in CLAVES_USO.items():
        for clave in claves:
            if " " in clave:
                if clave in texto:
                    puntajes[uso] = puntajes.get(uso, 0.0) + 1.5
            elif clave in tokens:
                puntajes[uso] = puntajes.get(uso, 0.0) + 1.0

    if tipo == "mcp_server":
        puntajes["integracion"] = puntajes.get("integracion", 0.0) + 2.0
    elif tipo == "skill":
        puntajes["prompts"] = puntajes.get("prompts", 0.0) + 1.0
    elif tipo in {"post", "noticia"}:
        puntajes["investigacion"] = puntajes.get("investigacion", 0.0) + 0.5

    elegidos = sorted(
        (uso for uso, puntos in puntajes.items() if puntos > 0),
        key=lambda uso: (-puntajes[uso], _ORDEN_USO.get(uso, 99)),
    )[:maximo]
    return elegidos or [FALLBACK_USO.get(tipo, "general")]


def definiciones() -> dict[str, Any]:
    """Definiciones serializables para la web."""
    return {
        "tipos": [dict(tipo) | {"alias": list(tipo["alias"])} for tipo in TIPOS],
        "usos": [dict(uso) | {"alias": list(uso["alias"])} for uso in USOS],
    }


__all__ = [
    "CATEGORIA_USOS",
    "FALLBACK_USO",
    "TIPOS",
    "USOS",
    "clasificar_tipo",
    "clasificar_usos",
    "definiciones",
]
