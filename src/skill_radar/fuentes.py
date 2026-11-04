"""Catalogo de fuentes conocidas (metadatos, sin logica de red)."""

from __future__ import annotations

from typing import TypedDict


class FuenteInfo(TypedDict):
    id: str
    nombre: str
    tipo: str
    url: str
    descripcion: str


FUENTES: tuple[FuenteInfo, ...] = (
    {
        "id": "github",
        "nombre": "GitHub",
        "tipo": "repositorio",
        "url": "https://github.com",
        "descripcion": "Repositorios por topic, con estrellas y crecimiento diario",
    },
    {
        "id": "mcp_registry",
        "nombre": "Registro MCP",
        "tipo": "registro",
        "url": "https://registry.modelcontextprotocol.io",
        "descripcion": "Servidores MCP publicados en el registro oficial",
    },
    {
        "id": "awesome",
        "nombre": "Listas curadas",
        "tipo": "curaduria",
        "url": "https://github.com/topics/awesome",
        "descripcion": "Entradas de awesome-lists de MCP, agentes y skills",
    },
    {
        "id": "hackernews",
        "nombre": "Hacker News",
        "tipo": "comunidad",
        "url": "https://news.ycombinator.com",
        "descripcion": "Lanzamientos y discusion via la API de Algolia",
    },
    {
        "id": "reddit",
        "nombre": "Reddit",
        "tipo": "comunidad",
        "url": "https://www.reddit.com",
        "descripcion": "Posts de subreddits de IA (requiere credenciales OAuth)",
    },
    {
        "id": "pypi",
        "nombre": "PyPI",
        "tipo": "paquetes",
        "url": "https://pypi.org",
        "descripcion": "Paquetes Python nuevos y actualizados (RSS)",
    },
    {
        "id": "npm",
        "nombre": "npm",
        "tipo": "paquetes",
        "url": "https://www.npmjs.com",
        "descripcion": "Paquetes JavaScript por palabras clave",
    },
    {
        "id": "huggingface",
        "nombre": "Hugging Face",
        "tipo": "modelos",
        "url": "https://huggingface.co",
        "descripcion": "Modelos por descargas, likes y novedad",
    },
)

IDS_FUENTES = tuple(f["id"] for f in FUENTES)
