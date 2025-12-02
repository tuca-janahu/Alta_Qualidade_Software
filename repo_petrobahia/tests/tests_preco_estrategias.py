from __future__ import annotations

from decimal import Decimal

from src.domains.pedido import Pedido, Produto
from src.services.preco_calculadora import (
    ESTRATEGIAS,
    EstrategiaLubrificante,
    processar_pedido,
)


def test_so_um_cupom_por_vez_em_lubrificante():
    """Garante compatibilidade com o legado: apenas um cupom por vez."""
    estrateg = ESTRATEGIAS[Produto.LUBRIFICANTE]
    assert isinstance(estrateg, EstrategiaLubrificante)

    base = Decimal("250.00")
    assert estrateg.aplicar_cupom(base, "LUB2") == Decimal("248.00")
    assert estrateg.aplicar_cupom(base, "MEGA10") == Decimal("225.00")
    assert estrateg.aplicar_cupom(base, "NOVO5") == Decimal("237.50")


def test_produto_sem_estrategia_retorna_zero(monkeypatch):
    """Se faltar mapeamento de estratégia, o serviço devolve 0."""
    from src.services import preco_calculadora as svc

    original = svc.ESTRATEGIAS.get(Produto.DIESEL)
    svc.ESTRATEGIAS.pop(Produto.DIESEL, None)
    try:
        pedido = Pedido(cliente="X", produto=Produto.DIESEL, qtd=10, cupom=None)
        assert processar_pedido(pedido) == Decimal("0")
    finally:
        if original is not None:
            svc.ESTRATEGIAS[Produto.DIESEL] = original
