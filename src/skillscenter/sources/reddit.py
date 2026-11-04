"""Posts de subreddits de IA.

Reddit bloquea el JSON publico sin autenticacion, asi que la fuente solo se
activa si existen ``REDDIT_CLIENT_ID`` y ``REDDIT_CLIENT_SECRET`` (app tipo
"script" en https://www.reddit.com/prefs/apps).
"""

from __future__ import annotations

import os
import time

from .. import config
from ..http import Cliente, ErrorFuente
from ..models import Item
from .base import Fuente, Resultado

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"

SUBREDDITS_POR_DEFECTO = (
    "LocalLLaMA",
    "mcp",
    "AIAgents",
    "ClaudeAI",
    "ChatGPT",
    "LocalLLM",
    "MachineLearning",
    "artificial",
)


def _subreddits() -> tuple[str, ...]:
    personalizados = os.getenv("SKILLSCENTER_SUBREDDITS")
    if personalizados:
        return tuple(s.strip() for s in personalizados.split(",") if s.strip())
    return SUBREDDITS_POR_DEFECTO


class Reddit(Fuente):
    id = "reddit"
    nombre = "Reddit"
    tipo = "comunidad"
    url = "https://www.reddit.com"
    limite_por_defecto = 25

    def __init__(self) -> None:
        self._credenciales = config.credenciales_reddit()
        self._token: str | None = None
        self._expira = 0.0

    def disponible(self) -> tuple[bool, str]:
        if not self._credenciales:
            return False, (
                "faltan REDDIT_CLIENT_ID y REDDIT_CLIENT_SECRET "
                "(crea una app 'script' en reddit.com/prefs/apps)"
            )
        return True, ""

    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        if not self._credenciales:
            raise ErrorFuente("Reddit sin credenciales")

        self._asegurar_token(cliente)
        vistos: dict[str, Item] = {}
        avisos: list[str] = []

        for subreddit in _subreddits():
            try:
                datos = self._top(cliente, subreddit, limite)
            except Exception as exc:
                avisos.append(f"r/{subreddit}: {exc}")
                continue

            for hijo in datos.get("data", {}).get("children", []):
                item = _a_item(hijo.get("data") or {}, subreddit)
                if item is not None:
                    vistos.setdefault(item.uid, item)

        if not vistos and avisos:
            raise RuntimeError("; ".join(avisos[:3]))

        return Resultado(items=list(vistos.values()), avisos=avisos)

    def _asegurar_token(self, cliente: Cliente) -> None:
        if self._token and time.monotonic() < self._expira:
            return
        assert self._credenciales is not None
        usuario, secreto = self._credenciales
        respuesta = cliente.peticion(
            "POST",
            TOKEN_URL,
            auth=(usuario, secreto),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": config.user_agent()},
        ).json()
        token = respuesta.get("access_token")
        if not token:
            raise ErrorFuente("Reddit no devolvio access_token")
        self._token = token
        self._expira = time.monotonic() + float(respuesta.get("expires_in", 3600)) - 60

    def _top(self, cliente: Cliente, subreddit: str, limite: int) -> dict:
        return cliente.get_json(
            f"{API}/r/{subreddit}/top",
            params={"t": "day", "limit": max(5, min(limite, 100))},
            headers={"Authorization": f"Bearer {self._token}"},
        )


def _a_item(bruto: dict, subreddit: str) -> Item | None:
    identificador = bruto.get("id")
    titulo = bruto.get("title")
    if not identificador or not titulo:
        return None

    permalink = bruto.get("permalink") or f"/r/{subreddit}/comments/{identificador}/"
    topics = ["reddit", subreddit.lower()]
    flair = bruto.get("link_flair_text")
    if flair:
        topics.append(flair)

    return Item(
        uid=f"reddit:{identificador}",
        fuente="reddit",
        tipo="post",
        nombre=titulo,
        url=f"https://www.reddit.com{permalink}",
        descripcion=bruto.get("selftext") or "",
        autor=bruto.get("author"),
        homepage=bruto.get("url_overridden_by_dest") or None,
        topics=topics,
        metricas={
            "puntos": bruto.get("score") or 0,
            "comentarios": bruto.get("num_comments") or 0,
            "ratio": bruto.get("upvote_ratio") or 0,
        },
        creado_en=_iso(bruto.get("created_utc")),
        actualizado_fuente=_iso(bruto.get("created_utc")),
        estado="activo",
    )


def _iso(epoch: float | None) -> str | None:
    if not epoch:
        return None
    from datetime import datetime, timezone

    return datetime.fromtimestamp(float(epoch), tz=timezone.utc).isoformat(timespec="seconds")
