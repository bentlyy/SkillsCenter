#!/usr/bin/env python3
"""Busqueda literal y conceptual sobre el catalogo de SkillsCenter.

Funciona sin dependencias externas. Lee, en este orden: el `catalogo.js`
exportado por el proyecto, un CSV del catalogo o la base SQLite en modo lectura.

Ejemplos:
    python skill_finder.py "quiero armar una pagina web"
    python skill_finder.py "mcp postgres" --tipo mcp --limite 5
    python skill_finder.py "agentes" --concepto automatizacion --json
    python skill_finder.py --stats
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from typing import Any

STOP = {
    "necesito",
    "quiero",
    "busco",
    "buscar",
    "algo",
    "una",
    "un",
    "que",
    "haga",
    "hacer",
    "sirva",
    "sirve",
    "para",
    "de",
    "del",
    "la",
    "el",
    "los",
    "las",
    "en",
    "con",
    "por",
    "mi",
    "me",
    "y",
    "o",
    "u",
    "como",
    "donde",
    "cual",
    "cuales",
    "es",
    "son",
    "herramienta",
    "herramientas",
    "tool",
    "tools",
    "the",
    "a",
    "an",
    "for",
    "to",
    "with",
    "that",
    "does",
    "do",
    "i",
    "need",
    "want",
    "looking",
    "make",
    "using",
    "use",
}

TIPOS: dict[str, dict[str, Any]] = {
    "agente": {
        "nombre": "Agente",
        "alias": ["agent", "agents", "agente", "agentes", "autonomo", "orquestador"],
    },
    "modelo": {"nombre": "Modelo", "alias": ["model", "models", "llm", "embeddings"]},
    "mcp": {
        "nombre": "MCP",
        "alias": ["mcp", "servidor mcp", "model context protocol", "mcp server"],
    },
    "skill": {"nombre": "Skill", "alias": ["skill", "skills", "habilidad", "habilidades"]},
    "prompt": {"nombre": "Prompt", "alias": ["prompt", "prompts", "instrucciones"]},
    "script": {"nombre": "Script", "alias": ["script", "cli", "command line", "terminal"]},
    "paquete": {"nombre": "Paquete", "alias": ["paquete", "package", "libreria", "library"]},
    "articulo": {"nombre": "Articulo", "alias": ["articulo", "noticia", "post", "blog"]},
    "herramienta": {"nombre": "Herramienta", "alias": ["herramienta", "tool", "repo", "app"]},
    "recurso": {"nombre": "Recurso", "alias": ["recurso", "resource", "material"]},
}

USOS: dict[str, dict[str, Any]] = {
    "codigo": {
        "nombre": "Codigo",
        "alias": ["code", "coding", "programming", "developer", "ide", "sdk"],
    },
    "prompts": {
        "nombre": "Prompts",
        "alias": ["prompt", "prompts", "instrucciones", "prompt engineering"],
    },
    "investigacion": {
        "nombre": "Investigacion",
        "alias": ["research", "search", "rag", "retrieval", "knowledge base", "memory"],
    },
    "datos": {
        "nombre": "Datos",
        "alias": ["data", "sql", "etl", "dataframe", "analytics", "database"],
    },
    "automatizacion": {
        "nombre": "Automatizacion",
        "alias": ["automation", "workflow", "agents", "orchestration", "pipeline"],
    },
    "contenido": {
        "nombre": "Contenido",
        "alias": ["writing", "content", "docs", "chat", "summarization", "translation"],
    },
    "imagen": {
        "nombre": "Imagen",
        "alias": ["image", "images", "vision", "diffusion", "text to image"],
    },
    "audio": {
        "nombre": "Audio",
        "alias": ["audio", "voice", "speech", "tts", "asr", "whisper"],
    },
    "video": {"nombre": "Video", "alias": ["video", "animation", "avatar", "text to video"]},
    "diseno": {
        "nombre": "Diseno",
        "alias": ["design", "ui", "ux", "frontend", "css", "tailwind", "components"],
    },
    "infraestructura": {
        "nombre": "Infraestructura",
        "alias": ["inference", "serving", "gpu", "deploy", "docker", "llmops"],
    },
    "evaluacion": {
        "nombre": "Evaluacion",
        "alias": ["eval", "evaluation", "benchmark", "testing", "guardrails"],
    },
    "integracion": {
        "nombre": "Integracion",
        "alias": ["api", "connector", "integration", "plugin", "webhook", "mcp"],
    },
    "general": {"nombre": "General", "alias": ["otros", "general", "multiproposito"]},
}

FUENTES = {
    "github": "GitHub",
    "mcp_registry": "Registro MCP",
    "awesome": "Listas curadas",
    "hackernews": "Hacker News",
    "reddit": "Reddit",
    "pypi": "PyPI",
    "npm": "npm",
    "huggingface": "Hugging Face",
}

CATEGORIA_ALIAS = {
    "mcp": "mcp",
    "agentes": "agentes",
    "skills y prompts": "skills",
    "rag y memoria": "rag",
    "programacion": "programacion",
    "imagen": "imagen",
    "audio y voz": "audio",
    "video": "video",
    "datos y analisis": "datos",
    "infraestructura": "infra",
    "modelos": "modelos",
    "automatizacion": "automatizacion",
    "evaluacion": "evaluacion",
    "busqueda y navegacion": "busqueda",
    "otros": "otros",
}

CATEGORIA_USOS = {
    "mcp": ["integracion"],
    "agentes": ["automatizacion", "codigo"],
    "skills": ["prompts", "contenido"],
    "rag": ["investigacion", "datos"],
    "programacion": ["codigo"],
    "imagen": ["imagen", "diseno"],
    "audio": ["audio"],
    "video": ["video"],
    "datos": ["datos", "investigacion"],
    "infra": ["infraestructura"],
    "modelos": [],
    "automatizacion": ["automatizacion"],
    "evaluacion": ["evaluacion"],
    "busqueda": ["investigacion"],
    "otros": [],
}

INTENCIONES: list[dict[str, Any]] = [
    {
        "id": "web",
        "nombre": "Diseñar una web",
        "descripcion": "Landings, interfaces y componentes.",
        "consulta": "diseño de páginas web",
        "frases": [
            "diseno de paginas web",
            "diseno web",
            "pagina web",
            "paginas web",
            "landing page",
            "sitio web",
            "aplicacion web",
            "interfaz web",
            "disenar una web",
        ],
        "terminos": [
            "web",
            "landing",
            "frontend",
            "front-end",
            "html",
            "css",
            "react",
            "vue",
            "svelte",
            "tailwind",
            "figma",
            "interfaz",
            "componente",
            "componentes",
            "ui",
            "ux",
            "design",
            "diseno",
            "disenar",
            "shadcn",
        ],
        "usos": ["diseno", "codigo"],
        "tipos": ["skill", "herramienta", "agente"],
    },
    {
        "id": "datos",
        "nombre": "Modelar una base de datos",
        "descripcion": "Esquemas, SQL, ETL y análisis.",
        "consulta": "arquitectura de base de datos",
        "frases": [
            "base de datos",
            "bases de datos",
            "arquitectura de datos",
            "modelo de datos",
            "esquema de datos",
            "consultar datos",
            "analizar datos",
            "analisis de datos",
            "disenar base de datos",
        ],
        "terminos": [
            "sql",
            "database",
            "postgres",
            "postgresql",
            "mysql",
            "sqlite",
            "mongodb",
            "esquema",
            "schema",
            "etl",
            "dataframe",
            "datos",
            "analitica",
            "duckdb",
            "bigquery",
            "consulta",
            "pandas",
        ],
        "usos": ["datos", "investigacion"],
        "tipos": ["mcp", "herramienta", "script", "paquete"],
    },
    {
        "id": "automatizacion",
        "nombre": "Automatizar tareas",
        "descripcion": "Agentes, flujos y orquestación.",
        "consulta": "automatizar tareas",
        "frases": [
            "automatizar tareas",
            "automatizar procesos",
            "flujo de trabajo",
            "workflow",
            "orquestar agentes",
            "agentes autonomos",
            "automatizacion",
        ],
        "terminos": [
            "automatizar",
            "automatizacion",
            "automation",
            "workflow",
            "orquestador",
            "orquestar",
            "orchestration",
            "agente",
            "agentes",
            "agents",
            "agentic",
            "n8n",
            "zapier",
            "make",
            "pipeline",
            "tarea",
            "tareas",
            "rpa",
        ],
        "usos": ["automatizacion"],
        "tipos": ["agente", "herramienta", "script", "mcp"],
    },
    {
        "id": "codigo",
        "nombre": "Escribir código",
        "descripcion": "Programar, revisar y probar.",
        "consulta": "escribir código",
        "frases": [
            "escribir codigo",
            "programar",
            "revisar codigo",
            "generar codigo",
            "asistente de codigo",
            "desarrollo de software",
            "code review",
        ],
        "terminos": [
            "codigo",
            "programar",
            "programacion",
            "code",
            "coding",
            "developer",
            "dev",
            "ide",
            "vscode",
            "copilot",
            "testing",
            "refactor",
            "debug",
            "software",
            "sdk",
        ],
        "usos": ["codigo"],
        "tipos": ["agente", "skill", "herramienta", "paquete"],
    },
    {
        "id": "prompts",
        "nombre": "Crear prompts",
        "descripcion": "Instrucciones, plantillas y evaluación.",
        "consulta": "crear prompts",
        "frases": [
            "crear prompts",
            "disenar prompts",
            "prompt engineering",
            "plantillas de prompts",
            "mejorar prompts",
            "sistema de prompts",
            "prompt library",
        ],
        "terminos": [
            "prompt",
            "prompts",
            "instrucciones",
            "plantilla",
            "plantillas",
            "few shot",
            "system prompt",
        ],
        "usos": ["prompts"],
        "tipos": ["prompt", "skill", "herramienta"],
    },
    {
        "id": "skills",
        "nombre": "Encontrar o crear skills",
        "descripcion": "Skills empaquetadas para agentes.",
        "consulta": "agent skills",
        "frases": [
            "una skill",
            "crear una skill",
            "agent skill",
            "claude skill",
            "pack de skills",
            "habilidad para el agente",
        ],
        "terminos": [
            "skill",
            "skills",
            "habilidad",
            "habilidades",
            "agent skill",
            "claude skill",
            "skill manager",
            "plugin",
            "extension",
        ],
        "usos": ["prompts", "automatizacion"],
        "tipos": ["skill"],
    },
    {
        "id": "investigacion",
        "nombre": "Investigar y RAG",
        "descripcion": "Buscar, recuperar y sintetizar.",
        "consulta": "investigar con RAG",
        "frases": [
            "investigar",
            "buscar informacion",
            "rag",
            "retrieval augmented generation",
            "base de conocimiento",
            "resumir documentos",
            "analizar pdf",
            "leer documentos",
        ],
        "terminos": [
            "rag",
            "retrieval",
            "embedding",
            "embeddings",
            "vector",
            "busqueda",
            "search",
            "investigacion",
            "investigar",
            "research",
            "pdf",
            "documento",
            "documentos",
            "knowledge",
            "memoria",
            "memory",
            "crawler",
            "scraper",
        ],
        "usos": ["investigacion"],
        "tipos": ["mcp", "herramienta", "modelo", "agente"],
    },
    {
        "id": "integracion",
        "nombre": "Conectar herramientas",
        "descripcion": "APIs, MCP, Slack y datos.",
        "consulta": "conectar herramientas con MCP",
        "frases": [
            "conectar herramientas",
            "integrar api",
            "servidor mcp",
            "model context protocol",
            "conectar slack",
            "conectar base de datos",
            "conectar api",
            "plugin",
        ],
        "terminos": [
            "mcp",
            "api",
            "integracion",
            "integrar",
            "conectar",
            "connector",
            "plugin",
            "webhook",
            "slack",
            "notion",
            "github",
            "sdk",
            "server",
            "servidor",
            "adapter",
        ],
        "usos": ["integracion"],
        "tipos": ["mcp"],
    },
    {
        "id": "imagen",
        "nombre": "Generar imágenes",
        "descripcion": "Crear, editar y analizar imagen.",
        "consulta": "generar imágenes",
        "frases": [
            "generar imagenes",
            "crear imagenes",
            "editar imagenes",
            "analizar imagenes",
            "vision artificial",
            "texto a imagen",
            "generar fotos",
            "editar fotos",
        ],
        "terminos": [
            "imagen",
            "imagenes",
            "image",
            "images",
            "vision",
            "diffusion",
            "midjourney",
            "dalle",
            "flux",
            "comfyui",
            "ocr",
            "foto",
            "fotos",
        ],
        "usos": ["imagen"],
        "tipos": ["modelo", "herramienta", "skill"],
    },
    {
        "id": "audio",
        "nombre": "Voz y audio",
        "descripcion": "Voz, transcripción, música y sonido.",
        "consulta": "voz y transcripción",
        "frases": [
            "transcribir audio",
            "texto a voz",
            "reconocer voz",
            "clonar voz",
            "generar musica",
            "transcripcion",
        ],
        "terminos": [
            "audio",
            "voz",
            "voice",
            "speech",
            "tts",
            "asr",
            "whisper",
            "music",
            "transcription",
            "transcribir",
            "sound",
        ],
        "usos": ["audio"],
        "tipos": ["modelo", "herramienta", "mcp"],
    },
    {
        "id": "video",
        "nombre": "Generar vídeo",
        "descripcion": "Generar, editar o animar vídeo.",
        "consulta": "generar vídeo",
        "frases": ["generar video", "editar video", "texto a video", "animar imagenes"],
        "terminos": [
            "video",
            "videos",
            "animation",
            "avatar",
            "film",
            "animar",
            "animacion",
        ],
        "usos": ["video"],
        "tipos": ["modelo", "herramienta"],
    },
    {
        "id": "infraestructura",
        "nombre": "Desplegar y operar",
        "descripcion": "GPU, serving, Docker y LLMOps.",
        "consulta": "desplegar modelos con GPU",
        "frases": [
            "desplegar modelo",
            "servir modelo",
            "local llm",
            "en mi gpu",
            "fine tuning",
            "self hosted",
        ],
        "terminos": [
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
            "quantization",
            "cloud",
            "desplegar",
            "servidor",
        ],
        "usos": ["infraestructura"],
        "tipos": ["herramienta", "paquete", "modelo", "script"],
    },
    {
        "id": "evaluacion",
        "nombre": "Evaluar y probar",
        "descripcion": "Benchmarks, testing y guardrails.",
        "consulta": "evaluar prompts",
        "frases": [
            "evaluar prompts",
            "medir calidad",
            "probar prompts",
            "red teaming",
            "monitorear agente",
        ],
        "terminos": [
            "eval",
            "evaluation",
            "evaluar",
            "benchmark",
            "benchmarks",
            "testing",
            "test",
            "guardrails",
            "monitoring",
            "metrics",
            "tracing",
            "calidad",
        ],
        "usos": ["evaluacion"],
        "tipos": ["herramienta", "paquete", "skill"],
    },
    {
        "id": "contenido",
        "nombre": "Escribir y resumir",
        "descripcion": "Redacción, resumen, traducción y SEO.",
        "consulta": "escribir y resumir contenido",
        "frases": [
            "escribir contenido",
            "resumir texto",
            "traducir texto",
            "generar documentacion",
            "escribir blog",
            "hacer presentaciones",
        ],
        "terminos": [
            "writing",
            "content",
            "blog",
            "copywriting",
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
            "redactar",
            "resumir",
            "traducir",
        ],
        "usos": ["contenido"],
        "tipos": ["modelo", "skill", "herramienta", "prompt"],
    },
]


def normalizar(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    sin_acentos = sin_acentos.casefold()
    return re.sub(r"[^a-z0-9]+", " ", sin_acentos).strip()


def tokens_de(texto: str) -> list[str]:
    return [t for t in normalizar(texto).split() if len(t) > 1 and t not in STOP]


def coincide(texto: str, aguja: str) -> bool:
    """La aguja aparece al inicio de una palabra (prefijo con borde)."""
    if not aguja:
        return False
    inicio = texto.find(aguja)
    while inicio != -1:
        if inicio == 0 or not texto[inicio - 1].isalnum():
            return True
        inicio = texto.find(aguja, inicio + 1)
    return False


def exacta(texto: str, aguja: str) -> bool:
    """La aguja aparece como palabra completa."""
    if not aguja:
        return False
    inicio = texto.find(aguja)
    while inicio != -1:
        fin = inicio + len(aguja)
        borde_izq = inicio == 0 or not texto[inicio - 1].isalnum()
        borde_der = fin == len(texto) or not texto[fin].isalnum()
        if borde_izq and borde_der:
            return True
        inicio = texto.find(aguja, inicio + 1)
    return False


def _compacto(numero: float) -> str:
    numero = float(numero or 0)
    if numero >= 1_000_000:
        return f"{numero / 1_000_000:.1f}M".replace(".0M", "M")
    if numero >= 1_000:
        return f"{round(numero / 1_000)}k"
    return str(int(numero))


def _metrica_texto(metricas: dict[str, Any]) -> str:
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


def _categoria_id(categoria: str) -> str:
    normalizada = normalizar(categoria)
    return CATEGORIA_ALIAS.get(normalizada, normalizada.replace(" ", "_"))


def _facetas() -> Any:
    try:
        from skillscenter import facetas
    except ImportError:
        return None
    return facetas


def _topicos(valor: Any) -> list[str]:
    if isinstance(valor, list):
        return [str(t) for t in valor if t][:25]
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return []
        if texto.startswith("["):
            try:
                return [str(t) for t in json.loads(texto) if t][:25]
            except ValueError:
                pass
        return texto.split()[:25]
    return []


def _tipo_faceta(
    crudo: str, nombre: str, descripcion: str, topics: list[str], categoria: str
) -> str:
    nombre_n = normalizar(nombre)
    categoria_n = _categoria_id(categoria)
    texto = normalizar(" ".join([nombre, descripcion, *topics, categoria]))
    if crudo in {"post", "noticia"}:
        return "articulo"
    if crudo == "modelo" or categoria_n == "modelos":
        return "modelo"
    if crudo == "mcp_server" or categoria_n == "mcp" or "mcp" in nombre_n.split():
        return "mcp"
    if "prompt" in nombre_n:
        return "prompt"
    if crudo == "skill" or categoria_n == "skills":
        return "skill"
    if categoria_n == "agentes" or "agent" in nombre_n:
        return "agente"
    if any(clave in texto.split() for clave in ("cli", "script", "terminal", "shell")):
        return "script"
    if crudo == "paquete":
        return "paquete"
    if crudo == "repo":
        return "herramienta"
    return "recurso"


def _usos_faceta(
    crudo: str, nombre: str, descripcion: str, topics: list[str], categoria: str
) -> list[str]:
    texto = normalizar(" ".join([nombre, descripcion, *topics, categoria]))
    tokens = set(texto.split())
    puntajes: dict[str, float] = {}
    for uso in CATEGORIA_USOS.get(_categoria_id(categoria), []):
        puntajes[uso] = puntajes.get(uso, 0.0) + 2.0
    for uso, datos in USOS.items():
        for clave in datos["alias"]:
            clave_n = normalizar(clave)
            if " " in clave_n:
                if clave_n in texto:
                    puntajes[uso] = puntajes.get(uso, 0.0) + 1.5
            elif clave_n in tokens:
                puntajes[uso] = puntajes.get(uso, 0.0) + 1.0
    if crudo == "mcp_server":
        puntajes["integracion"] = puntajes.get("integracion", 0.0) + 2.0
    elif crudo == "skill":
        puntajes["prompts"] = puntajes.get("prompts", 0.0) + 1.0
    orden = {u: i for i, u in enumerate(USOS)}
    elegidos = sorted(
        (u for u, p in puntajes.items() if p > 0),
        key=lambda u: (-puntajes[u], orden.get(u, 99)),
    )[:3]
    return elegidos or ["general"]


def _por_nombre(valor: Any, defecto: str) -> str:
    return str(valor).strip() if valor else defecto


def _crear_item(
    *,
    nombre: str,
    url: str,
    fuente: str,
    tipo: str,
    categoria: str,
    score: float,
    usos: list[str],
    metrica: str,
    descripcion: str,
    topics: list[str],
    fecha: str | None = None,
    alta: str | None = None,
) -> dict[str, Any]:
    fuente_nombre = FUENTES.get(fuente, fuente)
    tipo_datos = TIPOS.get(tipo, {"nombre": tipo, "alias": []})
    uso_datos = [USOS.get(u, {"nombre": u, "alias": []}) for u in usos]
    alias = [tipo_datos["nombre"] + " " + " ".join(tipo_datos["alias"])]
    alias.extend(u["nombre"] + " " + " ".join(u["alias"]) for u in uso_datos)
    nombre_n = normalizar(nombre)
    desc_n = normalizar(descripcion)
    topics_n = normalizar(" ".join(topics))
    categoria_n = normalizar(categoria)
    fuente_n = normalizar(fuente_nombre)
    tipo_n = normalizar(tipo_datos["nombre"] + " " + " ".join(tipo_datos["alias"]))
    uso_n = normalizar(" ".join(alias))
    texto = " ".join([nombre_n, desc_n, categoria_n, topics_n, fuente_n, uso_n, tipo_n])
    texto_concepto = " ".join([nombre_n, desc_n, categoria_n, topics_n, fuente_n, tipo_n])
    return {
        "nombre": nombre,
        "url": url,
        "fuente": fuente,
        "fuente_nombre": fuente_nombre,
        "tipo": tipo,
        "tipo_nombre": tipo_datos["nombre"],
        "usos": usos,
        "categoria": categoria,
        "score": float(score or 0),
        "metrica": metrica,
        "descripcion": descripcion,
        "topics": topics[:12],
        "fecha": fecha,
        "alta": alta,
        "nn": nombre_n,
        "nd": desc_n,
        "nk": topics_n,
        "nc": categoria_n,
        "nu": uso_n,
        "h": texto,
        "hc": texto_concepto,
    }


def cargar_catalogo_js(ruta: Path) -> tuple[list[dict[str, Any]], str | None]:
    texto = ruta.read_text("utf-8")
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio == -1 or fin == -1:
        raise ValueError(f"{ruta} no contiene un objeto JSON")
    datos = json.loads(texto[inicio : fin + 1])

    fuentes = datos.get("fuentes") or []
    tipos = datos.get("tipos") or []
    usos = datos.get("usos") or []
    filas = datos.get("items") or []
    if not isinstance(filas, list):
        raise ValueError(f"{ruta} no tiene una lista de items")

    items: list[dict[str, Any]] = []
    for fila in filas:
        if not isinstance(fila, list) or len(fila) < 10:
            continue
        fuente_def = fuentes[fila[2]] if 0 <= fila[2] < len(fuentes) else {}
        tipo_def = tipos[fila[3]] if 0 <= fila[3] < len(tipos) else {}
        usos_def = [usos[i] for i in fila[6] if isinstance(i, int) and 0 <= i < len(usos)]
        fuente_id = str(fuente_def.get("id") or fila[2])
        tipo_id = str(tipo_def.get("id") or fila[3])
        uso_ids = [str(u.get("id") or "") for u in usos_def if u.get("id")]
        items.append(
            _crear_item(
                nombre=_por_nombre(fila[0], "sin nombre"),
                url=_por_nombre(fila[1], ""),
                fuente=fuente_id,
                tipo=tipo_id,
                categoria=_categoria_id(_por_nombre(fila[4], "otros")),
                score=float(fila[5] or 0),
                usos=uso_ids or ["general"],
                metrica=_por_nombre(fila[7], ""),
                descripcion=_por_nombre(fila[8], ""),
                topics=_topicos(fila[9]),
            )
        )
    return items, datos.get("actualizado")


def cargar_catalogo_csv(ruta: Path) -> tuple[list[dict[str, Any]], str | None]:
    items: list[dict[str, Any]] = []
    actualizado: str | None = None
    facetas = _facetas()
    with ruta.open("r", encoding="utf-8-sig", newline="") as fh:
        for fila in csv.DictReader(fh):
            nombre = fila.get("nombre") or "sin nombre"
            descripcion = fila.get("descripcion") or ""
            topics = _topicos(fila.get("topics") or fila.get("topics_str") or "")
            categoria = _categoria_id(
                (fila.get("categorias") or "otros").split(",")[0].strip() or "otros"
            )
            crudo = fila.get("tipo") or "recurso"
            tipo = (
                facetas.clasificar_tipo(nombre, descripcion, crudo, topics, categoria)
                if facetas
                else _tipo_faceta(crudo, nombre, descripcion, topics, categoria)
            )
            usos = (
                facetas.clasificar_usos(nombre, descripcion, crudo, topics, categoria)
                if facetas
                else _usos_faceta(crudo, nombre, descripcion, topics, categoria)
            )
            metricas: dict[str, Any] = {}
            with contextlib.suppress(ValueError):
                metricas = json.loads(fila.get("metricas") or "{}")
            fecha = fila.get("ultima_vez_visto") or None
            alta = fila.get("primera_vez_visto") or None
            if fecha and (actualizado is None or fecha > actualizado):
                actualizado = fecha[:10]
            items.append(
                _crear_item(
                    nombre=nombre,
                    url=fila.get("url") or "",
                    fuente=fila.get("fuente") or "desconocida",
                    tipo=tipo,
                    categoria=categoria,
                    score=float(fila.get("score") or 0),
                    usos=usos,
                    metrica=_metrica_texto(metricas),
                    descripcion=descripcion,
                    topics=topics,
                    fecha=fecha,
                    alta=alta,
                )
            )
    return items, actualizado


def cargar_catalogo_sqlite(ruta: Path) -> tuple[list[dict[str, Any]], str | None]:
    uri = f"file:{ruta.as_posix()}?mode=ro"
    conexion = sqlite3.connect(uri, uri=True)
    conexion.row_factory = sqlite3.Row
    try:
        filas = conexion.execute(
            """
            SELECT i.nombre, i.url, i.fuente, i.tipo, i.descripcion, i.topics,
                   i.metricas, i.primera_vez_visto, i.ultima_vez_visto,
                   (SELECT score FROM puntuaciones p WHERE p.item_id = i.id
                     ORDER BY p.fecha DESC LIMIT 1) AS score,
                   (SELECT ic.categoria_id FROM item_categorias ic
                      JOIN categorias c ON c.id = ic.categoria_id
                     WHERE ic.item_id = i.id ORDER BY c.orden LIMIT 1) AS categoria
              FROM items i
             WHERE i.aprobado = 1
            """
        ).fetchall()
    finally:
        conexion.close()

    items: list[dict[str, Any]] = []
    actualizado: str | None = None
    facetas = _facetas()
    for fila in filas:
        nombre = fila["nombre"] or "sin nombre"
        descripcion = fila["descripcion"] or ""
        topics = _topicos(fila["topics"])
        categoria = _categoria_id(fila["categoria"] or "otros")
        crudo = fila["tipo"] or "recurso"
        tipo = (
            facetas.clasificar_tipo(nombre, descripcion, crudo, topics, categoria)
            if facetas
            else _tipo_faceta(crudo, nombre, descripcion, topics, categoria)
        )
        usos = (
            facetas.clasificar_usos(nombre, descripcion, crudo, topics, categoria)
            if facetas
            else _usos_faceta(crudo, nombre, descripcion, topics, categoria)
        )
        try:
            metricas = json.loads(fila["metricas"] or "{}")
        except ValueError:
            metricas = {}
        fecha = fila["ultima_vez_visto"] or None
        alta = fila["primera_vez_visto"] or None
        if fecha and (actualizado is None or fecha > actualizado):
            actualizado = fecha[:10]
        items.append(
            _crear_item(
                nombre=nombre,
                url=fila["url"] or "",
                fuente=fila["fuente"] or "desconocida",
                tipo=tipo,
                categoria=categoria,
                score=float(fila["score"] or 0),
                usos=usos,
                metrica=_metrica_texto(metricas),
                descripcion=descripcion,
                topics=topics,
                fecha=fecha,
                alta=alta,
            )
        )
    return items, actualizado


def cargar_archivo(ruta: Path) -> tuple[list[dict[str, Any]], str | None]:
    sufijo = ruta.suffix.lower()
    if sufijo in {".db", ".sqlite", ".sqlite3"}:
        return cargar_catalogo_sqlite(ruta)
    if sufijo == ".csv":
        return cargar_catalogo_csv(ruta)
    return cargar_catalogo_js(ruta)


def _candidatos(explicito: str | None) -> list[Path]:
    candidatos: list[Path] = []
    if explicito:
        candidatos.append(Path(explicito))
    variable = os.environ.get("SKILLSCENTER_CATALOGO")
    if variable:
        candidatos.append(Path(variable))
    base_datos = os.environ.get("SKILLSCENTER_DB")
    if base_datos:
        candidatos.append(Path(base_datos))
    else:
        local = os.environ.get("LOCALAPPDATA")
        if local:
            candidatos.append(Path(local) / "skillscenter" / "radar.db")
    skill_root = Path(__file__).resolve().parents[1]
    candidatos.append(skill_root / "assets" / "catalogo.js")
    raiz = Path(__file__).resolve().parents[3]
    candidatos.append(raiz / "landings" / "assets" / "catalogo.js")
    candidatos.append(Path.cwd() / "landings" / "assets" / "catalogo.js")
    candidatos.append(Path.cwd() / "informes" / "catalogo-completo.csv")
    return candidatos


def cargar_catalogo(explicito: str | None) -> tuple[Path, list[dict[str, Any]], str | None]:
    vistos: set[Path] = set()
    for candidato in _candidatos(explicito):
        if candidato in vistos or not candidato.is_file():
            continue
        vistos.add(candidato)
        try:
            items, actualizado = cargar_archivo(candidato)
        except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError):
            continue
        if items:
            return candidato, items, actualizado
    raise FileNotFoundError(
        "No se encontro el catalogo. Usa --catalogo, SKILLSCENTER_CATALOGO o "
        "genera landings/assets/catalogo.js con scripts/generar-datos-landings.py."
    )


def intencion_por_id(identificador: str) -> dict[str, Any] | None:
    buscado = normalizar(identificador).replace(" ", "")
    for intencion in INTENCIONES:
        if intencion["id"] == buscado:
            return intencion
    return None


def detectar_intenciones(texto: str, tokens: list[str]) -> list[tuple[float, dict[str, Any]]]:
    halladas: list[tuple[float, dict[str, Any]]] = []
    for intencion in INTENCIONES:
        puntos = 0.0
        for frase in intencion["frases"]:
            frase_n = normalizar(frase)
            if coincide(texto, frase_n):
                puntos += 8 + len(frase_n.split())
        for termino in intencion["terminos"]:
            termino_n = normalizar(termino)
            if termino_n in tokens:
                puntos += 5
            elif len(termino_n) > 3 and coincide(texto, termino_n):
                puntos += 2
        if puntos >= 5:
            halladas.append((puntos, intencion))
    halladas.sort(key=lambda par: -par[0])
    return halladas[:2]


def _aplicar_filtros(
    items: list[dict[str, Any]],
    tipo: str | None,
    uso: str | None,
    fuente: str | None,
    categoria: str | None,
) -> list[dict[str, Any]]:
    tipo_n = normalizar(tipo) if tipo else None
    uso_n = normalizar(uso) if uso else None
    fuente_n = normalizar(fuente) if fuente else None
    categoria_n = _categoria_id(categoria) if categoria else None
    filtrados = []
    for item in items:
        if tipo_n and normalizar(item["tipo"]) != tipo_n:
            continue
        if uso_n and uso_n not in {normalizar(u) for u in item["usos"]}:
            continue
        if fuente_n and normalizar(item["fuente"]) != fuente_n:
            continue
        if categoria_n and _categoria_id(item["categoria"]) != categoria_n:
            continue
        filtrados.append(item)
    return filtrados


def _literal(item: dict[str, Any], texto: str, tokens: list[str]) -> float | None:
    if not tokens:
        return 0.0
    for token in tokens:
        if not coincide(item["h"], token):
            return None
    puntos = 0.0
    if len(tokens) > 1 and coincide(item["h"], texto):
        puntos += 4
    for token in tokens:
        if exacta(item["nn"], token):
            puntos += 3
        elif coincide(item["nn"], token):
            puntos += 2
        elif coincide(item["nk"], token):
            puntos += 1.5
        elif coincide(item["nc"], token):
            puntos += 0.5
    return puntos


def _concepto(
    item: dict[str, Any],
    detectadas: list[tuple[float, dict[str, Any]]],
    tokens: list[str],
    permitir_sin_terminos: bool = False,
) -> tuple[float, list[str]]:
    puntos = 0.0
    ids: list[str] = []
    for valor, intencion in detectadas:
        aciertos = 0.0
        for termino in intencion["terminos"]:
            termino_n = normalizar(termino)
            if " " in termino_n:
                if coincide(item["hc"], termino_n):
                    aciertos += 2
            elif exacta(item["hc"], termino_n):
                aciertos += 1
        uso_match = bool(set(item["usos"]) & set(intencion["usos"]))
        tipo_match = item["tipo"] in intencion["tipos"]
        if not aciertos and not (permitir_sin_terminos and (uso_match or tipo_match)):
            continue
        aporte = aciertos * 3 + valor * 0.5
        if uso_match:
            aporte += 3
        if tipo_match:
            aporte += 1.5
        puntos += aporte
        ids.append(intencion["id"])
    for token in tokens:
        if len(token) > 3 and exacta(item["hc"], token):
            puntos += 1.5
    return puntos, ids


def buscar(
    items: list[dict[str, Any]],
    consulta: str,
    *,
    tipo: str | None = None,
    uso: str | None = None,
    fuente: str | None = None,
    categoria: str | None = None,
    orden: str = "relevancia",
    limite: int = 20,
    concepto: str | None = None,
    nuevos: int | None = None,
) -> dict[str, Any]:
    texto = normalizar(consulta)
    tokens = tokens_de(consulta)
    filtrados = _aplicar_filtros(items, tipo, uso, fuente, categoria)

    sin_fechas = not any(item["alta"] for item in items)
    if nuevos is not None:
        if sin_fechas:
            filtrados = []
        else:
            from datetime import date, timedelta

            corte = (date.today() - timedelta(days=max(1, nuevos))).isoformat()
            filtrados = [i for i in filtrados if (i["alta"] or "") >= corte]

    detectadas: list[tuple[float, dict[str, Any]]] = []
    forzada = intencion_por_id(concepto) if concepto else None
    if forzada:
        detectadas = [(10.0, forzada)]
    elif texto:
        detectadas = detectar_intenciones(texto, tokens)

    modo = "filtros"
    candidatos: list[tuple[float, dict[str, Any], list[str]]] = []

    if texto and not forzada:
        literales = []
        for item in filtrados:
            puntos = _literal(item, texto, tokens)
            if puntos:
                literales.append((puntos, item, []))
        if literales:
            candidatos = literales
            modo = "literal"

    if not candidatos:
        filtros_activos = any((tipo, uso, fuente, categoria))
        frases = {normalizar(f) for _, intencion in detectadas for f in intencion["frases"]}
        permitir_sin_terminos = bool(filtros_activos or forzada or texto in frases)
        for item in filtrados:
            puntos, ids = _concepto(item, detectadas, tokens, permitir_sin_terminos)
            if puntos > 0:
                candidatos.append((puntos, item, ids))
        if candidatos:
            modo = "concepto"
        elif not texto and not forzada:
            candidatos = [(0.0, item, []) for item in filtrados]
            modo = "filtros"

    def clave(par: tuple[float, dict[str, Any], list[str]]) -> tuple[float, ...]:
        puntos, item, _ = par
        if orden == "calor":
            return (-item["score"], -puntos)
        if orden == "nombre":
            return (item["nn"],)
        if modo == "concepto":
            return (-(puntos + item["score"] / 8), -puntos)
        return (-puntos, -item["score"])

    candidatos.sort(key=clave)
    limite = max(1, min(int(limite), 200))
    seleccion = candidatos[:limite]

    resultados = []
    for puntos, item, ids in seleccion:
        motivo = "literal" if modo == "literal" else "filtro"
        if modo == "concepto":
            motivo = "intencion:" + (
                ids[0] if ids else (detectadas[0][1]["id"] if detectadas else "")
            )
        resultados.append(
            {
                "nombre": item["nombre"],
                "url": item["url"],
                "fuente": item["fuente"],
                "fuente_nombre": item["fuente_nombre"],
                "tipo": item["tipo"],
                "tipo_nombre": item["tipo_nombre"],
                "usos": item["usos"],
                "categoria": item["categoria"],
                "score": round(item["score"], 1),
                "metrica": item["metrica"],
                "descripcion": item["descripcion"][:280],
                "topics": item["topics"],
                "fecha": item["fecha"],
                "motivo": motivo,
                "ajuste": round(puntos, 1),
            }
        )

    return {
        "consulta": consulta,
        "modo": modo,
        "intenciones": [
            {"id": intencion["id"], "nombre": intencion["nombre"], "puntos": round(valor, 1)}
            for valor, intencion in detectadas
        ],
        "nuevos": nuevos,
        "nuevos_sin_fechas": bool(nuevos is not None and sin_fechas),
        "total": len(candidatos),
        "items": resultados,
    }


def _escapar(texto: str) -> str:
    return " ".join(str(texto).split()).replace("|", "/")


def imprimir_markdown(
    resultado: dict[str, Any], ruta: Path, actualizado: str | None, total_catalogo: int
) -> None:
    titulo = resultado["consulta"]
    if not titulo:
        titulo = "(concepto)" if resultado["intenciones"] else "(filtros)"
    print(f"# Busqueda: {titulo}")
    fecha = actualizado or "sin fecha"
    print(f"Catalogo: {total_catalogo} entradas · actualizado {fecha} · {ruta}")
    if resultado["intenciones"]:
        print(
            "Intenciones: "
            + ", ".join(f"{i['nombre']} ({i['puntos']:.0f})" for i in resultado["intenciones"])
        )
    if resultado["modo"] == "concepto":
        if resultado["consulta"]:
            print("Sin coincidencias literales: se aplico la busqueda por intencion.")
        else:
            print("Sin texto de busqueda: se aplico la intencion forzada.")
    if resultado["modo"] == "filtros":
        print("Sin texto de busqueda: se listan los resultados mejor puntuados.")
    if resultado["nuevos"] is not None:
        if resultado["nuevos_sin_fechas"]:
            print("AVISO: la fuente no trae fecha por item; --nuevos no puede filtrar.")
            print("Usa la base SQLite o un CSV con primera_vez_visto.")
        else:
            print(f"Filtro: altas en los ultimos {resultado['nuevos']} dias.")
    print()
    if not resultado["items"]:
        print("No hay resultados verificados para esta consulta.")
        print("Prueba menos palabras, otro concepto o sincroniza el catalogo.")
        return
    print("| # | Entrada | Fuente / Tipo | Uso | Score | Por que |")
    print("|---|---------|---------------|-----|-------|---------|")
    for numero, item in enumerate(resultado["items"], 1):
        nombre = _escapar(item["nombre"])
        desc = _escapar(item["descripcion"])[:110]
        entrada = f"[{nombre}]({item['url']})" if item["url"] else nombre
        if desc:
            entrada += f" — {desc}"
        fuente = f"{item['fuente_nombre']} / {item['tipo_nombre']}"
        usos = ", ".join(item["usos"])
        motivo = item["motivo"].replace("intencion:", "concepto ")
        print(f"| {numero} | {entrada} | {fuente} | {usos} | {item['score']:.0f} | {motivo} |")


def imprimir_stats(
    items: list[dict[str, Any]], ruta: Path, actualizado: str | None, max_dias: int
) -> None:
    from collections import Counter
    from datetime import date

    print("# Catalogo")
    print(f"- Ruta: {ruta}")
    print(f"- Actualizado: {actualizado or 'sin fecha'}")
    if actualizado:
        try:
            dias = (date.today() - date.fromisoformat(actualizado[:10])).days
            print(f"- Antiguedad: {dias} dias")
            if dias > max_dias:
                print(
                    f"- AVISO: el catalogo supera {max_dias} dias. "
                    "Sincroniza antes de prometer novedades."
                )
        except ValueError:
            pass
    print(f"- Total: {len(items)}")
    for titulo, campo in (
        ("Por fuente", "fuente"),
        ("Por tipo", "tipo"),
        ("Por categoria", "categoria"),
    ):
        print(f"\n## {titulo}")
        for clave, valor in Counter(i[campo] for i in items).most_common():
            print(f"- {clave or 'sin dato'}: {valor}")
    print("\n## Por uso")
    usos: Counter[str] = Counter()
    for item in items:
        usos.update(item["usos"])
    for clave, valor in usos.most_common():
        print(f"- {clave}: {valor}")


def imprimir_intenciones() -> None:
    print("| ID | Intencion | Frases | Terminos | Usos |")
    print("|----|-----------|--------|----------|------|")
    for intencion in INTENCIONES:
        print(
            f"| `{intencion['id']}` | {intencion['nombre']} | {len(intencion['frases'])} "
            f"| {len(intencion['terminos'])} | {', '.join(intencion['usos'])} |"
        )
    print("\nFuerza una intencion con --concepto ID.")


def _parsear(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Busqueda literal y conceptual en el catalogo de SkillsCenter."
    )
    parser.add_argument("consulta", nargs="*", help="texto libre a buscar")
    parser.add_argument("--catalogo", help="ruta a catalogo.js, CSV o SQLite")
    parser.add_argument("--tipo", help="faceta de tipo: skill, mcp, agente, modelo...")
    parser.add_argument("--uso", help="faceta de uso: diseno, datos, codigo...")
    parser.add_argument("--fuente", help="github, npm, pypi, huggingface...")
    parser.add_argument("--categoria", help="seccion del catalogo: skills, mcp...")
    parser.add_argument("--concepto", help="fuerza una intencion (ver --intenciones)")
    parser.add_argument("--intenciones", action="store_true", help="lista las intenciones")
    parser.add_argument(
        "--orden",
        default="relevancia",
        choices=["relevancia", "calor", "nombre"],
        help="criterio de orden",
    )
    parser.add_argument("--limite", type=int, default=20, help="maximo de resultados")
    parser.add_argument("--nuevos", type=int, help="solo entradas de los ultimos N dias")
    parser.add_argument("--json", action="store_true", help="salida JSON")
    parser.add_argument("--stats", action="store_true", help="estado del catalogo")
    parser.add_argument("--max-dias", type=int, default=3, help="aviso de antiguedad")
    args = parser.parse_args(argv)
    _validar_filtros(parser, args)
    return args


def _validar_filtros(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    def exigir(valor: str | None, validos: set[str], etiqueta: str) -> None:
        if valor and normalizar(valor) not in validos:
            opciones = ", ".join(sorted(validos))
            parser.error(f"{etiqueta} invalido: {valor}. Opciones: {opciones}")

    exigir(args.tipo, set(TIPOS), "tipo")
    exigir(args.uso, set(USOS), "uso")
    exigir(args.fuente, set(FUENTES), "fuente")
    exigir(args.categoria, set(CATEGORIA_ALIAS.values()), "categoria")
    if args.concepto and intencion_por_id(args.concepto) is None:
        ids = ", ".join(i["id"] for i in INTENCIONES)
        parser.error(f"intencion invalida: {args.concepto}. Opciones: {ids}")


def main(argv: list[str] | None = None) -> int:
    with contextlib.suppress(AttributeError, ValueError):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = _parsear(argv)

    if args.intenciones:
        imprimir_intenciones()
        return 0

    try:
        ruta, items, actualizado = cargar_catalogo(args.catalogo)
    except FileNotFoundError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError) as error:
        print(f"error: no se pudo leer el catalogo: {error}", file=sys.stderr)
        return 1

    if args.stats:
        imprimir_stats(items, ruta, actualizado, args.max_dias)
        return 0

    consulta = " ".join(args.consulta).strip()
    resultado = buscar(
        items,
        consulta,
        tipo=args.tipo,
        uso=args.uso,
        fuente=args.fuente,
        categoria=args.categoria,
        orden=args.orden,
        limite=args.limite,
        concepto=args.concepto,
        nuevos=args.nuevos,
    )

    if args.json:
        salida = {
            "consulta": resultado["consulta"],
            "catalogo": {
                "ruta": str(ruta),
                "actualizado": actualizado,
                "total": len(items),
            },
            "modo": resultado["modo"],
            "nuevos": resultado["nuevos"],
            "nuevos_sin_fechas": resultado["nuevos_sin_fechas"],
            "intenciones": resultado["intenciones"],
            "total": resultado["total"],
            "items": resultado["items"],
        }
        print(json.dumps(salida, ensure_ascii=False, indent=2))
        return 0

    imprimir_markdown(resultado, ruta, actualizado, len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
