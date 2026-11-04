"""Normalizacion de URLs e identificadores estables."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

PARAMETROS_RUIDO = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "source",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}

GITHUB_REPO = re.compile(r"^https?://github\.com/([^/]+)/([^/?#]+)$")


def normalizar_url(url: str) -> str:
    partes = urlsplit(url.strip())
    host = (partes.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    consulta = [
        (k, v)
        for k, v in parse_qsl(partes.query, keep_blank_values=False)
        if k.lower() not in PARAMETROS_RUIDO
    ]
    ruta = partes.path.rstrip("/") or "/"
    return urlunsplit(("https", host, ruta, urlencode(consulta), ""))


def uid_desde_url(url: str) -> tuple[str, str]:
    """Devuelve (uid, url_canonica).

    Las URLs de repositorio de GitHub se convierten al uid de GitHub para que la
    misma herramienta no aparezca dos veces (awesome-list + repositorio).
    """
    canonica = normalizar_url(url)
    repo = GITHUB_REPO.match(canonica)
    if repo:
        propietario = repo.group(1).lower()
        nombre = repo.group(2).lower()
        return f"github:{propietario}/{nombre}", f"https://github.com/{propietario}/{nombre}"
    huella = hashlib.blake2b(canonica.encode("utf-8"), digest_size=6).hexdigest()
    return f"web:{huella}", canonica
