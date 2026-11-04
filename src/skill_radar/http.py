"""Cliente HTTP con reintentos, timeout y errores legibles."""

from __future__ import annotations

import time
from typing import Any

import httpx

from . import config


class ErrorFuente(RuntimeError):
    """Fallo recuperable de una fuente externa."""


class Cliente:
    def __init__(
        self,
        user_agent: str | None = None,
        timeout: float | None = None,
        reintentos: int | None = None,
    ) -> None:
        self.reintentos = config.REINTENTOS if reintentos is None else reintentos
        self._cliente = httpx.Client(
            headers={
                "User-Agent": user_agent or config.user_agent(),
                "Accept": "application/json, text/plain, */*",
            },
            timeout=timeout or config.TIEMPO_ESPERA,
            follow_redirects=True,
        )

    def __enter__(self) -> Cliente:
        return self

    def __exit__(self, *exc: object) -> None:
        self.cerrar()

    def cerrar(self) -> None:
        self._cliente.close()

    def peticion(self, metodo: str, url: str, **kwargs: Any) -> httpx.Response:
        ultimo_error: Exception | None = None

        for intento in range(self.reintentos):
            try:
                respuesta = self._cliente.request(metodo, url, **kwargs)
            except httpx.HTTPError as exc:
                ultimo_error = exc
                if intento == self.reintentos - 1:
                    raise ErrorFuente(f"{url}: {exc}") from exc
                time.sleep(config.PAUSA_REINTENTO * (2**intento))
                continue

            if respuesta.status_code in (429, 500, 502, 503, 504):
                ultimo_error = ErrorFuente(f"{url}: HTTP {respuesta.status_code}")
                if intento == self.reintentos - 1:
                    raise ultimo_error
                espera = _segundos_reintento(respuesta)
                time.sleep(espera if espera is not None else config.PAUSA_REINTENTO * (2**intento))
                continue

            if respuesta.status_code == 403 and _agoto_cuota(respuesta):
                reinicio = respuesta.headers.get("x-ratelimit-reset", "desconocido")
                raise ErrorFuente(
                    f"{url}: cuota agotada (reinicio epoch {reinicio}). "
                    "Configura GITHUB_TOKEN para elevar el limite."
                )

            if respuesta.status_code >= 400:
                raise ErrorFuente(f"{url}: HTTP {respuesta.status_code}")

            return respuesta

        raise ErrorFuente(str(ultimo_error or f"{url}: fallo desconocido"))

    def get_json(self, url: str, **kwargs: Any) -> Any:
        return self.peticion("GET", url, **kwargs).json()

    def get_text(self, url: str, **kwargs: Any) -> str:
        return self.peticion("GET", url, **kwargs).text

    def post_json(self, url: str, **kwargs: Any) -> Any:
        return self.peticion("POST", url, **kwargs).json()


def _agoto_cuota(respuesta: httpx.Response) -> bool:
    return respuesta.headers.get("x-ratelimit-remaining") == "0"


def _segundos_reintento(respuesta: httpx.Response) -> float | None:
    valor = respuesta.headers.get("retry-after")
    if not valor:
        return None
    try:
        return min(30.0, max(0.0, float(valor)))
    except ValueError:
        return None
