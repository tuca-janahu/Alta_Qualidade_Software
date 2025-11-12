"""
Regras de cálculo de preço de pedidos:
- preço bruto por produto/qtd
- aplicação de cupons
- arredondamentos/truncamentos por produto
"""

from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, getcontext
from typing import Final

from ..domains.pedido import Pedido, Produto

# Precisão numérica adequada para dinheiro
getcontext().prec = 28

BASES: Final[dict[Produto, Decimal]] = {
    Produto.DIESEL: Decimal("3.99"),
    Produto.GASOLINA: Decimal("5.19"),
    Produto.ETANOL: Decimal("3.59"),
    Produto.LUBRIFICANTE: Decimal("25.00"),
}


def _preco_bruto(produto: Produto, qtd: int) -> Decimal:
    """
    Regras (compatíveis com o legado):
    - diesel: >1000 -> 10% off; >500 -> 5% off; senão preço cheio
    - gasolina: >200 -> -100 fixo; senão preço cheio
    - etanol: >80 -> 3% off; senão preço cheio
    - lubrificante: somatório unitário (equivale a base*qtd)
    """
    if produto is Produto.DIESEL:
        base = BASES[Produto.DIESEL] * qtd
        if qtd > 1000:
            return base * Decimal("0.90")
        if qtd > 500:
            return base * Decimal("0.95")
        return base

    if produto is Produto.GASOLINA:
        base = BASES[Produto.GASOLINA] * qtd
        if qtd > 200:
            return base - Decimal("100")
        return base

    if produto is Produto.ETANOL:
        base = BASES[Produto.ETANOL] * qtd
        if qtd > 80:
            return base * Decimal("0.97")
        return base

    if produto is Produto.LUBRIFICANTE:
        total = Decimal("0")
        for _ in range(qtd):
            total += BASES[Produto.LUBRIFICANTE]
        return total

    # Produto desconhecido -> 0 (compatível com legado)
    return Decimal("0")


def _aplicar_cupom(valor: Decimal, produto: Produto, cupom: str | None) -> Decimal:
    """
    Cupons (compatíveis com o legado):
    - MEGA10: -10%
    - NOVO5:  -5%
    - LUB2:   -2 (apenas lubrificante)
    """
    if not cupom:
        return valor

    c = cupom.upper().strip()
    if c == "MEGA10":
        return valor * Decimal("0.90")
    if c == "NOVO5":
        return valor * Decimal("0.95")
    if c == "LUB2" and produto is Produto.LUBRIFICANTE:
        return valor - Decimal("2")
    return valor


def _arredondar_final(produto: Produto, valor: Decimal) -> Decimal:
    """
    Arredondamentos (compatíveis com o legado):
    - diesel    -> round(..., 0) (meio para cima)
    - gasolina  -> round(..., 2) (meio para cima)
    - outros    -> truncar para 2 casas (como int(preco*100)/100.0)
    """
    if produto is Produto.DIESEL:
        return valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    if produto is Produto.GASOLINA:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return valor.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def processar_pedido(pedido: Pedido) -> Decimal:
    """
    Calcula o valor final do pedido:
    - qtd == 0 -> 0
    - preço bruto negativo -> força 0 (tolerância do legado)
    - aplica cupom
    - aplica arredondamento conforme produto
    """
    if pedido.qtd == 0:
        logging.info("Quantidade zero para %s; retornando 0.", pedido.cliente)
        return Decimal("0")

    preco = _preco_bruto(pedido.produto, pedido.qtd)
    if preco < 0:
        logging.warning("Preço bruto negativo; corrigindo para 0.")
        preco = Decimal("0")

    preco = _aplicar_cupom(preco, pedido.produto, pedido.cupom)
    preco = _arredondar_final(pedido.produto, preco)

    logging.info(
        "Pedido ok: %s, %s, qtd=%s => %s",
        pedido.cliente, pedido.produto.value, pedido.qtd, preco
    )
    return preco
