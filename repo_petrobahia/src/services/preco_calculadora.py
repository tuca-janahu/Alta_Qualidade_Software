"""
Regras de cálculo de preço de pedidos:
- preço bruto por produto/quantidade
- aplicação de cupons
- arredondamentos/truncamentos por produto
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, getcontext
from typing import Final

from ..domains.pedido import Pedido, Produto

# Configuração global
getcontext().prec = 28


class EstrategiaPreco(ABC):
    """
    Classe base abstrata que define o contrato para cálculo de preços (SOLID - OCP/LSP).
    """
    BASE_PRICE: Decimal = Decimal("0.00")

    @abstractmethod
    def calcular_bruto(self, quantidade: int) -> Decimal:
        """Calcula o preço bruto baseado na quantidade."""
        pass

    def aplicar_cupom(self, valor: Decimal, cupom: str | None) -> Decimal:
        """
        Aplica cupons genéricos. Classes filhas podem sobrescrever para cupons específicos.
        """
        if not cupom:
            return valor

        c = cupom.upper().strip()
        if c == "MEGA10":
            return valor * Decimal("0.90")
        if c == "NOVO5":
            return valor * Decimal("0.95")
        return valor

    @abstractmethod
    def arredondar(self, valor: Decimal) -> Decimal:
        """Aplica a regra de arredondamento específica do produto."""
        pass


class EstrategiaDiesel(EstrategiaPreco):
    BASE_PRICE = Decimal("3.99")

    def calcular_bruto(self, quantidade: int) -> Decimal:
        total = self.BASE_PRICE * quantidade
        if quantidade > 1000:
            return total * Decimal("0.90")
        if quantidade > 500:
            return total * Decimal("0.95")
        return total

    def arredondar(self, valor: Decimal) -> Decimal:
        # Diesel arredonda para inteiro (meio para cima)
        return valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


class EstrategiaGasolina(EstrategiaPreco):
    BASE_PRICE = Decimal("5.19")

    def calcular_bruto(self, quantidade: int) -> Decimal:
        total = self.BASE_PRICE * quantidade
        if quantidade > 200:
            return total - Decimal("100")
        return total

    def arredondar(self, valor: Decimal) -> Decimal:
        # Gasolina arredonda para 2 casas (meio para cima)
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class EstrategiaEtanol(EstrategiaPreco):
    BASE_PRICE = Decimal("3.59")

    def calcular_bruto(self, quantidade: int) -> Decimal:
        total = self.BASE_PRICE * quantidade
        if quantidade > 80:
            return total * Decimal("0.97")
        return total

    def arredondar(self, valor: Decimal) -> Decimal:
        # Padrão: Truncar (ROUND_DOWN)
        return valor.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class EstrategiaLubrificante(EstrategiaPreco):
    BASE_PRICE = Decimal("25.00")

    def calcular_bruto(self, quantidade: int) -> Decimal:
        # Otimização: Substituído loop for por multiplicação simples
        return self.BASE_PRICE * quantidade

    def aplicar_cupom(self, valor: Decimal, cupom: str | None) -> Decimal:
        # Sobrescreve para tratar o cupom específico, depois chama o pai para os genéricos
        if cupom and cupom.upper().strip() == "LUB2":
            return valor - Decimal("2")
        return super().aplicar_cupom(valor, cupom)

    def arredondar(self, valor: Decimal) -> Decimal:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


# Factory: Mapeia o Enum do produto para a classe de estratégia correta
ESTRATEGIAS: Final[dict[Produto, EstrategiaPreco]] = {
    Produto.DIESEL: EstrategiaDiesel(),
    Produto.GASOLINA: EstrategiaGasolina(),
    Produto.ETANOL: EstrategiaEtanol(),
    Produto.LUBRIFICANTE: EstrategiaLubrificante(),
}


def processar_pedido(pedido: Pedido) -> Decimal:
    """
    Calcula o valor final do pedido:
    - quantidade == 0 -> 0
    - preço bruto negativo -> força 0 (tolerância do legado)
    - aplica cupom
    - aplica arredondamento conforme produto
    """
    if pedido.quantidade == 0:
        logging.info("quantidade zero para %s -> 0.", pedido.cliente)
        return Decimal("0")

    # Recupera a estratégia correta (Polimorfismo)
    estrategia = ESTRATEGIAS.get(pedido.produto)

    if not estrategia:
        logging.error("Produto desconhecido: %s", pedido.produto)
        return Decimal("0")

    # O fluxo agora é limpo e linear
    preco = estrategia.calcular_bruto(pedido.quantidade)

    if preco < 0:
        logging.warning("Preço negativo corrigido.")
        preco = Decimal("0")

    preco = estrategia.aplicar_cupom(preco, pedido.cupom)
    preco = estrategia.arredondar(preco)

    logging.info(
        "Pedido processado: %s, %s => %s",
        pedido.cliente, pedido.produto.value, preco
    )
    return preco