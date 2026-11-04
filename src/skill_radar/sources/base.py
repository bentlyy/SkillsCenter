"""Contrato comun de las fuentes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..http import Cliente
from ..models import Item


@dataclass(slots=True)
class Resultado:
    items: list[Item] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.items)


class Fuente(ABC):
    id: str = ""
    nombre: str = ""
    tipo: str = ""
    url: str = ""
    limite_por_defecto: int = 50

    def disponible(self) -> tuple[bool, str]:
        """Indica si la fuente puede ejecutarse (por ejemplo, si hay credenciales)."""
        return True, ""

    @abstractmethod
    def recolectar(self, cliente: Cliente, limite: int) -> Resultado:
        """Devuelve las entradas encontradas. Puede lanzar ErrorFuente."""
