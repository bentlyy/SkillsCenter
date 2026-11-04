"""Repositorios de GitHub por topic.

Las estrellas se acumulan en ``snapshots``; el crecimiento diario se calcula
comparando con el snapshot de hace 7 dias. Sin token, GitHub limita la busqueda
a 10 peticiones por minuto, asi que se espacian las consultas.
"""

from __future__ import annotations

import time
from datetime import date, timedelta

from .. import config
from ..http import Cliente
from ..models import Item
from .base import Fuente, Resultado

API = "https://api.github.com/search/repositories"
ESTRELLAS_MINIMAS = 5

CONSULTAS: tuple[dict[str, str], ...] = (
    {"q": "topic:mcp", "sort": "stars"},
    {"q": "topic:model-context-protocol", "sort": "stars"},
    {"q": "topic:ai-agents", "sort": "stars"},
    {"q": "topic:ai-agent", "sort": "stars"},
    {"q": "topic:llm-tools", "sort": "stars"},
    {"q": "topic:rag", "sort": "stars"},
    {"q": "topic:prompt-engineering", "sort": "stars"},
    {"q": "topic:claude-skills", "sort": "stars"},
    {"q": "topic:mcp", "sort": "updated"},
)


class Github(Fuente):
    id = "github"
    nombre = "GitHub"
    tipo = "repositorio"
    url = "https://github.com"
    limite_por_defecto = 50

    def __init__(self) -> None:
        self._token = config.token_github()
        self._ultima_peticion = 0.0
        self._intervalo = 2.1 if self._token else 6.5

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        por_consulta = max(5, min(limite, 100))
        consultas = list(CONSULTAS)
        creados_desde = (date.today() - timedelta(days=30)).isoformat()
        consultas.append({"q": f"topic:ai-agents created:>={creados_desde}", "sort": "stars"})

        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for indice, consulta in enumerate(consultas):
            if indice:
                self._esperar_turno()
            try:
                datos = self._buscar(cliente, consulta, por_consulta)
            except Exception as exc:
                avisos.append(f"{consulta['q']}: {exc}")
                continue

            for bruto in datos.get("items", []):
                item = _a_item(bruto)
                if item is not None and item.uid not in vistos:
                    vistos[item.uid] = item

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)

    def _buscar(self, cliente: Cliente, consulta: dict[str, str], por_consulta: int) -> dict:
        self._ultima_peticion = time.monotonic()
        cabeceras = {"Accept": "application/vnd.github+json"}
        if self._token:
            cabeceras["Authorization"] = f"Bearer {self._token}"

        return cliente.get_json(
            API,
            params={
                "q": f"{consulta['q']} stars:>={ESTRELLAS_MINIMAS}",
                "sort": consulta.get("sort", "stars"),
                "order": "desc",
                "per_page": por_consulta,
            },
            headers=cabeceras,
        )

    def _esperar_turno(self) -> None:
        transcurrido = time.monotonic() - self._ultima_peticion
        if transcurrido < self._intervalo:
            time.sleep(self._intervalo - transcurrido)


def _a_item(bruto: dict) -> Item | None:
    nombre_completo = bruto.get("full_name")
    if not nombre_completo:
        return None
    licencia = (bruto.get("license") or {}).get("spdx_id")
    return Item(
        uid=f"github:{nombre_completo.lower()}",
        fuente="github",
        tipo="repo",
        nombre=nombre_completo,
        url=bruto.get("html_url") or f"https://github.com/{nombre_completo}",
        descripcion=bruto.get("description") or "",
        autor=(bruto.get("owner") or {}).get("login"),
        homepage=bruto.get("homepage") or None,
        licencia=None if licencia in (None, "NOASSERTION") else licencia,
        lenguaje=bruto.get("language"),
        topics=bruto.get("topics") or [],
        metricas={
            "estrellas": bruto.get("stargazers_count") or 0,
            "forks": bruto.get("forks_count") or 0,
            "issues_abiertas": bruto.get("open_issues_count") or 0,
        },
        creado_en=bruto.get("created_at"),
        actualizado_fuente=bruto.get("pushed_at") or bruto.get("updated_at"),
        estado="archivado" if bruto.get("archived") else "activo",
    )
