"""
Entidades de Pedido/Produto (domínio).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Produto(str, Enum):
    DIESEL = "diesel"
    GASOLINA = "gasolina"
    ETANOL = "etanol"
    LUBRIFICANTE = "lubrificante"


@dataclass(slots=True)
class Pedido:
    """Pedido de combustíveis e derivados."""
    cliente: str
    produto: Produto
    quantidade: int
    cupom: str | None = None

    def __post_init__(self) -> None:
        if not self.cliente or not self.cliente.strip():
            raise ValueError("Cliente obrigatório.")
        if not isinstance(self.quantidade, int) or self.quantidade < 0:
            raise ValueError("Quantidade deve ser um inteiro >= 0.")
