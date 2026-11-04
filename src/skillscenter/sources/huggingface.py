"""Modelos de Hugging Face por traccion y por novedad."""

from __future__ import annotations

from ..http import Cliente
from ..models import Item
from .base import Fuente, Resultado

API = "https://huggingface.co/api/models"

CONSULTAS: tuple[dict[str, object], ...] = (
    {"search": "", "sort": "downloads", "direction": -1},
    {"search": "agent", "sort": "downloads", "direction": -1},
    {"search": "mcp", "sort": "downloads", "direction": -1},
    {"search": "llm", "sort": "downloads", "direction": -1},
    {"search": "embedding", "sort": "downloads", "direction": -1},
    {"search": "rag", "sort": "downloads", "direction": -1},
    {"search": "speech", "sort": "downloads", "direction": -1},
    {"search": "image", "sort": "downloads", "direction": -1},
    {"search": "", "sort": "createdAt", "direction": -1},
)

RUIDO = ("base_model:", "license:", "region:", "dataset:", "arxiv:", "doi:")


class HuggingFace(Fuente):
    id = "huggingface"
    nombre = "Hugging Face"
    tipo = "modelos"
    url = "https://huggingface.co"
    limite_por_defecto = 60

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        por_consulta = max(5, min(limite, 100))
        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for consulta in CONSULTAS:
            try:
                datos = cliente.get_json(
                    API,
                    params={**consulta, "limit": por_consulta},
                )
            except Exception as exc:
                avisos.append(f"{consulta.get('search') or 'populares'}: {exc}")
                continue

            for bruto in datos if isinstance(datos, list) else []:
                item = _a_item(bruto)
                if item is not None:
                    vistos.setdefault(item.uid, item)

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)


def _a_item(bruto: dict) -> Item | None:
    model_id = bruto.get("modelId") or bruto.get("id")
    if not model_id:
        return None

    topics = [
        tag
        for tag in (bruto.get("tags") or [])
        if isinstance(tag, str) and not tag.startswith(RUIDO)
    ][:15]
    for extra in (bruto.get("pipeline_tag"), bruto.get("library_name")):
        if extra and extra not in topics:
            topics.append(str(extra))

    return Item(
        uid=f"hf:{model_id.lower()}",
        fuente="huggingface",
        tipo="modelo",
        nombre=model_id,
        url=f"https://huggingface.co/{model_id}",
        descripcion="",
        autor=model_id.split("/")[0] if "/" in model_id else None,
        homepage=f"https://huggingface.co/{model_id}",
        topics=topics,
        metricas={
            "descargas": bruto.get("downloads") or 0,
            "likes": bruto.get("likes") or 0,
        },
        creado_en=bruto.get("createdAt"),
        actualizado_fuente=bruto.get("lastModified") or bruto.get("createdAt"),
        estado="activo",
    )
