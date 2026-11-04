"""Servidores publicados en el registro oficial de Model Context Protocol."""

from __future__ import annotations

from ..http import Cliente
from ..models import Item
from .base import Fuente, Resultado

API = "https://registry.modelcontextprotocol.io/v0/servers"
META_CLAVE = "io.modelcontextprotocol.registry/official"


class McpRegistry(Fuente):
    id = "mcp_registry"
    nombre = "Registro MCP"
    tipo = "registro"
    url = "https://registry.modelcontextprotocol.io"
    limite_por_defecto = 200

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        objetivo = max(20, min(limite, 500))
        vistos: dict[str, Item] = {}
        avisos: list[str] = []
        cursor: str | None = None
        paginas = 0

        while len(vistos) < objetivo and paginas < 10:
            parametros: dict[str, str | int] = {"limit": min(100, objetivo - len(vistos) + 20)}
            if cursor:
                parametros["cursor"] = cursor

            try:
                datos = cliente.get_json(API, params=parametros)
            except Exception as exc:
                avisos.append(str(exc))
                break

            servidores = datos.get("servers", [])
            if not servidores:
                break

            for entrada in servidores:
                item = _a_item(entrada)
                if item is not None:
                    vistos.setdefault(item.uid, item)

            cursor = (datos.get("metadata") or {}).get("nextCursor")
            paginas += 1
            if not cursor:
                break

        if not vistos and avisos:
            raise RuntimeError(avisos[0])

        return Resultado(items=list(vistos.values()), avisos=avisos)


def _a_item(entrada: dict) -> Item | None:
    servidor = entrada.get("server") or {}
    nombre = servidor.get("name")
    if not nombre:
        return None

    meta = (entrada.get("_meta") or {}).get(META_CLAVE) or {}
    if meta.get("status") not in (None, "active"):
        return None

    repositorio = servidor.get("repository") or {}
    url_repo = repositorio.get("url") if isinstance(repositorio, dict) else None
    remotes = servidor.get("remotes") or []
    primer_remote = remotes[0] if remotes else {}
    packages = servidor.get("packages") or []

    url = (
        url_repo
        or servidor.get("websiteUrl")
        or (primer_remote.get("url") if isinstance(primer_remote, dict) else None)
        or API
    )

    topics = ["mcp", "mcp-server"]
    for paquete in packages:
        if isinstance(paquete, dict):
            tipo = paquete.get("registryType") or paquete.get("registry_type")
            if tipo:
                topics.append(str(tipo))
            transporte = paquete.get("transport") or {}
            if isinstance(transporte, dict) and transporte.get("type"):
                topics.append(str(transporte["type"]))
    for remote in remotes:
        if isinstance(remote, dict) and remote.get("type"):
            topics.append(str(remote["type"]))

    return Item(
        uid=f"mcp:{nombre}",
        fuente="mcp_registry",
        tipo="mcp_server",
        nombre=servidor.get("title") or nombre,
        url=url,
        descripcion=servidor.get("description") or "",
        autor=nombre.split("/")[0] if "/" in nombre else None,
        homepage=servidor.get("websiteUrl") or None,
        topics=topics,
        metricas={},
        creado_en=meta.get("publishedAt"),
        actualizado_fuente=meta.get("updatedAt") or meta.get("publishedAt"),
        estado="activo",
    )
