"""Paquetes de npm por palabras clave del ecosistema de IA."""

from __future__ import annotations

from ..http import Cliente
from ..models import Item
from .base import Fuente, Resultado

API = "https://registry.npmjs.org/-/v1/search"

CONSULTAS = (
    "keywords:mcp",
    "keywords:model-context-protocol",
    "keywords:ai-agent",
    "keywords:ai-agents",
    "keywords:llm",
    "keywords:claude",
    "keywords:rag",
    "keywords:ai-tools",
)


class Npm(Fuente):
    id = "npm"
    nombre = "npm"
    tipo = "paquetes"
    url = "https://www.npmjs.com"
    limite_por_defecto = 60

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        por_consulta = max(5, min(limite, 250))
        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for consulta in CONSULTAS:
            try:
                datos = cliente.get_json(API, params={"text": consulta, "size": por_consulta})
            except Exception as exc:
                avisos.append(f"{consulta}: {exc}")
                continue

            for objeto in datos.get("objects", []):
                item = _a_item(objeto.get("package") or {})
                if item is not None:
                    vistos.setdefault(item.uid, item)

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)


def _a_item(paquete: dict) -> Item | None:
    nombre = paquete.get("name")
    if not nombre:
        return None

    enlaces = paquete.get("links") or {}
    repositorio = _limpiar_repo(enlaces.get("repository"))
    publicador = paquete.get("publisher") or {}

    return Item(
        uid=f"npm:{nombre.lower()}",
        fuente="npm",
        tipo="paquete",
        nombre=nombre,
        url=enlaces.get("npm") or f"https://www.npmjs.com/package/{nombre}",
        descripcion=paquete.get("description") or "",
        autor=publicador.get("username"),
        homepage=enlaces.get("homepage") or repositorio,
        licencia=paquete.get("license"),
        topics=paquete.get("keywords") or [],
        metricas={},
        creado_en=paquete.get("date"),
        actualizado_fuente=paquete.get("date"),
        estado="activo",
    )


def _limpiar_repo(url: str | None) -> str | None:
    if not url:
        return None
    limpio = url.removeprefix("git+").removesuffix(".git")
    return limpio or None
